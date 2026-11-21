# SUBMIT · final_v1 · 交审③

- **案卷**：`2026-11-07-us-3day-market-correct`（美股三日修正·选举日先涨/芯片砸三成）
- **片型**：浅度 · 股票类 · ≈150.6s
- **交棒时间**：2026-11-07 05:49 Asia/Hong_Kong
- **交棒人**：视频制作工程师 → 审稿核验官（审③）
- **父代理交棒**：本岗**未** SendToAgent；**未** Drive/UploadFile

## 成片

| 项 | 值 |
|---|---|
| 路径 | `/workspace/pub/video-clone/cases/2026-11-07-us-3day-market-correct/final/final_v1.mp4` |
| md5 | `f4060b93c55210a0a0a9814b6adea01c` |
| 时长 | **150.567s**（v=150.567 / a=150.564；DURATION_GATE PASS vs mix +0.003s） |
| 字幕 | `final/final_v1.ass`（已藏 SUB_DUP「大约三成」1 条） |
| Drive | **未生成 / 未上传**（交审③前禁；nodrive mux；无 `_drive.mp4`） |
| 视频号 / X / 微信 | **HOLD** |

## Gate0 锁版 md5（开渲前自核合）

| 文件 | md5 |
|---|---|
| rewrite-v3/script-final.md | `ec16a2c2889d6272eb505b0ace81bd11` |
| rewrite-v3/cover_three_lines.md | `b9f27775f80666a07e9ed2b327927405`（根目录旧 `2a11afff…` 未用） |
| COVER_LOCKED 9:16 / cover.jpg | `9c0b12b037e3246788399deae202ccfc` |
| cover_3x4 | `d39ac785b84faa9ae5b47e89ca3c19f1` |
| cover_grid | `868cc8c81b2fc5b85c76e69bcd84975b` |
| storyboard.md | `f06a87f7c3f4ccb462918bcfadf22337` |
| plan.json | `2ed8c49e9ca5657bedbe79bd80aa19f4` |
| sfx_events.json | `0a47d973569b95897a60ccf93c5212f8` |
| materials.md | `63ce95c240ca22c25314bc9b7c993999` |
| S01/S03 clip `x_magic_cnbc_wed_rally_screen` | `0c88632772919adb8e1d9546a97e34dd`（trim 0–5 / 5–9，**禁≥10**） |
| S12 `x_quantdata_spx_2t_wipe_9s` | `2deac0a9fba8ddcafac1fea433685bb0` |
| S14 `x_etftrad_fri_premarket_qqq_54s` | `cafec356f77509c757d28b93aeea4bc2` |

## 硬注意自检

| # | 要求 | 落地 | 证据 |
|---|---|---|---|
| 1 | S01 0–1.5s COVER_LOCKED + 轻推；其后 CNBC；禁 overrun t≥10 | ✅ cover→s01_cnbc(0–5)；s03_cnbc(5–9) | `build/final_v1_frames/t0.8.jpg`（封面）· `t2.0.jpg`/`t4.0.jpg`（绿盘）· trim aliases |
| 2 | S12 QuantData + 黄「约三成」 | ✅ y220「约三成」+ BGPunch；字幕藏重复「大约三成」 | `t63.5.jpg`/`t66.0.jpg` · ASS Comment |
| 3 | S14 半透明遮罩盖源片%；HF 仅盘中反抽/还没收盘 | ✅ 三块 pctmask；pillc 两枚；无收盘% | `t75.0.jpg`/`t77.0.jpg` |
| 4 | title_band 上移 y≈120–280；左缘净空；行距 | ✅ L1黄 y130 / L2白 y220；缝26；居中 | `build/hf/assets/title_band.png` md5 `0f0cea7d…` · `*_titlezone.jpg` |
| 5 | 语速 1.1；P1 录音室干声 | ✅ tts_zh_standard speed=1.1 + vo_p1.sh chains.txt 第1行 | `build/tts.log` · `build/vo_p1.log` |
| 6 | 交审③前禁 Drive；视频号 HOLD | ✅ nodrive；无 UploadFile | 本文件 |
| 7 | Thin：片内 e7y；禁 Ultra 长循环 | ✅ `ask.sh video` ×1（S12 精修） | `build/opus/opus_calls.jsonl` |
| 8 | grain 关；禁 AI 水印字样 | ✅ poster-grain opacity:0；无「示意图/AI生成」 | starter CSS |

## 音频四闸（审③预检）

| 闸 | 数值 | 结果 |
|---|---|---|
| BGM vs VO 互相关 | **0.010** ≤0.3 | PASS（mix_stem_gate） |
| mix_pre 峰值 | **-1.34 dBFS** ≤0 | PASS |
| 人声优势 vo_dominance | win3s_min=**15.8** dB ≥15；speech_masked=**23.8** | PASS · `build/review_final_v1_audio/vo_dominance_gate.json` |
| 成片响度 | **I=−14.0 LUFS** / True peak **−2.4 dBTP** / LRA≈2.3 | PASS · `build/qa_final_v1_ebur.txt` |

BGM：pb569428→pb622408→pb623319→pb628035；gap_lu=**24**；`final/bgmtool_fullmix.wav.report.json` speech_gap≈23.9 LU。

## 其他自检

| 项 | 结果 |
|---|---|
| 真视频占比 | **46.9%**（70.58s / 150.56s）∈20–50% |
| phone_check | **PASS** 0/22（`LAYOUT_CHECK_final_v1_phone.md`） |
| LAYOUT / HARD_GATE | PASS（全 22 镜） |
| blackdetect d=0.4 | **PASS**（无 hit） |
| liang_er 两/二 | **PASS** |
| impact SFX | 仅 S20；0–3s 无炸 |
| card_* / 蓝线 / grain | 无 |

## Opus

| 项 | 值 |
|---|---|
| 次数 | **1**（e7y `ask.sh video` / claude-opus-5-5） |
| 用途 | S12「约三成」BGPunch / expo 精修建议 |
| 花费 | e7y 路由；单次短答（未走 OpenRouter 计费单）；DELIVERY 记 1 次 |
| 记录 | `build/opus/opus_calls.jsonl` · `build/opus/s12_refine.md` |

## 禁

- **交审③前禁 Drive**（未出 `_drive.mp4`；未 UploadFile）
- **视频号 HOLD** 等审③ + 东风「发」
- 勿用根目录 `cover_three_lines.md`=`2a11afff…`
- S01/S03 源片勿取 t≥10（人设讲话段）

## 证据路径摘要

- 成片：`final/final_v1.mp4`
- 审③音频：`build/review_final_v1_audio/vo_dominance_gate.json`
- 手机检：`LAYOUT_CHECK_final_v1_phone.md` · `build/final_v1_phone_check/`
- 硬注意抽帧：`build/final_v1_frames/`
- 版面：`LAYOUT_CHECK.md` · `LAYOUT_CHECK.summary.json`
