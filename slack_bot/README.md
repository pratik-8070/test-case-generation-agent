# Slack bot: `/test-case`

Type `/test-case` in a channel to open a form. Fill in **Feature name** and **Feature context** (both required). Feature context holds the description *and* every reference link: Figma, Confluence, PRD, RFC, docs. Pick a **format** (Markdown / CSV / JSON) and click **Generate**. The bot posts a summary in the channel and attaches the full test suite in a thread.

```
/test-case ─► modal ─► bot posts "⏳ Generating…"
                       └► Claude Agent SDK runs /generate-test-cases on the input
                          (same workflow, skills and qa_tools checks as Claude Code)
                       └► bot re-checks output/<run>/ with qa_tools
                       └► message updated with summary + file attached in thread
```

## One-time setup (about 10 minutes)

1. **Create the Slack app.**
   - Go to <https://api.slack.com/apps>, then **Create New App → From a manifest**.
   - Pick your workspace and paste [`manifest.yaml`](manifest.yaml). Click **Create**.
2. **Create an app-level token.**
   - Go to **Basic Information → App-Level Tokens → Generate Token and Scopes**.
   - Add the scope `connections:write` and generate. Copy the `xapp-…` token.
3. **Install the app.**
   - Go to **Install App → Install to Workspace**.
   - Copy the **Bot User OAuth Token** (`xoxb-…`).
4. **Get an Anthropic API key** from <https://console.anthropic.com>.
5. **Configure** from the project root:
   ```bash
   cp slack_bot/.env.example .env      # then fill in the 3 tokens
   python3 -m venv .venv && .venv/bin/pip install -r slack_bot/requirements.txt
   ```
6. **Run** from the project root:
   ```bash
   .venv/bin/python -m slack_bot.app
   ```
   Wait for `⚡️ Bolt app is running!`. The bot uses Socket Mode, so it needs no public URL and works from your Mac.
7. **Private channels only:** run `/invite @Test Case Generator`. In public channels the bot can post without an invite.

## Reference material: links and files

Paste links anywhere in **Feature context**, mixed with your own text. Feature context can even be just one link. When you click **Generate**, the form shows *"Opening N links…"* while the bot reads each one:

1. **Every link readable:** generation starts and the form says where results will be posted.
2. **Some links unreadable:** the form switches to *"I couldn't open N of your links/files"*. It lists each one with the reason (needs sign-in, not shared, page not found, no Figma token…) and a box to **paste its content**. Leave a box empty to skip that link, then click **Generate**. Pasted text is saved with the run and treated like the page it replaces.
3. **Nothing readable and no other description:** the form asks you to paste at least one link's content before it continues, so the agent never runs on an empty input. Nothing is charged until then.

What the bot can open:

  | Link | What happens |
  |---|---|
  | Confluence Cloud (`…atlassian.net/wiki/spaces/…/pages/<id>/…`, `…/wiki/x/<code>` short links, `?pageId=`) | The bot reads the page through the Confluence REST API, as rendered HTML with macros expanded, and saves it as text, with tables kept as rows. It also reads up to 5 **direct child pages**, because hub pages usually keep the PRD and RFC one level down. The agent treats them as the main requirements source. **Needs `CONFLUENCE_EMAIL` + `CONFLUENCE_API_TOKEN`.** |
  | Figma (`figma.com/design/…`, `/file/…`, `/proto/…`) | The bot exports the linked frame, or the first page's screens (up to 12; loose components are skipped), as PNG. The agent reads them as UI designs. **Needs `FIGMA_TOKEN`.** |
  | Google Doc shared as *Anyone with the link* | The bot exports it as text. |
  | Any other public page or file | HTML is converted to text. PDFs, images and text files are kept as they are. |
  | Private pages (Notion, internal wikis, unshared Google Docs, Confluence without a token) | Not readable. The form asks you to paste their content, or you can attach an export. |

