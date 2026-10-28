import json
from pathlib import Path
import pytest
from screening_ai.transcript_schema import (
    TranscriptValidationError, load_transcript, normalize_timestamp,
    normalize_transcript_text, validate_transcript, write_transcript,
)

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "data" / "transcripts" / "example_transcript.json"


def sample():
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


def test_example_transcript_loads_and_validates():
    assert load_transcript(EXAMPLE)["schema_version"] == "1.0.0"


def test_text_normalization_preserves_meaningful_punctuation_and_case():
    assert normalize_transcript_text("  Hello,\tWORLD! \n ") == "Hello, WORLD!"


def test_unicode_normalization_uses_nfc():
    assert normalize_transcript_text("cafe\u0301") == "café"


def test_timestamp_converts_offset_to_utc():
    assert normalize_timestamp("2026-10-28T14:00:00+05:30") == "2026-10-28T08:30:00Z"


def test_naive_timestamp_is_rejected():
    with pytest.raises(TranscriptValidationError, match="timezone"):
        normalize_timestamp("2026-10-28T08:30:00")


def test_confidence_outside_range_is_rejected():
    record = sample()
    record["turns"][0]["confidence"] = 1.2
    with pytest.raises(TranscriptValidationError, match="confidence"):
        validate_transcript(record)


def test_duplicate_turn_sequence_is_rejected():
    record = sample()
    record["turns"][1]["sequence_no"] = record["turns"][0]["sequence_no"]
    with pytest.raises(TranscriptValidationError, match="sequence_no"):
        validate_transcript(record)


def test_normalized_text_mismatch_is_rejected():
    record = sample()
    record["turns"][0]["normalized_text"] = "some other text"
    with pytest.raises(TranscriptValidationError, match="normalized_text"):
        validate_transcript(record)


def test_empty_text_is_rejected_by_normalizer():
    with pytest.raises(TranscriptValidationError, match="empty"):
        normalize_transcript_text(" \t\n ")


def test_write_then_read_round_trip(tmp_path):
    path = write_transcript(tmp_path / "saved.json", sample())
    assert load_transcript(path) == sample()


def test_question_id_can_be_null_for_free_form_turn():
    record = sample()
    record["turns"][0]["question_id"] = None
    assert validate_transcript(record) is record
