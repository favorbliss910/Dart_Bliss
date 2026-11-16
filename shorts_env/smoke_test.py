"""End-to-end check of the Shorts toolchain: Eevee frames -> voice -> -14 LUFS mp4.

Run: /opt/shorts/venv/bin/python shorts_env/smoke_test.py [out_dir]
"""
import math
import os
import subprocess
import sys
import time

import bpy

out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "smoke_out")
os.makedirs(out, exist_ok=True)
FPS, FRAMES = 30, 6

s = bpy.context.scene
s.render.engine = "BLENDER_EEVEE"
s.render.resolution_x, s.render.resolution_y = 720, 1280
s.render.fps = FPS
s.eevee.taa_render_samples = 24
s.render.use_motion_blur = True
s.frame_start, s.frame_end = 1, FRAMES

cube = bpy.data.objects["Cube"]
for f in (1, FRAMES):
    cube.rotation_euler.z = math.radians(8 * (f - 1))
    cube.keyframe_insert("rotation_euler", frame=f)

times = []
for f in range(1, FRAMES + 1):
    s.frame_set(f)
    s.render.filepath = os.path.join(out, f"f_{f:04d}.png")
    t = time.time()
    bpy.ops.render.render(write_still=True)
    times.append(time.time() - t)

wav = os.path.join(out, "voice.wav")
subprocess.run(["espeak-ng", "-w", wav, "The toolchain works."], check=True)

mp4 = os.path.join(out, "smoke.mp4")
subprocess.run(
    ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS),
     "-i", os.path.join(out, "f_%04d.png"), "-i", wav,
     "-af", "loudnorm=I=-14:TP=-1:LRA=11,apad", "-shortest",
     "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "48000", mp4],
    check=True,
)

steady = sorted(times[1:])[len(times[1:]) // 2]
print(f"blender {bpy.app.version_string}")
print(f"first frame {times[0]:.1f}s, steady {steady:.1f}s/frame (trivial scene)")
print(f"=> a 60 s Short (1800 frames) is at least {steady * 1800 / 3600:.1f} h on this machine")
print(f"wrote {mp4}")