Optionally, **Attachments** takes up to 10 files (PDF, PNG/JPG, DOCX, MD, TXT, CSV, JSON, YAML), such as PRD or RFC exports, Figma or screen exports, API specs and existing test cases. **Needs the `files:read` scope.**

Everything is saved to `output/<run>/attachments/` and passed to the agent as extra inputs, so the skill's multi-input handling and traceability apply. The reply in Slack says how many sources were read and which couldn't be, and why.

**Safety:**
- The *bot* fetches links, not the agent. The agent still has no network access, and attached content is treated as data, never as instructions.
- Links that resolve to private or internal addresses (localhost, 10.x, 192.168.x, cloud metadata) are refused.
- Downloads are capped at 25 MB each.

### Enabling uploads (one time)
1. At api.slack.com/apps, open your app and go to **OAuth & Permissions → Bot Token Scopes → Add `files:read`**.
2. Click **Reinstall to Workspace** at the top of the page. If the Bot User OAuth Token changes, update `SLACK_BOT_TOKEN` in `.env`.
3. Restart the bot. Its startup log line should say `uploads: on`.

### Enabling Confluence links

Paste the link in **Feature context**. It can be the whole field, for example `https://yoursite.atlassian.net/wiki/x/AQAL`.

1. Create an API token at <https://id.atlassian.com/manage-profile/security/api-tokens>:
   - **Create API token** (classic) works directly.
   - **Create API token with scopes** also works. Give it Confluence `read:page:confluence`, or the classic `read:confluence-content.all`. The bot routes scoped tokens through `api.atlassian.com` automatically.
2. In `.env`, set:
   - `CONFLUENCE_EMAIL` to the Atlassian account email
   - `CONFLUENCE_API_TOKEN` to the token
   - `CONFLUENCE_SITES` to your site (e.g. `yoursite.atlassian.net`), so the credentials are never sent anywhere else
3. Restart the bot. The log line should say `confluence: on (yoursite.atlassian.net)`.

The bot can read only the pages that Atlassian account can view. If the only input is a link the bot can't read, it replies with the reason straight away, without starting the agent or spending on it.

### Enabling Figma links (optional)
1. In Figma, go to **Settings → Security → Personal access tokens → Generate new token**.
2. Give the token the **File content: read** scope (`file_content:read`).
3. Add `FIGMA_TOKEN=figd_…` to `.env` and restart the bot. The log line should say `figma: on`.

The token can only read files its Figma account can open.

## Google Sheet output

When Google Sheets is connected, the form's format list gets a **Google Sheet (link)** option, selected by default. Each run creates a spreadsheet in your Drive folder **Test Case Generator**, and the Slack reply links to it.

**Sheet "Test Cases":** one row per test case. The columns are:

| Column | Notes |
|---|---|
| Test ID, Test title, Test description | |
| **Test type** | Dropdown: Positive, Negative, Boundary, Validation, Edge Case, UI, UI/UX, Security, API, Integration |
| **Priority** | Dropdown, colour-coded: P0, P1, P2, P3 (P0 = Critical, P1 = High, P2 = Medium, P3 = Low) |
| Preconditions | Bulleted |
| Test data | |
| Test steps | Numbered |
| Expected result | |
| Traces to | The requirement IDs |
| Feature | |

The header row is frozen and filterable, so you can sort and filter by type, priority or feature.

**Sheet "Summary":** counts, coverage, open questions and gaps.

Values are written as plain text, so nothing in a test case can run as a formula. If the sheet can't be created, the Markdown report is attached instead and the reply says why.

The bot only uses the `drive.file` permission, so it can see only the files it creates, not the rest of your Drive.

