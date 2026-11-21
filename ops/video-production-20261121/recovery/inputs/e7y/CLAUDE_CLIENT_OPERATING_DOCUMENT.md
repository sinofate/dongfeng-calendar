# 动效模板库索引（2026-10-20 下载，只读 clone --depth 1）

> **剪辑标准化（2026-11-02）**：按场景从本索引套用模板；开篇优先真切片；真视频约20%–50%。详见 [`../brand/EDIT_STANDARD_2026-11-02.md`](../brand/EDIT_STANDARD_2026-11-02.md)。

> **AI认知局动效速查（按内容类型勾选）2026-11-02d-prod**：
> [`ai-renzhiju-motion-cheatsheet.md`](./ai-renzhiju-motion-cheatsheet.md)（权威同源：`../brand/ai-renzhiju-motion-cheatsheet.md` · md5 `09394cb700c2a1c40290d5ee8f109118`）· 制作核对+备注列；新案卷分镜强制勾选；已发不返工。
> 核对报告：[`../brand/_verify_motion_cheatsheet_2026-11-02.md`](../brand/_verify_motion_cheatsheet_2026-11-02.md)


## 选中仓库
| 角色 | 仓库 | star | 许可证 | 路径 |
|---|---|---|---|---|
| 主库 | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | 67,860 | Apache-2.0（可商用，保留 LICENSE/NOTICE） | ./hyperframes |
| 备选（Remotion 体系，贴合我们现有 Remotion） | [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) | 12,563 | Apache-2.0（可商用；镜头卡为"研究后重写"，见 references/shots/ATTRIBUTION.md，勿复刻原片品牌素材） | ./video-shotcraft |

HyperFrames = "Write HTML. Render video. Built for agents"，自带 Claude Code skills + registry（约 210 个 blocks + 270 个 components，GSAP/HTML 动效）。
未选：calesthio/OpenMontage（70,047★，AGPL-3.0，是整套制作系统而非模板库，AGPL 有商用传染风险）。

## 一、HyperFrames registry（按口播场景挑）
完整目录：hyperframes/registry/components/CATALOG.md；blocks 在 registry/blocks/<名>/。
- 开场钩子：headline-slam, char-slam-explode, shutter-slam, kinetic-center-build, titlecard-lockup, logo-sting, zoom-through-transition, pull-back-reveal, glass-shard-title(block), yt-prism-title(block), wireframe-portal-title(block)
- 数据增长/数字：count-up, number-pop-in, number-wheel, slot-machine-roll, animated-bar-chart, chart-story, decline-chart, conic-progress-ring, mk-usage-arc, bar-chart-race(block), data-chart(block), mk-line-graph(block), mk-progress-stat(block), heatmap(block), apple-money-count(block), split-flap-board(block)
- 对比：comparison-split, before-after-wipe, grade-split-reveal, split-tilt-cards, strikethrough-replace, text-state-swap
- 引语/新闻截图/帖子：x-post(block), reddit-post(block), yt-comment-card(block), news-ticker(block), ticker-takeover, testimonial-card, spotlight-card, marker-highlight, inline-highlight, hw-underline, hw-callout-circle, vox-annotate, paper-collage-reveal, editorial-flash-overlay(block)
- 字幕/关键词强调：caption-kinetic-slam, caption-highlight, caption-pill-karaoke, caption-editorial-emphasis, caption-weight-shift, per-word-rise, per-word-crossfade, text-stagger, typewriter, scramble-reveal, matrix-decode
- 地图/地缘：world-map, us-map, us-map-flow, us-map-bubble, nyc-paris-flight（blocks）
- 运镜/节拍推近：push-in, parallax-zoom, camera-shake, focus-rack, camera-dolly-zoom(block), cinematic-zoom(block), whip-pan(block), beat-accent, beat-pulse-background, beat-freeze-cut(block)
- 转场：whip-pan-cut, match-cut, type-match-cut, iris-reveal, directional-wipe, torn-paper-rip, ink-bleed-reveal, flash-through-white(block), transitions-*(block 系列：blur/push/grid/light/radial/scale/destruction 等)
- 背景/质感：mesh-gradient-bg, aurora-drift, grain-overlay, vignette, light-sweep-pass, starfield/nebula/godrays/light-leak(blocks)
- 结尾：cta-close, cta-lockup, logo-brand-close, x-follow-card, logo-outro(block), tiktok-follow(block)

