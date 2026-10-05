# Zecpath AI System — Day 16 ATS API Specification

**Project:** Zecpath AI System  
**Organization:** Zecser Technology  
**Day:** 16  
**Focus:** ATS API Design & Integration Planning  
**Status:** Design Specification

---

# 1. Objective

Day 16 focuses on making the ATS AI system consumable by backend
systems through a clearly defined REST API architecture.

The API layer is designed to expose the existing ATS capabilities
developed in previous stages:

- Resume upload
- Resume parsing
- ATS scoring
- Candidate ranking and shortlisting

The API design also defines asynchronous job handling,
request/response contracts, error standards, and logging standards.

---

# 2. Existing ATS Components

The API is intended to consume the existing Zecpath processing
pipeline rather than duplicate its internal logic.

| Existing component | API responsibility |
|---|---|
| Resume extraction | Input processing |
| Resume parsing | Candidate profile generation |
| Skill extraction | Candidate skill analysis |
| Experience analysis | Experience relevance |
| Education analysis | Education alignment |
| Semantic matching | Semantic similarity |
| ATS scoring | Candidate score generation |
| Candidate ranking | Score-based ranking |
| Shortlisting | Shortlist/review/reject classification |

---

# 3. Proposed API Architecture

```text
                   Client / Frontend
                          |
                          v
                 +------------------+
                 |   ATS REST API   |
                 +------------------+
                          |
             +------------+------------+
             |            |            |
             v            v            v
        Resume API    Processing    Shortlisting
             |            |            |
             +------------+------------+
                          |
                          v
                Zecpath ATS Engine
                          |
       +------------------+------------------+
       |                  |                  |
       v                  v                  v
    Parsing          Day 13 Scoring      Day 14 Ranking
       |                  |                  |
       +------------------+------------------+
                          |
                          v
                  Recruiter Output