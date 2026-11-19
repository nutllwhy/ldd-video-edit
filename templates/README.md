# templates

- `project/` — `scripts/new_animation.sh` 用来搭 animation 工程的文件（hyperframes.json、package.json、tools/）
- `shots/` — 三套系列画风的参考镜头，每个 6 秒，都能直接渲：
  - `paper-manual.html` 剪纸拼贴：助理接活 → 翻开手册 → 指着第 2 条 → 打勾
  - `dossier-doc.html` 资料拼贴：任务纸条 → 文件滑进来 → 荧光笔 → 红笔圈 → 真截图冲印件 → 胶带结论（截图放 `assets/shots/shot.png`）
  - `sketch-notebook.html` 铅笔素描本：手册一笔笔画出来 → 镜头跟到助理 → 蓝笔圈重点 → 拉远

- `sketch/` — **SK 素描本管线**（`scripts/new_sketch.sh` 用）：`BRIEF.md` 派活模板、`shots/` 6 个参考镜头（竖屏 1080×1920，改 svg 宽高即横屏）、`assets/shot.png` 占位截图。说明见 `references/sketch.md`

复制成新镜头时（House kit 那三套），文件名、`data-composition-id`、`window.__timelines[...]` 三处改成同一个名字。
