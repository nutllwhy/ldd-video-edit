#!/usr/bin/env bash
# prep.sh <talk.mp4> <project_dir> [W] [H] [x_shift]
# 1) work/voice16k.wav  2) whisper transcript with word timestamps (work/voice16k.{json,srt,txt})
# 3) work/face.mp4: speaker cropped to W x H (default 1440x1080, 4:3), x_shift moves the crop (px in source)
set -euo pipefail
SRC="$1"; P="$2"; W="${3:-1440}"; H="${4:-1080}"; XS="${5:-0}"
mkdir -p "$P/work" "$P/footage" "$P/edit" "$P/audio" "$P/成片"
ffprobe -v error -show_entries stream=codec_type,width,height,r_frame_rate -show_entries format=duration -of compact "$SRC"
ffmpeg -v error -y -i "$SRC" -vn -ac 1 -ar 16000 "$P/work/voice16k.wav"
mlx_whisper "$P/work/voice16k.wav" --model mlx-community/whisper-large-v3-turbo --language zh \
  --word-timestamps True --output-format all --output-dir "$P/work" --output-name voice16k >/dev/null
# crop: keep full height, take a W:H window from the centre (+x_shift), then scale
ffmpeg -v error -y -i "$SRC" -an -vf "crop=ih*$W/$H:ih:(iw-ih*$W/$H)/2+$XS:0,scale=$W:$H:flags=lanczos,fps=30" \
  -c:v libx264 -crf 16 -preset medium -pix_fmt yuv420p "$P/work/face.mp4"
for t in 5 60 120; do ffmpeg -v error -y -ss $t -i "$P/work/face.mp4" -frames:v 1 -vf scale=480:-1 "$P/work/face_$t.jpg" 2>/dev/null || true; done
echo "done: $P/work/voice16k.txt (read it all), $P/work/face_*.jpg (check the crop keeps the face)"
