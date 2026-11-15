"""Build and render one P02 shot.

Usage:
  python tools/p02/build.py --shot S05 [--res 360x640] [--samples 16] [--stills 1,40,80 | --frames 1-104]
         [--out renders/P02] [--step 1] [--save-blend]

Frames go to <out>/<shot>/frames/####.png. Existing frames are skipped (restart-safe).
With --step 2 only every 2nd frame is rendered; assembly holds each rendered frame (animation "on twos").
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import bpy  # noqa: E402,F401

import lib  # noqa: E402
import shots  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--shot", required=True)
ap.add_argument("--res", default="360x640")
ap.add_argument("--samples", type=int, default=16)
ap.add_argument("--stills", default="")
ap.add_argument("--frames", default="")
ap.add_argument("--step", type=int, default=1)
ap.add_argument("--out", default="renders/P02")
ap.add_argument("--save-blend", action="store_true")
ap.add_argument("--no-render", action="store_true")
args = ap.parse_args(sys.argv[1:])

timing = json.load(open(os.path.join(ROOT, "manifests", "p02_audio_timing.json")))
sh = next(s for s in timing["shots"] if s["id"] == args.shot)
N = sh["frames"]
FPS = timing["fps"]
P = [1 + round(p["start_s"] * FPS) for p in sh["phrases"]]
E = [1 + round(p["end_s"] * FPS) for p in sh["phrases"]]

t0 = time.time()
scene = lib.reset(FPS)
scene.frame_start, scene.frame_end = 1, N
lib.build_materials()
lib.build_char_mats()
lib.build_lab()
lib.lab_lights()
shots.SHOTS[args.shot](N, P, E)
os.makedirs(os.path.join(ROOT, "manifests", "p02_events"), exist_ok=True)
json.dump({"shot": args.shot, "frames": N, "fps": FPS, "events": sorted(shots.EVENTS, key=lambda e: e["frame"])},
          open(os.path.join(ROOT, "manifests", "p02_events", f"{args.shot}.json"), "w"), indent=1)
OUT = os.path.join(ROOT, args.out, args.shot)
os.makedirs(os.path.join(OUT, "frames"), exist_ok=True)
lib.render_settings(args.res, args.samples, OUT)
print(f"[{args.shot}] built in {time.time() - t0:.1f}s, {N} frames", flush=True)
if args.save_blend:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "scene.blend"))
if args.no_render:
    sys.exit(0)

if args.stills:
    frames = [int(x) if x not in ("N", "last") else N for x in args.stills.split(",")]
    sub = "stills"
else:
    a, b = (int(x) for x in args.frames.split("-")) if args.frames else (1, N)
    frames = list(range(a, b + 1, args.step))
    if N not in frames and b == N:
        frames.append(N)
    sub = "frames"
os.makedirs(os.path.join(OUT, sub), exist_ok=True)
log_path = os.path.join(OUT, "render_timings.json")
log = json.load(open(log_path)) if os.path.exists(log_path) else {"frames": []}
for f in frames:
    path = os.path.join(OUT, sub, f"{f:04d}.png")
    if sub == "frames" and os.path.exists(path):
        continue
    scene.frame_set(f)
    scene.render.filepath = path
    t1 = time.time()
    bpy.ops.render.render(write_still=True)
    dt = round(time.time() - t1, 2)
    log["frames"].append({"frame": f, "seconds": dt, "res": args.res, "samples": args.samples, "kind": sub})
    print(f"[{args.shot}] {sub} {f} {dt}s", flush=True)
    json.dump(log, open(log_path, "w"), indent=1)
