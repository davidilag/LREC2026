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
```

---

# Reproducing the FPSC Pipeline

## 1. Scrape parliamentary recordings and metadata

Script:

```text
1_Faroese_Parlament_web-scraping-of-recordings.ipynb
```

Purpose:

- Connects to the public Faroese Parliament (*Løgtingið*) website and automatically retrieves parliamentary meeting recordings together with associated metadata.
- Extracts information such as meeting IDs, dates, agenda items, speaker order, timestamps, and links to individual recordings.
- Organizes the downloaded recordings and metadata into a structured format that can be used in later processing stages.
- Forms the foundation of the corpus creation pipeline by transforming publicly available parliamentary data into machine-readable resources.

---

## 2. Process parliamentary audio

Script:

```text
2_Process_parliament_audio.py
```

Purpose:

- Converts downloaded parliamentary recordings into a standardized WAV audio format suitable for ASR processing.
- Resamples all audio to 16 kHz mono in order to ensure compatibility across the different ASR systems used in the pipeline.
- Applies normalization and cleaning procedures to reduce inconsistencies in recording quality between parliamentary sessions.
- Prepares the recordings for segmentation by creating a consistent and reproducible audio processing pipeline.

---

## 3. Speech segmentation

Script:

```text
3_Speech_segmentation.py
```

Purpose:

- Splits long parliamentary recordings into smaller speech segments corresponding to individual speaker contributions.
- Uses metadata timestamps together with speech boundary processing to isolate speeches from debates and parliamentary sessions.
- Removes problematic or invalid segments such as overlapping timestamps, zero-length segments, or incorrectly aligned regions.
- Produces speech chunks that are optimized for downstream ASR inference and transcript generation.

---

## 4a. ASR inference — Wav2Vec2 Model M1

Script:

```text
4a_Wav2vec2_inference_M1_CPT-FO.ipynb
```

Purpose:

- Performs ASR inference using a continually pretrained Wav2Vec2 XLS-R model adapted to Faroese parliamentary speech.
- Generates weakly supervised transcripts for each speech segment using a model exposed to approximately 1,000 hours of Faroese parliamentary audio during continual pretraining.
- Produces transcripts with strong domain adaptation to parliamentary speech patterns, pronunciation variation, and spontaneous spoken Faroese.
- Serves as one of the primary transcription systems used later in the ROVER ensemble voting process.

---

## 4b. ASR inference — Wav2Vec2 Model M2

Script:

```text
4b_Wav2vec2_inference_M2_FO.ipynb
```

Purpose:

- Performs ASR inference using a Faroese fine-tuned Wav2Vec2 XLS-R model trained on the Ravnursson Faroese speech corpus.
- Generates an additional independent transcription hypothesis for every speech segment in the dataset.
- Introduces architectural and prediction diversity into the ensemble setup, which improves robustness during ROVER voting.
- Provides a comparison point between standard fine-tuning and continual pretraining approaches for Faroese ASR.

---

## 4c. ASR inference — Whisper Model M3

Script:

```text
4c_Whisper-inference-M3_FO.ipynb
```

Purpose:

- Performs ASR inference using a Whisper Large model fine-tuned specifically on Faroese speech data.
- Generates weak transcripts using a transformer-based multilingual ASR architecture different from the Wav2Vec2 systems.
- Captures complementary prediction patterns and decoding behavior that improve ensemble diversity.
- Contributes Faroese-specific transcription hypotheses to the later ROVER consensus generation stage.

---

## 4d. ASR inference — Whisper Model M4

Script:

```text
4d_Whisper-inference-M4_NO-IS-FO.ipynb
```

Purpose:

- Performs ASR inference using a multilingual Whisper model fine-tuned on Norwegian, Icelandic, and Faroese speech.
- Exploits linguistic and phonetic similarities between closely related North Germanic languages to improve Faroese recognition performance.
- Generates multilingual-informed transcription hypotheses with lower word error rates on spontaneous parliamentary speech.
- Adds complementary multilingual predictions to the ensemble voting system used for final transcript generation.

---

## 5. ROVER voting and transcript generation

Script:

```text
5_ROVER_voting_transcripts.ipynb
```

Purpose:

- Combines transcripts from all four ASR systems into a single consensus transcription using ROVER (Recognizer Output Voting Error Reduction).
- Aligns the different ASR hypotheses and performs weighted voting to determine the most likely word sequence for each speech segment.
- Uses model performance statistics such as WER and CER to assign weights to the different ASR systems during voting.
- Produces the final weakly supervised transcripts used in the Faroese Parliament Speech Corpus (FPSC).
- Generates transcript metadata, confidence scores, and final corpus-ready outputs for downstream ASR and language technology research.

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
  institution = {University of the Faroe Islands},
  keywords = {Faroese, Parliamentary Speech, Automatic Speech Recognition, Weakly-Supervised Transcription, Whisper, Wav2Vec2},
  abstract = {We present FPSC, a 1,600-hour Faroese parliamentary speech corpus comprising approximately 89,000 speeches enriched with detailed speaker and linguistic metadata. The corpus was constructed using a sustainable ASR-assisted pipeline combining speech segmentation, multiple Faroese-adapted ASR systems, and ROVER-based consensus voting for weakly supervised transcription. FPSC represents the first large-scale corpus of natural spoken Faroese and provides an open resource for future research in automatic speech recognition and low-resource language technology.}
}
```
---

# FPSC Dataset

The final Faroese Parliament Speech Corpus (FPSC) dataset is publicly available on Hugging Face:

https://huggingface.co/datasets/davidilag/FPSC

---

# Contact

Dávid í Lág  
University of the Faroe Islands  
MSc. in Computer Science, Ph.D.-student (2024-2028)  
Research area: Automatic Speech Recognition for Low-Resource Languages
