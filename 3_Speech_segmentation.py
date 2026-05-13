import os
import json
import math
import re
import logging
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from typing import Tuple

from pydub import AudioSegment

# ================== CONFIG ==================
METADATA_FILE = r"C:\code\parlament_split_recordings\PARLIAMENT_META_DATA_ALL.jsonl"
MEETING_WAV_DIR = r"D:\parliament\data\WAV"
OUTPUT_DIR = r"D:\parliament\data\audio_files"

OVERWRITE = False               # overwrite existing speech wavs
NORMALIZE = True                # peak normalization
TARGET_PEAK_DBFS = -1.0         # target peak for normalization
EXPECTED_SAMPLERATE = None      # e.g. 16000 to warn if different, or None to skip

# Logging
LOG_DIR = r"C:\code\parlament_split_recordings\logs"
LOG_NAME = f"split_log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
LOG_PATH = str(Path(LOG_DIR) / LOG_NAME)
# ============================================

# --- Logging setup ---
logger = logging.getLogger("splitter")
logger.setLevel(logging.INFO)
fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

fh = logging.FileHandler(LOG_PATH, encoding="utf-8")
fh.setFormatter(fmt)
logger.addHandler(fh)

ch = logging.StreamHandler()
ch.setFormatter(fmt)
logger.addHandler(ch)

ID_PAT = re.compile(r"^M(?P<mid>\d+)_S(?P<seq>\d+)$")

def parse_meeting_and_seq(sid: str) -> Tuple[int, int]:
    """
    Parse 'M<meeting>_S<seq>' -> (meeting:int, seq:int). Returns (inf, inf) if not matched.
    """
    if not isinstance(sid, str):
        return (float("inf"), float("inf"))  # type: ignore
    m = ID_PAT.match(sid.strip())
    if not m:
        return (float("inf"), float("inf"))  # type: ignore
    try:
        return int(m.group("mid")), int(m.group("seq"))
    except Exception:
        return (float("inf"), float("inf"))  # type: ignore

def find_meeting_wav(meeting_id: str) -> str | None:
    """
    Find first .wav file in MEETING_WAV_DIR that starts with '<meeting_id>_'.
    """
    prefix = f"{meeting_id}_"
    for name in os.listdir(MEETING_WAV_DIR):
        if name.startswith(prefix) and name.lower().endswith(".wav"):
            return str(Path(MEETING_WAV_DIR) / name)
    return None

def peak_normalize(segment: AudioSegment, target_dbfs: float = -1.0) -> AudioSegment:
    """
    Peak-normalize segment to target_dbfs (if max_dBFS available), fallback to RMS-based.
    """
    try:
        max_dbfs = segment.max_dBFS  # type: ignore[attr-defined]
        if math.isfinite(max_dbfs):
            gain = target_dbfs - max_dbfs
            return segment.apply_gain(gain)
    except Exception:
        pass
    if segment.dBFS == float("-inf"):
        return segment
    gain = min(target_dbfs - segment.dBFS, 0.0)
    return segment.apply_gain(gain)

def ensure_output_dir(out_dir: str):
    Path(out_dir).mkdir(parents=True, exist_ok=True)

