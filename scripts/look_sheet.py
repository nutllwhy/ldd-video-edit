#!/usr/bin/env python3
"""Tile 2-4 style frames into one comparison sheet for the G2 look check.

usage: look_sheet.py out.png A=look/a.png B=look/b.png [C=look/c.png D=look/d.png]

Labels go on the sheet only (top-left badge), never into the style frames.
Each frame is scaled to 960 px wide; 2 frames -> 1x2, 3-4 frames -> 2x2.
"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

out, items = sys.argv[1], [a.split('=', 1) for a in sys.argv[2:]]
assert 2 <= len(items) <= 4, 'give 2-4 frames'
ims = []
for lab, p in items:
    im = Image.open(p).convert('RGB'); w = 960; h = round(im.height * w / im.width)
    ims.append((lab, im.resize((w, h), Image.LANCZOS)))
cols = 2; rows = 1 if len(ims) == 2 else 2
W, H, G = 960, max(i.height for _, i in ims), 16
sheet = Image.new('RGB', (cols * W + (cols + 1) * G, rows * H + (rows + 1) * G), (24, 24, 24))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cjkfont
font_path, font_idx = cjkfont.find()
try:
    f = ImageFont.truetype(font_path, 44, index=font_idx) if font_path and os.path.isfile(font_path) else ImageFont.load_default()
except Exception:
    f = ImageFont.load_default()
d = ImageDraw.Draw(sheet)
for k, (lab, im) in enumerate(ims):
    x = G + (k % cols) * (W + G); y = G + (k // cols) * (H + G)
    sheet.paste(im, (x, y))
    d.rounded_rectangle((x + 16, y + 16, x + 88, y + 84), radius=12, fill=(255, 255, 255))
    d.text((x + 52, y + 50), lab, font=f, fill=(20, 20, 20), anchor='mm')
sheet.save(out); print('wrote', out, sheet.size)
