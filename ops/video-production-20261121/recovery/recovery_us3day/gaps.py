"""Source and gap table. Generated from the files this package actually reads."""

from __future__ import annotations

from .assparse import parse_ass
from .layout import OBSERVED_INK, RECONSTRUCTION
from .project import DEFAULT_ASS, DEFAULT_TIMELINE, build_project
from .suggestions import E7Y_CALL
from .timeline import accumulated_frame_clock, frame_sum, load_timeline, validate_timeline


def build_report() -> dict:
    timeline = load_timeline(DEFAULT_TIMELINE)
    clock = validate_timeline(timeline)
    drift = accumulated_frame_clock(timeline)
    ass = parse_ass(DEFAULT_ASS)
    project = build_project()
    missing_assets = [shot["id"] for shot in project["shots"] if not shot.get("media")]
    return {
        "case": project["case"],
        "recovered_master": False,
        "e7y": E7Y_CALL,
        "layers": {
            "extracted": [
                "1080×1920, 30 fps, h264+aac, video 150.566667s, 4517 frames, master ffprobe",
                "timeline t0/t1, 22 shots, total 150.564s, impact_at s20.hero_land",
                f"ASS Style D Noto Sans CJK SC {ass.style.fontsize} Bold, fill {ass.style.primary}, outline {ass.style.outline_color} width {ass.style.outline}, shadow {ass.style.shadow}, alignment {ass.style.alignment}, MarginL/R {ass.style.margin_l}, MarginV {ass.style.margin_v}",
                f"{len(ass.dialogues)} Dialogue rows, {len(ass.comments)} Comment row: {[event.text for event in ass.comments]}",
                "cover_1080x1920.jpg md5 9c0b12b037e3246788399deae202ccfc",
            ],
            "documented": [
                "frame.md title-band 44px and accent #FFD247; not the ASS 76px / #FFD700",
                "SUBMIT L1 y130 / L2 y220 / ink gap 26; WARROOM title_band y150–290",
                "storyboard clock is the 159.3s plan (S01 0–8.00 … S22 153.40–159.30), not timeline.json",
                "later MarginL/R range 80–100, no single approved value",
                "opening 0–1.5s cover, about 3% push, hard cut; ease curve was not in the pack",
                "BGM plan pb569428 / pb622408 / pb623319 / pb628035 does not share the final 150.564s clock",
            ],
            "observed_on_frames": OBSERVED_INK,
            "reconstructed": RECONSTRUCTION,
        },
        "clock": {
            "placement": "timeline t0/t1 seconds",
            "frame_sum": frame_sum(timeline),
            "frame_sum_seconds": clock["frame_sum_seconds"],
            "timeline_total": timeline.total,
            "frame_quantization_gap_seconds": clock["frame_quantization_gap_seconds"],
            "media_duration": 150.566667,
            "tail_after_timeline_seconds": 150.566667 - timeline.total,
            "s02_frame_accumulation_delta": drift[1]["delta_seconds"],
            "frame_accumulation_used_for_placement": False,
        },
        "subtitles": {
            "historical_lr": 30,
            "historical_space": "us-3day final_v1.ass Style D",
            "later_revision_lr": 90,
            "later_revision_evidence": "revenue-race final_v4.ass line 10, md5 4887b2bebd4e502ee44f53c0ae132316, delivered 2026-11-11 15:11 HKT",
            "comment_excluded": "大约三成",
        },
        "missing_before_a_recovered_master": [
            "原母带 final/final_v1.mp4（84,893,878 字节）。只有要全分辨率底板时才需要；当前 smoke 用的是 360×640 参考片。",
            "分镜列出的各镜原切片（CNBC、QuantData 等）。参考片裁切不能代替这些切片。",
            "audio/vo_raw.wav 和未混人声。smoke 只裁了参考片里已经混好的声音。",
            "build/hf 镜头 HTML/JS，以及 build/hf/assets/title_band.png。",
            "本机 Noto 文件：/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc 与 NotoSansCJK-Bold.ttc（SC 面 index 2）。这台云端环境没有这两份文件，不能用文泉驿顶上再写验收通过。",
            "封面轻推的原始缓动曲线。smoke 用的是匀速，并标成重建。",
            "plan.json 与 sfx_events.json 不在这包证据里。",
            f"22 镜 media 与 component.id 仍未填：{', '.join(missing_assets)}。参考片 smoke 不能代替这些槽。",
        ],
        "present_for_smoke": [
            "inputs/source-docs/final_v1.ass",
            "inputs/source-docs/timeline.json",
            "inputs/reference/cover_1080x1920.jpg",
            "inputs/reference/master_full_lowbitrate_REFERENCE_NOT_RERENDER.mp4",
            "inputs/reference/frame_01.jpg … frame_05.jpg",
            "inputs/asset_catalog.json",
            "inputs/e7y/claude_raw_response.json",
        ],
        "not_done": [
            "150 秒全片重渲",
            "把参考片裁切说成新画面",
            "抹掉封面 JPEG 和参考片画面里已经烧进去的来源行。合成器自己不写来源角标。",
            "安装或调用 hyperframes 0.8.181。镜头 HTML 不在。",
            "这次云端编程没有新的 Claude / e7y / Suno 调用",
            "三审或打分门",
        ],
    }


