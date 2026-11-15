#!/bin/bash
# Stage 7: full render of every P02 shot (restart-safe: existing frames are skipped).
# RES/SPP/STEP default to the budgeted proof settings in docs/render_budget_P02.md.
cd "$(dirname "$0")/../.." && . .venv/bin/activate
RES=${RES:-360x640}; SPP=${SPP:-16}; STEP=${STEP:-2}
for s in ${SHOTS:-S01 S02 S03 S04 S05 S06 S07 S08 S09 S10 S11 S12 S13 S14 S15 S16 S17 S18 S19 S20 S21 S22 S23 S24}; do
  echo "=== $s $(date +%T)"
  python tools/p02/build.py --shot $s --res $RES --samples $SPP --step $STEP 2>&1 | grep -E "^\[|Error|Traceback|line [0-9]"
done
echo "=== ALL DONE $(date +%T)"
