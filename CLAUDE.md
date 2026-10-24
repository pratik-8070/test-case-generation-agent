# Project Context

This project is an AI-powered Test Case Generation Agent built using
Claude Code. The agent is designed to analyze different types of QA and
product inputs and generate structured, comprehensive test cases.

The main goal is to reduce manual effort in test case creation while
improving functional, negative, boundary, validation, and edge-case
coverage.

# About This Project

The agent accepts different types of inputs such as:

-   Requirements
-   User Stories
-   Acceptance Criteria
-   Feature Descriptions
-   PRDs / Product Requirement Documents
-   BRDs / Functional Specifications
-   Technical Specifications
-   API Specifications
-   API Documentation
-   UI Designs or Screenshots
-   Existing Test Cases
-   Plain-text feature descriptions

The agent first identifies the type of input, extracts relevant
information, understands the functionality, and then generates
appropriate test cases.

# Core Rules

-   First understand and classify the input before generating test
    cases.
-   Do not assume that every input is a requirement.
-   Do not invent requirements, business rules, validations, APIs, or
    functionality.
-   If important information is missing, clearly mention it or ask for
    clarification.
-   Generate meaningful test coverage instead of producing unnecessary
    test cases.
-   Cover positive, negative, boundary, validation, and edge scenarios
    where applicable.
-   Maintain traceability between generated test cases and the source
    requirement or document.
-   Avoid duplicate or overlapping test cases.
-   Keep test steps clear, actionable, and easy for a QA engineer to
    execute.
-   Expected results must be specific and verifiable.
-   Use consistent IDs, priorities, and test types.
-   Validate the generated output before returning it.
-   Keep the implementation modular so additional QA capabilities can be
    added later.

# Agent Workflow

The agent should follow this workflow:

Input → Input Type Detection → Input / Document Parsing → Requirement
Extraction → Feature and Business Rule Identification → Scenario
Identification → Test Case Generation → Duplicate Detection → Output
Validation → Coverage Analysis → Structured Test Case Output → QA
Summary

# Input Classification

Supported input types include:

-   REQUIREMENT
-   USER_STORY
-   ACCEPTANCE_CRITERIA
-   FEATURE_DESCRIPTION
-   PRD
-   BRD
-   TECHNICAL_SPEC
-   API_SPEC
-   UI_DESIGN
-   EXISTING_TEST_CASES
-   PLAIN_TEXT
-   UNKNOWN

If the input is ambiguous, do not make assumptions. Ask for
clarification when necessary.

# Requirement Analysis

For every input, extract the following information when available:

-   Feature name
-   Requirement
-   Requirement ID
-   User role
-   Business rules
-   Acceptance criteria
-   Preconditions
-   Dependencies
-   Inputs
-   Expected behavior
-   Validations
-   Error conditions
-   Boundary conditions
-   Data requirements
-   UI behavior
-   API behavior
-   Authentication and authorization requirements
-   External dependencies

For documents such as PRDs, identify individual features and
requirements before generating test cases.

# Test Scenario Coverage

Generate relevant scenarios for:

-   Positive flows
-   Negative flows
-   Boundary conditions
-   Edge cases
-   Field validations
-   Business rules
-   Error handling
-   Authentication
-   Authorization and role permissions
-   Data validation
-   UI behavior
-   API behavior
-   Integration behavior
-   Session handling
-   Security-related behavior when explicitly relevant
-   Compatibility or responsive behavior for UI features when applicable

Do not generate irrelevant scenarios simply to increase test case count.

# Test Case Structure

Each test case should contain:

-   Test Case ID
-   Requirement / Source Reference
-   Feature
-   Scenario
-   Test Type
-   Priority
-   Preconditions
-   Test Data
-   Test Steps
-   Expected Result
-   Postconditions when applicable

Use a consistent structured schema internally so the output can be
consumed by other tools or agents.

# Traceability

Every test case should be traceable to its source.

For example:

Requirement → Acceptance Criterion → Test Case

