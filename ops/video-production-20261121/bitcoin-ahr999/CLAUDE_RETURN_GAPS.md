# 本轮 e7y Claude 返回的缺件与字段偏差（如实记录，未换路由）

调用：engine/produce-v4/run_e7y.py，端点 https://e7y.com/v1/messages，模型 claude-opus-5-5，http 200，stop_reason=end_turn，146.9s，input 6122 / output 8022 tokens，费用记 0（包月中转）。原始请求（密钥已打码）与响应在 evidence/e7y/。返回了要求的 9 个文件且 JSON 可解析，engine=us3day-vertical-recovery，9 镜，VO 时长 109.050604，未改口播正文。

cloud 渲染前必须处理（不要改 recovery-runtime 源码来迁就占位符；在项目配置侧绑定）：

1. `project.bitcoin-ahr999.json` 的 `subtitles.file` 与代表工程字段名不同，代表配置用 `subtitles.path`。渲染前把键改成 `path`，或同时保留两者指向 `inputs/subtitles/main_LR90.ass`。
2. `bgm_plan.json` 用了 `excerpts[].t0/t1/file`，代表工程是 `segments[].start/end/offset/file/gain_db/fade_in/fade_out`。需按代表 schema 改写，或确认当前 produce 能读 excerpts。曲目与时段本身已按实测轴填好。
3. 占位媒体不是文件：`TITLE_CARD_OK`（s02/s08/s09）、`COMPONENT_price_decline`（s05）。本包提供重建底板 `inputs/media/title_card_bg_071829.jpg`（#071829，非新设计）。把这三处 media 指到该底板；s05 仍叠加 `hf_components:price-decline-56000-44800`。
4. 已有组件 `number-pop-in` / `kinetic-center-build` / `panel-reveal` 只在 project 里引用，源码不在本包 `inputs/components/`。produce 须能从既有 777 catalog / registry 解析这些 id；本包 library_roots 仅含新写的两个组件目录。不要为此去改工具源码翻旧 22 镜。
5. 新组件 registry 的 variables 是对象而不是官方 registry 的数组；`files[].target` 写成了 `main` 而不是 `compositions/components/...`。cover-push-3.html 是 CSS `scale(1)→scale(1.03)` 重建轻推，`push_percent` 变量未接入关键帧（效果已是 3%）。price-decline 有独立 html。都标重建值。
6. 字幕 ASS：口播用字与 script-v4 一致，但夹了两行空事件 `{\alpha&HFF&}`（约 0:00:53.03 与 0:01:34.16），应删除；有一条 18 字「快到二零二零年三一二币灾时的位置了。」超过 15 字切行。Style 名为 Main（代表样片用 D），SecondaryColour 误成黄。时间总体对齐实测 VO。
7. SFX 适度：1.5s 一次 whoosh；数字落板挂在 s03/s06/s07。s01 的 0.23 未单独挂 SFX。s02/s04/s09 明确无。

未把上述偏差在本地改成「已修复的假完整工程」。原始 Claude 文件保持原样。
