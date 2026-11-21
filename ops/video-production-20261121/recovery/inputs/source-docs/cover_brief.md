# 封面简报｜2026-11-07-us-3day-market-correct｜LOCK_DRAFT v1
更新：2026-11-07 04:42 HKT｜封面设计师执行手

## 输入（只排不写）
- 三行定稿：`rewrite-v3/cover_three_lines.md` md5 `b9f27775f80666a07e9ed2b327927405`
- 口播：`rewrite-v3/script-final.md` md5 `ec16a2c2889d6272eb505b0ace81bd11`
- L1 白：选举结果出来那天美股先涨
- L2 黄：芯片砸掉三成
- L3 白：见底了吗？科技股在重定价（叠字断两行）
- why_click：戳破「选举一宣布就崩」；一眼看到结果日先涨 vs 芯片砸三成；点进听见底/抄底多空边界

## 三硬逻辑：过
1. 点因：结果日先涨 vs 砸三成反差 → 想点进来听见底判断
2. 核心：时间纠偏 + SOX约三成 + 见底/重定价
3. 黄字钉子：「芯片砸掉三成」（「三成」）= 全图唯一黄最大

## 映射（未改写主句）
| 层 | 承载 | 字号/gap/scale_x |
|---|---|---|
| 品牌 | AI认知局（青+白）y160 | 52 |
| L1 白 | 选举结果出来那天美股先涨 | 95 / gap0 / sx0.7832 / w896 slack32 |
| L2 黄 | 芯片砸掉三成 | 220 / gap0 / sx0.7025 / w928 |
| L3 白 | 见底了吗？｜科技股在重定价 | 91+87 / gap0 / sx1.0 |

字距硬规：L1/L2/L3 全 gap≥0；L1 留 slack 未与 L2 同宽硬撑；L2 scale_x=0.7025≥0.70（6字无法同时≥240且≥0.70，取≥220保 scale）；安全区 y420–1250 过。

## 通读自检
链：先涨 → 砸三成 → 见底?／重定价。禁读成「选举结果出来那天芯片砸掉三成」漏先涨——叠字保留「先涨」词；L3 断行后「见底了吗？」独立成问。

## 盲测（e7y gpt-6-astra vision）
- 结果：PASS（overall / transcribe / hard3 / yellow / chain）
- 复述：能抄出三行+品牌；黄字=芯片砸掉三成且最大；点因=先涨vs砸三成反差+见底悬念；主视觉=破裂晶圆红蓝张力
- 备注：模型提示快速扫图时巨大黄字可能抢走注意力、有漏读先涨风险；但逐字抄录与通读链均正确保留先涨。属长 L1 vs 大黄字固有张力，非定稿问题。
- 证据：`build/cover/blind_v1.json`

## 底图
- e7y `gpt-image-2.5-flare` 1024×1536 medium ≈$0.4
- 气质：碎裂晶圆 + 暗红下跌张力 + 冷蓝希望残留；上半留空；无字/台标/二维码/金币/火箭
- `media/bg_cover.jpg` md5 `bd0b8b7ff167d2b3192691644691fe5a`

## 花费
- 生图 ≈ $0.40
- 盲测 ≈ $0.03
- 合计 ≈ **$0.43**（未堆 Ultra）

## 产物路径 / md5
| 文件 | md5 |
|---|---|
| cover_1080x1920.jpg / cover.jpg / build/cover/cover_9x16_v1.jpg | `9c0b12b037e3246788399deae202ccfc` |
| cover_3x4.jpg / cover_3x4_1080x1440.jpg / build/cover/cover_3x4_v1.jpg | `d39ac785b84faa9ae5b47e89ca3c19f1` |
| cover_grid_150x200.jpg / build/cover/cover_grid_150x200_v1.jpg | `868cc8c81b2fc5b85c76e69bcd84975b` |
| media/bg_cover.jpg | `bd0b8b7ff167d2b3192691644691fe5a` |
| rewrite-v3/cover_three_lines.md | `b9f27775f80666a07e9ed2b327927405` |
| sizes：`build/cover/sizes_v1.json` | — |

## 状态
**LOCK_DRAFT v1** — 交审②合闸；制作禁抢跑；禁 Drive；视频号 HOLD。未自称终锁。
