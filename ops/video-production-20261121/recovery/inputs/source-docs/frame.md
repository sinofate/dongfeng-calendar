---
version: 2026-11-02a
name: AI认知局 — Frame（正片字色 / Hyperframes）
description: >
  视频号「AI认知局」竖屏正片的品牌令牌。与封面 COVER_STANDARD / ai-renzhiju-cover
  同色同气质：深海军蓝底、白主字、唯一暖黄强调、品牌青辅色。禁止公文白底黑字说明卡。
  案卷开工时复制本文件为 cases/<slug>/frame.md；hyperframes 与分镜/成片审以此为真理。
unit: the frame — 1080×1920 (9:16) primary
principle: atoms are sacred · one accent per frame · cover and body share one palette
source: 东风 2026-11-02 否 A股「白底黑字+多黄同屏」观感；审稿核验官落盘

colors:
  bg: "#071829"                    # 深海军蓝气质底（封面同）
  bg-scrim: "rgba(7,24,41,0.72)"   # 字区压暗 / 半透明卡底
  bg-card: "rgba(7,24,41,0.82)"    # 说明卡 / 过门卡唯一合法底
  ink: "#FFFFFF"                   # 白主字、说明字
  ink-muted: "rgba(255,255,255,0.72)"
  accent: "#FFD247"                # 暖黄 · 全屏唯一强调色（封面黄核心同）
  brand: "#20C5E8"                 # 品牌青 · 标签/角标/附属小字
  stamp-deny: "#E63946"            # 仅否定章 / 删除线（非行情红）
  # 禁：纯白实心底 #FFFFFF 作说明卡；禁行情红绿作装饰

radii:
  card: "16px"
  pill: "100px"
  none: "0px"

typography:
  # 中文默认粗无衬线（系统/项目已装：Noto Sans SC / Source Han Sans SC / PingFang SC）
  # 英文可配 Space Grotesk；数字大字可用同族 700–900
  font-cjk: "Noto Sans SC"
  font-latin: "Space Grotesk"
  title-band:   { family: "font-cjk", px: 44, weight: 700, color: "accent", maxLines: 1 }
  impact-white: { family: "font-cjk", px: "150-190", weight: 800, color: "ink", maxChars: 6 }
  impact-yellow:{ family: "font-cjk", px: "≥220", weight: 900, color: "accent", maxChars: 5 }
  gate-card:    { family: "font-cjk", px: "120-160", weight: 800, color: "ink" }   # 过门「第一场/第二场」
  note-on-card: { family: "font-cjk", px: "36-48", weight: 600, color: "ink" }     # 说明句（在 bg-card 上）
  pill:         { family: "font-cjk", px: "≤44", weight: 600, color: "ink" }
  source-mark:  { family: "font-cjk", px: "≤40", weight: 500, color: "ink-muted" }
  subtitle:     { family: "font-cjk", px: "36-44", weight: 500, color: "accent" }  # 底栏字幕可黄，但勿与冲击黄同屏抢

spacing:
  safe-top: "0-250"          # 顶空；title_band 贴其上沿、整体偏上
  stage: "370-1470"
  subtitle-y: "1475-1550"
  source-xy: "x≈40-60 · y≈1380-1450"
  title-band-y: "墨迹优先 y≈120–280；贴顶上移；禁长期压主体；左缘 x0–120 角标净空（2026-11-05）"
  title-band-linegap: "行首距≥72；双行墨迹缝≥约20（标杆币安≈23）"

components:
  title-band:
    textColor: "{colors.accent}"
    maxLines: 1
    description: "正片顶栏金黄；禁副标题第二行进正片。2026-11-05：整体上移、不挡实景主体、不与左侧台标/角标叠字。"
  impact-card-dark:
    backgroundColor: "{colors.bg-card}"
    textColor: "{colors.ink}"
    rounded: "{radii.card}"
    description: "过门/名词/说明的唯一卡底。半透明深海军蓝 + 白字。禁纯黑实心、禁白底黑字。"
  impact-yellow-solo:
    textColor: "{colors.accent}"
    backgroundColor: "{colors.bg-card}"
    description: "全片高潮数字/金句；同屏主冲击黄 ≤1；勿与底栏黄字幕双黄抢。"
  note-pill:
    backgroundColor: "{colors.bg-scrim}"
    textColor: "{colors.ink}"
    border: "1px solid rgba(32,197,232,0.25)"
    rounded: "{radii.pill}"
    description: "「设立时 1.75%」「个人解读」等限定词。禁止白底黑字 pill。"
  source-corner:
    textColor: "{colors.ink-muted}"
    position: "bottom-left only"
    description: "来源仅左下极小角标；禁中置抢视线。"
  deny-stamp:
    color: "{colors.stamp-deny}"
    description: "否定章/删除线专用；不作行情涨跌色。"
  evidence-crop:
    description: "真新闻页/公告截图可保留原稿白底黑字（一手证据不可改排）。只裁正文；黄框高亮关键句。"
