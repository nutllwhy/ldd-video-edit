#!/usr/bin/env bash
# frames.sh NAME t1 t2 ... -> renders/.frames/NAME_strip.png (each 960x720, 2 per row; hidden dir — look in renders/.frames/)
set -euo pipefail
cd "$(dirname "$0")/.."
name="$1"; shift; mkdir -p renders/.frames; inputs=(); i=0
for t in "$@"; do ffmpeg -v error -y -ss "$t" -i "renders/$name.mp4" -frames:v 1 -vf scale=960:720 "renders/.frames/${name}_$i.png"; inputs+=(-i "renders/.frames/${name}_$i.png"); i=$((i+1)); done
n=$i; layout=""; for k in $(seq 0 $((n-1))); do c=$((k%2)); r=$((k/2)); sep=""; if [ "$k" -gt 0 ]; then sep="|"; fi; layout+="${sep}$((c*960))_$((r*720))"; done
ffmpeg -v error -y "${inputs[@]}" -filter_complex "xstack=inputs=$n:layout=$layout:fill=gray" "renders/.frames/${name}_strip.png"
echo "$PWD/renders/.frames/${name}_strip.png"