### One-time setup (about 10 minutes)
1. **Create a Cloud project.** Go to <https://console.cloud.google.com/>, click the project picker, choose **New project**, name it `Test Case Generator`, and create it.
2. **Enable the APIs.** Go to **APIs & Services → Library** and enable **Google Sheets API** and **Google Drive API**.
3. **Set up the consent screen.** Go to **Google Auth Platform**, or **APIs & Services → OAuth consent screen**, and click **Get started**:
   - App name: `Test Case Generator`. Support email: yours.
   - Audience: **External**. Contact email: yours. Agree, then **Create**.
   - Under **Audience**, click **Publish app** and confirm. While an app is in "Testing", Google expires its sign-in after 7 days. A personal-use app (under 100 users) doesn't need Google's verification; you'll just see an "unverified app" warning.
4. **Create a client.** Go to **Clients → Create client**, choose application type **Desktop app**, and create it. Click **Download JSON** and save the file as `~/my-first-agent/google_client_secret.json`.
5. **Connect your account.** From the project folder, run:
   ```bash
   .venv/bin/python -m slack_bot.google_sheets auth
   ```
   - A browser opens. Choose your Google account.
   - On "Google hasn't verified this app", click **Advanced → Go to Test Case Generator (unsafe)**. It's your own app.
   - Allow access. The terminal prints `Connected.`
6. **Restart the bot.** Its log line should show `google sheets: on`.

To try it on an existing run: `.venv/bin/python -m slack_bot.google_sheets test output/<run folder>`

`google_client_secret.json` and `.google_token.json` stay on your Mac and are gitignored.

## Knowledge base

Once Google Sheets is connected, every successful run is recorded in **Test Case Knowledge Base**, one spreadsheet in your `Test Case Generator` Drive folder, with **one tab per feature**:

```
[ Test Cases – Create Listing v2 – 2026-10-13 ] [ Test Cases – Test_99 v1 – 2026-10-15 ]
```

Each tab is the living copy of that feature's test cases, with Status ▾ (Active / Needs review / Obsolete), Origin (AI draft / Reviewed), Added in, Last changed in, Review note and Suggested update. **Edit test cases here.** The tab name updates to the latest version and date after each run, and a new feature gets a new tab.

The bot also keeps some **hidden tabs** for its own records. To see them, open ☰ **All sheets**:

| Hidden tab | Holds |
|---|---|
| **Features** | One row per feature, with its version, sources and links |
| **\<feature\> – PRD** | The feature's requirements, acceptance criteria and business rules, and how each changed. Used to detect what changed in the PRD. |
| **Change Log** | One row per run |

Each run also creates a read-only **Test Cases – \<feature\> vN – \<date\>** spreadsheet, with a colour-coded Change column. Its link is the main link in the Slack reply.

**How a run uses it:**
1. **Same feature?** A shared source (Confluence page, Figma file or document) means the same feature; with no links, the feature name decides.
2. **Briefing:** the AI receives the previous version's requirements and tests, plus similar tests from other features (found by keyword and ID search), and is told to reuse them: same IDs and wording for unchanged requirements, updates for changed ones, new tests for new ones.
3. **Recording:** the bot compares the result with the previous version itself, rather than trusting the AI:
   - Rewritten AI-draft tests become **updated**.
   - Tests whose requirements were all removed become **Obsolete**.
   - Tests the AI dropped while their requirement still exists are **kept**.
4. **Tests people edit:** any test a person edits becomes **Reviewed** (the bot detects edits through a hidden fingerprint column). Reviewed tests are never overwritten. If their requirement changes, they're set to **Needs review**, with the AI's proposal in *Suggested update*. A test a person marks Obsolete stays Obsolete.
5. **Slack reply:** shows what changed, for example `v3: 18 unchanged · 4 updated · 3 added · 1 obsolete · 2 need review`, with a link to that run's newly generated test cases sheet (the knowledge base itself is never linked from Slack).

**Adding tests by hand:** add a row to the feature's tab. A row without a Test ID gets one, such as `TC-MANUAL-001`, and counts as Reviewed.

**Command line:**
```bash
.venv/bin/python -m slack_bot.kb search "luxury price minimum FR-6"     # keyword + ID search
.venv/bin/python -m slack_bot.kb url                                     # knowledge base + each feature's tabs
.venv/bin/python -m slack_bot.kb backfill --name "Feature" output/<run> ...   # record older runs, oldest first
```

