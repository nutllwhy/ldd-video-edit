#!/usr/bin/env bash
# check_env.sh : tools + fonts this skill needs. Prints OK / MISSING per item.
ok(){ printf "  %-28s %s\n" "$1" "$2"; }
for b in ffmpeg ffprobe node npx mlx_whisper fc-list; do command -v $b >/dev/null && ok $b OK || ok $b MISSING; done
python3 -c "import PIL" 2>/dev/null && ok "python3 PIL" OK || ok "python3 PIL" "MISSING (pip install pillow)"
python3 -c "import numpy" 2>/dev/null && ok "python3 numpy (bed.py)" OK || ok "python3 numpy (bed.py)" "MISSING -> python3 -m venv .venv && .venv/bin/pip install numpy, then run bed.py with .venv/bin/python"
if [ -n "${CHROME:-}" ] && [ -x "$CHROME" ]; then
  ok "Chromium browser" OK
elif command -v chromium >/dev/null || command -v google-chrome >/dev/null || command -v chromium-browser >/dev/null; then
  ok "Chromium browser" OK
else
  ok "Chromium browser" "MISSING (install Playwright Chromium or set CHROME)"
fi
echo "fonts:"
for f in "TsangerYuMo" "HanziPen SC" "Hannotate SC" "YouSheBiaoTiHei" "Source Han Sans CN" "PingFang SC"; do
  fc-list : family | grep -q "$f" && ok "$f" OK || ok "$f" "MISSING (style will fall back to a default font)"
done
