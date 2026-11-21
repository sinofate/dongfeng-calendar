"""Command line. validate, gaps, and short smoke. No full-length stand-in film."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .catalog import counts, load_catalog
from .compose import extract_frame, render_window, write_reference_extract, yellow_in_band
from .gaps import build_report, render_markdown
from .layout import RECONSTRUCTION
from .project import (
    DEFAULT_ASS,
    DEFAULT_CATALOG,
    DEFAULT_COVER,
    DEFAULT_PROJECT,
    DEFAULT_REFERENCE,
    ROOT,
    load_project,
    validate_project,
    write_project,
)


def _cmd_validate(args: argparse.Namespace) -> int:
    project = load_project(args.project)
    catalog = load_catalog(args.catalog)
    result = validate_project(project, catalog)
    result["catalog_counts"] = counts(catalog)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


def _cmd_gaps(args: argparse.Namespace) -> int:
    report = build_report()
    if args.md:
        text = render_markdown(report)
        if args.out:
            Path(args.out).write_text(text, encoding="utf-8")
        else:
            sys.stdout.write(text)
    else:
        text = json.dumps(report, ensure_ascii=False, indent=2)
        if args.out:
            Path(args.out).write_text(text + "\n", encoding="utf-8")
        else:
            print(text)
    return 0


def _cmd_materialize(_args: argparse.Namespace) -> int:
    project = write_project(DEFAULT_PROJECT)
    result = validate_project(project, load_catalog(DEFAULT_CATALOG))
    if not result["ok"]:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1
    print(f"wrote {DEFAULT_PROJECT}")
    return 0


def _cmd_smoke(args: argparse.Namespace) -> int:
    reference = Path(args.reference)
    ass_path = Path(args.ass)
    cover = Path(args.cover) if args.cover else None
    out_dir = Path(args.out)
    if not reference.is_file() or not ass_path.is_file():
        report = {
            "recovered_master": False,
            "status": "local_verification_pending",
            "missing": [str(path) for path in (reference, ass_path) if not path.is_file()],
        }
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "preflight.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 2
    if not args.allow_reference_plate:
        report = {
            "recovered_master": False,
            "status": "local_verification_pending",
            "reason": "shot assets are null and --allow-reference-plate was not set",
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 2
    protected = [ROOT / "inputs"]
    opening = render_window(
        reference=reference,
        ass_path=ass_path,
        output=out_dir / "smoke_opening_not_recovered_master.mp4",
        start=0.0,
        end=4.0,
        cover=cover,
        cover_until=1.5 if cover else None,
        protected_dirs=protected,
    )
    comment = render_window(
        reference=reference,
        ass_path=ass_path,
        output=out_dir / "smoke_s12_comment_window_not_recovered_master.mp4",
        start=65.9,
        end=67.0,
        cover=None,
        cover_until=None,
        protected_dirs=protected,
    )
    extract_frame(out_dir / "smoke_opening_not_recovered_master.mp4", 2.5, out_dir / "smoke_opening_t2.5.jpg")
    extract_frame(out_dir / "smoke_s12_comment_window_not_recovered_master.mp4", 0.5, out_dir / "smoke_s12_t66.4.jpg")
    write_reference_extract(reference, 15.0, out_dir / "reference_extract_t15_NOT_A_RENDER.jpg")
    write_reference_extract(reference, 66.2, out_dir / "reference_extract_t66.2_NOT_A_RENDER.jpg")
    title_band = RECONSTRUCTION["title_band"]
    subtitle_band = RECONSTRUCTION["subtitle_band"]
    measures = {
        "opening_t2.5_title_yellow": yellow_in_band(
            out_dir / "smoke_opening_t2.5.jpg", title_band["y"], title_band["y"] + title_band["h"]
        ),
        "opening_t2.5_subtitle_yellow": yellow_in_band(
            out_dir / "smoke_opening_t2.5.jpg", subtitle_band["y"], subtitle_band["y"] + subtitle_band["h"]
        ),
        "s12_t66.4_title_yellow": yellow_in_band(
            out_dir / "smoke_s12_t66.4.jpg", title_band["y"], title_band["y"] + title_band["h"]
        ),
        "s12_t66.4_subtitle_yellow": yellow_in_band(
            out_dir / "smoke_s12_t66.4.jpg", subtitle_band["y"], subtitle_band["y"] + subtitle_band["h"]
        ),
    }
    report = {
        "recovered_master": False,
        "status": "smoke_composite_on_reference_plate",
        "acceptance_recovered_film": False,
        "reason": "Original clips and vo_raw are absent. The stage shows a crop of the low-bitrate reference. Source lines baked into that plate and into the cover JPEG are still in those pixels; this compositor does not draw them.",
        "opening": opening,
        "s12_comment_window": comment,
        "band_yellow_counts": measures,
        "layout_layer": "reconstructed",
        "revised_lr_locked": False,
        "historical_lr_used_for_smoke": 30,
    }
    (out_dir / "smoke_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    title_ok = measures["opening_t2.5_title_yellow"] > 200 and measures["s12_t66.4_title_yellow"] > 200
    subtitle_ok = measures["opening_t2.5_subtitle_yellow"] > 200 and measures["s12_t66.4_subtitle_yellow"] < 30
    return 0 if title_ok and subtitle_ok else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="recovery_us3day")
    sub = parser.add_subparsers(dest="cmd", required=True)
    validate = sub.add_parser("validate")
    validate.add_argument("--project", type=Path, default=DEFAULT_PROJECT)
    validate.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    validate.set_defaults(func=_cmd_validate)
    gaps = sub.add_parser("gaps")
    gaps.add_argument("--md", action="store_true")
    gaps.add_argument("--out", type=Path)
    gaps.set_defaults(func=_cmd_gaps)
    materialize = sub.add_parser("materialize")
    materialize.set_defaults(func=_cmd_materialize)
    smoke = sub.add_parser("smoke")
    smoke.add_argument("--reference", type=Path, default=DEFAULT_REFERENCE)
    smoke.add_argument("--ass", type=Path, default=DEFAULT_ASS)
    smoke.add_argument("--cover", type=Path, default=DEFAULT_COVER)
    smoke.add_argument("--out", type=Path, required=True)
    smoke.add_argument("--allow-reference-plate", action="store_true")
    smoke.set_defaults(func=_cmd_smoke)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
