#!/bin/bash
# Usage: ./render_all.sh <project_dir> <out_dir> [segments=8] [parallel=4] [fps=60]
# Renders the whole timeline in parallel segments, then concatenates them (video only).
set -e
ENGINE="$(cd "$(dirname "$0")" && pwd)"
export JV_PROJECT="$(cd "$1" && pwd)"; OUT="$(mkdir -p "$2" && cd "$2" && pwd)"
K=${3:-8}; P=${4:-4}; FPS=${5:-60}
N=$(cd "$ENGINE" && python3 -c "import render,math;print(math.ceil(render.END_T*$FPS))" 2>/dev/null)
step=$(( (N + K - 1) / K ))
mkdir -p "$OUT/seg"; : > "$OUT/list.txt"
for i in $(seq 0 $((K-1))); do
  a=$((i*step)); b=$(( (i+1)*step )); [ $b -gt $N ] && b=$N
  echo "$a $b $OUT/seg/s$i.mp4"; echo "file 'seg/s$i.mp4'" >> "$OUT/list.txt"
done | (cd "$ENGINE" && xargs -P"$P" -L1 bash -c 'python3 render.py seg $0 $1 $2 '"$FPS"' > $2.log 2>&1 || echo FAIL $2')
ffmpeg -v error -y -f concat -safe 0 -i "$OUT/list.txt" -c copy "$OUT/video_only.mp4"
echo "DONE $N frames -> $OUT/video_only.mp4"
