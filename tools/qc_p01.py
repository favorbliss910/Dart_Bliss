"""Objective QC for shot P01, measured from the saved .blend (no rendering needed).

1. Parallax: project near/mid/far anchor points through the animated camera at frames 1/60/120
   and report screen-space displacement. Genuine 3D parallax => near layer moves much more than far.
2. Foot sliding: during each stance window the planted boot must not move in world XY.
3. Ground contact: lowest boot point vs. sidewalk top (z = 0) - detects floating/penetration.

Usage: python tools/qc_p01.py renders/proof_v1/proof_scene.blend
"""
import json
import os
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
blend = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "renders/proof_v1/proof_scene.blend")
bpy.ops.wm.open_mainfile(filepath=blend)
scene = bpy.context.scene
cam = scene.camera
W, H = scene.render.resolution_x, scene.render.resolution_y

ANCHORS = {
    "near": {"lamp_near_pole": Vector((3.6, 0.28, 1.2)), "bollard": Vector((2.55, 0.42, 0.6))},
    "mid": {"shop_window_center": Vector((0.45, 1.5, 1.15)), "hydrant": Vector((-1.6, 0.42, 0.4))},
    "far": {"far_block_5": Vector((-30.0, 3.0, 5.0)), "lamp_far_4_bulb": Vector((-29.0, 0.88, 3.05))},
}


def project(p, f):
    scene.frame_set(f)
    v = world_to_camera_view(scene, cam, p)
    return {"x_px": round(v.x * W, 1), "y_px": round((1 - v.y) * H, 1), "depth_m": round(v.z, 2), "in_front": v.z > 0}


parallax = {}
for layer, pts in ANCHORS.items():
    for name, p in pts.items():
        a, b = project(p, 1), project(p, 60)
        c = project(p, 120)
        parallax[name] = {
            "layer": layer,
            "f1": a, "f60": b, "f120": c,
            "screen_shift_f1_f60_px": round(((b["x_px"] - a["x_px"]) ** 2 + (b["y_px"] - a["y_px"]) ** 2) ** 0.5, 1),
            "screen_shift_f60_f120_px": round(((c["x_px"] - b["x_px"]) ** 2 + (c["y_px"] - b["y_px"]) ** 2) ** 0.5, 1),
        }
# camera orientation also changes, so compare RELATIVE motion: near vs far over the same interval
near_shift = max(v["screen_shift_f1_f60_px"] for v in parallax.values() if v["layer"] == "near")
far_shift = max(v["screen_shift_f1_f60_px"] for v in parallax.values() if v["layer"] == "far")

# foot slide + contact
events = json.load(open(os.path.join(ROOT, "manifests", "p01_animation_events.json")))
contacts = events["footstep_contacts"]
slides, min_z = [], {}
for side in ("L", "R"):
    boot = bpy.data.objects[f"pip_boot_{side}"]
    mine = [c["frame"] for c in contacts if c["foot"] == side]
    for i, cf in enumerate(mine):
        # stance lasts until lift-off; build_proof_scene.py lifts a foot at next_own - min(STEP=8, gap)
        nxt = mine[i + 1] if i + 1 < len(mine) else None
        end = 120 if nxt is None else nxt - min(8, nxt - cf)
        if end <= cf:
            continue
        pos = []
        for f in range(cf, end + 1):
            scene.frame_set(f)
            pos.append(boot.matrix_world.translation.copy())
            bb = [boot.matrix_world @ Vector(c) for c in boot.bound_box]
            min_z.setdefault(side, []).append(min(v.z for v in bb))
        drift = max(((p - pos[0]).to_2d().length for p in pos))
        slides.append({"foot": side, "contact_frame": cf, "stance_end": end, "max_xy_drift_mm": round(drift * 1000, 2)})

report = {
    "blend": os.path.relpath(blend, ROOT),
    "resolution": [W, H],
    "parallax": parallax,
    "parallax_ratio_near_over_far_f1_f60": round(near_shift / max(far_shift, 1e-3), 2),
    "parallax_pass": near_shift > 3 * far_shift,
    "foot_slide": slides,
    "foot_slide_max_mm": max(s["max_xy_drift_mm"] for s in slides),
    "foot_slide_pass": max(s["max_xy_drift_mm"] for s in slides) < 2.0,
    "boot_min_z_mm": {k: round(min(v) * 1000, 1) for k, v in min_z.items()},
    "ground_contact_pass": all(-5 <= min(v) * 1000 <= 8 for v in min_z.values()),
}
os.makedirs(os.path.join(ROOT, "benchmark"), exist_ok=True)
with open(os.path.join(ROOT, "benchmark", "p01_qc_metrics.json"), "w") as fh:
    json.dump(report, fh, indent=2)
print(json.dumps({k: v for k, v in report.items() if k != "parallax"}, indent=2))
for n, v in parallax.items():
    print(f"{v['layer']:>4} {n:<20} shift f1->f60 {v['screen_shift_f1_f60_px']:>7}px  f60->f120 {v['screen_shift_f60_f120_px']:>7}px  depth f1 {v['f1']['depth_m']}m")
