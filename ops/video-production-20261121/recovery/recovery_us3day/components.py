"""Resolve a filled component id to catalog schema, source files, and sync times."""

from __future__ import annotations

from pathlib import Path

from .catalog import get_entry, validate_binding


def resolve_component(catalog: dict, shot: dict, library_roots: dict) -> dict:
    component = shot.get("component") or {}
    entry_id = component.get("id")
    if not entry_id:
        return {
            "ok": False,
            "id": None,
            "status": "unfilled",
            "missing": [f"{shot['id']}.component.id"],
            "sync": [],
        }
    binding = validate_binding(
        catalog,
        {"id": entry_id, "variables": component.get("variables") or {}},
    )
    if not binding["ok"]:
        return {
            "ok": False,
            "id": entry_id,
            "status": "schema_rejected",
            "missing": binding["errors"],
            "sync": [],
        }
    entry = get_entry(catalog, entry_id)
    library = entry["library"]
    root = library_roots.get(library)
    name = entry.get("name") or entry_id.split(":", 1)[1]
    if not root:
        return {
            "ok": False,
            "id": entry_id,
            "status": "library_root_unset",
            "missing": [f"library_roots.{library}"],
            "catalog_path": entry.get("path"),
            "sync": _sync(shot, entry),
        }
    folder = Path(root) / name
    wanted = [folder / "registry-item.json"]
    for item in entry.get("files") or []:
        rel = item.get("path")
        if rel:
            wanted.append(folder / rel)
    missing = [str(path) for path in wanted if not path.is_file()]
    return {
        "ok": not missing,
        "id": entry_id,
        "status": "resolved" if not missing else "source_missing",
        "missing": missing,
        "folder": str(folder),
        "catalog_path": entry.get("path"),
        "sync": _sync(shot, entry),
    }


def _sync(shot: dict, entry: dict) -> list[dict]:
    points = []
    t0 = float(shot["t0"])
    t1 = float(shot["t1"])
    for point in entry.get("syncPoints") or []:
        offset = float(point.get("offset") or 0)
        instant = t0 + offset
        points.append(
            {
                "id": point.get("id"),
                "phase": point.get("phase"),
                "offset_in_shot": offset,
                "t": instant,
                "inside_shot": t0 <= instant <= t1,
                "layer": "catalog_offset_plus_shot_t0",
            }
        )
    return points
