# Skill: Input Classification

Decide what kind of artifact each input is **before** extracting anything.
Do not assume that every input is a requirement.

## Types and signals

| Type | Strong signals |
|---|---|
| `USER_STORY` | "As a <role>, I want <goal> so that <benefit>"; story IDs such as US-12; may carry an AC list |
| `ACCEPTANCE_CRITERIA` | Only criteria: Given/When/Then, a numbered "AC" list, or "should/must" bullets with no story or context |
| `REQUIREMENT` | "The system shall/must…"; REQ- or FR- IDs; one or a few atomic statements |
| `FEATURE_DESCRIPTION` | Narrative prose about one feature: what it does and how it looks, with no formal structure |
| `PRD` | Many features; sections such as Overview, Goals, Personas, Scope/Out of scope, Requirements, Metrics, Release |
| `BRD` | Business objectives, stakeholders, business process or rules, business requirement IDs (BR-), little UI or tech detail |
| `TECHNICAL_SPEC` | Architecture, components, data models, sequence flows, DB tables, events and queues, non-functional targets |
| `API_SPEC` | OpenAPI/Swagger keys (`openapi:`, `paths:`), HTTP verbs plus paths, request and response schemas, status codes, Postman collections |
| `UI_DESIGN` | Image or screenshot input, Figma export, wireframe description, a list of screens, fields and buttons |
| `EXISTING_TEST_CASES` | Columns or fields such as Test Case ID, Steps, Expected Result; Gherkin `.feature` files; TestRail, Xray or Zephyr exports |
| `PLAIN_TEXT` | An informal sentence or paragraph about behaviour, such as "users should be able to reset passwords" |
| `UNKNOWN` | No QA-relevant signals, or several types that are equally plausible |

## Rules

1. Choose **one** primary type based on the dominant structure.
   - Put embedded types in `secondary_types`. A PRD with user stories inside is `PRD` with secondary `USER_STORY`.
   - A story whose AC list is attached is `USER_STORY`, not `ACCEPTANCE_CRITERIA`.
2. Set `confidence`:
   - `high`: several strong signals and no competing type.
   - `medium`: signals are present but the input is thin or mixed.
   - `low`: you are mostly guessing. Low confidence and `UNKNOWN` **must** raise a blocking clarification.
3. Write `evidence` as concrete quotes or observations, such as `"'paths:' block with /orders"`. Never write "looks like an API".
4. Classify every input separately. Merging is a later step (`input-handlers/multi-input.md`).
5. Classification only decides how to read the input. It never adds requirements.
