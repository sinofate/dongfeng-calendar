"""Assemble and validate the slot config. Null means missing, not a coordinate."""

from __future__ import annotations

import json
from pathlib import Path

from .assparse import events_overlapping, parse_ass
from .catalog import assert_engine_allowed, validate_binding
from .layout import COLORS, RECONSTRUCTION, TITLE_DRAW
from .suggestions import E7Y_CALL, SUGGESTIONS
from .timeline import load_timeline, validate_timeline

ENGINE = "us3day-vertical-recovery"
CASE = "2026-11-07-us-3day-market-correct"

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TIMELINE = ROOT / "inputs" / "source-docs" / "timeline.json"
DEFAULT_ASS = ROOT / "inputs" / "source-docs" / "final_v1.ass"
DEFAULT_CATALOG = ROOT / "inputs" / "asset_catalog.json"
DEFAULT_COVER = ROOT / "inputs" / "reference" / "cover_1080x1920.jpg"
DEFAULT_REFERENCE = ROOT / "inputs" / "reference" / "master_full_lowbitrate_REFERENCE_NOT_RERENDER.mp4"
DEFAULT_PROJECT = ROOT / "config" / "project.us3day.json"


def build_project(timeline_path: Path = DEFAULT_TIMELINE, ass_path: Path = DEFAULT_ASS) -> dict:
    timeline = load_timeline(timeline_path)
    ass = parse_ass(ass_path)
    by_id = {item["id"]: item for item in SUGGESTIONS}
    if [shot.id for shot in timeline.shots] != [item["id"] for item in SUGGESTIONS]:
        raise ValueError("suggestion ids do not match timeline shot ids")
    shots = []
    for span in timeline.shots:
        suggestion = by_id[span.id]
        cues = events_overlapping(ass.events, span.t0, span.t1, kind="dialogue")
        shots.append(
            {
                "id": span.id,
                "t0": span.t0,
                "t1": span.t1,
                "frames_field": span.frames,
                "slot": suggestion["slot"],
                "content_from_suggestion": suggestion["content"],
                "method_from_suggestion": suggestion["method"],
                "fallback": suggestion["fallback"],
                "media": None,
                "component": {"id": None, "variables": None},
                "dialogue": [cue.text for cue in cues],
                "provenance": suggestion["provenance"],
                "comment_must_not_burn": suggestion.get("comment_must_not_burn"),
            }
        )
    return {
        "case": CASE,
        "engine": ENGINE,
        "e7y": E7Y_CALL,
        "timeline": {
            "path": str(timeline_path.relative_to(ROOT)),
            "fps": timeline.fps,
            "total": timeline.total,
            "impact_at": timeline.impact_at,
            "clock": "t0_t1_seconds",
        },
        "subtitles": {
            "path": str(ass_path.relative_to(ROOT)),
            "play_res": [ass.play_res_x, ass.play_res_y],
            "historical_style": ass.style.as_extracted(),
            "historical_lr": ass.style.margin_l,
            "historical_lr_layer": "extracted_us3day_final_v1_ass",
            "later_revision_lr": 90,
            "later_revision_layer": "evidenced_later_delivery",
            "later_revision_evidence": {
                "case": "2026-11-11-openai-anthropic-revenue-race",
                "ass": "inputs/local-validation/revenue_race_final_v4_ORIGINAL_COPY.ass",
                "line": 10,
                "md5": "4887b2bebd4e502ee44f53c0ae132316",
                "style": "Noto Sans CJK SC, 76, MarginL/R 90, MarginV 370",
                "warroom_ass_noted_hkt": "2026-11-11T15:06:00+08:00",
                "delivery_hkt": "2026-11-11T15:11:00+08:00",
                "film_md5": "bc2438d02897ef555f38a58c5a24ec1c",
                "not_the_us3day_historical_margin": True,
            },
            "revised_lr_range_documented": [80, 100],
            "layout_profile": "later_revision_lr90_on_reconstructed_bands",
            "dialogue_count": len(ass.dialogues),
            "comment_count": len(ass.comments),
            "comment_texts": [event.text for event in ass.comments],
        },
        "layout": {
            "title_band": RECONSTRUCTION["title_band"],
            "main_rect": RECONSTRUCTION["main_rect"],
            "subtitle_band": RECONSTRUCTION["subtitle_band"],
            "yellow_rule": None,
            "layer": "reconstructed",
            "title_draw": TITLE_DRAW,
            "colors": COLORS,
        },
        "fonts": {
            "family": "Noto Sans CJK SC",
            "regular": None,
            "bold": None,
            "known_regular": "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "known_bold": "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
            "face_index": 2,
            "substitute_forbidden": True,
        },
        "audio": {
            "vo": None,
            "bgm_plan": None,
            "sfx_events": None,
            "reference_mix": "forbidden_in_production",
            "loudness": {
                "target_i_lufs": -16.0,
                "true_peak_ceiling_dbtp": -1.5,
                "layer": "reconstructed_technical_target",
                "not_original_master_parameter": True,
            },
        },
        "library_roots": {},
        "opening": {
            "cover": str(DEFAULT_COVER.relative_to(ROOT)),
            "cover_until_seconds": 1.5,
            "push_percent": 3,
            "push_ease": "linear",
            "push_ease_layer": "reconstructed",
            "push_amount_layer": "documented",
            "hard_cut": True,
        },
        "shots": shots,
        "output": {
            "source_corner_labels": False,
            "yellow_outline": False,
            "width": 1080,
            "height": 1920,
            "fps": 30,
        },
        "media_duration_extracted": 150.566667,
    }


