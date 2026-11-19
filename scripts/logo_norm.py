#!/usr/bin/env python3
"""Normalise product logos to the same canvas and visual size (materials.md / rules M3).

usage: logo_norm.py <out_dir> a.png[:scale] b.svg.png[:scale] ... [--size 512] [--fill 0.94]

- a flat white or black background touching the corners is keyed out (only if the image has no alpha)
- trimmed to the alpha bbox, fitted into size x size at `fill` (x per-logo `scale`, e.g. square-logo.png:0.88)
- writes <out_dir>/<name>.png and <out_dir>/sheet.png (on dark and light, with a 4x edge crop) — look at it
"""
import os, sys
from PIL import Image, ImageDraw
args = [a for a in sys.argv[1:]]
def opt(k, d):
    if k in args: i = args.index(k); v = args[i + 1]; del args[i:i + 2]; return float(v)
    return d
S = int(opt('--size', 512)); FILL = opt('--fill', 0.94)
out, files = args[0], args[1:]; os.makedirs(out, exist_ok=True)
def key(im):
    im = im.convert('RGBA')
    if im.getextrema()[3][0] < 250: return im       # already has transparency
    px = im.load(); w, h = im.size; c = px[0, 0]
    if not all(abs(px[x, y][i] - c[i]) < 12 for x, y in ((w - 1, 0), (0, h - 1), (w - 1, h - 1)) for i in range(3)): return im
    ImageDraw.floodfill(im, (0, 0), (0, 0, 0, 0), thresh=40)
    for p in ((w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        if im.getpixel(p)[3]: ImageDraw.floodfill(im, p, (0, 0, 0, 0), thresh=40)
    return im
done = []
for spec in files:
    f, _, sc = spec.partition(':'); sc = float(sc or 1)
    im = key(Image.open(f)); im = im.crop(im.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox())
    side = S * FILL * sc; r = side / max(im.size)
    im = im.resize((max(1, round(im.width * r)), max(1, round(im.height * r))), Image.LANCZOS)
    cv = Image.new('RGBA', (S, S), (0, 0, 0, 0)); cv.alpha_composite(im, ((S - im.width) // 2, (S - im.height) // 2))
    n = os.path.splitext(os.path.basename(f))[0]; cv.save(os.path.join(out, n + '.png')); done.append((n, cv))
    print(f'{n}: {Image.open(f).size} -> {im.size} in {S}x{S}')
cell = 220; sheet = Image.new('RGBA', (cell * len(done), cell * 3), (0, 0, 0, 255))
for i, (n, cv) in enumerate(done):
    for row, bg in enumerate([(20, 20, 20, 255), (240, 238, 232, 255)]):
        tile = Image.new('RGBA', (cell, cell), bg); tile.alpha_composite(cv.resize((180, 180), Image.LANCZOS), (20, 20))
        sheet.paste(tile, (i * cell, row * cell))
    edge = cv.crop((0, S // 2 - 40, 80, S // 2 + 40)) if cv.getchannel('A').getbbox() else cv
    bb = cv.getchannel('A').getbbox(); x0 = bb[0]
    edge = cv.crop((x0, S // 2 - 27, x0 + 55, S // 2 + 28)).resize((cell, cell), Image.NEAREST)
    t = Image.new('RGBA', (cell, cell), (20, 20, 20, 255)); t.alpha_composite(edge); sheet.paste(t, (i * cell, 2 * cell))
sheet.convert('RGB').save(os.path.join(out, 'sheet.png')); print('sheet ->', os.path.join(out, 'sheet.png'))
