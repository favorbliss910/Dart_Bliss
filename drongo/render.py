"""2D renderer: layered parallax camera, depth-of-field, word-by-word captions.

python3 render.py OUT_DIR [--scale 0.5] [--fps 15] [--only i,j] [--stills]
"""
import argparse
import json
import math
import os
import random
import sys

import cairo
import numpy as np
from PIL import Image, ImageFilter

from chars import (C, INK, src, ellipse, stick, meerkat, meerkat_butt, drongo,
                   hawk, beetle, grub, scorpion, lizard, fill_stroke)
import env
from env import PALETTES, mix

W, H = 640, 1136
PI = math.pi


# ------------------------------------------------------------------ easing
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(u):
    u = clamp(u)
    return u * u * (3 - 2 * u)


def ease_io(u):
    u = clamp(u)
    return 4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2


def ease_out(u):
    u = clamp(u)
    return 1 - (1 - u) ** 3


def ease_in(u):
    u = clamp(u)
    return u ** 3


def back_out(u, k=1.8):
    u = clamp(u)
    return 1 + (k + 1) * (u - 1) ** 3 + k * (u - 1) ** 2


def lerp(a, b, t):
    return a + (b - a) * t


def seg(t, t0, t1):
    return clamp((t - t0) / max(1e-6, t1 - t0))


def blink_at(t, period=2.7, phase=0.0):
    k = (t + phase) % period
    return 1.0 if k < 0.09 else 0.0


# ------------------------------------------------------------------ camera
class Cam:
    def __init__(self, cx=0.0, cy=0.0, z=1.0, rot=0.0):
        self.cx, self.cy, self.z, self.rot = cx, cy, z, rot
        self.sx = self.sy = 0.0

    def shake(self, t, amp, freq=22.0, seed=1):
        if amp <= 0:
            return
        self.sx += amp * (math.sin(t * freq * 1.3 + seed) + 0.5 * math.sin(t * freq * 2.7 + seed * 3))
        self.sy += amp * (math.cos(t * freq * 1.1 + seed * 2) + 0.5 * math.sin(t * freq * 3.1 + seed))


def cam_path(u, keys, fn=ease_io):
    """keys: list of (u, cx, cy, z[, rot]); piecewise eased interpolation."""
    if u <= keys[0][0]:
        k = keys[0]
        return Cam(*k[1:])
    for a, b in zip(keys, keys[1:]):
        if u <= b[0]:
            v = fn((u - a[0]) / (b[0] - a[0]))
            vals = [lerp(x, y, v) for x, y in zip(a[1:], b[1:])]
            return Cam(*vals)
    return Cam(*keys[-1][1:])


# ------------------------------------------------------------------ frame
class Frame:
    def __init__(self, cam):
        self.cam = cam
        self.layers = []  # (surface, blur)

    def _surface(self, blur):
        if self.layers and self.layers[-1][1] == blur:
            return self.layers[-1][0]
        s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        self.layers.append((s, blur))
        return s

    def layer(self, p=1.0, blur=0.0, screen=False):
        s = self._surface(blur)
        ctx = cairo.Context(s)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        if screen:
            return ctx
        c = self.cam
        ctx.translate(W / 2, H / 2)
        ctx.rotate(c.rot)
        ctx.translate(c.sx, c.sy)
        ctx.translate(0, -c.cy * c.z)
        zp = 1 + (c.z - 1) * p if p < 1 else c.z * (1 + (p - 1) * 0.35)
        ctx.scale(zp, zp)
        ctx.translate(-c.cx * p, 0)
        return ctx

    def horizon_y(self):
        return H / 2 - self.cam.cy * self.cam.z

    def composite(self):
        out = np.zeros((H, W, 4), np.float32)
        for s, blur in self.layers:
            s.flush()
            a = np.ndarray((H, W, 4), np.uint8, s.get_data()).astype(np.float32)
            if blur > 0.3:
                im = Image.fromarray(a.astype(np.uint8), 'RGBA')  # premultiplied BGRA
                # blur each channel identically: premultiplied blur is correct
                chans = [c.filter(ImageFilter.GaussianBlur(blur)) for c in im.split()]
                a = np.dstack([np.asarray(c, np.float32) for c in chans])
            al = a[..., 3:4] / 255.0
            out = a + out * (1 - al)
        return out  # premultiplied BGRA float


