# 本机run2结果 · 2026-11-21T13:30:28.851969+08:00（香港时间 UTC+8）
- artifact安全提取89条；未调查/改动交付实现。validate exit0；unittest11项1失败（10通过），失败文本为test_unfilled_slots_write_no_film断言fonts.noto缺失，但本机确实有字体；需cloud让测试适应字体存在环境，不在本机改测试。
- smoke原1080p母带exit2（工具刻意不判资格），4秒/1.1秒已编码1080×1920/30fps；生成ASS全为Noto、后续Margin90，主窗按真实1080p取y312/h1128，抽帧已确认不再异常放大。上下字均在独立主窗外带；无黄粗边/黄线遮字。
- 仍明显含旧片烧录来源：opening_t2.5有MagicInvestors / X · 2026-11-04，s12有QuantData / X · 2026-11-05及旧画面大字约三成。不是已清除字幕/来源的生产片，不判完整恢复。
- produce默认配置实跑exit2，有47项缺口，不出mp4。尚未原生生产贯通，不虚填22镜；给cloud代表区间的真实干净输入。
- 独立媒体验证：/workspace/template-recovery-representative-CLEAN-MEDIA-PROBE-v2.mp4，7.3秒、1080×1920/30fps，用原案干净phone底图+完整p03+真实ASS s04+BGM；全程不用旧母带，不是旧片抹字。原asset是已存在Image2.5气氛图，不冒充实拍；尾字完整性未以人工耳听保证，完整p03保留。
- 独立试片字体日志实际选择NotoSansCJK-Bold.ttc SC index2；没有HF组件执行。此样本仅验证真实可替换输入/字带/声画路径，不是native produce结果或完整恢复成片。
- 字体两个独立zip，各<25MB；组件原目录及媒体输入包见/workspace/template-recovery-supplement-20261121.zip。字体与源目录只复制打包，不深入改代码，无新模型付费调用。
