# 实际资产盘点 · 2026-11-21（香港时间）

## 口径与证据
本次递归遍历下列真实路径，源文件只读；不搬、不删、不改库。排除.git、node_modules、缓存、routine-state及凭据类文件名；不读密钥。`asset_files.jsonl`逐文件记录路径/字节数/SHA256；`asset_summary.json`汇总；`asset_duplicates.json`列同字节重复组；`asset_catalog.json`统一查找ID/原路径/原生参数（不是新运行时）。可复查脚本`inventory_assets.py`只写本目录。
“去重”＝SHA256完全相同字节；不是感知动效去重，也不是声纹/去标签后音频去重。下表文件数含说明、预览、示例与构建中间件，**不是全部可直接调用的效果数或曲数**。未逐个渲染/试听，不声称全库已测试可用。

|库ID|真实根路径|实际文件|SHA256去重文件|音频文件/字节去重|
|---|---|---:|---:|---:|
|master|`/workspace/pub/video-clone/cases/2026-11-07-us-3day-market-correct`|484|461|22/22|
|echo_starter|`/workspace/pub/video-clone/knowledge/echotribble-template`|69|69|0/0|
|hf_components|`/workspace/pub/video-clone/knowledge/motion-templates/hyperframes/registry/components`|851|841|0/0|
|hf_blocks|`/workspace/pub/video-clone/knowledge/motion-templates/hyperframes/registry/blocks`|769|630|4/4|
|motion_curated|`/workspace/pub/video-clone/knowledge/motion-lib`|122|122|1/1|
|shotcraft|`/workspace/pub/video-clone/knowledge/motion-templates/video-shotcraft`|1360|1182|165/151|
|kinetic_385712|`/workspace/pub/video-clone/motion-templates/385712`|357|299|0/0|
|bgm_tracks|`/workspace/pub/video-clone/knowledge/bgm-library/tracks`|42|42|42/42|
|bgm_previews|`/workspace/pub/video-clone/knowledge/bgm-library/previews`|31|31|31/31|
|suno_ip|`/workspace/pub/video-clone/knowledge/bgm-library/suno-ip`|41|40|36/36|
|sfx_semantic|`/workspace/pub/video-clone/style_v2/sfx_semantic`|92|92|90/90|
|sfx_legacy|`/workspace/pub/video-clone/style_v2/sfx`|16|16|16/16|

## 可用生产口径（不可拿支持文件凑数）
- HyperFrames上游registry：**237 components + 210 blocks**（各自目录下registry-item.json数）；motion-lib精选**34**个registry条目是既有上游的调用入口/拷贝，不再加成34种新效果。旧COMPONENT_MANIFEST.md末行竟留有`{len(uniq)}`占位符，不能照抄为数量。
- video-shotcraft：references/shots下**125张镜头卡**；是配套TSX/Remotion参考，不是125个可直接插入HF的组件。全树165音频文件、字节去重151，含demo/镜头配音等；**不当作151条已授权可用BGM/SFX**，须核具体用途/许可。
- 另有echotribble旧starter（shared primitives及4示例）与**385712**原生动效模板。385712适配器明确仅支持landscape，当前不能冒充竖版us-3day母本，不能因它代码完整而偷换模板。
- 正式BGM `tracks/`：**42个MP3，字节去重42**。旧index.json只有**40条，40/40本地存在**；漏登记`tracks/ip-theme/AI认知局_theme_A_0m33.mp3`与`AI认知局_theme_B_0m31.mp3`。本次索引补作bgm_unindexed，不改旧库。previews/31个是试听，不额外算曲。
- Suno IP目录顶层**20个MP3**：4个`theme_{calm,tension,uplift,teaching}_ip.mp3`正式拼接候选、4个theme raw、2个共用logo、1个sonic_logo源、2个hook及2个hook raw、4个lyria旧备份、1个串联试听。另有16个_build中间WAV；总音频36，不可叫36首独立BGM。四版是否最终被东风定为唯一IP未在本次独立核实，不把“候选”升成已批。
- 正式语义SFX：**12类89个WAV，字节去重89，sound_map.json的89/89引用都存在**；加1个PREVIEW_all.mp3只是试听。旧style_v2/sfx有**16个WAV、去重16**。这两处生产SFX合计**105个WAV，跨两库字节去重105**（不是105种语义，只有12个语义类别＋旧通用声）。

## 语义音效分类
- `rise_up`：8
- `fall_down`：7
- `explode_impact`：8
- `keyboard_typing`：7
- `alert_alarm`：7
- `money_trade`：8
- `tech_ui`：7
- `error_wrong`：7
- `correct_check`：7
- `tension_heartbeat`：8
- `camera_paper`：8
- `crowd_news`：7