# ------------------------------------------------------------------ scenery helpers
def desert(F, pal, sun_xy=(140, -330), sun_r=34, blur_far=0.0, blur_mid=0.0, ground_blur=0.0,
           trees_far=True, x0=-2600, x1=2600, clouds=True, seed=0):
    c = F.layer(p=0.0, blur=0, screen=True)
    hy = F.horizon_y()
    env.sky(c, W, H, hy, pal)
    c = F.layer(p=0.06, blur=blur_far)
    env.sun(c, sun_xy[0], sun_xy[1], sun_r, pal)
    if clouds:
        env.cloud(c, -260, -520, 1.1, 0.55)
        env.cloud(c, 180, -700, 0.8, 0.45)
        env.cloud(c, 420, -430, 0.7, 0.4)
    c = F.layer(p=0.2, blur=blur_far)
    env.dune_band(c, x0, x1, 6, env.hills(seed + 11, 22, 20, 90), mix(pal['far'], pal['haze'], 0.35), pal['far'])
    if trees_far:
        rnd = random.Random(seed + 4)
        for i in range(10):
            env.acacia_far(c, rnd.uniform(x0 / 2, x1 / 2), rnd.uniform(-10, 4), rnd.uniform(0.4, 0.8),
                           mix(pal['tree_sh'], pal['far'], 0.55))
    c = F.layer(p=0.45, blur=blur_mid)
    env.dune_band(c, x0, x1, 10, env.hills(seed + 5, 18, 0, 48), pal['mid'], mix(pal['mid'], pal['near'], 0.6))
    c = F.layer(p=1.0, blur=ground_blur)
    env.ground(c, x0 * 2, x1 * 2, pal, seed=seed + 7)
    return c


