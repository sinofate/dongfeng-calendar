"""Timeline clock. Shot placement uses t0/t1 seconds, never a running frame sum."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ShotSpan:
    id: str
    t0: float
    t1: float
    duration: float
    frames: int


@dataclass(frozen=True)
class Timeline:
    case: str
    fps: int
    total: float
    impact_at: str | None
    shots: tuple[ShotSpan, ...]


def load_timeline(path: str | Path) -> Timeline:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    shots = tuple(
        ShotSpan(
            id=item["id"],
            t0=float(item["t0"]),
            t1=float(item["t1"]),
            duration=float(item["duration"]),
            frames=int(item["frames"]),
        )
        for item in payload["shots"]
    )
    return Timeline(
        case=payload.get("case", ""),
        fps=int(payload["fps"]),
        total=float(payload["total"]),
        impact_at=payload.get("impact_at"),
        shots=shots,
    )


def frame_sum(timeline: Timeline) -> int:
    return sum(shot.frames for shot in timeline.shots)


def accumulated_frame_clock(timeline: Timeline) -> list[dict]:
    """Diagnostic only. Rendering must not place shots on this clock."""
    cursor = 0.0
    rows = []
    for shot in timeline.shots:
        rows.append(
            {
                "id": shot.id,
                "t0": shot.t0,
                "accumulated_seconds": cursor,
                "delta_seconds": cursor - shot.t0,
            }
        )
        cursor += shot.frames / timeline.fps
    return rows


def validate_timeline(timeline: Timeline) -> dict:
    errors = []
    if not timeline.shots:
        errors.append("timeline has no shots")
    ids = [shot.id for shot in timeline.shots]
    if ids != [f"s{index:02d}" for index in range(1, len(ids) + 1)]:
        errors.append(f"shot ids are not contiguous s01..sN: {ids}")
    if timeline.shots and abs(timeline.shots[0].t0) > 1e-9:
        errors.append("first shot t0 is not 0")
    for previous, shot in zip(timeline.shots, timeline.shots[1:]):
        if abs(previous.t1 - shot.t0) > 1e-6:
            errors.append(f"{previous.id}.t1 {previous.t1} != {shot.id}.t0 {shot.t0}")
        if abs((shot.t1 - shot.t0) - shot.duration) > 1e-6:
            errors.append(f"{shot.id} duration does not match t1-t0")
    if timeline.shots and abs(timeline.shots[-1].t1 - timeline.total) > 1e-6:
        errors.append("last t1 does not equal timeline total")
    summed = frame_sum(timeline)
    summed_seconds = summed / timeline.fps
    return {
        "ok": not errors,
        "errors": errors,
        "shot_count": len(timeline.shots),
        "frame_sum": summed,
        "frame_sum_seconds": summed_seconds,
        "timeline_total": timeline.total,
        "frame_quantization_gap_seconds": timeline.total - summed_seconds,
        "clock": "t0_t1_seconds",
        "frame_accumulation_used_for_placement": False,
    }
