"""Shot staging for P02 "Be Seen". One function per shot; each builds what its frame needs on top of the lab.

Every shot receives N (frame count, from the measured voice) and P/E (phrase start / end frames).
Character yaw: 0 faces -Y, 90 faces +X, 180 faces +Y, -90 faces -X.
"""
import math
import random

import bpy  # noqa: E402
from mathutils import Vector

import lib
from lib import (arm_dir, M, SET, DOOR, HALO_C, LAB, LEVER_LOC, MACHINE, MAT_C, MIRROR_LOC, PLAQUE_LOC, WIN, Performer,
                 all_objs, area, box, camera, cyl, decal, empty, emis, foot_plants, footprint, holo_mat, key_hide,
                 lerp, link, mat, palm_print, point, smoothstep, sphere, spot, sprinkler_rain, static_feet, text,
                 track, vanish_mat, water_shell_mat, hex_rgb)

R_ = math.radians
EVENTS = []


def ev(kind, frame, **kw):
    """Sound cue exported to manifests/p02_events/<shot>.json; Stage 8 builds the audio from these."""
    EVENTS.append(dict(kind=kind, frame=int(frame), **kw))
GLASS_X = LAB["x1"] + 0.035  # lab-side face of the observation glass


# --------------------------------------------------------------------------- shared shot helpers
def near_flask(name, loc):
    """Near-layer prop: a ring stand with a round flask (the camera moves past it)."""
    x, y, z = loc
    box(f"{name}_base", (x, y, z + 0.01), (0.22, 0.14, 0.02), M["dark_metal"], "ENV_near", bevel=0.005)
    cyl(f"{name}_rod", (x - 0.07, y, z + 0.35), 0.008, 0.7, M["steel"], "ENV_near", verts=8)
    lib.torus(f"{name}_ring", (x, y, z + 0.42), 0.07, 0.006, M["steel"], "ENV_near", maj=24, mn=6)
    sphere(f"{name}_flask", (x, y, z + 0.46), (0.07, 0.07, 0.07), M["glass"], "ENV_near", seg=20)
    sphere(f"{name}_liq", (x, y, z + 0.44), (0.062, 0.062, 0.045), M["liquid_p"], "ENV_near", seg=16)
    cyl(f"{name}_neck", (x, y, z + 0.56), 0.018, 0.12, M["glass"], "ENV_near", verts=12)


def red_strobes(f_on, f0, f1, energy=900, period=30):
    beacons = []
    for i, (x, y) in enumerate(((-4.6, 4.6), (4.6, -2.6))):
        sphere(f"beacon_{i}", (x, y, LAB["h"] - 0.12), (0.08, 0.08, 0.1), M["red_lamp"], "ENV_far", seg=12)
        s = spot(f"strobe_{i}", (x, y, LAB["h"] - 0.15), (75, 0, 0), 0, (1.0, 0.04, 0.02), 50, 0.4, 0.05)
        beacons.append(s)
    for f in range(f0, f1 + 1):
        on = 1.0 if f >= f_on else 0.0
        for i, s in enumerate(beacons):
            s.rotation_euler.z = 2 * math.pi * (f + i * period / 2) / period
            s.data.energy = energy * on
            s.keyframe_insert("rotation_euler", index=2, frame=f)
            s.data.keyframe_insert("energy", frame=f)
    pt = point("strobe_ambient", (0, 1, LAB["h"] - 0.4), 0, (1.0, 0.05, 0.03), 1.0)
    for f in range(f0, f1 + 1):
        on = 1.0 if f >= f_on else 0.0
        pt.data.energy = on * (60 + 50 * math.sin(2 * math.pi * f / period) ** 2)
        pt.data.keyframe_insert("energy", frame=f)


def dim_lab(f_keys):
    """Scale the ceiling lights and strip emission by track(f, f_keys)."""
    lights = [o for o in bpy.data.objects if o.name.startswith("ceiling_area_")]
    strip_em = M["strip"].node_tree.nodes["Emission"].inputs["Strength"]
    fs = sorted(set(k[0] for k in f_keys))
    for f in range(fs[0], fs[-1] + 1):
        k = track(f, f_keys)
        for lo in lights:
            lo.data.energy = 70 * k
            lo.data.keyframe_insert("energy", frame=f)
        strip_em.default_value = 6.0 * k
        strip_em.keyframe_insert("default_value", frame=f)


def quill_groups(R):
    g = {"hands": [], "legs": [], "body": [], "disc": []}
    for o in all_objs(R):
        n = o.name
        if any(k in n for k in ("disc", "btn")):
            g["disc"].append(o)
        elif "hand" in n or "arm" in n:
            g["hands"].append(o)
        elif "leg" in n or "foot" in n or "torso_1" in n:
            g["legs"].append(o)
        else:
            g["body"].append(o)
    return g


def make_vanishable(objs):
    cache = {}
    for o in objs:
        if o.type not in ("MESH", "FONT"):
            continue
        mats = list(o.data.materials)
        o.data.materials.clear()
        for m in mats:
            if m.name not in cache:
                cache[m.name] = vanish_mat(m)
            o.data.materials.append(cache[m.name])
        o["vanish"] = 0.0


def key_vanish(objs, keys, f0, f1):
    for f in range(f0, f1 + 1):
        v = track(f, keys)
        for o in objs:
            o["vanish"] = v
            o.keyframe_insert('["vanish"]', frame=f)


def key_emission(m, keys, f0, f1, node="Principled BSDF", socket="Emission Strength"):
    inp = m.node_tree.nodes[node].inputs[socket]
    for f in range(f0, f1 + 1):
        inp.default_value = track(f, keys)
        inp.keyframe_insert("default_value", frame=f)


def head_pos(R):
    bpy.context.view_layer.update()
    return R["neck"].matrix_world @ Vector((0, 0, R["head_c"].z - R["hip"] - R["spec"]["neck_h"]))


def mote(f0, f1, look_at):
    mo = lib.build_mote(SET["habitat"] + Vector((0.0, 0.0, 0.0)))
    for f in range(f0, f1 + 1):
        tgt = Vector(look_at(f))
        d = tgt - mo["root"].location
        yaw = math.atan2(d.x, -d.y)
        mo["head"].rotation_euler = (0, 0, yaw + 0.15 * math.sin(f / 5.0))
        mo["head"].keyframe_insert("rotation_euler", frame=f)
    return mo


def stand(R, N, x, y, yaw, step=8, hw=0.1, **kw):
    pf = Performer(R, step=step, half_width=hw)
    yawf = kw.pop("yawf", lambda f: R_(yaw))
    pf.run(1, N, lambda f: (x, y), yawf, feet_override=kw.pop("feet", static_feet(R, x, y, R_(yaw), hw)), **kw)
    return pf


def walk(R, N, path_keys, yaw_keys, move_ranges, step=8, hw=0.1, lift=0.08, **kw):
    pos = lambda f: track(f, path_keys)
    yawf = lambda f: R_(track(f, yaw_keys))

    def speed(f):
        a = pos(f - 1)
        b = pos(f + 1)
        v = math.hypot(b[0] - a[0], b[1] - a[1]) / 2
        return min(1.0, v / 0.06)

    plants = foot_plants(pos, yawf, move_ranges, step, hw, 1, N)
    for c, side, p, _ in plants:
        if 1 <= c <= N:
            ev("step", c, who=R["prefix"], side=side, x=round(p.x, 2), y=round(p.y, 2), run=step <= 6)
    pf = Performer(R, step=step, foot_lift=lift, half_width=hw)
    pf.run(1, N, pos, yawf, plants=plants, speed=kw.pop("speed", speed), **kw)
    return pf, plants


def blinks_every(N, start=20, gap=70):
    return list(range(start, N, gap))


