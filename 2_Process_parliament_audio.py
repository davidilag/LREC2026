import os
import subprocess

def convert_mp4_to_wav(input_dir, output_dir, sample_rate=16000):
    """
    Converts all MP4 files in the input directory to WAV format
    with the specified sample rate and saves them to the output directory.

    Args:
        input_dir (str): Path to the folder containing MP4 files.
        output_dir (str): Path to the folder where WAV files will be saved.
        sample_rate (int): The target sample rate for the WAV files (default: 16000).
    """

    # --- Input Validation ---
    if not os.path.isdir(input_dir):
        print(f"Error: Input directory '{input_dir}' not found.")
        return
    if not os.path.isdir(output_dir):
        print(f"Output directory '{output_dir}' not found. Creating it...")
        try:
            os.makedirs(output_dir)
            print(f"Successfully created directory: {output_dir}")
        except OSError as e:
            print(f"Error creating output directory '{output_dir}': {e}")
            return

    print(f"Starting conversion from '{input_dir}' to '{output_dir}'...")
    print(f"Target sample rate: {sample_rate} Hz")
    print("-" * 30)

    # --- FFmpeg Check (Optional but Recommended) ---
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("FFmpeg found. Proceeding with conversion.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\n" + "="*50)
        print("WARNING: FFmpeg not found or not in your system's PATH.")
        print("This script relies on FFmpeg for conversion.")
        print("Please ensure FFmpeg is installed and accessible.")
        print("You can download it from: https://ffmpeg.org/download.html")
        print("="*50 + "\n")
        # You might want to exit here if FFmpeg is strictly required
        # return

    # --- Conversion Process ---
    converted_count = 0
    skipped_count = 0
    error_count = 0

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".mp4"):
            input_file = os.path.join(input_dir, filename)
            base_filename = os.path.splitext(filename)[0]
            output_file = os.path.join(output_dir, f"{base_filename}.wav")

            print(f"\nProcessing: {filename}")

            # --- FFmpeg Command Construction ---
            # -i: input file
            # -vn: no video (extract only audio)
            # -acodec pcm_s16le: set audio codec to PCM 16-bit little-endian (standard for WAV)
            # -ar: set audio sample rate
            # -ac 1: set audio channels to 1 (mono) - Often desired for ASR
            # -y: overwrite output file if it exists
            command = [
                "ffmpeg",
                "-i", input_file,
                "-vn",
                "-acodec", "pcm_s16le",
                "-ar", str(sample_rate),
                "-ac", "1", # Set to mono (adjust to 2 if you need stereo)
                "-y",
                output_file
            ]

            # --- Execute FFmpeg ---
            try:
                # Use capture_output=True in Python 3.7+ for cleaner output handling
                process = subprocess.run(
                    command,
                    check=True,         # Raise an exception if FFmpeg fails
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True           # Decode stdout/stderr as text
                )
                print(f"  -> Successfully converted to: {output_file}")
                converted_count += 1

            except FileNotFoundError:
                 print("  -> ERROR: FFmpeg command not found. Is it installed and in your PATH?")
                 error_count += 1
                 # Stop processing if FFmpeg isn't found
                 break
            except subprocess.CalledProcessError as e:
                print(f"  -> ERROR converting '{filename}':")
                print(f"     Command: {' '.join(e.cmd)}")
                print(f"     Return Code: {e.returncode}")
                print(f"     Stderr: {e.stderr.strip()}")
                error_count += 1
            except Exception as e:
                print(f"  -> An unexpected error occurred with '{filename}': {e}")
                error_count += 1

        else:
            # print(f"Skipping non-MP4 file: {filename}")
            skipped_count += 1

    # --- Summary ---
    print("\n" + "=" * 30)
    print("Conversion Complete!")
    print(f"  Files Converted: {converted_count}")
    print(f"  Files Skipped:   {skipped_count}")
    print(f"  Errors:          {error_count}")
    print("=" * 30)

# --- Configuration ---
input_mp4_dir = r"D:\parliament\data\MP4\MP4"
output_wav_dir = r"D:\parliament\data\WAV\WAV"

# --- Run Conversion ---
convert_mp4_to_wav(input_mp4_dir, output_wav_dir)