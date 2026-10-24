"""Read and write the knowledge base: one Google Sheet, "Test Case Knowledge Base".

Visible tabs: one per feature, "Test Cases – <feature> v<N> – <date>" (renamed on every run): the living,
editable copy of that feature's test cases.
Hidden tabs (bot bookkeeping, reachable from the "All sheets" menu): Features (one row per feature),
"<feature> – PRD" (requirements, acceptance criteria and business rules with their changes) and Change Log.

Feature tabs are found by their sheetId (stored in a hidden column), so renaming a tab doesn't break
anything. Rows are read by header name. Saves are serialised with a lock and only rewrite the features a run
touched (plus Features and Change Log). Features still stored in the earlier one-spreadsheet-per-feature
layout are moved into tabs on the next save, and that spreadsheet is then moved to the Drive trash.
"""

from __future__ import annotations

import json
import re
import threading
import urllib.parse

from .. import google_sheets as G
from .model import STATUSES, ChangeEntry, Feature, KBRequirement, KBTest, KnowledgeBase

KB_TITLE = "Test Case Knowledge Base"
FEATURES_TAB, CHANGELOG_TAB = "Features", "Change Log"
OLD_FEATURE_TABS = ["Test Cases", "Requirements", "Change Log"]  # layout of the per-feature spreadsheets
VALIDATION_ROWS = 5000
WRITE_LOCK = threading.Lock()  # load -> merge -> save must not interleave between two runs

_WIDTHS = {
    Feature: [80, 220, 110, 110, 100, 260, 260, 360, 300, 10, 10, 10],
    KBTest: [80, 160, 150, 240, 280, 110, 80, 240, 200, 320, 320, 130, 110, 100, 80, 110, 260, 320, 10],
    KBRequirement: [80, 160, 120, 150, 460, 220, 100, 100],
    ChangeEntry: [80, 160, 80, 100, 200, 300, 90, 80, 70, 80, 100, 360, 300],
}
_HIDDEN = {Feature: ["Source keys", "Tab IDs", "Sheet ID"], KBTest: ["Sync"]}


def _token() -> dict:
    return json.loads(G.TOKEN_FILE.read_text())


def _rgb(r, g, b) -> dict:
    return {"red": r, "green": g, "blue": b}


def _safe(name: str) -> str:
    return re.sub(r"[\[\]*?/\\:']", " ", name).strip()[:60] or "Feature"


def tab_title(name: str, kind: str, taken: set[str]) -> str:
    """'<name> – PRD' (hidden tab), made safe and unique."""
    base = _safe(name)
    title, n = f"{base} – {kind}", 2
    while title in taken:
        title, n = f"{base} ({n}) – {kind}", n + 1
    return title


def tests_tab_title(feature: Feature, taken: set[str]) -> str:
    """'Test Cases – <name> v<N> – <date>', the visible tab of a feature (same pattern as the run sheets)."""
    base = f"Test Cases – {_safe(feature.name)}" + (f" v{feature.version}" if feature.version else "")
    date = f" – {feature.updated}" if feature.updated else ""
    title, n = base + date, 2
    while title in taken:
        title, n = f"{base} ({n}){date}", n + 1
    return title


