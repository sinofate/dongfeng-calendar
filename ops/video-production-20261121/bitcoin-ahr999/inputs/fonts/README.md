# 字体依赖（本包不附 TTC，避免撑爆 25MB）

必须使用真 Noto Sans CJK SC，禁止文泉驿或其他替代。face index = 2（SC）。

从本机已有、且 recovery-runtime 已放置的文件拷贝到本包 `inputs/fonts/`：

| 文件 | 源路径（任选其一，须 sha256 一致） | sha256 | 大小 |
|---|---|---|---|
| NotoSansCJK-Regular.ttc | `/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc` 或 `/workspace/pub/ops/video-production-20261121/recovery-runtime/inputs/fonts/NotoSansCJK-Regular.ttc` | `b76b0433203017ca80401b2ee0dd69350349871c4b19d504c34dbdd80541690a` | 19484784 |
| NotoSansCJK-Bold.ttc | 同上目录 `NotoSansCJK-Bold.ttc` | `faa5f3656a78b2e2d450d27fe8382c778bc2b6bb5ea29c986664a6a435056ceb` | 20050760 |

project.json 已写 `fonts.regular` / `fonts.bold` / `face_index=2` / `substitute_forbidden=true`。
