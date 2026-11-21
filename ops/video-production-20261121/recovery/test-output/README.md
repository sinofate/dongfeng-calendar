这些静帧来自短 smoke，不是恢复后的成片。

- `smoke_t0.8_cover_not_master.jpg`：0.8 秒仍是锁定封面，合成器还没叠正文页头。
- `smoke_t2.5_plate_not_master.jpg`：封面 1.5 秒硬切之后。页头在主窗口上方，字幕「第二天芯片才崩」在主窗口下方。画面是 360p 参考片裁进主窗口，不是原切片。画面底部那行来源是参考片里原来就烧上的，合成器没有再写一条。
- `smoke_t66.4_comment_not_burned.jpg`：对应母带 66.4 秒。ASS Comment「大约三成」没有烧进字幕带。画面里的大字「约三成」是参考片原有图形，留在主窗口里。
- `smoke_report.json`：两次编码的时长、分辨率和哈希。`recovered_master` 为 false。输出哈希与参考片不同。

mp4 不入库。本机用 `scripts/smoke.sh` 可再生成。
