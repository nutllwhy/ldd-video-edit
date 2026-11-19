#!/usr/bin/env python3
"""pixel.py NAME T x1,y1 [x2,y2 ...]  -> prints RGB at each screen point of frame T.
Use this (not the vision model) to settle gaps / contact / out-of-frame questions:
sample along the line between two parts; if any sample is background colour, there is a gap."""
import sys, subprocess, io
from PIL import Image
n, t, *pts = sys.argv[1:]
png = subprocess.run(["ffmpeg","-v","error","-ss",t,"-i",f"renders/{n}.mp4","-frames:v","1","-f","image2pipe","-vcodec","png","-"],capture_output=True,check=True,cwd=__import__("os").path.join(__import__("os").path.dirname(__file__),"..")).stdout
im = Image.open(io.BytesIO(png)).convert("RGB")
for p in pts:
    x, y = map(int, p.split(",")); print(p, "#%02X%02X%02X" % im.getpixel((x, y)))
