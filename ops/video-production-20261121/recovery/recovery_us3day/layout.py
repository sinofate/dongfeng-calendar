"""Observed ink and the reconstructed bands that keep type outside the stage.

None of the rectangles below are original source parameters. The shot HTML and
title_band.png were not in the evidence pack. Bands are padded around ink that
was measured on the 540×960 master extracts.
"""

from __future__ import annotations

from .pixels import is_white, is_yellow, load_rgb, mask_bbox

CANVAS = {"w": 1080, "h": 1920, "fps": 30, "layer": "extracted", "source": "master ffprobe"}

# 540×960 extracts scale by 2 onto 1080×1920. Thresholds match pixels.is_yellow / is_white.
OBSERVED_INK = {
    "layer": "observed_on_scaled_jpeg",
    "source_frames": [
        "inputs/reference/frame_02.jpg",
        "inputs/reference/frame_04.jpg",
    ],
    "scale_from_extract": 2,
    "uncertainty_px": 4,
    "not_a_source_coordinate": True,
    "title_l1_yellow": {"x0": 352, "y0": 152, "x1": 726, "y1": 206},
    "title_l2_white": {"x0": 440, "y0": 240, "x1": 638, "y1": 282},
    "subtitle_bright_core": {"x0": 256, "y0": 1492, "x1": 824, "y1": 1536},
    "title_l1_median_rgb": [250, 217, 79],
    "notes": [
        "Bright-core boxes are smaller than an em box. ASS fontsize 76 with MarginV 370 puts the subtitle em center near y=1512, which matches this core.",
        "JPEG median yellow is not the fill token. The burn uses ASS #FFD700.",
        "Documented L1 y130 / L2 y220 and title_band y150–290 are a different record. They are not these boxes.",
    ],
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
    "font_requested": "Noto Sans CJK SC",
    "font_fallback": "WenQuanYi Micro Hei",
    "font_fallback_reason": "Noto Sans CJK SC is not installed in this environment and the original font file was not in the evidence pack.",
    "l1": {"text_observed": "芯片砸掉三成", "size": 54, "top": 152, "fill": "#FFD700", "outline": 0},
    "l2": {"text_observed": "见底了吗", "size": 42, "top": 240, "fill": "#FFFFFF", "outline": 0},
    "sample_times_seconds": [2.0, 4.0, 15.0, 60.0, 100.0, 140.0],
    "not_every_frame_verified": True,
}


def reference_crop() -> dict:
    """Crop of a 360×640 reference that corresponds to the reconstructed stage."""
    stage = RECONSTRUCTION["main_rect"]
    scale = RECONSTRUCTION["reference_plate_scale"]
    if stage["y"] % scale or stage["h"] % scale or stage["w"] % scale:
        raise ValueError("reconstructed stage is not on the reference pixel grid")
    return {
        "x": stage["x"] // scale,
        "y": stage["y"] // scale,
        "w": stage["w"] // scale,
        "h": stage["h"] // scale,
        "scale": scale,
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


def observation_matches_frozen(measured_scaled: dict, tolerance: int = 4) -> list[str]:
    expected = {
        "yellow_title": OBSERVED_INK["title_l1_yellow"],
        "white_top": OBSERVED_INK["title_l2_white"],
    }
    errors = []
    for key, want in expected.items():
        got = measured_scaled.get(key)
        if not got:
            errors.append(f"missing {key}")
            continue
        for edge in ("x0", "y0", "x1", "y1"):
            if abs(got[edge] - want[edge]) > tolerance:
                errors.append(f"{key}.{edge} {got[edge]} vs frozen {want[edge]}")
    return errors
