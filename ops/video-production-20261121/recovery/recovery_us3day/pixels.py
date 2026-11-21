"""RGB helpers. JPEG/PPM only, no third-party imaging library."""

from __future__ import annotations

import subprocess
from pathlib import Path


def is_yellow(r: int, g: int, b: int) -> bool:
    return r > 190 and 140 < g < 235 and b < 120 and r > g + 10 and g > b + 30


def is_white(r: int, g: int, b: int) -> bool:
    return r > 220 and g > 220 and b > 220 and abs(r - g) < 18 and abs(g - b) < 18


def is_yellow_hex(value: str) -> bool:
    hex_digits = value.strip().lstrip("#")
    if len(hex_digits) != 6:
        return False
    r = int(hex_digits[0:2], 16)
    g = int(hex_digits[2:4], 16)
    b = int(hex_digits[4:6], 16)
    return r > 200 and g > 150 and b < 140 and r > b + 60


def load_rgb(path: str | Path) -> tuple[int, int, bytes]:
    proc = subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-i",
            str(path),
            "-f",
            "image2pipe",
            "-vcodec",
            "ppm",
            "-frames:v",
            "1",
            "pipe:1",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode("utf-8", "replace")[-500:])
    data = proc.stdout
    if not data.startswith(b"P6"):
        raise RuntimeError(f"not a PPM: {path}")
    index = data.index(b"\n") + 1
    tokens: list[bytes] = []
    while len(tokens) < 3:
        while data[index : index + 1] in b" \n\t":
            index += 1
        end = index
        while data[end : end + 1] not in b" \n\t":
            end += 1
        tokens.append(data[index:end])
        index = end
    if data[index : index + 1] == b"\n":
        index += 1
    width, height = int(tokens[0]), int(tokens[1])
    raw = data[index:]
    if len(raw) != width * height * 3:
        raise RuntimeError(f"ppm size mismatch {path}: {len(raw)} != {width * height * 3}")
    return width, height, raw


def mask_bbox(width: int, height: int, raw: bytes, predicate, y0: int = 0, y1: int | None = None) -> dict | None:
    y1 = height if y1 is None else y1
    xs: list[int] = []
    ys: list[int] = []
    samples: list[tuple[int, int, int]] = []
    for y in range(y0, y1):
        row = y * width * 3
        for x in range(width):
            offset = row + x * 3
            red, green, blue = raw[offset], raw[offset + 1], raw[offset + 2]
            if predicate(red, green, blue):
                xs.append(x)
                ys.append(y)
                if len(samples) < 4000:
                    samples.append((red, green, blue))
    if not xs:
        return None
    samples.sort()
    median = samples[len(samples) // 2]
    return {
        "x0": min(xs),
        "y0": min(ys),
        "x1": max(xs),
        "y1": max(ys),
        "count": len(xs),
        "median_rgb": list(median),
    }


def count_mask(width: int, height: int, raw: bytes, predicate, y0: int, y1: int) -> int:
    total = 0
    y0 = max(0, y0)
    y1 = min(height, y1)
    for y in range(y0, y1):
        row = y * width * 3
        for x in range(width):
            offset = row + x * 3
            if predicate(raw[offset], raw[offset + 1], raw[offset + 2]):
                total += 1
    return total
