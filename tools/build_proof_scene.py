"""Build the 5-second 3D proof shot "LAST STOP" (shot P01) entirely in bpy.

Original content: a small rounded courier ("Pip") walks through a rainy night street
toward the camera, stops at a corner shop, turns, and looks up as the shop's OPEN sign
flickers on. All geometry, materials, animation and camera moves are procedural.

Usage:
  python tools/build_proof_scene.py --out renders/proof_v1 [--res 540x960] [--samples 32]
        [--frames 1-120 | --stills 1,40,80,120] [--no-render]

Writes: <out>/proof_scene.blend, <out>/frames/####.png, manifests/p01_animation_events.json
"""
import argparse
import json
import math
import os
import random
import sys
import time

import bpy  # noqa: E402  (bpy must load before bmesh)
import bmesh
from mathutils import Euler, Matrix, Quaternion, Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS = 24
F_START, F_END = 1, 120

ap = argparse.ArgumentParser()
ap.add_argument("--out", default="renders/proof_v1")
ap.add_argument("--res", default="540x960")
ap.add_argument("--samples", type=int, default=32)
ap.add_argument("--frames", default=f"{F_START}-{F_END}")
ap.add_argument("--stills", default="")
ap.add_argument("--no-render", action="store_true")
args = ap.parse_args(sys.argv[1:])
OUT = os.path.abspath(os.path.join(ROOT, args.out) if not os.path.isabs(args.out) else args.out)
os.makedirs(os.path.join(OUT, "frames"), exist_ok=True)
random.seed(7)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"  # 1 BU = 1 m
scene.render.fps = FPS
scene.frame_start, scene.frame_end = F_START, F_END


# --------------------------------------------------------------------------- helpers
def collection(name):
    c = bpy.data.collections.new(name)
    scene.collection.children.link(c)
    return c


COL = {n: collection(n) for n in ("ENV_far", "ENV_mid", "ENV_near", "CHAR_pip", "FX_rain", "LIGHTS", "CAMERA")}


def link(obj, col):
    for c in obj.users_collection:
        c.objects.unlink(obj)
    COL[col].objects.link(obj)
    return obj


def mat(name, color, rough=0.5, metal=0.0, emit=None, strength=0.0, alpha=1.0, coat=0.0, transmission=0.0):
    m = bpy.data.materials.new(name)
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    b.inputs["Alpha"].default_value = alpha
    b.inputs["Coat Weight"].default_value = coat
    b.inputs["Transmission Weight"].default_value = transmission
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = strength
    return m


def assign(obj, m):
    obj.data.materials.clear()
    obj.data.materials.append(m)
    return obj


def smooth(obj, levels=2):
    for p in obj.data.polygons:
        p.use_smooth = True
    if levels:
        mod = obj.modifiers.new("subd", "SUBSURF")
        mod.levels = mod.render_levels = levels
    return obj


