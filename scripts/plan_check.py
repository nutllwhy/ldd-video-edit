#!/usr/bin/env python3
"""G3 gate: check an edit list for flash frames and rhythm problems.

usage: plan_check.py <project>/edit/edl.json

FAIL  face sliver   : a face-visible gap shorter than `snap` between two clips
                      (assemble.py bridges gaps < snap automatically; this
                      catches gaps between snap and 1.5s that it won't bridge)
FAIL  overlap       : a clip starts before the previous one ends by > 0.5s
                      (usually an EDL typo)
WARN  long cover    : a cover clip longer than 8s
WARN  short cover   : a cover clip shorter than 3s
WARN  long face     : face-only stretch longer than 8s (excluding first/last 12s)
WARN  covers b2b    : more than 3 cover clips in a row with no face / pip between
FAIL  open/close    : first 1.5s or last 1.5s not on the speaker
"""
import json, os, subprocess, sys

edl_path = sys.argv[1]
P = os.path.dirname(os.path.dirname(os.path.abspath(edl_path)))
e = json.load(open(edl_path))
T = e['total']; snap = e.get('snap', 1.6)
FP = 'ffprobe'
def dur(f):
    return float(subprocess.check_output([FP, '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]))

clips = []
for c in e['clips']:
    f = c['file'] if os.path.isabs(c['file']) else os.path.join(P, c['file'])
    d = c.get('dur') or dur(f)
    clips.append(dict(name=c['name'], st=c['start'], end=c['start'] + d, d=d, mode=c.get('mode', 'cover')))
clips.sort(key=lambda c: c['st'])

fails, warns = [], []
prev_end, prev = 0.0, None
run = 0
for c in clips:
    gap = c['st'] - prev_end
    if prev is not None:
        if gap < -0.5:
            fails.append(f"overlap      {prev['name']} -> {c['name']}  {gap:+.2f}s")
        if snap <= gap < 1.5:
            fails.append(f"face sliver  {prev['name']} -> {c['name']}  {gap:.2f}s of face at {prev_end:.2f}")
        if gap >= 1.5 or c['mode'] == 'pip':
            run = 0
    if c['mode'] == 'cover':
        if c['d'] > 8.05: warns.append(f"long cover   {c['name']} {c['d']:.1f}s at {c['st']:.1f} — split into shots or cut back to face/pip")
        if c['d'] < 2.95: warns.append(f"short cover  {c['name']} {c['d']:.1f}s at {c['st']:.1f}")
        run += 1
        if run == 4: warns.append(f"covers b2b   4+ covers in a row ending {c['name']} at {c['st']:.1f}")
    if gap > 8 and prev_end > 12 and c['st'] < T - 12:
        warns.append(f"long face    {gap:.1f}s at {prev_end:.1f}–{c['st']:.1f} — add a B overlay or P")
    prev_end = max(prev_end, c['end']); prev = c

if clips and clips[0]['st'] < 1.5: fails.append('open/close   video does not open on the speaker')
if clips and max(c['end'] for c in clips if c['mode'] != 'end') > T - 1.5: fails.append('open/close   video does not close on the speaker')

cover_total = sum(c['d'] for c in clips if c['mode'] == 'cover')
pip_total = sum(c['d'] for c in clips if c['mode'] == 'pip')
print(f"total {T:.1f}s · cover {cover_total:.1f}s ({cover_total / T:.0%}) · pip {pip_total:.1f}s ({pip_total / T:.0%}) · face {T - cover_total - pip_total:.1f}s")
for w in warns: print('WARN ', w)
for f in fails: print('FAIL ', f)
print(f"{len(fails)} failed, {len(warns)} warnings")
sys.exit(1 if fails else 0)
