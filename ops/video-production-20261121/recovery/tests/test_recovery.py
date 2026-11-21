import tempfile
import unittest
from pathlib import Path

from recovery_us3day.assparse import parse_ass
from recovery_us3day.catalog import counts, load_catalog, lookup_name, validate_binding
from recovery_us3day.compose import build_smoke_ass, render_window, yellow_in_band
from recovery_us3day.layout import RECONSTRUCTION, measure_extract, observation_matches_frozen, reference_crop, scaled_box
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
        self.assertIsNone(project["subtitles"]["revised_lr"])
        self.assertEqual(project["subtitles"]["historical_lr"], 30)
        self.assertIsNone(project["layout"]["yellow_rule"])
        self.assertFalse(project["output"]["source_corner_labels"])
        self.assertIsNone(project["shots"][0]["asset"])
        self.assertIsNone(project["shots"][0]["component_id"])
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
        scaled = {
            "yellow_title": scaled_box(title["yellow_title"]),
            "white_top": scaled_box(title["white_top"]),
        }
        self.assertEqual(observation_matches_frozen(scaled, tolerance=2), [])
        subtitle = measure_extract(str(FRAME_04))["yellow_subtitle"]
        scaled_sub = scaled_box(subtitle)
        want = {
            "x0": 256,
            "y0": 1492,
            "x1": 824,
            "y1": 1536,
        }
        for edge, value in want.items():
            self.assertAlmostEqual(scaled_sub[edge], value, delta=2)
        crop = reference_crop()
        stage = RECONSTRUCTION["main_rect"]
        self.assertEqual(crop["y"] * 3, stage["y"])
        self.assertEqual((crop["y"] + crop["h"]) * 3, stage["y"] + stage["h"])
        self.assertLess(282, stage["y"])
        self.assertGreater(1492, stage["y"] + stage["h"])


class SmokeTests(unittest.TestCase):
    def test_short_composites_are_not_the_reference(self):
        with tempfile.TemporaryDirectory(prefix="us3day-smoke-") as tmp:
            out = Path(tmp)
            opening = render_window(
                reference=REFERENCE,
                ass_path=ASS,
                output=out / "opening.mp4",
                start=0.0,
                end=4.0,
                cover=COVER,
                cover_until=1.5,
                protected_dirs=[ROOT / "inputs"],
            )
            comment = render_window(
                reference=REFERENCE,
                ass_path=ASS,
                output=out / "s12.mp4",
                start=65.9,
                end=67.0,
                protected_dirs=[ROOT / "inputs"],
            )
            self.assertFalse(opening["recovered_master"])
            self.assertNotEqual(opening["sha256"], opening["reference_sha256"])
            self.assertNotEqual(comment["sha256"], comment["reference_sha256"])
            self.assertEqual(opening["width"], 1080)
            self.assertEqual(opening["height"], 1920)
            self.assertAlmostEqual(opening["video_duration"], 4.0, delta=0.08)
            self.assertAlmostEqual(opening["audio_duration"], opening["video_duration"], delta=0.08)
            from recovery_us3day.compose import extract_frame

            extract_frame(out / "opening.mp4", 2.5, out / "t2.5.jpg")
            extract_frame(out / "s12.mp4", 0.5, out / "t66.4.jpg")
            title = RECONSTRUCTION["title_band"]
            subtitle = RECONSTRUCTION["subtitle_band"]
            self.assertGreater(yellow_in_band(out / "t2.5.jpg", title["y"], title["y"] + title["h"]), 200)
            self.assertGreater(yellow_in_band(out / "t2.5.jpg", subtitle["y"], subtitle["y"] + subtitle["h"]), 200)
            # t=2.5 must be the plate, not the cover still filling the stage.
            from recovery_us3day.pixels import load_rgb

            width, height, raw = load_rgb(out / "t2.5.jpg")
            stage = RECONSTRUCTION["main_rect"]
            red = 0
            for y in range(stage["y"] + 40, stage["y"] + stage["h"] - 40, 4):
                row = y * width * 3
                for x in range(40, width - 40, 4):
                    offset = row + x * 3
                    if raw[offset] > 150 and raw[offset + 1] < 80 and raw[offset + 2] < 90:
                        red += 1
            self.assertLess(red, 80)
            self.assertGreater(yellow_in_band(out / "t66.4.jpg", title["y"], title["y"] + title["h"]), 200)
            self.assertLess(yellow_in_band(out / "t66.4.jpg", subtitle["y"], subtitle["y"] + subtitle["h"]), 30)
            ass_text = (out / "s12.ass").read_text(encoding="utf-8")
            self.assertNotIn("大约三成", ass_text)


if __name__ == "__main__":
    unittest.main()
