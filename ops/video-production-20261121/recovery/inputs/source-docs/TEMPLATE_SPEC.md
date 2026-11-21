# 98分母本参数与缺件（实测分层，不伪造完整工程）

母本：`/workspace/pub/video-clone/cases/2026-11-07-us-3day-market-correct/`；名称「半导体见底了吗？能不能抄」。证据机器摘录`template_extracted.json`，实片探测`evidence/master_ffprobe.json`，原片15s抽帧`evidence/master_t15.jpg`。抽帧不是重渲，也不是新验收。

## 1 已从真实产物提取
|项目|原产物直接值|证据/可调用入口|
|---|---|---|
|竖屏母带|1080×1920；30fps；h264＋aac；150.566667s|final/final_v1.mp4；ffprobe实测|
|实际时间轴|22镜；total=150.564s；镜长min1.993/max15.033/中位6.4555s|timeline.json（每镜t0/t1/frames）|
|实际字幕|PlayRes1080×1920；Noto Sans CJK SC；76；Bold=-1；黄#FFD700（ASS &H0000D7FF）|final/final_v1.ass:3–10；不是旧frame写的36–44px|
|字幕描边/阴影|Outline=5、Shadow=3；OutlineColour黑；非黄边|同ASS Style D；本次不改源字幕|
|字幕位置/边距|Alignment=2底部居中；MarginV=370、L/R=30；这是锚定/安全距，不等于字墨迹bbox|同ASS；不可把MarginL/R30冒充后来确认的80–100|
|字幕切句|81条有效Dialogue；均10.2593字；最长15字|直接数ASS；实际统计不是模型评分|
|封面成图|cover_1080x1920.jpg与cover.jpg；3:4另图；网格150×200|cover_grid_150x200.jpg已目视；L1白、L2黄最大、L3两行白|
|实际15s画面|上部居中双行“芯片砸掉三成／见底了吗”，第一行黄、第二行白；下部黄字幕；气氛图＋轻量信息pill|evidence/master_t15.jpg；这里只证明可见效果，不能反推出原字体文件/精确字号|

**关键发现**：旧frame字规写title-band44px、subtitle36–44、#FFD247；母本真实ASS却是76px、#FFD700。不能把“抄frame文字”当“克隆98分母本”。实际值与后来修正必须分层，未核定的冲突不能任意取更严后说已锁死。

## 2 有案卷文字记录，但源工程缺失，不能称源码提取
|项目|案卷记录值|出处与限制|
|---|---|---|
|封面字体字号|品牌52；L1=95/gap0/sx0.7832/w896；L2=220/gap0/sx0.7025/w928；L3=91＋87/gap0/sx1|cover_brief.md:18–25；封面生成源码/build/cover/sizes_v1.json不在，具体字体路径与各行y坐标未独立提取|
|封面颜色/底|白/黄/白，科技晶圆红蓝气氛|实际JPG可见；#071829/#FFD247/#20C5E8是案卷frame令牌，不把压缩像素当准确hex|
|页头|L1黄y130、L2白y220、墨迹缝26、居中；title_band记载y150–290|SUBMIT_final_v1.md:44与WARROOM:11；二者描述范围有差，不编成唯一坐标。精确字号/字体、title_band.png原资源缺失|
|开场|0–1.5s锁封面满幅，轻推3%，1.5硬切真切片|storyboard.md:S01；封面轻推动画代码不在，真实曲线/ease缺件|
|主字/配色令牌|白150–190px、黄≥220px；bg #071829；强调#FFD247；辅助#20C5E8；Noto Sans SC/Space Grotesk|案卷frame.md:29–48；是当时规范而非逐镜源码实参|
|四段BGM计划|pb569428 / pb622408 / pb623319 / pb628035；offset8/10/18/6；xfade1.5；原计划gap20，成片提交记gap24|plan.json与SUBMIT_final_v1.md:59；原计划159.3s≠真实150.567s，不能直接拿旧计划时间轴套新成片|
|动效语言|气氛底＋证据窗；Kinetic/CameraPunch/NumberTicker/BGPunch/MaskReveal等；分镜有选型|storyboard.md:106–131；每镜实际GSAP/参数/ease/场景源码缺失，不假称已组件化|

## 3 已确认的后续修正（新制作覆盖历史，不改旧片）
- **竖版上下画面外标题/字幕**：标题放上部画面外、字幕放下部画面外，不能压住主体/证据。新的主画面窗口准确rect、本次未从可运行源提取；不擅编safe-top/bottom坐标。制作负责人从源/已确认修正版固化，不能用原满幅图上叠字假称满足新规则。
- **禁止黄描/黄边糊笔画**：黄填色可以，不能加黄色粗边使字糊。母本ASS黑色outline=5是历史实参，不自动等于所有新场景都可直接照搬；新片须保笔画清楚，不擅拟新黄边参数。
- **句间停顿与尾字完整**：不能为追快切平停顿或掐最后一个音节；时间轴对齐真实口播及尾音，不强制编造新的0.x秒停顿/统一尾垫。
- **正片无来源角标**：清除旧storyboard/样式“来源左下”默认输出；来源URL/日期保存在案卷/切片记录，不在正片打角标。
- 后来已确认ASS MarginL/R≥80–100覆盖母本历史30；具体选择须从实际采用的修正版/工程读取，不把范围任意定成新默认。

## 4 真实调用入口与缺件
### 仍可只读调用
- 成片/字幕/timeline/封面图如上；可用于取帧、参数对照与读取，不用于擅改旧片。
- 通用echo starter `/workspace/pub/video-clone/knowledge/echotribble-template/`：README快速入口→复制hf-starter到**新案**，填shots.json/facts.json/真实assets/各镜HTML，`render_all.sh <shot-id...>`；脚本:36调用`npx hyperframes@0.8.181 render -c shots/<id>.html -o out/<id>.mp4 -q delivery`。
- 此入口属于通用旧模板，**不是现在可直接运行的us-3day母本入口**；本次未复制/运行/安装依赖/渲染。

### 现缺且阻止“一键98分母本”声明
`build/hf/`全目录、各镜HTML/JS、`build/hf/assets/title_band.png`、封面排字源码/字体绑定、原真视频切片、`audio/vo_raw.wav`等缺失。旧提交文件引用它们≠它们今天存在。母本源查找覆盖案卷、/workspace、/tmp、/home/box的命名路径与代码引用，未找到可独立运行的母本源工程，不断言任何远端备份不存在。

最小恢复任务：负责人先追现有备份/原工程文件，原地只读核对版本；确实没有则从母带取证补工程，并把新反求的参数标“重建值”而非原始值。不能换385712横版模板来填这个缺口。本次调查停止于明确缺件，不制作视频、不联系人员、不改母本。