def main():
    ensure_output_dir(OUTPUT_DIR)

    # 1) Load metadata (we do not modify it here)
    if not Path(METADATA_FILE).exists():
        logger.error(f"Metadata file not found: {METADATA_FILE}")
        return

    records = []
    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        for ln, line in enumerate(f, 1):
            line = line.rstrip("\r\n")
            if not line:
                continue
            try:
                obj = json.loads(line)
                records.append(obj)
            except json.JSONDecodeError as e:
                logger.error(f"Bad JSON at line {ln}: {e}")

    logger.info(f"Loaded {len(records):,} speech rows from metadata.")

    # 2) Group by meeting_id
    by_meeting = defaultdict(list)
    for r in records:
        mid = str(r.get("meeting_id", "")).strip()
        if not mid:
            logger.warning(f"Record with missing meeting_id: id={r.get('id')}")
            continue
        by_meeting[mid].append(r)

    total_meetings = len(by_meeting)
    logger.info(f"Found {total_meetings} meetings in metadata.")

    total_created = 0
    total_skipped = 0
    total_errors = 0
    meetings_missing_wav = 0

    # Process meetings in numeric order where possible
    def meeting_sort_key(mid: str):
        try:
            return int(mid)
        except Exception:
            return mid

    for idx, mid in enumerate(sorted(by_meeting.keys(), key=meeting_sort_key), 1):
        recs = by_meeting[mid]

        # --- SORT BY id (sequence), not by 'second' ---
        recs_sorted = sorted(
            recs,
            key=lambda r: parse_meeting_and_seq(str(r.get("id", "")))[1]
        )

        logger.info("-" * 88)
        logger.info(f"[{idx}/{total_meetings}] Processing meeting_id={mid} with {len(recs_sorted)} speeches (ordered by id)")

        # Load meeting WAV
        wav_path = find_meeting_wav(mid)
        if not wav_path:
            logger.warning(f"Could not find .wav for meeting_id={mid} in {MEETING_WAV_DIR}. Skipping {len(recs_sorted)} speeches.")
            meetings_missing_wav += 1
            total_skipped += len(recs_sorted)
            continue

        try:
            meeting_audio = AudioSegment.from_wav(wav_path)
        except Exception as e:
            logger.error(f"Error loading WAV for meeting_id={mid}: {wav_path} -> {e}. Skipping {len(recs_sorted)} speeches.")
            total_errors += len(recs_sorted)
            continue

        if EXPECTED_SAMPLERATE is not None:
            try:
                if meeting_audio.frame_rate != EXPECTED_SAMPLERATE:
                    logger.warning(f"Meeting {mid}: samplerate {meeting_audio.frame_rate} differs from expected {EXPECTED_SAMPLERATE}.")
            except Exception:
                pass

        meeting_len_s = len(meeting_audio) / 1000.0

        # For each speech in id-order, slice: [second, next.second) or to EOF for last
        for i, r in enumerate(recs_sorted):
            sid = r.get("id")
            audio_id = r.get("audio_id")

            # start from this speech's 'second'
            try:
                start_s = float(r.get("second", 0) or 0)
            except Exception:
                logger.error(f"Meeting {mid}, {sid}: invalid 'second' value -> {r.get('second')}. Skipping.")
                total_errors += 1
                continue

            # end at next speech's 'second' (id-order), or EOF for last
            if i + 1 < len(recs_sorted):
                next_second = recs_sorted[i+1].get("second", None)
                try:
                    end_s = float(next_second) if next_second is not None else meeting_len_s
                except Exception:
                    logger.warning(f"Meeting {mid}, {sid}: next 'second' invalid; using end of meeting.")
                    end_s = meeting_len_s
            else:
                end_s = meeting_len_s

            # Guards
            if math.isnan(start_s) or math.isnan(end_s):
                logger.error(f"Meeting {mid}, {sid}: NaN boundary (start={start_s}, end={end_s}). Skipping.")
                total_errors += 1
                continue

            if start_s < 0:
                logger.warning(f"Meeting {mid}, {sid}: start<0 ({start_s}); clamping to 0.")
                start_s = 0.0

            if end_s > meeting_len_s:
                logger.warning(f"Meeting {mid}, {sid}: end exceeds meeting length ({end_s} > {meeting_len_s}); clamping to end.")
                end_s = meeting_len_s

            if end_s <= start_s:
                # This can still happen if metadata has tight or inverted boundaries even after cleanup.
                logger.warning(f"Meeting {mid}, {sid}: non-positive segment length (start={start_s}, end={end_s}). Skipping.")
                total_skipped += 1
                continue

            # Output filename = audio_id from metadata (preferred)
            if not audio_id or not str(audio_id).lower().endswith(".wav"):
                # Fallback: preserve id-based name
                audio_id = f"{sid}.wav"
                logger.warning(f"Meeting {mid}, {sid}: missing/invalid audio_id; using fallback {audio_id}")

            out_path = str(Path(OUTPUT_DIR) / audio_id)

            if (not OVERWRITE) and Path(out_path).exists():
                logger.info(f"exists -> {audio_id} (skip, OVERWRITE=False)")
                total_skipped += 1
                continue

            # Slice & export
            start_ms = int(start_s * 1000)
            end_ms = int(end_s * 1000)
            try:
                seg = meeting_audio[start_ms:end_ms]
                if NORMALIZE:
                    seg = peak_normalize(seg, TARGET_PEAK_DBFS)
                seg.export(out_path, format="wav")
                logger.info(f"created -> {audio_id} | {round(end_s - start_s)}s (start={start_s:.2f}, end={end_s:.2f})")
                total_created += 1
            except Exception as e:
                logger.error(f"Meeting {mid}, {sid}: export failed -> {e}")
                total_errors += 1

        del meeting_audio  # free

    logger.info("=" * 88)
    logger.info(f"Done. Created: {total_created:,} | Skipped: {total_skipped:,} | Errors: {total_errors:,} | Meetings missing WAV: {meetings_missing_wav:,}")
    logger.info(f"Output dir: {OUTPUT_DIR}")
    logger.info(f"Log file:   {LOG_PATH}")

if __name__ == "__main__":
    main()
