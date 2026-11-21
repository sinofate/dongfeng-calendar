# 来源与缺口

这是竖版恢复工程的缺口表。短 smoke 不是找回的母本。

## 时钟

- 镜头落点用 timeline 的 t0/t1。s02 若改用累计帧会差 -0.012667 秒。
- 帧字段合计 4516，除以 30 是 150.533333 秒。
- timeline 合计 150.564 秒。量化差 0.030667 秒。
- 母带视频 150.566667 秒，比 timeline 多出 0.002667 秒。这段尾巴不靠累计帧裁掉。

## 字幕边距

- 提取值：MarginL/R = 30，MarginV = 370。
- 文书里的后续范围：80–100。没有单一核定值，`revised_lr` 保持 null。
- smoke 沿用提取到的 30，只为把字放进已标重建的下沿字幕带。这不是把 30 改写成修正版。

## 版心

- 页头、主窗口、字幕带的矩形是重建值，来自 540×960 抽帧墨迹再加 em/描边余量，并对齐 360p 参考片的 3 倍像素格。
- 文书 y130/y220 与 title_band y150–290 仍并列保留，没有合成成一个“原坐标”。
- 黄线不画。正片合成不写来源角标。

## 还缺的本机文件

- 原母带 final/final_v1.mp4（84,893,878 字节）。只有要全分辨率底板时才需要；当前 smoke 用的是 360×640 参考片。
- 分镜列出的各镜原切片（CNBC、QuantData 等）。参考片裁切不能代替这些切片。
- audio/vo_raw.wav 和未混人声。smoke 只裁了参考片里已经混好的声音。
- build/hf 镜头 HTML/JS，以及 build/hf/assets/title_band.png。
- Noto Sans CJK SC 字体文件。本环境没有，smoke 改用文泉驿微米黑。
- 80–100 这个范围内已经核定的单一 MarginL/R。现在 revised_lr 仍是 null。
- 封面轻推的原始缓动曲线。smoke 用的是匀速，并标成重建。
- plan.json 与 sfx_events.json 不在这包证据里。
- 22 镜 asset 仍全是 null：s01, s02, s03, s04, s05, s06, s07, s08, s09, s10, s11, s12, s13, s14, s15, s16, s17, s18, s19, s20, s21, s22

## 这次 smoke 用得到的

- inputs/source-docs/final_v1.ass
- inputs/source-docs/timeline.json
- inputs/reference/cover_1080x1920.jpg
- inputs/reference/master_full_lowbitrate_REFERENCE_NOT_RERENDER.mp4
- inputs/reference/frame_01.jpg … frame_05.jpg
- inputs/asset_catalog.json
- inputs/e7y/claude_raw_response.json

## 明确没做

- 150 秒全片重渲
- 把参考片裁切说成新画面
- 抹掉封面 JPEG 和参考片画面里已经烧进去的来源行。合成器自己不写来源角标。
- 安装或调用 hyperframes 0.8.181。镜头 HTML 不在。
- 这次云端编程没有新的 Claude / e7y / Suno 调用
- 三审或打分门
