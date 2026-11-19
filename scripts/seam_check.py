#!/usr/bin/env python3
"""Frame-difference check around every cut (rules E2).

usage: seam_check.py <video.mp4> <edl.json | vedl.json | t1,t2,...> [--out dir]

For each cut time: decode 0.3 s before to 0.3 s after, mean abs difference between consecutive frames
(grayscale 108x192). A hard cut is ONE big jump. Two big jumps within 4 frames = a flash (something
showed for 1-3 frames). Prints a line per cut and exits 1 if any flash is found.
"""
import json, os, subprocess, sys, tempfile, glob
from PIL import Image, ImageChops, ImageStat
v = sys.argv[1]; arg = sys.argv[2]
if arg.endswith('.json'):
    e = json.load(open(arg)); ts = set()
    for c in e['clips']:
        f = c['file'] if os.path.isabs(c['file']) else os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(arg))), c['file'])
        d = c.get('dur') or float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]))
        ts.add(round(c['start'], 2)); ts.add(round(c['start'] + d, 2))
    ts = sorted(t for t in ts if 0.3 < t < e['total'] - 0.3)
else:
    ts = [float(x) for x in arg.split(',')]
BIG = 25.0; bad = 0
tmp = tempfile.mkdtemp()
for t in ts:
    for f in glob.glob(f'{tmp}/*.png'): os.remove(f)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{max(0, t - 0.3):.3f}', '-i', v, '-frames:v', '18',
                    '-vf', 'scale=108:192,format=gray', f'{tmp}/%02d.png'], check=True)
    fr = [Image.open(f) for f in sorted(glob.glob(f'{tmp}/*.png'))]
    df = [round(ImageStat.Stat(ImageChops.difference(a, b)).mean[0], 1) for a, b in zip(fr, fr[1:])]
    big = [i for i, x in enumerate(df) if x > BIG]
    flash = any(b - a <= 4 for a, b in zip(big, big[1:]))
    bad += flash
    print(f'{t:8.2f}s  {"FLASH" if flash else "ok   "}  jumps={len(big)}  {df}')
print(f'{len(ts)} cuts, {bad} flash')
sys.exit(1 if bad else 0)
