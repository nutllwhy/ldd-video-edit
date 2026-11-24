"""找一个真能显示中文的字体文件。顺序：LDD_CJK_FONT → macOS PingFang → fc-list 里声明支持中文的字体。

注意：`fc-match 'sans:lang=zh'` 在部分 macOS 上会返回 Verdana 这类不含中文的字体，字幕变成方块，所以不用它。
返回 (path, index)；index 用于 .ttc 字体集（PingFang：3 = SC Regular，11 = SC Semibold）。
"""
import glob, os, subprocess

PREFER = ('PingFang', 'Source Han Sans', 'Noto Sans CJK', 'Noto Sans SC', 'Hiragino Sans GB', 'STHeiti', 'Heiti', 'WenQuanYi', 'Microsoft YaHei')


def find(bold=False):
    env = os.environ.get('LDD_CJK_FONT_BOLD' if bold else 'LDD_CJK_FONT', '') or os.environ.get('LDD_CJK_FONT', '')
    if env and os.path.exists(env): return env, 0
    pf = glob.glob('/System/Library/AssetsV2/com_apple_MobileAsset_Font*/*/AssetData/PingFang.ttc')
    if pf: return pf[0], (11 if bold else 3)
    try:
        files = subprocess.check_output(['fc-list', ':lang=zh', 'file'], stderr=subprocess.DEVNULL, text=True).split('\n')
        files = [f.split(':')[0].strip() for f in files if f.strip()]
        for p in PREFER:
            for f in files:
                if p.replace(' ', '').lower() in os.path.basename(f).replace(' ', '').lower(): return f, 0
        if files: return files[0], 0
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    for f in ('/System/Library/Fonts/STHeiti Medium.ttc', '/System/Library/Fonts/Hiragino Sans GB.ttc'):
        if os.path.exists(f): return f, 0
    return '', 0
