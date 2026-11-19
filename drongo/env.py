"""Kalahari environment: sky, sun, layered dunes, sand ground, acacias, burrows.
Background elements use soft colour and thin dark outlines so the thick-lined
characters pop, like the reference videos."""
import math
import random
import cairo
from chars import C, src, ellipse, fill_stroke, stick, INK, soft_ellipse, rim, clipped

PI = math.pi

PALETTES = {
    'dawn': dict(sky0=C('#f7b267'), sky1=C('#fbe3b4'), sky_top=C('#6f8fc9'),
                 far=C('#e8b98a'), mid=C('#dba066'), near=C('#e9b779'), near2=C('#d79a5c'),
                 sun=C('#fff3c9'), tree=C('#6d7a3a'), tree_sh=C('#4f5a28'), haze=C('#ffd9a0')),
    'day': dict(sky0=C('#9fd3f2'), sky1=C('#e9f6fb'), sky_top=C('#3f8fd8'),
                far=C('#efcf9b'), mid=C('#e4b678'), near=C('#efc287'), near2=C('#dca266'),
                sun=C('#fffbe6'), tree=C('#7b8b3d'), tree_sh=C('#57652a'), haze=C('#fdf1d3')),
}


def lerp(a, b, t):
    return a + (b - a) * t


def mix(c0, c1, t):
    return tuple(lerp(a, b, t) for a, b in zip(c0, c1))


def sky(ctx, W, H, horizon_y, pal, extra_top=0.0):
    g = cairo.LinearGradient(0, horizon_y - H * 1.2, 0, horizon_y)
    g.add_color_stop_rgb(0, *pal['sky_top'])
    g.add_color_stop_rgb(0.55, *pal['sky0'])
    g.add_color_stop_rgb(1, *pal['sky1'])
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(g)
    ctx.fill()


def sun(ctx, x, y, r, pal):
    g = cairo.RadialGradient(x, y, r * 0.2, x, y, r * 5)
    g.add_color_stop_rgba(0, *pal['sun'], 0.95)
    g.add_color_stop_rgba(0.25, *pal['sun'], 0.35)
    g.add_color_stop_rgba(1, *pal['sun'], 0)
    ctx.arc(x, y, r * 5, 0, 2 * PI)
    ctx.set_source(g)
    ctx.fill()
    ctx.arc(x, y, r, 0, 2 * PI)
    src(ctx, pal['sun'])
    ctx.fill()


def cloud(ctx, x, y, s, alpha=0.9):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    for (cx, cy, r) in ((0, 0, 30), (34, -12, 38), (72, 0, 30), (36, 10, 30)):
        ctx.new_sub_path()
        ctx.arc(cx, cy, r, 0, 2 * PI)
    src(ctx, (1, 1, 1, alpha))
    ctx.fill()
    ctx.restore()


def dune_band(ctx, x0, x1, base, heights, color, color2=None, seed=0, outline=None, depth=900):
    """Smooth rolling hills. y up is negative; base is the y of the band bottom."""
    rnd = random.Random(seed)
    n = len(heights)
    step = (x1 - x0) / (n - 1)
    pts = [(x0 + i * step, base - h) for i, h in enumerate(heights)]
    ctx.move_to(x0, base + depth)
    ctx.line_to(*pts[0])
    for i in range(1, n):
        (ax, ay), (bx, by) = pts[i - 1], pts[i]
        mx = (ax + bx) / 2
        ctx.curve_to(mx, ay, mx, by, bx, by)
    ctx.line_to(x1, base + depth)
    ctx.close_path()
    top = min(p[1] for p in pts)
    if color2:
        g = cairo.LinearGradient(0, top, 0, base + 60)
        g.add_color_stop_rgb(0, *color)
        g.add_color_stop_rgb(1, *color2)
        ctx.set_source(g)
    else:
        src(ctx, color)
    if outline:
        ctx.fill_preserve()
        ctx.set_line_width(outline[1])
        src(ctx, outline[0])
        ctx.stroke()
    else:
        ctx.fill()