def box(name, loc, size, m, col, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        mod = o.modifiers.new("bevel", "BEVEL")
        mod.width, mod.segments = bevel, 2
    return link(assign(o, m), col)


def sphere(name, loc, scale, m, col, seg=24):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=seg // 2, radius=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    smooth(o, 1)
    return link(assign(o, m), col)


def cyl(name, loc, r, depth, m, col, verts=24, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    for p in o.data.polygons:
        p.use_smooth = True
    return link(assign(o, m), col)


def empty(name, loc=(0, 0, 0), parent=None, col="CHAR_pip"):
    o = bpy.data.objects.new(name, None)
    o.empty_display_size = 0.1
    COL[col].objects.link(o)
    o.location = loc
    if parent:
        o.parent = parent
    return o


def parent_keep(child, parent):
    bpy.context.view_layer.update()  # matrix_world of fresh objects is stale until evaluated
    child.parent = parent
    child.matrix_parent_inverse = parent.matrix_world.inverted()


def smoothstep(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * t


# --------------------------------------------------------------------------- materials (style bible palette)
M = {
    "asphalt": None,
    "sidewalk": mat("sidewalk", (0.16, 0.16, 0.17), 0.35),
    "curb": mat("curb", (0.32, 0.31, 0.30), 0.55),
    "brick": mat("brick_dark", (0.20, 0.085, 0.06), 0.8),
    "brick2": mat("plaster_blue", (0.08, 0.11, 0.15), 0.75),
    "shopfront": mat("shopfront_green", (0.02, 0.16, 0.12), 0.35, coat=0.6),
    "trim": mat("trim_cream", (0.75, 0.68, 0.55), 0.4),
    "interior": mat("interior_wall", (0.5, 0.3, 0.17), 0.7),
    "shelf": mat("shelf_wood", (0.35, 0.18, 0.08), 0.6),
    "glass": mat("glass", (0.9, 0.95, 1.0), 0.03, transmission=1.0),
    "metal": mat("lamp_metal", (0.05, 0.06, 0.07), 0.3, metal=1.0),
    "win_lit": mat("window_lit", (0.0, 0.0, 0.0), 0.5, emit=(1.0, 0.55, 0.25), strength=0.9),
    "win_cool": mat("window_cool", (0.0, 0.0, 0.0), 0.5, emit=(0.55, 0.75, 1.0), strength=1.6),
    "win_dark": mat("window_dark", (0.01, 0.012, 0.02), 0.08),
    "lamp_glow": mat("lamp_glow", (0, 0, 0), 0.5, emit=(1.0, 0.75, 0.45), strength=25.0),
    "rain": mat("rain", (0.7, 0.8, 1.0), 0.1, emit=(0.6, 0.72, 0.95), strength=1.5, alpha=0.45),
    # character
    "coat": mat("pip_coat_teal", (0.02, 0.36, 0.40), 0.32, coat=0.8),
    "hat": mat("pip_hat_mustard", (0.85, 0.55, 0.05), 0.3, coat=0.8),
    "skin": mat("pip_skin", (0.80, 0.50, 0.33), 0.55),
    "eye": mat("pip_eye_white", (0.92, 0.92, 0.9), 0.15),
    "pupil": mat("pip_pupil", (0.01, 0.01, 0.012), 0.1),
    "dark": mat("pip_mouth_brow", (0.08, 0.03, 0.02), 0.6),
    "boot": mat("pip_boot_red", (0.45, 0.04, 0.03), 0.25, coat=0.6),
    "parcel": mat("parcel_kraft", (0.45, 0.28, 0.12), 0.8),
    "string": mat("parcel_string", (0.8, 0.75, 0.6), 0.9),
    "sign_neon": mat("sign_neon", (0.05, 0.0, 0.01), 0.4, emit=(1.0, 0.18, 0.35), strength=0.0),
}
for m in (M["rain"],):
    m.surface_render_method = "BLENDED" if hasattr(m, "surface_render_method") else None

# wet asphalt: noise-driven roughness gives reflective puddles + grain bump
asph = mat("asphalt_wet", (0.025, 0.026, 0.03), 0.3)
nt = asph.node_tree
bsdf = nt.nodes["Principled BSDF"]
tc = nt.nodes.new("ShaderNodeTexCoord")
noise = nt.nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value = 0.6
noise.inputs["Detail"].default_value = 4
ramp = nt.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position, ramp.color_ramp.elements[0].color = 0.45, (0.03, 0.03, 0.03, 1)
ramp.color_ramp.elements[1].position, ramp.color_ramp.elements[1].color = 0.6, (0.42, 0.42, 0.42, 1)
grain = nt.nodes.new("ShaderNodeTexNoise")
grain.inputs["Scale"].default_value = 90
bump = nt.nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = 0.15
nt.links.new(tc.outputs["Object"], noise.inputs["Vector"])
nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
nt.links.new(ramp.outputs["Color"], bsdf.inputs["Roughness"])
nt.links.new(grain.outputs["Fac"], bump.inputs["Height"])
nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
M["asphalt"] = asph

# striped awning
awn = mat("awning_stripes", (0.6, 0.05, 0.05), 0.6)
nt = awn.node_tree
wave = nt.nodes.new("ShaderNodeTexWave")
wave.wave_type = "BANDS"
wave.bands_direction = "X"
wave.inputs["Scale"].default_value = 3.5
wave.inputs["Distortion"].default_value = 0
r2 = nt.nodes.new("ShaderNodeValToRGB")
r2.color_ramp.interpolation = "CONSTANT"
r2.color_ramp.elements[0].color = (0.55, 0.04, 0.05, 1)
r2.color_ramp.elements[1].position, r2.color_ramp.elements[1].color = 0.5, (0.85, 0.78, 0.62, 1)
tc2 = nt.nodes.new("ShaderNodeTexCoord")
nt.links.new(tc2.outputs["Object"], wave.inputs["Vector"])
nt.links.new(wave.outputs["Fac"], r2.inputs["Fac"])
nt.links.new(r2.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"])
M["awning"] = awn

# --------------------------------------------------------------------------- environment
# Street runs along X. Sidewalk y in [0.2, 1.5]; shop facade plane at y=1.5; road y<0.2 at z=-0.15.
box("road", (-10, -4, -0.2), (60, 9, 0.1), M["asphalt"], "ENV_mid")
box("sidewalk", (-10, 0.85, -0.075), (60, 1.3, 0.15), M["asphalt"], "ENV_mid")
box("curb", (-10, 0.2, -0.075), (60, 0.12, 0.16), M["curb"], "ENV_mid", bevel=0.02)
box("road_far_sidewalk", (-10, -7.0, -0.1), (60, 2.0, 0.2), M["sidewalk"], "ENV_far")

# Shop (x in [-0.8, 2.0]) with a real window opening and interior volume (parallax inside).
WX0, WX1, WZ0, WZ1, FY = -0.55, 1.45, 0.45, 1.85, 1.5
box("shop_sill", (0.45, FY + 0.05, WZ0 / 2), (2.5, 0.1, WZ0), M["shopfront"], "ENV_mid")
box("shop_header", (0.45, FY + 0.05, 2.45), (2.5, 0.1, 1.2), M["shopfront"], "ENV_mid")
box("shop_pillar_L", (-0.68, FY + 0.05, 1.15), (0.26, 0.12, 1.4), M["shopfront"], "ENV_mid")
box("shop_pillar_R", (1.58, FY + 0.05, 1.15), (0.26, 0.12, 1.4), M["shopfront"], "ENV_mid")
box("shop_upper", (0.45, FY + 0.1, 4.2), (2.5, 0.2, 2.4), M["brick"], "ENV_mid")
box("window_frame_bottom", (0.45, FY - 0.02, WZ0), (2.05, 0.06, 0.06), M["trim"], "ENV_mid")
box("window_frame_top", (0.45, FY - 0.02, WZ1), (2.05, 0.06, 0.06), M["trim"], "ENV_mid")
box("window_mullion", (0.45, FY - 0.02, 1.15), (0.05, 0.05, 1.4), M["trim"], "ENV_mid")
glass = box("window_glass", (0.45, FY, 1.15), (2.0, 0.01, 1.4), M["glass"], "ENV_mid")
# interior
box("int_back", (0.45, 3.2, 1.2), (2.4, 0.05, 2.4), M["interior"], "ENV_mid")
box("int_floor", (0.45, 2.35, 0.0), (2.4, 1.7, 0.05), M["shelf"], "ENV_mid")
box("int_ceiling", (0.45, 2.35, 2.2), (2.4, 1.7, 0.05), M["interior"], "ENV_mid")
box("int_side_L", (-0.75, 2.35, 1.2), (0.05, 1.7, 2.4), M["interior"], "ENV_mid")
box("int_side_R", (1.65, 2.35, 1.2), (0.05, 1.7, 2.4), M["interior"], "ENV_mid")
goods_cols = [(0.8, 0.2, 0.1), (0.1, 0.4, 0.7), (0.9, 0.7, 0.1), (0.2, 0.55, 0.25), (0.85, 0.85, 0.8)]
for si, sz in enumerate((0.75, 1.2, 1.65)):
    box(f"shelf_{si}", (0.45, 3.0, sz), (2.3, 0.35, 0.04), M["shelf"], "ENV_mid")
    x = -0.6
    while x < 1.5:
        w = random.uniform(0.08, 0.18)
        h = random.uniform(0.12, 0.3)
        gm = mat(f"goods_{si}_{x:.2f}", random.choice(goods_cols), random.uniform(0.3, 0.7))
        if random.random() < 0.5:
            box(f"goods_{si}_{x:.2f}", (x + w / 2, 3.0, sz + h / 2 + 0.02), (w, 0.2, h), gm, "ENV_mid")
        else:
            cyl(f"jar_{si}_{x:.2f}", (x + w / 2, 3.0, sz + h / 2 + 0.02), w / 2, h, gm, "ENV_mid", verts=16)
        x += w + random.uniform(0.02, 0.06)
box("counter", (0.9, 2.2, 0.45), (1.0, 0.45, 0.9), M["shelf"], "ENV_mid", bevel=0.02)
# awning: tilted striped slab + valance
bpy.ops.mesh.primitive_plane_add(size=1, location=(0.45, FY - 0.42, 2.03))
aw = bpy.context.object
aw.name = "awning"
aw.scale = (2.6, 0.9, 1)
aw.rotation_euler = (math.radians(-22), 0, 0)
sol = aw.modifiers.new("thick", "SOLIDIFY")
sol.thickness = 0.03
link(assign(aw, M["awning"]), "ENV_mid")
box("awning_valance", (0.45, FY - 0.84, 1.79), (2.6, 0.02, 0.16), M["awning"], "ENV_mid")

# Blade sign (OPEN) protruding from facade above the awning; it flickers on mid-shot.
# Neon OPEN sign hangs just inside the window glass, facing the street (-Y).
SIGN = Vector((0.62, 1.6, 1.42))
bk = box("sign_backer", (SIGN.x, SIGN.y + 0.03, SIGN.z), (0.72, 0.02, 0.3), M["metal"], "ENV_mid", bevel=0.01)
bk.rotation_euler.z = math.radians(30)
for o_name, dz in (("sign_chain_L", -0.25), ("sign_chain_R", 0.25)):
    box(o_name, (SIGN.x + dz, SIGN.y + 0.03, (SIGN.z + WZ1) / 2), (0.008, 0.008, WZ1 - SIGN.z), M["metal"], "ENV_mid")
for side, sx in (("A", 0),):
    cu = bpy.data.curves.new(f"sign_text_{side}", "FONT")
    cu.body = "OPEN"
    cu.align_x, cu.align_y = "CENTER", "CENTER"
    cu.size = 0.16
    cu.extrude = 0.006
    to = bpy.data.objects.new(f"sign_text_{side}", cu)
    COL["ENV_mid"].objects.link(to)
    cu.size = 0.24
    cu.bevel_depth = 0.008
    to.location = (SIGN.x, SIGN.y, SIGN.z)
    to.rotation_euler = (math.radians(90), 0, math.radians(30))  # angled toward the street corner
    to.data.materials.append(M["sign_neon"])

# Neighbouring facades along y=1.5 (mid layer) with windows.
def facade(name, x0, x1, height, m, lit_ratio, rows=3):
    w = x1 - x0
    box(name, ((x0 + x1) / 2, FY + 0.15, height / 2), (w, 0.3, height), m, "ENV_mid")
    cols = max(1, int(w / 1.3))
    for r in range(rows):
        for c in range(cols):
            wx = x0 + (c + 0.5) * w / cols
            wz = 1.2 + r * 1.7
            if wz + 0.5 > height:
                continue
            wm = M["win_lit"] if random.random() < lit_ratio else (M["win_cool"] if random.random() < 0.2 else M["win_dark"])
            box(f"{name}_win_{r}_{c}", (wx, FY - 0.01, wz), (0.6, 0.04, 0.9), wm, "ENV_mid")
            box(f"{name}_sill_{r}_{c}", (wx, FY - 0.05, wz - 0.48), (0.72, 0.1, 0.05), M["trim"], "ENV_mid")


facade("bldg_L1", -6.0, -0.8, 6.5, M["brick2"], 0.25)
facade("bldg_L2", -11.5, -6.0, 8.0, M["brick"], 0.3)
facade("bldg_R1", 2.0, 6.0, 7.0, M["brick"], 0.2)
facade("bldg_L3", -19.0, -11.5, 10.0, M["brick2"], 0.35, rows=5)

# Far layer: across-the-street and down-the-street blocks with lit windows.
for i in range(14):
    x = -14 - i * 3.2
    side = -1 if i % 2 else 1
    h = random.uniform(7, 18)
    y = 1.6 + random.uniform(0, 1.5) if side > 0 else -8.5 - random.uniform(0, 2)
    b = box(f"far_block_{i}", (x, y + side * 1.5, h / 2), (3.0, 3.0, h), random.choice((M["brick"], M["brick2"])), "ENV_far")
    for r in range(int(h / 1.6)):
        if random.random() < 0.45:
            wm = M["win_lit"] if random.random() < 0.7 else M["win_cool"]
            box(f"far_win_{i}_{r}", (x + random.uniform(-0.8, 0.8), y - side * 0.02, 1.2 + r * 1.6), (0.5, 0.05, 0.7), wm, "ENV_far")
for i in range(8):  # across the street (y = -9) facing the shop
    x = 6 - i * 4.2
    h = random.uniform(6, 12)
    box(f"opp_block_{i}", (x, -10, h / 2), (4.0, 2.0, h), random.choice((M["brick"], M["brick2"])), "ENV_far")
    for r in range(int(h / 1.7)):
        for c in range(2):
            if random.random() < 0.4:
                box(f"opp_win_{i}_{r}_{c}", (x - 0.9 + c * 1.8, -8.98, 1.3 + r * 1.7), (0.6, 0.04, 0.9), M["win_lit"], "ENV_far")


# Street lamps receding down the street (near lamp is the foreground parallax object).
def street_lamp(name, x, y, col, energy=60.0):
    cyl(f"{name}_pole", (x, y, 1.6), 0.045, 3.2, M["metal"], col, verts=12)
    cyl(f"{name}_arm", (x, y + 0.3, 3.15), 0.025, 0.6, M["metal"], col, verts=8, rot=(math.radians(90), 0, 0))
    sphere(f"{name}_bulb", (x, y + 0.6, 3.05), (0.12, 0.12, 0.09), M["lamp_glow"], col, seg=12)
    ld = bpy.data.lights.new(f"{name}_light", "SPOT")
    ld.energy = energy
    ld.color = (1.0, 0.72, 0.42)
    ld.spot_size = math.radians(95)
    ld.spot_blend = 0.6
    ld.shadow_soft_size = 0.15
    lo = bpy.data.objects.new(f"{name}_light", ld)
    COL["LIGHTS"].objects.link(lo)
    lo.location = (x, y + 0.6, 2.95)


street_lamp("lamp_near", 3.6, 0.28, "ENV_near", energy=80)
for i, x in enumerate((-5.0, -11.0, -17.0, -23.0, -29.0)):
    street_lamp(f"lamp_far_{i}", x, 0.28, "ENV_far", energy=70)

# Near layer props: bollard + bin + hydrant close to camera path.
cyl("bollard", (2.55, 0.42, 0.42), 0.07, 0.84, M["metal"], "ENV_near", verts=16)
sphere("bollard_cap", (2.55, 0.42, 0.85), (0.075, 0.075, 0.05), M["metal"], "ENV_near", seg=12)
cyl("bin", (3.55, 1.2, 0.42), 0.24, 0.84, M["shopfront"], "ENV_near", verts=24)
cyl("hydrant", (-1.6, 0.42, 0.28), 0.09, 0.56, M["boot"], "ENV_mid", verts=16)
sphere("hydrant_cap", (-1.6, 0.42, 0.58), (0.1, 0.1, 0.07), M["boot"], "ENV_mid", seg=12)

# Puddle splash rings are omitted in v1 (see QC notes).

# --------------------------------------------------------------------------- rain (two stacked sheets, looping fall)
def rain_sheet(name, z0, n=900):
    bm = bmesh.new()
    for _ in range(n):
        x = random.uniform(-9, 5)
        y = random.uniform(-4, 4)
        z = random.uniform(0, 6)
        h = random.uniform(0.16, 0.3)
        w = 0.0045
        vs = [bm.verts.new(v) for v in ((x - w, y, z), (x + w, y, z), (x + w, y, z + h), (x - w, y, z + h))]
        bm.faces.new(vs)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    ob = bpy.data.objects.new(name, me)
    COL["FX_rain"].objects.link(ob)
    ob.location.z = z0
    me.materials.append(M["rain"])
    ob.visible_shadow = False
    return ob


rain = [rain_sheet("rain_A", 0.0), rain_sheet("rain_B", 6.0)]
RAIN_SPEED = 0.33  # m/frame (~8 m/s)
for f in range(F_START, F_END + 1):
    for i, ob in enumerate(rain):
        z = (i * 6.0 - RAIN_SPEED * (f - 1)) % 12.0 - 0.5
        ob.location.z = z
        ob.keyframe_insert("location", index=2, frame=f)

# --------------------------------------------------------------------------- character "Pip" (built facing -Y)
HIP_H = 0.42
root = empty("pip_root", col="CHAR_pip")
root.rotation_mode = "XYZ"
body = empty("pip_body", (0, 0, HIP_H), root)
coat = sphere("pip_coat", (0, 0, HIP_H + 0.15), (0.27, 0.23, 0.33), M["coat"], "CHAR_pip")
bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=0.3, radius2=0.22, depth=0.22, location=(0, 0, HIP_H - 0.02))
hem = link(assign(smooth(bpy.context.object, 1), M["coat"]), "CHAR_pip")
hem.name = "pip_coat_hem"
for b in (sphere("pip_button_1", (0, -0.235, HIP_H + 0.22), (0.025, 0.012, 0.025), M["hat"], "CHAR_pip", seg=12),
          sphere("pip_button_2", (0, -0.248, HIP_H + 0.08), (0.025, 0.012, 0.025), M["hat"], "CHAR_pip", seg=12)):
    parent_keep(b, body)
parent_keep(coat, body)
parent_keep(hem, body)

neck = empty("pip_neck", (0, 0, 0.42), body)  # local to body
neck.rotation_mode = "XYZ"
HEAD_C = Vector((0, 0, HIP_H + 0.42 + 0.17))
head = sphere("pip_head", HEAD_C, (0.25, 0.235, 0.23), M["skin"], "CHAR_pip", seg=32)
nose = sphere("pip_nose", HEAD_C + Vector((0, -0.235, -0.02)), (0.045, 0.04, 0.04), M["skin"], "CHAR_pip", seg=16)
eyes = {}
for side, sx in (("L", 0.085), ("R", -0.085)):
    ec = HEAD_C + Vector((sx, -0.19, 0.05))
    pivot = empty(f"pip_eye_{side}", ec, None)
    pivot.rotation_mode = "XYZ"
    eye = sphere(f"pip_eyeball_{side}", ec, (0.062, 0.05, 0.072), M["eye"], "CHAR_pip", seg=20)
    pupil = sphere(f"pip_pupil_{side}", ec + Vector((0, -0.045, 0)), (0.03, 0.012, 0.036), M["pupil"], "CHAR_pip", seg=16)
    parent_keep(pupil, pivot)
    lid = empty(f"pip_lidscale_{side}", ec, None)
    parent_keep(eye, lid)
    parent_keep(pivot, lid)
    brow = sphere(f"pip_brow_{side}", ec + Vector((0, -0.01, 0.105)), (0.05, 0.012, 0.012), M["dark"], "CHAR_pip", seg=12)
    eyes[side] = (pivot, lid, brow)
# smile arc: lower half of a torus
bpy.ops.mesh.primitive_torus_add(major_radius=0.055, minor_radius=0.011, location=(0, 0, 0))
mouth = bpy.context.object
mouth.name = "pip_mouth"
bm = bmesh.new()
bm.from_mesh(mouth.data)
bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.y > 0.004], context="VERTS")
bm.to_mesh(mouth.data)
bm.free()
mouth.rotation_euler = (math.radians(90), 0, 0)
bpy.ops.object.transform_apply(rotation=True)
mouth.location = HEAD_C + Vector((0, -0.215, -0.085))
link(assign(mouth, M["dark"]), "CHAR_pip")
hat_pivot = empty("pip_hat_pivot", HEAD_C + Vector((0, 0, 0.12)), None)
hat_pivot.rotation_mode = "XYZ"
hat_crown = sphere("pip_hat_crown", HEAD_C + Vector((0, 0.01, 0.15)), (0.2, 0.2, 0.15), M["hat"], "CHAR_pip")
bpy.ops.mesh.primitive_cylinder_add(vertices=40, radius=0.33, depth=0.02, location=HEAD_C + Vector((0, 0.0, 0.12)))
brim = link(assign(smooth(bpy.context.object, 0), M["hat"]), "CHAR_pip")
brim.name = "pip_hat_brim"
brim.rotation_euler = (math.radians(-8), 0, 0)  # brim tips down at the back = rain hat
for o in (hat_crown, brim):
    parent_keep(o, hat_pivot)
for o in (head, nose, mouth, hat_pivot, eyes["L"][1], eyes["R"][1], eyes["L"][2], eyes["R"][2]):
    parent_keep(o, neck)

arms = {}
for side, sx in (("L", 1), ("R", -1)):
    sh = empty(f"pip_shoulder_{side}", (sx * 0.24, 0, 0.3), body)  # local to body
    sh.rotation_mode = "XYZ"
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.055, depth=0.26, location=(sx * 0.27, 0, HIP_H + 0.17))
    arm = link(assign(smooth(bpy.context.object, 1), M["coat"]), "CHAR_pip")
    arm.name = f"pip_arm_{side}"
    arm.rotation_euler = (0, sx * math.radians(14), 0)
    mitt = sphere(f"pip_mitt_{side}", (sx * 0.31, 0, HIP_H + 0.03), (0.06, 0.06, 0.065), M["hat"], "CHAR_pip", seg=16)
    parent_keep(arm, sh)
    parent_keep(mitt, sh)
    arms[side] = sh
