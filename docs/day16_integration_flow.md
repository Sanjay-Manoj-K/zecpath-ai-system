# Zecpath AI System — Day 16 Integration Flow

**Project:** Zecpath AI System  
**Organization:** Zecser Technology  
**Day:** 16  
**Focus:** ATS API Integration Flow  
**Status:** Design Complete

---

# 1. Purpose

This document describes how the REST API layer will interact with
the existing Zecpath ATS processing components.

The goal is to make the ATS AI functionality consumable by backend
systems while keeping the existing ATS processing logic separate
from the API layer.

---

# 2. High-Level Integration

```text
+----------------------+
| Client / Frontend    |
+----------+-----------+
           |
           | HTTPS / REST
           v
+----------------------+
|      ATS API         |
|      /api/v1         |
+----------+-----------+
           |
           v
+----------------------+
| Request Validation   |
| Pydantic Schemas     |
+----------+-----------+
           |
           v
+----------------------+
| ATS Service Layer    |
+----------+-----------+
           |
           +-----------------------------+
           |              |              |
           v              v              v
       Resume          Parsing        Processing
       Storage           |              |
                         v              |
                  Candidate Profile     |
                                        |
                         +--------------+
                         |
                         v
                 Day 9–12 Analysis
                         |
                         v
                  Day 13 ATS Score
                         |
                         v
                  Day 14 Ranking
                         |
                         v
             Shortlist / Review / Reject
                         |
                         v
                  API Response