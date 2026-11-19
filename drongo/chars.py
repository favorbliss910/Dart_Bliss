"""Character + prop drawing in the reference style:
thick black outlines, flat fills with one cel-shade, big round white eyes
with dot pupils, thin black stick limbs."""
import math
import cairo

PI = math.pi
INK = (0.06, 0.05, 0.06)


def C(h, a=None):
    h = h.lstrip('#')
    c = tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return c if a is None else c + (a,)


def src(ctx, c):
    if len(c) == 4:
        ctx.set_source_rgba(*c)
    else:
        ctx.set_source_rgb(*c)


def ellipse(ctx, cx, cy, rx, ry, rot=0.0):
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(rot)
    ctx.scale(rx, ry)
    ctx.new_sub_path()
    ctx.arc(0, 0, 1, 0, 2 * PI)
    ctx.restore()


def fill_stroke(ctx, fill, lw=5.0, ink=INK):
    src(ctx, fill)
    ctx.fill_preserve()
    ctx.set_line_width(lw)
    src(ctx, ink)
    ctx.stroke()


def stick(ctx, pts, lw=5.0, ink=INK):
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.move_to(*pts[0])
    if len(pts) == 3:
        # smooth elbow
        (x0, y0), (x1, y1), (x2, y2) = pts
        ctx.curve_to(x1, y1, x1, y1, x2, y2)
    else:
        for p in pts[1:]:
            ctx.line_to(*p)
    ctx.set_line_width(lw)
    src(ctx, ink)
    ctx.stroke()


def shade_clip(ctx, path_fn, shade, cx, cy, rx, ry, rot=0.0):
    """Cel-shade: fill an offset ellipse clipped to the shape."""
    ctx.save()
    path_fn()
    ctx.clip()
    ellipse(ctx, cx, cy, rx, ry, rot)
    src(ctx, shade)
    ctx.fill()
    ctx.restore()


def eye(ctx, x, y, r, look=(0, 0), pupil=None, blink=0.0, iris=None, lw=3.6, lid=0.0):
    """Reference-style eye: white disc, black outline, black dot pupil."""
    if blink > 0.85:
        ctx.move_to(x - r * 0.9, y)
        ctx.curve_to(x - r * 0.3, y + r * 0.35, x + r * 0.3, y + r * 0.35, x + r * 0.9, y)
        ctx.set_line_width(lw)
        src(ctx, INK)
        ctx.stroke()
        return
    ry = r * (1 - blink)
    ellipse(ctx, x, y, r, max(ry, 1))
    src(ctx, (1, 1, 1))
    ctx.fill_preserve()
    ctx.save()
    ctx.clip()
    pr = pupil if pupil is not None else r * 0.36
    px, py = x + look[0] * r * 0.42, y + look[1] * r * 0.42
    if iris:
        ellipse(ctx, px, py, pr * 1.75, pr * 1.75)
        src(ctx, iris)
        ctx.fill()
    ellipse(ctx, px, py, pr, pr)
    src(ctx, INK)
    ctx.fill()
    ellipse(ctx, px - pr * 0.35, py - pr * 0.4, pr * 0.32, pr * 0.32)
    src(ctx, (1, 1, 1))
    ctx.fill()
    if lid > 0:  # heavy lid (smug / suspicious)
        ctx.rectangle(x - r * 1.2, y - r * 1.2, r * 2.4, r * 1.2 * lid * 1.6)
        src(ctx, C('#e9e4dc'))
        ctx.fill()
        ctx.move_to(x - r, y - r + r * 1.9 * lid)
        ctx.line_to(x + r, y - r + r * 1.9 * lid)
        ctx.set_line_width(lw)
        src(ctx, INK)
        ctx.stroke()
    ctx.restore()
    ctx.new_path()
    ellipse(ctx, x, y, r, max(ry, 1))
    ctx.set_line_width(lw)
    src(ctx, INK)
    ctx.stroke()


