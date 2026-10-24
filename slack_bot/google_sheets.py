"""Publish a test suite as a Google Sheet: one row per test case, Test type + Priority as dropdowns.

Layout (sheet "Test Cases"): Test ID | Test title | Test description | Test type | Priority | Preconditions |
Test data | Test steps | Expected result | Traces to | Feature. Header row frozen and filterable; Test type and
Priority use data-validation dropdowns; priorities are colour-coded. A second sheet "Summary" holds counts,
coverage and open questions. Values are written RAW, so text starting with "=" is never run as a formula.

Auth: OAuth for the user's own Google account with only the drive.file scope (the bot can see just the
files it creates). One-time setup:  .venv/bin/python -m slack_bot.google_sheets auth
Standard library only.
"""

from __future__ import annotations

import base64
import hashlib
import http.server
import json
import os
import re
import secrets
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from datetime import date
from pathlib import Path

from qa_tools.common import ROOT, test_data_text
from qa_tools.coverage import compute_coverage

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
CLIENT_SECRET_FILE = Path(os.environ.get("GOOGLE_CLIENT_SECRET_FILE", ROOT / "google_client_secret.json"))
TOKEN_FILE = Path(os.environ.get("GOOGLE_TOKEN_FILE", ROOT / ".google_token.json"))
FOLDER_NAME = "Test Case Generator"
TIMEOUT = 60

DRIVE_FILES = "https://www.googleapis.com/drive/v3/files"
SHEETS_API = "https://sheets.googleapis.com/v4/spreadsheets"

# ---------------------------------------------------------------- field mapping

TYPE_OPTIONS = ["Positive", "Negative", "Boundary", "Validation", "Edge Case", "UI", "UI/UX", "Security", "API", "Integration"]
PRIORITY_OPTIONS = ["P0", "P1", "P2", "P3"]
PRIORITY_MAP = {"Critical": "P0", "High": "P1", "Medium": "P2", "Low": "P3"}
PRIORITY_COLORS = {"P0": (0.96, 0.80, 0.80), "P1": (0.99, 0.88, 0.75), "P2": (1.0, 0.95, 0.75), "P3": (0.90, 0.90, 0.90)}
_TYPE_MAP = {
    "Positive": "Positive", "Negative": "Negative", "Error Handling": "Negative", "Boundary": "Boundary",
    "Validation": "Validation", "Business Rule": "Validation", "Edge Case": "Edge Case", "UI": "UI",
    "Compatibility": "UI/UX", "Security": "Security", "Authentication": "Security", "Authorization": "Security",
    "Session": "Security", "Integration": "Integration",
}
_HTTP_STEP = re.compile(r"\b(GET|POST|PUT|PATCH|DELETE)\s+/")

COLUMNS = ["Test ID", "Test title", "Test description", "Test type", "Priority", "Preconditions",
           "Test data", "Test steps", "Expected result", "Traces to", "Feature"]
COLUMN_WIDTHS = [130, 240, 280, 110, 80, 240, 200, 320, 320, 130, 140]
TYPE_COL, PRIORITY_COL = COLUMNS.index("Test type"), COLUMNS.index("Priority")
# Optional column for knowledge-base runs: what happened to each test in this version.
CHANGE_COLORS = {"New": (0.82, 0.93, 0.82), "Updated": (0.85, 0.91, 0.98), "Needs review": (1.0, 0.85, 0.60),
                 "Unchanged": (0.95, 0.95, 0.95)}
_WIDTH = {**dict(zip(COLUMNS, COLUMN_WIDTHS)), "Change": 110}


def sheet_columns(with_change: bool = False) -> list[str]:
    return [COLUMNS[0], "Change", *COLUMNS[1:]] if with_change else list(COLUMNS)


