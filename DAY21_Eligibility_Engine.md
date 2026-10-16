# Day 21 — Eligibility Decision Engine

## 1. Objective

Day 21 adds a rules-based eligibility decision engine to the Zecpath AI System.

The engine evaluates a candidate against configurable role requirements after retrieving the candidate's resume and calculating the ATS score.

The decision considers the configured ATS score threshold, mandatory skills, and additional requirements such as experience, location, and availability when those rules and inputs apply.

## 2. Main Features

- Role-specific eligibility rules loaded from JSON configuration.

- ATS score threshold validation.

- Mandatory skill checking.

- Skill alias normalization to handle common variations in skill names.

- Optional experience, location, and availability checks.

- Review handling for missing required information.

- FastAPI endpoint for evaluating resume eligibility.

- Automated tests for the eligibility decision engine.

## 3. Files Added or Modified

| File | Purpose |

|---|---|

| `eligibility/config.py` | Loads eligibility rules for the requested role. |

| `eligibility/decision\_engine.py` | Evaluates candidate information against configured rules. |

| `eligibility/\_\_init\_\_.py` | Initializes the eligibility package. |

| `configs/eligibility\_rules.json` | Stores role-specific eligibility requirements. |

| `api/eligibility\_schemas.py` | Defines request and response schemas. |

| `api/eligibility\_routes.py` | Implements the eligibility API route. |

| `api/main.py` | Registers the eligibility router with the FastAPI application. |

| `tests/test\_eligibility\_engine.py` | Tests eligibility rules and decision behavior. |

## 4. API Endpoint

\*\*Method:\*\* `POST`

\*\*Endpoint:\*\*

`/api/v1/resumes/{resume\_id}/eligibility`

The `resume\_id` identifies the uploaded resume to evaluate.

### Example request

```json

{

&#x20; "job\_description\_id": "JD-000001",

&#x20; "role": "python\_developer"

}

```

Additional optional request fields include:

- `experience\_years`

- `location`

- `availability\_confirmed`

These fields can supply candidate information used by applicable eligibility rules.

### Example using the API documentation

1\. Start the FastAPI application.

2\. Open `/docs` in the browser.

3\. Locate the eligibility endpoint.

4\. Select \*\*Try it out\*\*.

5\. Enter the resume ID and request body.

6\. Execute the request and inspect the response.

## 5. How the Engine Works

1\. The API receives the resume ID and eligibility request.

2\. The application retrieves the stored resume.

3\. The route checks that parsed profile information is available.

4\. The role-specific eligibility rules are loaded.

5\. The ATS scoring service calculates the candidate's score.

6\. Candidate information, including parsed skills and supplied optional details, is passed to the decision engine.

7\. The engine evaluates the configured rules.

8\. The API returns a decision, reasons, passed rules, failed rules, and review information.

### Workflow

```text

Eligibility API Request

&#x20;         |

&#x20;         v

Retrieve Stored Resume

&#x20;         |

&#x20;         v

Load Role-Specific Rules

&#x20;         |

&#x20;         v

Calculate ATS Score

&#x20;         |

&#x20;         v

Evaluate Eligibility Rules

&#x20;         |

&#x20;         v

Return Decision and Reasons

```

## 6. Rule Configuration

Eligibility requirements are maintained in:

`configs/eligibility\_rules.json`

For the configured Python Developer example, the rules include:

- Minimum ATS score: `0.70`

- Mandatory skills: `Python` and `REST API`

The threshold is represented as a normalized score between 0 and 1.

A score of `0.70` corresponds to 70% on that scale. A candidate scoring below the threshold fails the configured minimum-score rule.

The actual decision also depends on other configured requirements and whether the information necessary to evaluate them is available.

## 7. Skill Alias Normalization

Skill names may be written in different forms. The engine normalizes supported aliases before checking mandatory skills.

Examples include:

| Input skill | Normalized skill |

|---|---|

| `REST APIs` | `REST API` |

| `RESTful API` | `REST API` |

| `RESTful APIs` | `REST API` |

This prevents supported naming variations from being treated as different skills during mandatory-skill validation.

Alias normalization improves consistency, but it does not guarantee that every semantically similar skill will be recognized.

## 8. Example API Result

During manual API validation, the following result was returned for a Python Developer eligibility request:

- Decision: `REJECTED`

- ATS score: `0.5962`

- Minimum ATS score: `0.700`

- Mandatory skills: Passed

- Review required: `false`

The response reported that all configured mandatory skills were found, but the ATS score was below the minimum threshold.

The score was approximately 59.62%, which is 10.38 percentage points below the configured 70% threshold.

Therefore, the engine rejected this test candidate under the configured rules.

This result demonstrates the API workflow; it does not establish the fairness or accuracy of the hiring decision.

## 9. Testing and Validation

### Focused eligibility tests

Command:

```powershell

python -m pytest .\\tests\\test\_eligibility\_engine.py -q

```

Result:

`20 passed`

### Python syntax compilation

Command:

```powershell

python -m py\_compile .\\api\\main.py .\\api\\eligibility\_routes.py .\\api\\eligibility\_schemas.py .\\eligibility\\config.py .\\eligibility\\decision\_engine.py

```

Result: Completed without reported syntax errors.

### Full project test suite

Command:

```powershell

python -m pytest -q

```

Result:

`20 passed in 16.26s`

### Git whitespace validation

Command:

```powershell

git diff --check

```

Result: No whitespace errors reported. Git displayed a line-ending warning for `api/main.py`; this warning did not affect the tests.

## 10. Current Limitations

- Resume data is stored in memory by the current API implementation. Restarting the server may clear uploaded resume records, requiring the test resume to be uploaded again.

- Resume parsing can produce incomplete or incorrectly merged fields, including experience and education.

- Eligibility decisions depend on the quality of parsed resume data and the correctness of the configured rules.

- Passing automated tests does not prove production readiness.

- Eligibility output should be reviewed by a human before being used for real recruitment decisions.

## 11. Day 21 Summary

Day 21 adds a configurable rules-based eligibility engine to the existing ATS system.

The new API evaluates candidate information against role-specific requirements and returns a structured decision with reasons and rule results.

The focused eligibility test suite and the full project test suite both passed with 20 tests.

Further work should focus on improving resume parsing reliability, expanding test coverage for the API and decision scenarios, and ensuring that eligibility results are transparent and appropriately reviewed.
