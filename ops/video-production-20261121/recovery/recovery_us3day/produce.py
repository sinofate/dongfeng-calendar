"""Production fill check. A burned master or a reference crop is not a shot asset."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from .assparse import format_ass_time
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
    path = _locate(value)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if key == "events" and not payload.get(key) and str(payload.get("reason") or "").startswith("none"):
        return []
    rows = []
    for row in payload.get(key) or []:
        item = dict(row)
        if item.get("file"):
            item["file"] = str(_locate(item["file"]))
        rows.append(item)
    return rows


def _locate(value: str) -> Path:
    path = Path(value)
    if path.is_file():
        return path
    rooted = ROOT / value
    if rooted.is_file():
        return rooted
    return path


def _event_gaps(slot: str, value, key: str) -> list[dict]:
    if value in (None, ""):
        return [{"slot": slot, "missing": "unfilled"}]
    if value == "none":
        return []
    path = _locate(value)
    if not path.is_file():
        return [{"slot": slot, "missing": str(path)}]
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get(key) or []
    reason = str(payload.get("reason") or "")
    if not rows and reason.startswith("none"):
        return []
    if not rows:
        return [{"slot": slot, "missing": "no events in file"}]
    gaps = []
    for index, row in enumerate(rows):
        media = row.get("file")
        if not media or not _locate(str(media)).is_file():
            gaps.append({"slot": f"{slot}[{index}].file", "missing": str(media)})
    return gaps


def _file_gap(slot: str, value) -> dict | None:
    if value in (None, ""):
        return {"slot": slot, "missing": "unfilled"}
    if value == "none":
        return None
    path = _locate(value)
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


def _normalize_variables(entry: dict) -> dict:
    variables = entry.get("variables")
    if isinstance(variables, dict):
        entry = dict(entry)
        normalized = []
        for key, spec in variables.items():
            if isinstance(spec, dict):
                item = {"id": key, "type": spec.get("type", "string"), "default": spec.get("default", "")}
                item.update({k: v for k, v in spec.items() if k not in item})
                normalized.append(item)
            else:
                normalized.append({"id": key, "type": "string", "default": spec})
        entry["variables"] = normalized
    return entry


def catalog_for_project(catalog: dict, project: dict) -> dict:
    merged = {"version": catalog.get("version"), "entries": [_normalize_variables(dict(entry)) for entry in catalog["entries"]]}
    known = {entry["id"] for entry in merged["entries"]}
    root_value = (project.get("library_roots") or {}).get("hf_components")
    if not root_value:
        return merged
    root = _locate(str(root_value))
    if not root.is_dir():
        return merged
    for registry in root.glob("*/registry-item.json"):
        item = _normalize_variables(json.loads(registry.read_text(encoding="utf-8")))
        item.setdefault("kind", "motion")
        item.setdefault("library", "hf_components")
        item.setdefault("name", registry.parent.name)
        item.setdefault("id", f"hf_components:{item['name']}")
        item.setdefault("status", "local_registry")
        if item["id"] not in known:
            merged["entries"].append(item)
            known.add(item["id"])
    return merged


def produce(project: dict, catalog: dict, out_dir: Path) -> dict:
    """Write a gap report and no picture when any production slot is empty.

    The render branch is only for real per-shot media, Noto, VO, a BGM plan,
    and SFX events. It does not crop the burned master and it does not invent
    a black frame.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    timeline = project.setdefault("timeline", {})
    if "total" not in timeline and timeline.get("duration_seconds") is not None:
        timeline["total"] = timeline["duration_seconds"]
    subtitles = project.setdefault("subtitles", {})
    if not subtitles.get("path") and subtitles.get("file"):
        subtitles["path"] = subtitles["file"]
    catalog = catalog_for_project(catalog, project)
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
    return _render_filled(project, catalog, out_dir, report)


def _accent_map(html: str) -> dict[str, str]:
    return {
        name: color
        for name, color in re.findall(
            r"(\w+):\s*\"var\([^,]+,\s*(#[0-9A-Fa-f]{6})\)\"",
            html,
        )
    }


def _hex_to_ass(color: str) -> str:
    red, green, blue = color[1:3], color[3:5], color[5:7]
    return f"00{blue}{green}{red}".upper()