For PRDs and other documents, include the relevant section or
requirement reference whenever possible.

# Duplicate Detection

Before returning the final result:

-   Identify duplicate test cases.
-   Identify overlapping scenarios.
-   Merge redundant cases where appropriate.
-   Ensure every final test case adds meaningful coverage.

# Output Validation

Validate every generated test suite for:

-   Required fields
-   Unique test case IDs
-   Clear test steps
-   Specific expected results
-   Correct test type
-   Consistent priority
-   Requirement traceability
-   Duplicate scenarios
-   Unsupported assumptions
-   Missing important coverage

# Coverage Analysis

After generation, perform a coverage check.

Verify coverage of:

-   Every acceptance criterion
-   Every stated business rule
-   Positive flows
-   Negative flows
-   Boundary conditions
-   Important validations
-   Error handling
-   Roles and permissions where applicable

Provide a short summary containing:

-   Requirements identified
-   Acceptance criteria identified
-   Total test cases
-   Positive cases
-   Negative cases
-   Boundary cases
-   Edge cases
-   Validation cases
-   Coverage gaps

# Input-Specific Behavior

## Requirement or User Story

Extract the requirement and acceptance criteria and generate relevant
test cases.

## PRD

Read and analyze the document, identify features and requirements,
divide them into testable units, and generate test cases for each
relevant feature.

## API Specification

Identify endpoints, HTTP methods, parameters, headers, authentication,
request body, response body, status codes, validations, and error
conditions.

Generate API-specific positive, negative, boundary, validation, and
error scenarios.

## UI Design or Screenshot

Identify visible fields, buttons, links, navigation, UI states, and
validations that can reasonably be inferred.

Clearly distinguish observed behavior from assumptions.

## Existing Test Cases

Analyze existing cases for:

-   Missing coverage
-   Duplicate cases
-   Weak scenarios
-   Missing negative cases
-   Missing boundary cases
-   Missing validation

Generate additional or improved cases where required.

## Multiple Inputs

Combine the information from all inputs, resolve duplicates, maintain
traceability, and generate a unified test suite.

# Quality Standards

The agent should behave like an experienced QA engineer.

Do not simply convert sentences into test cases.

Understand the functionality first, identify potential risks, and then
create meaningful test coverage.

Prefer quality and coverage over quantity.

Never present an assumption as a confirmed requirement.

# How to Run

    /generate-test-cases resources/examples/login.md      # or any file(s), folder, or pasted text

Entry point: `.claude/skills/generate-test-cases/SKILL.md`. It drives
`workflows/test-case-generation.md`, which loads the `skills/` files stage by stage.

Tooling (Python 3.10+, standard library only):

    python3 -m qa_tools new-run <slug>                 # create output/<date>-<slug>/
    python3 -m qa_tools check-analysis <run>/input-analysis.json
    python3 -m qa_tools check    <run>/test-suite.json # validate + dedupe + coverage gate
    python3 -m qa_tools coverage <run>/test-suite.json
    python3 -m qa_tools finalize <run>/test-suite.json # check, store coverage, export .md + .csv
    python3 -m unittest discover tests                 # tooling unit tests
    python3 tests/agent_evals/check_run.py --all       # agent evals vs. latest example runs

# Project Structure

-   .claude/skills/generate-test-cases/ --- slash-command entry point
    (kept thin)
-   workflows/ --- the stage-by-stage pipeline, with its gates
-   skills/ --- reusable QA skill prompts, one concern per file;
    `skills/input-handlers/` holds the type-specific extraction rules
-   schemas/ --- `input-analysis.schema.json` and `test-suite.schema.json`
    (the internal contract)
-   qa_tools/ --- deterministic checks: schema, quality rules, de-dupe,
    coverage, export
-   slack_bot/ --- `/test-case` Slack front end: a Bolt modal, a
    headless run of the same skill through the Claude Agent SDK, and the
    results posted to the channel (see `slack_bot/README.md`).
    `slack_bot/kb/` is the knowledge base: one Google Sheet with Tests and
    PRD tabs per feature (model, store), feature matching and version merge rules
    (merge), keyword + ID search, and the reuse briefing given to the agent
