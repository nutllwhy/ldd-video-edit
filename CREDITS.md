# 参考的开源项目

## 本仓库的许可范围

本仓库原创内容采用 MIT License，详见根目录的 `LICENSE`。第三方组件不包含在该授权内，仍适用各自的许可和随附声明。

仓库包含 `kit/gsap.min.js`，其文件头注明适用 GreenSock Standard License。使用该组件前，请查看 [GreenSock Standard License](https://gsap.com/standard-license)。

本 skill 的规则是自己写的，部分做法和数字参考了下面这些 MIT 协议的开源项目，没有复制它们的代码。

| 项目 | 参考了什么 |
|---|---|
| [alchaincyf/huashu-art-motion](https://github.com/alchaincyf/huashu-art-motion)（MIT） | 按口播内容选画法的选型表、各画法的镜头时长、"每镜同一个动作就是 PPT"、快推/砸入的时长和倍率、两层帧率、"先出一帧设定稿"的四种做法 |
| [iart-ai/b-roll-skills](https://github.com/iart-ai/b-roll-skills)（MIT） | 口播 B-roll 的露脸/叠加/覆盖三分法、覆盖段 3–8 秒、"两段之间漏出一丝真人会像闪帧"、画面对时的三种方式、"暗底霓虹是 AI 视频的默认陈词" |
| [cth9191/animate](https://github.com/cth9191/animate)（MIT） | 开工前三次便宜的确认（故事 / 样张 / 分镜）、"每 2–4 秒有新东西"、"把概念演出来"、媒材在手机尺寸可见、风格卡片的写法、一拍二 |
| [charlie947/motion-graphics-skills](https://github.com/charlie947/motion-graphics-skills)（MIT） | 禁用默认清单（打字机、发光、弹跳、文字渐变、紫蓝背景）、Vox 风格的构成 |
| [LottieFiles/motion-design-skill](https://github.com/lottiefiles/motion-design-skill)（MIT） | 动作时长表、缓动方向规则、弹簧参数、"看起来廉价/机械"的排查表 |

另参考过 Vincentwei1021/video-talkcraft 的思路（版式轮换、画面字不重复字幕）。它是 PolyForm Noncommercial 协议，商用要作者许可，所以本 skill 没有使用它的任何代码和原文。

想要现成的动画引擎时，可以直接装 huashu-art-motion（`npx skills add alchaincyf/huashu-art-motion`），它的参数化片段能按口播时长渲出动画段，再交给本 skill 的剪辑流程拼接。

另参考过 [imraywang/rayskills](https://github.com/imraywang/rayskills) 里 ray-explainer 的思路：竖屏分屏版式（上半素材、下半真人）、版式之间硬切、"讲人物和名词时分屏字卡会挡嘴"、圆形头像取景到肩膀以上并留头顶。它是 CC BY-NC 4.0 协议，本 skill 没有使用它的代码和原文，竖屏版式的尺寸和脚本是自己做片时调出来的。
