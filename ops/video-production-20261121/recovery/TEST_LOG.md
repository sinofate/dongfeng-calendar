# 测试日志

环境：Python 3.12.3，ffmpeg 6.1.1。这台云端没有
`/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc` 和
`NotoSansCJK-Bold.ttc`。文泉驿不再写入生成 ASS，也不再当作验收字体。

## 本机上一轮不能算通过

2026-11-21 13:15 HKT 在原 1080×1920 母带上跑过 `validate`、8 项测试和 `smoke`，三次都是 exit 0。那个 exit 0 不合格：

- 生成 ASS 第 10–12 行写的是 `WenQuanYi Micro Hei`。
- 裁切按 360p 的 y104/h376 套到 1080p 上，主窗被放大，右上留下旧黄字碎片。
- 报告文案把这次输入说成低码率参考片。实际探测是 1080×1920、30fps、150.566667 秒。

证据在 `inputs/local-validation/`。

## 这一轮

```
python3 -m unittest tests.test_recovery -v
```

检查：540 坐标和 1080 坐标分开；1080 裁切是 y312/h1128，360 裁切才是 y104/h376；生成 ASS 使用 Noto Sans CJK SC 和 MarginL/R 90；没有 Noto 文件时 `smoke` 退出码 3 且不写 mp4；`produce` 在媒体、口播、BGM、音效、组件都未填时不写 mp4。历史边距 30 仍留在母本样式里。

缺字体测试改成显式传入不存在的字体路径，不再依赖系统里碰巧没有 Noto。附带的两份字体在时，`resolve_noto` 仍能找到它们。11 项测试通过。

## 原生代表片段

`python3 -m recovery_us3day produce --project config/representative.s04.json --out test-output/s04-native`

exit 0。1080×1920、30fps、7.300 秒，音画都是 7.300 秒。画面是干净的 phone_portfolio_mono，不是母带。ASS 为 Noto Sans CJK SC、MarginL/R 90。libass 日志：`fontselect: (Noto Sans CJK SC, 700, 0) -> NotoSansCJKsc-Bold, 2`。

组件调用写在 `production_report.json`：`hf_components:marker-highlight`，registry 的 `marker-draw` 在 0.9 秒，accent blue 从 snippet 读到 `#61a8ff`。这不是原镜 Kinetic 源码，绑定层写明了。SFX 是 none。BGM 是 pb622408 已有截段，-30 dB。

这不是本机那条独立 ffmpeg probe，也不是 22 镜成片。默认 `produce` 仍因整片缺素材拒绝编码。参考 smoke 里的旧字幕和来源行仍然不能当无来源证明。

## 响度

同一条 `produce` 在混音后做一次线性增益。原母带文件不在这台环境，没有重测它的响度。SUBMIT 记载的 I=-14.0 LUFS / TP=-2.4 dBTP 只作文书，不拿来当这次混音参数。重建目标是 -16 LUFS，真峰值不超过 -1.5 dBTP。

代表片实测：提升前 I=-32.77 LUFS、TP=-19.12 dBTP、时长 7.3 秒；增益 +16.77 dB；提升后 I=-16.04 LUFS、TP=-2.38 dBTP、时长仍是 7.3 秒。LRA 前后都是 1.8。视频流 sha256 与加响度前的视频编码相同，因为最终封装对视频是 copy。字体选择仍是 NotoSansCJKsc-Bold index 2。

## 本机观看后的窗口修正

观看结论写进 `GAPS.md`：1.5 秒后主窗极度放大，白卡右侧被截，右上有旧黄标题残笔；原底部字幕被裁掉，所以没有第二条黄字幕；新标题和字幕叠在满屏画面里。合成改为先把整帧缩放到 1080×1920，再取 y312–1440。色带测试确认上下带不再吃进画面的红/蓝。对 t2.5 抽帧做了同路径窗口，信息卡四个指数都在窗口里，来源行仍在，见 `test-output/geometry_window_t2.5_not_a_film.jpg`。标题字号从亮核估计的 54/42 改为重建 88/64，仍在主窗上方。这台环境没有 Noto，没有把这次窗口静帧写成字体验收。