def doc_test_type(tc: dict) -> str:
    """Map the agent's 14 test types onto the sheet's dropdown list."""
    mapped = _TYPE_MAP.get(tc.get("test_type", ""), "Positive")
    if mapped in ("Positive", "Integration") and any(_HTTP_STEP.search(s) for s in tc.get("steps", [])):
        return "API"
    return mapped


def doc_priority(tc: dict) -> str:
    return PRIORITY_MAP.get(tc.get("priority", ""), "P2")


def test_description(tc: dict) -> str:
    if tc.get("description"):
        return tc["description"]
    return f"Verifies: {tc['scenario']}. Covers {', '.join(tc.get('source_refs', []))}."


# ---------------------------------------------------------------- sheet content

def test_case_rows(suite: dict, changes: dict[str, str] | None = None) -> list[list[str]]:
    """Header + one row per test. With `changes` (test ID -> New/Updated/...), a Change column follows Test ID."""
    rows = [sheet_columns(changes is not None)]
    for tc in suite["test_cases"]:
        row = [
            tc["id"],
            tc["scenario"],
            test_description(tc),
            doc_test_type(tc),
            doc_priority(tc),
            "\n".join(f"• {p}" for p in tc["preconditions"]) or "None",
            test_data_text(tc.get("test_data")) or "None",
            "\n".join(f"{n}. {s}" for n, s in enumerate(tc["steps"], 1)),
            tc["expected_result"],
            ", ".join(tc.get("source_refs", [])),
            tc.get("feature", ""),
        ]
        if changes is not None:
            row.insert(1, changes.get(tc["id"], "Unchanged"))
        rows.append(row)
    return rows


def summary_rows(suite: dict, analysis: dict | None, feature_name: str) -> list[list[str]]:
    cov = compute_coverage(suite, analysis)
    rows = [["Test cases", feature_name], ["Generated", date.today().isoformat()], ["Total test cases", str(cov["total_test_cases"])]]
    for key, label in (("positive", "Positive"), ("negative", "Negative"), ("boundary", "Boundary"),
                       ("validation", "Validation"), ("edge", "Edge cases")):
        rows.append([label, str(cov[key])])
    rows.append(["By priority", ", ".join(f"{PRIORITY_MAP[p]}: {n}" for p, n in cov["by_priority"].items())])
    if "requirements_identified" in cov:
        rows += [["Requirements covered", f"{cov['requirements_covered']}/{cov['requirements_identified']}"],
                 ["Acceptance criteria covered", f"{cov['acceptance_criteria_covered']}/{cov['acceptance_criteria_identified']}"],
                 ["Business rules covered", f"{cov['business_rules_covered']}/{cov['business_rules_identified']}"]]
    open_q = [q["question"] for q in (analysis or {}).get("clarifications", []) if q.get("status") != "answered"]
    gaps = [g["description"] for g in suite.get("coverage_summary", {}).get("gaps", [])]
    rows += [[], ["Open questions", ""]] + [["", q] for q in open_q] if open_q else []
    rows += [[], ["Coverage gaps", ""]] + [["", g] for g in gaps] if gaps else []
    return rows


def _rgb(r, g, b) -> dict:
    return {"red": r, "green": g, "blue": b}