def format_requests(sid: int, cls) -> list[dict]:
    """Header, wrapping, filter, widths and hidden bot columns for one tab; dropdowns + colours on Tests tabs."""
    ncol = len(cls.COLUMNS)
    reqs = [
        {"repeatCell": {"range": {"sheetId": sid, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 0, "endColumnIndex": ncol},
                        "cell": {"userEnteredFormat": {"textFormat": {"bold": True, "foregroundColor": _rgb(1, 1, 1)},
                                                       "backgroundColor": _rgb(0.20, 0.27, 0.45), "wrapStrategy": "WRAP"}},
                        "fields": "userEnteredFormat(textFormat,backgroundColor,wrapStrategy)"}},
        {"repeatCell": {"range": {"sheetId": sid, "startRowIndex": 1, "startColumnIndex": 0, "endColumnIndex": ncol},
                        "cell": {"userEnteredFormat": {"verticalAlignment": "TOP", "wrapStrategy": "WRAP"}},
                        "fields": "userEnteredFormat(verticalAlignment,wrapStrategy)"}},
        {"setBasicFilter": {"filter": {"range": {"sheetId": sid, "startRowIndex": 0, "startColumnIndex": 0, "endColumnIndex": ncol}}}},
        # Unhide first: a column hidden under an older layout may now hold different data.
        {"updateDimensionProperties": {"range": {"sheetId": sid, "dimension": "COLUMNS", "startIndex": 0, "endIndex": ncol},
                                       "properties": {"hiddenByUser": False}, "fields": "hiddenByUser"}},
        {"updateSheetProperties": {"properties": {"sheetId": sid, "gridProperties": {
            "frozenRowCount": 1, "frozenColumnCount": 4 if cls is KBTest else 2}}, "fields": "gridProperties(frozenRowCount,frozenColumnCount)"}},
    ]
    for i, width in enumerate(_WIDTHS[cls]):
        reqs.append({"updateDimensionProperties": {"range": {"sheetId": sid, "dimension": "COLUMNS", "startIndex": i, "endIndex": i + 1},
                                                   "properties": {"pixelSize": width}, "fields": "pixelSize"}})
    for col in _HIDDEN.get(cls, []):
        i = cls.COLUMNS.index(col)
        reqs.append({"updateDimensionProperties": {"range": {"sheetId": sid, "dimension": "COLUMNS", "startIndex": i, "endIndex": i + 1},
                                                   "properties": {"hiddenByUser": True}, "fields": "hiddenByUser"}})
    if cls is not KBTest:
        return reqs

    def col_range(name):
        i = KBTest.COLUMNS.index(name)
        return {"sheetId": sid, "startRowIndex": 1, "endRowIndex": VALIDATION_ROWS, "startColumnIndex": i, "endColumnIndex": i + 1}

    for name, values in (("Test type", G.TYPE_OPTIONS), ("Priority", G.PRIORITY_OPTIONS), ("Status", STATUSES)):
        reqs.append({"setDataValidation": {"range": col_range(name), "rule": {
            "condition": {"type": "ONE_OF_LIST", "values": [{"userEnteredValue": v} for v in values]},
            "strict": True, "showCustomUi": True}}})
    colours = [("Priority", p, G.PRIORITY_COLORS[p]) for p in G.PRIORITY_OPTIONS]
    colours += [("Status", "Needs review", (1.0, 0.85, 0.60)), ("Status", "Obsolete", (0.85, 0.85, 0.85)),
                ("Origin", "Reviewed", (0.82, 0.93, 0.82))]
    for name, value, (r, g, b) in colours:
        reqs.append({"addConditionalFormatRule": {"index": 0, "rule": {"ranges": [col_range(name)], "booleanRule": {
            "condition": {"type": "TEXT_EQ", "values": [{"userEnteredValue": value}]},
            "format": {"backgroundColor": _rgb(r, g, b)}}}}})
    return reqs


# ---------------------------------------------------------------- spreadsheet + tabs

def _metadata(spreadsheet_id: str) -> dict:
    info = G._api("GET", f"{G.SHEETS_API}/{spreadsheet_id}?fields=spreadsheetId,spreadsheetUrl,sheets.properties(title,sheetId)")
    return {"id": info["spreadsheetId"], "url": info["spreadsheetUrl"],
            "tabs": {s["properties"]["title"]: s["properties"]["sheetId"] for s in info["sheets"]}}


def spreadsheet() -> dict:
    """{'id', 'url', 'tabs': {title: sheetId}} of the knowledge base, creating it on first use."""
    kb_id = _token().get("kb_spreadsheet_id")
    if kb_id:
        try:
            return _metadata(kb_id)
        except G.GoogleSheetsError:
            pass  # deleted or inaccessible: start a new one
    created = G._api("POST", G.SHEETS_API, {"properties": {"title": KB_TITLE},
                                             "sheets": [{"properties": {"title": FEATURES_TAB}}]})
    info = _metadata(created["spreadsheetId"])
    try:
        G._move_to_folder(info["id"], G.ensure_folder())
    except G.GoogleSheetsError:
        pass
    token = _token()
    token["kb_spreadsheet_id"] = info["id"]
    G._save_token(token)
    return info


index = spreadsheet


def tab_url(info: dict, tab: str | int = FEATURES_TAB) -> str:
    gid = tab if isinstance(tab, int) or str(tab).isdigit() else info["tabs"][tab]
    return f"https://docs.google.com/spreadsheets/d/{info['id']}/edit#gid={gid}"


def _add_tabs(info: dict, wanted: list[tuple[str, type]]) -> list[int]:
    """Create tabs (title, row class) with headers + formatting; returns their sheetIds in order."""
    if not wanted:
        return []
    reply = G._api("POST", f"{G.SHEETS_API}/{info['id']}:batchUpdate", {"requests": [
        {"addSheet": {"properties": {"title": title}}} for title, _ in wanted]})
    ids = [r["addSheet"]["properties"]["sheetId"] for r in reply["replies"]]
    for (title, _), sid in zip(wanted, ids):
        info["tabs"][title] = sid
    G._api("POST", f"{G.SHEETS_API}/{info['id']}/values:batchUpdate", {
        "valueInputOption": "RAW", "data": [{"range": f"'{t}'!A1", "values": [cls.COLUMNS]} for t, cls in wanted]})
    G._api("POST", f"{G.SHEETS_API}/{info['id']}:batchUpdate", {"requests": [
        r for (_, cls), sid in zip(wanted, ids) for r in format_requests(sid, cls)]})
    return ids


# ---------------------------------------------------------------- reading

def rows_to_dicts(values: list[list[str]]) -> list[dict]:
    if not values:
        return []
    header = [h.strip() for h in values[0]]
    out = []
    for row in values[1:]:
        if not any(str(c).strip() for c in row):
            continue
        out.append({h: (row[i] if i < len(row) else "") for i, h in enumerate(header) if h})
    return out


def _batch_get(spreadsheet_id: str, tabs: list[str]) -> list[dict]:
    if not tabs:
        return []
    query = urllib.parse.urlencode({"ranges": [f"'{t}'" for t in tabs]}, doseq=True)
    return G._api("GET", f"{G.SHEETS_API}/{spreadsheet_id}/values:batchGet?{query}").get("valueRanges", [])


def _own(items, feature: Feature):
    """Everything in a feature's tabs belongs to that feature."""
    for item in items:
        item.feature_id, item.feature = feature.feature_id, feature.name
    return items


def _fix_manual_rows(kb: KnowledgeBase) -> None:
    existing = {t.test_id for t in kb.tests}
    n = 0
    for t in kb.tests:
        if not t.test_id:
            n += 1
            while f"TC-MANUAL-{n:03d}" in existing:
                n += 1
            t.test_id = f"TC-MANUAL-{n:03d}"
            existing.add(t.test_id)
        if t.status not in STATUSES:
            t.status = "Active"


def load(info: dict | None = None) -> tuple[KnowledgeBase, dict, list[str]]:
    """The whole knowledge base. Returns (kb, spreadsheet info, ids of tests people edited)."""
    info = info or spreadsheet()
    title_by_id = {str(sid): title for title, sid in info["tabs"].items()}
    head = [t for t in (FEATURES_TAB, CHANGELOG_TAB) if t in info["tabs"]]
    head_ranges = dict(zip(head, _batch_get(info["id"], head)))
    kb = KnowledgeBase(features=[Feature.from_row(r) for r in rows_to_dicts(head_ranges.get(FEATURES_TAB, {}).get("values", []))
                                 if r.get("Feature ID") or r.get("Feature")])
    for f in kb.features:
        if not f.feature_id:
            f.feature_id = kb.next_feature_id()
    by_id = {f.feature_id: f for f in kb.features}
    kb.changelog = [c for c in (ChangeEntry.from_row(r) for r in rows_to_dicts(head_ranges.get(CHANGELOG_TAB, {}).get("values", [])))
                    if c.feature_id in by_id]

    in_tabs = [f for f in kb.features if f.tests_tab in title_by_id and f.prd_tab in title_by_id]
    ranges = _batch_get(info["id"], [title_by_id[t] for f in in_tabs for t in (f.tests_tab, f.prd_tab)])
    for i, f in enumerate(in_tabs):
        kb.tests += _own([KBTest.from_row(r) for r in rows_to_dicts(ranges[2 * i].get("values", []))], f)
        kb.requirements += _own([KBRequirement.from_row(r) for r in rows_to_dicts(ranges[2 * i + 1].get("values", []))], f)

    info["migrate"] = []
    for f in kb.features:
        if f in in_tabs or not f.sheet_id:
            continue
        try:  # earlier layout: the feature's own spreadsheet
            old = _batch_get(f.sheet_id, OLD_FEATURE_TABS)
        except G.GoogleSheetsError:
            continue
        kb.tests += _own([KBTest.from_row(r) for r in rows_to_dicts(old[0].get("values", []))], f)
        kb.requirements += _own([KBRequirement.from_row(r) for r in rows_to_dicts(old[1].get("values", []))], f)
        if not any(c.feature_id == f.feature_id for c in kb.changelog):
            kb.changelog += _own([ChangeEntry.from_row(r) for r in rows_to_dicts(old[2].get("values", []))], f)
        info["migrate"].append(f.feature_id)

    _fix_manual_rows(kb)
    edited = kb.mark_human_edits()
    return kb, info, edited


# ---------------------------------------------------------------- writing

def _id_sort_key(test_id: str):
    return [int(p) if p.isdigit() else p for p in re.split(r"(\d+)", test_id)]


