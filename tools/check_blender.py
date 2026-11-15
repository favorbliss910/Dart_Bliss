"""Blender capability check + headless smoke render (V3 page 003).

Usage:  python tools/check_blender.py [out_dir]
Runs with the `bpy` PyPI module (Blender-as-a-module). Prints version, engines,
Cycles devices and renders a 12-frame 360x640 cube/floor/area-light/moving-camera test.
"""
import json
import os
import sys
import time

import bpy

out_dir = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "renders/smoke")
os.makedirs(out_dir, exist_ok=True)

report = {"bpy_version": bpy.app.version_string, "build_platform": bpy.app.build_platform.decode()}
report["render_engines"] = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] + ["CYCLES (add-on)"]

prefs = bpy.context.preferences.addons["cycles"].preferences
devices = {}
for dev_type in ("CUDA", "OPTIX", "HIP", "ONEAPI", "METAL"):
    try:
        prefs.compute_device_type = dev_type
        prefs.get_devices()
        devices[dev_type] = [d.name for d in prefs.devices if d.type == dev_type]
    except TypeError:
        devices[dev_type] = "unsupported in this build"
report["cycles_gpu_devices"] = devices

# ---- smoke scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
bpy.ops.mesh.primitive_plane_add(size=10)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5))
cube = bpy.context.object
bpy.ops.object.light_add(type="AREA", location=(2, -2, 3))
light = bpy.context.object
light.data.energy = 400
light.data.size = 2
light.rotation_euler = (0.8, 0, 0.8)
bpy.ops.object.camera_add(location=(4, -6, 2.5))
cam = bpy.context.object
scene.camera = cam
con = cam.constraints.new("TRACK_TO")
con.target = cube
for f, x in ((1, 4.0), (12, -1.0)):
    cam.location.x = x
    cam.keyframe_insert("location", frame=f)
scene.world = bpy.data.worlds.new("w")
scene.world.color = (0.05, 0.05, 0.06)

scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 16
scene.render.resolution_x, scene.render.resolution_y = 360, 640
scene.frame_start, scene.frame_end = 1, 12
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = os.path.join(out_dir, "smoke_")
blend_path = os.path.join(out_dir, "smoke_scene.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_path)

t0 = time.time()
bpy.ops.render.render(animation=True)
elapsed = time.time() - t0
frames = sorted(f for f in os.listdir(out_dir) if f.startswith("smoke_") and f.endswith(".png"))
report.update(
    test_scene=blend_path,
    smoke_frames_written=len(frames),
    smoke_render_seconds=round(elapsed, 2),
    smoke_seconds_per_frame=round(elapsed / max(1, len(frames)), 3),
    smoke_pass=len(frames) == 12,
)
print(json.dumps(report, indent=2))
with open(os.path.join(out_dir, "check_blender.json"), "w") as fh:
    json.dump(report, fh, indent=2)
