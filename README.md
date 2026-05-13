# FPSC — Faroese Parliament Speech Corpus (LREC 2026)

This repository contains the scripts and processing pipeline used in the paper:

**FPSC: A Sustainable Pipeline for Building a Faroese Parliamentary Speech Corpus**

The project transforms publicly available recordings from the Faroese Parliament (*Løgtingið*) into a large-scale reusable speech corpus for Automatic Speech Recognition (ASR) and language technology research.

The pipeline combines:

- metadata extraction
- audio preprocessing
- speech segmentation
- ASR-based weak transcription
- multi-model decoding
- ROVER voting
- transcript generation
- corpus export

The final result is the **Faroese Parliament Speech Corpus (FPSC)** containing parliamentary speech recordings together with automatically generated transcripts and metadata.

---

# Repository Structure

```text
LREC2026/
│
├── 1_Faroese_Parlament_web-scraping-of-recordings.ipynb
├── 2_Process_parliament_audio.py
├── 3_Speech_segmentation.py
├── 4a_Wav2vec2_inference_M1_CPT-FO.ipynb
├── 4b_Wav2vec2_inference_M2_FO.ipynb
├── 4c_Whisper-inference-M3_FO.ipynb
├── 4d_Whisper-inference-M4_NO-IS-FO.ipynb
├── 5_ROVER_voting_transcripts.ipynb
│
├── audio/
├── metadata/
├── transcripts/
├── output/
└── README.md
```

---

# Reproducing the FPSC Pipeline

## 1. Scrape parliamentary recordings and metadata

Script:

```text
1_Faroese_Parlament_web-scraping-of-recordings.ipynb
```

Purpose:

- Download parliamentary session recordings
- Download metadata from the parliament website
- Store session IDs, speaker information, and dates

Output:

```text
raw_audio/
raw_metadata/
```

---

## 2. Process parliamentary audio

Script:

```text
2_Process_parliament_audio.py
```

Purpose:

- Convert recordings to WAV
- Resample audio to 16 kHz mono
- Normalize audio
- Prepare files for segmentation

Typical preprocessing:

```bash
ffmpeg -i input.mp4 -ar 16000 -ac 1 output.wav
```

Output:

```text
audio_wav/
```

---

## 3. Speech segmentation

Script:

```text
3_Speech_segmentation.py
```

Purpose:

- Split long parliamentary sessions into smaller speech segments
- Remove silence and non-speech regions
- Produce ASR-ready chunks

Output:

```text
segments/
```

---

## 4a. ASR inference — Wav2Vec2 Model M1

Script:

```text
4a_Wav2vec2_inference_M1_CPT-FO.ipynb
```

Purpose:

- Generate transcripts using the Wav2Vec2 M1 model
- Continual pretraining (CPT) Faroese model

Output:

```text
hypotheses/model1/
```

---

## 4b. ASR inference — Wav2Vec2 Model M2

Script:

```text
4b_Wav2vec2_inference_M2_FO.ipynb
```

Purpose:

- Generate transcripts using the Wav2Vec2 M2 model
- Faroese fine-tuned model

Output:

```text
hypotheses/model2/
```

---

## 4c. ASR inference — Whisper Model M3

Script:

```text
4c_Whisper-inference-M3_FO.ipynb
```

Purpose:

- Generate transcripts using Whisper M3
- Faroese Whisper model

Output:

```text
hypotheses/model3/
```

---

## 4d. ASR inference — Whisper Model M4

Script:

```text
4d_Whisper-inference-M4_NO-IS-FO.ipynb
```

Purpose:

- Generate transcripts using multilingual Whisper M4
- Norwegian–Icelandic–Faroese adapted model

Output:

```text
hypotheses/model4/
```

---

## 5. ROVER voting and transcript generation

Script:

```text
5_ROVER_voting_transcripts.ipynb
```

Purpose:

- Combine multiple ASR hypotheses
- Generate consensus transcripts using ROVER voting
- Produce final transcript outputs

Input:

- transcripts from M1–M4

Output:

```text
final_transcripts/
```

---

# Dataset Characteristics

The final FPSC corpus contains:

- parliamentary speech recordings
- machine-generated transcripts
- speaker metadata
- session metadata
- aligned speech segments

The dataset is intended for:

- Faroese ASR
- low-resource speech research
- parliamentary speech analysis
- political speech research
- weakly supervised ASR training

---


# Citation

If you use this repository or the FPSC corpus, please cite:

```bibtex
@inproceedings{iLag2026FPSC,
  author = {Dávid í Lág and Barbara Scalvini and Carlos Mena and Jón Guðnason},
  title = {{FPSC}: A Sustainable Pipeline for Building a Faroese Parliamentary Speech Corpus},
  booktitle = {Proceedings of the Language Resources and Evaluation Conference (LREC 2026)},
  year = {2026},
  address = {Palma de Mallorca, Spain},
  publisher = {European Language Resources Association (ELRA)},
  keywords = {Faroese, Parliamentary Speech, Automatic Speech Recognition, Weakly-Supervised Transcription, Whisper, Wav2Vec2},
  abstract = {We present FPSC, a 1,600-hour Faroese parliamentary speech corpus comprising approximately 89,000 speeches enriched with detailed speaker and linguistic metadata. The corpus was constructed using a sustainable ASR-assisted pipeline combining speech segmentation, multiple Faroese-adapted ASR systems, and ROVER-based consensus voting for weakly supervised transcription. FPSC represents the first large-scale corpus of natural spoken Faroese and provides an open resource for future research in automatic speech recognition and low-resource language technology.}
}
```

---

# Contact

Dávid í Lág  
University of the Faroe Islands  
MSc. in Computer Science, Ph.D.-student (2024-2028)  
Research area: Automatic Speech Recognition for Low-Resource Languages
