#!/bin/bash
# Stage 5 lookdev: 5 stills per shot (first, mid-action, pre-payoff, payoff, last) + a contact sheet per shot.
cd "$(dirname "$0")/../.." && . .venv/bin/activate
RES=${RES:-240x426}; SPP=${SPP:-8}
for s in ${SHOTS:-S01 S02 S03 S04 S05 S06 S07 S08 S09 S10 S11 S12 S13 S14 S15 S16 S17 S18 S19 S20 S21 S22 S23 S24}; do
  N=$(python -c "import json;print(next(x['frames'] for x in json.load(open('manifests/p02_audio_timing.json'))['shots'] if x['id']=='$s'))")
  rm -rf renders/P02/$s/stills
  python tools/p02/build.py --shot $s --res $RES --samples $SPP --stills 1,$((N/4)),$((N/2)),$((3*N/4)),$N 2>&1 | grep -E "^\[|Error|Traceback|line [0-9]" 
  ffmpeg -loglevel error -y -pattern_type glob -i "renders/P02/$s/stills/*.png" -filter_complex tile=5x1 -frames:v 1 renders/P02/$s/lookdev_$s.png
done
