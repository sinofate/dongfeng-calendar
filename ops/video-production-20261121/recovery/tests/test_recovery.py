import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from recovery_us3day.assparse import parse_ass
from recovery_us3day.catalog import counts, load_catalog, lookup_name, validate_binding
from recovery_us3day.cli import main
from recovery_us3day.components import resolve_component
from recovery_us3day.compose import build_smoke_ass
from recovery_us3day.fonts import resolve_noto
from recovery_us3day.produce import produce
from recovery_us3day.layout import (
    EXTRACT_SPACE,
    MASTER_SPACE,
    RECONSTRUCTION,
    measure_extract,
    observation_matches_frozen,
    plate_crop,
)
from recovery_us3day.project import ROOT, build_project, validate_project
from recovery_us3day.timeline import accumulated_frame_clock, frame_sum, load_timeline, validate_timeline

ASS = ROOT / "inputs" / "source-docs" / "final_v1.ass"
TIMELINE = ROOT / "inputs" / "source-docs" / "timeline.json"
CATALOG = ROOT / "inputs" / "asset_catalog.json"
REFERENCE = ROOT / "inputs" / "reference" / "master_full_lowbitrate_REFERENCE_NOT_RERENDER.mp4"
COVER = ROOT / "inputs" / "reference" / "cover_1080x1920.jpg"
FRAME_02 = ROOT / "inputs" / "reference" / "frame_02.jpg"
FRAME_04 = ROOT / "inputs" / "reference" / "frame_04.jpg"


class TimelineTests(unittest.TestCase):
    def test_clock_uses_seconds_and_reports_frame_gap(self):
        timeline = load_timeline(TIMELINE)
        report = validate_timeline(timeline)
        self.assertTrue(report["ok"], report["errors"])
        self.assertEqual(report["shot_count"], 22)
        self.assertEqual(frame_sum(timeline), 4516)
        self.assertAlmostEqual(report["frame_sum_seconds"], 4516 / 30, places=9)
        self.assertAlmostEqual(timeline.total, 150.564, places=6)
        self.assertGreater(report["frame_quantization_gap_seconds"], 0.03)
        drift = accumulated_frame_clock(timeline)
        self.assertNotEqual(drift[1]["accumulated_seconds"], drift[1]["t0"])
        self.assertEqual(timeline.shots[1].t0, 5.346)
        self.assertEqual(timeline.impact_at, "s20.hero_land")


class AssTests(unittest.TestCase):
    def test_dialogue_and_comment_are_split(self):
        ass = parse_ass(ASS)
        self.assertEqual((ass.play_res_x, ass.play_res_y), (1080, 1920))
        self.assertEqual(len(ass.dialogues), 81)
        self.assertEqual(len(ass.comments), 1)
        self.assertEqual(ass.comments[0].text, "大约三成")
        self.assertAlmostEqual(ass.comments[0].start, 66.09, places=2)
        lengths = [len(event.text) for event in ass.dialogues]
        self.assertEqual(max(lengths), 15)
        self.assertAlmostEqual(sum(lengths) / len(lengths), 10.2593, places=4)
        self.assertEqual(ass.style.fontsize, 76)
        self.assertEqual(ass.style.primary, "#FFD700")
        self.assertEqual(ass.style.outline_color, "#000000")
        self.assertEqual(ass.style.outline, 5)
        self.assertEqual(ass.style.margin_l, 30)
        self.assertEqual(ass.style.margin_r, 30)
        self.assertEqual(ass.style.margin_v, 370)
        burned = "\n".join(event.text for event in ass.dialogues)
        self.assertNotIn("\n大约三成\n", f"\n{burned}\n")

    def test_smoke_ass_skips_comment_and_source_badge(self):
        text = build_smoke_ass(ASS, 65.9, 67.0, 65.9, 65.9)
        self.assertNotIn("大约三成", text)
        self.assertNotIn("来源", text)
        self.assertIn("Noto Sans CJK SC", text)
        self.assertNotIn("WenQuanYi", text)
        self.assertIn(",90,90,370,", text)
        self.assertIn("砸到周四低点约九千，算下来", text)
        self.assertNotIn("&H0047D2FF", text)
        for line in text.splitlines():
            if line.startswith("Style: Title"):
                self.assertIn(",0,0,8,", line)
            if ",&H0000D7FF,&H000000FF,&H0000D7FF," in line:
                self.fail(line)


