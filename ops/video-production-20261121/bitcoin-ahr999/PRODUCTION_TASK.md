# 最短生产任务（立刻给 cloud，不要再开一轮准备）

案卷 2026-11-21-bitcoin-ahr999-bottom，锁稿 script-v4。VO 实测 109.050604 秒（语速 1.1），不要补到 3 分钟。用固定 us3day-vertical-recovery produce。不改工具源码，不恢复旧 22 镜，不发布。

## 输入包
- 配置与素材包（本 README 所在结构）
- 口播音频包：`inputs/audio/vo_p1_s16le.wav`（48k stereo pcm_s16le，与终稿 vo_p1.wav 同时长；原 f32le 未打包以免超 25MB）

## 步骤
1. 两包解压到同一目录，保持 `project.bitcoin-ahr999.json` 与 `inputs/` 相对关系。
2. 按 `FONT_DEPENDENCY.md` 把两份 Noto TTC 放到 `inputs/fonts/`，核对 sha256，禁止替代字体。
3. 只做配置绑定，不改口播、不动工具源码（详见 `CLAUDE_RETURN_GAPS.md`）：
   - `subtitles.path` = `inputs/subtitles/main_LR90.ass`
   - s02/s05/s08/s09 的 media 占位改为 `inputs/media/title_card_bg_071829.jpg`
   - 如 produce 只认 bgm `segments`，把 excerpts 改写成代表 schema（文件与时段已给定）
   - 确认 catalog 能解析 `hf_components:number-pop-in` 等已有组件；新组件在 `inputs/components/`
   - 删除 ASS 里两行 `{\alpha&HFF&}`；超 15 字的那句只切行不改字
4. 在 recovery-runtime 目录执行（路径按实际挂载调整）：
   `python3 -m recovery_us3day produce --project <解压根>/project.bitcoin-ahr999.json --out <out>`
5. 技术自检：可播、声画时长、无黑帧、字幕在主窗外、尾字完整、BGM 不压人声、正片无来源角标。成片先交东风看，不发布。

封面两比例与三件套已在 `inputs/covers/` 与 `case-docs/three_piece-v3.md`，本轮不用重做。
