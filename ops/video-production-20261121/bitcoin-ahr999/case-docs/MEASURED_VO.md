# 实测配音 · v4 · 2026-11-21-bitcoin-ahr999-bottom

核时：2026-11-21 15:51（Asia/Hong_Kong，UTC+8）。口播以 script-v4.md 为准，未改字。封面/三件套仍沿 v3。

## 客户端与授权（未换路由）
- 既有合法客户端：`/workspace/pub/video-clone/knowledge/voice-standard/tts_zh_standard.py`（规范 ZH_VOICE_STANDARD.md，2026-11-05 东风定：语速 1.1 + 录音室干声 P1）
- 本案内复制：`tts_zh_standard.py`；带原始请求/响应日志的案卷运行器：`engine/tts-v4/run_tts_logged.py`
- 模型：MiniMax `speech-2.8-hd`（「MiniMax1.1」指标准语速 1.1，不是另一个模型名）
- voice_id：`moss_audio_41079469-6be9-11f1-a3fb-6a64dd77666f`
- 参数：speed 1.1，vol 1.3，pitch 0，emotion 全段 surprised
- 端点：`https://tts.aurastd.com/api/v1/tts`（与 `TTS_BASE_URL` host 一致）。未改 OpenRouter，未新开付费渠道。密钥仅用已有 `TTS_API_KEY`。
- 原始请求/响应（Authorization 已打码）：`engine/tts-v4/raw/p00_request.json` … `p26_response.json`；汇总 `engine/tts-v4/tts_summary.json`、`engine/tts-v4/tts_run.log`
- 27 段全部 `tts_success`。本环境接口未返回美元计费字段，USD 不详。对齐为本地 faster-whisper `small` CPU，无云端费用。

## 正文与拼接
- 口播正文：`paras.json`（27 句，与 script-v4 纯口播逐字一致，不含主副标题）md5 `bf1098a05276a7ca36a38332984447ab`
- script-v4.md md5 `72a0b4d12564309b90c90d9efd0bd20e`（与 DURATION_v4 所记 `72a0b4d12564309b90c90d9efd0bd20e` 一致）
- 权威拼接：`/workspace/pub/ops/tools/vo_splice_no_clip.py` + 案卷 `vo_p1.sh`（chains.txt 第 1 行录音室干声；P1 延迟补偿 196 samples）
- 句间目标气口循环 0.45/0.48/0.44/0.47/0.43/0.46（均在 0.40–0.50）
- 交付：`audio/vo_p1.wav`（48 kHz / stereo / pcm_f32le）
  - 时长：**109.050604 秒**（约 1 分 49 秒）
  - md5：`4b22203ce78b32cbb861b2099e473bdd`  sha256：`9c3ae20e06e8f0450eb811019658149b3c9cf3b9f78458b7f1df4865b3117eda`  size：41875524
- 拼接前：`audio/vo_pre_p1.wav`；修前备份：`audio/vo_p1.before_decayfix.wav` md5 `ca795eab356dfc08d15cd1486e1c790b`
- 对齐：`audio/vo_alignment.json`、`audio/vo_splice_spec.json`、`audio/vo_splice_report.json`、`audio/align_run.log`

## 双闸
初拼：`clipped_tails=0`；`swallowed_tails=2`（p00「聊」dt=0.19、p24「看」dt=0.17，末字本体在，已低于 −50dB 后掉进数字零）。
按既有办法只在已静区把残响延续 120ms，不改末字本体、不插时间轴：`audio/decayfix_report.json`。
复跑：
- `python3 /workspace/pub/ops/tools/vo_tail_clip_check.py audio/vo_p1.wav audio/vo_alignment.json` → **clipped_tails=0**
- `python3 /workspace/pub/ops/tools/vo_last_char_fade_check.py audio/vo_p1.wav audio/vo_alignment.json` → **swallowed_tails=0**
- 气口 n=26，min=0.42，mean=0.447，max=0.49，lt040=0，no_safe_cut=0

## 实测轴 vs 公式估时
DURATION_v4 公式估时 178.15 秒（约 2 分 58 秒）。实测 109.05 秒，主要因锁定语速 1.1，不得为凑「约 3 分钟」改 speed。若加 1.5 秒开场封面，正片大约 **110.6 秒**（约 1 分 51 秒）。这不是配音失败，是标准语速下的真实长度。

部分句 faster-whisper 对齐比例偏低（p03≈0.53、p07=0.50、p08≈0.58），但末字时间有记录且双闸已过，不把对齐比例写成听感合格。
