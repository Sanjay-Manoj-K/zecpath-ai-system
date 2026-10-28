-- Day 23 logical storage schema for SQLite. Example DDL; not applied to any production DB.
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS screening_sessions (
    session_id       TEXT PRIMARY KEY,
    transcript_id    TEXT NOT NULL UNIQUE,
    candidate_id     TEXT NOT NULL,
    job_id           TEXT NOT NULL,
    language         TEXT NOT NULL,
    created_at_utc   TEXT NOT NULL,
    schema_version   TEXT NOT NULL DEFAULT '1.0.0',
    session_status   TEXT NOT NULL DEFAULT 'completed'
                     CHECK (session_status IN ('created','in_progress','completed','failed'))
);

CREATE TABLE IF NOT EXISTS transcript_turns (
    turn_id          TEXT PRIMARY KEY,
    session_id       TEXT NOT NULL,
    sequence_no      INTEGER NOT NULL CHECK (sequence_no >= 1),
    speaker_role     TEXT NOT NULL CHECK (speaker_role IN ('interviewer','candidate','system')),
    question_id      TEXT NULL,
    timestamp_utc    TEXT NOT NULL,
    raw_text         TEXT NOT NULL,
    normalized_text  TEXT NOT NULL,
    confidence       REAL NULL CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 1)),
    source           TEXT NOT NULL CHECK (source IN ('speech_to_text','typed','system_generated')),
    language         TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES screening_sessions(session_id) ON DELETE CASCADE,
    UNIQUE (session_id, sequence_no)
);

CREATE INDEX IF NOT EXISTS idx_sessions_candidate_job
    ON screening_sessions(candidate_id, job_id, created_at_utc);
CREATE INDEX IF NOT EXISTS idx_turns_question
    ON transcript_turns(question_id);
CREATE INDEX IF NOT EXISTS idx_turns_timestamp
    ON transcript_turns(timestamp_utc);
