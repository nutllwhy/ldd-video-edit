#!/usr/bin/env bash
# contact sheet: N evenly spaced frames (default 8) tiled 4 wide, with timestamps
set -euo pipefail
cd "$(dirname "$0")/.."
name="$1"; n="${2:-8}"
f="renders/$name.mp4"; d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
tmp="renders/.sheet_tmp/$name"; mkdir -p "$tmp"; find "$tmp" -name '*.png' -delete
for i in $(seq 0 $((n-1))); do
  t=$(python3 -c "print(round(($i+0.5)*$d/$n,2))")
  ffmpeg -v error -y -ss "$t" -i "$f" -frames:v 1 -vf "scale=720:540" "$tmp/$(printf %02d $i).png"
done
cols=4; rows=$(( (n+cols-1)/cols ))
ffmpeg -v error -y -pattern_type glob -i "$tmp/*.png" -vf "tile=${cols}x${rows}:padding=6:color=gray" -frames:v 1 "renders/sheets/$name.jpg"
echo "renders/sheets/$name.jpg"
