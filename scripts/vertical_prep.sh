#!/usr/bin/env bash
# vertical_prep.sh <talk.mp4> <project_dir> [circle_mask.mp4] [x_shift]
# Cuts the three speaker tracks a 9:16 video needs (layouts.md):
#   work/v_full.mp4  1080x1920  VA  full-screen speaker (centre 9:16 crop of the talk)
#   work/v_sq.mp4    1080x1080  VH  square speaker for the lower half of a split screen
#   work/v_circ.mp4   600x600   VS  round avatar source
# circle_mask.mp4: the user's own export with the speaker already framed inside a circle on black.
#   The circle is found automatically (bounding box of non-black pixels in a frame) and its square is cut out.
#   Without it the round avatar is a centre square of the talk, zoomed OUT (head room, shoulders) — check v_circ_*.jpg.
# x_shift moves every crop horizontally (source px) when the speaker is not centred.
# Also writes work/voice.wav (48k) and the whisper transcript if work/voice16k.json is missing.
set -euo pipefail
SRC="$1"; P="$2"; MASK="${3:-}"; XS="${4:-0}"
mkdir -p "$P/work" "$P/edit" "$P/成片"
IFS=x read SW SH < <(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 "$SRC")
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$SRC")
ENC="-an -r 30 -c:v libx264 -crf 16 -preset medium -pix_fmt yuv420p -g 30"
ffmpeg -v error -y -i "$SRC" -vn -ac 2 -ar 48000 "$P/work/voice.wav"
if [ ! -f "$P/work/voice16k.json" ]; then
  ffmpeg -v error -y -i "$SRC" -vn -ac 1 -ar 16000 "$P/work/voice16k.wav"
  mlx_whisper "$P/work/voice16k.wav" --model mlx-community/whisper-large-v3-turbo --language zh \
    --word-timestamps True --output-format all --output-dir "$P/work" --output-name voice16k >/dev/null
fi
FW=$(( SH * 9 / 16 / 2 * 2 ))
ffmpeg -v error -y -i "$SRC" -vf "crop=$FW:$SH:($SW-$FW)/2+$XS:0,scale=1080:1920:flags=lanczos" $ENC "$P/work/v_full.mp4"
SQ=$(( SH * 3 / 4 / 2 * 2 ))
ffmpeg -v error -y -i "$SRC" -vf "crop=$SQ:$SQ:($SW-$SQ)/2+$XS:0,scale=1080:1080:flags=lanczos" $ENC "$P/work/v_sq.mp4"
if [ -n "$MASK" ]; then
  ffmpeg -v error -y -ss 5 -i "$MASK" -frames:v 1 "$P/work/_mask.png"
  read CX CY CS < <(python3 - "$P/work/_mask.png" <<'PY'
import sys
from PIL import Image
im = Image.open(sys.argv[1]).convert('L').point(lambda v: 255 if v > 24 else 0)
x0, y0, x1, y1 = im.getbbox(); s = min(x1 - x0, y1 - y0)
print(x0 + (x1 - x0 - s) // 2, y0 + (y1 - y0 - s) // 2, s)
PY
)
  echo "circle in mask: x=$CX y=$CY side=$CS"
  ffmpeg -v error -y -i "$MASK" -t "$DUR" -vf "crop=$CS:$CS:$CX:$CY,scale=600:600:flags=lanczos" $ENC "$P/work/v_circ.mp4"
else
  # zoomed-out square: whole height, so the head has room and the shoulders show
  ffmpeg -v error -y -i "$SRC" -vf "crop=$SH:$SH:($SW-$SH)/2+$XS:0,scale=600:600:flags=lanczos" $ENC "$P/work/v_circ.mp4"
fi
for t in 5 30 60; do
  for k in full sq circ; do ffmpeg -v error -y -ss $t -i "$P/work/v_$k.mp4" -frames:v 1 -vf scale=-2:480 "$P/work/v_${k}_$t.jpg" 2>/dev/null || true; done
done
echo "done. look at work/v_*_*.jpg: face centred, head room in the circle, nothing cut."
