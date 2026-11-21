"""Consume the real asset_catalog.json. Counts come from the file, not from constants."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


REQUIRED_KEYS = ("id", "kind", "library", "status")
VARIABLE_TYPES = {"string", "number", "enum", "image", "color", "boolean"}
# These statuses are in the index. They are not drop-in components for this master.
UNUSABLE_AS_US3DAY_COMPONENT = {
    "generic_example_not_us3day_source",
    "reference_card_not_drop_in_hf_component",
    "copied_source_not_extra_effect",
}
FORBIDDEN_ENGINES = {"385712", "echo", "echotribble", "echo-starter", "landscape"}


def load_catalog(path: str | Path) -> dict:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("entries"), list):
        raise ValueError("asset catalog must be an object with an entries array")
    errors = []
    for index, entry in enumerate(payload["entries"]):
        for key in REQUIRED_KEYS:
            if key not in entry:
                errors.append(f"entries[{index}] missing {key}")
                break
        else:
            if not isinstance(entry["id"], str) or ":" not in entry["id"]:
                errors.append(f"entries[{index}].id is not library:name")
            variables = entry.get("variables")
            if variables is not None:
                if not isinstance(variables, list):
                    errors.append(f"{entry.get('id')} variables is not a list")
                else:
                    for variable in variables:
                        if "id" not in variable or "type" not in variable or "default" not in variable:
                            errors.append(f"{entry.get('id')} variable missing id/type/default")
                            continue
                        if variable["type"] not in VARIABLE_TYPES:
                            errors.append(f"{entry.get('id')}.{variable['id']} type {variable['type']}")
                        if variable["type"] == "enum" and not variable.get("options"):
                            errors.append(f"{entry.get('id')}.{variable['id']} enum has no options")
    if errors:
        raise ValueError("catalog schema errors: " + "; ".join(errors[:8]))
    return payload


def counts(catalog: dict) -> dict:
    kind = Counter()
    library = Counter()
    status = Counter()
    for entry in catalog["entries"]:
        kind[entry["kind"]] += 1
        library[entry["library"]] += 1
        status[entry["status"]] += 1
    return {
        "entries": len(catalog["entries"]),
        "by_kind": dict(kind),
        "by_library": dict(library),
        "by_status": dict(status),
    }


def get_entry(catalog: dict, entry_id: str) -> dict | None:
    for entry in catalog["entries"]:
        if entry["id"] == entry_id:
            return entry
    return None


def lookup_name(catalog: dict, name: str) -> list[str]:
    needle = name.strip().lower()
    found = []
    for entry in catalog["entries"]:
        entry_name = entry["id"].split(":", 1)[1].lower()
        if entry_name == needle or entry.get("name", "").lower() == needle:
            found.append(entry["id"])
    return found


def _check_variable(spec: dict, value):
    kind = spec["type"]
    if kind == "string":
        if not isinstance(value, str):
            return "expected string"
        max_length = spec.get("maxLength")
        if max_length is not None and len(value) > max_length:
            return f"longer than {max_length}"
    elif kind == "number":
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return "expected number"
        if "min" in spec and value < spec["min"]:
            return f"below min {spec['min']}"
        if "max" in spec and value > spec["max"]:
            return f"above max {spec['max']}"
    elif kind == "boolean":
        if not isinstance(value, bool):
            return "expected boolean"
    elif kind == "enum":
        allowed = [option["value"] if isinstance(option, dict) else option for option in spec.get("options", [])]
        if value not in allowed:
            return f"{value!r} not in {allowed}"
    elif kind == "color":
        if not isinstance(value, str) or not value.startswith("#") or len(value) != 7:
            return "expected #RRGGBB"
    elif kind == "image":
        if not isinstance(value, str) or not value:
            return "expected image path"
    return None


def validate_binding(catalog: dict, binding: dict) -> dict:
    """Validate one component binding against the index. Does not render it."""
    entry_id = binding.get("id")
    entry = get_entry(catalog, entry_id) if entry_id else None
    if entry is None:
        return {"ok": False, "id": entry_id, "errors": [f"unknown catalog id {entry_id}"]}
    errors = []
    status = entry.get("status")
    if status in UNUSABLE_AS_US3DAY_COMPONENT:
        errors.append(f"status {status} is not a drop-in component for this master")
    if entry.get("kind") != "motion":
        errors.append(f"kind {entry.get('kind')} is not a motion component")
    provided = binding.get("variables") or {}
    if not isinstance(provided, dict):
        errors.append("variables must be an object")
        provided = {}
    known = {variable["id"]: variable for variable in entry.get("variables") or []}
    for key in provided:
        if key not in known:
            errors.append(f"unknown variable {key}")
            continue
        problem = _check_variable(known[key], provided[key])
        if problem:
            errors.append(f"{key}: {problem}")
    return {"ok": not errors, "id": entry_id, "status": status, "errors": errors}


def assert_engine_allowed(engine: str) -> None:
    token = engine.strip().lower()
    if token in FORBIDDEN_ENGINES or "385712" in token or token.startswith("echo"):
        raise ValueError(f"engine {engine} cannot stand in for the vertical us-3day master")
