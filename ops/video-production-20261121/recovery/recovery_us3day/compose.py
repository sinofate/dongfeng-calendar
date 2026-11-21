"""Short smoke compositor.

The reference file is a downscaled copy of the old master. Cropping it into the
stage is a plate for layout smoke. It is not a recovered render and it is not
written back over the reference.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from .assparse import events_overlapping, format_ass_time, parse_ass
from .fonts import FAMILY, FontMissing, resolve_noto
from .layout import RECONSTRUCTION, TITLE_DRAW, plate_crop
from .pixels import count_mask, is_yellow, load_rgb

LATER_MARGIN_L = 90
LATER_MARGIN_R = 90
MATTE = "0x071829"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def probe(path: Path) -> dict:
    proc = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_streams",
            "-show_format",
            "-of",
            "json",
            str(path),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode("utf-8", "replace")[-800:])
    return json.loads(proc.stdout.decode("utf-8"))


def _hex_to_ass(color: str) -> str:
    red = color[1:3]
    green = color[3:5]
    blue = color[5:7]
    return f"&H00{blue}{green}{red}".upper()


def _style_line(name, font, size, primary, outline_color, outline, shadow, alignment, margin_l, margin_r, margin_v) -> str:
    primary_ass = _hex_to_ass(primary)
    outline_ass = _hex_to_ass(outline_color)
    return (
        f"Style: {name},{font},{size},{primary_ass},&H000000FF,{outline_ass},&H00000000,"
        f"-1,0,0,0,100,100,0,0,1,{outline},{shadow},{alignment},{margin_l},{margin_r},{margin_v},1"
    )


def build_smoke_ass(ass_path: Path, start: float, end: float, shift: float, title_from: float, titles: dict | None = None) -> str:
    parsed = parse_ass(ass_path)
    style = parsed.style
    if "WenQuanYi" in FAMILY or "Micro Hei" in FAMILY:
        raise ValueError("substitute font is not allowed")
    if style.outline_color.upper() != "#000000":
        raise ValueError("refusing to burn a non-black extracted outline")
    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: 1080",
        "PlayResY: 1920",
        "WrapStyle: 2",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        _style_line("TitleY", FAMILY, TITLE_DRAW["l1"]["size"], TITLE_DRAW["l1"]["fill"], "#000000", 0, 0, 8, LATER_MARGIN_L, LATER_MARGIN_R, TITLE_DRAW["l1"]["top"]),
        _style_line("TitleW", FAMILY, TITLE_DRAW["l2"]["size"], TITLE_DRAW["l2"]["fill"], "#000000", 0, 0, 8, LATER_MARGIN_L, LATER_MARGIN_R, TITLE_DRAW["l2"]["top"]),
        _style_line(
            "D",
            FAMILY,
            style.fontsize,
            style.primary,
            style.outline_color,
            style.outline,
            style.shadow,
            style.alignment,
            LATER_MARGIN_L,
            LATER_MARGIN_R,
            style.margin_v,
        ),
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    title_l1 = (titles or {}).get("l1") or TITLE_DRAW["l1"]["text_observed"]
    title_l2 = (titles or {}).get("l2") or TITLE_DRAW["l2"]["text_observed"]
    title_start = max(start, title_from)
    if title_start < end:
        lines.append(
            f"Dialogue: 0,{format_ass_time(title_start - shift)},{format_ass_time(end - shift)},TitleY,,0,0,0,,{title_l1}"
        )
        lines.append(
            f"Dialogue: 0,{format_ass_time(title_start - shift)},{format_ass_time(end - shift)},TitleW,,0,0,0,,{title_l2}"
        )
    for event in events_overlapping(parsed.events, start, end, kind="dialogue"):
        cue_start = max(event.start, start) - shift
        cue_end = min(event.end, end) - shift
        if cue_end <= cue_start:
            continue
        if "来源" in event.text or event.text == "大约三成":
            raise ValueError(f"refusing to burn {event.text!r}")
        lines.append(
            f"Dialogue: 0,{format_ass_time(cue_start)},{format_ass_time(cue_end)},D,,0,0,0,,{event.text}"
        )
    text = "\n".join(lines) + "\n"
    if "大约三成" in text or "来源" in text:
        raise ValueError("smoke ASS contains a comment cue or a source badge")
    if "&H0000D7FF" in text.split("Style: TitleY", 1)[-1].split("Style:", 1)[0]:
        pass
    for style_row in text.splitlines():
        if style_row.startswith("Style:") and ",&H0000D7FF,&H000000FF,&H0000D7FF," in style_row:
            raise ValueError("yellow outline style was generated")
        if style_row.startswith("Style:") and ",&H0047D2FF," in style_row:
            raise ValueError("documented #FFD247 was written into the burn")
    return text


CANVAS_W = 1080
CANVAS_H = 1920


def window_video_chain() -> str:
    """Normalize the whole frame to 1080×1920, then keep only the stage.

    Cropping a 360p rectangle out of a 1080p master zooms the top of the picture,
    clips the right side of the card, and pulls old title ink into the window.
    Scaling the full frame first makes a 1080×1920 input a 1:1 window. The pad
    is the only pixels in the title and subtitle bands.
    """
    from .layout import assert_type_outside_stage

    assert_type_outside_stage()
    stage = RECONSTRUCTION["main_rect"]
    return (
        f"setsar=1,scale={CANVAS_W}:{CANVAS_H}:flags=lanczos,"
        f"crop={stage['w']}:{stage['h']}:{stage['x']}:{stage['y']},"
        f"pad={CANVAS_W}:{CANVAS_H}:{stage['x']}:{stage['y']}:color={MATTE},setsar=1,format=yuv420p"
    )


def _filter_graph(ass_file: Path, start: float, end: float, cover_until: float | None, fontsdir: str) -> str:
    window = window_video_chain()
    subtitles = f"subtitles=filename='{ass_file}':fontsdir='{fontsdir}'"
    if cover_until is None:
        return ";".join(
            [
                f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS,{window}[staged]",
                f"[staged]{subtitles}[vout]",
                f"[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS[aout]",
            ]
        )
    plate_start = cover_until
    frames = int(round(cover_until * 30))
    return ";".join(
        [
            (
                f"[0:v]scale=1080:1920:flags=neighbor,setsar=1,"
                f"zoompan=z='1+0.03*on/{frames - 1}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                f"d={frames}:s=1080x1920:fps=30,format=yuv420p,trim=end={cover_until},setpts=PTS-STARTPTS[cover]"
            ),
            f"[1:v]trim=start={plate_start}:end={end},setpts=PTS-STARTPTS,{window}[staged]",
            "[cover][staged]concat=n=2:v=1:a=0[cat]",
            f"[cat]{subtitles}[vout]",
            f"[1:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS[aout]",
        ]
    )


def _assert_output_safe(output: Path, protected: list[Path]) -> None:
    output = output.resolve()
    for path in protected:
        path = path.resolve()
        if output == path:
            raise ValueError(f"refusing to overwrite protected input {path}")
        if path.is_dir() and output.is_relative_to(path):
            raise ValueError(f"refusing to write inside protected directory {path}")


def render_window(
    *,
    reference: Path,
    ass_path: Path,
    output: Path,
    start: float,
    end: float,
    cover: Path | None = None,
    cover_until: float | None = None,
    protected_dirs: list[Path] | None = None,
) -> dict:
    if end - start <= 0 or end - start > 12:
        raise ValueError("smoke window must be between 0 and 12 seconds")
    output.parent.mkdir(parents=True, exist_ok=True)
    protected = [reference, ass_path]
    if cover is not None:
        protected.append(cover)
    protected.extend(protected_dirs or [])
    _assert_output_safe(output, protected)
    fonts = resolve_noto()
    if not fonts["ok"]:
        raise FontMissing(fonts["missing"])
    info = probe(reference)
    video = next(stream for stream in info["streams"] if stream["codec_type"] == "video")
    crop = plate_crop(int(video["width"]), int(video["height"]))
    shift = 0.0 if cover_until is not None else start
    title_from = cover_until if cover_until is not None else start
    ass_text = build_smoke_ass(ass_path, start, end, shift, title_from)
    if "WenQuanYi" in ass_text or "Micro Hei" in ass_text:
        raise ValueError("generated ASS names a substitute font")
    ass_file = output.with_suffix(".ass")
    ass_file.write_text(ass_text, encoding="utf-8")
    graph = _filter_graph(ass_file, start, end, cover_until, fonts["fontsdir"])
    if cover_until is None:
        cmd = [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(reference),
            "-filter_complex",
            graph,
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
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            str(output),
        ]
    else:
        cmd = [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(cover),
            "-i",
            str(reference),
            "-filter_complex",
            graph,
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
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-t",
            f"{end - start:.3f}",
            str(output),
        ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    log_path = output.with_suffix(".ffmpeg.log")
    log_path.write_bytes(proc.stderr)
    if proc.returncode != 0 or not output.exists():
        raise RuntimeError(f"ffmpeg failed ({proc.returncode}): {proc.stderr.decode('utf-8', 'replace')[-1000:]}")
    if sha256_file(output) == sha256_file(reference):
        output.unlink()
        raise RuntimeError("output hash matched the reference; refusing to treat a copy as a render")
    info = probe(output)
    video = next(stream for stream in info["streams"] if stream["codec_type"] == "video")
    audio = next(stream for stream in info["streams"] if stream["codec_type"] == "audio")
    if int(video["width"]) != 1080 or int(video["height"]) != 1920:
        raise RuntimeError(f"unexpected size {video['width']}x{video['height']}")
    if video.get("avg_frame_rate") not in {"30/1", "30/1"}:
        raise RuntimeError(f"unexpected frame rate {video.get('avg_frame_rate')}")
    return {
        "output": str(output),
        "ass": str(ass_file),
        "sha256": sha256_file(output),
        "reference_sha256": sha256_file(reference),
        "same_bytes_as_reference": False,
        "width": int(video["width"]),
        "height": int(video["height"]),
        "fps": video.get("avg_frame_rate"),
        "video_duration": float(video["duration"]),
        "audio_duration": float(audio["duration"]),
        "recovered_master": False,
        "qualified": False,
        "acceptance": "not_qualified",
        "clearance_verified": False,
        "residual_burned_in_text_removed": False,
        "input_width": crop["input_w"],
        "input_height": crop["input_h"],
        "plate_crop": {key: crop[key] for key in ("x", "y", "w", "h", "space")},
        "font_family": FAMILY,
        "margin_l": LATER_MARGIN_L,
        "margin_r": LATER_MARGIN_R,
        "plate": "reference_plate_diagnostic" if cover_until is None else "cover_then_reference_plate_diagnostic",
        "audio": "reference_mix_trim_not_a_new_mix",
        "encode": "smoke_ultrafast_crf18_not_master_recipe",
        "ffmpeg_log": str(log_path),
    }


def extract_frame(video: Path, second: float, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-ss", f"{second:.3f}", "-i", str(video), "-frames:v", "1", str(output)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode("utf-8", "replace")[-500:])


def yellow_in_band(image: Path, y0: int, y1: int) -> int:
    _width, _height, raw = load_rgb(image)
    return count_mask(_width, _height, raw, is_yellow, y0, y1)


def write_reference_extract(reference: Path, second: float, output: Path) -> dict:
    extract_frame(reference, second, output)
    sidecar = output.with_suffix(".json")
    payload = {
        "role": "reference_extract_not_a_render",
        "source": str(reference),
        "second": second,
        "note": "Frame grabbed from the low-bitrate reference. Not a recovery render.",
    }
    sidecar.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload
