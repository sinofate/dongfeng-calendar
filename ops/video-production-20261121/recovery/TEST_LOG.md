# 测试日志

环境：Python 3.12.3，ffmpeg 6.1.1-3ubuntu5。无 pip 依赖。没有调用 Claude、e7y 或 Suno。

## unittest

```
python3 -m unittest tests.test_recovery -v
test_dialogue_and_comment_are_split ... ok
test_smoke_ass_skips_comment_and_source_badge ... ok
test_counts_come_from_the_index ... ok
test_schema_rejects_wrapper_coercion_and_stand_ins ... ok
test_frozen_ink_matches_master_extracts ... ok
test_project_joins_suggestion_to_timeline_clock ... ok
test_short_composites_are_not_the_reference ... ok
test_clock_uses_seconds_and_reports_frame_gap ... ok
Ran 8 tests in 2.052s
OK
```

集成测试实际跑了 ffmpeg：开场 4.0 秒 1080×1920 30fps，音画时长都是 4.0 秒；s12 窗口 1.1 秒。输出哈希与参考片 `fe69c7509c1d…` 不同。t=2.5 的主窗口红色晶圆像素被断言为不是封面。t=66.4 字幕带黄色像素为 0，「大约三成」不在烧录 ASS 里。

## smoke 报告摘要

`python3 -m recovery_us3day smoke --allow-reference-plate --out out/smoke`

- status: `smoke_composite_on_reference_plate`
- recovered_master: false
- acceptance_recovered_film: false
- opening 1080×1920，30/1，视频 4.0s，音频 4.0s
- s12 窗口 1.1s
- 黄色像素：开场 2.5 秒页头 3139、字幕带 7487；66.4 秒页头 3205、字幕带 0
- historical MarginL/R 30 被沿用，revised_lr 未锁定

静帧见 `test-output/`。这不是全片验收，原切片和 vo_raw 仍然缺失。
