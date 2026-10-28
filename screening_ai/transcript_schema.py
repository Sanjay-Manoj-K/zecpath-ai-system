"""Transcript record helpers for the Zecpath AI System (Day 23).

Uses only the Python standard library. It defines a data contract and validation
helpers; it does not perform speech recognition, audio storage, or hiring decisions.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, Optional

SCHEMA_VERSION = "1.0.0"
SPEAKER_ROLES = {"interviewer", "candidate", "system"}
SOURCE_TYPES = {"speech_to_text", "typed", "system_generated"}
TOP_LEVEL_REQUIRED = {
    "schema_version", "transcript_id", "session_id", "candidate_id", "job_id",
    "language", "created_at_utc", "turns",
}
TURN_REQUIRED = {
    "turn_id", "sequence_no", "speaker_role", "question_id", "timestamp_utc",
    "raw_text", "normalized_text", "confidence", "source", "language",
}


class TranscriptValidationError(ValueError):
    """Raised when a transcript does not match the documented data contract."""


def normalize_transcript_text(value: str) -> str:
    """Normalize Unicode to NFC, remove unsafe control characters, collapse whitespace.

    Punctuation and letter case are preserved. The original input should be kept in
    ``raw_text``; this function creates a separate normalized representation only.
    """
    if not isinstance(value, str):
        raise TranscriptValidationError("Transcript text must be a string.")
    # Convert non-printing control characters (except ordinary whitespace) to spaces.
    chars = []
    for char in value:
        if unicodedata.category(char) == "Cc" and char not in "\t\r\n":
            chars.append(" ")
        else:
            chars.append(char)
    value = unicodedata.normalize("NFC", "".join(chars))
    value = re.sub(r"\s+", " ", value).strip()
    if not value:
        raise TranscriptValidationError("Transcript text must not be empty after normalization.")
    return value


def normalize_timestamp(value: str) -> str:
    """Return an ISO-8601 UTC timestamp ending in Z; naive timestamps are rejected."""
    if not isinstance(value, str) or not value.strip():
        raise TranscriptValidationError("Timestamp must be a non-empty ISO-8601 string.")
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise TranscriptValidationError("Timestamp must be valid ISO-8601.") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise TranscriptValidationError("Timestamp must include a timezone offset.")
    return parsed.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _require_nonempty_string(obj: Dict[str, Any], key: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        raise TranscriptValidationError("{} must be a non-empty string.".format(key))
    return value


def validate_transcript(record: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a transcript document; return the same record if it is valid.

    Required metadata includes candidate, job, question (per turn when applicable),
    UTC timestamps and optional ASR confidence in the inclusive range [0, 1].
    """
    if not isinstance(record, dict):
        raise TranscriptValidationError("Transcript must be a JSON object.")
    missing = TOP_LEVEL_REQUIRED - set(record)
    if missing:
        raise TranscriptValidationError("Transcript is missing fields: {}".format(sorted(missing)))
    if record["schema_version"] != SCHEMA_VERSION:
        raise TranscriptValidationError("Unsupported schema_version: {}".format(record["schema_version"]))
    for key in ("transcript_id", "session_id", "candidate_id", "job_id", "language"):
        _require_nonempty_string(record, key)
    if normalize_timestamp(record["created_at_utc"]) != record["created_at_utc"]:
        raise TranscriptValidationError("created_at_utc must be normalized to UTC and end in Z.")
    turns = record["turns"]
    if not isinstance(turns, list) or not turns:
        raise TranscriptValidationError("turns must be a non-empty list.")

    turn_ids, sequence_numbers = set(), set()
    for index, turn in enumerate(turns, start=1):
        if not isinstance(turn, dict):
            raise TranscriptValidationError("Every turn must be an object.")
        missing_turn = TURN_REQUIRED - set(turn)
        if missing_turn:
            raise TranscriptValidationError("Turn {} is missing fields: {}".format(index, sorted(missing_turn)))
        for key in ("turn_id", "speaker_role", "raw_text", "normalized_text", "source", "language"):
            _require_nonempty_string(turn, key)
        if turn["speaker_role"] not in SPEAKER_ROLES:
            raise TranscriptValidationError("Unsupported speaker_role: {}".format(turn["speaker_role"]))
        if turn["source"] not in SOURCE_TYPES:
            raise TranscriptValidationError("Unsupported source: {}".format(turn["source"]))
        seq = turn["sequence_no"]
        if isinstance(seq, bool) or not isinstance(seq, int) or seq < 1:
            raise TranscriptValidationError("sequence_no must be a positive integer.")
        if seq in sequence_numbers:
            raise TranscriptValidationError("sequence_no values must be unique within a transcript.")
        if turn["turn_id"] in turn_ids:
            raise TranscriptValidationError("turn_id values must be unique within a transcript.")
        turn_ids.add(turn["turn_id"])
        sequence_numbers.add(seq)
        question_id = turn["question_id"]
        if question_id is not None and (not isinstance(question_id, str) or not question_id.strip()):
            raise TranscriptValidationError("question_id must be null or a non-empty string.")
        if normalize_timestamp(turn["timestamp_utc"]) != turn["timestamp_utc"]:
            raise TranscriptValidationError("timestamp_utc must be normalized to UTC and end in Z.")
        normalized = normalize_transcript_text(turn["raw_text"])
        if turn["normalized_text"] != normalized:
            raise TranscriptValidationError("normalized_text does not match the documented normalization rules.")
        confidence = turn["confidence"]
        if confidence is not None:
            if isinstance(confidence, bool) or not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
                raise TranscriptValidationError("confidence must be null or a number in the range [0, 1].")
        if turn["language"] != record["language"]:
            # Mixed-language turns are allowed, but each turn must identify its own language.
            pass
    return record


def load_transcript(path: str | Path) -> Dict[str, Any]:
    """Load a UTF-8 JSON transcript and validate the data contract."""
    try:
        with Path(path).open("r", encoding="utf-8-sig") as stream:
            record = json.load(stream)
    except json.JSONDecodeError as exc:
        raise TranscriptValidationError("Invalid transcript JSON: {}".format(exc)) from exc
    return validate_transcript(record)


def write_transcript(path: str | Path, record: Dict[str, Any]) -> Path:
    """Validate and write a transcript as readable UTF-8 JSON."""
    validate_transcript(record)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return target
