#!/usr/bin/env python3
"""顶部章节条：逐帧 RGBA PNG，叠在画面最上方。

usage: chapter_bar.py <out_dir> <total_sec> <fps> <width> '<chapters json>'
  chapters: [[0, "开场"], [12.5, "拉片分析"], [40, "上手剪辑"], [70, "总结"]]   # 起始秒 + 名字，最多 5 段

画法（rules.md L10）：
- 每段等宽，读起来像目录，不像时间轴；段名居中在自己那段条的正上方
- 当前段：名字加粗高亮，条用强调色往前走；讲完的段：条变白；没讲到的：暗灰
- 只用在讲解结构清楚、有 3–5 个章节的片子上；不是默认元素
也可以在 Python 里 import 后调用 render(...)。
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFont

ACC = (255, 90, 31, 255)          # #FF5A1F
INK = (245, 245, 242)             # #F5F5F2


def fonts(size):
    """返回 (加粗, 常规)，字体查找见 cjkfont.py。"""
    import cjkfont
    (b, bi), (r, ri) = cjkfont.find(bold=True), cjkfont.find()
    if not r: sys.exit('no CJK font found; set LDD_CJK_FONT')
    return ImageFont.truetype(b, int(size * 1.06), index=bi), ImageFont.truetype(r, size, index=ri)


def render(out, T, fps, W, chapters, acc=ACC, k=None, t0=0.0, dur=None, total=None):
    """T = 整条片子的时长（决定最后一段的终点）；t0/dur 只渲片子里的一段窗口，帧号从 1 开始。"""
    os.makedirs(out, exist_ok=True)
    T = total or T
    dur = T - t0 if dur is None else dur
    k = k or W / 1080                              # 以 1080 宽为基准等比
    H = int(180 * k)
    X0, X1, GAP = 48 * k, W - 48 * k, 10 * k
    TRACK_Y, TRACK_H, LABEL_Y = 132 * k, max(4, round(8 * k)), 70 * k
    f_on, f_off = fonts(round(30 * k))
    ch = sorted(chapters)
    starts = [c[0] for c in ch] + [T]
    segw = (X1 - X0 - GAP * (len(ch) - 1)) / len(ch)
    n = int(round(dur * fps))
    for i in range(n):
        t = t0 + i / fps
        im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        for j, (s, name) in enumerate(ch):
            e = starts[j + 1]
            x = X0 + j * (segw + GAP)
            cur = s <= t < e
            r = TRACK_H / 2
            d.rounded_rectangle([x, TRACK_Y, x + segw, TRACK_Y + TRACK_H], r, fill=(255, 255, 255, 60))
            p = 1 if t >= e else (0 if t < s else (t - s) / (e - s))
            if p > 0:
                d.rounded_rectangle([x, TRACK_Y, x + max(TRACK_H, segw * p), TRACK_Y + TRACK_H], r,
                                    fill=acc if cur else INK + (255,))
            d.text((x + segw / 2, LABEL_Y), name, font=f_on if cur else f_off,
                   fill=INK + ((255,) if cur else (120,)), anchor='mt')
        im.save(f'{out}/{i + 1:05d}.png')
    return n, H


if __name__ == '__main__':
    if len(sys.argv) < 6: sys.exit(__doc__)
    n, h = render(sys.argv[1], float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), json.loads(sys.argv[5]))
    print('bar frames', n, 'height', h)