# parcel tucked under right arm (child of right shoulder)
parcel = box("pip_parcel", (-0.33, -0.1, HIP_H + 0.12), (0.12, 0.26, 0.2), M["parcel"], "CHAR_pip", bevel=0.01)
box("pip_parcel_string", (-0.33, -0.1, HIP_H + 0.12), (0.125, 0.02, 0.205), M["string"], "CHAR_pip")
parent_keep(parcel, arms["R"])
parent_keep(bpy.data.objects["pip_parcel_string"], arms["R"])

# legs + boots are posed in world space each frame (planted feet => no foot sliding)
legs, boots = {}, {}
for side in ("L", "R"):
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.06, depth=1.0, location=(0, 0, -0.5))
    lg = bpy.context.object
    bpy.ops.object.transform_apply(location=True)  # origin at top (hip), extends along -Z
    lg.name = f"pip_leg_{side}"
    link(assign(smooth(lg, 1), M["coat"]), "CHAR_pip")
    lg.rotation_mode = "QUATERNION"
    legs[side] = lg
    bt = sphere(f"pip_boot_{side}", (0, 0, 0), (0.075, 0.11, 0.06), M["boot"], "CHAR_pip", seg=20)
    bt.rotation_mode = "XYZ"
    boots[side] = bt

# --------------------------------------------------------------------------- performance (procedural keyframes)
PATH_Y = 0.78
X0, X_STOP = -2.9, 0.42
WALK_END, STOP_DONE = 50, 66          # decel window
TURN_A, TURN_B = 72, 86               # body turn toward the shop
YAW_WALK, YAW_TURN = math.radians(90), math.radians(140)
STEP = 8                              # frames per step (3 steps/s)


