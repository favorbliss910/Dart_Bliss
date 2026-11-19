"""The Blank Library: environments, post-process looks and the 20 shots.

    python3 scenes.py OUT_DIR --fps 30 --ss 2.25 --size 1440x2560 [--times ...]
"""
import math
import os
import random
import sys

import cairo
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'drongo'))

import render as R  # noqa: E402  (engine: Frame, Cam, cam_path, easing, captions)
from render import (Frame, Cam, cam_path, ease, ease_io, ease_out, ease_in, back_out, seg, clamp, lerp,  # noqa: E402
                    blink_at, W, H)
from chars import C, INK, src, ellipse, stick, fill_stroke, soft_ellipse, form_shade, rim, clipped, grad_fill  # noqa: E402
from env import mix as cmix  # noqa: E402
from people import person, librarian, book_open, book_closed, car, cctv, lamp  # noqa: E402

PI = math.pi

# ============================================================== palettes
NIGHT = dict(top=C('#070d24'), mid=C('#16305a'), hor=C('#3f6f86'), mount=C('#1b2b47'), mount2=C('#2b4466'),
             snow=C('#e3edf6'), snow_sh=C('#9fb4cc'), wall=C('#2b2f3a'), wall_hi=C('#454b5c'))
INT = dict(wall=C('#2e211a'), wall2=C('#3d2b20'), wood=C('#5a3b26'), wood_dk=C('#2f1d12'), floor=C('#3a2618'),
           light=C('#ffd98a'))
SPINES = [C('#7a2e2e'), C('#2e4a6b'), C('#4a6b3a'), C('#8a6a2e'), C('#5b2b6b'), C('#2b5b5b'), C('#6b4a2e'), C('#3b3b5b')]


# ============================================================== environment pieces
def night_sky(F, aur=1.0, t=0.0, stars=True):
    c = F.layer(screen=True)
    hy = F.horizon_y()
    g = cairo.LinearGradient(0, hy - 1400, 0, hy)
    g.add_color_stop_rgb(0, *NIGHT['top'])
    g.add_color_stop_rgb(0.6, *NIGHT['mid'])
    g.add_color_stop_rgb(1, *NIGHT['hor'])
    c.rectangle(0, 0, W, H)
    c.set_source(g)
    c.fill()
    c = F.layer(p=0.05)
    if stars:
        rnd = random.Random(3)
        for i in range(140):
            x, y = rnd.uniform(-900, 900), rnd.uniform(-1500, -120)
            r = rnd.uniform(0.6, 2.0)
            tw = 0.6 + 0.4 * math.sin(t * rnd.uniform(1, 3) + i)
            ellipse(c, x, y, r, r)
            src(c, (1, 1, 1, 0.75 * tw))
            c.fill()
    if aur > 0:  # aurora: translucent wavy curtains
        for k, (col, yb, amp) in enumerate(((C('#5dffb0'), -620, 60), (C('#42d6c9'), -760, 80), (C('#9b7bff'), -880, 50))):
            for j in range(26):
                x = -700 + j * 56
                y0 = yb + amp * math.sin(j * 0.45 + t * 0.6 + k)
                c.move_to(x, y0)
                c.line_to(x, y0 - 260 - 60 * math.sin(j * 0.8 + t + k))
                g = cairo.LinearGradient(0, y0, 0, y0 - 300)
                g.add_color_stop_rgba(0, *col, 0.0)
                g.add_color_stop_rgba(0.15, *col, 0.22 * aur)
                g.add_color_stop_rgba(1, *col, 0)
                c.set_source(g)
                c.set_line_width(58)
                c.stroke()


def mountains(F, blur=0.0):
    c = F.layer(p=0.2, blur=blur)
    for (base, col, seed, hmin, hmax) in ((0, NIGHT['mount2'], 1, 220, 420), (8, NIGHT['mount'], 2, 120, 300)):
        rnd = random.Random(seed)
        xs = list(range(-1600, 1700, 160))
        pts = [(x, base - rnd.uniform(hmin, hmax)) for x in xs]
        c.move_to(-1600, base + 600)
        for (x, y) in pts:
            c.line_to(x, y)
        c.line_to(1700, base + 600)
        c.close_path()
        g = cairo.LinearGradient(0, base - hmax, 0, base + 40)
        g.add_color_stop_rgb(0, *cmix(col, (1, 1, 1), 0.15))
        g.add_color_stop_rgb(1, *col)
        c.set_source(g)
        c.fill()
        # snow caps
        for (x, y) in pts:
            if y < base - hmin * 1.1:
                c.move_to(x - 60, y + 50)
                c.line_to(x, y)
                c.line_to(x + 60, y + 50)
                c.curve_to(x + 30, y + 40, x - 20, y + 60, x - 60, y + 50)
                src(c, (0.85, 0.92, 1, 0.75))
                c.fill()


def snow_ground(F, blur=0.0):
    c = F.layer(p=1.0, blur=blur)
    g = cairo.LinearGradient(0, 0, 0, 900)
    g.add_color_stop_rgb(0, *NIGHT['snow_sh'])
    g.add_color_stop_rgb(0.25, *NIGHT['snow'])
    g.add_color_stop_rgb(1, *cmix(NIGHT['snow'], NIGHT['snow_sh'], 0.4))
    c.rectangle(-4000, -2, 8000, 4000)
    c.set_source(g)
    c.fill()
    rnd = random.Random(5)
    for i in range(60):
        y = 10 + (i / 60) ** 1.5 * 800
        x = rnd.uniform(-1500, 1500)
        w = lerp(40, 260, y / 800)
        c.move_to(x - w, y)
        c.curve_to(x - w * 0.3, y - 8, x + w * 0.3, y - 8, x + w, y)
        c.set_line_width(lerp(1, 4, y / 800))
        src(c, (*NIGHT['snow_sh'], 0.5))
        c.stroke()
    return c