def format_requests(sheet_id: int, summary_id: int, n_rows: int, columns: list[str] | None = None) -> list[dict]:
    """Header style, wrapping, column widths, filter, the two dropdown columns, colour-coded priority (and Change)."""
    columns = columns or COLUMNS
    type_col, priority_col = columns.index("Test type"), columns.index("Priority")
    def grid(r0, r1, c0, c1, sid=sheet_id):
        return {"sheetId": sid, "startRowIndex": r0, "endRowIndex": r1, "startColumnIndex": c0, "endColumnIndex": c1}

    def dropdown(col, values):
        return {"setDataValidation": {"range": grid(1, n_rows, col, col + 1), "rule": {
            "condition": {"type": "ONE_OF_LIST", "values": [{"userEnteredValue": v} for v in values]},
            "strict": True, "showCustomUi": True}}}

    requests = [
        {"repeatCell": {"range": grid(0, 1, 0, len(columns)), "cell": {"userEnteredFormat": {
            "textFormat": {"bold": True, "foregroundColor": _rgb(1, 1, 1)}, "backgroundColor": _rgb(0.20, 0.27, 0.45),
            "verticalAlignment": "MIDDLE", "wrapStrategy": "WRAP"}},
            "fields": "userEnteredFormat(textFormat,backgroundColor,verticalAlignment,wrapStrategy)"}},
        {"repeatCell": {"range": grid(1, n_rows, 0, len(columns)), "cell": {"userEnteredFormat": {
            "verticalAlignment": "TOP", "wrapStrategy": "WRAP"}}, "fields": "userEnteredFormat(verticalAlignment,wrapStrategy)"}},
        {"setBasicFilter": {"filter": {"range": grid(0, n_rows, 0, len(columns))}}},
        dropdown(type_col, TYPE_OPTIONS),
        dropdown(priority_col, PRIORITY_OPTIONS),
        {"repeatCell": {"range": grid(0, 30, 0, 1, summary_id), "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}},
                        "fields": "userEnteredFormat.textFormat"}},
        {"updateDimensionProperties": {"range": {"sheetId": summary_id, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 2},
                                       "properties": {"pixelSize": 260}, "fields": "pixelSize"}},
    ]
    for i, width in enumerate(_WIDTH[c] for c in columns):
        requests.append({"updateDimensionProperties": {"range": {"sheetId": sheet_id, "dimension": "COLUMNS",
                                                                 "startIndex": i, "endIndex": i + 1},
                                                       "properties": {"pixelSize": width}, "fields": "pixelSize"}})
    colour_rules = [(priority_col, p, rgb) for p, rgb in PRIORITY_COLORS.items()]
    if "Change" in columns:
        colour_rules += [(columns.index("Change"), c, rgb) for c, rgb in CHANGE_COLORS.items()]
    for col, value, (r, g, b) in colour_rules:
        requests.append({"addConditionalFormatRule": {"index": 0, "rule": {
            "ranges": [grid(1, n_rows, col, col + 1)],
            "booleanRule": {"condition": {"type": "TEXT_EQ", "values": [{"userEnteredValue": value}]},
                            "format": {"backgroundColor": _rgb(r, g, b), "textFormat": {"bold": True}}}}}})
    return requests


# ---------------------------------------------------------------- OAuth (installed app, loopback + PKCE)

class GoogleSheetsError(Exception):
    pass


def is_configured() -> bool:
    return TOKEN_FILE.exists()


def _client() -> dict:
    if not CLIENT_SECRET_FILE.exists():
        raise GoogleSheetsError(f"{CLIENT_SECRET_FILE.name} not found; download the OAuth client JSON (see slack_bot/README.md)")
    data = json.loads(CLIENT_SECRET_FILE.read_text())
    client = data.get("installed") or data.get("web")
    if not client:
        raise GoogleSheetsError(f"{CLIENT_SECRET_FILE.name} is not an OAuth client file (expected an 'installed' Desktop app client)")
    return client


def _save_token(token: dict) -> None:
    TOKEN_FILE.write_text(json.dumps(token, indent=2))
    TOKEN_FILE.chmod(0o600)