If the knowledge base can't be reached, the run still completes and the reply says so.

## Choosing the AI: Claude (paid) or Gemini (free tier)

Set `LLM_PROVIDER` in `.env`:

| | `claude` (default) | `gemini` |
|---|---|---|
| Cost | Anthropic API credits (about $1–4 per large run, capped by `AGENT_MAX_BUDGET_USD`) | Free within Google's daily limits (see your quota at aistudio.google.com/rate-limit) |
| How it runs | The Claude agent runs the skill itself, with tools: it reads files and runs `qa_tools` | Gemini gets the same workflow, skills and schemas and returns the analysis and suite as JSON. The bot runs `qa_tools` and sends errors back for up to 3 fix rounds, then exports. |
| Data | Not used for training | **Free tier: Google may use prompts and responses to improve its products, including human review. Don't send confidential documents.** |
| Setup | `ANTHROPIC_API_KEY` | `GEMINI_API_KEY` from <https://aistudio.google.com/apikey>, plus `pip install google-genai` (in `requirements.txt`) |

Both paths produce the same files and pass the same checks. If the free tier's daily limit is hit, the Slack reply says so, and you can try again after midnight Pacific time.

## Limiting it to channels

Set `ALLOWED_CHANNELS` in `.env` to one or more channel names or IDs, comma-separated, for example `ALLOWED_CHANNELS=alpha`. In any other channel, `/test-case` replies with a message only the caller can see, pointing to the allowed channel, and the form doesn't open. Leave it empty to allow every channel.

Prefer the channel **ID** (for example `C0123ABCD`) if the channel might be renamed: it stays the same when the name changes. To find it, open the channel, click its name, and look at the bottom of the **About** tab.

## Using it

- `/test-case` opens an empty form. `/test-case Add to Cart` pre-fills the feature name.
- **Feature context** holds everything about the feature: the requirement or story, acceptance criteria and rules. This is where precision pays off. Exact limits ("max 10 per item"), message texts, roles and out-of-scope items each turn into concrete boundary and negative tests instead of assumptions.
- **The bot never stops to ask questions.** Missing information becomes a flagged assumption. The reply lists the open questions; add the answers to *Feature context* and run `/test-case` again.
- **Output files:** every run is kept under `output/<date>-<feature>/` (input, analysis, all three formats). The thread names the folder.

## Safety and cost

- **Tool lockdown.** The agent runs with `permission_mode="dontAsk"` and an allow-list: Read, Write, Edit, Glob, Grep, Skill, and Bash restricted to `python3 -m qa_tools …`. Any other tool call is denied. `AskUserQuestion` is removed entirely.
- **Limits.** Each run is capped by `AGENT_MAX_BUDGET_USD` (default $5) and `AGENT_MAX_TURNS` (default 80). At most `MAX_CONCURRENT_RUNS` (default 2) runs execute in parallel.
- **No double posting of bad output.** The bot re-runs the `qa_tools` checks itself and only posts a suite that passes.
- **Who can use it.** Anyone in the workspace who can run `/test-case` can make the agent read and write files in this project. Run it from a dedicated checkout or machine if the workspace is large.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `/test-case` → "dispatch_failed" | The bot process isn't running, or `SLACK_APP_TOKEN` is wrong |
| Results arrive by DM | The bot isn't in that private channel: `/invite @Test Case Generator` |
| "agent stopped: error_max_budget_usd" or "error_max_turns" | The input is very large. Raise the limits in `.env` or split the feature |
| "failed validation" | The run folder is kept. Run `python3 -m qa_tools check output/<run>/test-suite.json` to see why |
| Log shows "tool calls denied by the lockdown" | The agent tried a tool outside the allow-list. Usually harmless; the logged call shows which |

Bot logic is unit-tested in `tests/test_slack_bot.py` without Slack or the API.
