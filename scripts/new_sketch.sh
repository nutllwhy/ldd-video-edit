#!/usr/bin/env bash
# 搭一个手绘动画工程：<project>/anim/（画风菜单拷到 <project>/look/画风菜单.jpg，五种画风参考在 anim/_ref/styles/）
#   usage: new_sketch.sh <project_dir> [参考镜头 ...]
#   参考镜头：stick-sort steps-climb flow-money match-lines note-reaction egg-reveal paper-checklist（不写就全拷）
set -euo pipefail
SK="$(cd "$(dirname "$0")/.." && pwd)"; T="$SK/templates/sketch"
P="$1"; shift || true; A="$P/anim"
mkdir -p "$A"/{kit,assets,renders,_chk} "$P"/{look,edit,work,成片}
cp "$SK/kit/sk.js" "$SK/kit/gsap.min.js" "$SK/kit/stick.js" "$A/kit/"
cp "$T/assets/shot.png" "$A/assets/"
[ -f "$A/BRIEF.md" ] || sed "s#{{ANIM}}#$A#g; s#{{SK}}#$SK#g" "$T/BRIEF.md" > "$A/BRIEF.md"
mkdir -p "$A/_ref"
if [ $# -eq 0 ]; then cp "$T/shots/"*.html "$A/_ref/"; else for s in "$@"; do cp "$T/shots/$s.html" "$A/_ref/"; done; fi
mkdir -p "$A/_ref/styles"; cp "$T/styles/"*.html "$A/_ref/styles/"; rm -f "$A/_ref/styles/_demo.tpl.html"; cp "$T/styles/preview/menu.html" "$P/look/画风菜单.html"; cp "$T/styles/preview/"*.jpg "$P/look/"
# 参考镜头放 _ref/，但脚本路径按 anim/ 根目录写；复制到 anim/ 下再改
echo "$A"
