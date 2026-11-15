"""Shared building blocks for P02 "Be Seen" (bpy): helpers, materials, the lab set and characters.

Every object, material and animation here is procedural and original. Quality rules come from
docs/prompt_book (sections 3.1-3.7); the cast and world come from docs/cast_P02.md / docs/world_P02.md.
"""
import math
import random

import bpy  # noqa: E402  (bpy before bmesh)
import bmesh
from mathutils import Vector

scene = None
COL = {}


def reset(fps=24):
    global scene
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.render.fps = fps
    COL.clear()
    for n in ("ENV_near", "ENV_mid", "ENV_far", "CHAR_quill", "CHAR_juno", "CHAR_scanner", "CHAR_mote",
              "FX", "LIGHTS", "CAMERA"):
        c = bpy.data.collections.new(n)
        scene.collection.children.link(c)
        COL[n] = c
    random.seed(7)
    return scene


# --------------------------------------------------------------------------- small helpers
def smoothstep(a, b, x):
    if b == a:
        return 1.0 if x >= b else 0.0
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * t


def track(f, keys):
    """Piecewise smoothstep through [(frame, value), ...]; values may be numbers or tuples."""
    keys = sorted(keys, key=lambda k: k[0])
    if f <= keys[0][0]:
        return keys[0][1]
    for (f0, v0), (f1, v1) in zip(keys, keys[1:]):
        if f <= f1:
            t = smoothstep(f0, f1, f)
            if isinstance(v0, (tuple, list, Vector)):
                return tuple(lerp(a, b, t) for a, b in zip(v0, v1))
            return lerp(v0, v1, t)
    return keys[-1][1]


def link(obj, col):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    COL[col].objects.link(obj)
    return obj


def mat(name, color, rough=0.5, metal=0.0, emit=None, strength=0.0, alpha=1.0, coat=0.0, transmission=0.0,
        ior=1.45, sheen=0.0):
    m = bpy.data.materials.new(name)
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    b.inputs["Alpha"].default_value = alpha
    b.inputs["Coat Weight"].default_value = coat
    b.inputs["Transmission Weight"].default_value = transmission
    b.inputs["IOR"].default_value = ior
    b.inputs["Sheen Weight"].default_value = sheen
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = strength
    return m