class CatalogTests(unittest.TestCase):
    def test_counts_come_from_the_index(self):
        catalog = load_catalog(CATALOG)
        tally = counts(catalog)
        self.assertEqual(tally["entries"], len(catalog["entries"]))
        self.assertEqual(tally["entries"], 777)
        self.assertEqual(tally["by_library"]["hf_components"], 237)
        self.assertEqual(tally["by_library"]["hf_blocks"], 210)
        self.assertEqual(tally["by_library"]["shotcraft"], 125)
        self.assertEqual(tally["by_library"]["motion_curated"], 34)
        self.assertEqual(tally["by_library"]["bgm_tracks"], 42)
        self.assertEqual(tally["by_library"]["sfx_semantic"], 89)
        self.assertEqual(tally["by_library"]["sfx_legacy"], 16)
        self.assertEqual(tally["by_kind"]["motion"], 481)
        self.assertEqual(lookup_name(catalog, "count-up"), ["hf_components:count-up", "motion_curated:count-up"])

    def test_schema_rejects_wrapper_coercion_and_stand_ins(self):
        catalog = load_catalog(CATALOG)
        valid = validate_binding(
            catalog,
            {
                "id": "hf_components:count-up",
                "variables": {
                    "start": 0,
                    "end": 128,
                    "prefix": "",
                    "suffix": "%",
                    "accent": "green",
                    "glow": False,
                    "exit": "none",
                },
            },
        )
        self.assertTrue(valid["ok"], valid)
        coerced = validate_binding(
            catalog,
            {"id": "hf_components:count-up", "variables": {"accent": "#FFD247", "glow": 0.6}},
        )
        self.assertFalse(coerced["ok"])
        echo = validate_binding(catalog, {"id": "echo_example:18-water", "variables": {}})
        self.assertFalse(echo["ok"])
        recipe = validate_binding(catalog, {"id": "shotcraft:ATTRIBUTION", "variables": {}})
        self.assertFalse(recipe["ok"])
        missing = validate_binding(catalog, {"id": "hf_components:not-a-real-component", "variables": {}})
        self.assertFalse(missing["ok"])


class ProjectTests(unittest.TestCase):
    def test_project_joins_suggestion_to_timeline_clock(self):
        project = build_project()
        catalog = load_catalog(CATALOG)
        result = validate_project(project, catalog)
        self.assertTrue(result["ok"], result)
        self.assertEqual(len(project["shots"]), 22)
        self.assertEqual(project["subtitles"]["later_revision_lr"], 90)
        self.assertEqual(project["subtitles"]["historical_lr"], 30)
        self.assertEqual(
            project["subtitles"]["later_revision_evidence"]["md5"],
            "4887b2bebd4e502ee44f53c0ae132316",
        )
        self.assertIsNone(project["layout"]["yellow_rule"])
        self.assertFalse(project["output"]["source_corner_labels"])
        self.assertIsNone(project["shots"][0]["media"])
        self.assertIsNone(project["shots"][0]["component"]["id"])
        s12 = project["shots"][11]
        self.assertNotIn("大约三成", s12["dialogue"])
        self.assertEqual(s12["t0"], 60.756)
        self.assertEqual(project["shots"][1]["t0"], 5.346)
        self.assertEqual(project["e7y"]["invoked_by_this_cloud_session"], False)
        self.assertEqual(project["e7y"]["full_code_returned"], False)
        project["engine"] = "385712"
        self.assertFalse(validate_project(project, catalog)["ok"])


