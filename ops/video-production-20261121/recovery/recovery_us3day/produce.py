"""Production fill check. A burned master or a reference crop is not a shot asset."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from .components import resolve_component
from .compose import build_smoke_ass
from .fonts import resolve_noto
from .layout import RECONSTRUCTION
from .project import ROOT

BURNED_PLATE_NAMES = {
    "final_v1.mp4",
    "master_full_lowbitrate_REFERENCE_NOT_RERENDER.mp4",
}


def _rows(value, key: str) -> list[dict]:
    if value in (None, "", "none"):
        return []
    payload = json.loads(Path(value).read_text(encoding="utf-8"))
    return payload.get(key) or []


def _event_gaps(slot: str, value, key: str) -> list[dict]:
    if value in (None, ""):
        return [{"slot": slot, "missing": "unfilled"}]
    if value == "none":
        return []
    path = Path(value)
    if not path.is_file():
        return [{"slot": slot, "missing": str(path)}]
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get(key) or []
    if not rows:
        return [{"slot": slot, "missing": "no events in file"}]
    gaps = []
    for index, row in enumerate(rows):
        media = row.get("file")
        if not media or not Path(media).is_file():
            gaps.append({"slot": f"{slot}[{index}].file", "missing": str(media)})
    return gaps


def _file_gap(slot: str, value) -> dict | None:
    if value in (None, ""):
        return {"slot": slot, "missing": "unfilled"}
    if value == "none":
        return None
    path = Path(value)
    if path.name in BURNED_PLATE_NAMES or "REFERENCE_NOT_RERENDER" in path.name:
        return {"slot": slot, "missing": f"{path} is a burned plate, not a clean shot"}
    if not path.is_file():
        return {"slot": slot, "missing": str(path)}
    return None


def production_gaps(project: dict, catalog: dict | None = None) -> list[dict]:
    gaps = []
    fonts = project.get("fonts") or {}
    resolved = resolve_noto(fonts.get("regular"), fonts.get("bold"))
    if not resolved["ok"]:
        gaps.append({"slot": "fonts.noto", "missing": resolved["missing"], "family": resolved["family"]})
    audio = project.get("audio") or {}
    gap = _file_gap("audio.vo", audio.get("vo"))
    if gap:
        gaps.append(gap)
    gaps.extend(_event_gaps("audio.bgm_plan", audio.get("bgm_plan"), "segments"))
    gaps.extend(_event_gaps("audio.sfx_events", audio.get("sfx_events"), "events"))
    roots = project.get("library_roots") or {}
    for shot in project.get("shots") or []:
        gap = _file_gap(f"{shot['id']}.media", shot.get("media"))
        if gap:
            gaps.append(gap)
        if catalog is None:
            gaps.append({"slot": f"{shot['id']}.component", "missing": "catalog not loaded"})
            continue
        resolved_component = resolve_component(catalog, shot, roots)
        if not resolved_component["ok"]:
            gaps.append(
                {
                    "slot": f"{shot['id']}.component",
                    "id": resolved_component.get("id"),
                    "status": resolved_component["status"],
                    "missing": resolved_component["missing"],
                }
            )
    return gaps


def produce(project: dict, catalog: dict, out_dir: Path) -> dict:
    """Write a gap report and no picture when any production slot is empty.

    The render branch is only for real per-shot media, Noto, VO, a BGM plan,
    and SFX events. It does not crop the burned master and it does not invent
    a black frame.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    gaps = production_gaps(project, catalog)
    report = {
        "mode": "production",
        "qualified": False,
        "recovered_master": False,
        "reference_plate_used": False,
        "gaps": gaps,
    }
    if gaps:
        report["status"] = "production_inputs_missing"
        report["mp4_written"] = []
        (out_dir / "production_gaps.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return report
    return _render_filled(project, out_dir, report)


def _render_filled(project: dict, out_dir: Path, report: dict) -> dict:
    fonts = resolve_noto((project.get("fonts") or {}).get("regular"), (project.get("fonts") or {}).get("bold"))
    shots = project["shots"]
    stage = RECONSTRUCTION["main_rect"]
    ass_path = Path(project["subtitles"]["path"])
    if not ass_path.is_absolute():
        ass_path = ROOT / ass_path
    ass_file = out_dir / "production.ass"
    cover_until = float((project.get("opening") or {}).get("cover_until_seconds") or 0)
    ass_file.write_text(
        build_smoke_ass(ass_path, 0, float(project["timeline"]["total"]), 0, cover_until),
        encoding="utf-8",
    )
    filters = []
    cmd = ["ffmpeg", "-y", "-v", "error"]
    for index, shot in enumerate(shots):
        cmd.extend(["-i", shot["media"]])
        duration = float(shot["t1"]) - float(shot["t0"])
        filters.append(
            f"[{index}:v]trim=start=0:end={duration:.6f},setpts=PTS-STARTPTS,"
            f"scale={stage['w']}:{stage['h']}:force_original_aspect_ratio=increase,"
            f"crop={stage['w']}:{stage['h']},"
            f"pad=1080:1920:{stage['x']}:{stage['y']}:color=0x071829,fps=30,setsar=1[v{index}]"
        )
    filters.append("".join(f"[v{index}]" for index in range(len(shots))) + f"concat=n={len(shots)}:v=1:a=0[cat]")
    filters.append(f"[cat]subtitles=filename='{ass_file}':fontsdir='{fonts['fontsdir']}'[vout]")
    vo = project["audio"]["vo"]
    cmd.extend(["-i", vo])
    vo_index = len(shots)
    duration = float(project["timeline"]["total"])
    filters.append(f"[{vo_index}:a]atrim=0:{duration:.6f},asetpts=PTS-STARTPTS[vo]")
    labels = ["[vo]"]
    next_input = vo_index + 1
    for row in _rows(project["audio"].get("bgm_plan"), "segments"):
        cmd.extend(["-i", row["file"]])
        length = float(row["end"]) - float(row["start"])
        offset = float(row.get("offset") or 0)
        delay = int(round(float(row["start"]) * 1000))
        gain = float(row.get("gain_db") or 0)
        filters.append(
            f"[{next_input}:a]atrim=start={offset}:end={offset + length},asetpts=PTS-STARTPTS,"
            f"volume={gain}dB,adelay={delay}|{delay}[m{next_input}]"
        )
        labels.append(f"[m{next_input}]")
        next_input += 1
    for row in _rows(project["audio"].get("sfx_events"), "events"):
        cmd.extend(["-i", row["file"]])
        delay = int(round(float(row["t_peak"]) * 1000))
        if row.get("peak_ms") is not None:
            delay = max(0, delay - int(row["peak_ms"]))
        gain = float(row.get("gain_db") or 0)
        filters.append(f"[{next_input}:a]volume={gain}dB,adelay={delay}|{delay}[s{next_input}]")
        labels.append(f"[s{next_input}]")
        next_input += 1
    if len(labels) == 1:
        filters.append("[vo]aresample=48000[aout]")
    else:
        filters.append("".join(labels) + f"amix=inputs={len(labels)}:duration=first:dropout_transition=0:normalize=0[aout]")
    output = out_dir / "production_not_reference.mp4"
    cmd.extend(
        [
            "-filter_complex",
            ";".join(filters),
            "-map",
            "[vout]",
            "-map",
            "[aout]",
            "-r",
            "30",
            "-c:v",
            "libx264",
            "-preset",
            "ultrafast",
            "-crf",
            "18",
            "-c:a",
            "aac",
            "-pix_fmt",
            "yuv420p",
            str(output),
        ]
    )
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    (out_dir / "production.ffmpeg.log").write_bytes(proc.stderr)
    if proc.returncode != 0:
        report["status"] = "production_encode_failed"
        report["qualified"] = False
        return report
    report["status"] = "production_composite"
    report["output"] = str(output)
    report["qualified"] = False
    report["note"] = "Picture uses the supplied shot media and Noto. Component snippets are checked on disk but are not executed as HyperFrames."
    return report