---

# Overview

AI认知局正片要和封面是同一套脸：深、克制、一个黄点砸中。手机竖屏上，字靠对比度和字号分层，不靠「白便签贴在阴天外滩上」。

触发（2026-11-02）：A股两场会成片里，顶栏金黄 + 大黄数字 + 白底黑字说明卡 + 黄字幕同屏，观感怪；已发不返工，自下一条新片起强制。

# Colors

| Token | Hex / value | 用法 |
|---|---|---|
| bg | `#071829` | 气质底；字区压暗 |
| bg-card / bg-scrim | 半透明同色 | **唯一**合法说明卡/过门卡底 |
| ink | `#FFFFFF` | 白冲击、说明字 |
| accent | `#FFD247` | 顶栏 / 高潮黄 / 真页高亮框；**同屏≤1 个主黄冲击** |
| brand | `#20C5E8` | 标签、附属小字、轻描边 |
| stamp-deny | `#E63946` | 仅「不是」类否定 |

**禁止**

1. **白底黑字说明卡 / pill**（`#FFFFFF` 实心底 + 黑字）——可读但公文感，与品牌拧。
2. 纯黑 `#000000` 实心大牌作过门（可用 `bg-card` 半透明代替）。
3. 行情红绿、上扬箭头、涨跌配色当装饰。
4. 同屏两个及以上暖黄大字抢视线（含黄辅文 vs 底栏黄字幕）。

**例外**：一手证据截图（新闻/公告/实录）保留原白底黑字版面，只裁切+黄框，不重排成品牌卡。

# Typography

- 中文：粗无衬线（Noto Sans SC / 思源黑体 / 苹方），平面字，允许轻微阴影，禁金属立体字与夸张光晕。
- 白冲击 ≤6 字，约 150–190px；黄冲击 ≤5 字，≥220px，且须大于同屏白字。
- 层级用字号与 opacity，不靠再加第三种高饱和色。

# Composition Rules（正片）

1. **一镜一意**：同屏主冲击 ≤1。
2. **单黄**：主冲击黄与底栏黄字幕不要双黄抢；说明句用白字上 `bg-card`。
3. **数字+限定词**：主数字用黄砸；「设立时 / 年利率…」用 `note-pill`（深半透+白字），**不要**白底黑字第二块。
4. **过门卡**（「第一场」「第二场」）：`impact-card-dark` + 白字，勿纯黑实心底。
5. **底图**：须有实景/真页/生图底；禁干海军蓝空场只靠字。底图缓推幅度宜小（建议 ≤1.02），避免晃晕。
6. **安全区**：主字 y420–1250；来源左下；字幕底栏。

# Do's and Don'ts

**Do**

- 案卷根目录放 `frame.md`（本文件副本）；hyperframes / Opus 写镜前先读 frontmatter。
- 分镜 HARD_LAYOUT 写明：卡底=`bg-card`，说明禁白底。
- 成片审抽帧：若见白底黑字说明卡 → 观感 FAIL（自 2026-11-02 新片）。

**Don't**

- 不要从外站 skill 整包替换本品牌色（可借鉴 FRAME 结构，色值以本文件为准）。
- 不要为「好读」临时发明第三套卡片材质。
- 已发成片不追溯返工。

# Adoption

```bash
# 新案卷
cp /workspace/pub/video-clone/knowledge/brand/ai-renzhiju-frame.md \
   /workspace/pub/video-clone/cases/<slug>/frame.md
```

审稿：分镜审 / 成片审对照本文件 + HARD_GATE；HANDBOOK 补丁 **2026-11-02a**。
剪辑 / 制作：写分镜与渲 hyperframes 前必读案卷 `frame.md`。

---

## 补丁 2026-11-04 晚 · 禁乱码卡底 / 蓝线默认关

- 说明卡文字必须走本 frame 的 CJK 字层；**禁止**预烙中文到 `card_*.png` 再当满屏底。
- 标题带下**短蓝线 / 长装饰蓝线默认关闭**；强调靠字号与 `#FFD247`，不靠贴字线。
- 依据：币安假面试乱码诊断；详见 `TASTE_RECOVERY_2026-11-04.md`。
