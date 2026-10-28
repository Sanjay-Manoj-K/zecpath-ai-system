# Day 23 — Transcript Data Architecture

This bundle defines a versioned, structured transcript contract for the Zecpath AI System. It is data architecture and validation only; it does not implement audio capture, speech recognition, a live API, or production database deployment.

## Deliverables

- `screening_ai/transcript_schema.py`: standard-library normalizer, validation helpers, JSON loader and writer.
- `data/transcripts/transcript_schema.json`: formal JSON Schema for transcript documents.
- `data/transcripts/metadata_standards.json`: definitions for candidate/job/question IDs, timestamps and confidence metadata.
- `data/transcripts/normalization_rules.json`: explicit text and timestamp normalization rules.
- `data/transcripts/database_schema.sql`: SQLite DDL for screening sessions and transcript turns.
- `data/transcripts/example_transcript.json`: synthetic demonstration record. It contains no actual candidate interview data.
- `tests/test_transcript_schema.py`: focused tests.
- `docs/DAY23_Transcript_Data_Architecture.md`: implementation notes and next steps.

## Data contract

A transcript identifies the transcript/session, candidate, job, language, creation timestamp and ordered turns. Each turn identifies its speaker, optional question-bank reference, timestamp, raw and normalized text, language, source and optional speech-to-text confidence (`0.0`–`1.0`). A missing confidence is represented as JSON `null`; it is never fabricated.

## Normalization policy

Raw input is retained separately. Normalized text applies Unicode NFC, replaces non-printing control characters with spaces, collapses whitespace and trims leading/trailing spaces. It preserves punctuation and letter case and does not translate or guess speech. Timestamps must be timezone-aware ISO 8601 and are stored in UTC using a trailing `Z`.

## Run tests

```powershell
python -m pytest .\tests\test_transcript_schema.py -q
python -m py_compile .\screening_ai\transcript_schema.py
python -m pytest -q
```

## Integration guidance

Copy the bundle contents into the existing project root and merge directories. The bundle intentionally does not include `screening_ai/__init__.py`, `screening_engine.py`, `voice_analysis.py`, interview modules, or Day 21/22 files; keep them unchanged. Review `git status --short` before staging only Day 23 files.