def _component_call(project: dict, catalog: dict, shot: dict, total: float) -> dict | None:
    resolved = resolve_component(catalog, shot, project.get("library_roots") or {})
    if not resolved["ok"]:
        return None
    variables = shot["component"].get("variables") or {}
    folder = Path(resolved["folder"])
    registry = json.loads((folder / "registry-item.json").read_text(encoding="utf-8"))
    snippet_name = ((registry.get("files") or [{}])[0]).get("path")
    html_path = folder / snippet_name if snippet_name else None
    html = html_path.read_text(encoding="utf-8") if html_path and html_path.is_file() else ""
    accent = str(variables.get("accent") or "green")
    hex_color = _accent_map(html).get(accent)
    if not hex_color:
        return None
    sync = resolved["sync"][:1]
    start = float(sync[0]["offset_in_shot"]) if sync else float(variables.get("draw_at") or 0)
    stage = RECONSTRUCTION["main_rect"]
    size = int(round(min(0.08 * stage["w"], 0.15 * stage["h"])))
    text = str(variables.get("emphasis_word") or variables.get("text") or "")
    margin_v = 1920 - (stage["y"] + stage["h"] - 16)
    override = "{\\u1\\c&H" + _hex_to_ass(hex_color) + "&\\fs" + str(size) + "\\bord0\\shad0}"
    return {
        "id": shot["component"]["id"],
        "binding_layer": shot["component"].get("binding_layer"),
        "not_original_shot_source": bool(shot["component"].get("not_original_shot_source")),
        "why": shot["component"].get("why"),
        "variables": variables,
        "sync": resolved["sync"],
        "drawn_text": text,
        "drawn_text_is": "registry emphasis_word; the full registry text stays in the subtitle line",
        "accent_hex": hex_color,
        "accent_source": str(html_path) if html_path else "",
        "font_size_px": size,
        "font_size_rule": "min(8cqw, 15cqh) of the 1080×1128 stage, from the component stylesheet",
        "registry": str(folder / "registry-item.json"),
        "snippet": str(html_path) if html_path else "",
        "ass_line": (
            f"Dialogue: 1,{format_ass_time(start)},{format_ass_time(total)},D,,0,0,{margin_v},,{override}{text}"
        ),
    }


def _shot_video_filter(index: int, shot: dict, duration: float, stage: dict, still_motion: str | None = None) -> str:
    component_id = str((shot.get("component") or {}).get("id") or "")
    frames = max(2, int(round(duration * 30)))
    if component_id.endswith("cover-push-3"):
        # One input frame. zoompan d= is frames-per-input-frame, so a looped still would multiply the shot.
        return (
            f"[{index}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            f"zoompan=z='1+0.03*on/{frames - 1}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d={frames}:s=1080x1920:fps=30,format=yuv420p,setsar=1[v{index}]"
        )
    if still_motion == "contain_push":
        # Fit the whole plate inside the stage, then push 3.5% through the matte margin so tables are not cropped.
        inner_w = int(stage["w"] * 0.965)
        inner_h = int(stage["h"] * 0.965)
        return (
            f"[{index}:v]scale={inner_w}:{inner_h}:force_original_aspect_ratio=decrease,"
            f"pad={stage['w']}:{stage['h']}:(ow-iw)/2:(oh-ih)/2:color=0x071829,"
            f"zoompan=z='1+0.035*on/{frames - 1}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d={frames}:s={stage['w']}x{stage['h']}:fps=30,"
            f"pad=1080:1920:{stage['x']}:{stage['y']}:color=0x071829,setsar=1[v{index}]"
        )
    return (
        f"[{index}:v]trim=start=0:end={duration:.6f},setpts=PTS-STARTPTS,"
        f"scale={stage['w']}:{stage['h']}:force_original_aspect_ratio=increase,"
        f"crop={stage['w']}:{stage['h']},"
        f"pad=1080:1920:{stage['x']}:{stage['y']}:color=0x071829,fps=30,setsar=1[v{index}]"
    )


def _bezier(p0, p1, p2, p3, count: int) -> list[tuple[float, float]]:
    points = []
    for index in range(count + 1):
        t = index / count
        u = 1 - t
        x = u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0]
        y = u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1]
        points.append((x, y))
    return points


