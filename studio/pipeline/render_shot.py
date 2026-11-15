"""Build and render one shot in Blender (bpy, headless) from a JSON shot spec.

    python render_shot.py <shot.json> <out_dir> [--preview] [--still]

--preview  : 50% resolution, low samples (fast look-dev on the CPU container)
--still    : render only the middle frame (for quick checks)

The shot spec format is documented in studio/README.md ("Shot spec").
Render = Cycles on CPU (no GPU in the cloud container). Frames are written as
PNG to <out_dir>/frames/ and encoded to <out_dir>/<shot_id>.mp4 with ffmpeg.
"""
import json
import math
import os
import subprocess
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
STUDIO = os.path.dirname(HERE)


def hex_rgba(h, a=1.0):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    srgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb]
    return (*lin, a)


def safe(fn):
    try:
        fn()
    except Exception as e:  # API drift between Blender versions
        print("[render_shot] skipped setting:", e)


# --------------------------------------------------------------- scene setup
def setup_scene(spec, preview):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    r = sc.render
    fps = spec.get("fps", 30)
    r.fps = fps
    r.resolution_x, r.resolution_y = 1080, 1920
    r.resolution_percentage = 50 if preview else spec.get("resolution_percentage", 100)
    sc.frame_start = 1
    sc.frame_end = max(1, int(round(spec.get("duration", 3.0) * fps)))
    r.engine = "CYCLES"
    sc.cycles.device = "CPU"
    c = sc.cycles
    c.samples = 8 if preview else spec.get("samples", 32)
    c.use_adaptive_sampling = True
    c.use_denoising = True
    safe(lambda: setattr(c, "denoiser", "OPENIMAGEDENOISE"))
    # Cartoon sets don't need deep light paths; these settings halve CPU time.
    c.max_bounces, c.diffuse_bounces, c.glossy_bounces = 3, 2, 2
    c.transmission_bounces, c.volume_bounces = 2, 0
    c.caustics_reflective = c.caustics_refractive = False
    c.volume_step_rate = 4
    safe(lambda: setattr(c, "texture_limit_render", "1024" if preview else "2048"))
    r.use_persistent_data = True
    r.use_motion_blur = spec.get("motion_blur", True)
    r.image_settings.file_format = "PNG"
    # Colour: AgX with a punchy look = saturated, contrasty cartoon-film feel
    safe(lambda: setattr(sc.view_settings, "view_transform", "AgX"))
    for look in ("AgX - Punchy", "Punchy"):
        try:
            sc.view_settings.look = look
            break
        except Exception:
            pass
    sc.view_settings.exposure = spec.get("exposure", 0.0)

    w = bpy.data.worlds.new("World")
    sc.world = w
    safe(lambda: setattr(w, "use_nodes", True))
    bg = w.node_tree.nodes.get("Background") or w.node_tree.nodes.new("ShaderNodeBackground")
    if not bg.outputs[0].is_linked:
        out = w.node_tree.nodes.get("World Output") or w.node_tree.nodes.new("ShaderNodeOutputWorld")
        w.node_tree.links.new(bg.outputs[0], out.inputs[0])
    bg.inputs[0].default_value = hex_rgba(spec.get("world_color", "#101830"))
    bg.inputs[1].default_value = spec.get("world_strength", 1.0)
    return sc


# --------------------------------------------------------------- materials
def new_mat(name):
    m = bpy.data.materials.new(name)
    safe(lambda: setattr(m, "use_nodes", True))
    return m


def solid_material(o):
    m = new_mat(o.get("name", "mat"))
    nt = m.node_tree
    p = nt.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = hex_rgba(o.get("color", "#888888"))
    p.inputs["Roughness"].default_value = o.get("roughness", 0.6)
    if o.get("metallic"):
        p.inputs["Metallic"].default_value = o["metallic"]
    if o.get("transmission"):
        p.inputs["Transmission Weight"].default_value = o["transmission"]
    if o.get("emission"):
        p.inputs["Emission Color"].default_value = hex_rgba(o["emission"])
        p.inputs["Emission Strength"].default_value = o.get("emission_strength", 5.0)
    if o.get("pattern") == "checker":
        ch = nt.nodes.new("ShaderNodeTexChecker")
        ch.inputs["Color1"].default_value = hex_rgba(o.get("color", "#E8E8E8"))
        ch.inputs["Color2"].default_value = hex_rgba(o.get("color2", "#1E5F8C"))
        ch.inputs["Scale"].default_value = o.get("pattern_scale", 8.0)
        nt.links.new(ch.outputs["Color"], p.inputs["Base Color"])
    if o.get("texture"):
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(resolve(o["texture"]))
        nt.links.new(tex.outputs["Color"], p.inputs["Base Color"])
    return m


