# Test Case Generation Agent

An AI QA agent that turns product inputs into **structured, traceable, validated test cases**. It accepts requirements, user stories, acceptance criteria, PRDs, Confluence pages, Figma designs, API specs and existing test suites.

It works like an experienced QA engineer:
1. Works out what kind of input it has been given.
2. Extracts the requirements and business rules.
3. Asks about anything important that is missing.
4. Designs positive, negative, boundary, validation and edge-case scenarios.

Every suite then goes through deterministic checks for missing fields, vague expected results, duplicates, coverage gaps and broken traceability before it is returned.

You can use it in two ways:

- **In Claude Code:** run `/generate-test-cases <file, folder or pasted text>` and get Markdown, CSV and JSON reports.
- **From Slack:** type `/test-case`, paste a description plus Confluence, Figma or PRD links, and get a Google Sheet of test cases back. Every run is also saved to a versioned **knowledge base** in Google Sheets, so later runs reuse and update tests instead of starting over.

---

## Features

- **Input classification:** REQUIREMENT, USER_STORY, ACCEPTANCE_CRITERIA, FEATURE_DESCRIPTION, PRD, BRD, TECHNICAL_SPEC, API_SPEC, UI_DESIGN, EXISTING_TEST_CASES, PLAIN_TEXT, or UNKNOWN.
- **Requirement extraction:**
  - Keeps the source's own IDs (FR-6, AC2…).
  - Every item records where it came from and whether it is stated, observed, inferred or clarified.
- **Clarification gate:** if important information is missing, the agent asks before generating instead of inventing behaviour.
- **Scenario design:** uses equivalence partitioning, boundary values (min-1/min/max/max+1), decision tables, state transitions and error guessing.
- **Test case fields:** ID, source refs, feature, title, description, type, priority, preconditions, test data, steps, expected result and postconditions.
- **Deterministic quality gate** (`qa_tools`): schema checks, unique IDs, vague-wording detection, duplicate and near-duplicate detection, coverage of every acceptance criterion and business rule, and a traceability matrix.
- **Reviewing existing suites:** finds duplicates, weak steps, vague results and missing negative or boundary cases, then improves them.
- **Slack bot:**
  - One form with a feature name and feature context. Links to Confluence (including short links and child pages), Figma (exported as screen images), Google Docs and public pages are read automatically.
  - Links that can't be opened prompt you to paste their content.
- **Google Sheets output:** a fresh sheet per run with Test type and Priority (P0–P3) dropdowns and a colour-coded Change column.
- **Knowledge base:**
  - One tab per feature; people edit test cases there.
  - Edits by a person are detected and never overwritten. When requirements change, those tests are flagged "Needs review" with the AI's suggested update.
  - Version-to-version changes are computed by the bot itself: unchanged, updated, added or obsolete.
- **Choice of AI:**
  - **Claude**, through the Claude Agent SDK, runs the skill with locked-down tools.
  - **Google Gemini's** free tier is also supported, with model fallback and automatic fix rounds.

## How it works

```
Input ─► Classify ─► Extract requirements ─► Clarify (gate) ─► Design scenarios ─► Write test cases
                                                                                         │
     Report ◄── Export (MD / CSV / JSON / Google Sheet) ◄── Coverage ◄── Validate + de-duplicate (qa_tools)
```

The judgement work (classification, extraction, scenario design, writing) is done by the AI, following the workflow and skill prompts in `workflows/` and `skills/`. Everything that must be repeatable (validation, duplicates, coverage, export, version diffs) is done by plain Python in `qa_tools/` and `slack_bot/kb/`. The AI's output is only accepted once those checks pass.

### Slack flow

```
/test-case ─► form (name + context with links) ─► bot reads Confluence / Figma / docs
          ─► (paste screen for unreadable links) ─► knowledge base briefing (previous version, similar tests)
          ─► Gemini or Claude writes the suite ─► qa_tools checks + fix rounds ─► record version in knowledge base
          ─► reply in channel: link to the new Google Sheet + what changed
```

## Quick start

### 1. Use it in Claude Code (no extra setup)

