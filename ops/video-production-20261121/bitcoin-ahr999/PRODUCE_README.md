将本包与 `recovery-runtime` 并列放置，保持所有 `inputs/` 相对路径。必须补齐事实 JSON 所列封面、S01/S03/S04/S06/S07 图片、VO、五段 BGM excerpt 和 SFX 文件；`inputs/components/` 还必须放入现有 `number-pop-in`、`kinetic-center-build`、`panel-reveal` 的原始 registry 与 snippet，本包未重写这三个组件。

必须拷贝同 SHA-256 的 `inputs/fonts/NotoSansCJK-Regular.ttc`、`inputs/fonts/NotoSansCJK-Bold.ttc`，使用 Noto Sans CJK SC 的 TTC face_index=2，禁止替代。**缺件记录：提供的事实 JSON 没有这两个文件的 SHA-256 值，也没有上述媒体及现有组件的文件实体；本包无法列出或核验其摘要。** 拷贝后用 `sha256sum inputs/fonts/NotoSansCJK-Regular.ttc inputs/fonts/NotoSansCJK-Bold.ttc` 与案卷原件逐一比对。

**未验证记录：未提供 `representative.s04.json`、现有组件 registry 样本或运行中的 `recovery-runtime`；因此本包 project、BGM/SFX plan 和新组件 registry 的具体解析兼容性尚未经 `produce` 验证，不能声称已可直接渲染。** 不修改工具源码，不改用其他模型或渠道。

文件和原始组件补齐并核验后，从本包所在目录执行：

```sh
cd /workspace/pub/ops/video-production-20261121/recovery-runtime
python3 -m recovery_us3day produce --project ../project.bitcoin-ahr999.json --out ../out
```

若本包不与 runtime 并列，`--project` 改为本 JSON 的实际路径；须先确认该入口如何解析 `inputs/` 相对路径。
