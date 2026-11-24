#!/usr/bin/env python3
"""抠像版式：把口播里的人抠出来、加贴纸描边，叠在素材卡片前面，背后垫磨砂面板，顶部可选章节条。

  竖屏 VK（1080×1920）：素材卡在上，人在下方偏左，人背后一块圆角磨砂面板
  横屏 K （1440×1080）：素材卡在右上，人在左下，人背后一块圆角磨砂面板

usage: cutout_compose.py <project>/edit/cutout-01.json [out.mp4]

配置（路径相对 <project>）：
{
  "orient": "vertical",                 # vertical = VK，landscape = K
  "fps": 30,
  "speaker": "footage/talk.mp4", "speaker_in": 20.0,
  "speaker_crop": null,                 # 可选 "w:h:x:y"（原片像素），取一个以人为中心的正方形；默认取画面中间的正方形
  "screen": "footage/screen.mp4", "screen_in": 2.0,   # 录屏、网页、成片；也可以是一张图片
  "dur": 8.0,
  "chapters": [[0, "开场"], [12, "拉片分析"], [40, "上手剪辑"], [70, "总结"]],   # 可选；时间是整条片子的时间
  "film_t0": 12.0, "film_total": 90.0,  # 这一段在整条片子里从第几秒开始、整条片子多长（章节条用）
  "stroke": {"color": "#F5F5F2", "px": 11},           # 描边颜色与最终粗细（像素）
  "person": {"size": 820, "face_x": 0.28, "top": 1170},   # 可选，覆盖默认站位
  "audio": false                        # true = 带上口播原声，方便单独预览；进 assemble 时保持 false
}

输出是一条无字幕的画面段。竖屏放进 assemble_vertical.py 的 clips（mode "bare"，并写 "subs_y" 让字幕落在卡片和面板之间）；
横屏放进 assemble.py 的 clips（mode "cover"）。仅支持 macOS 14+（人像分割用系统 Vision）。
"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import chapter_bar  # noqa: E402

SQ = 1080   # 抠像在 1080 正方形上做，最后再缩放

LAYOUT = {
    'vertical': dict(W=1080, H=1920, bar_k=1.0,
                     card=dict(x=40, w=1000, y=190, y_nobar=120, max_h=760, r=22),
                     panel=(32, 1000, 1048, 1888), panel_r=44,
                     person=dict(size=820, face_x=0.28, top=1170)),
    'landscape': dict(W=1440, H=1080, bar_k=0.8,
                      card=dict(x=520, w=880, y=150, y_nobar=60, max_h=560, r=20),
                      panel=(28, 440, 496, 1052), panel_r=36,     # 面板和卡片左右错开，不在角上叠
                      person=dict(size=580, face_x=0.18, top=520)),
}


def sh(cmd, **kw):
    subprocess.run(cmd, check=True, **kw)


def probe(f, entries):
    out = subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', entries,
                                   '-of', 'csv=p=0', f], text=True).strip().split('\n')[0]
    return out.split(',')


def fg_tool():
    """编译 scripts/cutout/fg_mask.swift，缓存到 ~/.cache/ldd-video-edit/。"""
    src = os.path.join(HERE, 'cutout', 'fg_mask.swift')
    cache = os.path.expanduser('~/.cache/ldd-video-edit'); os.makedirs(cache, exist_ok=True)
    exe = os.path.join(cache, 'fg_mask')
    if os.path.exists(exe) and os.path.getmtime(exe) >= os.path.getmtime(src): return exe
    cmd = ['xcrun', 'swiftc', '-O', src, '-o', exe]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 and os.path.isdir('/Applications/Xcode.app'):
        # Command Line Tools 和 Xcode 的 SDK 模块冲突时（redefinition of module 'SwiftBridging'），改用 Xcode 的工具链
        env = dict(os.environ, DEVELOPER_DIR='/Applications/Xcode.app/Contents/Developer')
        r = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if r.returncode != 0: sys.exit('swiftc failed:\n' + r.stderr[-2000:])
    return exe


def stroke(mask_dir, out_dir, px_src):
    """时间平滑 → 收边（去掉发丝里残留的原背景色）→ 圆角外扩得到描边蒙版。逐帧滑窗，不整段进内存。"""
    os.makedirs(f'{out_dir}/m', exist_ok=True); os.makedirs(f'{out_dir}/s', exist_ok=True)
    fs = sorted(f for f in os.listdir(mask_dir) if f.endswith('.png'))
    load = lambda i: Image.open(os.path.join(mask_dir, fs[min(max(i, 0), len(fs) - 1)])).convert('L')
    choke = [0 if v < 100 else 255 if v > 200 else int((v - 100) * 2.55) for v in range(256)]
    win = [load(-1), load(0), load(1)]
    for i, n in enumerate(fs):
        m = Image.blend(win[1], Image.blend(win[0], win[2], .5), .4)
        m = m.point(choke).filter(ImageFilter.GaussianBlur(.8))
        m.save(f'{out_dir}/m/{n}')
        b = m.point(lambda v: 255 if v > 128 else 0)
        s = b.filter(ImageFilter.GaussianBlur(px_src * .45)).point(lambda v: 255 if v > 12 else 0)
        s = s.filter(ImageFilter.GaussianBlur(2.2)).point(lambda v: 255 if v > 128 else 0)
        s.filter(ImageFilter.GaussianBlur(.9)).save(f'{out_dir}/s/{n}')
        win = [win[1], win[2], load(i + 2)]
    return fs


def head_anchor(mdir, fs):
    """在几帧蒙版上量头的位置：返回 (头顶 y, 头中心 x)，坐标在 1080 正方形里。"""
    tops, xs = [], []
    for n in fs[:: max(1, len(fs) // 8)]:
        m = Image.open(os.path.join(mdir, n)).point(lambda v: 255 if v > 128 else 0)
        bb = m.getbbox()
        if not bb: continue
        y0 = bb[1]; band = m.crop((0, y0, SQ, min(SQ, y0 + int(SQ * .18)))).getbbox()
        if band: tops.append(y0); xs.append((band[0] + band[2]) / 2)
    if not tops: sys.exit('no person found in the speaker footage; check speaker_crop')
    tops.sort(); xs.sort()
    return tops[len(tops) // 2], xs[len(xs) // 2]


def main():
    cfg_path = os.path.abspath(sys.argv[1]); P = os.path.dirname(os.path.dirname(cfg_path))
    c = json.load(open(cfg_path))
    ab = lambda p: p if os.path.isabs(p) else os.path.join(P, p)
    name = os.path.splitext(os.path.basename(cfg_path))[0]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(P, 'work', f'{name}.mp4')
    L = LAYOUT[c.get('orient', 'vertical')]; W, H = L['W'], L['H']
    fps, dur = c.get('fps', 30), float(c['dur'])
    pers = dict(L['person'], **c.get('person', {}))
    st = dict(dict(color='#F5F5F2', px=11), **c.get('stroke', {}))
    wd = os.path.join(P, 'work', 'cutout', name)
    for d in ('src', 'mask', 'bar', 'plate', 'st/m', 'st/s'):          # 重跑时清掉上一次的帧，免得段变短后尾部残留旧帧
        p = os.path.join(wd, d); os.makedirs(p, exist_ok=True)
        for f in os.listdir(p):
            if f.endswith('.png'): os.remove(os.path.join(p, f))

    # 1. 口播取正方形，逐帧
    crop = c.get('speaker_crop') or 'ih:ih:(iw-ih)/2:0'
    sh(['ffmpeg', '-loglevel', 'error', '-y', '-ss', str(c.get('speaker_in', 0)), '-t', str(dur), '-i', ab(c['speaker']),
        '-vf', f'crop={crop},scale={SQ}:{SQ},fps={fps}', f'{wd}/src/%05d.png'])
    if c.get('audio'):
        sh(['ffmpeg', '-loglevel', 'error', '-y', '-ss', str(c.get('speaker_in', 0)), '-t', str(dur), '-i', ab(c['speaker']),
            '-vn', '-c:a', 'aac', f'{wd}/a.m4a'])
    # 2. 抠像 + 描边
    sh([fg_tool(), f'{wd}/src', f'{wd}/mask'])
    fs = stroke(f'{wd}/mask', f'{wd}/st', st['px'] * SQ / pers['size'])
    top, hx = head_anchor(f'{wd}/st/m', fs)
    k = pers['size'] / SQ
    PX, PY = round(W * pers['face_x'] - hx * k), round(pers['top'] - top * k)
    # 3. 章节条
    has_bar = bool(c.get('chapters'))
    bar_h = 0
    if has_bar:
        total = float(c.get('film_total') or dur)
        _, bar_h = chapter_bar.render(f'{wd}/bar', total, fps, W, c['chapters'], k=L['bar_k'],
                                      t0=float(c.get('film_t0', 0)), dur=dur, total=total)
    # 4. 素材卡、面板
    cd = L['card']
    sw, shh = map(int, probe(ab(c['screen']), 'stream=width,height'))
    cw = cd['w']; ch = round(cw * shh / sw)
    if ch > cd['max_h']: ch = cd['max_h']; cw = round(ch * sw / shh)
    cw, ch = cw // 2 * 2, ch // 2 * 2
    cx = cd['x'] + (cd['w'] - cw) // 2; cy = cd['y'] if has_bar else cd['y_nobar']
    m = Image.new('L', (cw, ch), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, cw - 1, ch - 1), cd['r'], fill=255); m.save(f'{wd}/plate/card.png')
    pm = Image.new('L', (W, H), 0); ImageDraw.Draw(pm).rounded_rectangle(L['panel'], L['panel_r'], fill=255); pm.save(f'{wd}/plate/panel.png')
    pe = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(pe).rounded_rectangle(L['panel'], L['panel_r'], outline=(255, 255, 255, 46), width=2); pe.save(f'{wd}/plate/edge.png')

    # 5. 合成
    still = os.path.splitext(c['screen'])[1].lower() in ('.png', '.jpg', '.jpeg', '.webp')
    scr = (['-loop', '1', '-t', str(dur), '-i', ab(c['screen'])] if still
           else ['-ss', str(c.get('screen_in', 0)), '-t', str(dur), '-i', ab(c['screen'])])
    S = pers['size'] // 2 * 2
    inp = ['-framerate', str(fps), '-i', f'{wd}/src/%05d.png',
           '-framerate', str(fps), '-i', f'{wd}/st/m/%05d.png',
           '-framerate', str(fps), '-i', f'{wd}/st/s/%05d.png'] + scr + [
           '-loop', '1', '-i', f'{wd}/plate/panel.png', '-loop', '1', '-i', f'{wd}/plate/edge.png', '-loop', '1', '-i', f'{wd}/plate/card.png']
    if has_bar: inp += ['-framerate', str(fps), '-i', f'{wd}/bar/%05d.png']
    cover = f'scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}'
    fc = [f'[3]fps={fps},setsar=1,tpad=stop_mode=clone:stop_duration={dur},trim=0:{dur},split=3[r1][r2][r3]',
          f'[r1]{cover},gblur=sigma=60,eq=brightness=-0.32:saturation=0.7[bd]',
          f'[r2]{cover},gblur=sigma=18,eq=brightness=-0.14:saturation=0.8,drawbox=x=0:y=0:w=iw:h=ih:color=white@0.10:t=fill,format=rgba[fz]',
          '[4]format=gray[pm];[fz][pm]alphamerge[panel]',
          f'[r3]scale={cw}:{ch},format=rgba[rc];[6]format=gray[cm];[rc][cm]alphamerge[card]',
          f"color=c={st['color'].replace('#', '0x')}:s={SQ}x{SQ}:r={fps},format=rgba[sc];[2]format=gray[sm];[sc][sm]alphamerge,scale={S}:{S}[stroke]",
          f'[0]format=rgba[s0];[1]format=gray[mm];[s0][mm]alphamerge,scale={S}:{S}[person]',
          '[bd][panel]overlay=0:0:shortest=1[a0];[a0][5]overlay=0:0:shortest=1[a1]',
          f'[a1][card]overlay={cx}:{cy}[a2]',
          f'[a2][stroke]overlay={PX}:{PY}:shortest=1[a3];[a3][person]overlay={PX}:{PY}[a4]']
    fc.append('[a4][7]overlay=0:0,format=yuv420p[v]' if has_bar else '[a4]format=yuv420p[v]')
    cmd = ['ffmpeg', '-loglevel', 'error', '-y'] + inp
    if c.get('audio'): cmd += ['-i', f'{wd}/a.m4a']
    cmd += ['-filter_complex', ';'.join(fc), '-map', '[v]']
    if c.get('audio'): cmd += ['-map', f'{len([a for a in inp if a == "-i"])}:a', '-c:a', 'aac']
    cmd += ['-t', str(dur), '-r', str(fps), '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p', out]
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    sh(cmd)
    info = dict(out=out, size=[W, H], card=[cx, cy, cw, ch], person=[PX, PY, S], bar_h=bar_h)
    if c.get('orient', 'vertical') == 'vertical':
        info['subs_y'] = (cy + ch + L['panel'][1]) // 2          # 字幕落在卡片和面板之间，写进 vedl 那条 clip 的 "subs_y"
    else:
        zx = (L['panel'][2] + W - 28) // 2; zy = (cy + ch + H) // 2   # 卡片下方、面板右侧的空区
        info['subs_shift'] = [zx - W // 2, zy - 940]               # 写进 edl 那条 clip 的 "subs_shift"（subs.py 默认字幕中线 y=940）
        info['subs_max_w'] = W - 28 - L['panel'][2] - 40
    print(json.dumps(info, ensure_ascii=False))


if __name__ == '__main__':
    if len(sys.argv) < 2: sys.exit(__doc__)
    main()