def _render_price_decline(output: Path, duration: float, variables: dict) -> None:
    """Draw the attached component's own cubic, not a new market curve.

    Path, guides, and stroke width come from price-decline-56000-44800.html:
    M165 280 C320 315 375 385 505 435 S685 625 875 780, stroke 11, gold.
    The draw runs from 10% to 75% of the shot, matching the component keyframes.
    """
    first = _bezier((165, 280), (320, 315), (375, 385), (505, 435), 90)
    second = _bezier((505, 435), (635, 485), (685, 625), (875, 780), 90)
    points = first[:-1] + second
    boxes = []
    for y in (260, 790):
        x = 110
        while x < 970:
            boxes.append(f"drawbox=x={x}:y={y}:w=10:h=2:color=0x43536b@1:t=fill")
            x += 22
    for index, (x, y) in enumerate(points):
        appear = duration * (0.10 + 0.65 * index / max(1, len(points) - 1))
        left = int(round(x - 5))
        top = int(round(y - 5))
        boxes.append(
            f"drawbox=x={left}:y={top}:w=11:h=11:color=0xFFD700@1:t=fill:enable='gte(t,{appear:.3f})'"
        )
    boxes.append("drawbox=x=152:y=267:w=26:h=26:color=0xFFD700@1:t=fill")
    land = duration * 0.72
    boxes.append(f"drawbox=x=859:y=764:w=32:h=32:color=0xFFD700@1:t=fill:enable='gte(t,{land:.3f})'")
    filt = "scale=1080:1128,setsar=1," + ",".join(boxes)
    proc = subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-f", "lavfi", "-i", f"color=c=0x080d17:s=1080x1128:r=30:d={duration:.3f}",
            "-vf", filt,
            "-frames:v", str(max(2, int(round(duration * 30)))),
            "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
            str(output),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode("utf-8", "replace")[-500:])


def _ass_time_pair(start: float, end: float) -> tuple[str, str]:
    return format_ass_time(start), format_ass_time(end)


def _motion_overlay(project: dict, catalog: dict, shot: dict, total: float) -> dict | None:
    component = shot.get("component") or {}
    component_id = str(component.get("id") or "")
    name = component_id.split(":")[-1]
    variables = component.get("variables") or {}
    t0 = float(shot["t0"])
    t1 = float(shot["t1"])
    resolved = resolve_component(catalog, shot, project.get("library_roots") or {})
    base = {
        "id": component_id,
        "status": resolved.get("status"),
        "variables": variables,
        "sync": resolved.get("sync") or [],
        "binding_layer": component.get("binding_layer") or "project_component",
        "not_original_shot_source": bool(component.get("not_original_shot_source")),
    }
    if name == "cover-push-3":
        base["rendered_as"] = "zoompan 1.00 to 1.03 over the cover, full frame, then hard cut"
        base["ass_lines"] = []
        return base
    if name == "number-pop-in":
        start, end = _ass_time_pair(min(t1, t0 + 0.45), t1)
        text = str(variables.get("value", ""))
        line = "Dialogue: 1,%s,%s,D,,0,0,560,,{\\fad(180,0)\\bord8\\3c&H00201807&\\c&H00FFFFFF&\\fs96}%s" % (start, end, text)
        base["rendered_as"] = "catalog number-pop-in value, tone paper, pop fade"
        base["ass_lines"] = [line]
        return base
    if name == "kinetic-center-build":
        text = str(variables.get("text") or "")
        words = text.split()
        lines = []
        lock = 1.2
        if len(words) <= 1:
            shown = text
            slash = text.find("／")
            if slash > 0 and len(text) > 16:
                shown = text[: slash + 1] + r"\N" + text[slash + 1 :]
            start, end = _ass_time_pair(t0, t1)
            lines.append(
                "Dialogue: 1,%s,%s,D,,0,0,640,,{\\fs64\\c&H00FFFFFF&\\bord6\\3c&H00201807&}%s" % (start, end, shown)
            )
        else:
            # Each build step replaces the previous line. Overlapping copies stacked into three phrases.
            for index in range(len(words)):
                start_s = min(t1, t0 + lock * index / max(1, len(words)))
                end_s = t1 if index == len(words) - 1 else min(t1, t0 + lock * (index + 1) / max(1, len(words)))
                start, end = _ass_time_pair(start_s, end_s)
                chunk = " ".join(words[: index + 1])
                lines.append(
                    "Dialogue: 1,%s,%s,D,,0,0,640,,{\\fs72\\c&H00FFFFFF&\\bord6\\3c&H00201807&}%s" % (start, end, chunk)
                )
        base["rendered_as"] = "catalog kinetic-center-build, phrase builds to phrase-locked"
        base["ass_lines"] = lines
        return base
    if name == "panel-reveal":
        start, end = _ass_time_pair(min(t1, t0 + 0.35), t1)
        title = str(variables.get("title") or "")
        line = "Dialogue: 1,%s,%s,D,,0,0,620,,{\\fad(400,0)\\fs48\\c&H00171717&\\bord12\\3c&H00FFFFFF&}%s" % (start, end, title)
        base["rendered_as"] = "catalog panel-reveal title, tone ink, reveal fade"
        base["ass_lines"] = [line]
        return base
    if name == "price-decline-56000-44800":
        start, end = _ass_time_pair(t0, t1)
        land, end_at = _ass_time_pair(t0 + (t1 - t0) * 0.72, t1)
        label = str(variables.get("scenario_label") or "")
        start_price = variables.get("start_price")
        end_price = variables.get("end_price")
        base["rendered_as"] = "attached component cubic from (165,280) through the written S control to (875,780); not a new market series"
        # Positions are the component SVG text anchors, plus the stage top at y312.
        base["ass_lines"] = [
            "Dialogue: 1,%s,%s,D,,0,0,0,,{\\an8\\pos(540,348)\\fs42\\c&H00FFFFFF&\\bord0\\3c&H004A3527&\\shad0}%s" % (start, end, label),
            "Dialogue: 1,%s,%s,D,,0,0,0,,{\\an7\\pos(165,537)\\fs60\\b1\\c&H00FFFFFF&\\bord0}约 %s" % (start, end, start_price),
            "Dialogue: 1,%s,%s,D,,0,0,0,,{\\an7\\pos(610,1207)\\fs68\\b1\\c&H0000D7FF&\\bord0}约 %s" % (land, end_at, end_price),
            "Dialogue: 1,%s,%s,D,,0,0,0,,{\\an7\\pos(165,1307)\\fs36\\c&H00E1D5CB&\\bord0}参考条件不变 · 压力测试" % (start, end),
        ]
        return base
    call = _component_call(project, catalog, shot, total)
    if not call:
        return None
    call["ass_lines"] = [call["ass_line"]]
    return call


