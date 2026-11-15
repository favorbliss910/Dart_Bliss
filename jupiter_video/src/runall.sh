#!/bin/bash
cd "$(dirname "$0")"
N=$(python3 -c "import sys;sys.path.insert(0,'.');import render,math;print(math.ceil(render.END_T*60))" 2>/dev/null)
K=8; step=$(( (N + K - 1) / K ))
for i in $(seq 0 $((K-1))); do a=$((i*step)); b=$(( (i+1)*step )); [ $b -gt $N ] && b=$N; echo "$a $b ../out/seg/s$i.mp4"; done | xargs -P4 -L1 bash -c 'python3 render.py seg $0 $1 $2 > $2.log 2>&1 || echo FAIL $2'
echo DONE $N