def hills(seed, n, lo, hi):
    r = random.Random(seed)
    return [r.uniform(lo, hi) for _ in range(n)]


def acacia(ctx, x, y, s, pal, seed=1, outline=True):
    """Flat-topped Kalahari acacia (umbrella thorn). Origin at the trunk base."""
    rnd = random.Random(seed)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    # canopy shadow pooled on the sand
    soft_ellipse(ctx, 40, 6, 230, 30, C('#5a3418'), 0.35, core=0.5)
    soft_ellipse(ctx, 0, 2, 40, 8, C('#2a1608'), 0.5)
    trunk = C('#5b3d2a')
    lw = 5 if outline else 0
    # trunk and branches
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    branches = [((0, 0), (-4, -110), (-60, -190)), ((-4, -110), (30, -160), (70, -200)),
                ((-2, -60), (-30, -120), (-110, -170)), ((30, -160), (10, -190), (5, -215))]
    for w, col in ((22, INK), (14, trunk)):
        if col is INK and not outline:
            continue
        for a, b, c in branches:
            ctx.move_to(*a)
            ctx.curve_to(*b, *b, *c)
            ctx.set_line_width(w * (0.9 if a != (0, 0) else 1.15))
            src(ctx, col)
            ctx.stroke()
    for a, b, c in branches[:1]:
        ctx.move_to(a[0] - 3, a[1])
        ctx.curve_to(b[0] - 3, b[1], b[0] - 3, b[1], c[0], c[1] + 4)
        ctx.set_line_width(3)
        src(ctx, (0.85, 0.65, 0.45, 0.5))
        ctx.stroke()
    # canopy: flat umbrella of overlapping puffs
    puffs = []
    for i in range(13):
        px = -170 + i * 26 + rnd.uniform(-8, 8)
        py = -205 - 22 * math.sin(i / 12 * PI) + rnd.uniform(-6, 6)
        puffs.append((px, py, rnd.uniform(30, 42), rnd.uniform(20, 26)))

    def canopy_path():
        for (px, py, rx, ry) in puffs:
            ellipse(ctx, px, py, rx, ry)

    if outline:
        canopy_path()
        ctx.set_line_width(lw * 2)
        src(ctx, INK)
        ctx.stroke()
    canopy_path()
    src(ctx, pal['tree'])
    ctx.fill()
    ctx.save()
    canopy_path()
    ctx.clip()
    for (px, py, rx, ry) in puffs:
        ellipse(ctx, px + 6, py + 14, rx, ry * 0.7)
    src(ctx, pal['tree_sh'])
    ctx.fill()
    for (px, py, rx, ry) in puffs[::2]:
        ellipse(ctx, px - 8, py - 12, rx * 0.5, ry * 0.35)
    src(ctx, (1, 1, 0.85, 0.18))
    ctx.fill()
    ctx.restore()
    ctx.restore()


def acacia_far(ctx, x, y, s, col):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(0, 0)
    ctx.line_to(0, -40)
    ctx.set_line_width(4)
    src(ctx, col)
    ctx.stroke()
    ellipse(ctx, 0, -48, 46, 10)
    src(ctx, col)
    ctx.fill()
    ctx.restore()


def grass(ctx, x, y, s, col=C('#a99a4a'), seed=0, sway=0.0):
    rnd = random.Random(seed)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for i in range(9):
        a = -PI / 2 + rnd.uniform(-0.7, 0.7)
        L = rnd.uniform(30, 60)
        ex = math.cos(a) * L + sway * L * 0.3
        ey = math.sin(a) * L
        ctx.move_to(rnd.uniform(-6, 6), 0)
        ctx.curve_to(ex * 0.3, ey * 0.5, ex * 0.8, ey * 0.9, ex, ey)
        ctx.set_line_width(3.2)
        src(ctx, col)
        ctx.stroke()
    ctx.restore()