# --------------------------------------------------------------------------- shots
def S01(N, P, E):
    """Cold open: only the chest disc floats in the empty air above two foot dents."""
    q = lib.build_quill()
    g = quill_groups(q)
    key_hide(g["hands"] + g["legs"] + g["body"], 1, True)
    x, y = MAT_C.x, MAT_C.y
    stand(q, N, x, y, 0, neck=lambda f: (R_(20) * smoothstep(P[1], P[1] + 20, f), 0))
    # switch-off: cyan held, amber presses at the end of "switched off", glow dies
    press = P[0] + 22
    key_emission(q["disc_cyan_mat"], [(1, 3.0), (press - 6, 3.0), (press, 0.0)], 1, N)
    key_emission(q["disc_amber_mat"], [(1, 0.4), (press, 0.4), (press + 2, 8.0), (press + 40, 0.15), (N, 0.1)], 1, N)
    ev("click", press)
    ev("powerdown", press)
    btn = q["btn_amber"]
    for f, s in ((press - 1, 1.0), (press + 1, 0.4), (press + 5, 1.0)):
        btn.scale = (1, s, 1)
        btn.keyframe_insert("scale", frame=f)
    glow = point("disc_glow", (x, y - 0.35, 1.37), 0, hex_rgb("#F2A33A"), 0.05)
    for f in range(1, N + 1):
        glow.data.energy = track(f, [(1, 2.0), (press, 2.0), (press + 2, 25.0), (press + 40, 0.5)])
        glow.data.keyframe_insert("energy", frame=f)
    # foot dents: they shift as the invisible man looks down at himself
    prints = footprint("dentL", (x + 0.1, y - 0.03, 0.017), 0) + footprint("dentR", (x - 0.1, y - 0.03, 0.017), 0)
    for o in prints[2:]:
        for f, rz in ((P[1], 0.0), (P[1] + 14, R_(-12))):
            o.rotation_euler.z = rz
            o.keyframe_insert("rotation_euler", index=2, frame=f)
    near_flask("near", (-0.3, 0.75, 0.62))
    box("near_cart", (-0.3, 0.75, 0.3), (0.4, 0.35, 0.6), M["bench_body"], "ENV_near", bevel=0.02)
    mote(1, N, lambda f: (x, y, 1.3))
    camera({1: (0.05, 0.35, 1.45), N // 2: (0.25, 0.05, 1.3), N: (0.5, -0.25, 1.05)}, {1: 34, N: 32},
           lambda f: Vector((x, y - 0.17, lerp(1.37, 0.8, smoothstep(P[1], P[1] + 34, f)))), 1, N, focus=q["body"], fstop=2.8)


def S02(N, P, E):
    """Flashback: the suit sleeve bends the Halo's light."""
    q = lib.build_quill()
    g = quill_groups(q)
    make_vanishable(all_objs(q))
    x, y = 0.0, 2.75
    reach = lambda f: smoothstep(12, 40, f)
    stand(q, N, x, y, -15,
          arms=lambda f: ((R_(-35) * reach(f), R_(-75) * reach(f), 0), (0, 0, 0)),
          neck=lambda f: (R_(-5), R_(45) * reach(f)), eyes=lambda f: (R_(-5), R_(15) * reach(f)),
          smile=lambda f: smoothstep(P[0] + 40, P[0] + 60, f), brows=lambda f: smoothstep(50, 60, f),
          blinks=blinks_every(N, 30, 80))
    sleeve = [o for o in all_objs(q) if o.name in ("quill_arm_L", "quill_hand_L")]
    ev("shimmer", P[0] + 30)
    ev("halo_swell", P[0] + 25)
    key_vanish(sleeve, [(1, 0.0), (P[0] + 30, 0.0), (P[0] + 60, 0.55), (N - 30, 0.5), (N, 0.35)], 1, N)
    j = lib.build_juno()
    key_hide([j["mug"]], 1, True)
    stand(j, N, -1.4, 1.3, -60, neck=lambda f: (R_(-14), R_(15)), eyes=lambda f: (R_(-8), R_(5)),
          arms=lambda f: ((0, 0, 0), (R_(-45), 0, 0)), smile=lambda f: 0.4, brows=lambda f: smoothstep(P[0] + 50, P[0] + 60, f),
          blinks=blinks_every(N, 45, 75))
    mote(1, N, lambda f: (x, y, 1.6))
    camera({1: (2.45, 0.6, 0.55), N // 2: (2.0, 0.0, 1.15), N: (1.55, -0.4, 1.7)}, {1: 26, N: 28},
           lambda f: head_pos(q).lerp(Vector((0.55, 2.85, 1.45)), 0.45 * smoothstep(30, 90, f)), 1, N, focus=q["neck"])


def S03(N, P, E):
    """Close on the control disc: the cyan button makes a hand blink out, the amber brings it back."""
    q = lib.build_quill()
    make_vanishable(all_objs(q))
    x, y = MAT_C.x, MAT_C.y
    t1, t2 = P[0] + 4, P[1] + 4
    stand(q, N, x, y, -10,
          arms=lambda f: (arm_dir((-0.1, -0.35, 0.25), 0.42, 0.68, smoothstep(1, 10, f)),
                          arm_dir((0.25, -0.24, -0.16), 0.36, 0.68, smoothstep(1, 10, f))),
          neck=lambda f: (R_(22), 0), eyes=lambda f: (R_(15), 0), smile=lambda f: smoothstep(t2 + 8, t2 + 16, f),
          brows=lambda f: smoothstep(t1, t1 + 6, f), blinks=[t2 + 20])
    ev("tone_low", t1)
    ev("shimmer", t1 + 1)
    ev("tone_high", t2)
    ev("shimmer", t2 + 1)
    hand = [o for o in all_objs(q) if o.name == "quill_hand_L"]
    key_vanish(hand, [(1, 0.0), (t1, 0.0), (t1 + 8, 1.0), (t2, 1.0), (t2 + 8, 0.0)], 1, N)
    key_emission(q["disc_cyan_mat"], [(1, 3), (t1 - 1, 3), (t1 + 1, 14), (t1 + 10, 3)], 1, N)
    key_emission(q["disc_amber_mat"], [(1, 3), (t2 - 1, 3), (t2 + 1, 14), (t2 + 10, 3)], 1, N)
    for b, t in ((q["btn_cyan"], t1), (q["btn_amber"], t2)):
        for f, s in ((t - 1, 1.0), (t + 1, 0.4), (t + 5, 1.0)):
            b.scale = (1, s, 1)
            b.keyframe_insert("scale", frame=f)
    j = lib.build_juno()
    key_hide([j["mug"]], 1, True)
    stand(j, N, x + 0.75, y + 0.9, -25, neck=lambda f: (R_(-18), 0), eyes=lambda f: (R_(5), R_(-10)),
          arms=lambda f: ((0, 0, 0), (R_(-45), 0, 0)), smile=lambda f: 0.6, brows=lambda f: 0.5, blinks=[30, 90])
    near_flask("near", (x + 0.55, y - 0.85, 0.75))
    box("near_cart", (x + 0.55, y - 0.85, 0.37), (0.4, 0.35, 0.74), M["bench_body"], "ENV_near", bevel=0.02)
    camera({1: (x - 0.35, y - 0.95, 1.38), N // 2: (x + 0.1, y - 1.05, 1.42), N: (x + 0.6, y - 1.0, 1.45)}, {1: 35, N: 35},
           lambda f: Vector((x - 0.02, y - 0.15, 1.42)), 1, N, focus=q["body"], fstop=2.8)


def S04(N, P, E):
    """Over Quill's shoulder: the emergency machine in the corridor powers up."""
    q = lib.build_quill()
    x, y = 4.0, 1.75
    point_t = lambda f: smoothstep(10, 30, f)
    stand(q, N, x, y, 90, arms=lambda f: (arm_dir((0.1, -1.0, 0.12), blend=point_t(f)), (0, 0, 0)),
          neck=lambda f: (R_(-3), R_(-8)), blinks=[60, 150])
    j = lib.build_juno()
    key_hide([j["mug"]], 1, True)
    tap = lambda f: 0.5 + 0.5 * math.sin(f / 2.2) if P[0] + 60 < f < P[0] + 80 else 0.0
    stand(j, N, 3.9, 0.85, 70, neck=lambda f: (R_(-8) + R_(10) * math.sin(f / 4.0) * (1 if P[0] + 50 < f < P[0] + 70 else 0), R_(-30)),
          arms=lambda f: ((R_(-30) * tap(f), 0, 0), (R_(-50), 0, 0)), eyes=lambda f: (R_(-5), R_(-10)), smile=lambda f: 0.3,
          blinks=[40, 120])
    on = P[0] + int(0.45 * (E[0] - P[0]))
    ev("machine_on", on)
    key_emission(SET["machine_dial_mat"], [(1, 0.0), (on, 0.0), (on + 6, 6.0), (on + 9, 2.0), (on + 14, 6.0)], 1, N)
    ml = SET["machine_light"]
    for f in range(1, N + 1):
        ml.data.energy = track(f, [(1, 0.0), (on, 0.0), (on + 6, 40.0), (on + 9, 10.0), (on + 14, 40.0)])
        ml.data.keyframe_insert("energy", frame=f)
    camera({1: (2.35, 2.55, 1.85), N // 2: (2.6, 2.35, 1.78), N: (2.85, 2.2, 1.72)}, {1: 30, N: 34},
           lambda f: Vector((5.0, 1.55, 1.4)).lerp(Vector((MACHINE.x - 0.3, MACHINE.y, 1.0)), smoothstep(on - 30, on + 20, f)),
           1, N, focus=q["neck"], fstop=2.8)


def S05(N, P, E):
    """Juno taps the NEVER TEST ALONE plaque with her clipboard; Quill rolls his eyes."""
    j = lib.build_juno()
    key_hide([j["mug"]], 1, True)
    taps = (P[0] + 6, P[1] - 2, P[1] + 6)
    for t in taps:
        ev("tap", t)
    def tap(f):
        return max([math.exp(-((f - t) / 3.0) ** 2) for t in taps])
    stand(j, N, 4.45, -0.2, 75,
          arms=lambda f: ((0, 0, 0), (R_(-120) * smoothstep(1, 12, f) + R_(-12) * tap(f), R_(8), 0)),
          neck=lambda f: (R_(-28) + R_(18) * smoothstep(P[1] + 10, P[1] + 22, f), R_(40) * smoothstep(P[1] + 10, P[1] + 22, f)),
          eyes=lambda f: (R_(-10), R_(10) * smoothstep(P[1] + 6, P[1] + 14, f)), brows=lambda f: 0.6,
          smile=lambda f: 0.0, blinks=[50])
    q = lib.build_quill()
    stand(q, N, 3.45, 0.75, 120, neck=lambda f: (R_(-10) * smoothstep(P[1] + 10, P[1] + 20, f), R_(-10)),
          eyes=lambda f: (R_(-28) * smoothstep(P[1] + 8, P[1] + 16, f), R_(25) * smoothstep(P[1] + 8, P[1] + 16, f)),
          arms=lambda f: ((R_(-20), R_(-10), 0), (R_(-20), R_(10), 0)), smile=lambda f: 0.0,
          lids=lambda f: 1 - 0.4 * smoothstep(P[1] + 10, P[1] + 18, f), blinks=[30])
    camera({1: (3.55, -2.75, 0.55), N // 2: (3.65, -2.0, 0.85), N: (3.8, -1.25, 1.12)}, {1: 26, N: 34},
           lambda f: Vector((4.6, -0.1, 1.2)).lerp(PLAQUE_LOC, smoothstep(P[1] - 10, P[1] + 10, f)), 1, N,
           focus=j["neck"], fstop=2.8)


def S06(N, P, E):
    """He ignored it: Quill swings the vault door shut on Juno walking away down the corridor."""
    hinge, wheel = SET["door_hinge"], SET["door_wheel"]
    c0, c1 = 12, 52
    ev("door_creak", c0)
    ev("door_thud", c1)
    ev("ratchet", c1 + 4, dur=26)
    for f in range(1, N + 1):
        hinge.rotation_euler.z = R_(-80) * (1 - smoothstep(c0, c1, f))
        hinge.keyframe_insert("rotation_euler", index=2, frame=f)
        wheel.rotation_euler.x = R_(-300) * smoothstep(c1 + 4, c1 + 30, f)
        wheel.keyframe_insert("rotation_euler", index=0, frame=f)
    q = lib.build_quill()
    walk(q, N, [(1, (3.85, -0.35)), (c0, (3.85, -0.35)), (c1, (4.3, -1.05))], [(1, 140), (c0, 120), (c1, 95)],
         [(c0, c1)], neck=lambda f: (R_(-5), R_(-15)), arms=lambda f: ((R_(-70), R_(-10), 0), (R_(-70), R_(10), 0)),
         blinks=[70])
    j = lib.build_juno()
    walk(j, N, [(1, (6.4, -0.2)), (N, (6.45, -3.8))], [(1, 0), (N, 0)], [(1, N)], step=7, hw=0.09,
         neck=lambda f: (R_(-5), 0), arms=lambda f: ((R_(-60), 0, 0), (R_(-35), 0, 0)))
    camera({1: (2.2, 0.6, 2.65), N // 2: (2.55, 0.15, 2.35), N: (2.85, -0.25, 2.05)}, {1: 26, N: 30},
           lambda f: Vector((4.9, -1.5, 1.2)), 1, N, focus=None)


def S07(N, P, E):
    """Locked. Quill turns from the door and presses the cyan button."""
    hinge, wheel = SET["door_hinge"], SET["door_wheel"]
    lock = P[0] + 10
    ev("ratchet", 1, dur=lock - 1)
    ev("bolt", lock)
    for f in range(1, N + 1):
        wheel.rotation_euler.x = R_(-300) + R_(-60) * smoothstep(1, lock, f)
        wheel.keyframe_insert("rotation_euler", index=0, frame=f)
    key_emission(SET["locked_lamp_mat"], [(1, 0.0), (lock, 0.0), (lock + 1, 10.0)], 1, N)
    ll = SET["locked_light"]
    for f in range(1, N + 1):
        ll.data.energy = 0 if f < lock else 15
        ll.data.keyframe_insert("energy", frame=f)
    q = lib.build_quill()
    press = P[1] + 14
    turn = (lock + 4, P[1] - 2)
    stand(q, N, 4.15, -1.25, 0, yawf=lambda f: R_(track(f, [(1, 90), (turn[0], 90), (turn[1], 240)])),
          feet=lambda side, f: (Vector((4.15 + (0.1 if side == "L" else -0.1) * math.cos(R_(track(f, [(1, 90), (turn[0], 90), (turn[1], 240)]))),
                                        -1.25 + (0.1 if side == "L" else -0.1) * math.sin(R_(track(f, [(1, 90), (turn[0], 90), (turn[1], 240)]))), 0)),
                                R_(track(f, [(1, 90), (turn[0], 90), (turn[1], 240)])), 0.0),
          arms=lambda f: ((0, 0, 0), arm_dir((0.25, -0.24, -0.16), 0.36, 0.68, smoothstep(press - 14, press - 4, f))),
          neck=lambda f: (R_(-6) + R_(12) * smoothstep(press - 10, press, f), 0), eyes=lambda f: (R_(10) * smoothstep(press - 14, press - 8, f), 0),
          smile=lambda f: 0.5 * smoothstep(turn[1], turn[1] + 10, f), brows=lambda f: -0.5 + 0.5 * smoothstep(turn[1], turn[1] + 8, f),
          blinks=[turn[1] + 2])
    ev("tone_low", press)
    ev("whine", press, dur=N - press)
    key_emission(q["disc_cyan_mat"], [(1, 3), (press - 1, 3), (press + 1, 30), (press + 14, 6)], 1, N)
    fl = point("press_flash", (4.0, -1.5, 1.4), 0, hex_rgb("#19C3D6"), 0.2)
    for f in range(1, N + 1):
        fl.data.energy = track(f, [(1, 0), (press, 0), (press + 2, 120), (press + 16, 15)])
        fl.data.keyframe_insert("energy", frame=f)
    camera({1: (3.3, -2.75, 1.6), N // 2: (2.7, -2.2, 1.6), N: (2.6, -0.85, 1.65)}, {1: 30, N: 32},
           lambda f: Vector((5.0, -1.6, 2.3)).lerp(head_pos(q), smoothstep(lock - 4, turn[1], f)), 1, N, focus=q["neck"])


def S08(N, P, E):
    """In the mirror: hands, legs, then the whole man dissolve. The mirror shows an empty lab."""
    q = lib.build_quill()
    g = quill_groups(q)
    make_vanishable(all_objs(q))
    x, y = MIRROR_LOC.x, MIRROR_LOC.y - 1.0
    stand(q, N, x, y, 180, arms=lambda f: ((R_(-50) * smoothstep(P[0] - 10, P[0] + 5, f), R_(-15), 0),
                                           (R_(-50) * smoothstep(P[0] - 10, P[0] + 5, f), R_(15), 0)),
          neck=lambda f: (R_(25) * smoothstep(P[0] - 5, P[0] + 5, f) * (1 - smoothstep(P[1] + 5, P[2], f)), 0),
          brows=lambda f: smoothstep(P[0], P[0] + 8, f), mouth_open=lambda f: 0.4 * smoothstep(P[1], P[1] + 8, f),
          blinks=[P[2] - 6])
    key_vanish(g["hands"], [(1, 0), (P[0], 0), (E[0] + 4, 1.0)], 1, N)
    key_vanish(g["legs"], [(1, 0), (P[1], 0), (E[1] + 4, 1.0)], 1, N)
    key_vanish(g["body"] + g["disc"], [(1, 0), (P[2], 0), (E[2] - 2, 1.0)], 1, N)
    for t in (P[0] + 2, P[1] + 2, P[2] + 4):
        ev("shimmer", t)
    shimmer = point("vanish_shimmer", (x, y - 0.3, 1.2), 0, hex_rgb("#19C3D6"), 0.4)
    for f in range(1, N + 1):
        shimmer.data.energy = 40 * max(math.exp(-((f - t) / 8) ** 2) for t in (P[0] + 6, P[1] + 6, P[2] + 10))
        shimmer.data.keyframe_insert("energy", frame=f)
    camera({1: (-0.35, 0.35, 1.72), N // 2: (-0.45, 0.85, 1.76), N: (-0.55, 1.35, 1.8)}, {1: 30, N: 32},
           lambda f: Vector((x - 0.05, MIRROR_LOC.y, 1.42)), 1, N, focus=SET["mirror"], fstop=4.0)


def S09(N, P, E):
    """The amber button, pressed again and again. Nothing. Then even the disc fades; alarms start."""
    q = lib.build_quill()
    g = quill_groups(q)
    make_vanishable(g["disc"])
    key_hide(g["hands"] + g["legs"] + g["body"], 1, True)
    x, y = MAT_C.x, MAT_C.y
    stand(q, N, x, y, 0)
    presses = [P[0] + 6 + 14 * k for k in range(4)]
    for t in presses:
        ev("click", t)
    ev("error", P[1])
    ev("alarm_on", P[1] + 4)
    btn = q["btn_amber"]
    keys = [(1, 1.0)]
    em = [(1, 2.0)]
    for t in presses:
        keys += [(t - 1, 1.0), (t + 1, 0.35), (t + 5, 1.0)]
        em += [(t - 1, 2.0), (t + 1, 10.0), (t + 6, 2.0)]
    for f, s in keys:
        btn.scale = (1, s, 1)
        btn.keyframe_insert("scale", frame=f)
    key_emission(bpy.data.materials["disc_amber_vanish"], em, 1, N)
    key_vanish(g["disc"], [(1, 0), (P[1] + 6, 0), (E[1] + 6, 1.0)], 1, N)
    prints = footprint("dentL", (x + 0.1, y - 0.03, 0.017), 0) + footprint("dentR", (x - 0.1, y - 0.03, 0.017), 0)
    red_strobes(P[1] + 4, 1, N)
    near_flask("near", (1.3, 0.55, 0.74))
    box("near_cart", (1.3, 0.55, 0.36), (0.4, 0.35, 0.72), M["bench_body"], "ENV_near", bevel=0.02)
    camera({1: (1.55, 0.15, 1.35), N // 2: (1.1, -0.05, 1.38), N: (0.7, -0.1, 1.42)}, {1: 36, N: 40},
           lambda f: Vector((x, y - 0.18, 1.32)), 1, N, focus=q["body"], fstop=2.8)


def S10(N, P, E):
    """He rips off the suit: it pops into view, flies and crumples beside two footprints."""
    x, y = MAT_C.x, MAT_C.y
    rip = P[0] + 10
    land = rip + 18
    ev("rip", rip)
    ev("cloth_thump", land)
    suit = empty("suit_root", (0, 0, 0), col="CHAR_quill")
    tex = bpy.data.textures.new("crumple", "CLOUDS")
    tex.noise_scale = 0.25
    parts = []
    torso = sphere("suit_torso", (0, 0, 0), (0.24, 0.32, 0.06), M["q_suit"], "CHAR_quill", seg=32)
    d = torso.modifiers.new("disp", "DISPLACE")
    d.texture, d.strength = tex, 0.05
    parts.append(torso)
    for nm, loc, rz, ln in (("sleeve_L", (0.3, -0.12, 0.0), 70, 0.5), ("sleeve_R", (-0.28, -0.05, 0.0), -100, 0.45),
                            ("leg_L", (0.12, 0.52, 0.0), 10, 0.55), ("leg_R", (-0.14, 0.5, 0.0), -25, 0.6)):
        o = cyl(f"suit_{nm}", loc, 0.06, ln, M["q_suit"], "CHAR_quill", verts=16, rot=(R_(90), 0, R_(rz)))
        o.scale = (1, 1, 1)
        o.modifiers.new("flat", "SIMPLE_DEFORM").deform_method = "BEND"
        o.modifiers["flat"].angle = R_(25)
        lib.smooth(o, 1)
        parts.append(o)
    disc = cyl("suit_disc", (0.0, -0.1, 0.06), 0.07, 0.02, M["dark_metal"], "CHAR_quill", verts=24)
    dm = mat("suit_disc_amber", (0.1, 0.06, 0.0), 0.3, emit=hex_rgb("#F2A33A"), strength=1.0)
    da = sphere("suit_disc_btn", (0.03, -0.1, 0.075), (0.022, 0.022, 0.012), dm, "CHAR_quill", seg=12)
    parts += [disc, da]
    for o in parts:
        lib.parent_keep(o, suit)
    make_vanishable(parts)
    key_vanish(parts, [(1, 1.0), (rip, 1.0), (rip + 6, 0.0)], 1, N)
    p0, p1 = Vector((x, y - 0.1, 1.2)), Vector((x + 0.9, y - 0.8, 0.09))
    for f in range(1, N + 1):
        u = smoothstep(rip, land, f) if f < land else 1.0
        u = min(1.0, max(0.0, (f - rip) / (land - rip)))
        pos = p0.lerp(p1, u) + Vector((0, 0, 0.6 * math.sin(math.pi * u)))
        suit.location = pos
        suit.rotation_euler = (R_(-360) * u if u < 1 else 0.0, R_(25) * math.sin(math.pi * u), R_(70) * u)
        sq = 1.0 - 0.3 * math.exp(-((f - land) / 3.0) ** 2) if f >= land - 2 else 1.0
        flap = 1.0 + 0.25 * math.sin(f * 0.9) * (1 - u) if f < land else 1.0
        suit.scale = (1 / math.sqrt(sq), flap / math.sqrt(sq), sq)
        for prop in ("location", "rotation_euler", "scale"):
            suit.keyframe_insert(prop, frame=f)
    footprint("dentL", (x + 0.1, y - 0.03, 0.017), 0)
    footprint("dentR", (x - 0.1, y - 0.03, 0.017), 0)
    red_strobes(1, 1, N)
    camera({1: (x - 1.0, y - 2.0, 0.55), N // 2: (x - 0.4, y - 2.15, 0.42), N: (x + 0.2, y - 2.05, 0.38)}, {1: 26, N: 30},
           lambda f: (suit.matrix_world.translation.copy() if f > rip else Vector((x, y, 0.9))) + Vector((0, 0, 0.05)), 1, N,
           focus=suit, fstop=2.8, damp=0.35)
    # foreground stool on the camera path
    SET["stool"].location = (x - 1.25, y - 1.55, 0)


def S11(N, P, E):
    """SCANNER rolls up, probes the empty mat and flashes the warning."""
    S = lib.build_scanner(loc=(0, 0, 0))
    roll_end = P[0] + 20
    for f in range(1, N + 1):
        p = track(f, [(1, (2.9, -1.0)), (roll_end, (1.55, 0.35))])
        S["root"].location = (p[0], p[1], 0)
        S["root"].rotation_euler.z = R_(track(f, [(1, 40), (roll_end, 35), (P[1] - 4, 35), (P[1] + 6, 0)]))
        S["body"].location.z = 0.008 * math.sin(f * 1.7) if f < roll_end else 0.0
        S["head"].rotation_euler = (R_(4) * math.sin(f / 6), 0, 0)
        S["arm"].rotation_euler = (0, 0, R_(track(f, [(1, 0), (roll_end, 0), (roll_end + 10, 35), (P[1] - 2, 35), (P[1] + 6, 0)])))
        for o, prop in ((S["root"], "location"), (S["root"], "rotation_euler"), (S["body"], "location"),
                        (S["head"], "rotation_euler"), (S["arm"], "rotation_euler")):
            o.keyframe_insert(prop, frame=f)
    bpy.context.view_layer.update()
    scan = lib.scanner_text(S, "SCANNING...", red=False, size=0.04, name="scanner_txt_scan")
    lines = [lib.scanner_text(S, t, size=s, name=f"scanner_txt_w{i}") for i, (t, s) in
             enumerate((("NINETY SECONDS", 0.038), ("UNTIL PERMANENT", 0.03), ("DISPLACEMENT", 0.03)))]
    for i, o in enumerate(lines):
        o.location.z += 0.07 - i * 0.055
    warn = P[1]
    ev("roll", 1, dur=roll_end)
    for t in range(roll_end + 6, warn - 4, 18):
        ev("beep", t)
    ev("warning", warn)
    key_hide([scan], 1, False)
    key_hide([scan], warn, True)
    key_hide(lines, 1, True)
    key_hide(lines, warn, False)
    bg = S["screen"]
    red_bg = emis("screen_flash", (1.0, 0.05, 0.03), 3.0)
    bg.data.materials.append(red_bg)
    for b in S["brows"]:
        for f, r in ((warn - 1, 0), (warn + 3, R_(-20) if "L" in b.name else R_(20))):
            b.rotation_euler.y = r
            b.keyframe_insert("rotation_euler", index=1, frame=f)
    lamp = M["red_lamp"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    flash = point("warn_flash", (1.5, -0.4, 1.1), 0, (1.0, 0.05, 0.03), 0.2)
    for f in range(1, N + 1):
        flash.data.energy = 60 * math.exp(-((f - warn - 2) / 4) ** 2) + (8 if f > warn else 0)
        flash.data.keyframe_insert("energy", frame=f)
    red_strobes(1, 1, N)
    mote(1, N, lambda f: (MAT_C.x, MAT_C.y, 1.2))
    camera({1: (1.05, -1.95, 1.25), N // 2: (1.2, -1.25, 1.12), N: (1.4, -0.62, 1.07)}, {1: 30, N: 34},
           lambda f: (S["head"].matrix_world.translation + Vector((0, -0.2, 0))), 1, N, focus=S["head"], fstop=2.8, damp=0.3)


def _holo_beam(src, dst):
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=0.02, radius2=0.35, depth=1.0)
    c = bpy.context.object
    c.name = "holo_beam"
    link(lib.assign(c, holo_mat("beam", hex_rgb("#19C3D6"), 0.6)), "FX")
    d = Vector(dst) - Vector(src)
    c.location = Vector(src) + d / 2
    c.scale = (1, 1, d.length)
    c.rotation_mode = "QUATERNION"
    c.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    c.visible_shadow = False
    return c


def _holo_stage(N, hc_z=1.38):
    S = lib.build_scanner(loc=(1.5, 0.35, 0))
    S["head"].rotation_euler.x = R_(-25)
    dim_lab([(1, 0.25), (N, 0.25)])
    red_strobes(1, 1, N, energy=250, period=48)
    return S


def S12(N, P, E):
    """Hologram of the arm: glittering particles sink from the surface into the skin layer."""
    S = _holo_stage(N)
    c = Vector((1.5, 0.35, 1.75))
    skin = cyl("holo_arm_skin", c, 0.11, 0.9, M["holo"], "FX", verts=32, rot=(0, R_(90), 0))
    lib.smooth(skin, 1)
    muscle = cyl("holo_arm_muscle", c, 0.075, 0.86, holo_mat("holo_muscle", (0.9, 0.35, 0.3), 1.2), "FX", verts=24, rot=(0, R_(90), 0))
    hand = sphere("holo_hand", c + Vector((0.55, 0, 0)), (0.11, 0.05, 0.1), M["holo"], "FX", seg=24)
    for k in range(4):
        cyl(f"holo_finger_{k}", c + Vector((0.72, 0, 0.06 - 0.04 * k)), 0.015, 0.13, M["holo"], "FX", verts=10, rot=(0, R_(90), 0))
    # glitter particles in one mesh around the arm axis (object origin on the axis -> radial scale sinks them)
    import bmesh
    bm = bmesh.new()
    rng = random.Random(3)
    for _ in range(260):
        a = rng.uniform(0, 2 * math.pi)
        xx = rng.uniform(-0.45, 0.45)
        rr = 0.125 + rng.uniform(0, 0.03)
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.006,
                                   matrix=__import__("mathutils").Matrix.Translation((xx, rr * math.cos(a), rr * math.sin(a))))
    me = bpy.data.meshes.new("holo_particles")
    bm.to_mesh(me)
    parts = bpy.data.objects.new("holo_particles", me)
    lib.COL["FX"].objects.link(parts)
    parts.location = c
    pm = emis("holo_particle_mat", (0.6, 1.0, 1.0), 5.0)
    me.materials.append(pm)
    parts.visible_shadow = False
    sink0, sink1 = P[1], E[2]
    ev("glitter", sink0, dur=sink1 - sink0)
    ev("bonded", P[2] + 24)
    col = pm.node_tree.nodes["Emission"].inputs["Color"]
    for f in range(1, N + 1):
        s = track(f, [(1, 1.0), (sink0, 1.0), (P[2], 0.72), (sink1, 0.66)])
        jitter = 0.01 * math.sin(f * 0.9)
        parts.scale = (1.0, s + jitter, s - jitter)
        parts.rotation_euler.x = f * 0.01
        parts.keyframe_insert("scale", frame=f)
        parts.keyframe_insert("rotation_euler", index=0, frame=f)
        u = smoothstep(P[2], P[2] + 30, f)
        col.default_value = (lerp(0.45, 1.0, u), lerp(0.95, 0.04, u), lerp(1.0, 0.02, u), 1)
        col.keyframe_insert("default_value", frame=f)
    tag = text("holo_tag", "BONDED", c + Vector((0.0, -0.02, 0.24)), 0.07, M["holo_red"], "FX")
    key_hide([tag], 1, True)
    key_hide([tag], P[2] + 24, False)
    _holo_beam(S["hc"] + Vector((0, -0.05, 0.25)), c - Vector((0, 0, 0.12)))
    th = lambda a: Vector((c.x + 1.15 * math.sin(R_(a)), c.y - 1.15 * math.cos(R_(a)), c.z + 0.1))
    camera({1: th(-40), N // 2: th(-5), N: th(30)}, {1: 32, N: 36}, lambda f: c + Vector((0.12, 0, 0)), 1, N, focus=skin, fstop=4)


def _holo_figure(c, mat_):
    """A small hologram of Quill's silhouette (box head, noodle body)."""
    objs = [lib.rbox("hf_head", c + Vector((0, 0, 0.88)), (0.17, 0.16, 0.2), mat_, "FX"),
            sphere("hf_torso", c + Vector((0, 0, 0.5)), (0.11, 0.08, 0.22), mat_, "FX", seg=24),
            sphere("hf_hips", c + Vector((0, 0, 0.3)), (0.09, 0.07, 0.08), mat_, "FX", seg=20)]
    for sx in (-1, 1):
        objs.append(cyl(f"hf_leg_{sx}", c + Vector((sx * 0.05, 0, 0.13)), 0.03, 0.3, mat_, "FX", verts=12))
    objs.append(cyl("hf_arm_R", c + Vector((-0.27, 0, 0.66)), 0.027, 0.36, mat_, "FX", verts=12, rot=(0, R_(90), 0)))
    objs.append(sphere("hf_hand_R", c + Vector((-0.47, 0, 0.66)), (0.035, 0.03, 0.035), mat_, "FX", seg=12))
    objs.append(cyl("hf_arm_L", c + Vector((0.13, 0, 0.5)), 0.027, 0.32, mat_, "FX", verts=12, rot=(0, R_(15), 0)))
    eyes = [sphere(f"hf_eye_{sx}", c + Vector((sx * 0.04, -0.08, 0.9)), (0.022, 0.012, 0.025), mat_, "FX", seg=12) for sx in (-1, 1)]
    return objs, eyes


def _front_mat(name, center, value_keys, f0, f1):
    """Hologram material: red where the world position is within `radius` of `center`, cyan elsewhere."""
    m = holo_mat(name, hex_rgb("#19C3D6"), 2.5)
    nt = m.node_tree
    em = nt.nodes["Emission"]
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    dist = nt.nodes.new("ShaderNodeVectorMath")
    dist.operation = "DISTANCE"
    dist.inputs[1].default_value = center
    nt.links.new(geo.outputs["Position"], dist.inputs[0])
    val = nt.nodes.new("ShaderNodeValue")
    sub = nt.nodes.new("ShaderNodeMath")
    sub.operation = "SUBTRACT"
    nt.links.new(val.outputs[0], sub.inputs[0])
    nt.links.new(dist.outputs["Value"], sub.inputs[1])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = -0.02, 0.02
    nt.links.new(sub.outputs[0], mr.inputs["Value"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["A"].default_value = (*hex_rgb("#19C3D6"), 1)
    mix.inputs["B"].default_value = (1.0, 0.1, 0.06, 1)
    nt.links.new(mr.outputs["Result"], mix.inputs["Factor"])
    nt.links.new(mix.outputs["Result"], em.inputs["Color"])
    for f in range(f0, f1 + 1):
        val.outputs[0].default_value = track(f, value_keys)
        val.outputs[0].keyframe_insert("default_value", frame=f)
    return m


def S13(N, P, E):
    """The bonded front spreads up the arm, through the body, into the eyes."""
    S = _holo_stage(N)
    c = Vector((1.5, 0.35, 1.38))
    hand = c + Vector((-0.47, 0, 0.66))
    m = _front_mat("holo_front", hand, [(1, 0.0), (P[0], 0.05), (E[0], 0.3), (E[1], 0.6), (E[2] - 4, 0.75)], 1, N)
    objs, eyes = _holo_figure(c, m)
    eye_m = emis("holo_eye", (0.6, 1.0, 1.0), 6.0)
    for e in eyes:
        lib.assign(e, eye_m)
    ec = eye_m.node_tree.nodes["Emission"].inputs["Color"]
    for f in range(1, N + 1):
        u = smoothstep(P[2], E[2], f)
        ec.default_value = (lerp(0.6, 1.0, u), lerp(1.0, 0.1, u), lerp(1.0, 0.05, u), 1)
        ec.keyframe_insert("default_value", frame=f)
    ev("swell", P[0], dur=E[2] - P[0])
    _holo_beam(S["hc"] + Vector((0, -0.05, 0.25)), c + Vector((0, 0, 0.0)))
    camera({1: (1.15, -0.85, 1.65), N // 2: (1.3, -0.95, 2.0), N: (1.45, -0.85, 2.35)}, {1: 30, N: 34},
           lambda f: (hand.lerp(c + Vector((0, 0, 0.5)), 0.5)).lerp(c + Vector((0, 0, 0.88)), smoothstep(P[0], E[2], f)), 1, N, focus=None)


def S14(N, P, E):
    """Macro of the hologram eye: light bends around the retina and never reaches it."""
    S = _holo_stage(N)
    dim_lab([(1, 0.2), (P[1], 0.2), (P[1] + 10, 0.06), (N, 0.06)])
    c = Vector((1.5, 0.35, 1.95))
    shell = sphere("eye_shell", c, (0.26, 0.26, 0.26), M["holo"], "FX", seg=48)
    iris = lib.torus("eye_iris", c + Vector((0, -0.245, 0)), 0.08, 0.025, holo_mat("iris", hex_rgb("#19C3D6"), 4.0), "FX",
                     rot=(R_(90), 0, 0), maj=40, mn=10)
    ret_m = emis("retina", hex_rgb("#19C3D6"), 6.0)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=40, ring_count=20, radius=0.22, location=c)
    ret = bpy.context.object
    ret.name = "eye_retina"
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(ret.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.y < 0.08], context="VERTS")
    bm.to_mesh(ret.data)
    bm.free()
    link(lib.assign(ret, ret_m), "FX")
    rs = ret_m.node_tree.nodes["Emission"].inputs["Strength"]
    for f in range(1, N + 1):
        rs.default_value = track(f, [(1, 6.0), (P[0] + 20, 6.0), (E[0], 0.6), (P[1], 0.15), (P[1] + 6, 0.0)])
        rs.keyframe_insert("default_value", frame=f)
    # light rays: straight set (reaching the retina) and bent set (deflected around it)
    ray_m = emis("ray", (1.0, 0.92, 0.75), 4.0)
    straight, bent = [], []
    for k in range(10):
        a = 2 * math.pi * k / 10
        r0 = 0.05
        p0 = c + Vector((-0.55 + 0.08 * math.cos(a), -0.75, 0.55 + 0.08 * math.sin(a)))
        for kind, lst in (("s", straight), ("b", bent)):
            cu = bpy.data.curves.new(f"ray_{kind}{k}", "CURVE")
            cu.dimensions = "3D"
            cu.bevel_depth = 0.0022
            sp = cu.splines.new("BEZIER")
            sp.bezier_points.add(2)
            if kind == "s":
                pts = [p0, c + Vector((0.02 * math.cos(a), -0.24, 0.02 * math.sin(a))), c + Vector((0.18 * math.cos(a), 0.12, 0.18 * math.sin(a)))]
            else:
                pts = [p0, c + Vector((0.32 * math.cos(a), -0.05, 0.32 * math.sin(a))), c + Vector((0.12 * math.cos(a), 0.9, 0.12 * math.sin(a)))]
            for bp, pt in zip(sp.bezier_points, pts):
                bp.co = pt
                bp.handle_left_type = bp.handle_right_type = "AUTO"
            o = bpy.data.objects.new(f"ray_{kind}{k}", cu)
            lib.COL["FX"].objects.link(o)
            o.data.materials.append(ray_m)
            o.visible_shadow = False
            lst.append(o)
    swap = P[0] + int(0.55 * (E[0] - P[0]))
    ev("bend", swap)
    ev("drain", P[1])
    for k, (s, b) in enumerate(zip(straight, bent)):
        t = swap + 2 * k
        key_hide([s], 1, False)
        key_hide([s], t, True)
        key_hide([b], 1, True)
        key_hide([b], t, False)
    camera({1: (1.5, -1.1, 1.97), N // 2: (1.48, -0.8, 1.96), N: (1.5, -0.55, 1.95)}, {1: 34, N: 40},
           lambda f: c, 1, N, focus=None)


def S15(N, P, E):
    """An invisible rush: the stool spins away, papers fly, footprints race to the door and stop dead."""
    start, stop = 8, P[1] - 2
    path = [Vector((-0.9, 0.9)), Vector((0.6, 0.0)), Vector((2.4, -0.7)), Vector((3.95, -1.25))]
    pts = []
    n_steps = 13
    for k in range(n_steps):
        u = k / (n_steps - 1)
        seg = min(2, int(u * 3))
        uu = u * 3 - seg
        p = path[seg].lerp(path[seg + 1], uu)
        d = (path[seg + 1] - path[seg]).normalized()
        yaw = math.atan2(d.x, -d.y)
        side = 0.1 if k % 2 == 0 else -0.1
        p = p + Vector((math.cos(yaw), math.sin(yaw))) * side
        pts.append((p, yaw))
    times = [start + int((stop - start) * k / (n_steps - 1)) for k in range(n_steps)]
    for k, t in enumerate(times):
        ev("step", t, who="quill", side="L" if k % 2 == 0 else "R", run=True)
    ev("stop", stop)
    for k, ((p, yaw), t) in enumerate(zip(pts, times)):
        objs = footprint(f"run_{k}", (p.x, p.y, 0.003), yaw, size=1.05)
        key_hide(objs, 1, True)
        key_hide(objs, t, False)
    st = SET["stool"]
    st.location = (0.1, 0.55, 0)
    hit = times[2]
    ev("stool", hit)
    ev("papers", times[1])
    for f in range(1, N + 1):
        u = smoothstep(hit, hit + 30, f)
        st.location = (lerp(0.1, -0.6, u), lerp(0.55, -0.6, u), 0)
        st.rotation_euler = (R_(8) * math.sin(math.pi * u), 0, R_(540) * (1 - (1 - u) ** 2))
        st.keyframe_insert("location", frame=f)
        st.keyframe_insert("rotation_euler", frame=f)
    rng = random.Random(5)
    for i, p in enumerate(SET["papers"]):
        p.location = (-0.6 + rng.uniform(-0.2, 0.2), 0.95 + rng.uniform(-0.2, 0.2), 0.905 + i * 0.002)
        lib.box  # keep linter quiet
        t0 = times[1] + rng.randint(0, 4)
        p0 = p.location.copy()
        p1 = Vector((p0.x + rng.uniform(0.5, 2.0), p0.y + rng.uniform(-1.6, -0.4), 0.002 + i * 0.001))
        r0 = p.rotation_euler.copy()
        for f in range(1, N + 1):
            u = min(1.0, max(0.0, (f - t0) / 40.0))
            e = 1 - (1 - u) ** 2
            pos = p0.lerp(p1, e) + Vector((0, 0, 0.9 * math.sin(math.pi * min(1.0, u * 1.3)) * (1 - u)))
            p.location = pos
            p.rotation_euler = (r0.x + R_(rng.uniform(-1, 1)) * 0 + math.sin(u * 9 + i) * R_(50) * (1 - u), math.cos(u * 7 + i) * R_(40) * (1 - u),
                                r0.z + u * R_(120 + 30 * i))
            p.keyframe_insert("location", frame=f)
            p.keyframe_insert("rotation_euler", frame=f)
    red_strobes(1, 1, N)
    mote(1, N, lambda f: (track(f, [(1, (-0.9, 0.9)), (stop, (3.9, -1.2))]) + (1.2,)))
    near_flask("near", (0.9, -1.85, 0.0))
    front = lambda f: track(f, [(1, (-0.9, 0.9)), (start, (-0.9, 0.9)), (stop, (3.95, -1.25))])
    camera({1: (-1.5, -2.45, 1.05), N // 2: (0.6, -2.6, 1.1), N: (2.5, -2.55, 1.15)}, {1: 26, N: 28},
           lambda f: Vector((front(f)[0], front(f)[1], 0.45)), 1, N, focus=None, damp=0.2)


def S16(N, P, E):
    """Through the glass: Juno arrives at the window, out of reach, the machine beside her."""
    j = lib.build_juno()
    arrive = P[1] + 6
    walk(j, N, [(1, (6.1, -2.4)), (arrive, (5.62, 1.15))], [(1, 10), (arrive - 16, 10), (arrive, -90)], [(1, arrive)], step=7, hw=0.09,
         neck=lambda f: (R_(-12) * smoothstep(arrive, arrive + 12, f), R_(-10) * smoothstep(arrive, arrive + 12, f)),
         eyes=lambda f: (R_(-6), R_(-5)), arms=lambda f: ((R_(-60), 0, 0), (R_(-35), 0, 0)),
         brows=lambda f: smoothstep(arrive + 6, arrive + 14, f), blinks=[arrive + 18])
    S = lib.build_scanner(loc=(2.9, -0.4, 0), yaw=R_(60))
    red_strobes(1, 1, N)
    camera({1: (2.5, 1.0, 1.3), N // 2: (3.35, 1.15, 1.22), N: (4.25, 1.3, 1.15)}, {1: 30, N: 34},
           lambda f: Vector((5.9, 1.0, 1.05)) if f > arrive - 20 else Vector((6.1, -0.6, 1.0)), 1, N,
           focus=j["neck"], damp=0.12)


def S17(N, P, E):
    """Corridor side: breath fog and palm prints come and go on the glass; Juno looks straight through them."""
    j = lib.build_juno()
    key_hide(j["clipboard"], 1, False)
    shrug = P[3]
    stand(j, N, 5.62, 1.15, -90,
          neck=lambda f: (R_(-12), R_(-55) * smoothstep(shrug + 4, shrug + 18, f)),
          eyes=lambda f: (R_(-8), R_(-12) * smoothstep(shrug + 2, shrug + 10, f)),
          arms=lambda f: ((R_(-60), R_(-30) * math.sin(math.pi * smoothstep(shrug, shrug + 16, f)), 0),
                          (R_(-35), R_(30) * math.sin(math.pi * smoothstep(shrug, shrug + 16, f)), 0)),
          body_extra=lambda f: (0.03 * math.sin(math.pi * smoothstep(shrug, shrug + 16, f)), 0, 0),
          brows=lambda f: 0.4 * math.sin(math.pi * smoothstep(shrug, shrug + 16, f)), smile=lambda f: 0.15,
          blinks=[P[1] + 10, shrug + 20])
    ev("silence", P[1], dur=E[1] - P[1] + 6)
    gx = GLASS_X - 0.004
    fog = decal("breath_fog", (gx, 1.55, 1.85), (0.13, 0.09, 1), M["fog"], rot=(0, R_(90), 0))
    for f in range(1, N + 1):
        a = track(f, [(1, 0.0), (P[0] + 2, 0.0), (P[0] + 6, 0.6), (P[1] + 20, 0.0)])
        fog.scale = (0.13 * (0.6 + a), 0.09 * (0.6 + a), 1)
        fog.keyframe_insert("scale", frame=f)
        key_hide([fog], f, a < 0.03)
    wave_ts = [P[2] + 2, P[2] + 10, P[2] + 18]
    for k, t in enumerate(wave_ts):
        hp = palm_print(f"palm_{k}", (gx, 1.3 + 0.28 * k, 1.6 + 0.05 * (k % 2)), M["smudge"])
        key_hide(hp, 1, True)
        key_hide(hp, t, False)
        key_hide(hp, t + 14, True)
    camera({1: (6.15, 2.75, 1.05), N // 2: (6.05, 2.6, 1.1), N: (5.95, 2.45, 1.15)}, {1: 28, N: 30},
           lambda f: Vector((5.3, 1.35, 1.35)).lerp(head_pos(j), smoothstep(shrug - 6, shrug + 10, f)), 1, N, focus=j["neck"], fstop=2.8)


def S18(N, P, E):
    """SIXTY. A fist hits the glass: a smudge and a shudder. Juno has turned away. THIRTY."""
    S = lib.build_scanner(loc=(3.65, -0.35, 0), yaw=R_(-25))
    t60 = lib.scanner_text(S, "60", size=0.13, name="txt60")
    t30 = lib.scanner_text(S, "30", size=0.13, name="txt30")
    key_hide([t60], 1, False)
    key_hide([t60], P[3], True)
    key_hide([t30], 1, True)
    key_hide([t30], P[3], False)
    hit = P[1] + int(0.75 * (E[1] - P[1]))
    ev("beep", P[0])
    ev("thump", hit)
    ev("beep", P[3])
    win = SET["window"]
    x0 = win.location.x
    for f in range(1, N + 1):
        win.location.x = x0 + (0.006 * math.exp(-(f - hit) / 5.0) * math.sin((f - hit) * 2.4) if f >= hit else 0)
        win.keyframe_insert("location", index=0, frame=f)
    fist = [decal("fist_smudge", (GLASS_X - 0.004, 1.35, 1.55), (0.06, 0.05, 1), M["smudge"], rot=(0, R_(90), 0))]
    for k in range(4):
        fist.append(decal(f"fist_knuckle_{k}", (GLASS_X - 0.004, 1.3 + 0.03 * k, 1.6), (0.014, 0.014, 1), M["smudge"], rot=(0, R_(90), 0)))
    key_hide(fist, 1, True)
    key_hide(fist, hit, False)
    j = lib.build_juno()
    stand(j, N, 5.95, 1.95, 170, neck=lambda f: (R_(22), 0), eyes=lambda f: (R_(15), 0),
          arms=lambda f: ((R_(-40), 0, 0), (R_(-60), 0, 0)), blinks=[60, 130])
    red_strobes(1, 1, N, period=22)
    tgt = lambda f: (S["head"].matrix_world.translation + Vector((0, -0.2, 0))).lerp(Vector((GLASS_X, 1.4, 1.5)),
                                                                                       track(f, [(1, 0), (P[1] - 4, 0), (P[1] + 6, 1), (P[3] - 6, 1), (P[3] + 2, 0)]))
    camera({1: (2.55, -1.3, 1.2), N // 2: (2.75, -0.75, 1.32), N: (2.6, -1.25, 1.22)}, {1: 28, N: 28}, tgt, 1, N, focus=None, damp=0.3)


def S19(N, P, E):
    """The sprinkler lever is yanked down by an unseen hand; the heads pop."""
    lp = SET["lever"]
    pull = P[1] + 4
    ev("lever", pull)
    ev("pipe_groan", pull + 3)
    ev("water_on", pull + 14)
    for f in range(1, N + 1):
        a = track(f, [(1, -35), (pull - 2, -35), (pull - 1, -30), (pull + 4, 52), (pull + 7, 46), (pull + 10, 50)])
        lp.rotation_euler.y = R_(a)
        lp.keyframe_insert("rotation_euler", index=1, frame=f)
    for d in SET["sprinklers"]:
        z0 = d.location.z
        for f, dz in ((pull + 6, 0), (pull + 9, -0.03)):
            d.location.z = z0 + dz
            d.keyframe_insert("location", index=2, frame=f)
    sprinkler_rain(pull + 14, 1, N, n=500)
    red_strobes(1, 1, N)
    camera({1: (-3.3, -2.5, 0.95), N // 2: (-3.75, -2.05, 1.1), N: (-4.1, -1.75, 1.25)}, {1: 26, N: 34},
           lambda f: LEVER_LOC + Vector((0.12, 0, 0.05)), 1, N, focus=lp, fstop=2.8)


def _wet_quill(amount_keys, N):
    q = lib.build_quill(undressed=True)
    wm = water_shell_mat("water_shell")
    for o in all_objs(q):
        if o.type in ("MESH", "FONT"):
            o.data.materials.clear()
            o.data.materials.append(wm)
    amt = wm.node_tree.nodes["water_amount"].inputs[1]
    mp = wm.node_tree.nodes[wm["mapping"]].inputs["Location"]
    for f in range(1, N + 1):
        amt.default_value = track(f, amount_keys)
        amt.keyframe_insert("default_value", frame=f)
        mp.default_value = (0, 0, 0.11 * f)
        mp.keyframe_insert("default_value", frame=f)
    return q


def S20(N, P, E):
    """Sprinkler rain outlines a tall man with his hands on the glass. Juno turns, and sees him."""
    sprinkler_rain(1, 1, N)
    q = _wet_quill([(1, 0.0), (P[0] + 6, 0.0), (P[0] + 30, 0.55), (P[2], 0.8), (N, 1.0)], N)
    stand(q, N, 4.45, 1.5, 90, arms=lambda f: ((R_(-78), R_(-12), 0), (R_(-78), R_(12), 0)),
          neck=lambda f: (R_(-4), 0), mouth_open=lambda f: 0.5)
    j = lib.build_juno()
    turn = P[1] + 4
    ev("gasp", turn + 16)
    yawj = lambda f: R_(track(f, [(1, 180), (turn, 180), (turn + 14, 270)]))
    hw = 0.09
    stand(j, N, 5.75, 2.25, 180, yawf=yawj,
          feet=lambda side, f: (Vector((5.75 + (hw if side == "L" else -hw) * math.cos(yawj(f)), 2.25 + (hw if side == "L" else -hw) * math.sin(yawj(f)), 0)), yawj(f), 0.0),
          neck=lambda f: (R_(-14) * smoothstep(turn + 6, turn + 20, f), 0), eyes=lambda f: (R_(-10) * smoothstep(turn + 8, turn + 14, f), 0),
          arms=lambda f: ((R_(-60) + R_(-30) * smoothstep(P[2], P[2] + 12, f), 0, 0), (R_(-35), 0, 0)),
          mouth_open=lambda f: smoothstep(turn + 16, turn + 26, f), brows=lambda f: 1.2 * smoothstep(turn + 14, turn + 22, f),
          lids=lambda f: 1 + 0.25 * smoothstep(turn + 14, turn + 22, f), blinks=[turn + 2])
    red_strobes(1, 1, N)
    camera({1: (7.0, 3.35, 0.95), N // 2: (6.85, 3.15, 1.35), N: (6.6, 2.95, 1.75)}, {1: 28, N: 30},
           lambda f: head_pos(j).lerp(Vector((4.6, 1.5, 1.6)), smoothstep(turn, P[2] + 10, f)), 1, N, focus=j["neck"], fstop=2.8)


def S21(N, P, E):
    """Juno sprints to the machine, leaps for the lever and pulls the reversal pulse."""
    j = lib.build_juno()
    key_hide(j["clipboard"] + [j["mug"]], 1, True)
    arrive = P[1] + 2
    pull = P[2] + 14
    ev("beep", P[1])
    ev("lever", pull + 3)
    ev("charge", pull, dur=N - pull)
    walk(j, N, [(1, (5.7, 3.9)), (arrive, (6.5, 0.9))], [(1, 0), (arrive - 10, 10), (arrive, 150)], [(1, arrive)],
         step=6, hw=0.09, lift=0.12,
         arms=lambda f: (arm_dir((0.15, -0.5, 1.0), blend=smoothstep(arrive, arrive + 10, f)),
                         arm_dir((-0.15, -0.5, 1.0), blend=smoothstep(arrive, arrive + 10, f))),
         body_extra=lambda f: (0.25 * math.sin(math.pi * smoothstep(pull - 12, pull + 6, f)), 0, 0),
         neck=lambda f: (R_(-25) * smoothstep(arrive, arrive + 10, f), 0), brows=lambda f: 1.0, mouth_open=lambda f: 0.3,
         lean_extra=lambda f: R_(12) * (1 - smoothstep(arrive - 8, arrive, f)))
    S = lib.build_scanner(loc=(4.35, 1.2, 0), yaw=R_(90))
    t20 = lib.scanner_text(S, "20", size=0.13, name="txt20")
    lv = SET["machine_lever"]
    nd = SET["needle"]
    for f in range(1, N + 1):
        lv.rotation_euler.y = R_(track(f, [(1, -25), (pull, -25), (pull + 4, 45)]))
        lv.keyframe_insert("rotation_euler", index=1, frame=f)
        nd.rotation_euler.x = R_(track(f, [(1, 70), (pull + 2, 70), (pull + 20, -70)]))
        nd.keyframe_insert("rotation_euler", index=0, frame=f)
    key_emission(SET["machine_dial_mat"], [(1, 2), (pull, 2), (pull + 20, 20)], 1, N)
    ml = SET["machine_light"]
    for f in range(1, N + 1):
        ml.data.energy = track(f, [(1, 20), (pull, 20), (pull + 20, 180)])
        ml.data.keyframe_insert("energy", frame=f)
    sprinkler_rain(1, 1, N, n=600)
    red_strobes(1, 1, N, period=18)
    camera({1: (6.3, 5.2, 0.7), N // 2: (5.75, 2.9, 0.95), N: (5.8, 2.15, 1.25)}, {1: 26, N: 28},
           lambda f: head_pos(j).lerp(Vector((6.8, 1.45, 1.1)), smoothstep(pull - 20, pull, f)), 1, N, focus=j["neck"], damp=0.25)


def _flash(t, N):
    vs = scene_view()
    for f in range(1, N + 1):
        vs.exposure = track(f, [(1, 0.35), (t - 1, 0.35), (t + 1, 5.0), (t + 5, 3.0), (t + 22, 0.35)])
        vs.keyframe_insert("exposure", frame=f)
    fl = point("reversal_flash", (MAT_C.x, MAT_C.y - 0.4, 1.4), 0, (1.0, 0.85, 0.6), 0.8)
    for f in range(1, N + 1):
        fl.data.energy = track(f, [(1, 0), (t - 1, 0), (t + 1, 3000), (t + 18, 0)])
        fl.data.keyframe_insert("energy", frame=f)


def scene_view():
    return bpy.context.scene.view_settings


def _sitting_quill(N, sit_keys, neck, eyes, arms, lids, smile, blinks, vanish_keys=None, amount_keys=None):
    q = _wet_quill(amount_keys, N) if amount_keys else lib.build_quill(undressed=True)
    x, y = MAT_C.x, MAT_C.y
    def feet(side, f):
        s = track(f, sit_keys)
        lx = 0.12 if side == "L" else -0.12
        fy = lerp(0.0, -0.75, s)
        return Vector((x + lx, y + fy, 0)), 0.0, R_(-60) * s
    stand(q, N, x, y, 0, feet=feet,
          body_extra=lambda f: (-0.78 * track(f, sit_keys), R_(-10) * track(f, sit_keys), 0),
          neck=neck, eyes=eyes, arms=arms, lids=lids, smile=smile, blinks=blinks)
    return q


def S22(N, P, E):
    """The reversal flash: he reappears mid-fall and collapses. The door swings open; Juno rushes in."""
    flash_t = P[0] + 10
    _flash(flash_t, N)
    collapse = (P[1] - 4, P[1] + 14)
    ev("flash_boom", flash_t)
    ev("collapse", collapse[1])
    q = _sitting_quill(N, [(1, 0.0), (collapse[0], 0.0), (collapse[1], 1.0)],
                       neck=lambda f: (R_(35) * smoothstep(*collapse, f), R_(10)), eyes=lambda f: (R_(15), 0),
                       arms=lambda f: ((R_(-15) * smoothstep(*collapse, f), R_(-25), 0), (R_(-15) * smoothstep(*collapse, f), R_(25), 0)),
                       lids=lambda f: lerp(1.0, 0.04, smoothstep(collapse[0], collapse[0] + 6, f)), smile=lambda f: 0.0, blinks=[])
    hidden = all_objs(q)
    key_hide(hidden, 1, True)
    key_hide(hidden, flash_t + 1, False)
    hinge = SET["door_hinge"]
    op = P[2] - 6
    ev("door_creak", op)
    for f in range(1, N + 1):
        hinge.rotation_euler.z = R_(-85) * smoothstep(op, op + 12, f)
        hinge.keyframe_insert("rotation_euler", index=2, frame=f)
    j = lib.build_juno()
    key_hide(j["clipboard"] + [j["mug"]], 1, True)
    kneel = P[3] - 4
    walk(j, N, [(1, (6.0, -1.6)), (op + 8, (6.0, -1.6)), (kneel, (1.25, 1.0))], [(1, -90), (op + 8, -90), (op + 18, -45), (kneel - 6, -55), (kneel, -60)],
         [(op + 8, kneel)], step=6, hw=0.09, lift=0.11,
         body_extra=lambda f: (-0.14 * smoothstep(kneel, kneel + 10, f), R_(18) * smoothstep(kneel, kneel + 10, f), 0),
         neck=lambda f: (R_(20) * smoothstep(kneel, kneel + 10, f), 0),
         arms=lambda f: ((R_(-55) * smoothstep(kneel, kneel + 10, f), R_(-10), 0), (R_(-55) * smoothstep(kneel, kneel + 10, f), R_(10), 0)),
         brows=lambda f: 1.0, mouth_open=lambda f: 0.4 * (1 - smoothstep(kneel, kneel + 20, f)), blinks=[kneel + 30])
    sprinkler_rain(1, 1, N)
    red_strobes(10 ** 6, 1, N)
    dim_lab([(1, 0.6), (N, 0.6)])
    camera({1: (0.65, -1.7, 2.0), N // 2: (0.85, -0.95, 1.5), N: (1.0, -0.3, 1.05)}, {1: 26, N: 28},
           lambda f: Vector((MAT_C.x + 0.2, MAT_C.y - 0.3, lerp(1.3, 0.55, smoothstep(collapse[0], collapse[1], f)))), 1, N,
           focus=q["neck"], damp=0.2)


def S23(N, P, E):
    """His eyes open. He can see. He looks down: his hands are back."""
    look_down = P[2]
    hands_up = (P[2] + 6, P[3] + 4)
    q = _sitting_quill(N, [(1, 1.0), (N, 1.0)],
                       neck=lambda f: (R_(track(f, [(1, 30), (P[0], 30), (P[1], 5), (look_down, 5), (look_down + 14, 32)])),
                                       R_(track(f, [(1, 10), (P[1], -18), (look_down, -18), (look_down + 10, 0)]))),
                       eyes=lambda f: (R_(track(f, [(1, 10), (P[1], -4), (look_down - 2, -4), (look_down + 6, 20)])),
                                       R_(track(f, [(1, 0), (P[1] - 4, -22), (look_down - 2, -22), (look_down + 6, 0)]))),
                       arms=lambda f: (arm_dir((-0.12, -0.75, 0.5), 0.5, 0.68, smoothstep(*hands_up, f)),
                                       arm_dir((0.12, -0.75, 0.5), 0.5, 0.68, smoothstep(*hands_up, f))),
                       lids=lambda f: track(f, [(1, 0.04), (P[0] + 6, 0.04), (E[0], 1.0)]),
                       smile=lambda f: smoothstep(P[3] + 6, P[3] + 16, f), blinks=[P[1] + 4],
                       amount_keys=None)
    j = lib.build_juno()
    key_hide(j["clipboard"] + [j["mug"]], 1, True)
    stand(j, N, 1.3, 1.6, -100, body_extra=lambda f: (-0.14, R_(18), 0),
          neck=lambda f: (R_(20), R_(-10)), eyes=lambda f: (R_(10), 0),
          arms=lambda f: ((R_(-55), R_(-10), 0), (R_(-55), R_(10), 0)), brows=lambda f: 1.0 - 0.6 * smoothstep(P[1], P[1] + 10, f),
          smile=lambda f: smoothstep(P[1] + 4, P[1] + 14, f), blinks=[30, 120])
    sprinkler_rain(1, 1, N, n=700, speed=0.2)
    dim_lab([(1, 0.6), (N, 0.6)])
    hand = lambda: q["hand_L"].matrix_world.translation
    camera({1: (0.15, 0.35, 1.0), N // 2: (0.25, 0.4, 0.95), N: (0.35, 0.45, 0.9)}, {1: 32, N: 30},
           lambda f: head_pos(q).lerp(hand(), 0.4 * smoothstep(hands_up[0], hands_up[1], f)), 1, N, focus=q["neck"], damp=0.2)


def S24(N, P, E):
    """Wide: the two of them on the wet floor, the sprinklers easing off, the Halo still glowing."""
    q = _sitting_quill(N, [(1, 1.0), (N, 1.0)],
                       neck=lambda f: (R_(5), R_(-25)), eyes=lambda f: (R_(-3), R_(-15)),
                       arms=lambda f: ((R_(-25), R_(-25), 0), (R_(-60), R_(10), 0)),
                       lids=lambda f: 1.0, smile=lambda f: 0.6 + 0.4 * smoothstep(P[2], P[2] + 20, f), blinks=[40, 140])
    j = lib.build_juno()
    key_hide(j["clipboard"] + [j["mug"]], 1, True)
    stand(j, N, 1.25, 1.0, -60, body_extra=lambda f: (-0.14, R_(10), 0), neck=lambda f: (R_(5), R_(-15)),
          arms=lambda f: ((R_(-40), R_(-10), 0), (R_(-70), R_(30), 0)), smile=lambda f: 1.0, brows=lambda f: 0.3,
          blinks=[70, 170])
    sheets = sprinkler_rain(1, 1, N, n=700, speed=0.2)
    off = P[2]
    ev("water_off", off)
    ev("sting", P[2] + 2)
    for s in sheets:
        key_hide([s], 1, False)
        key_hide([s], off, True)
    dim_lab([(1, 0.6), (N, 0.75)])
    mote(1, N, lambda f: (MAT_C.x, MAT_C.y, 0.6))
    key_area = area("key_warm", (2.5, -0.6, 2.0), (70, 0, 55), 140, 1.5, (1.0, 0.72, 0.45), hide_glossy=True)
    camera({1: (1.3, -0.35, 0.95), N // 2: (1.55, -1.25, 1.55), N: (1.75, -2.1, 2.25)}, {1: 28, N: 26},
           lambda f: Vector((0.85, 1.2, 0.6)).lerp(Vector((0.6, 2.4, 1.1)), smoothstep(P[1], N, f)), 1, N, focus=q["neck"], fstop=4, damp=0.15)


SHOTS = {k: v for k, v in globals().items() if len(k) == 3 and k.startswith("S") and k[1:].isdigit()}