def _render_filled(project: dict, catalog: dict, out_dir: Path, report: dict) -> dict:
    fonts = resolve_noto((project.get("fonts") or {}).get("regular"), (project.get("fonts") or {}).get("bold"))
    shots = project["shots"]
    stage = RECONSTRUCTION["main_rect"]
    ass_path = _locate(project["subtitles"]["path"])
    ass_file = out_dir / "production.ass"
    cover_until = float((project.get("opening") or {}).get("cover_until_seconds") or 0)
    ass_file.write_text(
        build_smoke_ass(
            ass_path,
            0,
            float(project["timeline"]["total"]),
            0,
            cover_until,
            project.get("titles"),
        ),
        encoding="utf-8",
    )
    component_calls = []
    prepared = []
    for shot in shots:
        shot = dict(shot)
        component = shot.get("component") or {}
        if str(component.get("id") or "").endswith("price-decline-56000-44800"):
            plate = out_dir / f"{shot['id']}_price_decline.mp4"
            _render_price_decline(plate, float(shot["t1"]) - float(shot["t0"]), component.get("variables") or {})
            shot["media"] = str(plate)
        prepared.append(shot)
        if component.get("id"):
            call = _motion_overlay(project, catalog, shot, float(project["timeline"]["total"]))
            if call:
                component_calls.append(call)
    if component_calls:
        extra = "\n".join(line for call in component_calls for line in call.get("ass_lines") or ([call["ass_line"]] if call.get("ass_line") else []))
        if extra:
            ass_file.write_text(ass_file.read_text(encoding="utf-8") + extra + "\n", encoding="utf-8")
    filters = []
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "verbose"]
    still_motion = (project.get("picture") or {}).get("still_motion")
    for index, shot in enumerate(prepared):
        media = _locate(shot["media"])
        duration = float(shot["t1"]) - float(shot["t0"])
        component_id = str((shot.get("component") or {}).get("id") or "")
        one_frame = media.suffix.lower() in {".jpg", ".jpeg", ".png"} and (
            component_id.endswith("cover-push-3") or still_motion == "contain_push"
        )
        if one_frame:
            cmd.extend(["-i", str(media)])
        elif media.suffix.lower() in {".jpg", ".jpeg", ".png"}:
            cmd.extend(["-loop", "1", "-framerate", "30", "-t", f"{duration:.6f}", "-i", str(media)])
        else:
            cmd.extend(["-i", str(media)])
        filters.append(_shot_video_filter(index, shot, duration, stage, still_motion if one_frame else None))
    filters.append("".join(f"[v{index}]" for index in range(len(shots))) + f"concat=n={len(shots)}:v=1:a=0[cat]")
    filters.append(f"[cat]subtitles=filename='{ass_file}':fontsdir='{fonts['fontsdir']}'[vout]")
    vo = str(_locate(project["audio"]["vo"]))
    cmd.extend(["-i", vo])
    vo_index = len(shots)
    duration = float(project["timeline"]["total"])
    filters.append(
        f"[{vo_index}:a]aresample=48000,apad=whole_dur={duration:.6f},atrim=0:{duration:.6f},asetpts=PTS-STARTPTS[vo]"
    )
    labels = ["[vo]"]
    next_input = vo_index + 1
    for row in _rows(project["audio"].get("bgm_plan"), "segments"):
        cmd.extend(["-i", row["file"]])
        length = float(row["end"]) - float(row["start"])
        offset = float(row.get("offset") or 0)
        delay = int(round(float(row["start"]) * 1000))
        gain = float(row.get("gain_db") or 0)
        fades = ""
        if row.get("fade_in"):
            fades += f",afade=t=in:st=0:d={float(row['fade_in'])}"
        if row.get("fade_out"):
            # fade_out_start in this case is a timeline second. afade runs on the trimmed clip, whose PTS starts at 0.
            fade_at = float(row.get("fade_out_start", float(row["end"]) - float(row["fade_out"])))
            if fade_at >= float(row["start"]):
                fade_at -= float(row["start"])
            fade_at = max(0.0, min(fade_at, max(0.0, length - 0.05)))
            fades += f",afade=t=out:st={fade_at:.3f}:d={float(row['fade_out'])}"
        filters.append(
            f"[{next_input}:a]atrim=start={offset}:end={offset + length},asetpts=PTS-STARTPTS,"
            f"volume={gain}dB{fades},adelay={delay}|{delay}[m{next_input}]"
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
    video_only = out_dir / "video_only.mp4"
    premaster = out_dir / "premaster.wav"
    split_cmd = cmd + [
        "-filter_complex",
        ";".join(filters),
        "-map",
        "[vout]",
        "-an",
        "-r",
        "30",
        "-c:v",
        "libx264",
        "-preset",
        "ultrafast",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        str(video_only),
        "-map",
        "[aout]",
        "-c:a",
        "pcm_s24le",
        str(premaster),
    ]
    proc = subprocess.run(split_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    (out_dir / "production.ffmpeg.log").write_bytes(proc.stderr)
    if proc.returncode != 0 or not video_only.is_file() or not premaster.is_file():
        report["status"] = "production_encode_failed"
        report["qualified"] = False
        return report
    output = out_dir / "production_not_reference.mp4"
    loudness = _apply_loudness(project, premaster, video_only, output, out_dir)
    if not loudness.get("ok"):
        report["status"] = "production_encode_failed"
        report["loudness"] = loudness
        report["qualified"] = False
        return report
    log_text = (out_dir / "production.ffmpeg.log").read_text(encoding="utf-8", errors="replace")
    fontselect = [line.strip() for line in log_text.splitlines() if "fontselect:" in line]
    report["status"] = "representative_native_produce" if project.get("span") == "representative" else "production_composite"
    report["output"] = str(output)
    report["qualified"] = False
    report["recovered_master"] = False
    report["independent_ffmpeg_probe"] = False
    report["component_calls"] = [
        {key: value for key, value in call.items() if key != "ass_line"} for call in component_calls
    ]
    report["fontselect"] = fontselect
    report["loudness"] = loudness
    report["video_stream_sha256"] = _stream_sha256(output, "v")
    report["video_unchanged_from_pre_loudness_encode"] = report["video_stream_sha256"] == _stream_sha256(video_only, "v")
    report["note"] = (
        "Encoded by recovery_us3day produce. Not the separate local ffmpeg probe. "
        "Not a restored 22-shot film. The burned master was not used as the picture."
    )
    (out_dir / "production_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    premaster.unlink(missing_ok=True)
    video_only.unlink(missing_ok=True)
    return report


def linear_gain_db(measured_i: float, measured_tp: float, target_i: float, tp_ceiling: float) -> float:
    """One linear gain for the whole mix. Voice/BGM ratio stays as mixed."""
    gain = target_i - measured_i
    if measured_tp + gain > tp_ceiling:
        gain = tp_ceiling - measured_tp
    return gain


def _loudness_spec(project: dict) -> dict:
    spec = (project.get("audio") or {}).get("loudness") or {}
    return {
        "target_i_lufs": float(spec.get("target_i_lufs", -16.0)),
        "true_peak_ceiling_dbtp": float(spec.get("true_peak_ceiling_dbtp", -1.5)),
        "layer": spec.get("layer", "reconstructed_technical_target"),
        "not_original_master_parameter": True,
        "master_file_remeasured": False,
        "documented_master_not_applied": {
            "i_lufs": -14.0,
            "true_peak_dbtp": -2.4,
            "source": "SUBMIT_final_v1.md",
            "note": "Document value only. final_v1.mp4 is not in this environment, so it was not measured again and is not this mix target.",
        },
    }


def _measure_loudness(path: Path) -> dict:
    proc = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-i",
            str(path),
            "-af",
            "loudnorm=print_format=json",
            "-f",
            "null",
            "-",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    text = proc.stderr.decode("utf-8", "replace")
    start = text.rfind("{")
    end = text.rfind("}")
    if proc.returncode != 0 or start < 0 or end < start:
        return {"ok": False, "error": text[-400:]}
    payload = json.loads(text[start : end + 1])
    probe = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(path),
        ],
        stdout=subprocess.PIPE,
        check=False,
    )
    duration = None
    if probe.returncode == 0:
        duration = float(json.loads(probe.stdout.decode("utf-8"))["format"]["duration"])
    return {
        "ok": True,
        "i_lufs": float(payload["input_i"]),
        "true_peak_dbtp": float(payload["input_tp"]),
        "lra": float(payload["input_lra"]),
        "threshold_lufs": float(payload["input_thresh"]),
        "duration_seconds": duration,
    }


def _stream_sha256(path: Path, kind: str) -> str:
    proc = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-map", f"0:{kind}:0", "-f", "streamhash", "-hash", "sha256", "-"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    line = proc.stdout.decode("utf-8", "replace").strip()
    return line.split("=", 1)[-1].strip()


def _mux_gain(video: Path, wav: Path, output: Path, gain_db: float) -> bool:
    proc = subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(video),
            "-i",
            str(wav),
            "-filter:a",
            f"volume={gain_db:.4f}dB",
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            str(output),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return proc.returncode == 0 and output.is_file()


def _apply_loudness(project: dict, premaster: Path, video_only: Path, output: Path, out_dir: Path) -> dict:
    spec = _loudness_spec(project)
    before = _measure_loudness(premaster)
    if not before.get("ok"):
        return {"ok": False, "stage": "measure_premaster", **before, "spec": spec}
    gain = linear_gain_db(
        before["i_lufs"],
        before["true_peak_dbtp"],
        spec["target_i_lufs"],
        spec["true_peak_ceiling_dbtp"],
    )
    if not _mux_gain(video_only, premaster, output, gain):
        return {"ok": False, "stage": "mux", "applied_gain_db": gain, "spec": spec}
    after = _measure_loudness(output)
    if not after.get("ok"):
        return {"ok": False, "stage": "measure_output", "applied_gain_db": gain, "spec": spec}
    limited_again = False
    if after["true_peak_dbtp"] > spec["true_peak_ceiling_dbtp"]:
        gain -= after["true_peak_dbtp"] - spec["true_peak_ceiling_dbtp"] + 0.3
        limited_again = True
        if not _mux_gain(video_only, premaster, output, gain):
            return {"ok": False, "stage": "remux_peak", "applied_gain_db": gain, "spec": spec}
        after = _measure_loudness(output)
    return {
        "ok": True,
        "method": "linear_gain_on_finished_mix",
        "ratio_preserved": True,
        "tail_trimmed": False,
        "spec": spec,
        "before": before,
        "applied_gain_db": round(gain, 4),
        "peak_limited": before["true_peak_dbtp"] + (spec["target_i_lufs"] - before["i_lufs"]) > spec["true_peak_ceiling_dbtp"] or limited_again,
        "after": after,
        "true_peak_within_ceiling": after.get("true_peak_dbtp", 99) <= spec["true_peak_ceiling_dbtp"] + 0.05,
    }
