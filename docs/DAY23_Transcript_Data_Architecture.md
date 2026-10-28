# Day 23 — Transcript Data Architecture

## Objective
Define how voice conversations are converted into structured, AI-processable data. The scope is limited to transcript architecture, metadata standards, normalization and a proposed relational schema; this deliverable does not claim to implement live audio capture or speech-to-text.

## Architecture

```text
Voice / Typed Interaction
          |
          v
  ASR or Text Source
          |
          v
   Raw Turn Capture
          |
          +---------------------> Preserve raw_text
          |
          v
 Unicode + Whitespace Normalization
          |
          v
 Transcript Schema Validation
          |
          v
 Versioned Transcript JSON
          |
          v
 Optional SQLite persistence
 (screening_sessions + transcript_turns)
          |
          v
 Downstream AI screening / analytics
```

## Data structures

| Structure | Responsibility |
|---|---|
| Transcript document | Groups a screening session and identifies candidate, job, language and schema version. |
| Transcript turn | Stores one interviewer/candidate/system utterance with order, timestamp, question reference, text, source and optional confidence. |
| Metadata standards | Defines field meaning, timestamp policy, confidence semantics and use of the Day 22 question IDs. |
| JSON Schema | Documents required fields and types for interoperable validation. |
| SQLite DDL | Proposes a normalized persistence layout with foreign keys, uniqueness constraints and indexes. |

## Key metadata standards

| Field | Standard |
|---|---|
| `candidate_id` | Opaque upstream candidate identifier; do not use a person's name as the key. |
| `job_id` | Job description or requisition identifier. |
| `question_id` | Day 22 question ID where mapped; null for free-form turns. |
| `timestamp_utc` | Timezone-aware ISO 8601, stored as UTC with trailing `Z`. |
| `confidence` | Optional speech-recognizer confidence from 0 to 1; null if unavailable. It is not a measure of candidate quality. |
| `raw_text` / `normalized_text` | Keep source text for traceability and normalized text for downstream processing. |
| `sequence_no` | Positive, unique position of a turn within one transcript. |

## Example code

```python
from screening_ai.transcript_schema import load_transcript, normalize_transcript_text

record = load_transcript("data/transcripts/example_transcript.json")
clean_text = normalize_transcript_text("  Hello!\nPlease begin.  ")
print(record["session_id"], clean_text)
```

## Validation

The focused test suite covers schema compliance, Unicode normalization, whitespace handling, UTC conversion, rejection of naive timestamps, confidence bounds, sequence uniqueness, normalized-text consistency, empty text and JSON round-tripping. The synthetic example uses clearly artificial IDs and text.

## Challenges and solutions

| Challenge | Design decision |
|---|---|
| Different whitespace and Unicode forms | Normalize with NFC and collapse whitespace while preserving punctuation and case. |
| Raw recognition text must remain auditable | Store `raw_text` separately from `normalized_text`. |
| Missing or incomparable confidence | Make confidence nullable and constrain known values to `[0, 1]`. |
| Timestamp ambiguity across time zones | Reject naive timestamps and canonicalize offset-aware values to UTC. |
| Questions may be open-ended | Permit null `question_id` for free-form turns while reusing Day 22 IDs when applicable. |
| Future storage queries | Separate session metadata from individual turns and add lookup indexes in the proposed SQLite schema. |

## Deliverables

- Voice transcript schema in JSON Schema format.
- AI screening transcript document/turn structure.
- Metadata standards and normalization rules.
- Proposed SQLite database schema.
- Synthetic example transcript.
- Standard-library helper module and focused tests.

## Limitations and next steps

This is a validated data-contract prototype, not a live voice pipeline. Next: review fields with the screening integration, run the tests in the existing repository, add repository-wide validation, then integrate ASR/audio references and persistent storage only when those components are implemented. Apply retention, access control and consent policies before storing real candidate transcripts.