def speed_profile(f):
    return 1.0 - smoothstep(WALK_END, STOP_DONE, f)


# integrate body x so that it lands exactly on X_STOP
xs = {}
acc = 0.0
raw = []
for f in range(-30, F_END + 2):
    raw.append((f, acc))
    acc += speed_profile(f)
total = dict(raw)[STOP_DONE + 2]
for f, a in raw:
    xs[f] = X0 + (X_STOP - X0) * min(1.0, (a - dict(raw)[F_START]) / (total - dict(raw)[F_START])) if f >= F_START else X0 + (X_STOP - X0) * (a - dict(raw)[F_START]) / (total - dict(raw)[F_START])
v_full = (X_STOP - X0) / (total - dict(raw)[F_START])


def body_x(f):
    fi = math.floor(f)
    return lerp(xs[fi], xs[fi + 1], f - fi)


def yaw_at(f):
    return lerp(YAW_WALK, YAW_TURN, smoothstep(TURN_A, TURN_B, f))


def local_offset(side, yaw):
    lx = 0.1 if side == "L" else -0.1
    return Vector((lx * math.cos(yaw), lx * math.sin(yaw), 0))


# footstep plants: (contact_frame, side, position, yaw)
plants = []
c, k = -12, 0
while c <= 58:
    side = "L" if k % 2 == 0 else "R"
    lead = 0.15 * speed_profile(c)
    pos = Vector((body_x(c) + lead, PATH_Y, 0)) + local_offset(side, YAW_WALK)
    plants.append((c, side, pos, YAW_WALK))
    c += STEP
    k += 1
