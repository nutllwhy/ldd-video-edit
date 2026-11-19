#!/usr/bin/env bash
# crop.sh NAME T x y w h [scale]  -> renders/crops/NAME_T_x_y.png
# Coordinates are SCREEN pixels (1440x1080). World -> screen when House.cam is at {cx,cy,s}:
#   sx = 720 - cx*s + x*s ,  sy = 540 - cy*s + y*s   ; visible world range: cx ± 720/s , cy ± 540/s
set -euo pipefail
cd "$(dirname "$0")/.."
n="$1"; t="$2"; x="$3"; y="$4"; w="$5"; h="$6"; k="${7:-2}"; mkdir -p renders/crops
out="renders/crops/${n}_${t}_${x}_${y}.png"
ffmpeg -v error -y -ss "$t" -i "renders/$n.mp4" -frames:v 1 -vf "crop=$w:$h:$x:$y,scale=iw*$k:ih*$k:flags=neighbor" "$out"
echo "$out"