Requirements: [Claude Code](https://claude.com/claude-code) and Python 3.10+. `qa_tools` uses only the standard library.

```bash
git clone https://github.com/pratik-8070/test-case-generation-agent.git
cd test-case-generation-agent
claude
```

Then, inside Claude Code:

```
/generate-test-cases resources/examples/login.md
```

Results are written to `output/<date>-<name>/` as `input-analysis.json`, `test-suite.json`, `test-suite.md` and `test-suite.csv`.

### 2. Run the Slack bot

```bash
python3 -m venv .venv
.venv/bin/pip install -r slack_bot/requirements.txt
cp slack_bot/.env.example .env      # then fill in the values
.venv/bin/python -m slack_bot.app
```

Set up the Slack app from [`slack_bot/manifest.yaml`](slack_bot/manifest.yaml). The full guide is in [`slack_bot/README.md`](slack_bot/README.md). It covers:
- Slack tokens, including automatic renewal for apps with token rotation
- choosing Claude or Gemini
- Confluence and Figma tokens
- connecting Google Sheets and the knowledge base
- channel restrictions

| Setting (`.env`) | Purpose |
|---|---|
| `SLACK_BOT_TOKEN`, `SLACK_APP_TOKEN` | Slack bot and Socket Mode connection |
| `SLACK_APP_CLIENT_ID`, `SLACK_APP_CLIENT_SECRET`, `SLACK_APP_REFRESH_TOKEN` | Renew rotating Slack app tokens automatically |
| `LLM_PROVIDER` | `claude` (Anthropic API) or `gemini` (free tier) |
| `ANTHROPIC_API_KEY` / `GEMINI_API_KEY` | AI provider key |
| `CONFLUENCE_EMAIL`, `CONFLUENCE_API_TOKEN`, `CONFLUENCE_SITES` | Read linked Confluence pages |
| `FIGMA_TOKEN` | Export linked Figma screens |
| `ALLOWED_CHANNELS` | Channels where `/test-case` works |

Google Sheets is connected once with `.venv/bin/python -m slack_bot.google_sheets auth`. It uses the `drive.file` scope only, so the bot can access only the files it creates.

## Project structure

```
.claude/skills/generate-test-cases/   /generate-test-cases entry point (Claude Code skill)
workflows/                            the stage-by-stage pipeline and its gates
skills/                               QA skill prompts: classification, extraction, clarification,
                                      scenario design, test case writing, duplicates, coverage,
                                      plus input handlers for PRDs, API specs, UI designs, existing tests
schemas/                              JSON schemas for the input analysis and the test suite
qa_tools/                             deterministic checks: schema, quality rules, de-dupe, coverage, export
slack_bot/                            Slack front end: form, link reading (Confluence/Figma/docs),
                                      Claude / Gemini runners, Google Sheets export
slack_bot/kb/                         knowledge base: feature matching, version merge rules, search, storage
resources/                            test design technique reference, report template, example inputs
output/                               generated runs (examples included)
tests/                                unit tests and agent evals
CLAUDE.md                             project rules for the agent
```

## Testing

```bash
python3 -m unittest discover tests                  # tooling tests (standard library)
.venv/bin/python -m unittest discover tests         # all 152 tests, including Slack, Gemini and knowledge base
python3 tests/agent_evals/check_run.py --all        # check example runs against expectations
```

The examples in `resources/examples/` cover a login story, a homepage description, add-to-cart acceptance criteria, an OpenAPI spec, a multi-feature PRD, an existing test suite, and a deliberately vague input that must stop at the clarification gate.

## Security notes

- **Secrets:** they live in `.env`, `.google_token.json`, `google_client_secret.json` and `.slack_app_token.json`. All four are gitignored.
- **The AI never gets network access.** The bot fetches links itself, and fetched content is passed to the AI as data, never as instructions.
- **Link fetching refuses** private or internal addresses, and caps downloads at 25 MB.
- **Claude runs with an allow-list of tools.** Bash is restricted to `python3 -m qa_tools …`, and each run has a budget cap.
- **Gemini's free tier** may use prompts to improve Google's products. Don't send confidential documents through it.

## Status

This is a working prototype, used with a Slack workspace, Confluence Cloud, Figma and Google Sheets. Planned extensions are listed in `CLAUDE.md`, under "Future Extensions": Jira and test-management integration, an RTM export, and Playwright or Selenium generation.
