# 半导体见底了吗 · 竖版恢复工程

这是 `2026-11-07-us-3day-market-correct` 的配置驱动竖版合成入口。母本的 HyperFrames 镜头源（`build/hf`、`title_band.png`、原切片、`vo_raw.wav`）不在证据包里，仓库历史里也没有 `engine-claude-seed` 工程。这里按母带抽帧、ASS、timeline 和低码率参考片重建合成壳，不拿 echo starter 或 385712 横版模板冒充。

短 smoke 会真实编码。它使用封面成图，以及 360×640 参考片裁进主窗口后的画面。参考片是旧母带降码，不是重渲，也不能当成恢复成功的成片。

本次云端编程没有发起 Claude / e7y / Suno 调用。`inputs/e7y/` 里的 22 镜建议是本机 2026-11-21 13:01:56 HKT 那一次返回，stdout 8296 字节、stderr 空、exit 0。模型字段 `claude-opus-5-5` 只是 e7y/CLI 自报。那次返回没有完整代码，示例 JSON 只有 s01。本目录的配置和代码是实现方补上的。

## 命令

在本目录执行：

```sh
python3 -m recovery_us3day validate
python3 -m recovery_us3day gaps --md --out GAPS.md
python3 -m recovery_us3day smoke \
  --reference inputs/reference/master_full_lowbitrate_REFERENCE_NOT_RERENDER.mp4 \
  --ass inputs/source-docs/final_v1.ass \
  --cover inputs/reference/cover_1080x1920.jpg \
  --allow-reference-plate \
  --out out/smoke
python3 -m unittest tests/test_recovery.py
```

本机若改用全分辨率母带或真正的分镜素材，仍用同一条 `smoke`，把 `--reference` 指到母带。`smoke` 不是验收。没有 Noto 文件时退出码 3，不编码，也不改用文泉驿。字体在时可以写出诊断片，退出码仍是 2：参考片里的旧字和来源行没有被证明清除。生产填槽用 `produce`，缺媒体、口播、BGM 计划、音效事件或组件源码时只写缺口，不产 mp4。

```sh
python3 -m recovery_us3day produce --out out/produce
```

`out/smoke/reference_extract_t15_NOT_A_RENDER.jpg` 是参考片抽帧，旁边的 json 写明它不是渲染结果。

## 参数怎么分层

- 提取：1080×1920 / 30fps / 150.566667 秒；timeline 的 t0/t1 与 150.564 秒；ASS 的 76 号字、`#FFD700`、黑描边 5、MarginL/R 30、MarginV 370；81 条 Dialogue；1 条 Comment「大约三成」。
- 文书：页头 y130/y220、title_band y150–290、frame.md 的 44px 与 `#FFD247`、后续 MarginL/R 80–100 这个范围、分镜表上 159.3 秒的计划时钟。这些不写成唯一原坐标。
- 观察，分两套坐标。540×960 抽帧上：黄页头约 y76–104，白页头约 y119–142，字幕亮核约 y745–768。乘 2 后的 1080×1920 才是 y152–208、y238–284、y1490–1536。后一组不能当成 540 图上的 y。
- 重建：主窗口在 1080×1920 上是 y312–1440。参考片按输入真实宽高换算裁切。1080×1920 母带裁 y312/h1128；360×640 才是 y104/h376。历史 MarginL/R 仍是 30。后续终交实参是 90，证据 md5 `4887b2bebd4e502ee44f53c0ae132316`。

镜头落点只用 t0/t1。逐镜 `frames` 合计 4516，除以 30 是 150.5333 秒，不能拿来累加，否则从 s02 就开始漂。

## 组件

`inputs/asset_catalog.json` 是盘点索引，777 条。选择器只接受索引里真实的 id，并按每条 variables 的 type/enum/min/max 校验。数量由文件现算。`echo_example:*` 和 shotcraft 参考卡不能当成这个母本的可插入组件。385712 横版引擎会被拒绝。22 镜的 `component.id` 仍是未填，不是已选。填上 id 之后，`produce` 会按目录名找 `registry-item.json` 和 snippet，并把 catalog 的 sync offset 加到该镜 t0 上。分镜里的 Kinetic / NumberTicker 名字不当成绑定。

## 还要本机补的文件

- 各镜干净画面，不是烧了字幕和来源的 `final_v1.mp4`。原母带可以做尺寸对照，不能当生产画面槽。
- `audio/vo_raw.wav`，以及 BGM 计划、音效事件里写明的音频文件。
- `/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc` 与 `NotoSansCJK-Bold.ttc`。本机已有。这台云端没有，所以这里不能出字体验收。
- 选定组件之后，该组件目录下的源码。不要在 id 未填时把整个动效库搬进来。