def sprite_material(name, img_path, flat):
    """Cartoon sprite: image colour, alpha cut-out, partly emissive so the
    flat drawn look survives while scene light still tints and rims it."""
    m = new_mat(name)
    nt = m.node_tree
    p = nt.nodes.get("Principled BSDF")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(img_path)
    tex.interpolation = "Cubic"
    nt.links.new(tex.outputs["Color"], p.inputs["Base Color"])
    nt.links.new(tex.outputs["Alpha"], p.inputs["Alpha"])
    nt.links.new(tex.outputs["Color"], p.inputs["Emission Color"])
    p.inputs["Emission Strength"].default_value = flat
    p.inputs["Roughness"].default_value = 0.9
    safe(lambda: setattr(m, "surface_render_method", "DITHERED"))
    return m


def resolve(path):
    return path if os.path.isabs(path) else os.path.join(STUDIO, path)


# --------------------------------------------------------------- objects
def add_object(o):
    t = o["type"]
    loc = o.get("loc", [0, 0, 0])
    if t == "box":
        bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
        bpy.context.object.scale = o.get("size", [1, 1, 1])
    elif t == "plane":
        bpy.ops.mesh.primitive_plane_add(size=1, location=loc)
        sz = o.get("size", [1, 1])
        bpy.context.object.scale = (sz[0], sz[1], 1)
    elif t == "cylinder":
        bpy.ops.mesh.primitive_cylinder_add(radius=o.get("radius", 0.5), depth=o.get("depth", 1), location=loc, vertices=48)
    elif t == "sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=o.get("radius", 0.5), location=loc, segments=48, ring_count=24)
        bpy.ops.object.shade_smooth()
    elif t == "cone":
        bpy.ops.mesh.primitive_cone_add(radius1=o.get("radius", 0.5), radius2=o.get("radius_top", 0.0), depth=o.get("depth", 1), location=loc, vertices=48)
        bpy.ops.object.shade_smooth()
    else:
        raise ValueError("unknown object type " + t)
    ob = bpy.context.object
    ob.name = o.get("name", t)
    ob.rotation_euler = [math.radians(a) for a in o.get("rot", [0, 0, 0])]
    if o.get("bevel"):
        mod = ob.modifiers.new("bevel", "BEVEL")
        mod.width = o["bevel"]
        mod.segments = 3
    ob.data.materials.append(solid_material(o))
    return ob


def add_character(c, cam, work_dir):
    sys.path.insert(0, HERE)
    from make_character import draw_character

    if c.get("image"):
        img_path = resolve(c["image"])
    else:
        img_path = os.path.join(work_dir, f"char_{c['name']}.png")
        draw_character(c.get("look", {})).save(img_path)
    h = c.get("height", 1.7)
    w = h / 2.0
    me = bpy.data.meshes.new(c["name"])
    me.from_pydata([(-w / 2, 0, 0), (w / 2, 0, 0), (w / 2, 0, h), (-w / 2, 0, h)], [], [(0, 1, 2, 3)])
    me.uv_layers.new()
    for i, uv in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]):
        me.uv_layers[0].data[i].uv = uv
    ob = bpy.data.objects.new(c["name"], me)
    bpy.context.collection.objects.link(ob)
    ob.location = c.get("loc", [0, 0, 0])
    ob.data.materials.append(sprite_material(c["name"], img_path, c.get("flat", 0.55)))
    if c.get("face_camera", True):
        con = ob.constraints.new("LOCKED_TRACK")
        con.target = cam
        con.lock_axis = "LOCK_Z"
        con.track_axis = "TRACK_NEGATIVE_Y"
    for k in c.get("keys", []):  # simple position animation
        ob.location = k["loc"]
        ob.keyframe_insert("location", frame=k["frame"])
    return ob