def emis(name, color, strength):
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = (*color, 1)
    e.inputs["Strength"].default_value = strength
    nt.links.new(e.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
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


def box(name, loc, size, m, col, bevel=0.0, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        mod = o.modifiers.new("bevel", "BEVEL")
        mod.width, mod.segments = bevel, 2
    return link(assign(o, m), col)


def rbox(name, loc, size, m, col, levels=2):
    """Rounded box: a cube with subdivision (soft, toy-like)."""
    o = box(name, loc, size, m, col)
    return smooth(o, levels)


def sphere(name, loc, scale, m, col, seg=24, levels=1):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=seg // 2, radius=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    smooth(o, levels)
    return link(assign(o, m), col)


def cyl(name, loc, r, depth, m, col, verts=24, rot=(0, 0, 0), bevel=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    for p in o.data.polygons:
        p.use_smooth = True
    if bevel:
        mod = o.modifiers.new("bevel", "BEVEL")
        mod.width, mod.segments = bevel, 2
        mod.limit_method = "ANGLE"
    return link(assign(o, m), col)


def torus(name, loc, R, r, m, col, rot=(0, 0, 0), maj=48, mn=16):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=maj, minor_segments=mn,
                                     location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    for p in o.data.polygons:
        p.use_smooth = True
    return link(assign(o, m), col)


def empty(name, loc=(0, 0, 0), parent=None, col="CHAR_quill"):
    o = bpy.data.objects.new(name, None)
    o.empty_display_size = 0.1
    COL[col].objects.link(o)
    o.location = loc
    o.rotation_mode = "XYZ"
    if parent:
        o.parent = parent
    return o


def parent_keep(child, parent):
    bpy.context.view_layer.update()
    child.parent = parent
    child.matrix_parent_inverse = parent.matrix_world.inverted()


def text(name, body, loc, size, m, col, rot=(math.radians(90), 0, 0), extrude=0.004, align="CENTER"):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.align_x, cu.align_y = align, "CENTER"
    cu.size = size
    cu.extrude = extrude
    o = bpy.data.objects.new(name, cu)
    COL[col].objects.link(o)
    o.location = loc
    o.rotation_euler = rot
    o.data.materials.append(m)
    return o


def area(name, loc, rot, energy, size, color, size_y=None, hide_glossy=False):
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
    lo.visible_camera = False
    if hide_glossy:
        lo.visible_glossy = False
        lo.visible_transmission = False
    return lo


def point(name, loc, energy, color, radius=0.1):
    ld = bpy.data.lights.new(name, "POINT")
    ld.energy = energy
    ld.color = color
    ld.shadow_soft_size = radius
    lo = bpy.data.objects.new(name, ld)
    COL["LIGHTS"].objects.link(lo)
    lo.location = loc
    lo.visible_camera = False
    return lo


def spot(name, loc, rot, energy, color, size_deg=60, blend=0.5, radius=0.05):
    ld = bpy.data.lights.new(name, "SPOT")
    ld.energy = energy
    ld.color = color
    ld.spot_size = math.radians(size_deg)
    ld.spot_blend = blend
    ld.shadow_soft_size = radius
    lo = bpy.data.objects.new(name, ld)
    COL["LIGHTS"].objects.link(lo)
    lo.location = loc
    lo.rotation_euler = [math.radians(a) for a in rot]
    lo.visible_camera = False
    return lo


def key_hide(objs, f, hidden):
    for o in objs:
        o.hide_render = hidden
        o.keyframe_insert("hide_render", frame=f)


def hex_rgb(h):
    h = h.lstrip("#")
    srgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb)


# --------------------------------------------------------------------------- materials
M = {}


def noise_rough(m, scale, lo, hi, bump=0.0, bump_scale=90):
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    n = nt.nodes.new("ShaderNodeTexNoise")
    n.inputs["Scale"].default_value = scale
    r = nt.nodes.new("ShaderNodeMapRange")
    r.inputs["To Min"].default_value, r.inputs["To Max"].default_value = lo, hi
    nt.links.new(tc.outputs["Object"], n.inputs["Vector"])
    nt.links.new(n.outputs["Fac"], r.inputs["Value"])
    nt.links.new(r.outputs["Result"], b.inputs["Roughness"])
    if bump:
        g = nt.nodes.new("ShaderNodeTexNoise")
        g.inputs["Scale"].default_value = bump_scale
        bp = nt.nodes.new("ShaderNodeBump")
        bp.inputs["Strength"].default_value = bump
        nt.links.new(tc.outputs["Object"], g.inputs["Vector"])
        nt.links.new(g.outputs["Fac"], bp.inputs["Height"])
        nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return r


def tile_mat(name, base, grout, scale=4.0, rough=0.35):
    m = mat(name, base, rough, coat=0.3)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.inputs["Scale"].default_value = scale
    br.inputs["Mortar Size"].default_value = 0.012
    br.inputs["Color1"].default_value = (*base, 1)
    br.inputs["Color2"].default_value = tuple(c * 0.93 for c in base) + (1,)
    br.inputs["Mortar"].default_value = (*grout, 1)
    br.offset = 0.0
    nt.links.new(tc.outputs["Object"], br.inputs["Vector"])
    nt.links.new(br.outputs["Color"], b.inputs["Base Color"])
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.25
    bp.invert = True
    nt.links.new(br.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m


def build_materials():
    M.clear()
    M["tile"] = tile_mat("wall_tile_white", (0.80, 0.84, 0.82), (0.35, 0.40, 0.39), scale=3.0)
    M["tile_mint"] = tile_mat("wall_tile_mint", hex_rgb("#9FD8C4"), (0.25, 0.32, 0.30), scale=3.0)
    M["floor"] = mat("floor_epoxy", (0.30, 0.36, 0.36), 0.25, coat=0.4)
    M["floor_r"] = noise_rough(M["floor"], 0.8, 0.12, 0.45, bump=0.05)
    M["mat_rubber"] = mat("floor_mat_rubber", (0.03, 0.035, 0.04), 0.7)
    M["ceiling"] = mat("ceiling", (0.55, 0.58, 0.58), 0.8)
    M["strip"] = emis("ceiling_strip", (0.80, 0.92, 1.0), 6.0)
    M["steel"] = mat("brushed_steel", (0.55, 0.57, 0.6), 0.28, metal=1.0)
    M["dark_metal"] = mat("dark_metal", (0.05, 0.06, 0.07), 0.3, metal=1.0)
    M["bench_top"] = mat("bench_top_black", (0.02, 0.025, 0.03), 0.22, coat=0.5)
    M["bench_body"] = mat("bench_cabinet_mint", hex_rgb("#7FBFAE"), 0.4, coat=0.4)
    M["glass"] = mat("glass", (0.92, 0.97, 1.0), 0.02, transmission=1.0)
    M["thick_glass"] = mat("thick_glass", (0.82, 0.92, 0.95), 0.03, transmission=1.0, ior=1.5)
    M["mirror"] = mat("mirror", (0.9, 0.92, 0.95), 0.015, metal=1.0)
    M["brass"] = mat("brass", (0.75, 0.52, 0.18), 0.25, metal=1.0)
    M["red"] = mat("warning_red", (0.70, 0.03, 0.02), 0.3, coat=0.6)
    M["red_lamp"] = mat("red_lamp", (0.2, 0.0, 0.0), 0.3, emit=(1.0, 0.05, 0.02), strength=6.0)
    M["cream"] = mat("enamel_cream", (0.88, 0.83, 0.70), 0.3, coat=0.5)
    M["ink"] = mat("ink", hex_rgb("#1E2A44"), 0.5)
    M["halo_glow"] = emis("halo_glow", hex_rgb("#19C3D6"), 4.0)
    M["amber_glow"] = emis("amber_glow", hex_rgb("#F2A33A"), 5.0)
    M["cyan_glow"] = emis("cyan_glow", hex_rgb("#19C3D6"), 6.0)
    M["lamp_warm"] = emis("lamp_warm", (1.0, 0.75, 0.45), 18.0)
    M["corr_wall"] = mat("corridor_wall", (0.42, 0.33, 0.24), 0.75)
    M["corr_floor"] = mat("corridor_floor", (0.12, 0.10, 0.08), 0.35, coat=0.3)
    M["paper"] = mat("paper", (0.9, 0.9, 0.86), 0.8)
    M["cable"] = mat("cable_rubber", (0.04, 0.04, 0.045), 0.55)
    M["cable_or"] = mat("cable_orange", (0.8, 0.25, 0.03), 0.45, coat=0.3)
    M["stool"] = mat("stool_seat", hex_rgb("#E2553F"), 0.35, coat=0.6)
    M["liquid_g"] = mat("liquid_green", (0.1, 0.8, 0.4), 0.05, transmission=0.9, emit=(0.1, 0.9, 0.4), strength=0.6)
    M["liquid_p"] = mat("liquid_violet", (0.5, 0.1, 0.9), 0.05, transmission=0.9, emit=(0.5, 0.1, 0.9), strength=0.5)
    M["screen_bg"] = emis("screen_bg", (0.02, 0.08, 0.06), 1.0)
    M["screen_txt"] = emis("screen_text", (0.4, 1.0, 0.75), 4.0)
    M["screen_red"] = emis("screen_red", (1.0, 0.08, 0.05), 6.0)
    M["holo"] = holo_mat("holo", hex_rgb("#19C3D6"), 2.5)
    M["holo_red"] = emis("holo_red", (1.0, 0.1, 0.06), 8.0)
    M["particle"] = emis("particle", (0.6, 1.0, 1.0), 12.0)
    M["smudge"] = mat("glass_smudge", (0.9, 0.92, 0.95), 0.45, alpha=0.35)
    M["fog"] = mat("breath_fog", (0.95, 0.97, 1.0), 0.6, alpha=0.5)
    M["print"] = mat("footprint", (0.0, 0.0, 0.0), 0.15, alpha=0.55)
    M["water"] = mat("rain_water", (0.75, 0.85, 1.0), 0.1, emit=(0.6, 0.75, 1.0), strength=1.2, alpha=0.4)
    return M


def holo_mat(name, color, strength):
    """Fresnel-rimmed translucent emissive shell (reads as a hologram)."""
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    out = nt.nodes["Material Output"]
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.35
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = (*color, 1)
    e.inputs["Strength"].default_value = strength
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = 0.18, 1.0
    nt.links.new(lw.outputs["Facing"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], mix.inputs["Fac"])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(e.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


def water_shell_mat(name):
    """Water running over an invisible body: clear centre, bright refracting/reflecting rim, streaks."""
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    out = nt.nodes["Material Output"]
    glass = nt.nodes.new("ShaderNodeBsdfPrincipled")
    glass.inputs["Base Color"].default_value = (0.85, 0.93, 1.0, 1)
    glass.inputs["Roughness"].default_value = 0.04
    glass.inputs["Transmission Weight"].default_value = 1.0
    glass.inputs["IOR"].default_value = 1.33
    glass.inputs["Emission Color"].default_value = (0.55, 0.75, 1.0, 1)
    glass.inputs["Emission Strength"].default_value = 0.15
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.5
    # vertical streaks: stretched noise scrolling downward
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (14.0, 14.0, 1.6)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 3.0
    nz.inputs["Detail"].default_value = 3
    nt.links.new(mp.outputs["Vector"], nz.inputs["Vector"])
    st = nt.nodes.new("ShaderNodeMapRange")
    st.inputs["From Min"].default_value, st.inputs["From Max"].default_value = 0.5, 0.62
    nt.links.new(nz.outputs["Fac"], st.inputs["Value"])
    mx = nt.nodes.new("ShaderNodeMath")
    mx.operation = "MAXIMUM"
    nt.links.new(lw.outputs["Facing"], mx.inputs[0])
    nt.links.new(st.outputs["Result"], mx.inputs[1])
    amt = nt.nodes.new("ShaderNodeMath")
    amt.operation = "MULTIPLY"
    amt.inputs[1].default_value = 1.0
    amt.name = "water_amount"
    nt.links.new(mx.outputs[0], amt.inputs[0])
    clamp = nt.nodes.new("ShaderNodeClamp")
    nt.links.new(amt.outputs[0], clamp.inputs["Value"])
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(clamp.outputs[0], mix.inputs["Fac"])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(glass.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    m["mapping"] = mp.name
    return m


def vanish_mat(base):
    """Copy of a character material that dissolves by the object's custom property 'vanish' (0..1),
    with a thin cyan light-bending edge where the dissolve front passes."""
    m = base.copy()
    m.name = base.name + "_vanish"
    nt = m.node_tree
    out = nt.nodes["Material Output"]
    bsdf = nt.nodes["Principled BSDF"]
    attr = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_type = "OBJECT"
    attr.attribute_name = "vanish"
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 9.0
    nz.inputs["Detail"].default_value = 2
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    # remap noise to 0.1..0.9 so vanish=0 is fully solid and vanish=1 fully gone
    nr = nt.nodes.new("ShaderNodeMapRange")
    nr.inputs["From Min"].default_value, nr.inputs["From Max"].default_value = 0.3, 0.7
    nr.inputs["To Min"].default_value, nr.inputs["To Max"].default_value = 0.08, 0.92
    nt.links.new(nz.outputs["Fac"], nr.inputs["Value"])
    diff = nt.nodes.new("ShaderNodeMath")
    diff.operation = "SUBTRACT"
    nt.links.new(attr.outputs["Fac"], diff.inputs[0])
    nt.links.new(nr.outputs["Result"], diff.inputs[1])
    gone = nt.nodes.new("ShaderNodeMath")
    gone.operation = "GREATER_THAN"
    gone.inputs[1].default_value = 0.0
    nt.links.new(diff.outputs[0], gone.inputs[0])
    edge = nt.nodes.new("ShaderNodeMath")
    edge.operation = "ABSOLUTE"
    nt.links.new(diff.outputs[0], edge.inputs[0])
    edge2 = nt.nodes.new("ShaderNodeMapRange")
    edge2.inputs["From Min"].default_value, edge2.inputs["From Max"].default_value = 0.06, 0.0
    nt.links.new(edge.outputs[0], edge2.inputs["Value"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(gone.outputs[0], mix.inputs["Fac"])
    nt.links.new(bsdf.outputs[0], mix.inputs[1])
    nt.links.new(tr.outputs[0], mix.inputs[2])
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*hex_rgb("#19C3D6"), 1)
    em.inputs["Strength"].default_value = 12.0
    em_mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(edge2.outputs["Result"], em_mix.inputs["Fac"])
    nt.links.new(mix.outputs[0], em_mix.inputs[1])
    nt.links.new(em.outputs[0], em_mix.inputs[2])
    nt.links.new(em_mix.outputs[0], out.inputs["Surface"])
    return m


# --------------------------------------------------------------------------- the lab set
# Lab floor z=0, x in [-5, 5], y in [-3, 5]. Right wall (x=5) holds the soundproof observation window
# (y 0.2..2.8) and the round vault door (centre y=-1.6). The corridor beyond runs x 5.15..8.
LAB = dict(x0=-5.0, x1=5.0, y0=-3.0, y1=5.0, h=3.0)
WIN = dict(y0=0.2, y1=2.8, z0=0.85, z1=2.35)
DOOR = dict(y=-1.6, z=1.05, r=0.95)
MACHINE = Vector((7.15, 1.2, 0.0))
LEVER_LOC = Vector((-4.9, -1.2, 1.35))
PLAQUE_LOC = Vector((4.92, -0.25, 1.3))
MIRROR_LOC = Vector((-1.2, 3.3, 0.0))
HALO_C = Vector((0.6, 4.25, 1.55))
MAT_C = Vector((0.6, 1.4, 0.0))
SET = {}


def build_lab(sprinkler_heads=True):
    x0, x1, y0, y1, h = LAB["x0"], LAB["x1"], LAB["y0"], LAB["y1"], LAB["h"]
    box("floor", (0, 1, -0.05), (x1 - x0, y1 - y0, 0.1), M["floor"], "ENV_mid")
    box("ceiling", (0, 1, h + 0.05), (x1 - x0, y1 - y0, 0.1), M["ceiling"], "ENV_far")
    box("wall_back", (0, y1 + 0.075, h / 2), (x1 - x0, 0.15, h), M["tile"], "ENV_far")
    box("wall_front", (0, y0 - 0.075, h / 2), (x1 - x0, 0.15, h), M["tile"], "ENV_far")
    box("wall_left", (x0 - 0.075, 1, h / 2), (0.15, y1 - y0, h), M["tile"], "ENV_far")
    # mint dado band around the room
    box("dado_back", (0, y1 - 0.005, 0.5), (x1 - x0, 0.02, 1.0), M["tile_mint"], "ENV_far")
    box("dado_left", (x0 + 0.005, 1, 0.5), (0.02, y1 - y0, 1.0), M["tile_mint"], "ENV_far")
    # right wall with window + door openings (x = 5 .. 5.15)
    wx = x1 + 0.075
    dy0, dy1 = DOOR["y"] - 1.0, DOOR["y"] + 1.0
    segs = [(y0, dy0), (dy1, WIN["y0"]), (WIN["y1"], y1)]
    for i, (a, b) in enumerate(segs):
        box(f"wall_right_{i}", (wx, (a + b) / 2, h / 2), (0.15, b - a, h), M["tile"], "ENV_mid")
    box("wall_right_door_top", (wx, DOOR["y"], (2.1 + h) / 2), (0.15, 2.0, h - 2.1), M["tile"], "ENV_mid")
    box("wall_right_win_sill", (wx, (WIN["y0"] + WIN["y1"]) / 2, WIN["z0"] / 2), (0.15, WIN["y1"] - WIN["y0"], WIN["z0"]),
        M["tile"], "ENV_mid")
    box("wall_right_win_head", (wx, (WIN["y0"] + WIN["y1"]) / 2, (WIN["z1"] + h) / 2),
        (0.15, WIN["y1"] - WIN["y0"], h - WIN["z1"]), M["tile"], "ENV_mid")
    # thick soundproof glass + steel frame
    wc = (WIN["y0"] + WIN["y1"]) / 2
    SET["window"] = box("window_glass", (wx, wc, (WIN["z0"] + WIN["z1"]) / 2),
                        (0.06, WIN["y1"] - WIN["y0"], WIN["z1"] - WIN["z0"]), M["thick_glass"], "ENV_mid")
    for nm, loc, size in (("win_frame_b", (x1 - 0.01, wc, WIN["z0"]), (0.08, WIN["y1"] - WIN["y0"] + 0.1, 0.08)),
                          ("win_frame_t", (x1 - 0.01, wc, WIN["z1"]), (0.08, WIN["y1"] - WIN["y0"] + 0.1, 0.08)),
                          ("win_frame_l", (x1 - 0.01, WIN["y0"], (WIN["z0"] + WIN["z1"]) / 2), (0.08, 0.08, WIN["z1"] - WIN["z0"])),
                          ("win_frame_r", (x1 - 0.01, WIN["y1"], (WIN["z0"] + WIN["z1"]) / 2), (0.08, 0.08, WIN["z1"] - WIN["z0"])),
                          ("win_mullion", (x1 - 0.01, wc, (WIN["z0"] + WIN["z1"]) / 2), (0.05, 0.05, WIN["z1"] - WIN["z0"]))):
        box(nm, loc, size, M["steel"], "ENV_mid", bevel=0.01)
    # vault door: thick round steel disc hinged on its +y edge; frame ring around the opening
    hinge = empty("door_hinge", (x1 - 0.02, DOOR["y"] + 0.98, 0), col="ENV_mid")
    door = cyl("vault_door", (x1 - 0.06, DOOR["y"], DOOR["z"]), DOOR["r"], 0.16, M["steel"], "ENV_mid", verts=48,
               rot=(0, math.radians(90), 0), bevel=0.02)
    torus("vault_ring", (x1 - 0.15, DOOR["y"], DOOR["z"]), 0.62, 0.04, M["dark_metal"], "ENV_mid", rot=(0, math.radians(90), 0))
    wheel = torus("vault_wheel", (x1 - 0.2, DOOR["y"], DOOR["z"]), 0.28, 0.025, M["brass"], "ENV_mid", rot=(0, math.radians(90), 0))
    spokes = []
    for k in range(3):
        a = k * math.pi / 3
        spokes.append(box(f"vault_spoke_{k}", (x1 - 0.2, DOOR["y"], DOOR["z"]), (0.03, 0.56, 0.03), M["brass"], "ENV_mid",
                          rot=(a, 0, 0)))
    wheel_pivot = empty("vault_wheel_pivot", (x1 - 0.2, DOOR["y"], DOOR["z"]), col="ENV_mid")
    for o in [wheel] + spokes:
        parent_keep(o, wheel_pivot)
    for o in (door, bpy.data.objects["vault_ring"], wheel_pivot):
        parent_keep(o, hinge)
    torus("vault_frame", (x1 - 0.005, DOOR["y"], DOOR["z"]), 1.0, 0.07, M["dark_metal"], "ENV_mid", rot=(0, math.radians(90), 0))
    box("vault_jamb_fill_top", (x1 + 0.075, DOOR["y"], 2.07), (0.15, 2.0, 0.06), M["tile"], "ENV_mid")
    SET["door_hinge"], SET["door_wheel"] = hinge, wheel_pivot
    # LOCKED lamp above the door
    SET["locked_lamp_mat"] = mat("locked_lamp", (0.15, 0.02, 0.02), 0.3, emit=(1.0, 0.04, 0.02), strength=0.0)
    box("locked_lamp_base", (x1 - 0.03, DOOR["y"], 2.35), (0.06, 0.42, 0.16), M["dark_metal"], "ENV_mid", bevel=0.01)
    box("locked_lamp", (x1 - 0.07, DOOR["y"], 2.35), (0.03, 0.38, 0.12), SET["locked_lamp_mat"], "ENV_mid")
    text("locked_txt", "LOCKED", (x1 - 0.09, DOOR["y"], 2.35), 0.075, M["cream"], "ENV_mid",
         rot=(math.radians(90), 0, math.radians(-90)))
    SET["locked_light"] = point("locked_light", (x1 - 0.35, DOOR["y"], 2.3), 0.0, (1.0, 0.05, 0.02), 0.08)
    # plaque NEVER TEST ALONE
    box("plaque", (PLAQUE_LOC.x, PLAQUE_LOC.y, PLAQUE_LOC.z), (0.02, 0.62, 0.36), M["red"], "ENV_mid", bevel=0.01)
    for i, line in enumerate(("NEVER", "TEST ALONE")):
        text(f"plaque_txt_{i}", line, (PLAQUE_LOC.x - 0.015, PLAQUE_LOC.y, PLAQUE_LOC.z + 0.07 - i * 0.13),
             0.1 if i == 0 else 0.085, M["cream"], "ENV_mid", rot=(math.radians(90), 0, math.radians(-90)))
    # sprinkler lever (left wall)
    lx, ly, lz = LEVER_LOC
    box("lever_plate", (lx - 0.06, ly, lz), (0.03, 0.34, 0.55), M["red"], "ENV_mid", bevel=0.01)
    text("lever_txt", "SPRINKLER", (lx - 0.04, ly, lz + 0.2), 0.05, M["cream"], "ENV_mid",
         rot=(math.radians(90), 0, math.radians(90)))
    lp = empty("lever_pivot", (lx, ly, lz + 0.06), col="ENV_mid")
    arm = box("lever_arm", (lx + 0.12, ly, lz + 0.06), (0.24, 0.035, 0.035), M["steel"], "ENV_mid", bevel=0.008)
    grip = cyl("lever_grip", (lx + 0.25, ly, lz + 0.06), 0.035, 0.14, M["red"], "ENV_mid", verts=16,
               rot=(math.radians(90), 0, 0))
    for o in (arm, grip):
        parent_keep(o, lp)
    lp.rotation_euler = (0, math.radians(-35), 0)
    SET["lever"] = lp
    box("pipe_v", (lx + 0.08, ly - 0.45, 1.9), (0.06, 0.06, 2.2), M["red"], "ENV_mid", bevel=0.01)
    # ceiling strips + sprinkler heads
    SET["strips"] = []
    for i, x in enumerate((-3.0, 0.0, 3.0)):
        for j, y in enumerate((-1.0, 2.0)):
            s = box(f"strip_{i}{j}", (x, y + 0.5, h - 0.01), (0.25, 2.2, 0.03), M["strip"], "ENV_far")
            SET["strips"].append(s)
    SET["sprinklers"] = []
    if sprinkler_heads:
        for x in (-3.5, -1.5, 0.5, 2.5, 4.2):
            for y in (-1.8, 0.6, 3.2):
                cyl(f"sprk_{x}_{y}", (x, y, h - 0.04), 0.025, 0.08, M["brass"], "ENV_far", verts=10)
                SET["sprinklers"].append(cyl(f"sprk_d_{x}_{y}", (x, y, h - 0.09), 0.05, 0.012, M["brass"], "ENV_far", verts=12))
    build_halo()
    build_benches()
    build_mirror()
    build_floor_mat()
    build_corridor()


def build_halo():
    c = HALO_C
    torus("halo_ring", c, 1.05, 0.11, M["steel"], "ENV_far", rot=(math.radians(90), 0, 0), maj=64)
    torus("halo_glow_ring", c + Vector((0, -0.08, 0)), 0.92, 0.03, M["halo_glow"], "ENV_far", rot=(math.radians(90), 0, 0), maj=64)
    for k in range(8):
        a = k * math.pi / 4
        p = c + Vector((math.cos(a) * 1.05, -0.14, math.sin(a) * 1.05))
        cyl(f"halo_lens_{k}", p, 0.16, 0.05, M["glass"], "ENV_far", verts=24, rot=(math.radians(90), 0, 0))
        torus(f"halo_lens_rim_{k}", p, 0.165, 0.018, M["brass"], "ENV_far", rot=(math.radians(90), 0, 0))
    for sx in (-1, 1):
        box(f"halo_leg_{sx}", (c.x + sx * 1.25, c.y, c.z / 2), (0.12, 0.3, c.z), M["dark_metal"], "ENV_far", bevel=0.02)
    box("halo_base", (c.x, c.y, 0.06), (2.9, 0.6, 0.12), M["dark_metal"], "ENV_far", bevel=0.02)
    SET["halo_light"] = point("halo_light", c + Vector((0, -0.6, 0)), 60.0, hex_rgb("#19C3D6"), 0.6)


def build_benches():
    # centre island bench (left of the floor mat) with prisms, beakers, Mote's habitat
    bx, by = -2.4, 1.0
    box("bench_c_body", (bx, by, 0.42), (2.2, 0.8, 0.84), M["bench_body"], "ENV_mid", bevel=0.02)
    box("bench_c_top", (bx, by, 0.87), (2.3, 0.9, 0.06), M["bench_top"], "ENV_mid", bevel=0.01)
    SET["bench_top_z"] = 0.9
    for i, (dx, dy, hh, m) in enumerate(((-0.8, -0.2, 0.22, M["liquid_g"]), (-0.6, 0.15, 0.3, M["liquid_p"]),
                                         (0.75, -0.25, 0.18, M["liquid_g"]))):
        cyl(f"beaker_{i}", (bx + dx, by + dy, 0.9 + hh / 2), 0.07, hh, M["glass"], "ENV_mid", verts=20)
        cyl(f"beaker_liq_{i}", (bx + dx, by + dy, 0.9 + hh * 0.3), 0.062, hh * 0.55, m, "ENV_mid", verts=20)
    for i, dx in enumerate((-0.2, 0.15)):
        bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=0.09, depth=0.2, location=(bx + dx, by - 0.25, 1.0),
                                        rotation=(math.radians(90), 0, 0))
        p = bpy.context.object
        p.name = f"prism_{i}"
        link(assign(p, M["glass"]), "ENV_mid")
    # Mote's habitat: glass box with sawdust floor
    hx, hy = bx + 0.35, by + 0.15
    SET["habitat"] = Vector((hx, hy, 0.9))
    box("habitat_glass", (hx, hy, 1.06), (0.42, 0.32, 0.3), M["glass"], "ENV_mid")
    box("habitat_floor", (hx, hy, 0.915), (0.4, 0.3, 0.02), mat("sawdust", (0.6, 0.45, 0.25), 0.9), "ENV_mid")
    # bench lamp (warm practical)
    cyl("bench_lamp_post", (bx - 1.0, by + 0.3, 1.15), 0.015, 0.5, M["dark_metal"], "ENV_mid", verts=10)
    sphere("bench_lamp_shade", (bx - 0.9, by + 0.3, 1.38), (0.12, 0.12, 0.08), M["dark_metal"], "ENV_mid", seg=16)
    sphere("bench_lamp_bulb", (bx - 0.9, by + 0.3, 1.33), (0.05, 0.05, 0.03), M["lamp_warm"], "ENV_mid", seg=12)
    SET["bench_lamp"] = spot("bench_lamp_light", (bx - 0.9, by + 0.3, 1.32), (0, 0, 0), 60, (1.0, 0.68, 0.38), 100, 0.6, 0.06)
    # left wall bench with shelves and cable coils
    box("bench_l_body", (-4.55, 1.5, 0.42), (0.8, 5.0, 0.84), M["bench_body"], "ENV_far", bevel=0.02)
    box("bench_l_top", (-4.55, 1.5, 0.87), (0.9, 5.1, 0.06), M["bench_top"], "ENV_far", bevel=0.01)
    for k, z in enumerate((1.5, 2.1)):
        box(f"shelf_l_{k}", (-4.8, 1.5, z), (0.35, 5.0, 0.04), M["steel"], "ENV_far")
        y = -0.8
        while y < 3.9:
            w = random.uniform(0.1, 0.25)
            hh = random.uniform(0.12, 0.35)
            c = random.choice((M["liquid_g"], M["bench_body"], M["cream"], M["red"], M["glass"], M["steel"]))
            if random.random() < 0.5:
                box(f"shelf_item_{k}_{y:.2f}", (-4.8, y + w / 2, z + hh / 2 + 0.02), (0.2, w, hh), c, "ENV_far", bevel=0.01)
            else:
                cyl(f"shelf_jar_{k}_{y:.2f}", (-4.8, y + w / 2, z + hh / 2 + 0.02), w / 2.4, hh, c, "ENV_far", verts=14)
            y += w + random.uniform(0.03, 0.12)
    # cable coil on the floor (near-layer candidate)
    SET["coil"] = torus("cable_coil", (1.9, 3.0, 0.05), 0.28, 0.045, M["cable_or"], "ENV_near", maj=40)
    torus("cable_coil_2", (1.9, 3.0, 0.13), 0.25, 0.04, M["cable"], "ENV_near", maj=40)
    # stool
    st = empty("stool_root", (-1.0, -0.2, 0), col="ENV_mid")
    parts = [cyl("stool_seat", (-1.0, -0.2, 0.62), 0.2, 0.06, M["stool"], "ENV_mid", verts=24, bevel=0.01),
             cyl("stool_post", (-1.0, -0.2, 0.31), 0.025, 0.6, M["steel"], "ENV_mid", verts=10),
             cyl("stool_base", (-1.0, -0.2, 0.02), 0.2, 0.03, M["steel"], "ENV_mid", verts=20)]
    for p in parts:
        parent_keep(p, st)
    SET["stool"] = st
    # papers on the bench end (blow away in S15)
    SET["papers"] = []
    for i in range(7):
        bpy.ops.mesh.primitive_plane_add(size=1, location=(-1.5 + random.uniform(-0.15, 0.1), 0.8 + random.uniform(-0.2, 0.2), 0.905 + i * 0.002))
        p = bpy.context.object
        p.name = f"paper_{i}"
        p.scale = (0.21, 0.29, 1)
        p.rotation_euler.z = random.uniform(-0.4, 0.4)
        link(assign(p, M["paper"]), "ENV_mid")
        SET["papers"].append(p)
    # fire extinguisher by the door (near-layer candidate)
    cyl("extinguisher", (4.6, -2.6, 0.32), 0.09, 0.6, M["red"], "ENV_near", verts=20, bevel=0.02)
    sphere("extinguisher_top", (4.6, -2.6, 0.64), (0.09, 0.09, 0.06), M["red"], "ENV_near", seg=16)


def build_mirror():
    mx, my = MIRROR_LOC.x, MIRROR_LOC.y
    box("mirror_frame", (mx, my + 0.03, 1.15), (0.98, 0.05, 1.9), M["brass"], "ENV_mid", bevel=0.02)
    SET["mirror"] = box("mirror_glass", (mx, my, 1.15), (0.88, 0.02, 1.8), M["mirror"], "ENV_mid")
    for sx in (-1, 1):
        box(f"mirror_foot_{sx}", (mx + sx * 0.45, my + 0.03, 0.04), (0.08, 0.5, 0.08), M["brass"], "ENV_mid", bevel=0.01)


def build_floor_mat():
    box("floor_mat", (MAT_C.x, MAT_C.y, 0.008), (1.8, 1.8, 0.016), M["mat_rubber"], "ENV_mid", bevel=0.005)
    # yellow test-spot ring
    torus("mat_ring", (MAT_C.x, MAT_C.y, 0.018), 0.45, 0.012, mat("mat_ring", (0.85, 0.65, 0.05), 0.4), "ENV_mid", maj=48, mn=6)


def build_corridor():
    x0, x1 = 5.15, 8.2
    box("corr_floor", ((x0 + x1) / 2, 0.5, -0.05), (x1 - x0, 10, 0.1), M["corr_floor"], "ENV_far")
    box("corr_ceiling", ((x0 + x1) / 2, 0.5, 2.85), (x1 - x0, 10, 0.1), M["corr_wall"], "ENV_far")
    box("corr_wall_far", (x1 + 0.075, 0.5, 1.4), (0.15, 10, 2.8), M["corr_wall"], "ENV_far")
    for y in (-4.4, 5.4):
        box(f"corr_end_{y}", ((x0 + x1) / 2, y, 1.4), (x1 - x0, 0.15, 2.8), M["corr_wall"], "ENV_far")
    # emergency reversal machine (faces -X, toward the window)
    mx, my = MACHINE.x, MACHINE.y
    box("machine_body", (mx, my, 0.6), (0.7, 1.0, 1.2), mat("machine_paint", (0.12, 0.13, 0.14), 0.35, coat=0.5), "ENV_far", bevel=0.04)
    box("machine_top", (mx + 0.05, my, 1.32), (0.6, 0.9, 0.24), mat("machine_hood", (0.55, 0.32, 0.06), 0.35, coat=0.6), "ENV_far", bevel=0.04)
    SET["machine_dial_mat"] = mat("machine_dial", (0.1, 0.05, 0.0), 0.3, emit=hex_rgb("#F2A33A"), strength=2.0)
    cyl("machine_dial", (mx - 0.36, my - 0.2, 0.9), 0.17, 0.03, SET["machine_dial_mat"], "ENV_far", verts=32,
        rot=(0, math.radians(90), 0))
    torus("machine_dial_rim", (mx - 0.37, my - 0.2, 0.9), 0.18, 0.015, M["brass"], "ENV_far", rot=(0, math.radians(90), 0))
    needle_p = empty("machine_needle_pivot", (mx - 0.39, my - 0.2, 0.9), col="ENV_far")
    needle = box("machine_needle", (mx - 0.39, my - 0.2, 0.97), (0.01, 0.012, 0.13), M["red"], "ENV_far")
    parent_keep(needle, needle_p)
    needle_p.rotation_euler.x = math.radians(70)
    SET["needle"] = needle_p
    lp = empty("machine_lever_pivot", (mx - 0.36, my + 0.25, 0.75), col="ENV_far")
    la = box("machine_lever_arm", (mx - 0.36, my + 0.25, 1.0), (0.04, 0.04, 0.5), M["steel"], "ENV_far", bevel=0.01)
    lk = sphere("machine_lever_knob", (mx - 0.36, my + 0.25, 1.27), (0.07, 0.07, 0.07), M["red"], "ENV_far", seg=16)
    for o in (la, lk):
        parent_keep(o, lp)
    lp.rotation_euler.y = math.radians(-25)
    SET["machine_lever"] = lp
    text("machine_txt", "REVERSAL", (mx - 0.355, my, 1.32), 0.07, M["ink"], "ENV_far",
         rot=(math.radians(90), 0, math.radians(-90)))
    # warm corridor practicals
    for i, y in enumerate((-2.5, 0.6, 3.6)):
        sphere(f"corr_bulb_{i}", (7.9, y, 2.3), (0.08, 0.08, 0.08), M["lamp_warm"], "ENV_far", seg=12)
        point(f"corr_light_{i}", (7.6, y, 2.2), 55.0, (1.0, 0.68, 0.38), 0.15)
    SET["machine_light"] = point("machine_light", (mx - 0.6, my, 1.5), 20.0, hex_rgb("#F2A33A"), 0.2)


def lab_lights(warm_lamp=True):
    """Interior tungsten + cool fluorescent recipe. Key 1 : rim ~0.7 : fill ~0.15 (prompt book 3A.4)."""
    world = bpy.data.worlds.new("lab_world")
    scene.world = world
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.004, 0.006, 0.008, 1)
    for i, x in enumerate((-3.0, 0.0, 3.0)):
        for j, y in enumerate((-1.0, 2.0)):
            area(f"ceiling_area_{i}{j}", (x, y + 0.5, LAB["h"] - 0.08), (0, 0, 0), 70, 0.4, (0.80, 0.92, 1.0),
                 size_y=2.2, hide_glossy=True)
    SET["fill"] = area("fill_cam_side", (0.5, -2.6, 1.6), (85, 0, 0), 40, 3.0, (0.65, 0.75, 0.95))


# --------------------------------------------------------------------------- characters
def biped(prefix, col, spec):
    """Rounded biped following the prompt book 3.5 hierarchy:
    root -> body -> neck -> head parts; eye lid-scale -> eye pivot -> pupil; shoulders -> arm + hand;
    legs and feet solved in world space every frame from foot plants."""
    hip = spec["hip"]
    R = {"prefix": prefix, "col": col, "spec": spec, "objs": [], "hip": hip}
    root = empty(f"{prefix}_root", col=col)
    body = empty(f"{prefix}_body", (0, 0, hip), root, col)
    R["root"], R["body"] = root, body

    def add(o, parent):
        parent_keep(o, parent)
        R["objs"].append(o)
        return o

    for i, (off, sc, m, kind) in enumerate(spec["torso"]):
        loc = Vector(off) + Vector((0, 0, hip))
        o = sphere(f"{prefix}_torso_{i}", loc, sc, m, col, seg=24) if kind == "s" else rbox(f"{prefix}_torso_{i}", loc, sc, m, col)
        add(o, body)
    neck = empty(f"{prefix}_neck", (0, 0, spec["neck_h"]), body, col)
    R["neck"] = neck
    bpy.context.view_layer.update()
    HC = Vector((0, 0, hip + spec["neck_h"])) + Vector(spec["head_off"])
    R["head_c"] = HC
    hs = spec["head_scale"]
    if spec["head_kind"] == "box":
        head = rbox(f"{prefix}_head", HC, (hs[0] * 2, hs[1] * 2, hs[2] * 2), spec["skin"], col, levels=2)
        head.modifiers["subd"].levels = head.modifiers["subd"].render_levels = 3
    else:
        head = sphere(f"{prefix}_head", HC, hs, spec["skin"], col, seg=32)
    add(head, neck)
    face_y = -hs[1] * (0.9 if spec["head_kind"] == "box" else 0.86)
    nose = spec.get("nose")
    if nose:
        add(sphere(f"{prefix}_nose", HC + Vector((0, face_y - nose[1] * 0.6, nose[3])), nose[:3], spec["skin"], col, seg=16), neck)
    R["eyes"] = {}
    es = spec["eye_scale"]
    for side, sx in (("L", spec["eye_x"]), ("R", -spec["eye_x"])):
        ec = HC + Vector((sx, face_y + es[1] * 0.45, spec["eye_z"]))
        lid = empty(f"{prefix}_lid_{side}", ec, None, col)
        pivot = empty(f"{prefix}_eye_{side}", ec, None, col)
        eye = sphere(f"{prefix}_eyeball_{side}", ec, es, M["eye_white"], col, seg=20)
        pupil = sphere(f"{prefix}_pupil_{side}", ec + Vector((0, -es[1] * 0.85, 0)), (es[0] * 0.5, es[1] * 0.25, es[2] * 0.5),
                       M["pupil"], col, seg=16)
        add(pupil, pivot)
        add(eye, lid)
        parent_keep(pivot, lid)
        brow = sphere(f"{prefix}_brow_{side}", ec + Vector((0, -0.01, es[2] + spec["brow_gap"])), spec["brow_scale"],
                      spec["brow_mat"], col, seg=12)
        add(brow, neck)
        parent_keep(lid, neck)
        R["eyes"][side] = (pivot, lid, brow, brow.location.z)
    # mouth: lower half torus arc
    bpy.ops.mesh.primitive_torus_add(major_radius=spec["mouth_r"], minor_radius=spec["mouth_r"] * 0.2, location=(0, 0, 0))
    mouth = bpy.context.object
    mouth.name = f"{prefix}_mouth"
    bm = bmesh.new()
    bm.from_mesh(mouth.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.y > 0.004], context="VERTS")
    bm.to_mesh(mouth.data)
    bm.free()
    mouth.rotation_euler = (math.radians(90), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    mouth.location = HC + Vector((0, face_y - (0.02 if spec["head_kind"] == "box" else 0.005), spec["mouth_z"]))
    link(assign(mouth, M["mouth"]), col)
    add(mouth, neck)
    R["mouth"] = mouth
    # overlap pivot (hair / braids / goggles strap) lags the head
    R["lag"] = empty(f"{prefix}_lag", HC, None, col)
    parent_keep(R["lag"], neck)
    # arms
    R["arms"] = {}
    sx0, sz0 = spec["shoulder"]
    for side, sx in (("L", 1), ("R", -1)):
        sh = empty(f"{prefix}_shoulder_{side}", (sx * sx0, 0, sz0), body, col)
        L = spec["arm_len"]
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=spec["arm_r"], depth=L, location=(0, 0, -L / 2))
        arm = bpy.context.object
        arm.name = f"{prefix}_arm_{side}"
        link(assign(smooth(arm, 1), spec["sleeve"]), col)
        bpy.context.view_layer.update()
        arm.location = sh.matrix_world.translation + Vector((0, 0, -L / 2))
        hand = sphere(f"{prefix}_hand_{side}", sh.matrix_world.translation + Vector((0, 0, -L - spec["hand"][2] * 0.6)),
                      spec["hand"], spec["hand_mat"], col, seg=16)
        add(arm, sh)
        add(hand, sh)
        R["arms"][side] = sh
        R[f"hand_{side}"] = hand
    # legs (origin at hip, extend along -Z) and feet
    R["legs"], R["feet"] = {}, {}
    for side in ("L", "R"):
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=spec["leg_r"], depth=1.0, location=(0, 0, -0.5))
        lg = bpy.context.object
        bpy.ops.object.transform_apply(location=True)
        lg.name = f"{prefix}_leg_{side}"
        link(assign(smooth(lg, 1), spec["leg_mat"]), col)
        lg.rotation_mode = "QUATERNION"
        R["legs"][side] = lg
        ft = sphere(f"{prefix}_foot_{side}", (0, 0, 0), spec["foot"], spec["foot_mat"], col, seg=20)
        R["feet"][side] = ft
        R["objs"] += [lg, ft]
    R["head"] = head
    return R


def all_objs(R):
    return [o for o in bpy.data.objects if o.name.startswith(R["prefix"] + "_") and o.type in ("MESH", "FONT", "CURVE")]


def build_char_mats():
    M["eye_white"] = mat("eye_white", (0.92, 0.92, 0.9), 0.15, coat=0.5)
    M["pupil"] = mat("pupil", (0.01, 0.01, 0.012), 0.1, coat=0.8)
    M["mouth"] = mat("mouth_dark", (0.12, 0.03, 0.03), 0.6)
    # Quill
    M["q_skin"] = mat("quill_skin", (0.80, 0.55, 0.40), 0.55, sheen=0.2)
    M["q_suit"] = mat("quill_suit_graphite", hex_rgb("#2B2E33"), 0.45, coat=0.25)
    hexn = M["q_suit"].node_tree
    b = hexn.nodes["Principled BSDF"]
    vor = hexn.nodes.new("ShaderNodeTexVoronoi")
    vor.inputs["Scale"].default_value = 60
    vor.feature = "DISTANCE_TO_EDGE"
    tc = hexn.nodes.new("ShaderNodeTexCoord")
    hexn.links.new(tc.outputs["Object"], vor.inputs["Vector"])
    bp = hexn.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.2
    hexn.links.new(vor.outputs["Distance"], bp.inputs["Height"])
    hexn.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    M["q_shirt"] = mat("quill_undershirt", (0.75, 0.76, 0.74), 0.7, sheen=0.4)
    M["q_trouser"] = mat("quill_trousers", (0.16, 0.17, 0.2), 0.7, sheen=0.3)
    M["q_boot"] = mat("quill_boots", (0.06, 0.05, 0.05), 0.35, coat=0.5)
    M["q_brow"] = mat("quill_brows_white", hex_rgb("#EDEBE6"), 0.8, sheen=1.0)
    M["q_glove"] = mat("quill_gloves", hex_rgb("#2B2E33"), 0.4, coat=0.4)
    # Juno
    M["j_skin"] = mat("juno_skin", (0.55, 0.33, 0.22), 0.55, sheen=0.2)
    M["j_coat"] = mat("juno_coat_coral", hex_rgb("#E2553F"), 0.5, sheen=0.6)
    M["j_sweater"] = mat("juno_sweater_mustard", hex_rgb("#D9A520"), 0.8, sheen=1.0)
    M["j_hair"] = mat("juno_hair", (0.04, 0.02, 0.015), 0.5, coat=0.3)
    M["j_tie"] = mat("juno_hair_ties_coral", hex_rgb("#E2553F"), 0.3, coat=0.6)
    M["j_pants"] = mat("juno_trousers_ink", hex_rgb("#1E2A44"), 0.7, sheen=0.3)
    M["j_shoe"] = mat("juno_shoes", (0.85, 0.82, 0.75), 0.35, coat=0.5)
    M["j_glass"] = mat("juno_glasses", (0.9, 0.95, 1.0), 0.02, transmission=1.0)
    M["j_frame"] = mat("juno_glasses_frame", hex_rgb("#1E2A44"), 0.3, coat=0.6)
    M["clipboard"] = mat("clipboard", (0.45, 0.3, 0.15), 0.6)
    M["mug"] = mat("mug_white", (0.85, 0.85, 0.82), 0.25, coat=0.6)
    # Scanner, Mote
    M["s_body"] = mat("scanner_mint_metal", hex_rgb("#9FD8C4"), 0.3, metal=0.6)
    M["m_fur"] = mat("mote_fur_sandy", (0.75, 0.55, 0.30), 0.85, sheen=1.0)
    M["m_pink"] = mat("mote_pink", (0.9, 0.5, 0.5), 0.6)


def build_quill(undressed=False):
    torso_mat = M["q_shirt"] if undressed else M["q_suit"]
    leg_mat = M["q_trouser"] if undressed else M["q_suit"]
    spec = dict(
        hip=0.95,
        torso=[((0, 0, 0.33), (0.20, 0.16, 0.42), torso_mat, "s"),
               ((0, 0, 0.05), (0.17, 0.14, 0.16), leg_mat, "s"),
               ((0, 0, 0.66), (0.075, 0.07, 0.1), M["q_skin"], "s")],
        neck_h=0.72, head_off=(0, 0, 0.2), head_kind="box", head_scale=(0.17, 0.16, 0.2), skin=M["q_skin"],
        nose=(0.035, 0.07, 0.035, -0.01), eye_x=0.065, eye_z=0.03, eye_scale=(0.045, 0.035, 0.05),
        brow_gap=0.03, brow_scale=(0.06, 0.02, 0.022), brow_mat=M["q_brow"], mouth_r=0.04, mouth_z=-0.085,
        shoulder=(0.22, 0.6), arm_len=0.62, arm_r=0.045, sleeve=torso_mat,
        hand=(0.05, 0.05, 0.06), hand_mat=M["q_skin"] if undressed else M["q_glove"],
        leg_r=0.065, leg_mat=leg_mat, foot=(0.07, 0.13, 0.06), foot_mat=M["q_boot"],
    )
    R = biped("quill", "CHAR_quill", spec)
    HC = R["head_c"]
    # bushy white brows: extra tufts (signature), goggles on the forehead, tufts of white hair at the sides
    for side, sx in (("L", 1), ("R", -1)):
        tuft = sphere(f"quill_hair_{side}", HC + Vector((sx * 0.155, 0.04, -0.01)), (0.045, 0.075, 0.06), M["q_brow"], "CHAR_quill", seg=16)
        parent_keep(tuft, R["lag"])
        for k in range(3):
            t2 = sphere(f"quill_hairtuft_{side}{k}", HC + Vector((sx * 0.16, 0.07 - 0.035 * k, 0.03 + 0.012 * k)),
                        (0.03, 0.03, 0.032), M["q_brow"], "CHAR_quill", seg=12)
            parent_keep(t2, R["lag"])
    for side, sx in (("L", 0.07), ("R", -0.07)):
        g = torus(f"quill_goggle_{side}", HC + Vector((sx, -0.14, 0.15)), 0.045, 0.014, M["brass"], "CHAR_quill",
                  rot=(math.radians(70), 0, 0), maj=24, mn=8)
        lens = cyl(f"quill_goggle_lens_{side}", HC + Vector((sx, -0.14, 0.15)), 0.042, 0.01, mat(f"goggle_lens_{side}", (0.3, 0.6, 0.6), 0.05, metal=0.5),
                   "CHAR_quill", verts=20, rot=(math.radians(70), 0, 0))
        parent_keep(g, R["neck"])
        parent_keep(lens, R["neck"])
    strap = torus("quill_goggle_strap", HC + Vector((0, 0.0, 0.1)), 0.158, 0.011, M["q_suit"], "CHAR_quill",
                  rot=(math.radians(-8), 0, 0), maj=40, mn=6)
    strap.scale = (1, 0.95, 1)
    parent_keep(strap, R["neck"])
    # chest control disc (suit only)
    if not undressed:
        bpy.context.view_layer.update()
        dc = Vector((0, -0.165, 0.95 + 0.42))
        disc = cyl("quill_disc", dc, 0.07, 0.02, M["dark_metal"], "CHAR_quill", verts=32, rot=(math.radians(90), 0, 0))
        R["disc_cyan_mat"] = mat("disc_cyan", (0.02, 0.1, 0.12), 0.3, emit=hex_rgb("#19C3D6"), strength=3.0)
        R["disc_amber_mat"] = mat("disc_amber", (0.1, 0.06, 0.0), 0.3, emit=hex_rgb("#F2A33A"), strength=3.0)
        bc = sphere("quill_btn_cyan", dc + Vector((-0.028, -0.012, 0)), (0.022, 0.012, 0.022), R["disc_cyan_mat"], "CHAR_quill", seg=12)
        ba = sphere("quill_btn_amber", dc + Vector((0.028, -0.012, 0)), (0.022, 0.012, 0.022), R["disc_amber_mat"], "CHAR_quill", seg=12)
        ring = torus("quill_disc_ring", dc + Vector((0, -0.01, 0)), 0.07, 0.006, M["brass"], "CHAR_quill",
                     rot=(math.radians(90), 0, 0), maj=32, mn=6)
        for o in (disc, bc, ba, ring):
            parent_keep(o, R["body"])
        R["btn_cyan"], R["btn_amber"] = bc, ba
    return R


def build_juno():
    spec = dict(
        hip=0.4,
        torso=[((0, 0, 0.12), (0.26, 0.22, 0.26), M["j_coat"], "s"),
               ((0, -0.01, 0.3), (0.19, 0.17, 0.17), M["j_coat"], "s"),
               ((0, -0.105, 0.3), (0.09, 0.08, 0.11), M["j_sweater"], "s")],
        neck_h=0.42, head_off=(0, 0, 0.19), head_kind="sphere", head_scale=(0.25, 0.21, 0.2), skin=M["j_skin"],
        nose=(0.03, 0.03, 0.025, -0.02), eye_x=0.085, eye_z=0.02, eye_scale=(0.055, 0.045, 0.062),
        brow_gap=0.035, brow_scale=(0.045, 0.012, 0.012), brow_mat=M["j_hair"], mouth_r=0.045, mouth_z=-0.085,
        shoulder=(0.2, 0.35), arm_len=0.36, arm_r=0.045, sleeve=M["j_coat"], hand=(0.045, 0.045, 0.05),
        hand_mat=M["j_skin"], leg_r=0.05, leg_mat=M["j_pants"], foot=(0.06, 0.1, 0.05), foot_mat=M["j_shoe"],
    )
    R = biped("juno", "CHAR_juno", spec)
    HC = R["head_c"]
    hair = sphere("juno_hair_cap", HC + Vector((0, 0.03, 0.05)), (0.255, 0.215, 0.19), M["j_hair"], "CHAR_juno", seg=32)
    parent_keep(hair, R["neck"])
    fringe = sphere("juno_fringe", HC + Vector((0, -0.12, 0.13)), (0.2, 0.07, 0.06), M["j_hair"], "CHAR_juno", seg=20)
    parent_keep(fringe, R["neck"])
    # springy braids (signature silhouette): chains of beads off each side, hung on the lag pivot
    for side, sx in (("L", 1), ("R", -1)):
        prev = None
        for k in range(5):
            p = HC + Vector((sx * (0.24 + 0.05 * k), 0.04, -0.02 - 0.06 * k))
            b = sphere(f"juno_braid_{side}{k}", p, (0.045 - 0.004 * k,) * 3, M["j_hair"], "CHAR_juno", seg=12)
            parent_keep(b, R["lag"])
        tie = sphere(f"juno_tie_{side}", HC + Vector((sx * 0.46, 0.04, -0.3)), (0.03, 0.03, 0.025), M["j_tie"], "CHAR_juno", seg=12)
        parent_keep(tie, R["lag"])
    # square glasses
    for side, sx in (("L", 0.085), ("R", -0.085)):
        ec = R["eyes"][side][0].location.copy()
        bpy.context.view_layer.update()
        ec = R["eyes"][side][1].matrix_world.translation
        fr = box(f"juno_glass_frame_{side}", ec + Vector((0, -0.04, 0)), (0.13, 0.012, 0.11), M["j_frame"], "CHAR_juno")
        sol = fr.modifiers.new("wire", "WIREFRAME")
        sol.thickness = 0.012
        parent_keep(fr, R["neck"])
    bridge = box("juno_glass_bridge", R["head_c"] + Vector((0, -0.235, 0.025)), (0.05, 0.01, 0.01), M["j_frame"], "CHAR_juno")
    parent_keep(bridge, R["neck"])
    # clipboard in the right hand
    bpy.context.view_layer.update()
    hp = R["hand_R"].matrix_world.translation
    cb = box("juno_clipboard", hp + Vector((-0.02, -0.08, 0.08)), (0.02, 0.2, 0.28), M["clipboard"], "CHAR_juno", bevel=0.005)
    pp = box("juno_clip_paper", hp + Vector((-0.032, -0.08, 0.06)), (0.005, 0.18, 0.22), M["paper"], "CHAR_juno")
    parent_keep(cb, R["arms"]["R"])
    parent_keep(pp, R["arms"]["R"])
    R["clipboard"] = [cb, pp]
    # coffee mug in the left hand (hidden unless a shot needs it)
    hp = R["hand_L"].matrix_world.translation
    mug = cyl("juno_mug", hp + Vector((0.0, -0.06, 0.03)), 0.045, 0.1, M["mug"], "CHAR_juno", verts=20, bevel=0.005)
    parent_keep(mug, R["arms"]["L"])
    R["mug"] = mug
    return R


def build_scanner(loc=(1.7, 0.2, 0), yaw=0.0):
    R = {"prefix": "scanner"}
    root = empty("scanner_root", loc, col="CHAR_scanner")
    body = empty("scanner_body", (0, 0, 0), root, "CHAR_scanner")
    parts = [rbox("scanner_cart", (loc[0], loc[1], 0.4), (0.5, 0.45, 0.5), M["s_body"], "CHAR_scanner"),
             cyl("scanner_neck", (loc[0], loc[1], 0.75), 0.04, 0.3, M["dark_metal"], "CHAR_scanner", verts=12)]
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(cyl(f"scanner_wheel_{sx}{sy}", (loc[0] + sx * 0.2, loc[1] + sy * 0.17, 0.07), 0.07, 0.05,
                             M["cable"], "CHAR_scanner", verts=20, rot=(0, math.radians(90), 0)))
    for p in parts:
        parent_keep(p, body)
    head = empty("scanner_head", (0, 0, 1.05), body, "CHAR_scanner")
    bpy.context.view_layer.update()
    hc = Vector((loc[0], loc[1], 1.05))
    shell = sphere("scanner_shell", hc, (0.27, 0.2, 0.22), M["s_body"], "CHAR_scanner", seg=32)
    screen = box("scanner_screen", hc + Vector((0, -0.19, 0)), (0.36, 0.02, 0.26), M["screen_bg"], "CHAR_scanner")
    screen.modifiers.new("subd", "SUBSURF").levels = 0
    bez = torus("scanner_bezel", hc + Vector((0, -0.18, 0)), 0.2, 0.02, M["dark_metal"], "CHAR_scanner",
                rot=(math.radians(90), 0, 0), maj=40, mn=8)
    bez.scale = (1.0, 1.0, 0.78)
    lamp = sphere("scanner_lamp", hc + Vector((0, 0, 0.25)), (0.05, 0.05, 0.05), M["red_lamp"], "CHAR_scanner", seg=12)
    for o in (shell, screen, bez, lamp):
        parent_keep(o, head)
    # LED brows on the screen
    brows = []
    for side, sx in (("L", 0.08), ("R", -0.08)):
        b = box(f"scanner_brow_{side}", hc + Vector((sx, -0.205, 0.08)), (0.09, 0.005, 0.018), M["screen_txt"], "CHAR_scanner")
        parent_keep(b, head)
        brows.append(b)
    # probe arm
    ap = empty("scanner_arm", (0.25, 0, 0.65), body, "CHAR_scanner")
    a1 = cyl("scanner_arm_seg", (loc[0] + 0.25, loc[1] - 0.2, 0.65), 0.025, 0.4, M["dark_metal"], "CHAR_scanner", verts=12,
             rot=(math.radians(90), 0, 0))
    tip = sphere("scanner_probe_tip", (loc[0] + 0.25, loc[1] - 0.42, 0.65), (0.04, 0.04, 0.04), M["cyan_glow"], "CHAR_scanner", seg=12)
    for o in (a1, tip):
        parent_keep(o, ap)
    root.rotation_euler.z = yaw
    bpy.context.view_layer.update()
    R.update(root=root, body=body, head=head, brows=brows, arm=ap, screen=screen, hc=head.matrix_world.translation.copy())
    return R


def scanner_text(S, body, red=True, size=0.05, name="scanner_txt"):
    bpy.context.view_layer.update()
    hc = S["head"].matrix_world.translation
    o = text(name, body, S["head"].matrix_world @ Vector((0, -0.205, -0.02)), size, M["screen_red"] if red else M["screen_txt"],
             "CHAR_scanner", rot=(math.radians(90), 0, S["root"].rotation_euler.z))
    parent_keep(o, S["head"])
    return o


def build_mote(loc):
    root = empty("mote_root", loc, col="CHAR_mote")
    body = sphere("mote_body", loc + Vector((0, 0, 0.055)), (0.07, 0.065, 0.06), M["m_fur"], "CHAR_mote", seg=20)
    head = empty("mote_head", loc + Vector((0, -0.04, 0.08)), root, "CHAR_mote")
    parts = []
    for side, sx in (("L", 1), ("R", -1)):
        parts.append(sphere(f"mote_ear_{side}", loc + Vector((sx * 0.04, -0.02, 0.12)), (0.022, 0.01, 0.025), M["m_pink"], "CHAR_mote", seg=12))
        parts.append(sphere(f"mote_eye_{side}", loc + Vector((sx * 0.032, -0.06, 0.08)), (0.017, 0.012, 0.019), M["pupil"], "CHAR_mote", seg=12))
    parts.append(sphere("mote_nose", loc + Vector((0, -0.07, 0.06)), (0.008, 0.008, 0.008), M["m_pink"], "CHAR_mote", seg=8))
    for p in parts:
        parent_keep(p, head)
    parent_keep(body, root)
    return {"root": root, "head": head}


# --------------------------------------------------------------------------- performance helpers
def foot_plants(path_fn, yaw_fn, move_ranges, step, half_width, f0, f1):
    """Plants (contact_frame, side, pos, yaw). Feet start planted; during each move range the feet
    alternate every `step` frames landing slightly ahead of the body; a closing step squares the feet."""
    def off(side, yaw):
        lx = half_width if side == "L" else -half_width
        return Vector((lx * math.cos(yaw), lx * math.sin(yaw), 0))

    plants = []
    for side in ("L", "R"):
        p = path_fn(f0)
        plants.append((f0 - 100, side, Vector((p[0], p[1], 0)) + off(side, yaw_fn(f0)), yaw_fn(f0)))
    k = 0
    for (m0, m1) in move_ranges:
        c = m0 + step // 2
        while c < m1:
            side = "L" if k % 2 == 0 else "R"
            p = path_fn(min(c + step // 2, m1))
            plants.append((c, side, Vector((p[0], p[1], 0)) + off(side, yaw_fn(c)), yaw_fn(c)))
            c += step
            k += 1
        side = "L" if k % 2 == 0 else "R"
        p = path_fn(m1)
        plants.append((c, side, Vector((p[0], p[1], 0)) + off(side, yaw_fn(m1)), yaw_fn(m1)))
        k += 1
        other = "R" if side == "L" else "L"
        plants.append((c + step, other, Vector((p[0], p[1], 0)) + off(other, yaw_fn(m1)), yaw_fn(m1)))
        k += 1
    return plants


def foot_state(plants, side, f, step, lift=0.08):
    ps = sorted((p for p in plants if p[1] == side), key=lambda p: p[0])
    prev = ps[0]
    nxt = None
    for p in ps:
        if p[0] <= f:
            prev = p
        elif nxt is None:
            nxt = p
    if nxt is None:
        return prev[2].copy(), prev[3], 0.0
    swing = min(step, nxt[0] - prev[0])
    ls = nxt[0] - swing
    if f < ls:
        return prev[2].copy(), prev[3], 0.0
    u = (f - ls) / swing
    e = u * u * (3 - 2 * u)
    pos = prev[2].lerp(nxt[2], e)
    pos.z += lift * math.sin(math.pi * u)
    pitch = math.radians(18) * math.sin(math.pi * u) * (1 if u < 0.6 else -0.5)
    return pos, lerp(prev[3], nxt[3], e), pitch


class Performer:
    """Keys a biped every frame from simple callables. Everything defaults to a neutral idle."""

    def __init__(self, R, step=8, foot_lift=0.08, half_width=0.1):
        self.R, self.step, self.lift, self.hw = R, step, foot_lift, half_width
        self.head_trace = {}

    def run(self, f0, f1, pos, yaw, plants=None, speed=lambda f: 0.0, neck=lambda f: (0, 0), eyes=lambda f: (0, 0),
            arms=lambda f: ((0, 0, 0), (0, 0, 0)), smile=lambda f: 0.0, brows=lambda f: 0.0, blinks=(),
            body_extra=lambda f: (0.0, 0.0, 0.0), feet_override=None, lean_extra=lambda f: 0.0, mouth_open=lambda f: 0.0,
            body_roll=lambda f: 0.0, lids=lambda f: 1.0):
        R = self.R
        hip = R["hip"]
        for f in range(f0, f1 + 1):
            sp = speed(f)
            p = pos(f)
            R["root"].location = (p[0], p[1], 0)
            R["root"].rotation_euler = (0, 0, yaw(f))
            R["root"].keyframe_insert("location", frame=f)
            R["root"].keyframe_insert("rotation_euler", frame=f)
            phase = (f % self.step) / self.step
            bob = -0.022 * math.cos(2 * math.pi * phase) * sp * 1.4
            dz, dlean, dx = body_extra(f)
            lean = math.radians(7) * sp + lean_extra(f) + dlean
            R["body"].location = (dx, 0, hip + bob + dz)
            R["body"].rotation_euler = (lean, body_roll(f), math.radians(4) * math.sin(2 * math.pi * phase) * sp)
            sq = 1 - 0.035 * max(0.0, math.cos(2 * math.pi * phase)) * sp
            R["body"].scale = (1 / math.sqrt(sq), 1 / math.sqrt(sq), sq)
            for prop in ("location", "rotation_euler", "scale"):
                R["body"].keyframe_insert(prop, frame=f)
            swing = math.radians(28) * math.sin(2 * math.pi * f / (2 * self.step)) * sp
            aL, aR = arms(f)
            R["arms"]["L"].rotation_euler = (aL[0] - swing, aL[1], aL[2] - math.radians(6))
            R["arms"]["R"].rotation_euler = (aR[0] + swing, aR[1], aR[2] + math.radians(6))
            for side, a in (("L", aL), ("R", aR)):
                R["arms"][side].scale = (1, 1, a[3] if len(a) > 3 else 1.0)
                R["arms"][side].keyframe_insert("rotation_euler", frame=f)
                R["arms"][side].keyframe_insert("scale", frame=f)
            hp, hy = neck(f)
            hp = hp - lean * 0.6
            R["neck"].rotation_euler = (hp, 0, hy)
            R["neck"].keyframe_insert("rotation_euler", frame=f)
            self.head_trace[f] = (hp, hy)
            lp, ly = self.head_trace.get(f - 3, (hp, hy))
            R["lag"].rotation_euler = ((lp - hp) * 0.6 + math.radians(3) * math.sin(2 * math.pi * phase) * sp, 0, (ly - hy) * 0.6)
            R["lag"].keyframe_insert("rotation_euler", frame=f)
            ep, ey = eyes(f)
            for side in ("L", "R"):
                pivot, lid, brow, bz = R["eyes"][side]
                pivot.rotation_euler = (ep, 0, ey)
                pivot.keyframe_insert("rotation_euler", frame=f)
                bl = 1.0
                for b0 in blinks:
                    if b0 <= f <= b0 + 3:
                        bl = (0.15, 0.05, 0.4, 0.9)[f - b0]
                lid.scale = (1, 1, bl * lids(f))
                lid.keyframe_insert("scale", frame=f)
                brow.location.z = bz + 0.03 * brows(f)
                brow.keyframe_insert("location", index=2, frame=f)
            sm, mo = smile(f), mouth_open(f)
            R["mouth"].scale = (lerp(0.7, 1.15, sm) * (1 - 0.35 * mo), 1, lerp(0.25, 1.0, sm) + 1.6 * mo)
            R["mouth"].keyframe_insert("scale", frame=f)
            # legs: world-space hip -> foot
            scene.frame_set(f)
            for side in ("L", "R"):
                if feet_override:
                    fpos, fyaw, pitch = feet_override(side, f)
                else:
                    fpos, fyaw, pitch = foot_state(plants, side, f, self.step, self.lift)
                ft = R["feet"][side]
                fs = R["spec"]["foot"]
                ft.location = fpos + Vector((0, 0, fs[2] * 0.9)) + Vector((math.sin(fyaw), -math.cos(fyaw), 0)) * fs[1] * 0.3
                ft.rotation_euler = (pitch, 0, fyaw)
                ft.keyframe_insert("location", frame=f)
                ft.keyframe_insert("rotation_euler", frame=f)
                hipw = R["body"].matrix_world @ Vector((self.hw if side == "L" else -self.hw, 0, -0.02))
                ankle = fpos + Vector((0, 0, fs[2] * 1.4))
                d = ankle - hipw
                lg = R["legs"][side]
                lg.location = hipw
                lg.rotation_quaternion = Vector((0, 0, -1)).rotation_difference(d.normalized())
                lg.scale = (1, 1, max(0.05, d.length))
                for prop in ("location", "rotation_quaternion", "scale"):
                    lg.keyframe_insert(prop, frame=f)


def arm_dir(d, length=None, full=None, blend=1.0):
    """Euler (XYZ) that swings a hanging arm (0,0,-1) toward body-local direction d (character faces -Y),
    plus an optional length scale (toon stretch) so the hand lands `length` metres from the shoulder.
    `blend` eases from hanging (0) to aimed (1)."""
    from mathutils import Quaternion
    q = Vector((0, 0, -1)).rotation_difference(Vector(d).normalized())
    q = Quaternion().slerp(q, blend)
    e = q.to_euler("XYZ")
    sc = 1.0 if (length is None or full is None) else lerp(1.0, length / full, blend)
    return (e.x, e.y, e.z + (math.radians(6) if d[0] > 0 else -math.radians(6)) * 0, sc)


def static_feet(R, x, y, yaw, hw=0.1):
    def fo(side, f):
        lx = hw if side == "L" else -hw
        return Vector((x + lx * math.cos(yaw), y + lx * math.sin(yaw), 0)), yaw, 0.0
    return fo


# --------------------------------------------------------------------------- FX
def rain_sheet(name, bounds, n, z0, height, mat_):
    x0, x1, y0, y1 = bounds
    bm = bmesh.new()
    for _ in range(n):
        x, y = random.uniform(x0, x1), random.uniform(y0, y1)
        z = random.uniform(0, height)
        hh = random.uniform(0.12, 0.26)
        w = 0.004
        vs = [bm.verts.new(v) for v in ((x - w, y, z), (x + w, y, z), (x + w, y, z + hh), (x - w, y, z + hh))]
        bm.faces.new(vs)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    ob = bpy.data.objects.new(name, me)
    COL["FX"].objects.link(ob)
    ob.location.z = z0
    me.materials.append(mat_)
    ob.visible_shadow = False
    return ob


def sprinkler_rain(f_on, f0, f1, bounds=(-4.8, 4.8, -2.8, 4.8), n=1100, speed=0.22):
    H = LAB["h"]
    sheets = [rain_sheet("spr_A", bounds, n, 0, H, M["water"]), rain_sheet("spr_B", bounds, n, H, H, M["water"])]
    for f in range(f0, f1 + 1):
        for i, ob in enumerate(sheets):
            if f < f_on:
                ob.location.z = H + 1.0 + i * H  # parked above the ceiling
            else:
                ob.location.z = (i * H - speed * (f - f_on)) % (2 * H) - 0.3
            ob.keyframe_insert("location", index=2, frame=f)
    return sheets


def decal(name, loc, scale, m, rot=(0, 0, 0), col="FX"):
    bpy.ops.mesh.primitive_circle_add(vertices=24, radius=1, fill_type="NGON", location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    link(assign(o, m), col)
    o.visible_shadow = False
    return o


def footprint(name, loc, yaw, m=None, size=1.0):
    """A sole print (two ellipses: ball + heel) lying on the floor."""
    m = m or M["print"]
    objs = []
    for k, (dy, sx, sy) in enumerate(((-0.05, 0.045, 0.07), (0.07, 0.035, 0.045))):
        off = Vector((math.sin(yaw) * -dy, math.cos(yaw) * dy, 0)) * 1.0
        o = decal(f"{name}_{k}", Vector(loc) + off * size + Vector((0, 0, 0.0)), (sx * size, sy * size, 1), m, rot=(0, 0, yaw))
        objs.append(o)
    return objs


def palm_print(name, loc, m, size=1.0):
    """Hand print on the window glass (plane facing -X): palm + 4 fingers + thumb."""
    objs = [decal(f"{name}_palm", loc, (0.05 * size, 0.055 * size, 1), m, rot=(0, math.radians(90), 0))]
    for k, dy in enumerate((-0.045, -0.015, 0.015, 0.045)):
        objs.append(decal(f"{name}_f{k}", Vector(loc) + Vector((0, dy * size, (0.085 + 0.01 * (k % 3 == 1)) * size)),
                          (0.012 * size, 0.035 * size, 1), m, rot=(0, math.radians(90), 0)))
    objs.append(decal(f"{name}_thumb", Vector(loc) + Vector((0, 0.065 * size, 0.02 * size)), (0.012 * size, 0.03 * size, 1), m,
                      rot=(math.radians(-40), math.radians(90), 0)))
    return objs


# --------------------------------------------------------------------------- camera + render
def camera(keys, lens_keys, target_fn, f0, f1, focus=None, fstop=2.2, damp=0.25):
    cd = bpy.data.cameras.new("cam")
    cd.sensor_fit = "VERTICAL"
    cd.sensor_height = 36
    cd.dof.use_dof = focus is not None
    cd.dof.aperture_fstop = fstop
    cam = bpy.data.objects.new("cam", cd)
    COL["CAMERA"].objects.link(cam)
    scene.camera = cam
    for f, p in keys.items():
        cam.location = p
        cam.keyframe_insert("location", frame=f)
    for f, l in lens_keys.items():
        cd.lens = l
        cd.keyframe_insert("lens", frame=f)
    tgt = empty("cam_target", col="CAMERA")
    con = cam.constraints.new("TRACK_TO")
    con.target = tgt
    con.track_axis, con.up_axis = "TRACK_NEGATIVE_Z", "UP_Y"
    if focus is not None:
        cd.dof.focus_object = focus
    sm = None
    for f in range(f0, f1 + 1):
        scene.frame_set(f)
        g = Vector(target_fn(f))
        sm = g if sm is None else sm.lerp(g, damp)
        tgt.location = sm
        tgt.keyframe_insert("location", frame=f)
    return cam


def render_settings(res, samples, out_dir):
    rx, ry = (int(v) for v in res.split("x"))
    r = scene.render
    r.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = samples
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = 0.03
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 6
    scene.cycles.diffuse_bounces = 2
    scene.cycles.glossy_bounces = 3
    scene.cycles.transmission_bounces = 6
    scene.cycles.transparent_max_bounces = 10
    scene.cycles.volume_bounces = 0
    scene.cycles.caustics_reflective = scene.cycles.caustics_refractive = False
    scene.cycles.blur_glossy = 1.0
    scene.cycles.sample_clamp_indirect = 8.0
    r.use_persistent_data = True
    r.resolution_x, r.resolution_y, r.resolution_percentage = rx, ry, 100
    r.image_settings.file_format = "PNG"
    r.image_settings.color_mode = "RGB"
    r.use_motion_blur = False
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 0.35