last_side = plants[-1][1]
closing = "R" if last_side == "L" else "L"
plants.append((66, closing, Vector((X_STOP, PATH_Y, 0)) + local_offset(closing, YAW_WALK), YAW_WALK))
# turn-in-place: two small steps re-orient the feet
ctr = Vector((X_STOP, PATH_Y, 0))
plants.append((80, "R", ctr + local_offset("R", lerp(YAW_WALK, YAW_TURN, 0.6)), lerp(YAW_WALK, YAW_TURN, 0.6)))
plants.append((88, "L", ctr + local_offset("L", YAW_TURN), YAW_TURN))
plants.append((94, "R", ctr + local_offset("R", YAW_TURN), YAW_TURN))


def foot_state(side, f):
    ps = [p for p in plants if p[1] == side]
    prev = max((p for p in ps if p[0] <= f), key=lambda p: p[0], default=ps[0])
    nxt = min((p for p in ps if p[0] > f), key=lambda p: p[0], default=None)
    if nxt is None:
        return prev[2].copy(), prev[3], 0.0
    swing = min(STEP, nxt[0] - prev[0])
    lift_start = nxt[0] - swing
    if f < lift_start:
        return prev[2].copy(), prev[3], 0.0
    u = (f - lift_start) / swing
    e = u * u * (3 - 2 * u)
    pos = prev[2].lerp(nxt[2], e)
    lift = (0.075 if nxt[0] <= 66 else 0.04) * math.sin(math.pi * u)
    pos.z += lift
    pitch = math.radians(18) * math.sin(math.pi * u) * (1 if u < 0.6 else -0.5)
    return pos, lerp(prev[3], nxt[3], e), pitch