def add_light(l):
    ld = bpy.data.lights.new(l.get("name", "light"), l.get("type", "POINT"))
    ld.energy = l.get("energy", 500)
    ld.color = hex_rgba(l.get("color", "#FFFFFF"))[:3]
    if hasattr(ld, "shadow_soft_size"):
        ld.shadow_soft_size = l.get("soft", 0.25)
    if l.get("type") == "SPOT":
        ld.spot_size = math.radians(l.get("spot_deg", 45))
        ld.spot_blend = l.get("spot_blend", 0.4)
    if l.get("type") == "AREA":
        ld.size = l.get("size", 1.0)
    ob = bpy.data.objects.new(ld.name, ld)
    bpy.context.collection.objects.link(ob)
    ob.location = l.get("loc", [0, 0, 3])
    if "aim" in l:
        d = Vector(l["aim"]) - ob.location
        ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    return ob


def add_fog(f):
    bpy.ops.mesh.primitive_cube_add(size=1, location=f.get("loc", [0, 0, 2]))
    ob = bpy.context.object
    ob.name = "fog"
    ob.scale = f.get("size", [30, 30, 8])
    m = new_mat("fog")
    nt = m.node_tree
    nt.nodes.remove(nt.nodes.get("Principled BSDF"))
    vol = nt.nodes.new("ShaderNodeVolumePrincipled")
    vol.inputs["Density"].default_value = f.get("density", 0.03)
    vol.inputs["Color"].default_value = hex_rgba(f.get("color", "#9FB4FF"))
    vol.inputs["Anisotropy"].default_value = f.get("anisotropy", 0.3)
    nt.links.new(vol.outputs[0], nt.nodes.get("Material Output").inputs["Volume"])
    ob.data.materials.append(m)


def setup_camera(c, sc):
    cd = bpy.data.cameras.new("cam")
    cam = bpy.data.objects.new("cam", cd)
    bpy.context.collection.objects.link(cam)
    sc.camera = cam
    target = bpy.data.objects.new("cam_target", None)
    bpy.context.collection.objects.link(target)
    con = cam.constraints.new("TRACK_TO")
    con.target = target
    con.track_axis = "TRACK_NEGATIVE_Z"
    con.up_axis = "UP_Y"
    keys = c.get("keys") or [{"frame": 1, "loc": c.get("loc", [0, -6, 1.6]), "look_at": c.get("look_at", [0, 0, 1.2])}]
    for k in keys:
        cam.location = k["loc"]
        cam.keyframe_insert("location", frame=k["frame"])
        target.location = k.get("look_at", [0, 0, 1.2])
        target.keyframe_insert("location", frame=k["frame"])
        cd.lens = k.get("lens", c.get("lens", 35))
        cd.keyframe_insert("lens", frame=k["frame"])
        if "roll" in k:  # dutch angle via target offset is enough for most shots
            pass
    cd.dof.use_dof = c.get("dof", True)
    cd.dof.aperture_fstop = c.get("fstop", 2.0)
    return cam, cd


def finish_dof(c, cd):
    if c.get("focus"):
        cd.dof.focus_object = bpy.data.objects.get(c["focus"])
    elif c.get("focus_distance"):
        cd.dof.focus_distance = c["focus_distance"]


# --------------------------------------------------------------- main
def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    spec_path, out_dir = argv[0], argv[1]
    preview, still = "--preview" in argv, "--still" in argv
    spec = json.load(open(spec_path))
    os.makedirs(os.path.join(out_dir, "frames"), exist_ok=True)

    sc = setup_scene(spec, preview)
    cam, cd = setup_camera(spec.get("camera", {}), sc)
    for o in spec.get("objects", []):
        add_object(o)
    for l in spec.get("lights", []):
        add_light(l)
    for ch in spec.get("characters", []):
        add_character(ch, cam, out_dir)
    if spec.get("fog"):
        add_fog(spec["fog"])
    finish_dof(spec.get("camera", {}), cd)

    if spec.get("save_blend", True):
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(os.path.abspath(out_dir), spec["id"] + ".blend"))

    if still:
        mid = (sc.frame_start + sc.frame_end) // 2
        sc.frame_set(mid)
        sc.render.filepath = os.path.join(out_dir, spec["id"] + "_still.png")
        bpy.ops.render.render(write_still=True)
        return

    sc.render.filepath = os.path.join(out_dir, "frames", "f_")
    bpy.ops.render.render(animation=True)
    mp4 = os.path.join(out_dir, spec["id"] + ".mp4")
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-framerate", str(sc.render.fps),
        "-i", os.path.join(out_dir, "frames", "f_%04d.png"),
        "-vf", "scale=1080:1920:flags=lanczos", "-c:v", "libx264", "-crf", "16",
        "-pix_fmt", "yuv420p", mp4], check=True)
    print("[render_shot] wrote", mp4)


if __name__ == "__main__":
    main()
