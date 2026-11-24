#!/usr/bin/env python3
"""Assemble a talking-head knowledge video from an edit list.

usage: assemble.py <project>/edit/edl.json [out.mp4]

edl.json (paths relative to <project>):
{
  "W": 1440, "H": 1080, "total": 36.0, "snap": 1.6,
  "face":  "work/face.mp4",          # speaker, already cropped to W x H
  "voice": "footage/talk.mp4",       # source of the audio (the original recording)
  "bed":   "audio/bed.wav",          # optional music bed
  "bed_gain": 0.20,
  "subs":  "work/subs.mov", "subs_y": 820,   # optional ARGB subtitle strip
  "pip": { "card": [900, 680, 500, 40], "circle": [220, 40, 820],
           "face_crop": "600:600:420:80", "ring": "#3A7D68" },
  "clips": [ {"name": "OPEN", "file": "animation/renders/intro.mp4", "start": 2.0, "mode": "cover"},
             {"name": "DETAIL", "file": "animation/renders/detail.mp4", "start": 10.0, "mode": "pip"},
             {"name": "CUT", "file": "work/k-01.mp4", "start": 20.0, "mode": "cover", "subs_shift": [296, -96]},  # K cut-out (cutout_compose.py)
             {"name": "CLOSE", "file": "animation/renders/close.mp4", "start": 30.0, "mode": "end"} ]   # end = outro card, same as cover
}

What it guarantees:
- gaps shorter than `snap` between clips are bridged by holding the previous clip's last
  frame, so the speaker never flashes through for a few frames
- consecutive pip clips share one card + face circle; 0.2s fade only where the group
  borders the full-frame speaker, hard cut where it borders a full-frame clip
- VO loudnorm I=-16, bed ducked by sidechain; only the bed fades out (2.5s) — the speaker's last words are never faded
"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter

edl_path = os.path.abspath(sys.argv[1])
P = os.path.dirname(os.path.dirname(edl_path))
e = json.load(open(edl_path))
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(P, 'edit', 'draft.mp4')
FF, FP = 'ffmpeg', 'ffprobe'
W, H, T = e.get('W', 1440), e.get('H', 1080), e['total']
SNAP, FADE = e.get('snap', 1.6), 0.2
ab = lambda p: p if os.path.isabs(p) else os.path.join(P, p)
dur = lambda f: float(subprocess.check_output([FP, '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]))

pip = e.get('pip', {})
CW, CH, CX, CY = pip.get('card', [round(W * .76), round(H * .76), W - round(W * .76) - 40, 40])
D, PX, PY = pip.get('circle', [round(H * .222), 40, 40 + round(H * .76) - round(H * .222)])
FACE_CROP = pip.get('face_crop', f'{H}:{H}:{(W - H) // 2}:0')
ring = pip.get('ring', '#FF8C42').lstrip('#'); ring = tuple(int(ring[i:i + 2], 16) for i in (0, 2, 4))

# ---- pip plates
pd = os.path.join(P, 'edit', 'pip'); os.makedirs(pd, exist_ok=True)
m = Image.new('L', (CW, CH), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, CW - 1, CH - 1), radius=22, fill=255); m.save(f'{pd}/card_mask.png')
s = Image.new('L', (D * 4, D * 4), 0); ImageDraw.Draw(s).ellipse((0, 0, D * 4 - 1, D * 4 - 1), fill=255); s.resize((D, D), Image.LANCZOS).save(f'{pd}/circle_mask.png')
bg = e.get('pip_bg', '#141210').lstrip('#'); bg = tuple(int(bg[i:i + 2], 16) for i in (0, 2, 4))
pl = Image.new('RGBA', (W, H), bg + (255,))
sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(sh)
d.rounded_rectangle((CX, CY + 10, CX + CW, CY + CH + 10), radius=22, fill=(0, 0, 0, 170))
d.ellipse((PX - 2, PY + 8, PX + D + 2, PY + D + 10), fill=(0, 0, 0, 190))
pl = Image.alpha_composite(pl, sh.filter(ImageFilter.GaussianBlur(22)))
r = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(r)
dr.rounded_rectangle((CX - 1, CY - 1, CX + CW, CY + CH), radius=23, outline=(242, 235, 224, 40), width=2)
dr.ellipse((PX - 4, PY - 4, PX + D + 3, PY + D + 3), outline=ring + (230,), width=4)
Image.alpha_composite(pl, r).save(f'{pd}/plate.png')

# ---- clips, bridging
cl = sorted(e['clips'], key=lambda c: c['start'])
clips = []
for i, c in enumerate(cl):
    f = ab(c['file']); d_ = dur(f); st = c['start']
    nxt = cl[i + 1]['start'] if i + 1 < len(cl) else None
    # butt-joined clips (gap 0) also get a hold: float rounding at the seam otherwise lets one speaker frame through
    hold = max(0.0, nxt - (st + d_)) + 0.1 if nxt is not None and nxt - (st + d_) < SNAP else 0.0
    clips.append(dict(n=c['name'], st=st, d=d_, hold=hold, end=st + d_ + hold, f=f, pip=c.get('mode') == 'pip',
                      shift=c.get('subs_shift')))

groups = []
for c in clips:
    if not c['pip']: continue
    if groups and c['st'] - groups[-1]['end'] < SNAP:
        groups[-1]['clips'].append(c); groups[-1]['end'] = max(groups[-1]['end'], c['end'])
    else:
        groups.append(dict(st=c['st'], end=c['end'], clips=[c]))
for g in groups:
    for c in clips:
        if not c['pip'] and g['st'] < c['st'] < g['end']: g['end'] = c['st']

# ---- inputs
args = [FF, '-v', 'error', '-y', '-i', ab(e['face']), '-i', ab(e['voice'])]
has_bed, has_subs = bool(e.get('bed')), bool(e.get('subs'))
args += ['-i', ab(e['bed'])] if has_bed else ['-f', 'lavfi', '-t', str(T), '-i', 'anullsrc=r=48000:cl=stereo']
args += ['-i', ab(e['subs'])] if has_subs else ['-f', 'lavfi', '-t', str(T), '-i', f'color=c=black@0:s={W}x4,format=rgba']
for p_ in ('plate', 'card_mask', 'circle_mask'):
    args += ['-loop', '1', '-t', str(T), '-framerate', '30', '-i', f'{pd}/{p_}.png']
k = 7; idx = {}
for c in clips: args += ['-i', c['f']]; idx[c['n']] = k; k += 1

G = max(len(groups), 1); NM = max(sum(len(g['clips']) for g in groups), 1)
fc = [f'[0:v]tpad=stop_mode=clone:stop_duration=10,trim=0:{T},setpts=PTS-STARTPTS,format=yuv420p,split={1 + len(groups)}[b0]' + ''.join(f'[fs{j}]' for j in range(len(groups))),
      f'[4:v]format=rgba,split={G}' + ''.join(f'[pl{j}]' for j in range(G)),
      f'[5:v]format=gray,split={NM}' + ''.join(f'[cm{j}]' for j in range(NM)),
      f'[6:v]format=gray,split={G}' + ''.join(f'[ccm{j}]' for j in range(G))]
cur = 'b0'
for c in clips:
    if c['pip']: continue
    i = idx[c['n']]
    fc.append(f"[{i}:v]scale={W}:{H},tpad=stop_mode=clone:stop_duration={c['hold']:.3f},setpts=PTS-STARTPTS+{c['st']}/TB[c{i}]")
    fc.append(f"[{cur}][c{i}]overlay=enable='between(t,{c['st']},{c['end'] - 0.001:.3f})':eof_action=pass[o{i}]"); cur = f'o{i}'
mi = 0
for j, g in enumerate(groups):
    gd = g['end'] - g['st']
    fc.append(f"[pl{j}]trim=0:{gd:.3f},setpts=PTS-STARTPTS[g{j}_0]"); gc = f'g{j}_0'
    for c in g['clips']:
        i = idx[c['n']]; rs = c['st'] - g['st']; re_ = min(c['end'], g['end']) - g['st']
        fc.append(f"[{i}:v]tpad=stop_mode=clone:stop_duration={c['hold']:.3f},scale={CW}:{CH},format=rgba[s{i}]")
        fc.append(f"[s{i}][cm{mi}]alphamerge,setpts=PTS-STARTPTS+{rs:.3f}/TB[r{i}]"); mi += 1
        fc.append(f"[{gc}][r{i}]overlay={CX}:{CY}:enable='between(t,{rs:.3f},{re_ - 0.001:.3f})':eof_action=pass[g{j}_{i}]"); gc = f'g{j}_{i}'
    fc.append(f"[fs{j}]trim={g['st']}:{g['end']:.3f},setpts=PTS-STARTPTS,crop={FACE_CROP},scale={D}:{D},format=rgba[fc{j}]")
    fc.append(f"[fc{j}][ccm{j}]alphamerge[fm{j}]")
    fin = not any(abs(c['end'] - g['st']) < 0.3 for c in clips if not c['pip'])
    fout = not any(abs(c['st'] - g['end']) < 0.3 for c in clips if not c['pip'])
    fades = (f"fade=t=in:st=0:d={FADE}:alpha=1," if fin else '') + (f"fade=t=out:st={gd - FADE:.3f}:d={FADE}:alpha=1," if fout else '')
    fc.append(f"[{gc}][fm{j}]overlay={PX}:{PY}:eof_action=pass,{fades}setpts=PTS-STARTPTS+{g['st']}/TB[gg{j}]")
    fc.append(f"[{cur}][gg{j}]overlay=enable='between(t,{g['st']},{g['end'] - 0.001:.3f})':eof_action=pass[go{j}]"); cur = f'go{j}'
if not groups:                        # no pip clip in this edit: the split plates still need a sink
    fc.append('[pl0]nullsink;[cm0]nullsink;[ccm0]nullsink')
# per-clip "subs_shift": [dx, dy] moves the subtitle strip while that clip plays (K cut-out shots: captions sit under the card)
sx, sy = '0', str(e.get('subs_y', 840))
for c in clips:
    if c['shift']:
        w_ = f"between(t,{c['st']},{c['end'] - 0.001:.3f})"
        sx = f"if({w_},{c['shift'][0]},{sx})"; sy = f"if({w_},{e.get('subs_y', 840) + c['shift'][1]},{sy})"
fc.append(f"[{cur}][3:v]overlay=x='{sx}':y='{sy}':eof_action=pass,format=yuv420p[vout]")
fc.append(f'[1:a]aresample=48000,loudnorm=I=-16:TP=-1.5:LRA=11,apad,atrim=0:{T}[vo]')
fc.append('[vo]asplit[vo1][vo2]')
fc.append(f"[2:a]aresample=48000,atrim=0:{T},volume={e.get('bed_gain', 0.22)},afade=t=out:st={T - 2.5}:d=2.5[bed]")
fc.append('[bed][vo2]sidechaincompress=threshold=0.03:ratio=6:attack=40:release=600[bd]')
fc.append(f'[vo1][bd]amix=inputs=2:duration=first:normalize=0,afade=t=out:st={T - 0.12}:d=0.12[aout]')  # only the bed fades; the last words play in full

for c in clips: print(f"{c['n']:12} {c['st']:7.2f}-{c['end']:7.2f} hold={c['hold']:.2f} {'pip' if c['pip'] else 'cover'}")
for g in groups: print('pip group', round(g['st'], 2), round(g['end'], 2), [c['n'] for c in g['clips']])
args += ['-filter_complex', ';'.join(fc), '-map', '[vout]', '-map', '[aout]', '-t', str(T),
         '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', out]
subprocess.run(args, check=True); print('done', out)
