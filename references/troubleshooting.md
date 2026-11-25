# 故障排查（渲染与环境）

跑长片时反复踩到的坑，按现象查。

## 渲染

**长动画一次渲完太慢，改一版要等很久**
把动画按段落拆成 4 段左右分别渲染，可以并行。改完之后只重渲受影响的那几段，没动的段直接复用（拼接时按时间线放回去）。段落边界选在版式切换点或静音处，这样重渲也不会牵动相邻段。

**渲染到一半会话结束，进程被杀了**
后台渲染用 `nohup`（或环境里的等效托管方式）启动，把日志写到文件：

```bash
nohup node render.mjs > render.log 2>&1 &
```

不要只靠前台命令挂着。渲完先看 `render.log` 最后几行和输出文件的大小，再打开画面。

**ffmpeg 新版报 filter script 相关错误**
新版弃用了 `-filter_complex_script`，改用从文件读取的写法——注意那个前导短横是语法的一部分：

```bash
ffmpeg -y -i in.mp4 -/filter_complex fc.txt -map '[vout]' out.mp4
```

**命令里的多个参数被拆坏 / 引号在 zsh 里失效**
zsh 默认不按空格拆分未加引号的变量。带多参数的 ffmpeg 命令包一层：

```bash
bash -c "$cmd"
```

**拼完最后几秒闪一帧 / 某一版突然缺帧**
先跑 `scripts/seam_check.py`。绝大多数是相邻段之间留了小于一帧的空隙，或者口头剪点没对齐（rules E1/E2）。

**中文字幕渲染成方块**
字体查找走 `scripts/cjkfont.py`。`fc-match 'sans:lang=zh'` 在某些机器上会返回一个只有拉丁字符的字体，必须按它的顺序找（`LDD_CJK_FONT` → 系统 CJK 字体 → `fc-list :lang=zh`）。

## 依赖与网络

**`npm install` 被拦截**
用环境自带的安装脚本或离线包安装依赖；装完 `node -e "require('playwright-core')"` 验证一下，再跑渲染。

**`git clone` 超时**
改下载 tarball，比 clone 稳：

```bash
curl -L -o repo.tar.gz https://codeload.github.com/<owner>/<repo>/tar.gz/refs/heads/main
```

推送同理：`git push` 长时间 `Empty reply from server` / 端口 443 超时时，可以走 `gh api` 的 Git Data API 建 blob/tree/commit，再 PATCH `git/refs/heads/main`。

**路径里的中文在 git 里变成转义码**
先 `git config core.quotepath false`。

**macOS 上编译 Swift 工具报 `redefinition of module`**
用 Xcode 的开发者目录显式指定：

```bash
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer xcrun swiftc tools/x.swift -O -o tools/x
```