-   resources/ --- the technique reference, the report template
    (`templates/`) and sample inputs (`examples/`)
-   output/ --- one folder per run: `input-analysis.json`,
    `test-suite.json`, `test-suite.md` and `test-suite.csv`
-   tests/ --- unit tests for qa_tools (`test_*.py`, `fixtures/`) and agent
    evals (`agent_evals/`)
-   CLAUDE.md --- project context and agent rules

# Implementation Decisions

-   **Split of responsibility.** Claude does the judgement work:
    classification, extraction, clarification, scenario design and
    writing. `qa_tools` does every check that must be repeatable:
    required fields, unique IDs, vague wording, trace refs,
    duplicates, coverage holes and export. The agent may not export
    while `check` reports errors.
-   **Standard library only.** Nothing needs a `pip install`.
    `qa_tools/schema.py` implements the JSON Schema subset the
    schemas use. Swap in `jsonschema` if dependencies become
    acceptable.
-   **Traceability.** Source IDs are kept verbatim. Missing IDs are
    assigned as `REQ-001`, `AC-001.1` and `BR-001`. Test cases
    reference the most specific item, and covering an AC or BR rolls
    up to its parent requirement.
-   **Honest assumptions.** Every extracted item has an `origin`
    (`stated`, `observed`, `inferred` or `clarified`). Cases that
    depend on inferred items must set `assumption: true` with
    `assumption_refs`, and the validator enforces this.
-   **Accepted coverage gaps.** An uncovered AC, BR or requirement is
    an error unless it is listed in `coverage_summary.gaps` with a
    `ref` and a reason.
-   **IDs, types and priorities.** IDs are `TC-<FEATURE_CODE>-<NNN>`.
    Test types are a fixed enum of 14. Priorities are
    Critical/High/Medium/Low, applied with the rubric in
    `skills/test-case-writing.md`.
-   **Knowledge base.** One Google Sheet, "Test Case Knowledge Base",
    with one visible tab per feature ("Test Cases – <feature> vN –
    <date>", renamed each run): the source of truth for that feature's
    tests; people edit there. Hidden tabs hold the bot's bookkeeping:
    Features, "<feature> – PRD" (requirements, for change detection) and
    Change Log. A hidden
    fingerprint column detects human edits, and edited ("Reviewed") tests
    are never overwritten, only flagged "Needs review". Version diffs are
    computed by the bot, not reported by the agent.
-   **Adding a capability.** Add a skill file, wire it into the
    workflow, and if it needs a new deterministic check, add a
    `qa_tools` module with tests. Future exporters, such as an RTM
    or Jira, should read `test-suite.json` and not re-derive it.

# Future Extensions

Keep the architecture extensible for future capabilities such as:

-   Jira integration
-   Test management integration
-   Excel or CSV export
-   Requirement Traceability Matrix generation
-   API test generation
-   Playwright test generation
-   Selenium test generation
-   Automated regression suite generation
-   Test case prioritization
-   Defect generation from failed test cases

Do not implement future integrations unless specifically requested.

# Testing the Agent

Validate the agent using at least these examples:

1.  Login feature
2.  Homepage feature
3.  Add to Cart feature
4.  API endpoint
5.  Small PRD containing multiple features
6.  Existing test case set
7.  A deliberately vague input (must stop at the clarification gate)

For each example verify:

-   Correct input classification
-   Correct requirement extraction
-   Relevant scenario generation
-   Structured test case output
-   Duplicate detection
-   Output validation
-   Coverage analysis
-   Requirement traceability

# Development Rules

-   Inspect the existing project before creating new files.
-   Follow existing naming conventions.
-   Reuse existing utilities and schemas where possible.
-   Keep prompts and business logic modular.
-   Do not duplicate functionality already available in the framework.
-   Keep generated artifacts inside the appropriate output directory.
-   Document important implementation decisions.
-   Test changes before considering the skill complete.