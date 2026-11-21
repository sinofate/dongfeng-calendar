# 比特币抄底指数 v2

v1 文件还在 `out/native/production_not_reference.mp4`（109.051 秒）。这一版是 `out/native-v2/`，没有覆盖它。

口播正文、封面 v3、标题「是买点吗 / 见底还看有没有人接」、字幕样式都没改。NotoSansCJKsc-Bold index 2。

## 新时长

口播仍是 109.050604 秒，没有裁字，也没有对人声末字做淡出。人声结束后加了 0.85 秒尾垫。容器时长 **109.901 秒**。视频 3296 帧 / 109.867 秒，音频 109.901 秒。最后一句「不构成投资建议。」延长到 0:01:49.90，尾垫里还能读到。画面停在最后一张指数图上。BGM 从人声结束才开始 0.85 秒淡出。

人声末段（108.6–109.0）mean −22.0 dB。尾垫（109.2–109.85）mean −46.1 dB、max −31.1 dB，是淡出的配乐，不是把末字压掉。

全片响度：之前 −16.23 LUFS / −2.91 dBTP，线性增益 +0.23 dB，之后 −16.02 LUFS / −2.69 dBTP。视频流哈希与加响度前相同。

## 四项

1. 47–58 秒的压力线改由 librsvg 画附件里的那条三次曲线（M165 280 C320 315 375 385 505 435 S685 625 875 780），2 倍栅格后再缩回主窗。标值仍是约 56000 和约 44800。这是压力示意，不是行情曲线。
2. 58.2–65.5 秒只放官方 S21 规格表细部，200 / 3500 / 17.5 单独可读。65.5–72.7 秒主窗换成电费字卡，两段不叠。字卡和表都在 y312–1440 里面。
3. 16.5–27.3 秒先用 Makkler 日线细部，再切 Owl 的 AHR999 历史图。89.9–99.9 秒先用 Farside 近期行，再切 Bloomingbit 已下载的 ETF 流出页。99.9 秒到结尾先用 Swole 的 0.23 读数，再切同一张图的指数历史。都是本案已有截图的不同部位，不是新数据，也不是整图缩放冒充换内容。
4. 见上面的 0.85 秒尾垫。

## 三个组件是 HTML 调用

Chrome 157 headless 打开原 snippet，跑原脚本，再按 snippet 里的时间轴注释用 GSAP 3.14.2 做 seek 截帧。不是 ASS 重绘。`demo.html` 没打开。

| 组件 | sha256 |
| --- | --- |
| number-pop-in.html | `25bb2a0a3e2dc9a067cfb016d7d8a971b70774652a0a4dca200c9173a1fc4e48` |
| kinetic-center-build.html | `774f75b80d82fbc0c6226b85743804fb7a2229fb038eb0d38fa2e9503072c2e0` |
| panel-reveal.html | `0fbb1c9685a80e10e577d405544bf8db35ec1a27cb0c8bed55a4a1f5fd88d376` |

CustomEase 不在素材库里。按 snippet 的 CDN 地址取了官方 `gsap@3.14.2/dist/CustomEase.min.js`，sha256 `2dae8ef6daba66ce7b527b1f46a5695ba325b21ad5b4d73e4a843753c65415f6`。原 html 没有改。

宿主只做了这些适配，并写在报告的 `host_adaptations` 里：透明底、放在主窗下沿或电费段的正中、Inter/Geist 后面补 Noto 才能画出中文、kinetic 的量字字体补上中文、删掉 panel 自带的 “Duration 420ms / Easing power3.out”。没有把 demo 默认字烧进片子。

`qualified` 仍是 false。exit 0 不是观感通过。