## 二、video-shotcraft 镜头卡（references/shots/<类>/<名>.md，附 demo 源码）
- opening（开场钩子）：brand-ink-open, crane-rise-reveal, dataviz-landscape-open, fracture, letterspace-materialize, orbit-ring-title-open, spotlight-hero-card, stroke-segment-build, text-as-mask
- data（数据）：before-after-slider-scrub（对比）, chart-live-moves, gauge-readout-moves, timeline-travel（时间线）, scroll-brake-moves
- typography（金句/引语）：flying-words, lead-word-zoom-assemble, marker-underline-title, outline-word-fill, paper-title-card, document-typewriter-reveal, gradient-word-sweep, type-rhythm-sync, vertical-word-roll-blur-cycle, word-relay-*
- camera（运镜）：crash-zoom-punch（强调）, depth-layer-moves（2.5D 截图）, steep-tilt-glide, tension-camera-moves, space-camera-moves
- effects（点睛）：impact-feedback, spotlight-sweep-moves, scan-bracket-sweep, scanline-annotate-focus（截图标注）, fui-hud-moves, riso-print-hits, slam-entrance-moves
- rhythm（节拍）：beat-cut-moves, speed-ramp-freeze, rhythm-interrupt-moves, quad-split-parallel-scenes, trailer-grammar-moves
- transition（转场）：circle-match-iris, line-carry-transition, transition-hidden-cut, wipe-transitions, page-turn-transitions, tear-streak-transitions, white-flash-logo-simplify-cut, mosaic-reframe, card-flip-reveal
- ui-entrance（多卡/列表）：card-stack, carousel-3d, deck-deal-flyin, list-reveal, research-card-stack-scroll, integration-hub-map, wall-reveal-moves
- outro（结尾）：grain-dissolve, logo-shrink-wordmark-lockup, ui-to-brand-morph
- 另：references/sound-design.md、music-beat-sync.md（BGM/SFX 卡点）、aesthetic-rules.md、final-review.md

## 三、Claude Code 怎么调用
已软链安装到 ~/.claude/skills/：hyperframes 全部 21 个 skill（hyperframes, hyperframes-animation, hyperframes-registry, motion-graphics, faceless-explainer, embedded-captions, hyperframes-audio, media-use, …）+ video-shotcraft。
claude CLI 2.1.296 位于 /home/box/.local/bin/claude；环境变量 ANTHROPIC_BASE_URL=https://e7y.com、ANTHROPIC_API_KEY（不打印）。
示例 prompt：「用 hyperframes-registry 先选块，再用 hyperframes-animation 设计；1080×1920 竖版，按分镜 beats 表逐段挑 registry 组件，0–1.5s 为 coverC 封面推近」；或「用 video-shotcraft 的 opening/brand-ink-open 与 data/chart-live-moves 卡做第 2、5 镜」。

## 四、与现有流程衔接（code-reel-video skill）
1. 撰稿→分镜：剪辑师每个 beat 标注「场景类型 → 组件名」（用上面清单），写进分镜表。
2. 渲染路线二选一：A) HyperFrames（HTML+GSAP，`npx hyperframes render`，竖版 1080×1920）；B) 现有 Remotion：参照 video-shotcraft 的 demo 源码移植动效。PIL+ffmpeg 只做封面/拼接/混音。
3. 开场 0–1.5s 仍是 coverC 封面 + 轻推近（push-in / parallax-zoom），之后切第一个钩子组件。
4. 视频内不放 logo（Layout v2）；英文版只换口播/字幕，不重跑动效。
5. 首次使用 HyperFrames 需要在临时目录 npm/bun install（尚未执行、未验证渲染）。

## 五、AI认知局 Modern Motion 硬清单（2026-11-02b）

站内七招 + 每片 ≥3：`/workspace/pub/video-clone/knowledge/brand/ai-renzhiju-modern-motion.md`  
分镜写 `MOTION_MODERN: 招@镜,...`；色值用 brand frame（`#FFD247` 等），勿抄外站橙。