## 已检查接口、参数与示例
### 动效（索引统一，不移动源库）
1. `asset_catalog.json`查`hf_components:count-up`→原registry-item.json与variables/syncPoints；原生参数例：`start=0,end=128,prefix="",suffix="%",accent="green",glow=false,exit="none"`；`count-land`原同步偏移1.72s。**此例只说明原生schema，不是品牌可直接采用绿字的许可**；品牌适配必须保留98分母本字色字号，不能新造版式。
2. `motion_curated:count-up`是上游别名；`motion-lib/wrappers/wrap.py count-up number=128 intensity=0.6`本次运行仅输出JSON，**不是渲染成功**。发现返回accent="#FFD247"（原schema枚举仅green/blue/violet）、glow=0.6（原schema要boolean）；char-slam spread同样是枚举映射风险。此包装只实现count-up/marker-highlight/char-slam-explode三项且类型不完全合，不能当成熟统一调用层。
3. HF/shotcraft源码在；逐镜务必引用实际registry variables/源码入口，而不是只写“Kinetic”。shotcraft按`shotcraft:<分类>/<卡名>`定位参考卡和相应demo；跨引擎移植未测。
4. echo `hf-starter/shared/lib.js`有`markerSweep(tl,el,at,duration=.33)`、`scramble(tl,el,text,at,duration,options)`、`screenshotObject(screen,image,w,h)`等；这些是旧通用原语，不能证明us-3day直接源码仍在。
5. 385712 `template/adapter.py`检查`layout == landscape`，`render.mjs --root <消费工程> --out <新输出>`固定1920x1080/60fps。竖版不支持；本次只读未运行。

### BGM
`knowledge/bgm-library/tools/mix_bgm.py`：`--vo --plan --out --gap-lu --xfade --stem-dir --vo-start --vo-dur`。本次只运行`--help`成功，未混音。
plan格式：`{"segments":[{"start":0,"end":12,"track":"pb323181","offset":20,"role":"hook","gain_db":0}]}`；track可曲ID或文件绝对路径，Suno IP曲须用路径（该脚本ID查找只扫tracks）。role=hook/body/transition/climax/outro；默认xfade=1.5；输出是**人声+BGM全混**，不能再当纯BGM叠一次人声；纯BGM从stem-dir取`stem_bgm_ducked.wav`。
只读示例命令（未执行）：`python3 .../tools/mix_bgm.py --vo <新案>/audio/vo.wav --plan <新案>/plan.json --out <新案>/bgmtool_fullmix.wav --stem-dir <新案>/stems --gap-lu 20 --xfade 1.5`。具体音量与情绪在逐镜表确定，不把默认数字冒充本次试听结论。
Suno IP现有`build_ip_themes.py`是本地ffmpeg重拼/响度脚本，**不是Suno生成API**，会覆盖原IP文件，未运行。历史来源/拼法在suno-ip/README.md；本次未生成、未付费。

### Suno接口现状（不可称成功）
本次GetDynamicTools查询`suno|music|音乐`，`user-Suno`及`user-suno-mcp`均为**needsAuth**，工具schema不可用；没有调用生成/没有读取凭据/没有重试绕过。工作区按Suno命名查到的生产脚本只有上述本地build脚本，未发现可独立确认的Suno生成API客户端。不能据用户“已有接口”就声称现在可调用；也不能断言账号没有接口。恢复鉴权由主流程处理，本次只记事实。

### SFX
`style_v2/sfx_semantic/sound_map.json`按meaning_map/items选声；每条有file、category、good_for/avoid、duration_sec、peak_ms、来源/许可。示例`rise_up/rise_up_scale_major_01.wav`、峰值737ms；调用时写**真实本地路径、片内触发秒或peak目标、gain_db、淡入出**。无声写none，不用通用声凑数。
echo旧`audio/mix.py`消费`[{t_peak,file,gain_db,why}]`并用`sfx/sfx_peaks.json`的peak_s对齐；新案sfx_events常是events对象、t_est/db/path字段，**不能直接无转换喂旧混音器**。制作负责人从单一逐镜表导出适配结构，音效复制/寻址由新案完成；本次未混音验证。

## 母本可运行性（重要缺件）
us-3day目前484个可盘文件、去重461；final/final_v1.mp4在、字幕ASS在、22段pXX.mp3在；**build/hf不存在、title_band.png不存在、列出的media/clips原片全缺、audio/vo_raw.wav不存在**。所以“可运行98分母本入口”本轮结论＝**缺失，不能声称现成一键复用**。历史引用的路径不是现在可执行证据。
可追溯通用旧入口：echo README的`render_all.sh <shot-id...>`→`npx hyperframes@0.8.181 render -c shots/<id>.html -o out/<id>.mp4 -q delivery`；需要真实shots、assets、工具与依赖，不是us-3day工程。本机有node/npx/ffmpeg/ffprobe但未做npx安装/联网/渲染，不等于可复跑。细节见TEMPLATE_SPEC.md。

## 未做与后续最小动作
未全库试听/渲染/许可复审，未恢复缺件，未搜新选题素材；本清单范围只涵盖列出的现有根，不保证所有历史私聊发过的库都已归档。负责人先找回母本源工程与原资源或取得其备份；仅从实片反求参数时须明确“提取值”与“估计值”，不能假称原代码；其次修复三项wrapper类型映射与Suno鉴权，不以这些动作新设审稿门。其他旧案例不重渲。
