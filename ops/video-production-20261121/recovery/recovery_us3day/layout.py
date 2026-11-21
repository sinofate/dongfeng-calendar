"""Observed ink and the reconstructed bands that keep type outside the stage.

None of the rectangles below are original source parameters. The shot HTML and
title_band.png were not in the evidence pack. Bands are padded around ink that
was measured on the 540×960 master extracts.
"""

from __future__ import annotations

from .pixels import is_white, is_yellow, load_rgb, mask_bbox

CANVAS = {"w": 1080, "h": 1920, "fps": 30, "layer": "extracted", "source": "master ffprobe"}

# Two spaces. Do not read a master-space y through a 540-tall image.
# frame_02/04 are 540×960 extracts of the 1080×1920 master, so master px = extract px × 2.
EXTRACT_SPACE = {
    "space": "540x960",
    "layer": "observed_on_extract_jpeg",
    "width": 540,
    "height": 960,
    "source_frames": [
        "inputs/reference/frame_02.jpg",
        "inputs/reference/frame_04.jpg",
    ],
    "uncertainty_px": 2,
    "not_a_source_coordinate": True,
    "title_l1_yellow": {"x0": 176, "y0": 76, "x1": 363, "y1": 104},
    "title_l2_white": {"x0": 220, "y0": 119, "x1": 319, "y1": 142},
    "subtitle_bright_core": {"x0": 128, "y0": 745, "x1": 412, "y1": 768},
}
MASTER_SPACE = {
    "space": "1080x1920",
    "layer": "extract_multiplied_by_2",
    "width": 1080,
    "height": 1920,
    "scale_from_extract": 2,
    "not_measured_on_the_540_image": True,
    "title_l1_yellow": {"x0": 352, "y0": 152, "x1": 726, "y1": 208},
    "title_l2_white": {"x0": 440, "y0": 238, "x1": 638, "y1": 284},
    "subtitle_bright_core": {"x0": 256, "y0": 1490, "x1": 824, "y1": 1536},
    "notes": [
        "y1490–1536 is a 1080×1920 coordinate. The same ink on the 540×960 extract is y745–768.",
        "ASS fontsize 76 and MarginV 370 put the subtitle em center near master y=1512, which matches this scaled core.",
        "Documented L1 y130 / L2 y220 and title_band y150–290 are a third record, in master space, and are not these boxes.",
    ],
}
# Backward-looking alias. Values are master space, not extract space.
OBSERVED_INK = {
    **MASTER_SPACE,
    "extract_space": EXTRACT_SPACE,
}

# Padded so the extracted subtitle em (top about 1474, outline 5) and the observed
# title ink stay outside the stage. Heights are multiples of 3 so a 360×640
# reference plate crops on whole pixels. That grid snap is also reconstruction.
RECONSTRUCTION = {
    "layer": "reconstructed",
    "not_original_rect": True,
    "method": (
        "Title band contains the observed two-line ink. Subtitle band contains "
        "the ASS em estimated from fontsize 76 and MarginV 370, plus outline. "
        "The stage is the gap between those bands. 1440 and 312 are padded and "
        "snapped to a 3px grid; they are not source coordinates."
    ),
    "title_band": {"x": 0, "y": 0, "w": 1080, "h": 312},
    "main_rect": {"x": 0, "y": 312, "w": 1080, "h": 1128},
    "subtitle_band": {"x": 0, "y": 1440, "w": 1080, "h": 480},
    "yellow_rule": None,
    "source_corner_labels": False,
    "reference_plate_scale": 3,
}

COLORS = {
    "subtitle_fill": {
        "hex": "#FFD700",
        "layer": "extracted",
        "source": "ASS Style D PrimaryColour &H0000D7FF",
    },
    "subtitle_outline": {
        "hex": "#000000",
        "layer": "extracted",
        "source": "ASS Style D OutlineColour",
        "width": 5,
        "note": "Black historical outline. Not a yellow stroke.",
    },
    "title_l1_fill": {
        "hex": "#FFD700",
        "layer": "reconstructed_choice_of_extracted_ass_fill",
        "note": "Body frames show a yellow first line. The jpeg median is not used as the token.",
    },
    "title_l2_fill": {
        "hex": "#FFFFFF",
        "layer": "observed",
        "note": "Second title line is white on frames 02–05 and on the low-bitrate reference at 2s, 4s, 15s, 60s, 100s, 140s.",
    },
    "band_matte": {
        "hex": "#071829",
        "layer": "documented_token_used_as_reconstruction_matte",
        "source": "frame.md bg",
    },
    "accent_documented_not_used_for_burn": {
        "hex": "#FFD247",
        "layer": "documented",
        "source": "frame.md accent",
    },
    "brand_documented_not_used_for_burn": {
        "hex": "#20C5E8",
        "layer": "documented",
        "source": "frame.md brand",
    },
}