def save(kb: KnowledgeBase, info: dict, feature_ids: list[str] | None = None) -> None:
    """Write the touched features' Tests/PRD tabs (creating them if needed), Features and Change Log."""
    kb.stamp()
    migrate = info.get("migrate", [])
    title_by_id = {str(sid): title for title, sid in info["tabs"].items()}
    targets = [f for f in kb.features if feature_ids is None or f.feature_id in feature_ids or f.feature_id in migrate]

    taken = set(info["tabs"])
    wanted, owners = [], []
    for f in targets:
        if f.tests_tab not in title_by_id:
            title = tests_tab_title(f, taken)
            taken.add(title)
            wanted.append((title, KBTest))
            owners.append((f, "tests_tab"))
        if f.prd_tab not in title_by_id:
            title = tab_title(f.name, "PRD", taken)
            taken.add(title)
            wanted.append((title, KBRequirement))
            owners.append((f, "prd_tab"))
    if CHANGELOG_TAB not in info["tabs"]:
        wanted.append((CHANGELOG_TAB, ChangeEntry))
        owners.append((None, ""))
    for (f, attr), sid in zip(owners, _add_tabs(info, wanted)):
        if f is not None:
            setattr(f, attr, str(sid))
    title_by_id = {str(sid): title for title, sid in info["tabs"].items()}
    renames = []
    for f in targets:
        current = title_by_id[f.tests_tab]
        wanted_title = tests_tab_title(f, set(info["tabs"]) - {current})
        if wanted_title != current:
            renames.append({"updateSheetProperties": {"properties": {"sheetId": int(f.tests_tab), "title": wanted_title}, "fields": "title"}})
            info["tabs"][wanted_title] = info["tabs"].pop(current)
    if renames:
        G._api("POST", f"{G.SHEETS_API}/{info['id']}:batchUpdate", {"requests": renames})
    title_by_id = {str(sid): title for title, sid in info["tabs"].items()}
    for f in kb.features:
        if f.tests_tab in title_by_id:
            f.tests_url, f.prd_url = tab_url(info, int(f.tests_tab)), tab_url(info, int(f.prd_tab))

    data = {FEATURES_TAB: (Feature, kb.features), CHANGELOG_TAB: (ChangeEntry, kb.changelog)}
    for f in targets:
        data[title_by_id[f.tests_tab]] = (KBTest, sorted(kb.tests_for(f.feature_id), key=lambda t: _id_sort_key(t.test_id)))
        data[title_by_id[f.prd_tab]] = (KBRequirement, kb.requirements_for(f.feature_id))
    G._api("POST", f"{G.SHEETS_API}/{info['id']}/values:batchClear", {"ranges": [f"'{t}'" for t in data]})
    G._api("POST", f"{G.SHEETS_API}/{info['id']}/values:batchUpdate", {
        "valueInputOption": "RAW",
        "data": [{"range": f"'{t}'!A1", "values": [cls.COLUMNS] + [o.to_row() for o in rows]} for t, (cls, rows) in data.items()]})

    # Only the test case tabs are visible (one per feature); bookkeeping tabs are hidden and kept at the end.
    visible = [title_by_id[f.tests_tab] for f in kb.features if f.tests_tab in title_by_id]
    hidden = [FEATURES_TAB] + [title_by_id[f.prd_tab] for f in kb.features if f.prd_tab in title_by_id] + [CHANGELOG_TAB]
    hidden += [t for t in info["tabs"] if t not in visible and t not in hidden]
    G._api("POST", f"{G.SHEETS_API}/{info['id']}:batchUpdate", {"requests":
           format_requests(info["tabs"][FEATURES_TAB], Feature)
           + [{"updateSheetProperties": {"properties": {"sheetId": info["tabs"][t], "index": i, "hidden": t in hidden},
                                         "fields": "index,hidden"}}
              for i, t in enumerate(visible + hidden)]})

    for f in kb.features:  # finish moving features out of their old separate spreadsheets
        if f.feature_id in migrate and f.sheet_id:
            try:
                G._api("PATCH", f"{G.DRIVE_FILES}/{f.sheet_id}", {"trashed": True})
            except G.GoogleSheetsError:
                pass
            f.sheet_id = ""
    if migrate:
        info["migrate"] = []
        _write_features_only(kb, info)


def _write_features_only(kb: KnowledgeBase, info: dict) -> None:
    G._api("POST", f"{G.SHEETS_API}/{info['id']}/values:batchClear", {"ranges": [f"'{FEATURES_TAB}'"]})
    G._api("POST", f"{G.SHEETS_API}/{info['id']}/values:batchUpdate", {
        "valueInputOption": "RAW", "data": [{"range": f"'{FEATURES_TAB}'!A1", "values": [Feature.COLUMNS] + [f.to_row() for f in kb.features]}]})
