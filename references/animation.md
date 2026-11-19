# 动画怎么做（给接手的 Agent）

技术栈：**HyperFrames（Chrome 逐帧渲染 HTML）+ GSAP 时间轴 + SVG**。一个镜头 = 一个 `compositions/<名字>.html` = 渲出来一个 `renders/<名字>.mp4`，最后由 `scripts/assemble.py` 按剪辑表叠到口播上。

## 1. 搭工程
```bash
export SK="$(pwd)"  # 在 skill 仓库根目录运行
$SK/scripts/new_animation.sh <project> paper-manual dossier-doc sketch-notebook
cd <project>/animation && ./tools/render.sh paper-manual     # 先把模板原样渲一遍，确认环境没问题（约 10 秒）
```
得到：
```
animation/
  compositions/   每个镜头一个 html（从模板复制改）
  kit/house.js    画风滤镜 + 动作工具（见下）
  kit/house.css
  assets/gsap.min.js  assets/shots/（去过标识的真截图）  assets/media/
  tools/render.sh  sheet.sh  frames.sh  still.sh
  renders/        成品 mp4 + sheets/ 联系表
```

## 2. 一个镜头的写法（硬性约定）
- 根节点：`<div id="root" data-composition-id="X" data-start="0" data-width="1440" data-height="1080" data-duration="6" data-fps="30">`
- 最后一行：`window.__timelines["X"] = tl;`，**X 必须和 data-composition-id、文件名一致**
- 时间轴 `gsap.timeline({ paused: true })`，末尾加 `tl.to({}, { duration: D }, 0)` 把时长撑满
- 只用时间轴驱动动画。不要 `setTimeout`、`requestAnimationFrame`、CSS animation——渲染器是跳着 seek 的，这些都不会跟着走
- 要随时间变的属性（如噪声 seed）用一个代理 tween 的 `onUpdate` 去改，见 `House.boil`
- **画面里不放字幕**。字幕剪辑时统一烧在 y 930–1040；重要内容放在 y 920 以上（`#root` 加 class `safe` 可以看到字幕带）
- **路径按工程根目录（`animation/`）写**：`assets/gsap.min.js`、`kit/house.js`、`assets/shots/x.png`。HyperFrames 从工程根加载；直接双击 html 在浏览器里打开会找不到脚本，预览用 `npx hyperframes preview`
- **第 0 帧**：上一镜已经在画面里的东西（角色、桌子）这一镜第 0 帧就在，不要每镜都重新弹出来；`House.pop` 只给这个角色在整期里**第一次**出场
- 镜头时长按剪辑表来：全屏覆盖段 3–8 秒。口播一句话撑 15 秒的，拆成两三个镜头，中间换景别

## 3. House kit（`kit/house.js`）
| 函数 | 干什么 |
|---|---|
| `House.defs(svg, "paper"/"dossier"/"sketch")` | 把这个画风的滤镜和图案注入 svg 的 `<defs>` |
| `House.twos(ease, dur)` | 一拍二缓动：元素按 12fps 跳着动，镜头保持 30fps 平滑 |
| `House.cam(tl, "#world", {cx,cy,s})` | 镜头：把世界坐标 (cx,cy) 放到画面中心、缩放 s。`.to({cx,cy,s}, dur, ease, at)` |
| `House.slap(tl, sel, t, {rot,y})` | 纸片落下：过冲再回正 |
| `House.pop(tl, sel, t, {origin, from})` | 角色从后面弹出来，挤压拉伸 |
| `House.flip(tl, sel, t, {origin})` | 书页 / 盖子绕铰链翻开 |
| `House.draw(tl, sel, t, dur)` | 线一笔笔画出来（path、ellipse、rect 都行） |
| `House.wipe(tl, sel, t, dur, {stagger})` | 从左往右显出来（手写字、荧光笔、清单） |
| `House.boil(tl, [filterId...], D)` | 每 2 帧换一次噪声 seed，铅笔线 / 胶片颗粒会微微颤 |
| `House.loop(tl, sel, D, {period, from, to})` | 背景小动作：冒气、叶子晃 |
| `House.blink(tl, eyesSel, t)` | 眨一次眼 |

## 4. 动作规矩（详见 `motion.md`）
- **元素一拍二，镜头平滑**。所有纸片、线条、手写都用 `House.twos` 包的缓动；`House.cam` 用普通缓动
- 镜头只在视线要去新地方时动；一个镜头最多一次快推（0.25–0.35 s），推进去之后要么停、要么拉远或横移，不要连推
- 2–4 秒必须有一个新变化，但同一时刻只有一个主角在动；背景小动作一直在
- 入场 0.3–0.4 s，退场约 0.18 s；落定后至少停 0.5 s
- 画面上的字是口播的提炼（≤12 字），不是字幕再抄一遍

