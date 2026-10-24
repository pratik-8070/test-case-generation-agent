"""Minimal JSON Schema validator covering the subset used in schemas/.

Supported keywords: type (string or list), required, properties, items,
enum, pattern, minLength, minItems, $ref (local "#/$defs/..." only).
Unknown keywords are ignored. Kept in-house so the project needs no pip
install; swap for the `jsonschema` package if dependencies become acceptable.
"""

from __future__ import annotations

import re
from pathlib import Path

from .common import Report, SCHEMAS_DIR, load_json

_TYPES = {
    "object": dict,
    "array": list,
    "string": str,
    "boolean": bool,
    "integer": int,
    "number": (int, float),
    "null": type(None),
}


def _type_ok(value, expected) -> bool:
    names = expected if isinstance(expected, list) else [expected]
    for name in names:
        py = _TYPES[name]
        # bool is a subclass of int in Python; don't let True pass as a number.
        if name in ("integer", "number") and isinstance(value, bool):
            continue
        if isinstance(value, py):
            return True
    return False


def _resolve(ref: str, root: dict) -> dict:
    if not ref.startswith("#/"):
        raise ValueError(f"Only local $ref supported, got {ref}")
    node = root
    for part in ref[2:].split("/"):
        node = node[part]
    return node


def _validate(value, schema: dict, root: dict, path: str, report: Report) -> None:
    if "$ref" in schema:
        schema = _resolve(schema["$ref"], root)

    if "type" in schema and not _type_ok(value, schema["type"]):
        report.error("schema-type", f"{path}: expected {schema['type']}, got {type(value).__name__}")
        return

    if "enum" in schema and value not in schema["enum"]:
        report.error("schema-enum", f"{path}: {value!r} is not one of {schema['enum']}")

    if isinstance(value, str):
        if len(value.strip()) < schema.get("minLength", 0):
            report.error("schema-min-length", f"{path}: must be at least {schema['minLength']} character(s)")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            report.error("schema-pattern", f"{path}: {value!r} does not match {schema['pattern']}")

    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            report.error("schema-min-items", f"{path}: needs at least {schema['minItems']} item(s)")
        if "items" in schema:
            for i, item in enumerate(value):
                _validate(item, schema["items"], root, f"{path}[{i}]", report)

    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                report.error("schema-required", f"{path}: missing required field '{key}'")
        for key, sub in schema.get("properties", {}).items():
            if key in value:
                _validate(value[key], sub, root, f"{path}.{key}", report)


def validate_against(data: dict, schema_name: str, schemas_dir: Path = SCHEMAS_DIR) -> Report:
    schema = load_json(schemas_dir / schema_name)
    report = Report(f"schema: {schema_name}")
    _validate(data, schema, schema, "$", report)
    return report
