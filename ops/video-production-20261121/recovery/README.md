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

本机若改用全分辨率母带或真正的分镜素材，仍用同一条 `smoke`，把 `--reference` 指到母带。没有素材且不传 `--allow-reference-plate` 时，命令退出码 2，只写缺口，不产出 mp4。

`out/smoke/reference_extract_t15_NOT_A_RENDER.jpg` 是参考片抽帧，旁边的 json 写明它不是渲染结果。

## 参数怎么分层

- 提取：1080×1920 / 30fps / 150.566667 秒；timeline 的 t0/t1 与 150.564 秒；ASS 的 76 号字、`#FFD700`、黑描边 5、MarginL/R 30、MarginV 370；81 条 Dialogue；1 条 Comment「大约三成」。
- 文书：页头 y130/y220、title_band y150–290、frame.md 的 44px 与 `#FFD247`、后续 MarginL/R 80–100 这个范围、分镜表上 159.3 秒的计划时钟。这些不写成唯一原坐标。
- 观察：540×960 抽帧上的页头两行和字幕亮核。见 `recovery_us3day/layout.py` 的 `OBSERVED_INK`。
- 重建：主窗口 `y=312..1440`、上标题带、下字幕带、封面 3% 匀速轻推。矩形为了包住 em 和 5px 黑边，并且对齐 360p 参考片的 3 倍像素格。不是源码参数。`revised_lr` 保持 null。

镜头落点只用 t0/t1。逐镜 `frames` 合计 4516，除以 30 是 150.5333 秒，不能拿来累加，否则从 s02 就开始漂。

## 组件

`inputs/asset_catalog.json` 是盘点索引，777 条。选择器只接受索引里真实的 id，并按每条 variables 的 type/enum/min/max 校验。数量由文件现算。`echo_example:*` 和 shotcraft 参考卡不能当成这个母本的可插入组件。385712 横版引擎会被拒绝。22 镜的 `component_id` 全部是 null：建议表没有给出可校验的组件绑定，分镜里的 Kinetic / NumberTicker 名字也不当绑定。

## 还要本机补的文件

- 原母带 `final/final_v1.mp4`（84,893,878 字节），只有需要全分辨率底板时才用。
- 各镜原切片，以及 `audio/vo_raw.wav`。
- `build/hf/` 和 `title_band.png`，如果还找得到源工程。
- `Noto Sans CJK SC` 字体文件。这台环境没有，smoke 改用已安装的文泉驿微米黑，并在配置里标明。
- 若要把左右边距从历史 30 改到 80–100，需要一个已经核定的单一数值。现在没有，所以不代选。