contacts = sorted((p[0], p[1]) for p in plants if F_START <= p[0] <= F_END)

# acting beats (frames)
BEAT = {
    "walk_in": (1, 50), "decelerate_stop": (50, 66), "settle_overshoot": (64, 74),
    "anticipation_dip": (70, 76), "turn_to_shop": (72, 88), "sign_flicker_on": (80, 92),
    "eyes_lead_look_up": (76, 84), "head_look_up": (79, 92), "blink": (95, 98),
    "smile": (96, 104), "hold": (104, 120),
}

# sign flicker pattern (emission strength), on for good at 92
flicker = {79: 0.0, 80: 6.0, 81: 0.3, 82: 0.0, 84: 7.0, 85: 1.0, 86: 7.5, 87: 0.4, 89: 8.0, 92: 8.0}
sign_light = bpy.data.lights.new("sign_glow", "POINT")
sign_light.color = (1.0, 0.25, 0.4)
sign_light.shadow_soft_size = 0.3
slo = bpy.data.objects.new("sign_glow", sign_light)
COL["LIGHTS"].objects.link(slo)
slo.location = (SIGN.x, SIGN.y - 0.25, SIGN.z)
em = M["sign_neon"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
for f in range(F_START, F_END + 1):
    keys = sorted(flicker)
    val = 0.0
    for kf in keys:
        if kf <= f:
            val = flicker[kf]
    em.default_value = val
    em.keyframe_insert("default_value", frame=f)
    sign_light.energy = val * 4.0
    sign_light.keyframe_insert("energy", frame=f)

head_trace = {}
for f in range(F_START, F_END + 1):
    sp = speed_profile(f)
    yaw = yaw_at(f)
    # root
    root.location = (body_x(f), PATH_Y, 0)
    root.rotation_euler = (0, 0, yaw)
    root.keyframe_insert("location", frame=f)
    root.keyframe_insert("rotation_euler", frame=f)
    # body bob: lowest at contacts (every 8 frames from -12 => phase), squash on contact
    phase = ((f + 12) % STEP) / STEP
    bob = -0.022 * math.cos(2 * math.pi * phase) * sp
    settle = 0.0
    if f >= 60:  # stop overshoot then settle (follow-through)
        settle = math.exp(-(f - 64) / 5.0) * math.sin((f - 60) / 3.2) * 0.12 if f > 60 else 0
    dip = -0.035 * math.sin(math.pi * smoothstep(70, 76, f)) if f <= 78 else 0.0
    lean = math.radians(7) * sp + settle
    body.location = (0, 0, HIP_H + bob + dip)
    body.rotation_euler = (lean, 0, math.radians(4) * math.sin(math.pi * phase * 2) * sp)
    squash = 1 - 0.035 * max(0.0, math.cos(2 * math.pi * phase)) * sp
    body.scale = (1 / math.sqrt(squash), 1 / math.sqrt(squash), squash)
    for prop in ("location", "rotation_euler", "scale"):
        body.keyframe_insert(prop, frame=f)
    # arms: left swings opposite left leg; right holds parcel (small counter-sway)
    swing = math.radians(28) * math.sin(2 * math.pi * ((f + 12) / (2 * STEP))) * sp
    arms["L"].rotation_euler = (-swing, 0, math.radians(-6))
    arms["R"].rotation_euler = (math.radians(-8) + swing * 0.15, 0, math.radians(6))
    if f > 96:  # small hopeful lift of the free hand
        arms["L"].rotation_euler = (math.radians(-35) * smoothstep(96, 106, f), 0, math.radians(-6 - 12 * smoothstep(96, 106, f)))
    arms["L"].keyframe_insert("rotation_euler", frame=f)
    arms["R"].keyframe_insert("rotation_euler", frame=f)
    # head: walking = look ahead and a bit toward camera, then dip, then look up at the sign
    look_up = smoothstep(79, 92, f)
    head_pitch = lerp(math.radians(-4), math.radians(-22), look_up) + math.radians(6) * math.sin(math.pi * smoothstep(70, 78, f))
    head_yaw = lerp(math.radians(-12), math.radians(4), look_up)
    head_pitch += -lean * 0.6  # counter the body lean so the gaze stays level
    neck.rotation_euler = (head_pitch, 0, head_yaw)
    neck.keyframe_insert("rotation_euler", frame=f)
    head_trace[f] = (head_pitch, head_yaw)
    # eyes lead head by ~4 frames
    eye_up = smoothstep(76, 84, f)
    for side in ("L", "R"):
        pivot, lid, brow = eyes[side]
        pivot.rotation_euler = (math.radians(-6) - math.radians(22) * eye_up, 0, math.radians(-10) * (1 - eye_up) + math.radians(-6) * eye_up)
        pivot.keyframe_insert("rotation_euler", frame=f)
        blink = 1.0
        for b0 in (24, 95):
            if b0 <= f <= b0 + 3:
                blink = (0.15, 0.05, 0.4, 0.9)[f - b0]
        lid.scale = (1, 1, blink)
        lid.keyframe_insert("scale", frame=f)
        brow.location.z = (HEAD_C.z + 0.155) + 0.035 * smoothstep(82, 90, f)
        brow.keyframe_insert("location", index=2, frame=f)
    # mouth: neutral flat arc -> smile
    sm = smoothstep(96, 104, f)
    mouth.scale = (lerp(0.7, 1.15, sm), 1, lerp(0.25, 1.0, sm))
    mouth.keyframe_insert("scale", frame=f)
    # hat overlap: lags the head by 3 frames
    lagp, lagy = head_trace.get(f - 3, head_trace[f])
    hat_pivot.rotation_euler = ((lagp - head_pitch) * 0.6 + math.radians(2) * math.sin(2 * math.pi * phase) * sp, 0, (lagy - head_yaw) * 0.6)
    hat_pivot.keyframe_insert("rotation_euler", frame=f)

    # legs: world-space solve hip -> ankle
    scene.frame_set(f)
    bpy.context.view_layer.update()
    for side in ("L", "R"):
        fpos, fyaw, pitch = foot_state(side, f)
        bt = boots[side]
        bt.location = fpos + Vector((0, 0, 0.055))
        fwd = Vector((-math.sin(fyaw) * -1, math.cos(fyaw) * -1, 0))  # model front (-Y) rotated
        bt.location += Vector((math.sin(fyaw), -math.cos(fyaw), 0)) * 0.035
        bt.rotation_euler = (pitch, 0, fyaw)
        bt.keyframe_insert("location", frame=f)
        bt.keyframe_insert("rotation_euler", frame=f)
        hip = body.matrix_world @ Vector((0.1 if side == "L" else -0.1, 0, -0.02))
        ankle = fpos + Vector((0, 0, 0.09))
        d = ankle - hip
        lg = legs[side]
        lg.location = hip
        lg.rotation_quaternion = Vector((0, 0, -1)).rotation_difference(d.normalized())
        lg.scale = (1, 1, d.length)
        for prop in ("location", "rotation_quaternion", "scale"):
            lg.keyframe_insert(prop, frame=f)

# --------------------------------------------------------------------------- camera: true 3D truck + push-in past a foreground lamp
cam_data = bpy.data.cameras.new("cam_P01")
cam_data.lens = 32
cam_data.sensor_fit = "VERTICAL"
cam_data.sensor_height = 36
cam_data.dof.use_dof = True
cam_data.dof.aperture_fstop = 2.2
cam = bpy.data.objects.new("cam_P01", cam_data)
COL["CAMERA"].objects.link(cam)
scene.camera = cam
target = empty("cam_target", col="CAMERA")
cam_data.dof.focus_object = neck
con = cam.constraints.new("TRACK_TO")
con.target = target
con.track_axis, con.up_axis = "TRACK_NEGATIVE_Z", "UP_Y"
CAM_KEYS = {1: (4.6, -1.55, 0.78), 60: (3.75, -0.4, 0.9), 120: (2.55, 1.02, 1.05)}
for f, p in CAM_KEYS.items():
    cam.location = p
    cam.keyframe_insert("location", frame=f)
cam_data.lens = 30
cam_data.keyframe_insert("lens", frame=1)
cam_data.lens = 26
cam_data.keyframe_insert("lens", frame=120)
sm_t = None
for f in range(F_START, F_END + 1):
    scene.frame_set(f)
    h = neck.matrix_world.translation + Vector((0, 0, 0.12))
    goal = h.lerp(SIGN, 0.56 * smoothstep(80, 110, f)) + Vector((0, 0, 0.05))
    sm_t = goal if sm_t is None else sm_t.lerp(goal, 0.25)  # damped follow
    target.location = sm_t
    target.keyframe_insert("location", frame=f)

# --------------------------------------------------------------------------- lighting
world = bpy.data.worlds.new("night_rain")
scene.world = world
wn = world.node_tree.nodes
bg = wn["Background"]
sky = wn.new("ShaderNodeTexGradient")
skyramp = wn.new("ShaderNodeValToRGB")
skyramp.color_ramp.elements[0].color = (0.035, 0.05, 0.09, 1)
skyramp.color_ramp.elements[1].color = (0.006, 0.008, 0.016, 1)
sep = wn.new("ShaderNodeSeparateXYZ")
tcw = wn.new("ShaderNodeTexCoord")
mr = wn.new("ShaderNodeMapRange")
world.node_tree.links.new(tcw.outputs["Generated"], sep.inputs[0])
world.node_tree.links.new(sep.outputs["Z"], mr.inputs["Value"])
mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = 0.5, 0.8
world.node_tree.links.new(mr.outputs["Result"], skyramp.inputs["Fac"])
world.node_tree.links.new(skyramp.outputs["Color"], bg.inputs["Color"])
bg.inputs["Strength"].default_value = 1.0


def area(name, loc, rot, energy, size, color, size_y=None):
    ld = bpy.data.lights.new(name, "AREA")
    ld.energy = energy
    ld.color = color
    if size_y:
        ld.shape = "RECTANGLE"
        ld.size, ld.size_y = size, size_y
    else:
        ld.size = size
    lo = bpy.data.objects.new(name, ld)
    COL["LIGHTS"].objects.link(lo)
    lo.location = loc
    lo.rotation_euler = [math.radians(a) for a in rot]
    lo.visible_camera = False  # light emitters must not read as white planes
    return lo


# key: warm window spill (motivated by shop interior), facing out of the window (-Y)
spill = area("key_window_spill", (0.45, 1.3, 1.15), (90, 0, 0), 45, 2.0, (1.0, 0.65, 0.35), size_y=1.4)
spill.visible_glossy = spill.visible_transmission = False  # keep the window readable
area("shop_interior", (0.45, 2.4, 2.1), (0, 0, 0), 18, 1.5, (1.0, 0.7, 0.4))
# rim: cool moonlit/neon back light from down the street
area("rim_cool", (-3.5, -1.5, 3.5), (55, 0, -110), 220, 3.0, (0.45, 0.6, 1.0))
# low fill from the camera side so faces don't crush
area("fill_street", (5.0, -3.0, 1.6), (80, 0, 55), 35, 4.0, (0.6, 0.7, 0.95))
# atmospheric depth: thin volume in the far street only (cheap scatter)
bpy.ops.mesh.primitive_cube_add(size=1, location=(-22, -2, 6))
vol = bpy.context.object
vol.name = "fog_far"
vol.scale = (28, 20, 12)
vm = bpy.data.materials.new("fog")
vt = vm.node_tree
vt.nodes.remove(vt.nodes["Principled BSDF"])
vs = vt.nodes.new("ShaderNodeVolumeScatter")
vs.inputs["Density"].default_value = 0.035
vs.inputs["Color"].default_value = (0.6, 0.7, 0.9, 1)
vt.links.new(vs.outputs["Volume"], vt.nodes["Material Output"].inputs["Volume"])
vol.data.materials.append(vm)
link(vol, "ENV_far")

# --------------------------------------------------------------------------- render settings
rx, ry = (int(v) for v in args.res.split("x"))
r = scene.render
r.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = args.samples
scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = 0.03
scene.cycles.use_denoising = True
scene.cycles.max_bounces = 6
scene.cycles.transparent_max_bounces = 8
scene.cycles.volume_bounces = 0
scene.cycles.caustics_reflective = scene.cycles.caustics_refractive = False
scene.cycles.blur_glossy = 1.0
r.use_persistent_data = True
r.resolution_x, r.resolution_y, r.resolution_percentage = rx, ry, 100
r.image_settings.file_format = "PNG"
r.image_settings.color_mode = "RGB"
r.use_motion_blur = False
try:
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
except TypeError:
    pass
scene.view_settings.exposure = 0.35
r.filepath = os.path.join(OUT, "frames", "")

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "proof_scene.blend"))

