# T-1 恢复证据与实现交棒（非新流程）
时间：2026-11-21T12:59:50.593745+08:00（香港时间 UTC+8）

## 已执行及停点
- 已加载 video-production-owner / code-changes；读 MASTER_RECOVERY_STATUS.md、TEMPLATE_SPEC.md、ASSET_INVENTORY.md；asset_catalog.json 以程序加载检索777条，不整份读入对话。
- 用路径祖先 .git 元数据发现 `/workspace/pub/.git`；`git remote -v` 回 `https://github.com/sinofate/dongfeng-calendar.git`。目标 ops 与母本目录 `git ls-files` 均无输出，`git check-ignore` 均无输出：目前未跟踪也未忽略，但均在该仓库工作树内；不把“未跟踪”擅自当成非repo授权。
- 已有文件名中存在 `engine-claude-seed`，但不推断它是完整工程；发现repo后未深入代码/历史调查。未再做全盘扫描，未重查Drive。
- 本次仅新增用户明确要求的行政交棒/证据MD、JSON；没有新写恢复脚本、没有改工程代码或旧媒体。按任务repo分支停在清楚URL、输入路径及brief，交父岗由cloud执行，未联系其它bot。

## Claude证据与具体缺口
- `/home/box/.local/bin/claude --version` 实际返回 `2.1.296 (Claude Code)`；这是CLI执行证据，**不是模型调用返回**，模型/服务端时间均未知。
- `e7y` 不在PATH。现有索引777条检索 e7y/claude/title_band/engine-claude-seed 未给出e7y客户端（只命中无关claude-exchange动效条目）；非repo `/workspace/tools` 顶层也未发现命名客户端。
- 未读取CLI配置、环境token、凭据或安装脚本；不调用未经确认的Claude默认路由，避免静默切付费渠道。本轮**未完成实际Claude模型调用要求**。需父岗提供既有sanctioned客户端的非敏感入口及调用说明，或cloud在已授权渠道内确认入口后执行并留原始响应/模型/时间。

## 父岗可直接交cloud的实现brief
Repo：`https://github.com/sinofate/dongfeng-calendar.git`。
输入（本机独有，cloud远端不能假设存在；先确认可用共享worker或传递所需附件）：
- `/workspace/pub/video-clone/cases/2026-11-07-us-3day-market-correct/`（只读母带/ASS/timeline/封面/现有文书）
- `/workspace/pub/ops/video-production-20261121/` 下三份已读规范、template_extracted.json、asset_catalog.json、evidence。
输出：统一放 `/workspace/pub/ops/video-production-20261121/` 下新恢复目录；原案/已交片只读。
结果目标：先按repo历史/`engine-claude-seed`归属调查真正源文件；无源则按实片取证重建，不新设计。交依赖固定的运行入口、填槽配置、可追溯参数表、短smoke视频、母带/重建同时间点抽帧和ffprobe/字幕边界/声画检测证据。Claude必须真实调用，优先已有e7y客户端；记录模型与香港时间、返回，失败如实留证，不默认新付费渠道。
边界：不拿echo或横版385712替代；三审/打分不恢复；不动FJQ、不新选题、不发/上传成片；若远端无法取得本机媒体，先交源代码/命令给本机批准的媒体执行步骤，不凭空报渲染成功。

## 参数分层（来自已读规范，非本轮重新实测）
|层级|值或约束|处理|
|---|---|---|
|原始提取值（已有证据）|1080×1920、30fps、150.566667s；22镜；ASS Noto Sans CJK SC 76/Bold，黄填#FFD700、黑描边5、影3、MarginV370、L/R30|保留出处；本轮未独立重测|
|文书记载值|页头L1黄y130、L2白y220、墨迹缝26；另记title_band y150–290|存在差异，不能伪装唯一实参|
|后续确认约束|上标题/下字幕位于主画面外；黄线不挡字、无黄色粗描边；正片无来源角标；后来L/R80–100|与历史30明确区分；具体rect/边距选择须核源/标重建|
|重建估计值|尚未生成|不得把新估计写成原源码提取值|

## 未完成，不能交付为恢复成功
尚无运行入口/依赖锁定/填槽配置/smoke/对照抽帧/模型调用。未找回原切片、vo_raw或页头源图，未声称像素级还原。当前交付是repo分支的可行动实现brief及实际preflight证据，不是成片或恢复模板。