def acacia_with_perch(ctx, x, y, s, pal, seed=2):
    """Acacia plus a bare dead branch reaching left: the drongo's lookout."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for w, col in ((15, INK), (8, C('#6a4a34'))):
        ctx.move_to(-6, -96)
        ctx.curve_to(-80, -120, -160, -128, -250, -122)
        ctx.set_line_width(w)
        src(ctx, col)
        ctx.stroke()
        ctx.move_to(-150, -126)
        ctx.curve_to(-170, -150, -175, -160, -186, -176)
        ctx.set_line_width(w * 0.7)
        src(ctx, col)
        ctx.stroke()
    ctx.restore()
    env.acacia(ctx, x, y, s, pal, seed=seed)


PERCH = (-212, -124)  # local perch point on acacia_with_perch (s=1)


def perch_world(x, y, s):
    return x + PERCH[0] * s, y + PERCH[1] * s


def vignette(F, strength=0.32):
    c = F.layer(screen=True)
    g = cairo.RadialGradient(W / 2, H * 0.48, W * 0.35, W / 2, H * 0.48, H * 0.75)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0.12, 0.05, 0.02, strength)
    c.rectangle(0, 0, W, H)
    c.set_source(g)
    c.paint()


# ================================================================== SHOTS
# Each shot: fn(F_factory, t, d) -> Frame.  t local seconds, d shot duration.

def s01_vista(t, d):
    pal = PALETTES['dawn']
    u = t / d
    tx, ty, ts = 150, 70, 1.15
    px, py = perch_world(tx, ty, ts)
    cam = cam_path(u, [(0, 0, -560, 0.85), (0.35, 20, -300, 0.95), (1, px + 30, py - 40, 1.9)])
    F = Frame(cam)
    c = desert(F, pal, sun_xy=(-120, -260 + 60 * u), sun_r=40)
    env.grass(c, -240, 140, 1.4, seed=1, sway=math.sin(t * 2))
    env.grass(c, 330, 220, 1.6, seed=2, sway=math.sin(t * 2 + 1))
    acacia_with_perch(c, tx, ty, ts, pal)
    drongo(c, px, py, 0.42, look=(0.5, 0.1), blink=blink_at(t, 2.1))
    # birds drifting in the dawn sky
    c2 = F.layer(p=0.3)
    for i in range(3):
        bx = -300 + i * 60 + t * 40
        by = -520 - i * 30
        c2.move_to(bx - 10, by)
        c2.curve_to(bx - 5, by - 6, bx - 2, by - 6, bx, by)
        c2.curve_to(bx + 2, by - 6, bx + 5, by - 6, bx + 10, by)
        c2.set_line_width(2.5)
        src(c2, C('#5a3d3a', 0.7))
        c2.stroke()
    return F


def s02_drongo_idle(t, d):
    pal = PALETTES['dawn']
    tx, ty, ts = 150, 70, 1.15
    px, py = perch_world(tx, ty, ts)
    u = t / d
    cam = cam_path(u, [(0, px + 10, py - 60, 4.2), (1, px + 4, py - 58, 4.7)], ease)
    F = Frame(cam)
    c = desert(F, pal, sun_xy=(-120, -200), sun_r=40, blur_far=7, blur_mid=6, ground_blur=6)
    c = F.layer(p=1.0, blur=0)
    acacia_with_perch(c, tx, ty, ts, pal)
    # smug little head bob + tilt; slow side-eye toward camera
    tilt = 0.18 * math.sin(t * 3.1) if t < 0.6 else 0.22
    look = (0.6, 0.1) if t < 0.55 else (-0.2, 0.35)
    drongo(c, px, py, 0.42, look=look, tilt=tilt, blink=blink_at(t, 1.6, 0.9), lid=0.25 if t > 0.55 else 0)
    vignette(F)
    return F


def s03_scream(t, d):
    pal = PALETTES['dawn']
    tx, ty, ts = 150, 70, 1.15
    px, py = perch_world(tx, ty, ts)
    hx, hy = px + 0.42 * 12, py - 0.42 * 92
    pop = back_out(seg(t, 0, 0.18))
    z = lerp(6.0, 8.2, pop)
    cam = Cam(hx + 8, hy + 10, z, -0.06)
    cam.shake(t, 9 * (1 - seg(t, 0.2, d)) + 3)
    F = Frame(cam)
    desert(F, pal, sun_xy=(-120, -200), sun_r=40, blur_far=12, blur_mid=12, ground_blur=12)
    c = F.layer(p=1.0, blur=8)
    acacia_with_perch(c, tx, ty, ts, pal)
    c = F.layer(screen=True)
    env.speed_lines(c, W / 2, H * 0.47, t, n=26, r0=250, r1=760, seed=3, col=(1, 0.97, 0.88, 0.75))
    c = F.layer(p=1.0, blur=0)
    beak = clamp(back_out(seg(t, 0.02, 0.14)), 0, 1.2)
    drongo(c, px, py, 0.42, beak=beak, look=(0.9, -0.1), tilt=-0.25, puff=1, brow='angry', eye_scale=1.1)
    bx, by = px + 0.42 * 56, py - 0.42 * 88
    env.sound_rings(c, bx, by, t, n=3, r=6, gap=6, ang=-0.3, spread=1.4, lw=2.0)
    vignette(F, 0.4)
    return F


def s04_drop_lunch(t, d):
    pal = PALETTES['dawn']
    u = t / d
    cam = cam_path(u, [(0, 0, -60, 1.75), (1, 0, -50, 1.95)], ease)
    jolt = seg(t, 0.12, 0.22)
    cam.shake(t, 6 * (1 - seg(t, 0.2, 0.7)) * (t > 0.12))
    F = Frame(cam)
    c = desert(F, pal, sun_xy=(-200, -230), sun_r=36, blur_far=6, blur_mid=4, ground_blur=2)
    env.grass(c, -200, 160, 1.2, seed=5)
    startled = t > 0.15
    sq = -0.12 * math.sin(seg(t, 0.15, 0.4) * PI) if startled else 0.02 * math.sin(t * 9)
    # meerkat A: grub
    fall = ease_in(seg(t, 0.25, 0.95))
    gx, gy = lerp(-70, -96, fall), lerp(78, 200, fall)
    if not startled:
        hold = lambda k: grub(k, 0, 0, 0.55, rot=0.1, wiggle=t * 8)
        meerkat(c, -80, 200, 0.95, mouth='chew' if int(t * 8) % 2 else 'smile', arms='hold', hold=hold,
                look=(0.2, 0.4), lid=0.35, squash=sq)
    else:
        meerkat(c, -80, 200, 0.95, mouth='o', arms='up', eyes='wide', look=(0.6, -0.8), squash=sq, brow='raised')
        grub(c, gx, gy, 0.55, rot=fall * 4, wiggle=t * 10)
    # meerkat B: beetle (which scurries away happily)
    if not startled:
        hold = lambda k: beetle(k, 0, 0, 0.5, rot=PI, look=(0, -1), worried=True)
        meerkat(c, 120, 230, 0.95, mouth='grin', arms='hold', hold=hold, look=(-0.3, 0.5), lid=0.3,
                squash=sq, flip=True)
    else:
        meerkat(c, 120, 230, 0.95, mouth='scream', arms='up', eyes='wide', look=(-0.5, -0.8), squash=sq,
                flip=True, brow='worried')
        f2 = ease_in(seg(t, 0.25, 0.8))
        bx = 120 + 0 * f2
        by = lerp(124, 232, f2)
        if t < 0.8:
            beetle(c, bx, by, 0.5, rot=PI * (1 - f2), look=(0, 1))
        else:
            run = (t - 0.8) * 260
            beetle(c, 140 + run, 236, 0.5, rot=PI / 2, look=(1, 0), legs=t * 40)
    if startled:
        cc = F.layer(screen=True)
        for k, (x, y) in enumerate(((140, 400), (510, 430))):
            a = back_out(seg(t, 0.15 + k * 0.05, 0.3 + k * 0.05))
            cc.save()
            cc.translate(x, y)
            cc.scale(a, a)
            cc.select_font_face('Poppins', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            cc.set_font_size(140)
            cc.text_path('!')
            src(cc, (1, 0.85, 0.2))
            cc.fill_preserve()
            cc.set_line_width(7)
            src(cc, INK)
            cc.stroke()
            cc.restore()
    vignette(F)
    return F


def popup_meerkat(c, pal, hx, hy, s, rise, **kw):
    """Meerkat rising out of a hole at (hx, hy). rise 0..1."""
    up = back_out(rise, 1.4)
    c.save()
    # clip to above the hole lip so the body appears from inside
    c.rectangle(hx - 400 * s, hy - 900 * s, 800 * s, 900 * s + 6 * s)
    c.clip()
    meerkat(c, hx, hy + lerp(240, 30, up) * s, s, squash=-0.12 * math.sin(clamp(rise) * PI), **kw)
    c.restore()


def s05_meet(t, d):
    pal = PALETTES['day']
    u = t / d
    cam = cam_path(u, [(0, 0, 110, 2.7), (1, 0, 70, 2.05)], ease_out)
    F = Frame(cam)
    c = desert(F, pal, sun_xy=(220, -420), sun_r=34, blur_far=3, blur_mid=2)
    env.acacia(c, -330, 30, 0.8, pal, seed=4)
    env.grass(c, 260, 130, 1.3, seed=8)
    holes = [(-112, 168), (-36, 196), (44, 186), (118, 166)]
    order = [1, 2, 0, 3]
    faces = [dict(mouth='smile', tilt=0.15, look=(0.2, 0.2)),
             dict(mouth='grin', tilt=-0.1, look=(0, 0.2)),
             dict(mouth='o', tilt=0.2, look=(0.4, 0), eyes='wide'),
             dict(mouth='smile', tilt=-0.2, look=(-0.3, 0.2), lid=0.3)]
    for i, (hx, hy) in sorted(enumerate(holes), key=lambda e: e[1][1]):
        env.burrow(c, hx, hy, 0.62, pal)
        k = order.index(i)
        r = seg(t, 0.05 + k * 0.17, 0.35 + k * 0.17)
        if r > 0:
            popup_meerkat(c, pal, hx, hy, 0.62, r, blink=blink_at(t, 2.0, i * 0.7), **faces[i])
            env.dust(c, hx, hy, seg(t, 0.05 + k * 0.17, 0.6 + k * 0.17), 0.6, seed=i)
        env.burrow_front(c, hx, hy, 0.62, pal)
    vignette(F)
    return F


def sun_arc(u):
    a = lerp(PI * 0.92, PI * 0.08, u)
    return 520 * math.cos(a), -150 - 420 * math.sin(a)


def s06_all_day(t, d):
    u = t / d
    # time-lapse: dawn -> noon -> dusk while they dig
    p0, p1 = PALETTES['dawn'], PALETTES['day']
    w = math.sin(u * PI)
    pal = {k: mix(p0[k], p1[k], w) for k in p0}
    cam = cam_path(u, [(0, -110, 40, 1.65), (1, 110, 40, 1.75)], lambda v: v)
    F = Frame(cam)
    c = desert(F, pal, sun_xy=sun_arc(u), sun_r=34, clouds=False)
    env.acacia(c, 420, 40, 0.9, pal, seed=7)
    for i, x in enumerate((-300, -110, 80, 270)):
        y = 200 + (i % 2) * 22
        env.burrow(c, x - 46, y + 4, 0.3, pal)
        meerkat_butt(c, x, y, 0.9, wiggle=t * 9 + i, flip=i % 2 == 1)
        env.sand_spray(c, x + (-30 if i % 2 == 0 else 30), y - 30, t + i * 0.3, 0.9, seed=i,
                       dirx=-1 if i % 2 == 0 else 1)
    env.grass(c, -40, 300, 1.5, seed=9)
    # little clock-wipe sun trail
    c = F.layer(screen=True)
    vignette(F)
    return F


def s07_beetle(t, d):
    pal = PALETTES['day']
    u = t / d
    cam = cam_path(u, [(0, 0, 120, 2.2), (1, 10, 110, 2.6)], ease)
    F = Frame(cam)
    desert(F, pal, blur_far=8, blur_mid=8, ground_blur=3, clouds=False)
    c = F.layer(p=1.0)
    # meerkat looming in from the left, grinning down at it
    meerkat(c, -60, 345, 1.0, mouth='grin', look=(0.8, 0.7), tilt=0.3, arms='dig', lid=0.25, brow='raised')
    env.sand_spray(c, 40, 180, t, 0.6, seed=4, dirx=1, n=12)
    beetle(c, 70, 180 - 10 * ease_out(seg(t, 0, 0.3)), 0.75, look=(-0.6, -0.5), worried=True, legs=t * 30)
    vignette(F)
    return F


def s08_scorpion(t, d):
    pal = PALETTES['day']
    pop = back_out(seg(t, 0, 0.2))
    cam = Cam(0, 70, lerp(2.4, 2.8, pop), 0.12)
    F = Frame(cam)
    desert(F, pal, blur_far=9, blur_mid=8, ground_blur=4, clouds=False)
    c = F.layer(p=1.0)
    scorpion(c, 10, 140, 1.15, tail=math.sin(t * 6), claws=t * 14, look=(-0.4, -0.6))
    meerkat(c, 210, 330, 1.0, mouth='grin', look=(-0.8, 0.4), flip=True, arms='dig', tilt=-0.2, brow='angry')
    vignette(F)
    return F


def s09_lizard(t, d):
    pal = PALETTES['day']
    u = t / d
    cam = cam_path(u, [(0, 0, 100, 2.0), (1, 10, 110, 2.6)], ease_io)
    F = Frame(cam)
    desert(F, pal, blur_far=8, blur_mid=8, ground_blur=2, clouds=False)
    c = F.layer(p=1.0)
    # the growing shadow of a meerkat
    sh = ease_io(seg(t, 0.2, 2.0))
    env.ellipse(c, 10, 168, 60 + 160 * sh, 16 + 30 * sh)
    src(c, (0.25, 0.12, 0.05, 0.35 * sh))
    c.fill()
    lizard(c, -10, 150, 1.05, look=(0.3 * math.sin(t * 3), -0.7), sweat=t, tail=t * 4, blink=blink_at(t, 1.8))
    # meerkat face enters from the top on "unlucky"
    e = ease_out(seg(t, 1.55, 2.0))
    if e > 0:
        meerkat(c, 40, lerp(-260, 70, e), 1.05, mouth='grin', look=(-0.2, 0.9), tilt=0.15, lid=0.3,
                arms='up', brow='raised')
    vignette(F)
    return F


def s10_head_in_hole(t, d):
    pal = PALETTES['day']
    # head in a hole... then tilt up to the sky it cannot see
    tilt_u = seg(t, 1.6, d)
    cam = cam_path(tilt_u, [(0, 30, 120, 2.0), (1, 30, -760, 1.2)], ease_io)
    cam.cx += lerp(0, -20, seg(t, 0, 1.6))
    F = Frame(cam)
    c = desert(F, pal, sun_xy=(260, -720), sun_r=34)
    env.burrow(c, -16, 200, 0.4, pal)
    meerkat_butt(c, 20, 200, 1.0, wiggle=t * 8)
    env.sand_spray(c, -20, 190, t, 0.8, seed=11, dirx=-1)
    # a hawk circling high above
    c = F.layer(p=0.35)
    ang = t * 0.9
    hawk(c, 60 + 140 * math.cos(ang), -900 + 40 * math.sin(ang), 0.45, flap=t * 6, rot=ang + PI / 2)
    vignette(F)
    return F


def s11_hawks(t, d):
    pal = PALETTES['day']
    cam = Cam(0, -1200, 1.0, 0.1 * t)
    F = Frame(cam)
    c = F.layer(screen=True)
    g = cairo.RadialGradient(W * 0.7, H * 0.2, 20, W / 2, H / 2, H)
    g.add_color_stop_rgb(0, 1, 0.98, 0.9)
    g.add_color_stop_rgb(0.3, *pal['sky0'])
    g.add_color_stop_rgb(1, *pal['sky_top'])
    c.rectangle(0, 0, W, H)
    c.set_source(g)
    c.fill()
    # hawks circle the frame, at three depths
    c = F.layer(screen=True)
    c.translate(W / 2, H / 2)
    c.rotate(0.25 * t)
    specs = [(0.0, 300, 0.55, 0), (2.1, 260, 0.75, 1), (4.2, 330, 0.65, 2), (1.0, 120, 1.1, 3)]
    for ph, rad, s, i in specs:
        a = ph + t * 0.8 * (1 if i % 2 == 0 else -1)
        x, y = rad * math.cos(a), rad * math.sin(a) * 1.25
        e = back_out(seg(t, i * 0.12, 0.35 + i * 0.12))
        hawk(c, x, y, s * e, flap=t * 7 + i, rot=a + (PI / 2 if i % 2 == 0 else -PI / 2), menace=1.2)
    vignette(F, 0.45)
    return F


def s12_guard(t, d):
    pal = PALETTES['day']
    u = t / d
    cam = cam_path(u, [(0, 0, -150, 1.2), (1, 0, -190, 1.6)], ease_io)
    F = Frame(cam)
    c = desert(F, pal, sun_xy=(-240, -520), blur_far=3, blur_mid=2)
    # the gang digging in the background
    for i, x in enumerate((-260, -150, 230)):
        meerkat_butt(c, x, 60, 0.45, wiggle=t * 9 + i, flip=i == 2)
    env.termite_mound(c, 0, 180, 1.0, pal)
    look = (math.sin(t * 2.2) * 0.9, -0.2)
    meerkat(c, 0, 0, 1.05, look=look, turn=look[0] * 0.6, arms='tucked', mouth='flat', brow='angry',
            blink=blink_at(t, 1.9, 0.4))
    env.grass(c, -230, 250, 1.6, seed=3, sway=math.sin(t * 3))
    env.grass(c, 250, 280, 1.8, seed=4, sway=math.sin(t * 3 + 1))
    vignette(F)
    return F


def s13_spots(t, d):
    pal = PALETTES['day']
    zoom = back_out(seg(t, 0.85, 1.05))
    cam = Cam(0, -185, lerp(3.4, 4.6, zoom) + 0.2 * t, 0)
    if t > 0.85:
        cam.shake(t, 5 * (1 - seg(t, 0.9, 1.4)))
    F = Frame(cam)
    desert(F, pal, sun_xy=(-240, -520), blur_far=10, blur_mid=10, ground_blur=8)
    c = F.layer(p=1.0)
    spotted = t > 0.85
    look = (math.sin(t * 3.0) * 0.8, -0.2) if not spotted else (0.55, -0.85)
    meerkat(c, 0, 0, 1.05, look=look, eyes='wide' if spotted else 'normal', mouth='o' if spotted else 'flat',
            brow='raised' if spotted else 'angry', blink=0, turn=look[0] * 0.5)
    vignette(F, 0.4)
    return F


def s14_bark(t, d):
    pal = PALETTES['day']
    pop = back_out(seg(t, 0, 0.15))
    cam = Cam(0, -150, lerp(2.4, 2.8, pop), -0.05)
    cam.shake(t, 10 * (1 - seg(t, 0.1, d)) + 2)
    F = Frame(cam)
    desert(F, pal, sun_xy=(-240, -520), blur_far=8, blur_mid=8, ground_blur=6)
    c = F.layer(screen=True)
    env.speed_lines(c, W / 2, H * 0.36, t, n=30, r0=230, r1=760, seed=8, col=(1, 1, 1, 0.7))
    c = F.layer(p=1.0)
    env.termite_mound(c, 0, 180, 1.0, pal)
    meerkat(c, 0, 0, 1.05, mouth='bark', eyes='wide', arms='up', look=(0.4, -0.6), brow='angry',
            squash=-0.06 * math.sin(t * 30))
    env.sound_rings(c, 0, -150, t, n=3, r=80, gap=40, ang=-PI / 2, spread=2.4, lw=7)
    vignette(F, 0.4)
    return F


def s15_dive(t, d):
    pal = PALETTES['day']
    u = t / d
    cam = cam_path(u, [(0, 0, 80, 2.05), (1, 0, 100, 2.3)], ease_out)
    F = Frame(cam)
    c = desert(F, pal, sun_xy=(220, -420), sun_r=34)
    env.acacia(c, -330, 30, 0.8, pal, seed=4)
    holes = [(-112, 168), (-36, 196), (44, 186), (118, 166)]
    for i, (hx, hy) in sorted(enumerate(holes), key=lambda e: e[1][1]):
        env.burrow(c, hx, hy, 0.62, pal)
        t0 = 0.1 + i * 0.16
        k = seg(t, t0, t0 + 0.28)
        if k < 1:
            c.save()
            c.rectangle(hx - 300, hy - 600, 600, 606)
            c.clip()
            jump = math.sin(min(k, 0.4) / 0.4 * PI / 2) * 40 * (1 - k)
            meerkat(c, hx, hy + 30 * 0.62 - jump + ease_in(k) * 260 * 0.62, 0.62, mouth='scream', eyes='wide',
                    arms='up', look=(0, -0.9), squash=-0.25 * k, brow='worried')
            c.restore()
        env.dust(c, hx, hy, seg(t, t0 + 0.2, t0 + 0.9), 0.7, seed=i + 3)
        env.burrow_front(c, hx, hy, 0.62, pal)
    # hawk shadow sweeps across the empty ground
    sx = lerp(-900, 900, seg(t, 1.2, d))
    c.save()
    c.translate(sx, 230)
    c.scale(1, 0.32)
    hawk(c, 0, 0, 0.9, flap=1.0, rot=PI / 2, silhouette=True)
    c.restore()
    vignette(F)
    return F


# shot list: (first word index, fn)
SHOTS = [
    (0, s01_vista), (9, s02_drongo_idle), (12, s03_scream), (15, s04_drop_lunch),
    (21, s05_meet), (24, s06_all_day), (34, s07_beetle), (37, s08_scorpion),
    (38, s09_lizard), (44, s10_head_in_hole), (57, s11_hawks), (64, s12_guard),
    (70, s13_spots), (76, s14_bark), (80, s15_dive),
]


# ------------------------------------------------------------------ captions
def caption(ctx, word, age):
    a = back_out(clamp(age / 0.09), 2.4)
    s = lerp(0.82, 1.0, a)
    ctx.save()
    ctx.select_font_face('Poppins', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    fs = 50
    ctx.set_font_size(fs)
    ext = ctx.text_extents(word)
    ctx.translate(W / 2, H * 0.705)
    ctx.scale(s, s)
    x = -ext.x_advance / 2
    y = fs * 0.35
    # soft drop shadow
    ctx.move_to(x + 2, y + 4)
    ctx.text_path(word)
    ctx.set_source_rgba(0, 0, 0, 0.35)
    ctx.set_line_width(12)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.stroke()
    ctx.new_path()
    ctx.move_to(x, y)
    ctx.text_path(word)
    ctx.set_source_rgb(0, 0, 0)
    ctx.set_line_width(9)
    ctx.stroke_preserve()
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill()
    ctx.restore()


def word_at(words, T):
    cur = None
    for i, w in enumerate(words):
        if w['t0'] <= T:
            cur = i
    if cur is None:
        return None, 0
    w = words[cur]
    nxt = words[cur + 1]['t0'] if cur + 1 < len(words) else w['t0'] + 0.8
    if T > min(nxt, w['t0'] + 0.9):
        return None, 0
    return w['w'], T - w['t0']


# ------------------------------------------------------------------ main
def shot_bounds(words, total):
    starts = [0.0 if wi == 0 else words[wi]['t0'] - 0.06 for wi, _ in SHOTS]
    ends = starts[1:] + [total]
    return list(zip(starts, ends))


def render_frame(T, words, bounds):
    for (t0, t1), (_, fn) in zip(bounds, SHOTS):
        if t0 <= T < t1 or (fn is SHOTS[-1][1] and T >= t0):
            F = fn(T - t0, t1 - t0)
            break
    img = F.composite()
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    buf = np.ndarray((H, W, 4), np.uint8, s.get_data())
    buf[:] = np.clip(img, 0, 255).astype(np.uint8)
    s.mark_dirty()
    ctx = cairo.Context(s)
    wd, age = word_at(words, T)
    if wd:
        caption(ctx, wd, age)
    s.flush()
    arr = np.ndarray((H, W, 4), np.uint8, s.get_data())
    return arr[..., [2, 1, 0]].copy()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('--fps', type=float, default=15)
    ap.add_argument('--times', default='')
    ap.add_argument('--start', type=int, default=0)
    ap.add_argument('--step', type=int, default=1)
    ap.add_argument('--size', default='320x568')
    a = ap.parse_args()
    meta = json.load(open(os.path.join(os.path.dirname(__file__), 'words.json')))
    words, total = meta['words'], meta['duration']
    bounds = shot_bounds(words, total)
    os.makedirs(a.out, exist_ok=True)
    ow, oh = map(int, a.size.split('x'))
    if a.times:
        for T in map(float, a.times.split(',')):
            Image.fromarray(render_frame(T, words, bounds)).resize((ow, oh), Image.LANCZOS).save(
                os.path.join(a.out, f't{T:06.2f}.png'))
        return
    n = int(math.ceil(total * a.fps))
    for i in range(a.start, n, a.step):
        T = i / a.fps
        Image.fromarray(render_frame(T, words, bounds)).resize((ow, oh), Image.LANCZOS).save(
            os.path.join(a.out, f'f{i:05d}.png'))


if __name__ == '__main__':
    main()