def render_markdown(report: dict) -> str:
    clock = report["clock"]
    lines = [
        "# 来源与缺口",
        "",
        "这是竖版恢复工程的缺口表。短 smoke 不是找回的母本。",
        "",
        "## 时钟",
        "",
        f"- 镜头落点用 timeline 的 t0/t1。s02 若改用累计帧会差 {clock['s02_frame_accumulation_delta']:.6f} 秒。",
        f"- 帧字段合计 {clock['frame_sum']}，除以 30 是 {clock['frame_sum_seconds']:.6f} 秒。",
        f"- timeline 合计 {clock['timeline_total']} 秒。量化差 {clock['frame_quantization_gap_seconds']:.6f} 秒。",
        f"- 母带视频 150.566667 秒，比 timeline 多出 {clock['tail_after_timeline_seconds']:.6f} 秒。这段尾巴不靠累计帧裁掉。",
        "",
        "## 字幕边距",
        "",
        "- 母本提取值：MarginL/R = 30，MarginV = 370。这是 us-3day 的 final_v1.ass，不改写成 90。",
        "- 后续实参：MarginL/R = 90。证据是 revenue-race `final_v4.ass` 第 10 行，md5 `4887b2bebd4e502ee44f53c0ae132316`，2026-11-11 15:06 HKT 案卷记下这个 md5，15:11 HKT 终交。新烧录用 90。80–100 只是当时的范围，不是这次取值的来源。",
        "",
        "## 版心",
        "",
        "- 抽帧文件是 540×960。黄页头在这张图上大约 y76–104，白页头 y119–142，字幕亮核 y745–768。",
        "- 乘 2 才是 1080×1920：字幕亮核 y1490–1536。这个数不能写回 540 高的图上。",
        "- 主窗口重建矩形在 1080×1920 上是 y312–1440。合成先把整帧归一化到 1080×1920，再取这个窗口，上下用色带接上。1080p 母带不再套 360p 的 y104/h376。",
        "- 2026-11-21 本机观看原母带 smoke：0–1.5 秒封面正常；1.5–4.1 秒主窗被极度放大，白信息卡右侧截断，右上有旧黄标题残笔。原底部字幕被裁出窗口，所以没有看到第二条黄字幕，不能写成重复字幕。当时背景铺满全屏，新标题和字幕叠在画面里，没有分开的上下区域。新字笔画清楚，标题太小。那次 exit 0 不是合格。",
        "- 烧了字的母带只能检查窗口几何。它不能证明干净切片的生产观感，也不能证明来源行或旧字已经被清除。",
        "- 文书 y130/y220 与 title_band y150–290 仍是另一层记载。",
        "",
        "## 还缺的本机文件",
        "",
    ]
    for item in report["missing_before_a_recovered_master"]:
        lines.append(f"- {item}")
    lines.extend(["", "## 这次 smoke 用得到的", ""])
    for item in report["present_for_smoke"]:
        lines.append(f"- {item}")
    lines.extend(["", "## 明确没做", ""])
    for item in report["not_done"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)