def _post_form(url: str, fields: dict) -> dict:
    req = urllib.request.Request(url, data=urllib.parse.urlencode(fields).encode(),
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as exc:
        try:
            body = json.load(exc)
        except ValueError:
            body = {}
        raise GoogleSheetsError(f"{body.get('error', exc.code)}: {body.get('error_description', exc.reason)}") from exc


def access_token() -> str:
    if not TOKEN_FILE.exists():
        raise GoogleSheetsError("Google Sheets isn't connected; run: .venv/bin/python -m slack_bot.google_sheets auth")
    token = json.loads(TOKEN_FILE.read_text())
    if token.get("access_token") and token.get("expires_at", 0) > time.time() + 60:
        return token["access_token"]
    client = _client()
    try:
        fresh = _post_form(client.get("token_uri", "https://oauth2.googleapis.com/token"), {
            "client_id": client["client_id"], "client_secret": client.get("client_secret", ""),
            "refresh_token": token["refresh_token"], "grant_type": "refresh_token"})
    except GoogleSheetsError as exc:
        if "invalid_grant" in str(exc):
            raise GoogleSheetsError("Google sign-in expired or was revoked; run: .venv/bin/python -m slack_bot.google_sheets auth") from exc
        raise
    token.update(access_token=fresh["access_token"], expires_at=time.time() + int(fresh.get("expires_in", 3600)))
    _save_token(token)
    return token["access_token"]


def authorize() -> None:
    """One-time browser consent; stores a refresh token in .google_token.json."""
    client = _client()
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    state = secrets.token_urlsafe(16)
    result: dict = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if "code" not in query and "error" not in query:
                self.send_response(404); self.end_headers(); return
            result.update({k: v[0] for k, v in query.items()})
            ok = "code" in query and query.get("state", [""])[0] == state
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(("<h2>Google Sheets connected. You can close this tab.</h2>" if ok
                              else "<h2>Sign-in failed. Check the terminal.</h2>").encode())

        def log_message(self, *args):
            pass

    server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    redirect = f"http://127.0.0.1:{server.server_port}"
    url = client.get("auth_uri", "https://accounts.google.com/o/oauth2/auth") + "?" + urllib.parse.urlencode({
        "client_id": client["client_id"], "redirect_uri": redirect, "response_type": "code", "scope": " ".join(SCOPES),
        "access_type": "offline", "prompt": "consent", "state": state,
        "code_challenge": challenge, "code_challenge_method": "S256"})
    print("Opening your browser to connect Google Sheets. If it doesn't open, visit:\n" + url)
    webbrowser.open(url)
    thread = threading.Thread(target=server.handle_request)
    thread.start()
    thread.join(timeout=300)
    server.server_close()
    if result.get("state") != state or "code" not in result:
        raise GoogleSheetsError(f"sign-in did not complete ({result.get('error', 'timed out or state mismatch')})")
    token = _post_form(client.get("token_uri", "https://oauth2.googleapis.com/token"), {
        "client_id": client["client_id"], "client_secret": client.get("client_secret", ""), "code": result["code"],
        "code_verifier": verifier, "grant_type": "authorization_code", "redirect_uri": redirect})
    if "refresh_token" not in token:
        raise GoogleSheetsError("Google returned no refresh token; remove the app at myaccount.google.com/permissions and retry")
    _save_token({"refresh_token": token["refresh_token"], "access_token": token["access_token"],
                 "expires_at": time.time() + int(token.get("expires_in", 3600)), "scope": token.get("scope", "")})


# ---------------------------------------------------------------- Drive / Docs calls

def _api(method: str, url: str, body: dict | None = None, raw: bytes | None = None, content_type: str = "application/json") -> dict:
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Authorization": f"Bearer {access_token()}", "Content-Type": content_type})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            payload = resp.read()
            return json.loads(payload) if payload else {}
    except urllib.error.HTTPError as exc:
        try:
            err = json.load(exc).get("error", {})
        except (ValueError, AttributeError):
            err = {}
        message = err.get("message", exc.reason) if isinstance(err, dict) else str(err)
        if exc.code == 403 and "has not been used" in str(message):
            message += " (enable the Google Sheets API and Google Drive API in your Cloud project)"
        raise GoogleSheetsError(f"Google API {exc.code}: {message}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise GoogleSheetsError(f"could not reach Google ({getattr(exc, 'reason', exc)})") from exc


def ensure_folder() -> str:
    token = json.loads(TOKEN_FILE.read_text())
    folder_id = token.get("folder_id")
    if folder_id:
        try:
            info = _api("GET", f"{DRIVE_FILES}/{folder_id}?fields=id,trashed")
            if not info.get("trashed"):
                return folder_id
        except GoogleSheetsError:
            pass
    created = _api("POST", f"{DRIVE_FILES}?fields=id", {"name": FOLDER_NAME, "mimeType": "application/vnd.google-apps.folder"})
    token = json.loads(TOKEN_FILE.read_text())
    token["folder_id"] = created["id"]
    _save_token(token)
    return created["id"]


def _move_to_folder(file_id: str, folder_id: str) -> None:
    info = _api("GET", f"{DRIVE_FILES}/{file_id}?fields=parents")
    remove = ",".join(info.get("parents", []))
    query = urllib.parse.urlencode({"addParents": folder_id, "removeParents": remove, "fields": "id"})
    _api("PATCH", f"{DRIVE_FILES}/{file_id}?{query}", {})


def create_test_case_sheet(suite: dict, analysis: dict | None, feature_name: str, run_dir: Path | None = None,
                           changes: dict[str, str] | None = None) -> str:
    """Create a fresh Google Sheet in the Test Case Generator folder and return its URL.

    `changes` (test ID -> New / Updated / Unchanged / Needs review) adds a colour-coded Change column.
    """
    title = f"Test Cases – {feature_name} – {date.today().isoformat()}"
    rows = test_case_rows(suite, changes)
    created = _api("POST", SHEETS_API, {
        "properties": {"title": title},
        "sheets": [{"properties": {"title": "Test Cases", "gridProperties": {
                       "frozenRowCount": 1, "frozenColumnCount": 3 if changes is not None else 2}}},
                   {"properties": {"title": "Summary"}}],
    })
    sheet_id = created["sheets"][0]["properties"]["sheetId"]
    summary_id = created["sheets"][1]["properties"]["sheetId"]
    spreadsheet_id, url = created["spreadsheetId"], created["spreadsheetUrl"]

    _api("POST", f"{SHEETS_API}/{spreadsheet_id}/values:batchUpdate", {
        "valueInputOption": "RAW",
        "data": [{"range": "'Test Cases'!A1", "values": rows},
                 {"range": "'Summary'!A1", "values": summary_rows(suite, analysis, feature_name)}],
    })
    _api("POST", f"{SHEETS_API}/{spreadsheet_id}:batchUpdate", {"requests": format_requests(sheet_id, summary_id, len(rows), rows[0])})
    try:
        _move_to_folder(spreadsheet_id, ensure_folder())
    except GoogleSheetsError:
        pass  # the sheet still exists in My Drive; the folder is only a convenience
    if run_dir is not None:
        (run_dir / "google-sheet.txt").write_text(url + "\n")
    return url


# ---------------------------------------------------------------- CLI

def main(argv: list[str]) -> int:
    from .net import prefer_ipv4

    prefer_ipv4()
    try:
        import certifi  # python.org builds on macOS ship without root certificates

        os.environ.setdefault("SSL_CERT_FILE", certifi.where())
    except ImportError:
        pass
    if argv[:1] == ["auth"]:
        try:
            authorize()
            folder = ensure_folder()
        except GoogleSheetsError as exc:
            print(f"error: {exc}")
            return 1
        print(f"Connected. Sheets will be created in your Drive folder '{FOLDER_NAME}' (id {folder}).")
        return 0
    if argv[:1] == ["test"] and len(argv) == 2:
        from qa_tools.common import load_json

        run = Path(argv[1])
        suite = load_json(run / "test-suite.json")
        analysis = load_json(run / "input-analysis.json") if (run / "input-analysis.json").exists() else None
        try:
            print(create_test_case_sheet(suite, analysis, suite["metadata"]["suite_name"], run))
        except GoogleSheetsError as exc:
            print(f"error: {exc}")
            return 1
        return 0
    print("usage: python -m slack_bot.google_sheets auth | test <run folder>")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
