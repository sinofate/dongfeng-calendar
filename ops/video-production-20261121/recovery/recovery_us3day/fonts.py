"""Noto Sans CJK SC only. A missing file is a gap, not a licence to substitute."""

from __future__ import annotations

from pathlib import Path

FAMILY = "Noto Sans CJK SC"
KNOWN_REGULAR = Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
KNOWN_BOLD = Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc")
# fc-match on the production machine: SC is face index 2 inside each TTC.
FACE_INDEX = 2


class FontMissing(RuntimeError):
    def __init__(self, missing: list[str]):
        self.missing = missing
        super().__init__("Noto Sans CJK SC is not available: " + ", ".join(missing))


def _resolve_file(value: str | None, fallback: Path) -> Path:
    if not value:
        vendored = Path(__file__).resolve().parents[1] / "inputs" / "fonts" / fallback.name
        if vendored.is_file():
            return vendored
        return fallback
    path = Path(value)
    if path.is_file():
        return path
    rooted = Path(__file__).resolve().parents[1] / value
    if rooted.is_file():
        return rooted
    return path


def resolve_noto(regular: str | None = None, bold: str | None = None) -> dict:
    regular_path = _resolve_file(regular, KNOWN_REGULAR)
    bold_path = _resolve_file(bold, KNOWN_BOLD)
    missing = [str(path) for path in (regular_path, bold_path) if not path.is_file()]
    fontsdir = str(bold_path.parent) if not missing and regular_path.parent == bold_path.parent else None
    if not missing and fontsdir is None:
        missing = ["regular and bold are not in the same fonts directory"]
    return {
        "family": FAMILY,
        "regular": str(regular_path),
        "bold": str(bold_path),
        "face_index": FACE_INDEX,
        "fontsdir": fontsdir,
        "missing": missing,
        "ok": not missing,
        "substitute_forbidden": True,
    }
