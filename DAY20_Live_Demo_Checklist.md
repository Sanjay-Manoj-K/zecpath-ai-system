# Day 20 — Live Demo Checklist

## Before the demonstration

- [ ] Activate the project virtual environment.
- [ ] Confirm `scoring/semantic_matching.py` compiles.
- [ ] Run `python -m scoring.day13_validation` and confirm all 9 tests pass.
- [ ] Start the API using the project's existing launch command.
- [ ] Open `http://127.0.0.1:8000/docs`.
- [ ] Check `/health`, `/docs`, and `/openapi.json`.

## Demonstration workflow

- [ ] Upload a test resume.
- [ ] Confirm a resume ID is returned.
- [ ] Parse the uploaded resume.
- [ ] Score it against an existing job description.
- [ ] Generate the candidate shortlist.
- [ ] Submit an asynchronous scoring job.
- [ ] Poll the job status until it reaches `COMPLETED`.
- [ ] Check that the result contains a score and decision.
- [ ] Confirm no out-of-range score exception occurs.

## Benchmark evidence

- [ ] Show the Day 17 metrics JSON.
- [ ] Show the final benchmark log.
- [ ] Explain the distinction between accuracy, precision, and recall.
- [ ] Explicitly disclose the 20% recall result and the four false negatives.

## Before committing

- [ ] Confirm the intended files are staged.
- [ ] Confirm `git diff --cached --check` reports no whitespace errors.
- [ ] Keep empty placeholder Python files and backup files out of the commit.
- [ ] Do not commit until the staged changes have been reviewed.

## Demonstration limitation

This system is for supervised demonstration only until recall, extraction quality, persistence, security, monitoring, and production reliability have been improved and validated.
