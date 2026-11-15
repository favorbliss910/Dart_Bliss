# Shared environment renderers used by scenes.
import math, functools
import numpy as np
import skia
from core import *
from assets import *
from elements import *

@functools.lru_cache(None)
def grad_img(key, top, bottom, mid=None, w=64, h=256, radial=False):
    s = skia.Surface(w, h); c = s.getCanvas()
    cols = [hexc(top), hexc(mid), hexc(bottom)] if mid else [hexc(top), hexc(bottom)]
    if radial:
        c.drawPaint(P(shader=rad(w / 2, h / 2, max(w, h) * .75, cols)))
    else:
        c.drawPaint(P(shader=lin((0, 0), (0, h), cols)))
    return s.makeImageSnapshot()

def bg(c, top, bottom, mid=None, alpha=1.0):
    img = grad_img((top, bottom, mid), top, bottom, mid)
    draw_img(c, img, 0, 0, W, H, alpha)

def space(c, t, zoom=1.0, ox=0.0, oy=0.0, alpha=1.0, star_alpha=1.0, seed=1):
    bg(c, '#0b1230', '#05070f', '#070B1A', alpha)
    # faint nebula haze
    draw_img(c, grad_img('neb', '#1C2A55', '#070B1A', w=128, h=128, radial=True), -300 + ox * .1, -200 + oy * .1, W + 600, H + 400, .35 * alpha)
    draw_stars(c, t, star_alpha * alpha, ox, oy, zoom, seed)

# ---------------------------------------------------------------- multiplane clouds (falling = clouds move up)
CLOUD_LAYERS = [  # depth factor, scale, count, alpha, brightness
    (0.25, 0.55, 9, .55, .70),
    (0.45, 0.85, 8, .75, .82),
    (0.75, 1.30, 6, .90, .95),
    (1.30, 2.30, 4, .95, 1.05),
]

@functools.lru_cache(None)
def _cloud_layout(seed, n):
    rng = np.random.default_rng(seed)
    return rng.random((n, 4))

def cloud_world(c, t, fall=60.0, drift=0.0, tint=(1.0, .78, .52), bg_top='#E3B47A', bg_bot='#7a4426', bg_mid=None,
                layers=None, alpha=1.0, density=1.0, haze=0.0, ox=0.0, oy=0.0, fg=True, bg_draw=True, depth_dark=0.0):
    """fall: px/s upward motion of the nearest layer. drift: horizontal px/s."""
    if bg_draw:
        bg(c, bg_top, bg_bot, bg_mid, alpha)
    sprites = cloud_sprites()
    lays = CLOUD_LAYERS if layers is None else layers
    for li, (dep, sc, cnt, la, br) in enumerate(lays):
        if not fg and dep > 1.0:
            continue
        lay = _cloud_layout(li * 13 + 7, cnt)
        span_y = H + 700 * sc
        span_x = W + 900 * sc
        dk = 1 - depth_dark * (1 - dep / 1.5) * .6
        cf = tint_cf(tint[0] * br * dk, tint[1] * br * dk, tint[2] * br * dk)
        for i in range(int(cnt * density + .5)):
            r = lay[i % cnt]
            x = (r[0] * span_x + drift * dep * t + ox * dep) % span_x - 450 * sc
            y = (r[1] * span_y - fall * dep * t + oy * dep) % span_y - 350 * sc
            img = sprites[int(r[2] * len(sprites)) % len(sprites)]
            w_ = 512 * sc * (0.8 + .5 * r[3]); h_ = 300 * sc * (0.8 + .5 * r[3])
            draw_img(c, img, x, y, w_, h_, alpha * la, cf=cf)
    if haze > 0:
        c.drawPaint(P(hexc(bg_bot, haze * alpha)))

def speed_lines(c, t, alpha, direction=(0, -1), n=60, speed=2400, length=180, color='#FFF1D6', seed=3, width=2.0):
    """Streaks moving along direction (unit vector)."""
    if alpha <= 0:
        return
    rng = np.random.default_rng(seed)
    pts = rng.random((n, 3))
    dx, dy = direction
    for i in range(n):
        ph = (pts[i, 2] + t * speed / 2400.0) % 1.0
        if abs(dy) > abs(dx):
            x = pts[i, 0] * W
            y = (pts[i, 1] * H + ph * (H + length) * (-dy)) % (H + length) - length
            # draw along direction
            c.drawLine(x, y, x - dx * length, y - dy * length, P(hexc(color, alpha * (.25 + .5 * pts[i, 0])), stroke=width))
        else:
            y = pts[i, 1] * H
            x = (pts[i, 0] * W + ph * (W + length) * (-dx)) % (W + length) - length
            c.drawLine(x, y, x - dx * length, y - dy * length, P(hexc(color, alpha * (.25 + .5 * pts[i, 1])), stroke=width))

def particles(c, t, alpha, n=120, vy=-80, vx=0, color='#FFF1D6', size=(1.5, 4), seed=5, blur=0):
    if alpha <= 0:
        return
    rng = np.random.default_rng(seed)
    pr = rng.random((n, 4))
    for i in range(n):
        d = .4 + pr[i, 3] * .8
        x = (pr[i, 0] * (W + 100) + vx * d * t) % (W + 100) - 50
        y = (pr[i, 1] * (H + 100) + vy * d * t) % (H + 100) - 50
        r = lerp(size[0], size[1], pr[i, 2]) * d
        c.drawCircle(x, y, r, P(hexc(color, alpha * (.3 + .5 * pr[i, 2])), blur=blur))

def flash(c, a, color='#FFF1D6'):
    if a > 0:
        c.drawPaint(P(hexc(color, clamp(a))))

def letter_dim(c, a):
    if a > 0:
        c.drawPaint(P(rgba(0, 0, 0, a)))

def depth_ruler(c, x, y0, y1, offset_px, alpha=1.0, step_px=120, label_fn=None, color=HUDC):
    """Scrolling vertical ruler on the right edge (offset moves ticks upward)."""
    if alpha <= 0:
        return
    c.drawLine(x, y0, x, y1, P(hexc(color, .5 * alpha), stroke=2))
    first = -((offset_px) % step_px)
    k0 = int(offset_px // step_px)
    yy = y0 + first
    i = 0
    while yy <= y1:
        if yy >= y0:
            c.drawLine(x - 18, yy, x, yy, P(hexc(color, .8 * alpha), stroke=2))
            if label_fn:
                draw_text(c, label_fn(k0 + i), x - 26, yy + 6, mono(16, 'medium'), hexc(color), 'right', alpha * .8)
        for j in range(1, 4):
            ys = yy + j * step_px / 4
            if y0 <= ys <= y1:
                c.drawLine(x - 8, ys, x, ys, P(hexc(color, .45 * alpha), stroke=1.5))
        yy += step_px; i += 1

def tex_strip_img(lat_top=30, lat_bot=-30):
    return _tex_strip(lat_top, lat_bot)

@functools.lru_cache(None)
def _tex_strip(lat_top, lat_bot):
    tex = jupiter_tex()
    th = tex.shape[0]
    r0 = int((0.5 - lat_top / 180) * th); r1 = int((0.5 - lat_bot / 180) * th)
    return to_img(tex[r0:r1])