events = {
    "shot_id": "P01",
    "fps": FPS,
    "frame_in": F_START,
    "frame_out": F_END,
    "footstep_contacts": [{"frame": f, "foot": s, "time_s": round((f - 1) / FPS, 4)} for f, s in contacts],
    "sign_flicker_keys": [{"frame": f, "emission": v, "time_s": round((f - 1) / FPS, 4)} for f, v in sorted(flicker.items())],
    "beats": BEAT,
    "camera_keys": CAM_KEYS,
}
os.makedirs(os.path.join(ROOT, "manifests"), exist_ok=True)
with open(os.path.join(ROOT, "manifests", "p01_animation_events.json"), "w") as fh:
    json.dump(events, fh, indent=2)

if args.no_render:
    sys.exit(0)

timings = []
if args.stills:
    frames = [int(x) for x in args.stills.split(",")]
else:
    a, b = (int(x) for x in args.frames.split("-"))
    frames = list(range(a, b + 1))
for f in frames:
    out_png = os.path.join(OUT, "frames", f"{f:04d}.png")
    if not args.stills and os.path.exists(out_png):  # restart-safe: skip frames already on disk
        continue
    scene.frame_set(f)
    r.filepath = out_png
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    timings.append({"frame": f, "seconds": round(time.time() - t0, 2)})
    print(f"[P01] frame {f} {timings[-1]['seconds']}s", flush=True)
with open(os.path.join(OUT, "render_timings.json"), "w") as fh:
    json.dump({"res": args.res, "samples": args.samples, "frames": timings,
               "mean_s": round(sum(t["seconds"] for t in timings) / max(1, len(timings)), 2)}, fh, indent=2)
