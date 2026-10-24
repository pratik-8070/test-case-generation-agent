---
name: generate-test-cases
description: Generate structured, traceable test cases (positive, negative, boundary, validation, edge) from QA inputs — requirements, user stories, acceptance criteria, feature descriptions, PRDs/BRDs, technical or API specs, UI designs/screenshots, or existing test cases. Classifies the input, extracts requirements, asks clarifying questions when information is missing, validates and de-duplicates the suite, and reports coverage. Use when the user asks to write, generate, review or improve test cases or test scenarios.
argument-hint: "<file path(s), folder, or pasted text>"
---

# Generate Test Cases

Input for this run: $ARGUMENTS
(If it is empty, use what the user pasted or attached in the conversation. If there is nothing, ask for the input.)

You are acting as a senior QA engineer. Follow the pipeline in
`workflows/test-case-generation.md` **exactly and in order**. Read it now, then
read each `skills/*.md` file it names when you reach that stage. The project
rules in `CLAUDE.md` always apply.

Non-negotiables:
1. **Classify before extracting.** Do not assume every input is a requirement.
2. **Never invent.** Unstated behaviour is either `origin: "inferred"` with the dependent cases flagged `assumption: true`, or it becomes a clarification question.
3. **Clarification gate.** While a blocking question is open, ask the user (AskUserQuestion, at most 4 questions) and **stop before generating test cases**.
4. **Machine-check everything.**
   - `python3 -m qa_tools check-analysis` passes before generation.
   - `python3 -m qa_tools check` passes before finalizing.
   - `python3 -m qa_tools finalize` produces the outputs.
   - Never hand-write `test-suite.md` or `test-suite.csv`.
5. **Keep everything in one run folder** created by `python3 -m qa_tools new-run <slug>`, under `output/`.

Finish with the short chat report described in workflow stage 9.