def pebbles(ctx, x0, x1, y0, y1, n, seed, cols):
    rnd = random.Random(seed)
    for i in range(n):
        x = rnd.uniform(x0, x1)
        y = rnd.uniform(y0, y1)
        k = (y - y0) / max(1, (y1 - y0))
        r = lerp(1.0, 5.5, k) * rnd.uniform(0.6, 1.3)
        ellipse(ctx, x, y, r * 1.5, r * 0.8)
        src(ctx, rnd.choice(cols))
        ctx.fill()


def ground(ctx, x0, x1, pal, seed=3, depth=2400):
    g = cairo.LinearGradient(0, 0, 0, 700)
    g.add_color_stop_rgb(0, *mix(pal['near'], pal['haze'], 0.35))
    g.add_color_stop_rgb(1, *pal['near2'])
    ctx.rectangle(x0, -2, x1 - x0, depth)
    ctx.set_source(g)
    ctx.fill()
    # sand ripples
    rnd = random.Random(seed)
    for i in range(40):
        y = 8 + (i / 40) ** 1.6 * 900
        x = rnd.uniform(x0, x1)
        w = lerp(30, 200, y / 900)
        ctx.move_to(x - w, y)
        ctx.curve_to(x - w * 0.3, y - 4 - y * 0.01, x + w * 0.3, y - 4 - y * 0.01, x + w, y)
        ctx.set_line_width(lerp(1, 3.5, y / 900))
        src(ctx, (*pal['near2'], 0.45))
        ctx.stroke()
    pebbles(ctx, x0, x1, 4, 900, 220, seed + 1, [(*pal['near2'], 0.8), C('#c48a52', 0.7), C('#f6dcae', 0.8)])


def burrow(ctx, x, y, s, pal, dark=C('#2b1a10')):
    """Mound with a dark hole. Origin = hole centre."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(-150, 14)
    ctx.curve_to(-110, -34, -50, -40, 0, -38)
    ctx.curve_to(50, -40, 110, -34, 150, 14)
    ctx.close_path()
    g = cairo.LinearGradient(0, -40, 0, 14)
    g.add_color_stop_rgb(0, *mix(pal['near'], (1, 0.95, 0.85), 0.25))
    g.add_color_stop_rgb(1, *pal['near2'])
    ctx.set_source(g)
    ctx.fill()
    soft_ellipse(ctx, 6, -6, 110, 40, C('#6a3e1e'), 0.25)
    ellipse(ctx, 0, 0, 52, 17)
    g2 = cairo.RadialGradient(0, 6, 4, 0, 0, 52)
    g2.add_color_stop_rgb(0, 0.05, 0.03, 0.02)
    g2.add_color_stop_rgb(1, *C('#4a2c18'))
    ctx.set_source(g2)
    ctx.fill_preserve()
    ctx.set_line_width(4)
    src(ctx, C('#7a4e2c'))
    ctx.stroke()
    ctx.restore()


def burrow_front(ctx, x, y, s, pal):
    """Front lip of the burrow, drawn over a character to hide its lower body."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(-150, 14)
    ctx.curve_to(-110, -2, -60, 0, -52, 0)
    ctx.curve_to(-40, 18, 40, 18, 52, 0)
    ctx.curve_to(60, 0, 110, -2, 150, 14)
    ctx.line_to(150, 60)
    ctx.line_to(-150, 60)
    ctx.close_path()
    g = cairo.LinearGradient(0, 0, 0, 40)
    g.add_color_stop_rgb(0, *mix(pal['near'], (1, 0.95, 0.85), 0.15))
    g.add_color_stop_rgb(1, *pal['near'])
    ctx.set_source(g)
    ctx.fill()
    ctx.move_to(-52, 0)
    ctx.curve_to(-40, 18, 40, 18, 52, 0)
    ctx.set_line_width(4)
    src(ctx, C('#7a4e2c'))
    ctx.stroke()
    ctx.restore()


