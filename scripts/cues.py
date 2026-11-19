#!/usr/bin/env python3
"""Whisper json -> subtitle cues (work/cues.json), with a fix table.

usage: cues.py <project> [--max 20]
  reads  work/voice16k.json  (mlx_whisper, word timestamps if available)
         work/fixes.tsv      optional, one "wrong<TAB>right" per line (names, products, terms)
  writes work/cues.json      [[start, end, "text"], ...]  no punctuation at line ends, <= max chars
"""
import json, os, re, sys
P = os.path.abspath(sys.argv[1]); MAX = int(sys.argv[sys.argv.index('--max') + 1]) if '--max' in sys.argv else 20
d = json.load(open(os.path.join(P, 'work/voice16k.json')))
fixes = []
fp = os.path.join(P, 'work/fixes.tsv')
if os.path.exists(fp):
    for ln in open(fp, encoding='utf-8'):
        if '\t' in ln:
            a, b = ln.rstrip('\n').split('\t', 1); fixes.append((a, b))
def fix(s):
    for a, b in fixes: s = s.replace(a, b)
    return s
PUN = '，。！？、；：,.!?;:'
def chars_with_time(seg):
    """[(char, t)] — word timestamps if present, else spread evenly over the segment."""
    ws = seg.get('words') or []
    out = []
    if ws:
        for w in ws:
            txt = w['word'].strip(); n = max(1, len(txt))
            for i, ch in enumerate(txt):
                out.append((ch, w['start'] + (w['end'] - w['start']) * i / n))
        out.append(('', ws[-1]['end']))
    else:
        txt = seg['text'].strip(); n = max(1, len(txt))
        for i, ch in enumerate(txt):
            out.append((ch, seg['start'] + (seg['end'] - seg['start']) * i / n))
        out.append(('', seg['end']))
    return out
AFTER, BEFORE = '的了吗呢吧啊着过', '我你他她它这那就也都还然但所因如跟和把被给让在是去来用'
def best_cut(chars):
    n = len(chars); target = (n + 1) // 2 if n <= 2 * MAX else MAX
    lo, hi = max(4, n - MAX), min(MAX, n - 4)
    best, score = target, 99
    for i in range(lo, hi + 1):
        a, b = chars[i - 1][0], chars[i][0]
        ok = a in AFTER or b in BEFORE or (a.isascii() != b.isascii())
        if ok and abs(i - target) < score: best, score = i, abs(i - target)
    return best
cues = []
for seg in d['segments']:
    ct = chars_with_time(seg)
    # split at punctuation
    pieces, cur = [], []
    for ch, t in ct:
        if ch == '' or ch in PUN:
            if cur: pieces.append((cur, t))
            cur = []
        else:
            cur.append((ch, t))
    for chars, tend in pieces:
        # further split long pieces into <= MAX chars, preferring the middle
        while chars:
            take = len(chars) if len(chars) <= MAX else best_cut(chars)
            part, chars = chars[:take], chars[take:]
            end = chars[0][1] if chars else tend
            text = fix(''.join(c for c, _ in part)).strip()
            if text: cues.append([round(part[0][1], 2), round(end, 2), text])
# close tiny gaps so subtitles don't blink
for a, b in zip(cues, cues[1:]):
    if 0 < b[0] - a[1] < 0.3: a[1] = b[0]
json.dump(cues, open(os.path.join(P, 'work/cues.json'), 'w'), ensure_ascii=False, indent=0)
long = [c for c in cues if len(c[2]) > MAX]
print(f'{len(cues)} cues -> work/cues.json' + (f'  ({len(long)} still > {MAX} chars, split by hand)' if long else ''))
