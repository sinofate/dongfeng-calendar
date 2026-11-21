# 本机制作工具运行证据 · 2026-11-21T13:17:45.549676+08:00（香港时间 UTC+8）

## 提取/原案保护
artifact 3,752,572字节；tar69条全部确认无绝对路径、..、symlink/hardlink/device后解到本非repo运行目录。未读实现代码，未改交付源码/配置，未合并PR；母本/FJQ/已交片只读。
读取README、TEST_LOG、GAPS及JSON配置；执行已交付工具，不做新片。源码/逻辑问题请回原cloud。

## 实际命令和退出码
工作目录 `/workspace/template-recovery-runtime-20261121/recovery`。
1. `python3 -m recovery_us3day validate` exit0：22镜配置通过；日志 ../validate.log。
2. `python3 -m unittest tests/test_recovery.py` exit0：8项测试通过，2.607秒；日志 ../unittest.log（测试是交付原包执行，不能替代人工观感/真字体验收）。
3. `python3 -m recovery_us3day smoke --reference /workspace/pub/video-clone/cases/2026-11-07-us-3day-market-correct/final/final_v1.mp4 --ass /workspace/pub/video-clone/cases/2026-11-07-us-3day-market-correct/final/final_v1.ass --cover /workspace/pub/video-clone/cases/2026-11-07-us-3day-market-correct/cover_1080x1920.jpg --allow-reference-plate --out /workspace/template-recovery-runtime-20261121/smoke-original` exit0；日志 ../smoke.log；实际opening 4.0秒、s12 1.1秒，均1080×1920、30fps，音画时长匹配。空ffmpeg错误日志只证明未报编码错误。
主短片另复制到 `/workspace/template-recovery-smoke-original-NOT-RECOVERED.mp4`，便于videoReview。明确：旧片底板裁切合成，**非完整恢复成片**。

## 必须回cloud的实际问题
- **真字体未被工具采用**：本机已装Noto，fc-match真实路径regular `/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc`（SC index2）；bold `/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc`（index2）。但交付工具生成的smoke ASS第10–12行仍全写`WenQuanYi Micro Hei`，不是Noto，故不能通过真字体验收。未本地改实现/配置，请cloud增加/修复真实字体选择及验证。
- **全分辨率输入裁切异常**：README允许原母带作为reference；实跑opening t2.5、s12 t66.4主窗都严重放大裁切，右上有残留黄色字碎片，英文新闻底板被截大，不可称符合母本。抽帧在smoke-original/。仅报告实测症状，不自行查代码定位。
- **来源/字幕残留风险仍未排除**：引用烧录旧字幕/字图的母带不是干净切片，现主窗已见旧黄字碎片（重复文字层风险）。原母带t2.5参考帧已确认烧录“来源：MagicInvestors / X · 2026-11-04”；当前smoke样本未见完整可读该角标，但不能据此宣称全片清除；工具自己不画角标≠底板没有角标。参考裁切不作为固定母本恢复成功。
- **报告输入文案不准确**：本次传原1080p母带，smoke_report仍用low-bitrate reference固定描述；需按实际输入探测写报告，不能误称本机用了360p。
- 不存在原镜头/vo_raw、22镜真实组件/素材绑定仍空；smoke通过≠全片恢复，不引入三审打分。

## 只做字体诊断的真实Noto视频（不是工具修复）
为验证本机Noto确可渲染，仅把**新生成输出ASS的副本**字体名替为Noto，在纯色测试底板用ffmpeg/libass渲染4秒；不改交付工程、不碰源ASS。
文件 `/workspace/template-recovery-Noto-font-only-PROBE.mp4`，无音频，只诊断字体，不是恢复合成片。
命令 `ffmpeg -hide_banner -loglevel verbose -f lavfi -i color=c=0x071829:s=1080x1920:r=30:d=4 -vf ass=<local-evidence/noto_font_only_probe.ass> -c:v libx264 -preset ultrafast -crf 25 -an -y /workspace/template-recovery-Noto-font-only-PROBE.mp4` exit0。
日志noto_font_only_ffmpeg.log第51行实证 `fontselect: (Noto Sans CJK SC, 700, 0) -> /usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc, 2, NotoSansCJKsc-Bold`。与交付工具的字体失败分开报告。

## 原母带独立探测
original_master_ffprobe.json：1080×1920；r_frame_rate=30/1；视频duration150.566667秒（format也请据探测值区分），原文件84,893,878字节；不是本轮重渲。

## 后续实际采用MarginL/R90证据（只读核准）
`/workspace/pub/video-clone/cases/2026-11-11-openai-anthropic-revenue-race/final/final_v4.ass:10`：
`Style: Default,Noto Sans CJK SC,76,&H0000D7FF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,5,3,2,90,90,370,1`
实际md5=`4887b2bebd4e502ee44f53c0ae132316`，与该案WARROOM:179在2026-11-11 15:06 HKT记载的ASS `4887b2be`相符；WARROOM:182记15:12 HKT已终交。`DELIVERY-final_v4-card.md:1–4,15–17`明确2026-11-11 15:11 HKT终交final_v4（成片md5 bc2438d02897ef555f38a58c5a24ec1c），微信15:11:40 HKT已发、视频号未发。这是**后续已交付片采用90**证据，不是随意从80–100范围选数，也不是证明母本历史30原本就是90。
源ASS文件mtime为2026-11-18 10:31:18 HKT（可能同步落盘），不冒充制作时间。历史文书含旧评分仅用于采用状态，不恢复三审规则。