def snowfall(F, t, n=120, seed=0, blur=0.0, speed=1.0, size=1.0):
    c = F.layer(screen=True, blur=blur)
    rnd = random.Random(seed)
    for i in range(n):
        x0 = rnd.uniform(-60, W + 60)
        sp = rnd.uniform(40, 110) * speed
        y = (rnd.uniform(0, H) + t * sp) % (H + 40) - 20
        x = x0 + 18 * math.sin(t * rnd.uniform(0.5, 1.5) + i)
        r = rnd.uniform(1.2, 3.8) * size
        ellipse(c, x, y, r, r)
        src(c, (1, 1, 1, rnd.uniform(0.5, 0.95)))
        c.fill()


def building(c, x, y, s=1.0, door_glow=1.0, t=0.0):
    """Windowless slate monolith with one glowing door. Origin bottom-centre."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    soft_ellipse(c, 0, 4, 330, 30, C('#1a2433'), 0.55)

    def mass():
        c.move_to(-200, 0)
        c.line_to(-200, -560)
        c.line_to(-150, -610)
        c.line_to(160, -610)
        c.line_to(200, -560)
        c.line_to(200, 0)
        c.close_path()
    form_shade(c, mass, NIGHT['wall'], NIGHT['wall_hi'], C('#151820'), (-200, -610, 200, 0))
    # stone courses
    for i in range(1, 14):
        stick(c, [(-196, -i * 44), (196, -i * 44)], 1.4, (1, 1, 1, 0.05))
    # snow on roof ledge
    c.move_to(-206, -560)
    c.line_to(-150, -616)
    c.line_to(160, -616)
    c.line_to(206, -560)
    c.curve_to(150, -580, 60, -566, 0, -578)
    c.curve_to(-60, -566, -150, -580, -206, -560)
    fill_stroke(c, NIGHT['snow'], 3.5)
    rim(c, mass, C('#8fb6ff'), -4, 3, 5, 0.35)
    mass()
    c.set_line_width(5)
    src(c, INK)
    c.stroke()
    # door + light spill
    if door_glow > 0:
        soft_ellipse(c, 0, 10, 220, 60, C('#ffcf7a'), 0.45 * door_glow)
        soft_ellipse(c, 0, -80, 110, 120, C('#ffcf7a'), 0.25 * door_glow)
    c.rectangle(-46, -150, 92, 150)
    g = cairo.LinearGradient(0, -150, 0, 0)
    g.add_color_stop_rgb(0, *cmix(C('#ffd98a'), C('#ff9a3c'), 0.2))
    g.add_color_stop_rgb(1, *C('#ffefc2'))
    c.set_source(g)
    c.fill_preserve()
    c.set_line_width(5)
    src(c, INK)
    c.stroke()
    c.restore()


def interior(F, blur=0.0, light=1.0):
    c = F.layer(p=0.4, blur=blur)
    g = cairo.LinearGradient(0, -1200, 0, 200)
    g.add_color_stop_rgb(0, *C('#150e0a'))
    g.add_color_stop_rgb(1, *INT['wall'])
    c.rectangle(-3000, -3000, 6000, 3200)
    c.set_source(g)
    c.fill()
    for i in range(-6, 7):  # panelling
        stick(c, [(i * 160, -2000), (i * 160, 200)], 3, (0, 0, 0, 0.25))
    return c


def floor(F, blur=0.0, y0=0):
    c = F.layer(p=1.0, blur=blur)
    g = cairo.LinearGradient(0, y0, 0, y0 + 900)
    g.add_color_stop_rgb(0, *C('#2a1a10'))
    g.add_color_stop_rgb(1, *INT['floor'])
    c.rectangle(-3000, y0, 6000, 3000)
    c.set_source(g)
    c.fill()
    for i in range(30):
        yy = y0 + 10 + (i / 30) ** 1.4 * 900
        stick(c, [(-3000, yy), (3000, yy)], lerp(1, 3, i / 30), (0, 0, 0, 0.25))
    return c


def bookshelf(c, x, y, w=360, h=760, seed=0, pulled=None, lit=0.6):
    """Tall shelf, origin bottom-left. pulled=(row, idx, amount) slides a book out."""
    rnd = random.Random(seed)
    c.save()
    c.translate(x, y)
    rows = 6
    rh = h / rows
    c.rectangle(0, -h - 20, w, h + 20)
    form_shade(c, lambda: c.rectangle(0, -h - 20, w, h + 20), INT['wood'], cmix(INT['wood'], (1, 0.9, 0.7), 0.25),
               INT['wood_dk'], (0, -h - 20, w, 0))
    c.rectangle(0, -h - 20, w, h + 20)
    c.set_line_width(5)
    src(c, INK)
    c.stroke()
    for r in range(rows):
        top = -h + r * rh
        c.rectangle(14, top, w - 28, rh - 16)
        src(c, C('#1a100a'))
        c.fill()
        xx = 18
        k = 0
        while xx < w - 34:
            bw = rnd.uniform(16, 30)
            bh = rnd.uniform(rh * 0.62, rh * 0.86)
            col = rnd.choice(SPINES)
            dx = 0
            if pulled and pulled[0] == r and pulled[1] == k:
                dx = pulled[2]
            if rnd.random() < 0.08:
                # leaning book
                c.save()
                c.translate(xx, top + rh - 16)
                c.rotate(-0.25)
                c.rectangle(0, -bh, bw, bh)
                fill_stroke(c, col, 2.5)
                c.restore()
            else:
                c.rectangle(xx, top + rh - 16 - bh + dx * 0.0, bw, bh)
                if dx:
                    c.save()
                    c.translate(0, 0)
                    c.restore()
                fill_stroke(c, col, 2.5)
                stick(c, [(xx + 4, top + rh - 16 - bh * 0.8), (xx + bw - 4, top + rh - 16 - bh * 0.8)], 1.6,
                      C('#d6b25a', 0.8))
            xx += bw + 1.5
            k += 1
        c.rectangle(6, top + rh - 16, w - 12, 14)
        fill_stroke(c, INT['wood'], 3)
        soft_ellipse(c, w / 2, top + 12, w * 0.45, 18, INK, 0.5)
    soft_ellipse(c, w * 0.3, -h * 0.6, w * 0.6, h * 0.5, INT['light'], 0.08 * lit)
    c.restore()


def table(c, x, y, w=520, lit=True):
    """Reading table, top surface at y."""
    c.save()
    c.translate(x, y)
    if lit:
        soft_ellipse(c, 0, -10, w * 0.75, 260, INT['light'], 0.18)
    c.rectangle(-w / 2, 0, w, 26)
    form_shade(c, lambda: c.rectangle(-w / 2, 0, w, 26), INT['wood'], cmix(INT['wood'], (1, 0.85, 0.6), 0.35),
               INT['wood_dk'], (-w / 2, 0, w / 2, 26))
    c.rectangle(-w / 2, 0, w, 26)
    c.set_line_width(5)
    src(c, INK)
    c.stroke()
    for lx in (-w / 2 + 30, w / 2 - 30):
        c.rectangle(lx - 10, 26, 20, 240)
        fill_stroke(c, INT['wood_dk'], 4.5)
    c.restore()


def lamp_light(c, x, y, r=320, k=1.0):
    soft_ellipse(c, x, y, r, r * 0.8, INT['light'], 0.28 * k, core=0.3)


def dust(F, t, n=40, seed=1, area=(0, 0, W, H)):
    c = F.layer(screen=True)
    rnd = random.Random(seed)
    for i in range(n):
        x = area[0] + (rnd.uniform(0, area[2]) + 8 * math.sin(t * 0.7 + i)) % area[2]
        y = area[1] + (rnd.uniform(0, area[3]) - t * rnd.uniform(4, 14)) % area[3]
        r = rnd.uniform(1, 2.6)
        soft_ellipse(c, x, y, r * 2, r * 2, (1, 0.95, 0.8), 0.5 * (0.5 + 0.5 * math.sin(t * 2 + i)))


def grade(F, tint=(0.0, 0.0, 0.0, 0.0), vig=0.45, warm_glow=None):
    c = F.layer(screen=True)
    if warm_glow:
        x, y, r, a = warm_glow
        soft_ellipse(c, x, y, r, r, INT['light'], a)
    if tint[3] > 0:
        c.rectangle(0, 0, W, H)
        src(c, tint)
        c.fill()
    g = cairo.RadialGradient(W / 2, H * 0.47, W * 0.28, W / 2, H * 0.47, H * 0.72)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0.02, 0.02, 0.05, vig)
    c.rectangle(0, 0, W, H)
    c.set_source(g)
    c.paint()


def speech_bubble(c, x, y, k, dots=True):
    if k <= 0:
        return
    c.save()
    c.translate(x, y)
    c.scale(k, k)
    c.move_to(-90, -40)
    c.curve_to(-90, -100, 90, -100, 90, -40)
    c.curve_to(90, 10, 10, 10, -10, 8)
    c.line_to(-50, 40)
    c.line_to(-40, 4)
    c.curve_to(-90, 0, -90, -20, -90, -40)
    fill_stroke(c, (1, 1, 1), 5)
    if dots:
        for i in (-1, 0, 1):
            ellipse(c, i * 26, -44, 7, 7)
            src(c, INK)
            c.fill()
    c.restore()


# ============================================================== post looks
def to_rgb(img):
    return img[..., [2, 1, 0]]


def from_rgb(img, rgb):
    img[..., 0], img[..., 1], img[..., 2] = rgb[..., 2], rgb[..., 1], rgb[..., 0]
    return img


def cctv_post(stamp_fn, cam_name='CAM 02', glitch=0.0):
    def post(img, T):
        rgb = to_rgb(img)
        lum = rgb @ np.array([0.3, 0.59, 0.11], np.float32)
        lum = np.clip(lum * 1.55 + 28, 0, 255)
        out = np.stack([lum * 0.78, lum * 0.98, lum * 0.82], -1)
        h, w = lum.shape
        out *= (0.86 + 0.14 * (np.arange(h) % max(2, int(4 * R.SS)) < max(1, int(2 * R.SS))))[:, None, None]  # scanlines
        rng = np.random.default_rng(int(T * 30))
        out += rng.normal(0, 9, (h // 3 + 1, w // 3 + 1)).repeat(3, 0).repeat(3, 1)[:h, :w, None]
        yy, xx = np.mgrid[0:h, 0:w]
        d = ((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2
        out *= (1 - 0.45 * np.clip(d, 0, 1.4))[..., None]
        g = glitch(T) if callable(glitch) else glitch
        if g > 0:  # horizontal tear bands
            for k in range(int(3 + 6 * g)):
                y0 = rng.integers(0, h - 20)
                hh = rng.integers(4, int(40 * R.SS))
                sh = int(rng.integers(-60, 60) * g * R.SS)
                out[y0:y0 + hh] = np.roll(out[y0:y0 + hh], sh, axis=1) * (1 + 0.4 * g)
        img = from_rgb(img, np.clip(out, 0, 255))
        # overlay text via cairo on the array
        s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        buf = np.ndarray((h, w, 4), np.uint8, s.get_data())
        buf[:] = np.clip(img, 0, 255).astype(np.uint8)
        s.mark_dirty()
        c = cairo.Context(s)
        c.scale(R.SS, R.SS)
        c.select_font_face('DejaVu Sans Mono', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        c.set_font_size(30)
        src(c, (0.92, 1, 0.92))
        c.move_to(40, 90)
        c.show_text(cam_name)
        c.move_to(40, H - 300)
        c.show_text(stamp_fn(T))
        if int(T * 2) % 2 == 0:
            ellipse(c, W - 140, 80, 11, 11)
            src(c, (1, 0.2, 0.2))
            c.fill()
        src(c, (0.92, 1, 0.92))
        c.move_to(W - 120, 90)
        c.show_text('REC')
        # corner brackets
        for (x, y, dx, dy) in ((30, 30, 1, 1), (W - 30, 30, -1, 1), (30, H - 30, 1, -1), (W - 30, H - 30, -1, -1)):
            stick(c, [(x, y + dy * 60), (x, y), (x + dx * 60, y)], 4, (0.92, 1, 0.92))
        s.flush()
        return np.ndarray((h, w, 4), np.uint8, s.get_data()).astype(np.float32)
    return post


def flashback_post(red_keep=0.0, page=True):
    """Blue-night duotone storybook look; red_keep isolates the red car colour."""
    def post(img, T):
        rgb = to_rgb(img) / 255.0
        lum = rgb @ np.array([0.3, 0.59, 0.11], np.float32)
        duo = np.stack([0.10 + lum * 0.70, 0.14 + lum * 0.78, 0.26 + lum * 0.80], -1)
        if red_keep > 0:
            r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
            m = np.clip((r - np.maximum(g, b) - 0.18) * 4, 0, 1)[..., None] * red_keep
            duo = duo * (1 - m) + rgb * m
        h, w = lum.shape
        yy, xx = np.mgrid[0:h, 0:w]
        d = ((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2
        duo *= (1 - 0.5 * np.clip(d, 0, 1.3))[..., None]
        return from_rgb(img, np.clip(duo * 255, 0, 255))
    return post


# ============================================================== shots
def s01_exterior(t, d):
    u = t / d
    cam = cam_path(u, [(0, 0, -760, 0.95), (1, 0, -180, 1.25)], ease_io)
    F = Frame(cam)
    night_sky(F, 1.0, t)
    mountains(F)
    snow_ground(F)
    c = F.layer(p=1.0)
    building(c, 0, 120, 0.9, t=t)
    # tiny queue at the door
    for i in range(7):
        person(c, 70 + i * 34, 140 + i * 6, 0.22, body=SPINES[i % 8], hat='beanie' if i % 2 else None,
               look=(-0.8, 0), shadow=False)
    snowfall(F, t, 120, seed=1)
    grade(F, vig=0.5)
    return F


def s02_blank_book(t, d):
    u = t / d
    cam = Cam(0, -40, lerp(1.05, 1.22, ease(u)), lerp(-0.06, 0.02, ease(u)))
    F = Frame(cam)
    c = F.layer(screen=True)
    src(c, C('#2a1a10'))
    c.paint()
    c = F.layer(p=1.0)
    c.rectangle(-900, -900, 1800, 1800)
    g = cairo.LinearGradient(-600, -600, 600, 600)
    g.add_color_stop_rgb(0, *C('#6a4430'))
    g.add_color_stop_rgb(1, *C('#3a2416'))
    c.set_source(g)
    c.fill()
    for i in range(-8, 9):
        stick(c, [(-900, i * 110), (900, i * 110 + 20)], 2, (0, 0, 0, 0.18))
    lamp_light(c, -80, -120, 520, 1.3)
    book_open(c, 0, 20, 1.15, flip=clamp(u * 1.4 - 0.2), seed=2)
    dust(F, t, 50, 2)
    grade(F, vig=0.55)
    return F


def s03_queue(t, d):
    u = t / d
    cam = cam_path(u, [(0, -360, -60, 1.55), (1, 260, -60, 1.6)], lambda v: v)
    F = Frame(cam)
    night_sky(F, 0.6, t)
    mountains(F, blur=3)
    snow_ground(F)
    c = F.layer(p=1.0)
    building(c, 640, 150, 0.95)
    snowpile = ease(seg(u, 0.1, 1.0))
    cols = [C('#3f7fc8'), C('#c0453c'), C('#5a8a4a'), C('#8a6a2e'), C('#7b5cc4'), C('#2b5b5b'), C('#b0563a'), C('#4a4a6b')]
    for i in range(9):
        x = 420 - i * 110
        y = 190 + (i % 2) * 14
        person(c, x, y, 0.62, body=cols[i % 8], hat='beanie' if i % 3 == 0 else None,
               scarf=C('#e0b84a') if i % 3 == 1 else None, hair='short' if i % 2 else 'messy',
               look=(0.9, 0.1), mouth='flat' if i != 4 else 'frown', blink=blink_at(t, 2.4, i * 0.37),
               beard=snowpile * (1.0 if i == 5 else 0.0), lid=0.3 if i == 5 else 0, arms='down')
        # snow piling on heads
        hx, hy = x, y - 0.62 * (92 + 104 + 92)
        ellipse(c, hx, hy + 6, 32 * snowpile + 4, 10 * snowpile + 2)
        src(c, (1, 1, 1, 0.95))
        c.fill()
    # calendar pages flying away = years passing
    cc = F.layer(screen=True)
    for k in range(6):
        p = seg(u, 0.1 + k * 0.13, 0.45 + k * 0.13)
        if 0 < p < 1:
            cx = lerp(W * 0.55, W * 1.2, ease_in(p)) - k * 10
            cy = lerp(H * 0.25, H * 0.05, p) + 30 * math.sin(p * 6)
            cc.save()
            cc.translate(cx, cy)
            cc.rotate(p * 3 + k)
            cc.rectangle(-46, -54, 92, 108)
            fill_stroke(cc, (1, 1, 1), 4)
            cc.rectangle(-46, -54, 92, 26)
            fill_stroke(cc, C('#d6332f'), 4)
            cc.select_font_face('Poppins', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            cc.set_font_size(40)
            src(cc, INK)
            cc.move_to(-24, 40)
            cc.show_text(str(2019 + k)[-2:])
            cc.restore()
    snowfall(F, t, 90, seed=3, speed=1.6)
    grade(F, vig=0.45)
    return F


def s04_facade(t, d):
    u = t / d
    cam = cam_path(u, [(0, 0, 40, 1.9), (1, 0, -400, 1.6)], ease_io)
    F = Frame(cam)
    night_sky(F, 0.8, t)
    snow_ground(F)
    c = F.layer(p=1.0)
    building(c, 0, 160, 1.15)
    # "no windows": ghost window outlines flash, then crumble away
    k = seg(t, 0.75, 1.0) - seg(t, 1.25, 1.5)
    if k > 0:
        for (wx, wy) in ((-120, -420), (60, -420), (-120, -620), (60, -620)):
            c.save()
            c.set_dash([14, 10])
            c.rectangle(wx, wy, 64, 90)
            c.set_line_width(5)
            src(c, (1, 1, 1, 0.8 * k))
            c.stroke()
            c.restore()
            stick(c, [(wx, wy), (wx + 64, wy + 90)], 6, (1, 0.35, 0.35, k))
            stick(c, [(wx + 64, wy), (wx, wy + 90)], 6, (1, 0.35, 0.35, k))
    # "no signs": an empty plaque that pops in blank
    k2 = back_out(seg(t, 1.45, 1.7))
    if k2 > 0:
        c.save()
        c.translate(0, -250 + 160)
        c.scale(k2, k2)
        c.rectangle(-120, -50, 240, 70)
        fill_stroke(c, C('#c9c3b5'), 5)
        c.select_font_face('Poppins', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        c.set_font_size(54)
        src(c, (0.3, 0.3, 0.3, 0.8))
        c.move_to(-16, 4)
        c.show_text('?')
        c.restore()
    snowfall(F, t, 120, seed=4)
    grade(F, vig=0.5)
    return F


def s05_librarian(t, d):
    u = t / d
    cam = cam_path(u, [(0, 0, -150, 1.9), (1, 0, -170, 2.25)], ease_io)
    F = Frame(cam)
    interior(F, blur=6)
    c = F.layer(p=0.6, blur=4)
    for i in range(-3, 4):
        bookshelf(c, i * 380 - 190, 120, 360, 760, seed=10 + i)
    floor(F, y0=120)
    c = F.layer(p=1.0)
    lamp_light(c, 120, -120, 300, 1.0)
    librarian(c, 0, 120, 1.0, look=(0, 0.15), blink=blink_at(t, 1.9, 0.6), lid=0.5)
    # desk in front
    c.rectangle(-260, -40, 520, 300)
    form_shade(c, lambda: c.rectangle(-260, -40, 520, 300), INT['wood'], cmix(INT['wood'], (1, 0.85, 0.6), 0.3),
               INT['wood_dk'], (-260, -40, 260, 260))
    c.rectangle(-260, -40, 520, 300)
    c.set_line_width(5)
    src(c, INK)
    c.stroke()
    lamp(c, 170, -40, 1.0)
    book_closed(c, -120, -56, 0.4, C('#2e4a6b'))
    # "never speaks": empty bubble pops up, then deflates
    k = back_out(seg(t, 1.05, 1.25)) * (1 - seg(t, 1.6, 1.8))
    speech_bubble(c, 120, -390, k)
    grade(F, vig=0.6, warm_glow=(W * 0.62, H * 0.45, 260, 0.12))
    return F


def s06_shelves(t, d):
    u = t / d
    cam = cam_path(u, [(0, 0, -100, 1.1), (1, 0, -130, 1.28)], ease_io)
    F = Frame(cam)
    interior(F)
    c = F.layer(p=0.7, blur=3)
    for i in range(-2, 3):
        bookshelf(c, i * 380 - 180, 60, 360, 820, seed=20 + i)
    floor(F, y0=60)
    c = F.layer(p=1.0)
    bookshelf(c, -560, 160, 300, 1000, seed=31)
    bookshelf(c, 260, 160, 300, 1000, seed=32)
    person(c, 0, 200, 0.95, body=C('#7b5cc4'), hair='short', look=(0.2, -0.9), mouth='o', arms='down',
           blink=blink_at(t, 2.0))
    dust(F, t, 30, 6)
    grade(F, vig=0.55, warm_glow=(W * 0.5, H * 0.2, 300, 0.12))
    return F


def s07_pick_book(t, d):
    u = t / d
    cam = Cam(0, -360, lerp(2.4, 2.65, ease(u)))
    F = Frame(cam)
    interior(F)
    c = F.layer(p=1.0)
    bookshelf(c, -260, 120, 520, 900, seed=41)
    # the chosen book slides out
    k = ease_out(seg(t, 0.1, 0.55))
    bx, by = 10, -470
    c.save()
    c.translate(bx, by)
    c.rotate(-0.3 * k)
    c.translate(0, -60 * k)
    c.rectangle(-16, -120, 34, 124)
    form_shade(c, lambda: c.rectangle(-16, -120, 34, 124), C('#5b2b6b'), C('#8a4aa0'), C('#2f1238'), (-16, -120, 18, 4))
    c.rectangle(-16, -120, 34, 124)
    c.set_line_width(4)
    src(c, INK)
    c.stroke()
    stick(c, [(-10, -96), (12, -96)], 2, C('#d6b25a'))
    c.restore()
    # stick arm + hand reaching in
    stick(c, [(260, -300), (120, -420), (bx + 14, by - 60 * k - 70)], 6)
    ellipse(c, bx + 14, by - 60 * k - 70, 8, 8)
    src(c, INK)
    c.fill()
    soft_ellipse(c, bx, by - 60, 140, 140, INT['light'], 0.25)
    grade(F, vig=0.55)
    return F


def s08_read_nothing(t, d):
    u = t / d
    cam = cam_path(u, [(0, 0, -170, 1.7), (1, 0, -150, 2.05)], ease_io)
    F = Frame(cam)
    interior(F, blur=6)
    c = F.layer(p=0.6, blur=5)
    for i in range(-3, 4):
        bookshelf(c, i * 380 - 190, 120, 360, 760, seed=50 + i)
    floor(F, y0=120, blur=3)
    c = F.layer(p=1.0)
    lamp_light(c, 0, -120, 360, 1.3)
    person(c, -20, -20, 0.95, body=C('#c0623c'), sit=True, arms='read', look=(0.1, 0.9) if t < 1.0 else (0.6, -0.3),
           mouth='flat' if t < 0.9 else 'frown', brows='worried' if t > 0.9 else None, blink=blink_at(t, 1.7))
    table(c, 0, 20, 560)
    lamp(c, 200, 20, 0.9)
    book_open(c, -20, -6, 0.42, flip=seg(t, 0.4, 0.9), seed=8)
    # "nothing": a tiny question mark puffs up
    k = back_out(seg(t, 1.0, 1.2))
    if k > 0:
        c.save()
        c.translate(60, -420)
        c.scale(k, k)
        c.select_font_face('Poppins', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        c.set_font_size(90)
        c.text_path('?')
        src(c, (1, 1, 1))
        c.fill_preserve()
        c.set_line_width(5)
        src(c, INK)
        c.stroke()
        c.restore()
    grade(F, vig=0.6)
    return F


def s09_strange(t, d):
    u = t / d
    cam = cam_path(u, [(0, 0, -160, 1.3), (1, 110, -230, 1.9)], ease_io)
    F = Frame(cam)
    interior(F, blur=4)
    floor(F, y0=120, blur=3)
    c = F.layer(p=0.8, blur=2.5)
    lamp_light(c, 150, -150, 260, 0.9)
    librarian(c, 150, 60, 0.85, look=(-0.2 + 0.5 * ease(seg(u, 0.3, 0.8)), 0.2), lid=0.35, tilt=-0.1 * ease(seg(u, 0.3, 0.8)))
    c = F.layer(p=1.0, blur=0)
    lamp_light(c, -120, -60, 300, 1.2)
    person(c, -130, 40, 0.95, body=C('#c0623c'), sit=True, arms='read', look=(0.1, 0.8), mouth='flat')
    table(c, -110, 80, 480)
    book_open(c, -130, 64, 0.42, seed=8)
    grade(F, vig=0.65, tint=(0.05, 0.08, 0.2, 0.15))
    return F


def s10_walk_out(t, d):
    u = t / d
    cam = cam_path(u, [(0, 0, -60, 1.9), (1, 0, -90, 1.45)], ease_out)
    F = Frame(cam)
    night_sky(F, 1.0, t)
    snow_ground(F)
    c = F.layer(p=1.0)
    building(c, 0, 80, 1.2)
    cols = [C('#3f7fc8'), C('#5a8a4a'), C('#b0563a')]
    for i, (dx, delay) in enumerate(((-120, 0.0), (10, 0.35), (130, 0.15))):
        k = ease_out(seg(t, delay, delay + 1.4))
        y = lerp(80, 240, k)
        x = dx * lerp(0.3, 1, k)
        sc = lerp(0.45, 0.8, k)
        person(c, x, y, sc, body=cols[i], look=(0, -0.3), eyes='wide', mouth='o' if i != 1 else 'smile',
               arms='hug', step=t * 8 + i, brows='raised',
               hold=lambda cc, bh: book_closed(cc, 0, -bh * 0.62, 0.14, SPINES[i + 2]))
        # glowing story-words floating up
        for j in range(4):
            p = (t * 0.6 + j / 4 + i * 0.3) % 1
            c.save()
            c.translate(x + 30 * math.sin(j + t), y - sc * 330 - p * 160)
            soft_ellipse(c, 0, 0, 30, 10, C('#ffe39a'), 0.6 * (1 - p))
            stick(c, [(-18, 0), (18, 0)], 3, (1, 0.9, 0.6, 1 - p))
            c.restore()
    snowfall(F, t, 100, seed=7)
    grade(F, vig=0.45)
    return F


def house_sketch(c):
    c.save()
    c.translate(130, 20)
    stick(c, [(-40, 0), (-40, -40), (0, -70), (40, -40), (40, 0), (-40, 0)], 2.6, C('#3b2a5a'))
    c.rectangle(-10, -24, 18, 24)
    c.set_line_width(2.4)
    src(c, C('#3b2a5a'))
    c.stroke()
    c.restore()


def s11_their_story(t, d):
    u = t / d
    cam = Cam(20, -40, lerp(1.25, 1.55, ease(u)), 0.03)
    F = Frame(cam)
    c = F.layer(screen=True)
    src(c, C('#20140c'))
    c.paint()
    c = F.layer(p=1.0)
    lamp_light(c, 0, -60, 560, 1.4)
    book_open(c, 0, 20, 1.1, text=ease(seg(u, 0.0, 0.85)), glow=0.6 + 0.3 * math.sin(t * 3), seed=11,
              drawing=house_sketch if u > 0.55 else None)
    dust(F, t, 40, 4)
    grade(F, vig=0.55)
    return F


def s12_crying(t, d):
    u = t / d
    cam = cam_path(u, [(0, 0, -60, 1.6), (1, 0, -100, 2.0)], ease_io)
    F = Frame(cam)
    night_sky(F, 0.5, t)
    snow_ground(F, blur=2)
    c = F.layer(p=0.9, blur=3)
    building(c, 0, 40, 1.4)
    c = F.layer(p=1.0)
    person(c, 0, 160, 0.95, body=C('#4a6b8a'), hair='side', tears=0.6 + 0.4 * math.sin(t * 4) ** 2, mouth='wobble',
           brows='worried', arms='hug', step=t * 5, hold=lambda cc, bh: book_closed(cc, 0, -bh * 0.62, 0.16, C('#7a2e2e')))
    snowfall(F, t, 110, seed=8, speed=0.8)
    grade(F, vig=0.55, tint=(0.05, 0.1, 0.25, 0.15))
    return F


def rain(F, t, n=140, seed=9):
    c = F.layer(screen=True)
    rnd = random.Random(seed)
    for i in range(n):
        x = (rnd.uniform(0, W + 200) - t * 160) % (W + 200) - 100
        y = (rnd.uniform(0, H) + t * rnd.uniform(900, 1400)) % (H + 80) - 40
        stick(c, [(x, y), (x - 8, y + 34)], 1.6, (0.85, 0.9, 1, 0.45))


def night_street(F, t, blur=0.0):
    c = F.layer(screen=True)
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, *C('#0b1020'))
    g.add_color_stop_rgb(1, *C('#232a3a'))
    c.rectangle(0, 0, W, H)
    c.set_source(g)
    c.fill()
    c = F.layer(p=0.5, blur=4)
    rnd = random.Random(4)
    for i in range(-6, 7):  # town silhouettes with lit windows
        hgt = rnd.uniform(180, 380)
        c.rectangle(i * 150 - 70, -hgt, 140, hgt + 20)
        src(c, C('#151a28'))
        c.fill()
        for k in range(4):
            if rnd.random() < 0.5:
                c.rectangle(i * 150 - 50 + (k % 2) * 60, -hgt + 30 + (k // 2) * 60, 26, 30)
                src(c, (1, 0.85, 0.5, 0.7))
                c.fill()
    c = F.layer(p=1.0, blur=blur)
    c.rectangle(-3000, 0, 6000, 3000)
    g = cairo.LinearGradient(0, 0, 0, 600)
    g.add_color_stop_rgb(0, *C('#2b3040'))
    g.add_color_stop_rgb(1, *C('#11141c'))
    c.set_source(g)
    c.fill()
    for i in range(-10, 11):  # wet road reflections
        stick(c, [(i * 120, 120), (i * 120 + 70, 120)], 6, (1, 1, 1, 0.25))
    return c


def streetlamp(c, x, y, s=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    stick(c, [(0, 0), (0, -420), (60, -440)], 10)
    soft_ellipse(c, 70, -300, 220, 320, C('#ffd98a'), 0.25)
    soft_ellipse(c, 70, 10, 200, 40, C('#ffd98a'), 0.35)
    ellipse(c, 70, -440, 26, 14)
    fill_stroke(c, C('#fff1c0'), 4)
    c.restore()


def s13_flashback(t, d):
    u = t / d
    cam = cam_path(u, [(0, 0, -160, 1.25), (1, 60, -180, 1.5)], ease_io)
    F = Frame(cam)
    night_street(F, t)
    c = F.layer(p=1.0)
    streetlamp(c, -60, 100, 1.0)
    car(c, 170, 110, 0.85, lights=True)
    # the father walks toward the car... and fades
    walk = ease_io(seg(u, 0.0, 0.9))
    ghost = seg(u, 0.55, 1.0)
    if ghost < 1:
        c.push_group()
        person(c, lerp(-200, 40, walk), 100, 0.8, body=C('#4a4a5a'), hair='short', hat=None, look=(1, 0),
               step=t * 6, arms='down', beard=0.3)
        c.pop_group_to_source()
        c.paint_with_alpha(1 - ghost)
    rain(F, t)
    F.post = flashback_post(0.0)
    return F


def s14_car_colour(t, d):
    u = t / d
    cam = Cam(170, 30, lerp(2.2, 2.6, ease(u)), 0.02)
    F = Frame(cam)
    night_street(F, t, blur=2)
    c = F.layer(p=1.0)
    streetlamp(c, -60, 100, 1.0)
    car(c, 170, 110, 0.85, lights=True)
    rain(F, t, 100, 11)
    F.post = flashback_post(red_keep=ease(seg(t, 0.35, 0.7)))
    return F


def s15_hide_camera(t, d):
    u = t / d
    cam = cam_path(u, [(0, 0, -230, 1.4), (1, 0, -250, 1.55)], ease_io)
    F = Frame(cam)
    interior(F)
    floor(F, y0=120)
    c = F.layer(p=1.0)
    bookshelf(c, -360, 120, 720, 540, seed=61)
    k = ease_out(seg(t, 0.2, 0.8))
    cctv(c, lerp(330, 130, k), -440, 0.8, rec=(t > 0.9 and int(t * 4) % 2 == 0))
    person(c, -120, 160, 0.95, coat=C('#f4f4f2'), glasses=True, hair='side', hair_col=C('#2a2a2a'),
           arms='shh', look=(0.6, -0.1), mouth='flat', brows='raised', step=0)
    person(c, 120, 160, 0.95, coat=C('#f4f4f2'), glasses=True, hair='messy', hair_col=C('#6a4a2a'),
           arms='up', look=(0.4, -0.9), mouth='grin', blink=blink_at(t, 2.0))
    grade(F, vig=0.55, warm_glow=(W * 0.5, H * 0.3, 300, 0.1))
    return F


def reading_room(c, t, readers=3, jitter=0.0, ghosts=0.0, whisper=0.0):
    """High-angle CCTV-ish view of three reading tables."""
    rnd = random.Random(int(t * 3) if jitter else 1)
    for i in range(readers):
        x = -230 + i * 230
        y = -40 + (i % 2) * 140
        lamp_light(c, x, y - 60, 200, 1.6)
        if ghosts > 0:
            c.push_group()
            librarian(c, x + 70, y - 20, 0.62, arms='whisper', lean=-0.35, tilt=-0.35, look=(-0.6, 0.6), lid=0.6)
            c.pop_group_to_source()
            c.paint_with_alpha(ghosts)
        jx = rnd.uniform(-8, 8) * jitter
        person(c, x + jx, y - 60, 0.6, body=SPINES[i + 1], sit=True, arms='read', look=(0, 0.9),
               hair=('short', 'messy', 'side')[i])
        table(c, x, y - 40, 200, lit=False)
        book_open(c, x, y - 50, 0.25, seed=i)
        if whisper > 0:
            for k in range(3):
                p = (t * 1.5 + k / 3) % 1
                c.new_path()
                c.arc(x + 30, y - 210, 10 + 22 * p, -0.6, 0.6)
                c.set_line_width(3)
                src(c, (1, 1, 1, whisper * (1 - p)))
                c.stroke()


def stamp(start_s, end_s, t0, d):
    def f(T):
        u = clamp((T - t0) / d)
        s = int(lerp(start_s, end_s, u ** 1.2))
        return f'{s // 3600:02d}:{(s // 60) % 60:02d}:{s % 60:02d}'
    return f


def s16_cctv_hours(t, d, T0=None):
    cam = Cam(0, -80, lerp(1.2, 1.3, t / d))
    F = Frame(cam)
    interior(F)
    floor(F, y0=-300)
    c = F.layer(p=1.0)
    reading_room(c, t, jitter=1.0)
    F.post = cctv_post(stamp(0, 3 * 3600, SHOT_T0['s16'], d))
    return F


def s17_monitor(t, d):
    u = t / d
    cam = cam_path(u, [(0, 0, -200, 1.4), (1, 0, -260, 2.1)], ease_in)
    F = Frame(cam)
    c = F.layer(screen=True)
    src(c, C('#06080d'))
    c.paint()
    c = F.layer(p=1.0)
    # monitor
    soft_ellipse(c, 0, -300, 420, 300, C('#7fd6ff'), 0.3)
    c.rectangle(-230, -460, 460, 320)
    fill_stroke(c, C('#202329'), 8)
    c.rectangle(-206, -438, 412, 276)
    rnd = random.Random(int(t * 30))
    g = cairo.LinearGradient(0, -438, 0, -162)
    g.add_color_stop_rgb(0, *C('#5f8f7a'))
    g.add_color_stop_rgb(1, *C('#2d4a3e'))
    c.set_source(g)
    c.fill()
    for k in range(40):  # static / rewind streaks
        y = -438 + rnd.uniform(0, 276)
        stick(c, [(-200, y), (200, y)], rnd.uniform(1, 4), (1, 1, 1, rnd.uniform(0.05, 0.3)))
    stick(c, [(0, -140), (0, -90)], 12)
    # scientists, backs to us, lit by the screen
    for i, x in enumerate((-150, 150)):
        person(c, x, 260, 1.05, coat=C('#f4f4f2'), hair=('side', 'messy')[i], hair_col=(C('#2a2a2a'), C('#6a4a2a'))[i],
               look=(0, -1), shadow=False)
    grade(F, vig=0.7, tint=(0.0, 0.08, 0.18, 0.2))
    return F


def s18_reveal(t, d):
    u = t / d
    cam = cam_path(u, [(0, 0, -80, 1.3), (0.75, 70, -160, 1.9), (1, 80, -180, 2.6)], ease_io)
    F = Frame(cam)
    interior(F)
    floor(F, y0=-300)
    c = F.layer(p=1.0)
    reading_room(c, t, ghosts=ease(seg(t, 0.1, 0.5)), whisper=seg(t, 1.6, 2.0))
    T0 = SHOT_T0['s18']
    F.post = cctv_post(lambda T: '01:47:' + f'{int((T - T0) * 30) % 60:02d}', 'CAM 02 ◀◀ PLAYBACK',
                       glitch=lambda T: 1.0 if (T - T0) < 0.15 or 0.95 < (T - T0) < 1.05 else 0.15)
    return F


def s19_be_honest(t, d):
    u = t / d
    cam = Cam(0, -190, lerp(2.6, 2.9, ease(u)))
    F = Frame(cam)
    interior(F, blur=8)
    c = F.layer(p=1.0)
    lamp_light(c, 0, -300, 300, 1.2)
    librarian(c, 0, 120, 1.0, look=(0, 0), lid=0.25, arms='shh', blink=0)
    grade(F, vig=0.75, tint=(0.04, 0.06, 0.16, 0.2))
    return F


def s20_open_book(t, d):
    u = t / d
    cam = cam_path(u, [(0, 0, -90, 1.05), (1, 0, -110, 1.3)], ease_io)
    F = Frame(cam)
    c = F.layer(screen=True)
    src(c, C('#120b07'))
    c.paint()
    c = F.layer(p=1.0)
    c.rectangle(-900, -40, 1800, 900)
    g = cairo.LinearGradient(0, -40, 0, 600)
    g.add_color_stop_rgb(0, *C('#5a3a26'))
    g.add_color_stop_rgb(1, *C('#24160d'))
    c.set_source(g)
    c.fill()
    ok = 0.95 * ease_io(seg(t, 0.15, 1.5))
    book_closed(c, 0, 40, 1.15, C('#5b2b6b'), open_k=ok, glow=ok)
    if ok > 0:
        for j in range(12):  # light motes rising from the pages
            p = (t * 0.5 + j / 12) % 1
            soft_ellipse(c, -150 + j * 27, 20 - p * 380, 6, 6, C('#ffe39a'), 0.8 * ok * (1 - p))
    dust(F, t, 30, 9)
    grade(F, vig=0.7)
    return F


# shot list: (first word index, fn)
SHOTS = [
    (0, s01_exterior), (5, s02_blank_book), (10, s03_queue), (17, s04_facade), (24, s05_librarian),
    (31, s06_shelves), (35, s07_pick_book), (39, s08_read_nothing), (46, s09_strange), (51, s10_walk_out),
    (62, s11_their_story), (72, s12_crying), (76, s13_flashback), (85, s14_car_colour), (92, s15_hide_camera),
    (97, s16_cctv_hours), (105, s17_monitor), (111, s18_reveal), (119, s19_be_honest), (122, s20_open_book),
]
SHOT_T0 = {}


def install(words, total):
    R.SHOTS = SHOTS
    b = R.shot_bounds(words, total)
    for (t0, _), (_, fn) in zip(b, SHOTS):
        SHOT_T0[fn.__name__.split('_')[0]] = t0
    return b


if __name__ == '__main__':
    import json
    args = sys.argv[1:]
    wpath = os.path.join(HERE, 'words.json')
    meta = json.load(open(wpath))
    install(meta['words'], meta['duration'])
    R.main(args + ['--words', wpath])