def validate_project(project: dict, catalog: dict | None = None) -> dict:
    errors = []
    warnings = []
    try:
        assert_engine_allowed(project.get("engine", ""))
    except ValueError as exc:
        errors.append(str(exc))
    if project.get("engine") != ENGINE:
        errors.append(f"engine must be {ENGINE}")
    shots = project.get("shots") or []
    ids = [shot.get("id") for shot in shots]
    if ids != [f"s{index:02d}" for index in range(1, 23)]:
        errors.append("project does not contain s01..s22 in order")
    if shots and shots[0]["t0"] != 0:
        errors.append("s01.t0 is not 0")
    for previous, shot in zip(shots, shots[1:]):
        if previous["t1"] != shot["t0"]:
            errors.append(f"boundary drift {previous['id']} -> {shot['id']}")
    if shots and shots[-1]["t1"] != project["timeline"]["total"]:
        errors.append("last shot does not end on the timeline total")
    for shot in shots:
        component = shot.get("component") or {}
        if component.get("id"):
            if catalog is None:
                errors.append(f"{shot['id']} binds {component['id']} but no catalog was loaded")
            else:
                result = validate_binding(
                    catalog,
                    {"id": component["id"], "variables": component.get("variables") or {}},
                )
                if not result["ok"]:
                    errors.append(f"{shot['id']} component: {result['errors']}")
        if shot.get("media") is not None and not isinstance(shot["media"], str):
            errors.append(f"{shot['id']} media must be a path or null")
        for line in shot.get("dialogue") or []:
            if line == "大约三成":
                errors.append(f"{shot['id']} dialogue list contains the ASS comment 大约三成")
            if "来源" in line:
                errors.append(f"{shot['id']} dialogue contains a source badge")
    style = project["subtitles"]["historical_style"]
    if style["margin_l"] != 30 or style["margin_r"] != 30:
        errors.append("historical MarginL/R was rewritten")
    if project["subtitles"].get("historical_lr") != 30:
        errors.append("historical MarginL/R must stay 30")
    if project["subtitles"].get("later_revision_lr") != 90:
        errors.append("later revision MarginL/R must stay 90")
    evidence = project["subtitles"].get("later_revision_evidence") or {}
    if evidence.get("md5") != "4887b2bebd4e502ee44f53c0ae132316":
        errors.append("later revision is missing the revenue-race ASS md5")
    if project["layout"]["yellow_rule"] is not None:
        errors.append("a yellow rule coordinate was invented")
    if project["output"].get("source_corner_labels"):
        errors.append("source corner labels are enabled")
    if project["output"].get("yellow_outline"):
        errors.append("yellow outline is enabled")
    if project["subtitles"]["historical_style"]["outline_color"].upper() != "#000000":
        errors.append("subtitle outline colour is not the extracted black")
    if project["subtitles"]["historical_style"]["primary"].upper() != "#FFD700":
        errors.append("subtitle fill is not the extracted #FFD700")
    impact = project["timeline"].get("impact_at")
    if impact != "s20.hero_land":
        errors.append(f"impact_at {impact} is not the extracted s20.hero_land")
    s20 = next((shot for shot in shots if shot["id"] == "s20"), None)
    if s20 is None or s20["slot"] != "hero_land":
        errors.append("s20 hero_land slot missing")
    return {"ok": not errors, "errors": errors, "warnings": warnings, "shot_count": len(shots)}


def write_project(path: Path = DEFAULT_PROJECT) -> dict:
    project = build_project()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(project, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return project


def load_project(path: str | Path = DEFAULT_PROJECT) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))
