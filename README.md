# ldd-video-edit

一套面向口播与知识类视频的剪辑、手绘 MG 动画工作流，覆盖 4:3 横屏和 9:16 竖屏。

它不是一键剪辑器，而是一套可以交给 Agent 执行、也方便自己继续改的流程：从素材整理、转写校对和分镜，到动画、字幕、组装与成片检查。

## 从这里开始

1. 先读 [`SKILL.md`](SKILL.md)，了解完整流程和 G1/G2/G3 三道审核关口。
2. 开始剪辑前读 [`references/rules.md`](references/rules.md)，并按项目情况准备素材、分镜和事实来源。
3. 做手绘 MG 时，先打开风格菜单 [`templates/sketch/styles/preview/menu.html`](templates/sketch/styles/preview/menu.html)，再读 [`references/sketch-styles.md`](references/sketch-styles.md)。新系列先选风格、看样张，再批量制作。
4. 用 `scripts/check_env.sh` 检查本机依赖。命令和路径配置见对应脚本说明。

## 工作流包含什么

- 口播素材整理、转写与专有名词校对
- 按口播内容逐镜规划画面和版式
- 手绘素描本、剪纸、档案拼贴等 MG 动画制作
- 抠像版式：人像抠出加描边、磨砂面板衬底、顶部章节条，横竖屏各一套
- 字幕、配乐、横竖屏组装与接缝检查
- 交付前检查镜头、字幕、角色姿态和道具接触

动画量产前需要先过 G2 样张确认；最终交付前按 G3 检查。自动化脚本能帮忙找问题，但不能替代成片目检。

## 目录

- `SKILL.md` — 从开工到交付的完整工作流
- `scripts/` — 素材预处理、字幕、组装、检查和项目初始化脚本
- `kit/` — 动画与渲染共用代码
- `templates/` — 可复用的动画镜头、风格菜单和项目模板
- `references/` — 剪辑规则、版式、动画、素材与画风说明
- `CREDITS.md` — 参考项目与第三方组件说明

## 隐私与素材

不要把客户 brief、项目复盘、真实用户原话或本机专属路径放进这个可复用仓库。具体项目的素材、事实来源和临时文件应留在对应项目目录。

## 许可

本仓库原创内容采用 MIT License，见 [`LICENSE`](LICENSE)。第三方组件不包含在这份授权内，应按各自的许可与文件声明使用；例如 `kit/gsap.min.js` 保留 GreenSock 自己的许可条款，详见 [`CREDITS.md`](CREDITS.md)。
