#!/usr/bin/env python3
"""Assemble a 9:16 talking-head video (layouts.md: VA / VS / VH).

usage: assemble_vertical.py <project>/edit/vedl.json [out.mp4]

vedl.json (paths relative to <project>):
{
  "total": 24.0, "snap": 1.6,
  "full":   "work/v_full.mp4",      # VA speaker 1080x1920 (vertical_prep.sh)
  "square": "work/v_sq.mp4",        # VH lower half 1080x1080
  "circ":   "work/v_circ.mp4",      # VS round avatar source, square
  "voice":  "work/voice.wav",
  "music":  null,                   # or {"file": "audio/bed.wav", "gain": 0.2}   rules S3: ask first
  "cues":   "work/cues.json",       # [[start, end, "text"], ...]  "/" = forced line break in VS
  "circle": [310, 44, 1250],        # diameter, x, y
  "seam":   840,                    # VH: footage above, square speaker below
  "subs_y": 1430,                   # optional: VA/bare subtitle centre y
  "push":   [[19.2, 0.2, 1.06, 19.8]],   # optional punch-in on VA: [t, ramp, scale, until]
  "clips":  [ {"file": "anim/renders/shot-01.mp4", "start": 0,  "mode": "vs"},
              {"file": "anim/renders/shot-02.mp4", "start": 6, "mode": "vh"},     # 1080x840
              {"file": "anim/renders/shot-04.mp4", "start": 19, "mode": "bare"},     # full screen, no avatar
              {"file": "work/vk-01.mp4", "start": 22, "mode": "bare", "subs_y": 864} ]  # VK cut-out from cutout_compose.py
}
Clip duration = the file's duration (or "dur"). Anywhere no clip plays is VA.

What it guarantees (rules.md):
- gaps shorter than `snap` are bridged by holding the previous clip's last frame; touching clips also hold 0.1 s (E1)
- VS clips get the round avatar; VH clips get the square speaker under the seam; cuts between layouts are hard (L5)
- subtitles: VA centred at y~1430, VS to the right of the avatar (wrapped, <= 940 px), VH centred on the seam (L8)
- voice loudnorm I=-16; music only if given, ducked, and only the music fades; the voice is never faded (S2)
"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

edl = os.path.abspath(sys.argv[1]); P = os.path.dirname(os.path.dirname(edl))
e = json.load(open(edl))
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(P, 'edit', 'draft.mp4')
W, H, T, SNAP = 1080, 1920, e['total'], e.get('snap', 1.6)
D, CXP, CYP = e.get('circle', [310, 44, 1250]); RING = 6
SEAM = e.get('seam', 840)
SUBY = e.get('subs_y', 1430)        # VA / bare subtitle centre line; raise it when MG shots need the lower third
ab = lambda p: p if os.path.isabs(p) else os.path.join(P, p)
dur = lambda f: float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cjkfont
FONT, FIDX = cjkfont.find()
if not FONT or not os.path.exists(FONT): sys.exit('no CJK font found; install a CJK font or set LDD_CJK_FONT')

clips = sorted(e['clips'], key=lambda c: c['start'])
for c in clips:
    c['d'] = c.get('dur') or dur(ab(c['file']))
    assert c['mode'] in ('vs', 'vh', 'bare'), c
# bridge gaps (E1)
for i, c in enumerate(clips):
    nxt = clips[i + 1]['start'] if i + 1 < len(clips) else None
    c['hold'] = 0.0
    if nxt is not None:
        gap = nxt - (c['start'] + c['d'])
        if gap < -0.05: print(f'WARN overlap {c["file"]} runs {-gap:.2f}s into the next clip')
        if gap < SNAP: c['hold'] = max(0.0, gap) + 0.1
    c['end'] = c['start'] + c['d'] + c['hold']
    if nxt is not None: c['end'] = min(c['end'], nxt + 0.1)

def mode_at(t):
    for c in reversed(clips):          # latest clip wins: the previous clip's hold frame is only a bridge
        if c['start'] - 1e-3 <= t < c['end']: return c['mode']
    return 'va'
def suby_at(t):                         # per-clip "subs_y" (e.g. VK cut-out shots keep captions off the face)
    for c in reversed(clips):
        if c['start'] - 1e-3 <= t < c['end']: return c.get('subs_y', SUBY)
    return SUBY

# ---- subtitles
fbig, fsm = ImageFont.truetype(FONT, 66, index=FIDX), ImageFont.truetype(FONT, 58, index=FIDX)
MAXW = 940 - (CXP + D + 26)
def wrap(txt):
    if '/' in txt: return txt.split('/')
    if fsm.getbbox(txt)[2] <= MAXW: return [txt]
    n = len(txt); best = None
    for k in range(3, n - 2):
        a, b = txt[:k], txt[k:]
        if fsm.getbbox(a)[2] > MAXW: break
        score = abs(len(a) - len(b)) + (0 if a[-1] in '的了吗呢吧着过，' or b[0] in '我你他她它这那就也都还但和把被给在是' else 3)
        if best is None or score < best[0]: best = (score, k)
    k = best[1] if best else n // 2
    return [txt[:k]] + wrap(txt[k:])
def render_cue(i, txt, m, suby=None):
    suby = SUBY if suby is None else suby
    big = m in ('va', 'vh', 'bare')
    f = fbig if big else fsm; lh = 84 if big else 78; st = 9
    lines = [txt.replace('/', '')] if big else wrap(txt)
    lw = max(f.getbbox(l)[2] for l in lines) + st * 2 + 8
    im = Image.new('RGBA', (lw, lh * len(lines) + st * 2 + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for j, l in enumerate(lines):
        x = (lw - f.getbbox(l)[2]) // 2 if big else st + 4
        d.text((x, st + j * lh), l, font=f, fill='#FFFFFF', stroke_width=st, stroke_fill='#111111')
    fn = os.path.join(P, f'edit/vsubs/c{i:03d}.png'); im.save(fn)
    if m == 'vh': x, y = (W - lw) // 2, SEAM - im.height // 2
    elif big: x, y = (W - lw) // 2, suby - im.height // 2
    else: x, y = CXP + D + 26, CYP + D // 2 - im.height // 2
    if lw > W - 80 or (not big and x + lw > 940): print(f'WARN cue {i} too wide ({lw}px): {txt}')
    return fn, x, y

# ---- avatar plates
os.makedirs(os.path.join(P, 'edit/vsubs'), exist_ok=True)
m = Image.new('L', (D * 4, D * 4), 0); ImageDraw.Draw(m).ellipse((0, 0, D * 4 - 1, D * 4 - 1), fill=255)
k = int(D * 0.012); cm = Image.new('L', (D, D), 0); cm.paste(m.resize((D - 2 * k, D - 2 * k), Image.LANCZOS), (k, k))
cm.save(os.path.join(P, 'edit/v_circle.png'))
o = 30; R = D + 2 * RING + 2 * o
sh = Image.new('L', (R, R), 0); ImageDraw.Draw(sh).ellipse((o, o + 12, o + D + 2 * RING, o + D + 2 * RING + 12), fill=150)
ring = Image.merge('RGBA', (Image.new('L', (R, R), 0),) * 3 + (sh.filter(ImageFilter.GaussianBlur(14)),))
bg = Image.new('RGBA', (R * 4, R * 4), (0, 0, 0, 0))
ImageDraw.Draw(bg).ellipse((o * 4, o * 4, (o + D + 2 * RING) * 4, (o + D + 2 * RING) * 4), fill='#FFFFFF')
ring.alpha_composite(bg.resize((R, R), Image.LANCZOS)); ring.save(os.path.join(P, 'edit/v_ring.png'))

# ---- filter graph
inp = ['-i', ab(e['full']), '-i', ab(e['circ']), '-i', ab('edit/v_circle.png'), '-i', ab('edit/v_ring.png'), '-i', ab(e['voice'])]
k = 5
fc = [f"[0:v]tpad=stop_mode=clone:stop_duration=0.5,trim=0:{T},setpts=PTS-STARTPTS[b0]"]
cur = 'b0'
for j, (t0, ramp, sc, until) in enumerate(e.get('push', [])):
    zw, zh = int(W * sc) // 2 * 2, int(H * sc) // 2 * 2
    fc.append(f"[0:v]tpad=stop_mode=clone:stop_duration=0.5,trim=0:{T},setpts=PTS-STARTPTS,scale={zw}:{zh},crop={W}:{H}:{(zw - W) // 2}:{int((zh - H) * 0.3)}[zp{j}]")
    fc.append(f"[{cur}][zp{j}]overlay=0:0:enable='between(t,{t0},{until})'[pb{j}]"); cur = f'pb{j}'
vh = [c for c in clips if c['mode'] == 'vh']
if vh:
    inp += ['-i', ab(e['square'])]; sqi = k; k += 1
    fc.append(f"[{sqi}:v]tpad=stop_mode=clone:stop_duration=0.5,split={len(vh)}" + ''.join(f'[sq{j}]' for j in range(len(vh))))
nv = 0
for j, c in enumerate(clips):
    inp += ['-i', ab(c['file'])]
    # always pad 0.2 s past the enable window: a clip whose last frame lands a hair before `end`
    # would otherwise let the layer below show for one frame (found at a VH -> VA cut)
    pad = f",tpad=stop_mode=clone:stop_duration={c['hold'] + 0.2:.3f}"
    fc.append(f"[{k}:v]trim=0:{c['d']},setpts=PTS-STARTPTS{pad},setpts=PTS+{c['start']}/TB[s{j}]")
    en = f"between(t,{c['start']},{c['end'] - 0.001:.3f})"
    fc.append(f"[{cur}][s{j}]overlay=0:0:enable='{en}':eof_action=pass[o{j}]"); cur = f'o{j}'; k += 1
    if c['mode'] == 'vh':
        fc.append(f"[{cur}][sq{nv}]overlay=0:{SEAM}:enable='{en}'[q{j}]"); cur = f'q{j}'; nv += 1
on = '+'.join(f"between(t,{c['start']},{c['end'] - 0.001:.3f})" for c in clips if c['mode'] == 'vs')
if on:
    fc.append(f"[1:v]tpad=stop_mode=clone:stop_duration=0.5,scale={D}:{D},format=rgba[fq];[2:v]format=gray[cm];[fq][cm]alphamerge[fcirc]")
    fc.append(f"[{cur}][3:v]overlay={CXP - RING - o}:{CYP - RING - o}:enable='{on}'[r1]")
    fc.append(f"[r1][fcirc]overlay={CXP}:{CYP}:enable='{on}'[r2]"); cur = 'r2'
cues = json.load(open(ab(e['cues']))) if e.get('cues') else []
for i, (a, b, txt) in enumerate(cues):
    fn, x, y = render_cue(i, txt, mode_at(a + 0.01), suby_at(a + 0.01))
    inp += ['-i', fn]
    fc.append(f"[{cur}][{k}:v]overlay={x}:{y}:enable='between(t,{a:.3f},{b - 0.001:.3f})'[u{i}]"); cur = f'u{i}'; k += 1
fc.append(f"[{cur}]format=yuv420p[vout]")
fc.append(f"[4:a]aresample=48000,loudnorm=I=-16:TP=-1.5:LRA=11,apad,atrim=0:{T}[vo]")
mu = e.get('music')
if mu:
    inp += ['-i', ab(mu['file'])]
    fc.append(f"[vo]asplit[vo1][vsc]")
    fc.append(f"[{k}:a]aresample=48000,volume={mu.get('gain', 0.2)},apad,atrim=0:{T},afade=t=out:st={T - 2.5}:d=2.5[bd]")
    fc.append("[bd][vsc]sidechaincompress=threshold=0.03:ratio=6:attack=40:release=600[bdd]")
    fc.append(f"[vo1][bdd]amix=inputs=2:normalize=0,afade=t=out:st={T - 0.12}:d=0.12[aout]")
else:
    fc.append(f"[vo]afade=t=out:st={T - 0.12}:d=0.12[aout]")
open(os.path.join(P, 'edit/v_fc.txt'), 'w').write(';\n'.join(fc))
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
cmd = ['ffmpeg', '-v', 'error', '-y'] + inp + ['-filter_complex_script', os.path.join(P, 'edit/v_fc.txt'),
       '-map', '[vout]', '-map', '[aout]', '-t', str(T), '-r', '30', '-c:v', 'libx264', '-crf', '18', '-preset', 'medium',
       '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', out]
print(f'{len(clips)} clips, {len(cues)} cues -> {out}')
sys.exit(subprocess.run(cmd).returncode)