class LayoutTests(unittest.TestCase):
    def test_frozen_ink_matches_master_extracts(self):
        title = measure_extract(str(FRAME_02))
        native = {"yellow_title": title["yellow_title"], "white_top": title["white_top"]}
        self.assertEqual(title["width"], 540)
        self.assertEqual(title["height"], 960)
        self.assertEqual(observation_matches_frozen(native, tolerance=2), [])
        subtitle = measure_extract(str(FRAME_04))["yellow_subtitle"]
        want = EXTRACT_SPACE["subtitle_bright_core"]
        for edge, value in want.items():
            self.assertAlmostEqual(subtitle[edge], value, delta=2)
        self.assertLess(want["y1"], 960)
        master = MASTER_SPACE["subtitle_bright_core"]
        self.assertEqual(master["y0"], want["y0"] * 2)
        self.assertGreater(master["y0"], 960)
        full = plate_crop(1080, 1920)
        small = plate_crop(360, 640)
        self.assertEqual((full["x"], full["y"], full["w"], full["h"]), (0, 312, 1080, 1128))
        self.assertEqual((small["y"], small["h"], small["w"]), (104, 376, 360))
        self.assertNotEqual(full["h"], small["h"])
        stage = RECONSTRUCTION["main_rect"]
        self.assertLess(MASTER_SPACE["title_l2_white"]["y1"], stage["y"])
        self.assertGreater(master["y0"], stage["y"] + stage["h"])
        from recovery_us3day.layout import assert_type_outside_stage

        assert_type_outside_stage()

    def test_normalize_then_window_keeps_bands_empty(self):
        from recovery_us3day.compose import window_video_chain
        from recovery_us3day.pixels import load_rgb

        chain = window_video_chain()
        self.assertIn("scale=1080:1920", chain)
        self.assertIn("crop=1080:1128:0:312", chain)
        self.assertNotIn("crop=360:376:0:104", chain)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "window.jpg"
            source = (
                "color=c=0xFF0000:s=1080x1920:r=30:d=0.1,"
                "geq=r='if(lt(Y,312),255,if(lt(Y,1440),0,0))':"
                "g='if(lt(Y,312),0,if(lt(Y,1440),255,0))':"
                "b='if(lt(Y,312),0,if(lt(Y,1440),0,255))'"
            )
            proc = subprocess.run(
                [
                    "ffmpeg", "-y", "-v", "error",
                    "-f", "lavfi", "-i", source,
                    "-vf", chain,
                    "-frames:v", "1",
                    str(out),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr.decode("utf-8", "replace")[-500:])
            width, height, raw = load_rgb(out)
            self.assertEqual((width, height), (1080, 1920))

            def pixel(x, y):
                offset = (y * width + x) * 3
                return raw[offset], raw[offset + 1], raw[offset + 2]

            top = pixel(20, 20)
            middle = pixel(540, 800)
            bottom = pixel(20, 1800)

            def near_matte(rgb):
                return abs(rgb[0] - 7) + abs(rgb[1] - 24) + abs(rgb[2] - 41) < 30

            self.assertTrue(near_matte(top), top)
            self.assertGreater(middle[1], 200)
            self.assertLess(middle[0], 40)
            self.assertTrue(near_matte(bottom), bottom)


class SmokeTests(unittest.TestCase):
    def test_smoke_does_not_pass_without_noto(self):
        with tempfile.TemporaryDirectory(prefix="us3day-smoke-") as tmp:
            code = main(
                [
                    "smoke",
                    "--allow-reference-plate",
                    "--font-regular",
                    "inputs/fonts/missing-regular.ttc",
                    "--font-bold",
                    "inputs/fonts/missing-bold.ttc",
                    "--reference",
                    str(REFERENCE),
                    "--ass",
                    str(ASS),
                    "--cover",
                    str(COVER),
                    "--out",
                    tmp,
                ]
            )
            self.assertEqual(code, 3)
            report = json.loads((Path(tmp) / "smoke_report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "font_missing_not_accepted")
            self.assertFalse(report["qualified"])
            self.assertEqual(list(Path(tmp).glob("*.mp4")), [])
            present = resolve_noto(
                "inputs/fonts/NotoSansCJK-Regular.ttc",
                "inputs/fonts/NotoSansCJK-Bold.ttc",
            )
            self.assertTrue(present["ok"], present)


class LoudnessTests(unittest.TestCase):
    def test_linear_gain_keeps_ratio_and_peak_ceiling(self):
        from recovery_us3day.produce import linear_gain_db

        self.assertAlmostEqual(linear_gain_db(-32.4, -20.0, -16.0, -1.5), 16.4)
        self.assertAlmostEqual(linear_gain_db(-32.4, -8.0, -16.0, -1.5), 6.5)


class ProductionTests(unittest.TestCase):
    def test_unfilled_slots_write_no_film(self):
        project = build_project()
        project["fonts"]["regular"] = "inputs/fonts/missing-regular.ttc"
        project["fonts"]["bold"] = "inputs/fonts/missing-bold.ttc"
        catalog = load_catalog(CATALOG)
        with tempfile.TemporaryDirectory(prefix="us3day-produce-") as tmp:
            report = produce(project, catalog, Path(tmp))
            self.assertTrue(report["gaps"])
            self.assertFalse(report["reference_plate_used"])
            self.assertEqual(list(Path(tmp).glob("*.mp4")), [])
            slots = {item["slot"] for item in report["gaps"]}
            self.assertIn("fonts.noto", slots)
            self.assertIn("audio.vo", slots)
            self.assertIn("audio.bgm_plan", slots)
            self.assertIn("audio.sfx_events", slots)
            self.assertIn("s01.media", slots)
            self.assertIn("s12.component", slots)

    def test_filled_component_resolves_source_and_sync(self):
        catalog = load_catalog(CATALOG)
        with tempfile.TemporaryDirectory(prefix="us3day-component-") as tmp:
            folder = Path(tmp) / "count-up"
            folder.mkdir()
            (folder / "registry-item.json").write_text("{}", encoding="utf-8")
            (folder / "count-up.html").write_text("<!-- fixture -->", encoding="utf-8")
            shot = {
                "id": "s09",
                "t0": 52.99,
                "t1": 55.535,
                "component": {
                    "id": "hf_components:count-up",
                    "variables": {
                        "start": 0,
                        "end": 128,
                        "prefix": "",
                        "suffix": "%",
                        "accent": "green",
                        "glow": False,
                        "exit": "none",
                    },
                },
            }
            resolved = resolve_component(catalog, shot, {"hf_components": tmp})
            self.assertTrue(resolved["ok"], resolved)
            self.assertEqual(resolved["sync"][0]["id"], "count-land")
            self.assertAlmostEqual(resolved["sync"][0]["t"], 52.99 + 1.72, places=2)


if __name__ == "__main__":
    unittest.main()
