#!/usr/bin/env bash
# Scaffold <project>/animation with the house kit + render tools.
#   usage: new_animation.sh <project_dir> [template ...]
#   templates: paper-manual dossier-doc sketch-notebook (copied into compositions/ as starting points)
set -euo pipefail
SK="$(cd "$(dirname "$0")/.." && pwd)"
P="$1"; shift || true
A="$P/animation"
mkdir -p "$A"/{compositions,assets/shots,assets/media,kit,renders/sheets,renders/crops,tools,.work}
mkdir -p "$P"/{look,edit,work,audio,成片}
[ -f "$P/plan.md" ] || printf "# 逐句方案\n\n| 时间 | 口播句 | 处理 A/B/P/C | 画风 A/B/D | 画面 | 理由 |\n|---|---|---|---|---|---|\n" > "$P/plan.md"
cp "$SK/kit/gsap.min.js" "$A/assets/gsap.min.js"
cp "$SK/kit/house.js" "$SK/kit/house.css" "$A/kit/"
cp "$SK/templates/project/hyperframes.json" "$SK/templates/project/package.json" "$A/"
cp "$SK/templates/project/tools/"* "$A/tools/"; chmod +x "$A/tools/"*
for t in "$@"; do cp "$SK/templates/shots/$t.html" "$A/compositions/$t.html"; done
echo "$A"
