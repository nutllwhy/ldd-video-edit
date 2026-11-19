#!/usr/bin/env bash
# still.sh NAME T : grab one exact frame at T seconds from renders/NAME.mp4 (renders first if missing)
set -euo pipefail
cd "$(dirname "$0")/.."
n="$1"; t="$2"; f="renders/$n.mp4"
[ -f "$f" ] || ./tools/render.sh "$n" >/dev/null
ffmpeg -v error -y -ss "$t" -i "$f" -frames:v 1 "renders/${n}_$t.png"; echo "$PWD/renders/${n}_$t.png"