# Reconstruction type metrics taken from observed ink height, not from a font file.
TITLE_DRAW = {
    "layer": "reconstructed",
    "coordinate_space": "1080x1920",
    "font_requested": "Noto Sans CJK SC",
    "font_fallback_forbidden": True,
    "l1": {
        "text_observed": "芯片砸掉三成",
        "size": 88,
        "top": 72,
        "fill": "#FFD700",
        "outline": 0,
        "size_layer": "reconstructed_after_20261121_viewing",
        "note": "Bright-core height on the master is about 56px. The local viewing of the 54px burn found the header too small, so the draw size fills the title band and stays above the stage.",
    },
    "l2": {
        "text_observed": "见底了吗",
        "size": 64,
        "top": 188,
        "fill": "#FFFFFF",
        "outline": 0,
        "size_layer": "reconstructed_after_20261121_viewing",
    },
    "sample_times_seconds": [2.0, 4.0, 15.0, 60.0, 100.0, 140.0],
    "not_every_frame_verified": True,
}


def assert_type_outside_stage() -> None:
    """Title and subtitle boxes must sit outside the stage on the 1080×1920 canvas."""
    stage = RECONSTRUCTION["main_rect"]
    stage_bottom = stage["y"] + stage["h"]
    for key in ("l1", "l2"):
        line = TITLE_DRAW[key]
        bottom = line["top"] + line["size"]
        if line["top"] < 0 or bottom > stage["y"]:
            raise ValueError(f"title {key} intersects the stage: {line['top']}–{bottom} vs stage y {stage['y']}")
    subtitle_bottom = CANVAS["h"] - 370
    subtitle_top = subtitle_bottom - 76 - 5
    if subtitle_top < stage_bottom:
        raise ValueError(f"subtitle top {subtitle_top} enters the stage ending at {stage_bottom}")


def plate_crop(input_w: int, input_h: int) -> dict:
    """Map the 1080×1920 stage onto the actual input frame.

    A 360×640 reference and a 1080×1920 master do not share a crop rectangle.
    Using the 360p crop on the master zooms the top of the picture and leaves
    scraps of the old yellow title inside the stage.
    """
    if input_w <= 0 or input_h <= 0:
        raise ValueError(f"bad input size {input_w}x{input_h}")
    stage = RECONSTRUCTION["main_rect"]
    canvas_w = CANVAS["w"]
    canvas_h = CANVAS["h"]
    x = int(round(stage["x"] * input_w / canvas_w))
    y = int(round(stage["y"] * input_h / canvas_h))
    w = int(round(stage["w"] * input_w / canvas_w))
    h = int(round(stage["h"] * input_h / canvas_h))
    if w < 2 or h < 2 or x < 0 or y < 0 or x + w > input_w or y + h > input_h:
        raise ValueError(f"stage crop {x},{y},{w},{h} does not fit {input_w}x{input_h}")
    return {
        "x": x,
        "y": y,
        "w": w,
        "h": h,
        "input_w": input_w,
        "input_h": input_h,
        "space": f"{input_w}x{input_h}",
        "mapped_from": "1080x1920 main_rect",
    }


def measure_extract(path: str) -> dict:
    width, height, raw = load_rgb(path)
    return {
        "path": path,
        "width": width,
        "height": height,
        "yellow": mask_bbox(width, height, raw, is_yellow),
        "white_top": mask_bbox(width, height, raw, is_white, 100, 160),
        "yellow_title": mask_bbox(width, height, raw, is_yellow, 60, 120),
        "yellow_subtitle": mask_bbox(width, height, raw, is_yellow, 720, 800),
    }


def scaled_box(box: dict | None, scale: int = 2) -> dict | None:
    if box is None:
        return None
    return {
        "x0": box["x0"] * scale,
        "y0": box["y0"] * scale,
        "x1": box["x1"] * scale,
        "y1": box["y1"] * scale,
        "count": box["count"],
        "median_rgb": box["median_rgb"],
    }


def observation_matches_frozen(measured_extract: dict, tolerance: int = 2) -> list[str]:
    """Compare boxes measured on the 540×960 extract, in that image's own pixels."""
    expected = {
        "yellow_title": EXTRACT_SPACE["title_l1_yellow"],
        "white_top": EXTRACT_SPACE["title_l2_white"],
    }
    errors = []
    for key, want in expected.items():
        got = measured_extract.get(key)
        if not got:
            errors.append(f"missing {key}")
            continue
        for edge in ("x0", "y0", "x1", "y1"):
            if abs(got[edge] - want[edge]) > tolerance:
                errors.append(f"{key}.{edge} {got[edge]} vs frozen {want[edge]}")
    return errors
