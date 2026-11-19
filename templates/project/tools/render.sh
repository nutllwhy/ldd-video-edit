#!/usr/bin/env bash
# render.sh NAME [NAME...] : compositions/NAME.html -> renders/NAME.mp4, then a 12-frame contact sheet
set -uo pipefail
cd "$(dirname "$0")/.."
mkdir -p .work renders/sheets
for n in "$@"; do
  perl -e 'alarm 900; exec @ARGV' npx --yes hyperframes@0.8.78 render -c "compositions/$n.html" -o "renders/$n.mp4" --quality high --quiet > ".work/render_$n.log" 2>&1 || { echo "FAIL $n (see .work/render_$n.log)"; tail -5 ".work/render_$n.log"; continue; }
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "renders/$n.mp4")
  echo "$n ${d}s"
  ./tools/sheet.sh "$n" 12
done
