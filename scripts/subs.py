#!/usr/bin/env python3
"""cues.json -> transparent subtitle strip work/subs.mov (W x 240, ARGB), overlaid by assemble.py at subs_y.

usage: subs.py <project> [--w 1440] [--font "/path/font.otf"] [--size 44]
Plain white text with a dark outline, no animation, no punctuation (house rule).
"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
P = os.path.abspath(sys.argv[1])
arg = lambda k, v: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else v
W, SIZE = int(arg('--w', 1440)), int(arg('--size', 44)); SH = 240
CANDS = [arg('--font', ''), os.environ.get('LDD_CJK_FONT', '')]
font = None
for c in CANDS:
    if c and os.path.exists(c):
        try: font = ImageFont.truetype(c, SIZE, index=0); break
        except Exception: pass
if font is None:
    try:
        out = subprocess.run(['fc-match', '-f', '%{file}', 'sans:lang=zh'], capture_output=True, text=True, check=True).stdout.strip()
        if not out or not os.path.isfile(out): raise OSError('fontconfig did not return an installed CJK font')
        font = ImageFont.truetype(out, SIZE)
    except (FileNotFoundError, subprocess.CalledProcessError, OSError):
        sys.exit('no CJK font found; install a CJK font or set LDD_CJK_FONT')
cues = json.load(open(os.path.join(P, 'work/cues.json')))
d = os.path.join(P, 'work/subs'); os.makedirs(d, exist_ok=True)
blank = os.path.join(d, 'blank.png'); Image.new('RGBA', (W, SH), (0, 0, 0, 0)).save(blank)
lst, t = [], 0.0
for i, (a, b, txt) in enumerate(cues):
    txt = txt.strip('，。！？、；：,.!?;: ')
    if a > t: lst.append((blank, a - t))
    im = Image.new('RGBA', (W, SH), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    tw = dr.textlength(txt, font=font)
    dr.text(((W - tw) / 2, SH / 2 - SIZE * 0.62), txt, font=font, fill=(255, 255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0, 170))
    f = os.path.join(d, f'{i:03d}.png'); im.save(f); lst.append((f, b - a)); t = b
lst.append((blank, 1.0))
with open(os.path.join(d, 'list.txt'), 'w') as fh:
    for f, du in lst: fh.write(f"file '{f}'\nduration {max(du, 0.034):.3f}\n")
    fh.write(f"file '{blank}'\n")
subprocess.check_call(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', os.path.join(d, 'list.txt'),
                       '-vf', 'fps=30,format=argb', '-c:v', 'qtrle', os.path.join(P, 'work/subs.mov')])
print(f'{len(cues)} cues -> work/subs.mov ({W}x{SH})')