def bez(p0, p1, p2, p3, t):
    u = 1 - t
    return (u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0],
            u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1])


def taper(ctx, pts, w0, w1, fill, lw=4.5, n=24):
    """Filled tapered stroke along a cubic bezier, outlined."""
    cs = [bez(*pts, i / n) for i in range(n + 1)]
    L, R = [], []
    for i, (x, y) in enumerate(cs):
        a = cs[max(i - 1, 0)]
        b = cs[min(i + 1, n)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        d = math.hypot(dx, dy) or 1
        nx, ny = -dy / d, dx / d
        w = (w0 + (w1 - w0) * i / n) / 2
        L.append((x + nx * w, y + ny * w))
        R.append((x - nx * w, y - ny * w))
    ctx.move_to(*L[0])
    for p in L[1:]:
        ctx.line_to(*p)
    ex, ey = cs[-1]
    for p in reversed(R):
        ctx.line_to(*p)
    ctx.close_path()
    fill_stroke(ctx, fill, lw)


# --------------------------------------------------------------------------
# MEERKAT
# --------------------------------------------------------------------------
FUR = C('#d9b07a')
FUR_SH = C('#b98a55')
FUR_HI = C('#ecc994')
BELLY = C('#f3e0b8')
MASK = C('#4a3020')
EAR = C('#5e3f29')


def meerkat(ctx, x, y, s=1.0, look=(0, 0), mouth='smile', blink=0.0, lean=0.0,
            tilt=0.0, arms='tucked', eyes='normal', turn=0.0, squash=0.0,
            tail=0.0, brow=None, sweat=False, hold=None, flip=False, lid=0.0,
            body_col=None):
    """Origin at the feet. ~230 units tall at s=1."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(-s if flip else s, s)
    # squash & stretch about the feet
    ctx.scale(1 + squash * 0.5, 1 - squash)
    lw = 5.0
    fur = body_col or FUR

    # tail (behind everything) - used as tripod
    ctx.save()
    ctx.translate(-26, -36)
    ctx.rotate(tail * 0.4)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(0, 0)
    ctx.curve_to(-30, 6, -55, 30, -86, 34)
    ctx.set_line_width(17)
    src(ctx, INK)
    ctx.stroke_preserve()
    ctx.set_line_width(9)
    src(ctx, fur)
    ctx.stroke()
    ctx.move_to(-70, 33)
    ctx.line_to(-86, 34)
    ctx.set_line_width(9)
    src(ctx, MASK)
    ctx.stroke()
    ctx.restore()

    # legs
    stick(ctx, [(-15, -34), (-17, -16), (-18, -2)], lw)
    stick(ctx, [(15, -34), (17, -16), (18, -2)], lw)
    for fx in (-18, 18):
        ellipse(ctx, fx + (3 if fx > 0 else -3), -1, 9, 4.5)
        src(ctx, INK)
        ctx.fill()

    # everything above the hips leans
    ctx.save()
    ctx.translate(0, -36)
    ctx.rotate(lean)
    ctx.translate(0, 36)

    def body_path():
        ctx.move_to(-21, -150)
        ctx.curve_to(-36, -112, -46, -64, -38, -42)
        ctx.curve_to(-30, -20, 30, -20, 38, -42)
        ctx.curve_to(46, -64, 36, -112, 21, -150)
        ctx.close_path()

    body_path()
    src(ctx, fur)
    ctx.fill()
    shade_clip(ctx, body_path, FUR_SH, 34, -70, 22, 70)
    ellipse(ctx, 0 + turn * 6, -80, 22, 40)
    src(ctx, BELLY)
    ctx.fill()
    body_path()
    ctx.set_line_width(lw)
    src(ctx, INK)
    ctx.stroke()

    # arms
    arm_sets = {
        'tucked': [[(-22, -118), (-34, -98), (-12, -100)], [(22, -118), (34, -98), (12, -100)]],
        'down':   [[(-24, -118), (-36, -92), (-32, -70)], [(24, -118), (36, -92), (32, -70)]],
        'up':     [[(-24, -118), (-52, -130), (-56, -160)], [(24, -118), (52, -130), (56, -160)]],
        'hold':   [[(-22, -118), (-34, -100), (-10, -112)], [(22, -118), (34, -100), (10, -112)]],
        'dig':    [[(-22, -118), (-30, -80), (-22, -46)], [(22, -118), (30, -80), (22, -46)]],
        'shrug':  [[(-24, -118), (-48, -112), (-56, -132)], [(24, -118), (48, -112), (56, -132)]],
        'point':  [[(-22, -118), (-34, -98), (-12, -100)], [(24, -118), (52, -126), (78, -140)]],
    }
    arm_list = arm_sets[arms] if isinstance(arms, str) else arms
    if hold:
        ctx.save()
        ctx.translate(0, -114)
        hold(ctx)
        ctx.restore()
    for a in arm_list:
        stick(ctx, a, lw)
        ellipse(ctx, a[-1][0], a[-1][1], 5.5, 5.5)
        src(ctx, INK)
        ctx.fill()

    # head
    ctx.save()
    ctx.translate(0, -140)
    ctx.rotate(tilt)
    ctx.translate(0, 140)
    hx = turn * 7
    for side in (-1, 1):
        ellipse(ctx, side * 46 + hx * 0.3, -186, 11, 11)
        fill_stroke(ctx, EAR, 4.5)

    def head_path():
        ellipse(ctx, 0, -180, 52, 44)

    head_path()
    src(ctx, fur)
    ctx.fill()
    shade_clip(ctx, head_path, FUR_SH, 34 - turn * 10, -160, 36, 34)
    shade_clip(ctx, head_path, FUR_HI, -20 + hx, -210, 30, 14)
    head_path()
    ctx.set_line_width(lw)
    src(ctx, INK)
    ctx.stroke()

    # eye patches
    for side in (-1, 1):
        ellipse(ctx, side * 22 + hx, -182, 22, 19, side * -0.35)
        src(ctx, MASK)
        ctx.fill()
    # eyes
    er = {'normal': 15, 'wide': 17.5, 'small': 13}[eyes]
    pr = {'normal': 5.6, 'wide': 3.4, 'small': 5.2}[eyes]
    for side in (-1, 1):
        eye(ctx, side * 21 + hx, -186, er, look, pupil=pr, blink=blink, lid=lid)
    if brow:  # 'angry' / 'worried' / 'raised'
        for side in (-1, 1):
            if brow == 'angry':
                a, b = (side * 34 + hx, -212), (side * 9 + hx, -203)
            elif brow == 'worried':
                a, b = (side * 34 + hx, -201), (side * 9 + hx, -212)
            else:
                a, b = (side * 32 + hx, -214), (side * 10 + hx, -216)
            stick(ctx, [a, b], 4.5)
    # snout
    ellipse(ctx, hx * 1.3, -157, 22, 14)
    src(ctx, BELLY)
    ctx.fill()
    ellipse(ctx, hx * 1.5, -164, 9, 6)
    src(ctx, INK)
    ctx.fill()
    ellipse(ctx, hx * 1.5 - 3, -166, 3, 1.8)
    src(ctx, (1, 1, 1, 0.7))
    ctx.fill()
    mx, my = hx * 1.3, -150
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    if mouth == 'smile':
        ctx.arc(mx, my - 6, 9, 0.25 * PI, 0.75 * PI)
        ctx.set_line_width(3.6)
        src(ctx, INK)
        ctx.stroke()
    elif mouth == 'flat':
        ctx.move_to(mx - 7, my)
        ctx.line_to(mx + 7, my)
        ctx.set_line_width(3.6)
        src(ctx, INK)
        ctx.stroke()
    elif mouth == 'frown':
        ctx.arc(mx, my + 6, 8, 1.2 * PI, 1.8 * PI)
        ctx.set_line_width(3.6)
        src(ctx, INK)
        ctx.stroke()
    elif mouth == 'o':
        ellipse(ctx, mx, my + 1, 5, 6)
        fill_stroke(ctx, C('#5a1f1f'), 3.4)
    elif mouth in ('bark', 'scream'):
        big = 1.0 if mouth == 'bark' else 1.35
        ctx.move_to(mx - 14 * big, my - 4)
        ctx.curve_to(mx - 14 * big, my + 22 * big, mx + 14 * big, my + 22 * big, mx + 14 * big, my - 4)
        ctx.close_path()
        src(ctx, C('#5a1a1c'))
        ctx.fill_preserve()
        ctx.save()
        ctx.clip()
        ellipse(ctx, mx, my + 16 * big, 10 * big, 7 * big)
        src(ctx, C('#e0707a'))
        ctx.fill()
        ctx.restore()
        ctx.move_to(mx - 14 * big, my - 4)
        ctx.curve_to(mx - 14 * big, my + 22 * big, mx + 14 * big, my + 22 * big, mx + 14 * big, my - 4)
        ctx.close_path()
        ctx.set_line_width(3.6)
        src(ctx, INK)
        ctx.stroke()
    elif mouth == 'grin':
        ctx.move_to(mx - 13, my - 4)
        ctx.curve_to(mx - 8, my + 10, mx + 8, my + 10, mx + 13, my - 4)
        ctx.close_path()
        fill_stroke(ctx, (1, 1, 1), 3.4)
    elif mouth == 'chew':
        ellipse(ctx, mx, my, 7, 3.5)
        fill_stroke(ctx, C('#5a1f1f'), 3.2)
    if sweat:
        ctx.move_to(54, -214)
        ctx.curve_to(46, -200, 50, -192, 56, -192)
        ctx.curve_to(62, -192, 66, -200, 54, -214)
        fill_stroke(ctx, C('#8fd3ff'), 3)
    ctx.restore()  # head
    ctx.restore()  # lean
    ctx.restore()


def meerkat_butt(ctx, x, y, s=1.0, wiggle=0.0, flip=False):
    """Meerkat seen from the side, head down in a hole (head hidden below y)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(-s if flip else s, s)
    ctx.rotate(0.15 * math.sin(wiggle))
    # legs planted
    stick(ctx, [(-10, -54), (-22, -22), (-26, 0)], 5)
    stick(ctx, [(14, -50), (8, -22), (6, 0)], 5)
    for fx in (-26, 6):
        ellipse(ctx, fx - 3, -1, 9, 4.5)
        src(ctx, INK)
        ctx.fill()
    # tail up and wagging
    ctx.save()
    ctx.translate(-14, -78)
    ctx.rotate(-0.25 + 0.25 * math.sin(wiggle * 2.3))
    ctx.move_to(0, 0)
    ctx.curve_to(-20, -26, -24, -60, -14, -96)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_width(17)
    src(ctx, INK)
    ctx.stroke_preserve()
    ctx.set_line_width(9)
    src(ctx, FUR)
    ctx.stroke()
    ctx.move_to(-16, -84)
    ctx.line_to(-14, -96)
    ctx.set_line_width(9)
    src(ctx, MASK)
    ctx.stroke()
    ctx.restore()

    def body_path():
        ellipse(ctx, 20, -48, 34, 50, 0.75)

    body_path()
    src(ctx, FUR)
    ctx.fill()
    shade_clip(ctx, body_path, FUR_SH, 34, -22, 26, 40, 0.75)
    body_path()
    ctx.set_line_width(5)
    src(ctx, INK)
    ctx.stroke()
    # digging arms + the sand pile hiding the head
    stick(ctx, [(-6, -30), (-24, -14), (-34, -4)], 5)
    ctx.move_to(-62, 2)
    ctx.curve_to(-56, -26, -20, -30, -8, 2)
    ctx.close_path()
    fill_stroke(ctx, C('#e2b273'), 4, C('#8a5a33'))
    for (px, py) in ((-44, -12), (-30, -18), (-22, -6)):
        ellipse(ctx, px, py, 3, 2)
        src(ctx, C('#b98a55'))
        ctx.fill()
    ctx.restore()


# --------------------------------------------------------------------------
# DRONGO
# --------------------------------------------------------------------------
DR = C('#1b1d29')
DR_HI = C('#3f5491')
DR_SH = C('#0d0e15')


def drongo(ctx, x, y, s=1.0, look=(0.3, 0), beak=0.0, blink=0.0, tilt=0.0,
           wing=0.0, flip=False, lid=0.0, brow=None, puff=0.0, eye_scale=1.0):
    """Fork-tailed drongo, perched. Origin at feet, faces right. ~150 tall at s=1."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(-s if flip else s, s)
    lw = 4.6
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)

    # forked tail - two long prongs that flare outward at the tips
    for side in (-1, 1):
        pts = [(-14, -24), (-18 + side * 10, 18), (-16 + side * 26, 50), (-16 + side * 50, 66)]
        taper(ctx, pts, 16, 9, DR, lw)
        stick(ctx, [(-14, -14), (-17 + side * 10, 20), (-16 + side * 24, 46)], 2.2, DR_HI + (0.6,))

    # legs
    stick(ctx, [(-4, -12), (-6, -2)], 4)
    stick(ctx, [(6, -12), (6, -2)], 4)
    for fx in (-6, 6):
        stick(ctx, [(fx - 6, 0), (fx + 7, 0)], 3.6)

    # body
    def body():
        ellipse(ctx, 0, -42, 28 + puff * 6, 38 + puff * 4, -0.3)

    body()
    src(ctx, DR)
    ctx.fill()
    shade_clip(ctx, body, DR_HI, -12, -60, 12, 22, -0.3)
    body()
    ctx.set_line_width(lw)
    src(ctx, INK)
    ctx.stroke()
    # wing
    ctx.save()
    ctx.translate(-8, -60)
    ctx.rotate(-wing * 1.2)
    ctx.move_to(0, 0)
    ctx.curve_to(-26, 6, -34, 40, -22, 62)
    ctx.curve_to(-14, 50, 4, 30, 10, 6)
    ctx.close_path()
    fill_stroke(ctx, DR_SH, lw)
    for i in range(3):
        ctx.move_to(-6 - i * 6, 16 + i * 8)
        ctx.line_to(-18 - i * 3, 42 + i * 6)
        ctx.set_line_width(2)
        src(ctx, DR_HI + (0.6,))
        ctx.stroke()
    ctx.restore()

    # head
    ctx.save()
    ctx.translate(8, -78)
    ctx.rotate(tilt)

    def head():
        ellipse(ctx, 4, -14, 30, 27)

    # tiny crest tuft
    ctx.move_to(-8, -38)
    ctx.curve_to(-6, -52, 6, -50, 2, -40)
    fill_stroke(ctx, DR, 3.6)
    head()
    src(ctx, DR)
    ctx.fill()
    shade_clip(ctx, head, DR_HI, -10, -30, 18, 9)
    head()
    ctx.set_line_width(lw)
    src(ctx, INK)
    ctx.stroke()
    # beak (upper + lower, hinge at ~(26,-10))
    bx, by = 24, -10
    op = beak
    ctx.save()
    ctx.translate(bx, by)
    if op > 0.05:
        ctx.move_to(0, -6)
        ctx.line_to(24, -6 - op * 8)
        ctx.line_to(20, 8 + op * 14)
        ctx.line_to(0, 8)
        ctx.close_path()
        src(ctx, C('#b2262f'))
        ctx.fill()
    ctx.save()
    ctx.rotate(-op * 0.35)
    ctx.move_to(-2, -8)
    ctx.curve_to(12, -10, 24, -6, 30, 0)
    ctx.line_to(0, 2)
    ctx.close_path()
    fill_stroke(ctx, C('#2a2a33'), 3.6)
    ctx.restore()
    ctx.save()
    ctx.rotate(op * 0.7)
    ctx.move_to(0, 2)
    ctx.line_to(26, 2)
    ctx.curve_to(20, 8, 10, 9, -1, 8)
    ctx.close_path()
    fill_stroke(ctx, C('#2a2a33'), 3.6)
    ctx.restore()
    ctx.restore()
    # eye: white disc with the drongo's ruby-red iris
    er = 12 * eye_scale
    eye(ctx, 10, -18, er, look, pupil=er * 0.3, blink=blink, iris=C('#d42a2a'), lid=lid, lw=3.4)
    if brow == 'angry':
        stick(ctx, [(-4, -38), (22, -30)], 4)
    elif brow == 'raised':
        stick(ctx, [(-2, -40), (22, -42)], 4)
    ctx.restore()
    ctx.restore()


# --------------------------------------------------------------------------
# HAWK (seen from below, soaring)
# --------------------------------------------------------------------------
HK = C('#7b4b2a')
HK_UNDER = C('#d8b07c')


def hawk(ctx, x, y, s=1.0, flap=0.0, rot=0.0, menace=1.0, silhouette=False):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    lw = 5
    f = math.sin(flap)
    body = INK if silhouette else HK
    under = INK if silhouette else HK_UNDER
    for side in (-1, 1):
        ctx.save()
        ctx.scale(side, 1)
        ctx.rotate(-0.12 * f)
        ctx.move_to(10, -10)
        ctx.curve_to(60, -40 - 20 * f, 130, -40 - 30 * f, 175, -14 - 30 * f)
        # finger feathers
        tip = -14 - 30 * f
        for i in range(4):
            ctx.line_to(180 - i * 12, tip + 10 + i * 6)
            ctx.line_to(166 - i * 12, tip + 10 + i * 7)
        ctx.curve_to(110, 30, 60, 32, 10, 18)
        ctx.close_path()
        fill_stroke(ctx, body, lw)
        if not silhouette:
            ctx.move_to(20, 0)
            ctx.curve_to(60, -18 - 14 * f, 110, -20 - 20 * f, 140, -6 - 24 * f)
            ctx.curve_to(100, 14, 60, 18, 20, 12)
            ctx.close_path()
            src(ctx, under)
            ctx.fill()
            for i in range(5):
                ctx.move_to(40 + i * 22, 14 - i * 2)
                ctx.line_to(46 + i * 22, 26 - i * 1)
                ctx.set_line_width(2.4)
                src(ctx, HK + (0.7,))
                ctx.stroke()
        ctx.restore()
    # tail fan
    ctx.move_to(-14, 30)
    ctx.line_to(-24, 86)
    ctx.curve_to(-8, 94, 8, 94, 24, 86)
    ctx.line_to(14, 30)
    ctx.close_path()
    fill_stroke(ctx, body, lw)
    if not silhouette:
        for i in (-1, 0, 1):
            ctx.move_to(i * 10, 70)
            ctx.line_to(i * 12, 88)
            ctx.set_line_width(4)
            src(ctx, C('#b0562e'))
            ctx.stroke()
    # body
    ellipse(ctx, 0, 8, 22, 42)
    fill_stroke(ctx, body, lw)
    if not silhouette:
        ellipse(ctx, 0, 14, 13, 28)
        src(ctx, under)
        ctx.fill()
        for i in range(4):
            stick(ctx, [(-6, 4 + i * 9), (0, 8 + i * 9), (6, 4 + i * 9)], 2.2, HK)
    # head
    ellipse(ctx, 0, -36, 20, 19)
    fill_stroke(ctx, body, lw)
    if not silhouette:
        # hooked yellow beak
        ctx.move_to(-7, -28)
        ctx.curve_to(-6, -16, 0, -8, 3, -6)
        ctx.curve_to(6, -12, 7, -20, 7, -28)
        ctx.close_path()
        fill_stroke(ctx, C('#f2c230'), 3.4)
        for side in (-1, 1):
            eye(ctx, side * 10, -40, 7, (0, 0.6), pupil=2.6, lw=3)
            # menacing brows
            stick(ctx, [(side * 18, -50), (side * 3, -44)], 4 * menace)
    ctx.restore()


# --------------------------------------------------------------------------
# PROPS
# --------------------------------------------------------------------------
def beetle(ctx, x, y, s=1.0, rot=0.0, look=(0, 0), legs=0.0, worried=False):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    for side in (-1, 1):
        for i in range(3):
            a = (i - 1) * 0.6 + math.sin(legs + i * 2) * 0.25
            stick(ctx, [(side * 14, -2 + i * 9), (side * (30 + 4 * math.cos(a)), -10 + i * 12 + 6 * math.sin(a))], 3.4)
    ellipse(ctx, 0, -24, 13, 11)
    fill_stroke(ctx, C('#20262a'), 4)

    def shell():
        ellipse(ctx, 0, 8, 22, 26)

    shell()
    src(ctx, C('#2f5d4a'))
    ctx.fill()
    shade_clip(ctx, shell, C('#1f3e33'), 10, 16, 16, 24)
    ellipse(ctx, -8, -2, 5, 10, 0.3)
    src(ctx, (1, 1, 1, 0.55))
    ctx.fill()
    shell()
    ctx.set_line_width(4)
    src(ctx, INK)
    ctx.stroke()
    stick(ctx, [(0, -16), (0, 33)], 3)
    for side in (-1, 1):
        eye(ctx, side * 6, -30, 6, look, pupil=2.2, lw=2.6)
    if worried:
        stick(ctx, [(-12, -42), (-3, -38)], 2.6)
        stick(ctx, [(12, -42), (3, -38)], 2.6)
    ctx.restore()


def grub(ctx, x, y, s=1.0, rot=0.0, wiggle=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    ctx.move_to(-30, 0)
    for i in range(7):
        a = -30 + i * 10
        ctx.line_to(a, 6 * math.sin(wiggle + i * 0.9))
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_width(26)
    src(ctx, INK)
    ctx.stroke_preserve()
    ctx.set_line_width(18)
    src(ctx, C('#f4e7c8'))
    ctx.stroke()
    ctx.restore()


def scorpion(ctx, x, y, s=1.0, rot=0.0, tail=0.0, claws=0.0, look=(0, 0)):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    col = C('#d98a3a')
    sh = C('#b0652a')
    for side in (-1, 1):
        for i in range(4):
            stick(ctx, [(side * 14, -6 + i * 8), (side * 34, -14 + i * 12), (side * 40, 2 + i * 12)], 3.4)
    # claws
    for side in (-1, 1):
        ox = math.sin(claws) * 4
        stick(ctx, [(side * 10, -16), (side * 30, -36), (side * 26, -56)], 6)
        ctx.save()
        ctx.translate(side * 26, -64)
        ctx.rotate(side * (0.2 + 0.2 * math.sin(claws)))
        ctx.move_to(-10, 6)
        ctx.curve_to(-14, -14, -2, -22, 2 + ox * 0.2, -10)
        ctx.line_to(0, -4)
        ctx.curve_to(6, -18, 14, -12, 10, 6)
        ctx.close_path()
        fill_stroke(ctx, col, 4)
        ctx.restore()
    # tail segments curling over the back
    segs = 7
    px, py = 0, 22
    ang = 0.5
    pts = []
    for i in range(segs):
        ang -= (0.55 + 0.08 * tail)
        px += math.cos(ang) * 17
        py += math.sin(ang) * 17
        pts.append((px, py))
    ellipse(ctx, 0, 6, 18, 24)
    fill_stroke(ctx, col, 4.4)
    for i in range(3):
        stick(ctx, [(-14, -2 + i * 10), (14, -2 + i * 10)], 2.4, sh)
    for i, (qx, qy) in enumerate(pts):
        r = 10 - i * 0.8
        ellipse(ctx, qx, qy, r, r)
        fill_stroke(ctx, col, 4)
    qx, qy = pts[-1]
    ctx.move_to(qx - 6, qy)
    ctx.curve_to(qx - 2, qy + 18, qx + 10, qy + 18, qx + 12, qy + 22)
    ctx.curve_to(qx + 6, qy + 10, qx + 8, qy + 2, qx + 6, qy - 2)
    ctx.close_path()
    fill_stroke(ctx, C('#5b2a12'), 3.4)
    for side in (-1, 1):
        eye(ctx, side * 7, -12, 6, look, pupil=2.2, lw=2.6)
    stick(ctx, [(-13, -24), (-3, -20)], 3)
    stick(ctx, [(13, -24), (3, -20)], 3)
    ctx.restore()


def lizard(ctx, x, y, s=1.0, rot=0.0, look=(0, 0), sweat=0.0, tail=0.0, blink=0.0, mouth='wobble'):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    col = C('#93c25a')
    sh = C('#6f9a3e')
    # tail
    ctx.move_to(-40, 6)
    ctx.curve_to(-90, 10 + 20 * math.sin(tail), -120, -10, -150, 8 + 10 * math.sin(tail + 1))
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_width(20)
    src(ctx, INK)
    ctx.stroke_preserve()
    ctx.set_line_width(11)
    src(ctx, col)
    ctx.stroke()
    for fx, d in ((-30, 1), (20, 1), (-30, -1), (20, -1)):
        stick(ctx, [(fx, 0), (fx + 10, 22 * d if d > 0 else 18), (fx + 18, 26 if d > 0 else 24)], 4)

    def body():
        ellipse(ctx, -6, 0, 50, 20)

    body()
    src(ctx, col)
    ctx.fill()
    shade_clip(ctx, body, sh, -6, 14, 50, 10)
    for i in range(4):
        ellipse(ctx, -34 + i * 16, -6, 4, 3)
        src(ctx, sh)
        ctx.fill()
    body()
    ctx.set_line_width(4.4)
    src(ctx, INK)
    ctx.stroke()
    # head
    ellipse(ctx, 52, -14, 32, 24)
    fill_stroke(ctx, col, 4.4)
    eye(ctx, 50, -26, 13, look, pupil=3.6, blink=blink, lw=3.2)
    eye(ctx, 70, -24, 11, look, pupil=3.2, blink=blink, lw=3.2)
    # worried brows
    stick(ctx, [(40, -46), (56, -40)], 3.4)
    stick(ctx, [(64, -40), (78, -44)], 3.4)
    # wobbly worried mouth
    ctx.move_to(54, -2)
    for i in range(5):
        ctx.line_to(56 + i * 5, -2 + (3 if i % 2 else -1))
    ctx.set_line_width(3)
    src(ctx, INK)
    ctx.stroke()
    if sweat > 0:
        for k, (sx, sy) in enumerate(((86, -46), (30, -44))):
            dy = (sweat * 30 + k * 12) % 26
            ctx.move_to(sx, sy + dy)
            ctx.curve_to(sx - 7, sy + dy + 12, sx - 4, sy + dy + 18, sx, sy + dy + 18)
            ctx.curve_to(sx + 4, sy + dy + 18, sx + 7, sy + dy + 12, sx, sy + dy)
            fill_stroke(ctx, C('#8fd3ff'), 2.6)
    ctx.restore()