## 5. 摆位和图层（实测踩过的坑）
- **"从桌子后面冒出来"**：角色要画在桌子**之前**（SVG 里先画的在下面），桌子盖住角色下半身
- **手臂要画在书之后**（在书上面），否则手像插在书里
- **SVG 滤镜区域**：线条加滤镜时，默认滤镜区域按几何外框算、不含描边，粗线会被切成方块。滤镜一律写 `filterUnits="userSpaceOnUse" x="-50" y="-50" width="1540" height="1180"`（kit 里的都已经这样写）
- **绝对定位的包裹层要给宽高**（用 class `full`），否则里面没设宽度的纸条会被挤成一个字一行的竖条
- **标注跟着真实文字走**：红圈、箭头、荧光笔用 `getBoundingClientRect()` 在建时间轴**之前**量好再放（`dossier-doc.html` 有示例）。不要按肉眼估坐标
- 要被镜头推近的画面，细节要经得起 1.4 倍放大：字号 ≥ 24px，线宽 ≥ 3px
- **挪角色不要靠套 `translate`**：模板里助理的 `svgOrigin` 是按世界坐标写死的，外面再套一层 translate 之后旋转中心会错。要挪位置，改 `#world` 里整组的坐标并同步改 `svgOrigin`，或者改用 `transformOrigin:"50% 100%"`（按元素自身外框算，不受外层影响）
- **手里拿道具**：手臂按 0°（自然下垂）画好，绕肩点 `svgOrigin` 旋转；道具画两份——一份在原位（工具板上），一份画在手里那一组里。交接那一帧原位那份 `autoAlpha:0`、手里那份 `autoAlpha:1`（用 `tl.set`，不要补间）。放下同理反过来
- **快推不能把反应推出画面**：推镜要推到一个具体东西上，但取景必须保住此刻在做反应的角色（笑、点头、惊讶）。画面可见的世界范围是 `cx ± 720/s`、`cy ± 540/s`，推之前算一下角色的脸在不在里面
- **量坐标要在 `House.cam` 之前**：`House.cam` 一建就给 `#world` 加了初始镜头变换，之后再 `getBoundingClientRect()` 量到的是被缩放过的屏幕坐标，拿去当世界坐标会整体偏
- **带滤镜的线不要放在缩放过的 `<g>` 里**：`userSpaceOnUse` 的滤镜区域按元素自己的局部坐标算，`<g transform="scale()">` 里的小路径（坐标在 0 附近）会被切掉一半，红圈变成一道弧。滤镜挂在外层不缩放的 `<g>` 上，或者干脆用 JS 算好屏幕坐标直接写 `d`（可将屏幕坐标计算封装成独立的辅助函数）
- **别用 `vector-effect="non-scaling-stroke"` 配 `House.draw`**：虚线长度会按屏幕算、`getTotalLength()` 按局部算，对不上，没画之前线就露出一截
- 颗粒、暗角放在 `#world` 外面，不跟着镜头缩放

## 6. 渲染与自检
```bash
./tools/render.sh X                 # -> renders/X.mp4 + renders/sheets/X.jpg（12 帧联系表）
./tools/frames.sh X 0.5 2 3.5 5.8   # 指定时间点的帧（960×720，2 张一行）-> renders/.frames/
./tools/still.sh X 3.2              # 单帧
```
每个镜头渲完都要看：
1. 联系表——动作顺序对不对、有没有哪一段完全没动
2. 关键时间点的原尺寸帧——字有没有被挡、手指有没有指对、东西有没有出界
3. 用看图模型检查时**先裁出局部，再指定要核对的内容**：`./tools/crop.sh X 3.2 600 300 400 300` → `renders/crops/`。避免只对整张图做开放式检查；模型可能臆测并不存在的边缘、遮挡或接触问题
4. **缝隙、接触、出界这类几何问题不要问看图模型**，取像素：`python3 tools/pixel.py X 3.2 812,440 812,446 812,452`，沿两件东西之间的线采几个点，有一个是背景色就是有缝。看图模型在这类问题上实测会连续两轮报错
   - 镜头在动时，世界坐标换屏幕坐标：`屏幕x = 720 - cx*s + x*s`，`屏幕y = 540 - cy*s + y*s`
5. 对照 `anti-ai-look.md` 过一遍

## 7. 风格样张（G2）
样张就是把镜头渲一遍取一帧：`./tools/still.sh X 5.5`。不要另外写一份静态 html，否则样张和成片会对不上。
拼对比图：`python3 $SK/scripts/look_sheet.py look/options.png A=... B=... C=...`