def termite_mound(ctx, x, y, s, pal):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    soft_ellipse(ctx, 50, 4, 200, 26, C('#4a2a12'), 0.4)
    ctx.move_to(-110, 0)
    ctx.curve_to(-90, -60, -60, -120, -40, -170)
    ctx.curve_to(-30, -200, 10, -206, 26, -176)
    ctx.curve_to(50, -130, 90, -60, 110, 0)
    ctx.close_path()
    g = cairo.LinearGradient(-110, 0, 110, 0)
    g.add_color_stop_rgb(0, *C('#d08a52'))
    g.add_color_stop_rgb(1, *C('#9c5c32'))
    ctx.set_source(g)
    ctx.fill()

    def mp():
        ctx.move_to(-110, 0)
        ctx.curve_to(-90, -60, -60, -120, -40, -170)
        ctx.curve_to(-30, -200, 10, -206, 26, -176)
        ctx.curve_to(50, -130, 90, -60, 110, 0)
        ctx.close_path()
    clipped(ctx, mp, lambda: (soft_ellipse(ctx, 80, -40, 70, 160, C('#5e3018'), 0.55),
                              soft_ellipse(ctx, -50, -120, 30, 70, C('#f2b27a'), 0.5),
                              soft_ellipse(ctx, 0, 0, 120, 16, C('#3a1c0c'), 0.45)))
    rim(ctx, mp, C('#ffd9a8'), 5, 3, 5, 0.6)
    mp()
    ctx.set_line_width(5)
    src(ctx, INK)
    ctx.stroke()
    for (a, b) in ((-30, -120), (20, -80), (-50, -50), (40, -30)):
        ellipse(ctx, a, b, 8, 4)
        src(ctx, C('#7b4426', 0.8))
        ctx.fill()
    ctx.restore()


def dust(ctx, x, y, t, s=1.0, seed=0, col=C('#f1d4a2')):
    """Dust puff, t in 0..1."""
    if t <= 0 or t >= 1:
        return
    rnd = random.Random(seed)
    for i in range(9):
        a = rnd.uniform(PI * 1.05, PI * 1.95)
        sp = rnd.uniform(40, 110) * s
        r = (14 + 20 * t) * s * rnd.uniform(0.7, 1.2)
        px = x + math.cos(a) * sp * (1 - (1 - t) ** 2)
        py = y + math.sin(a) * sp * 0.6 * (1 - (1 - t) ** 2)
        ellipse(ctx, px, py, r, r * 0.8)
        src(ctx, (*col, 0.85 * (1 - t)))
        ctx.fill()


def sand_spray(ctx, x, y, t, s=1.0, seed=0, n=18, dirx=-1, col=C('#e2b06e')):
    rnd = random.Random(seed)
    for i in range(n):
        ph = (t * 1.6 + rnd.random()) % 1.0
        vx = dirx * rnd.uniform(80, 220) * s
        vy = -rnd.uniform(140, 300) * s
        px = x + vx * ph
        py = y + vy * ph + 520 * s * ph * ph
        r = rnd.uniform(2.5, 6) * s
        ellipse(ctx, px, py, r, r)
        src(ctx, (*col, 1 - ph * 0.6))
        ctx.fill()


def speed_lines(ctx, cx, cy, t, n=18, r0=180, r1=520, seed=0, col=(1, 1, 1, 0.6)):
    rnd = random.Random(seed + int(t * 15))
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for i in range(n):
        a = rnd.uniform(0, 2 * PI)
        a0 = rnd.uniform(r0, r0 * 1.3)
        ctx.move_to(cx + math.cos(a) * a0, cy + math.sin(a) * a0)
        ctx.line_to(cx + math.cos(a) * r1, cy + math.sin(a) * r1)
        ctx.set_line_width(rnd.uniform(2, 6))
        src(ctx, col)
        ctx.stroke()


def sound_rings(ctx, x, y, t, n=3, r=40, gap=34, ang=0.0, spread=0.9, col=INK, lw=6):
    """Cartoon shout arcs."""
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for i in range(n):
        k = (t * 2.2 + i / n) % 1.0
        rr = r + k * gap * n
        ctx.new_path()
        ctx.arc(x, y, rr, ang - spread / 2, ang + spread / 2)
        ctx.set_line_width(lw * (1 - k * 0.5))
        src(ctx, (*col[:3], 1 - k))
        ctx.stroke()
