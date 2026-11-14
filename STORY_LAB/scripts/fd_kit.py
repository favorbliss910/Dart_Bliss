"""Drawing kit for 'What If You Could See the Fourth Dimension?' (landscape 1920x1080 world).
Same Style DNA as the Shorts: thick ink outlines, 3-tone toon shading, violet contact shadows,
glossy eyes, gold extruded titles."""
import math, random
import cairo
from engine import (W, H, INK, GOLD, rgb, shade, mix, fill, stroke, fs, ellipse, poly, rrect, soft_shadow,
                    glow, clamp, lerp, ease, ease_out, wob, pop, label, _font, text3d, vignette)
import cast

SKIN = cast.SKIN
SAM_COL = (0.98, 0.64, 0.22)
HEART = (0.86, 0.18, 0.28)
NEON = (0.55, 0.85, 1.0)
VIO = (0.62, 0.45, 0.95)
PAPER = (0.97, 0.93, 0.84)
YOU = dict(body="adult", outfit="tunic", tunic=(60, 125, 205), trim=(245, 245, 245), hat="hair", hatc=(60, 40, 30),
           face="plain", iris=(60, 110, 200))
SAM_FACE = dict(face="plain", iris=(40, 90, 170))
cast.CAST["you"] = YOU
cast.CAST["abbott"] = dict(body="elder", outfit="robe", tunic=(40, 40, 60), trim=(230, 230, 240), hat="hair",
                           hatc=(200, 200, 205), face="glasses", iris=(70, 90, 140))
cast.CAST["hinton"] = dict(body="tall", outfit="tunic", tunic=(110, 70, 50), trim=(230, 210, 170), hat="hair",
                           hatc=(90, 60, 40), face="stache", hairc=(90, 60, 40), iris=(60, 90, 120))
cast.CAST["ehrenfest"] = dict(body="adult", outfit="robe", tunic=(60, 70, 90), trim=(220, 220, 230), hat="hair",
                              hatc=(40, 35, 35), face="glasses", iris=(60, 70, 90))
cast.CAST["scholar"] = dict(body="adult", outfit="robe", tunic=(90, 60, 110), trim=(240, 220, 160), hat="hair",
                            hatc=(70, 50, 40), face="glasses", iris=(70, 90, 140))


# ----------------------------------------------------------------------------- backgrounds
def bg(f, top, bot):
    c = f.ctx
    f.screen()
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, *rgb(top))
    g.add_color_stop_rgb(1, *rgb(bot))
    c.rectangle(0, 0, W, H)
    c.set_source(g)
    c.fill()


def bg_space(f, seed=1, warm=False):
    bg(f, "#0B0A1E", "#2A1C48" if not warm else "#3A1E3A")
    c = f.ctx
    rnd = random.Random(seed)
    for _ in range(150):
        x, y = rnd.random() * W, rnd.random() * H
        r = rnd.random() * 2.2 + 0.6
        a = 0.35 + 0.4 * (0.5 + 0.5 * math.sin(f.t * 1.5 + rnd.random() * 6))
        c.arc(x, y, r, 0, 2 * math.pi)
        fill(c, (1, 1, 0.95), a)
    glow(c, W * 0.5, H * 0.55, 900, VIO, 0.18)


def bg_paper(f, tone=0):
    tops = ["#F6EEDC", "#EFE6F7", "#E7F1EA", "#F7E7DA"]
    bg(f, tops[tone % 4], "#E3D4B6")


def bg_dark(f):
    bg(f, "#120A16", "#2B1424")
    glow(f.ctx, W * 0.5, H * 0.5, 800, (0.6, 0.1, 0.2), 0.15)


def bg_room(f, night=False):
    c = f.ctx
    bg(f, "#5B3E5E" if night else "#E9D2AE", "#3D2A40" if night else "#D6B98E")
    f.ctx.rectangle(-2000, 760, 6000, 2000)
    fill(c, (0.45, 0.3, 0.22) if not night else (0.25, 0.17, 0.2))
    c.move_to(-2000, 760)
    c.line_to(4000, 760)
    stroke(c, 6)


# ----------------------------------------------------------------------------- camera variants
MOTIONS = ["push", "panr", "panl", "pull", "tiltu", "dutch", "drift", "tiltd", "snap"]


def cv(f, k, pts=((960, 540),), z=1.0, rng=None, wide=False):
    """camera variant k: picks a focus point and a move. Every shot gets a different framing."""
    px, py = pts[k % len(pts)]
    m = MOTIONS[(k * 5 + 3) % len(MOTIONS)]
    p = ease(f.p)
    tier = (k // len(pts)) % 3
    zz = z * (1.0 + (0.05 if wide else 0.15) * (tier == 1) + (0.09 if wide else 0.3) * (tier == 2))
    cx, cy, rot = px, py, 0.0
    if m == "push":
        zz *= lerp(1.0, 1.1, p)
    elif m == "pull":
        zz *= lerp(1.12, 1.0, p)
    elif m == "panr":
        cx += lerp(-70, 70, p) / zz
    elif m == "panl":
        cx += lerp(70, -70, p) / zz
    elif m == "tiltu":
        cy += lerp(50, -50, p) / zz
    elif m == "tiltd":
        cy += lerp(-50, 50, p) / zz
    elif m == "dutch":
        rot = 0.035 * (1 if k % 2 else -1)
        zz *= lerp(1.05, 1.1, p)
    elif m == "snap":
        zz *= 1.0 + 0.12 * (1 - ease_out(clamp(f.lt / 0.25)))
    else:
        cx += wob(f.t, 0.05, 20)
        cy += wob(f.t, 0.07, 12)
    # keep the frame inside a sensible region
    if zz <= 1.0001:
        cx, cy = lerp(960, cx, 0.35), lerp(540, cy, 0.35)
    f.cam(cx, cy, zz, rot)


# ----------------------------------------------------------------------------- characters
def you(c, x, y, s=1.0, expr="smile", arms="down", legs="stand", t=0.0, look=(0, 0), fd=0, hold=None, alpha=1.0, tint=None):
    cast.draw(c, "you", x, y, s, expr=expr, arms=arms, legs=legs, t=t, look=look, fd=fd, hold=hold, alpha=alpha, tint=tint)


def chest(x, y, s=1.0, who="you"):
    B = cast.BODY[cast.CAST[who]["body"]]
    return x + 16 * s, y - (B["leg"] + B["torso"] * 0.62) * s


def sam(c, x, y, s=1.0, expr="smile", t=0.0, look=(0, 0), rot=0.0, walk=0.0, a=1.0, shadow=True):
    """Sam the square (seen from above, the way we see Flatland)."""
    sz = 120
    bob = abs(math.sin(t * 7)) * 6 * walk
    c.save()
    c.translate(x, y - bob * s)
    c.rotate(rot)
    c.scale(s, s)
    if a < 1:
        c.push_group()
    if shadow:
        soft_shadow(c, 10, sz * 0.55, sz * 0.6, 14, 0.35)
    # feet
    for dx in (-30, 30):
        ph = math.sin(t * 7 + (0 if dx < 0 else math.pi)) * 8 * walk
        ellipse(c, dx + ph, sz * 0.5 + 6, 20, 11)
        fs(c, (0.35, 0.23, 0.15), 6)
    # sticker contour
    rrect(c, -sz / 2 - 7, -sz / 2 - 7, sz + 14, sz + 14, 26)
    fill(c, INK)
    rrect(c, -sz / 2, -sz / 2, sz, sz, 20)
    g = cairo.LinearGradient(-sz / 2, -sz / 2, sz / 2, sz / 2)
    g.add_color_stop_rgb(0, *shade(SAM_COL, 1.25))
    g.add_color_stop_rgb(0.55, *SAM_COL)
    g.add_color_stop_rgb(1, *shade(SAM_COL, 0.72))
    c.set_source(g)
    c.fill_preserve()
    stroke(c, 7)
    rrect(c, -sz / 2 + 12, -sz / 2 + 10, sz * 0.42, 14, 7)
    fill(c, (1, 1, 1), 0.45)
    # face
    c.save()
    c.translate(0, -6)
    cast.draw_face(c, SAM_FACE, 46, expr, look, 0, t)
    c.restore()
    if a < 1:
        c.pop_group_to_source()
        c.paint_with_alpha(a)
    c.restore()


def hand(c, x, y, s=1.0, rot=0.0, pinch=0.0, col=None, a=1.0):
    """big cartoon hand reaching DOWN (fingers at +y)."""
    col = col or SKIN
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    if a < 1:
        c.push_group()
    # arm / sleeve going up off-screen
    rrect(c, -55, -900, 110, 860, 40)
    fs(c, (0.36, 0.52, 0.85), 9)
    rrect(c, -62, -80, 124, 40, 16)
    fs(c, (0.9, 0.9, 0.95), 8)
    # palm
    rrect(c, -60, -45, 120, 110, 40)
    fs(c, col, 9)
    for i, dx in enumerate((-42, -14, 14, 42)):
        ln = 70 + (12 if i in (1, 2) else 0) - pinch * 20
        rrect(c, dx - 13, 40, 26, ln, 13)
        fs(c, col, 7)
    # thumb
    c.save()
    c.translate(-60, 10)
    c.rotate(0.9 - pinch * 0.6)
    rrect(c, -14, 0, 28, 66, 14)
    fs(c, col, 7)
    c.restore()
    if a < 1:
        c.pop_group_to_source()
        c.paint_with_alpha(a)
    c.restore()


def big_eye(c, x, y, s=1.0, t=0.0, look=(0, 0), col=VIO, open_=1.0, a=1.0):
    """the watcher: a huge almond eye."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    if a < 1:
        c.push_group()
    glow(c, 0, 0, 520, col, 0.35)
    blink = 1.0
    ph = (t % 5.3)
    if ph < 0.18:
        blink = abs(ph - 0.09) / 0.09
    op = max(0.04, open_ * blink)

    def almond(c):
        c.move_to(-300, 0)
        c.curve_to(-140, -190 * op, 140, -190 * op, 300, 0)
        c.curve_to(140, 190 * op, -140, 190 * op, -300, 0)
        c.close_path()
    almond(c)
    fill(c, INK)
    c.save()
    almond(c)
    c.clip()
    c.rectangle(-320, -220, 640, 440)
    g = cairo.RadialGradient(0, 0, 10, 0, 0, 320)
    g.add_color_stop_rgb(0, 0.98, 0.96, 1.0)
    g.add_color_stop_rgb(1, 0.72, 0.68, 0.85)
    c.set_source(g)
    c.fill()
    ix, iy = look[0] * 90 + wob(t, 0.13, 25), look[1] * 50 + wob(t, 0.09, 10)
    c.arc(ix, iy, 120, 0, 2 * math.pi)
    g = cairo.RadialGradient(ix, iy, 10, ix, iy, 120)
    g.add_color_stop_rgb(0, *shade(col, 1.4))
    g.add_color_stop_rgb(0.7, *col)
    g.add_color_stop_rgb(1, *shade(col, 0.5))
    c.set_source(g)
    c.fill()
    c.arc(ix, iy, 52, 0, 2 * math.pi)
    fill(c, (0.05, 0.03, 0.08))
    c.arc(ix - 38, iy - 40, 22, 0, 2 * math.pi)
    fill(c, (1, 1, 1), 0.9)
    c.restore()
    almond(c)
    stroke(c, 14)
    if a < 1:
        c.pop_group_to_source()
        c.paint_with_alpha(a)
    c.restore()


# ----------------------------------------------------------------------------- shapes / props
def heart(c, x, y, s=1.0, t=0.0, beat=True, a=1.0, col=HEART):
    k = 1 + (0.09 * max(0, math.sin(t * 7.5)) ** 8 if beat else 0)
    c.save()
    c.translate(x, y)
    c.scale(s * k, s * k)
    glow(c, 0, 0, 90, col, 0.35 * a)
    c.move_to(0, 38)
    c.curve_to(-70, -5, -45, -60, 0, -28)
    c.curve_to(45, -60, 70, -5, 0, 38)
    c.close_path()
    g = cairo.LinearGradient(-40, -40, 40, 40)
    g.add_color_stop_rgba(0, *shade(col, 1.3), a)
    g.add_color_stop_rgba(1, *shade(col, 0.7), a)
    c.set_source(g)
    c.fill_preserve()
    stroke(c, 6, INK, a)
    ellipse(c, -22, -24, 10, 6)
    fill(c, (1, 1, 1), 0.5 * a)
    c.restore()


def arrow(c, x0, y0, x1, y1, col=GOLD, w=18, a=1.0, head=40):
    ang = math.atan2(y1 - y0, x1 - x0)
    bx, by = x1 - math.cos(ang) * head * 0.8, y1 - math.sin(ang) * head * 0.8
    c.move_to(x0, y0)
    c.line_to(bx, by)
    stroke(c, w + 12, INK, a)
    c.move_to(x0, y0)
    c.line_to(bx, by)
    stroke(c, w, col, a)
    pts = [(x1, y1), (x1 - math.cos(ang - 0.5) * head, y1 - math.sin(ang - 0.5) * head),
           (x1 - math.cos(ang + 0.5) * head, y1 - math.sin(ang + 0.5) * head)]
    poly(c, pts)
    c.set_source_rgba(*rgb(col), a)
    c.fill_preserve()
    stroke(c, 6, INK, a)


def dashed_arrow(c, x0, y0, x1, y1, col=VIO, w=14, a=1.0, t=0.0):
    c.save()
    c.set_dash([30, 22], -t * 80)
    c.move_to(x0, y0)
    c.line_to(x1, y1)
    stroke(c, w, col, a)
    c.restore()
    c.arc(x1, y1, 18, 0, 2 * math.pi)
    c.set_source_rgba(*rgb(col), a)
    c.fill()


def qmark(f, x, y, size=200, t=None, col=VIO):
    text3d(f, "?", x, y, size, t=t, top=col, side=shade(col, 0.5))


def sphere(c, x, y, r, col=(0.5, 0.75, 1.0), a=1.0):
    if r < 1:
        return
    c.new_path()
    c.arc(x, y, r, 0, 2 * math.pi)
    g = cairo.RadialGradient(x - r * 0.35, y - r * 0.4, r * 0.05, x, y, r)
    g.add_color_stop_rgba(0, *shade(col, 1.5), a)
    g.add_color_stop_rgba(0.6, *col, a)
    g.add_color_stop_rgba(1, *shade(col, 0.55), a)
    c.set_source(g)
    c.fill_preserve()
    stroke(c, max(3, min(9, r * 0.08)), INK, a)


def box(c, x, y, w, h, d, col, open_=0.0, inside=None, ink=7):
    """cartoon 3/4 box; open_ 0..1 fades the front face to reveal 'inside(c)'."""
    top = [(x, y), (x + w, y), (x + w + d, y - d * 0.6), (x + d, y - d * 0.6)]
    side = [(x + w, y), (x + w + d, y - d * 0.6), (x + w + d, y + h - d * 0.6), (x + w, y + h)]
    soft_shadow(c, x + w / 2 + 20, y + h + 6, w * 0.7, 18, 0.35)
    poly(c, side)
    fs(c, shade(col, 0.7), ink)
    poly(c, top)
    fs(c, shade(col, 1.2), ink)
    if inside and open_ > 0:
        c.rectangle(x, y, w, h)
        fill(c, shade(col, 0.45))
        c.save()
        c.rectangle(x, y, w, h)
        c.clip()
        inside(c)
        c.restore()
    c.rectangle(x, y, w, h)
    c.set_source_rgba(*rgb(col), 1 - open_ * 0.88)
    c.fill_preserve()
    stroke(c, ink)


def cash(c, x, y, s=1.0):
    for i in range(3):
        rrect(c, x - 60 * s, y - i * 22 * s, 120 * s, 26 * s, 5)
        fs(c, (0.45, 0.78, 0.45), 4)
        c.arc(x, y - i * 22 * s + 13 * s, 8 * s, 0, 2 * math.pi)
        fill(c, (0.3, 0.55, 0.3))


def gold_bar(c, x, y, s=1.0):
    poly(c, [(x - 50 * s, y), (x + 50 * s, y), (x + 36 * s, y - 30 * s), (x - 36 * s, y - 30 * s)])
    fs(c, GOLD, 4)


def safe(c, x, y, s=1.0, see=0.0, t=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)

    def inside(c):
        cash(c, -60, 20, 0.9)
        cash(c, 70, 20, 0.9)
        gold_bar(c, 0, 90, 1.2)
        glow(c, 0, 0, 160, GOLD, 0.35)
    box(c, -170, -160, 340, 300, 70, (0.45, 0.5, 0.58), see, inside)
    if see < 0.5:
        c.arc(60, -10, 46, 0, 2 * math.pi)
        fs(c, (0.75, 0.78, 0.82), 6)
        for k in range(8):
            ang = k * math.pi / 4 + t
            c.move_to(60 + math.cos(ang) * 30, -10 + math.sin(ang) * 30)
            c.line_to(60 + math.cos(ang) * 42, -10 + math.sin(ang) * 42)
            stroke(c, 4)
        rrect(c, -130, -40, 26, 80, 8)
        fs(c, (0.3, 0.32, 0.38), 5)
    c.restore()


def padlock(c, x, y, s=1.0, open_=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.arc(0, -40 - open_ * 30, 38, math.pi, 2 * math.pi)
    stroke(c, 30)
    c.arc(0, -40 - open_ * 30, 38, math.pi, 2 * math.pi)
    stroke(c, 16, (0.7, 0.72, 0.78))
    rrect(c, -60, -40, 120, 100, 18)
    fs(c, GOLD, 8)
    c.arc(0, 0, 12, 0, 2 * math.pi)
    fill(c, INK)
    c.rectangle(-5, 0, 10, 26)
    fill(c, INK)
    c.restore()


def keys(c, x, y, s=1.0, rot=0.0):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    c.arc(0, 0, 26, 0, 2 * math.pi)
    stroke(c, 18)
    c.arc(0, 0, 26, 0, 2 * math.pi)
    stroke(c, 8, (0.8, 0.8, 0.85))
    for dx, col in ((30, GOLD), (40, (0.75, 0.78, 0.85))):
        c.save()
        c.rotate(0.5 if dx == 30 else -0.3)
        rrect(c, 20, -12, 40, 24, 10)
        fs(c, col, 5)
        c.rectangle(58, -5, 70, 10)
        fs(c, col, 4)
        for kx in (100, 116):
            c.rectangle(kx, 5, 8, 12)
            fs(c, col, 3)
        c.restore()
    c.restore()


def footprint(c, x, y, s=1.0, mirror=False, col=(0.35, 0.24, 0.18), a=1.0):
    c.save()
    c.translate(x, y)
    c.scale(-s if mirror else s, s)
    ellipse(c, 0, 30, 46, 70)
    c.set_source_rgba(*col, a)
    c.fill()
    ellipse(c, 6, -48, 34, 34)
    c.set_source_rgba(*col, a)
    c.fill()
    for i, (dx, dy, r) in enumerate(((-34, -92, 15), (-12, -106, 13), (10, -110, 12), (30, -104, 11), (46, -92, 10))):
        c.arc(dx, dy, r, 0, 2 * math.pi)
        c.set_source_rgba(*col, a)
        c.fill()
    c.restore()


def shoe(c, x, y, s=1.0, knot=1.0, t=0.0):
    """side view sneaker; knot 1=tied bow, 0=laces loose."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    soft_shadow(c, 0, 70, 260, 26, 0.4)
    c.move_to(-240, 60)
    c.curve_to(-250, -40, -150, -90, -60, -100)
    c.line_to(40, -40)
    c.curve_to(150, -20, 250, 0, 250, 60)
    c.close_path()
    fs(c, (0.9, 0.3, 0.3), 9)
    rrect(c, -255, 40, 515, 40, 18)
    fs(c, (0.97, 0.97, 0.97), 8)
    for i in range(4):
        lx, ly = -110 + i * 38, -84 + i * 16
        c.arc(lx, ly, 7, 0, 2 * math.pi)
        fill(c, INK)
    # bow / loose laces
    bx, by = -20, -70
    if knot > 0.02:
        for sgn in (-1, 1):
            c.save()
            c.translate(bx, by)
            c.rotate(sgn * (0.6 + 0.2 * knot))
            ellipse(c, sgn * 50 * knot, -10, 50 * knot, 22 * knot)
            stroke(c, 16)
            ellipse(c, sgn * 50 * knot, -10, 50 * knot, 22 * knot)
            stroke(c, 8, (1, 1, 1))
            c.restore()
    for sgn in (-1, 1):
        sway = wob(t, 0.8, 10, 0.3 * sgn)
        c.move_to(bx, by)
        c.curve_to(bx + sgn * 40, by + 40, bx + sgn * (60 + (1 - knot) * 60) + sway, by + 60, bx + sgn * (40 + (1 - knot) * 90) + sway, by + 120 + (1 - knot) * 40)
        stroke(c, 16)
        c.move_to(bx, by)
        c.curve_to(bx + sgn * 40, by + 40, bx + sgn * (60 + (1 - knot) * 60) + sway, by + 60, bx + sgn * (40 + (1 - knot) * 90) + sway, by + 120 + (1 - knot) * 40)
        stroke(c, 8, (1, 1, 1))
    c.arc(bx, by, 14 * max(knot, 0.3), 0, 2 * math.pi)
    fs(c, (1, 1, 1), 6)
    c.restore()


def rope_knot(c, x, y, s=1.0, loose=0.0, t=0.0, col=(0.85, 0.65, 0.35)):
    """a rope with a real loop-knot that pulls straight as loose -> 1."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    k = 1 - ease(loose)
    pts = []
    for i in range(161):
        u = i / 160
        px, py = lerp(-460, 460, u), wob(t, 0.3, 5, u * 2)
        if 0.3 < u < 0.7:
            a = (u - 0.3) / 0.4 * 2 * math.pi
            r = 130 * k
            px += r * math.sin(a) * 1.25
            py += -r * (1 - math.cos(a)) * 0.9
        pts.append((px, py))

    def path(a0, a1):
        c.move_to(*pts[a0])
        for p in pts[a0 + 1:a1 + 1]:
            c.line_to(*p)
    for w, cc in ((44, INK), (28, col)):
        path(0, 160)
        stroke(c, w, cc)
    # over-crossing piece redrawn on top so it reads as a knot
    if k > 0.1:
        for w, cc in ((44, INK), (28, shade(col, 1.12))):
            path(36, 52)
            stroke(c, w, cc)
    c.restore()


def book(c, x, y, s=1.0, open_=0.0, title="FLATLAND", sub="1884"):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    soft_shadow(c, 20, 150, 260, 26, 0.4)
    if open_ < 0.5:
        rrect(c, -170, -220, 340, 380, 14)
        fs(c, (0.55, 0.2, 0.25), 9)
        rrect(c, -150, -200, 300, 340, 10)
        stroke(c, 5, GOLD)
        _font(c, 52)
        e = c.text_extents(title)
        c.move_to(-e.x_advance / 2, -60)
        c.set_source_rgb(*GOLD)
        c.show_text(title)
        _font(c, 40)
        e = c.text_extents(sub)
        c.move_to(-e.x_advance / 2, 40)
        c.show_text(sub)
        rrect(c, -120, 80, 240, 4, 2)
        fill(c, GOLD)
    else:
        for sgn in (-1, 1):
            poly(c, [(0, -170), (sgn * 330, -200), (sgn * 330, 150), (0, 170)])
            fs(c, PAPER, 8)
            for i in range(7):
                c.move_to(sgn * 40, -120 + i * 34)
                c.line_to(sgn * (290 - (i % 3) * 30), -140 + i * 34)
                stroke(c, 4, (0.6, 0.55, 0.5))
        # tiny square + lines drawing on the right page
        rrect(c, 110, -40, 70, 70, 10)
        fs(c, SAM_COL, 5)
        poly(c, [(-260, 40), (-120, 10), (-90, 90), (-230, 110)])
        stroke(c, 5)
    c.restore()


def chalkboard(c, x, y, w, h):
    rrect(c, x - w / 2 - 18, y - h / 2 - 18, w + 36, h + 36, 14)
    fs(c, (0.55, 0.35, 0.2), 9)
    rrect(c, x - w / 2, y - h / 2, w, h, 8)
    fs(c, (0.16, 0.3, 0.26), 6)


def chalk(c, s, x, y, size=70, col=(0.95, 0.95, 0.9), reveal=1.0):
    _font(c, size)
    e = c.text_extents(s)
    c.save()
    c.rectangle(x - e.x_advance / 2 - 10, y - size, (e.x_advance + 20) * clamp(reveal), size * 2)
    c.clip()
    c.move_to(x - e.x_advance / 2, y + size * 0.35)
    c.set_source_rgba(*col, 0.95)
    c.show_text(s)
    c.restore()


def bubble(c, x, y, w, h, tail=(-1, 1), col=(1, 1, 1)):
    rrect(c, x - w / 2, y - h / 2, w, h, 30)
    fs(c, col, 8)
    poly(c, [(x + tail[0] * 40, y + h / 2 - 4), (x + tail[0] * 90, y + h / 2 + 60), (x + tail[0] * 100, y + h / 2 - 4)])
    fs(c, col, 8)
    rrect(c, x + tail[0] * 30 - 5, y + h / 2 - 12, 90, 14, 4)
    fill(c, col)


def tag(c, s, x, y, size=46, col=GOLD, txt=INK):
    _font(c, size)
    e = c.text_extents(s)
    rrect(c, x - e.x_advance / 2 - 26, y - size * 0.75, e.x_advance + 52, size * 1.45, 18)
    fs(c, col, 7)
    c.move_to(x - e.x_advance / 2, y + size * 0.35)
    c.set_source_rgb(*rgb(txt))
    c.show_text(s)


# ----------------------------------------------------------------------------- 4D maths
def _rot(p, i, j, a):
    p = list(p)
    ca, sa = math.cos(a), math.sin(a)
    p[i], p[j] = p[i] * ca - p[j] * sa, p[i] * sa + p[j] * ca
    return p


TESS_V = [(x, y, z, w) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1) for w in (-1, 1)]
TESS_E = [(a, b) for a in range(16) for b in range(a + 1, 16)
          if sum(1 for u, v in zip(TESS_V[a], TESS_V[b]) if u != v) == 1]


def tesseract(c, x, y, s, t, col=NEON, a=1.0, speed=0.5, w_dist=3.0):
    """true 4D rotation (XW + ZW + XY) projected 4D->3D->2D."""
    pts = []
    for v in TESS_V:
        p = _rot(v, 0, 3, t * speed)
        p = _rot(p, 2, 3, t * speed * 0.7)
        p = _rot(p, 0, 1, t * speed * 0.25)
        k = 1 / (w_dist - p[3])
        q = [p[0] * k, p[1] * k, p[2] * k]
        q = _rot(q, 1, 2, 0.45)
        k2 = 1 / (3.2 - q[2])
        pts.append((x + q[0] * k2 * s * 3, y + q[1] * k2 * s * 3, q[2]))
    glow(c, x, y, s * 1.6, col, 0.25 * a)
    for (i, j) in sorted(TESS_E, key=lambda e: pts[e[0]][2] + pts[e[1]][2]):
        dep = (pts[i][2] + pts[j][2]) / 2
        wv = 6 + dep * 4
        c.move_to(pts[i][0], pts[i][1])
        c.line_to(pts[j][0], pts[j][1])
        stroke(c, max(3, wv) + 8, INK, a)
        c.move_to(pts[i][0], pts[i][1])
        c.line_to(pts[j][0], pts[j][1])
        stroke(c, max(2, wv), shade(col, 0.8 + 0.3 * dep), a)
    for px, py, pz in pts:
        c.arc(px, py, 7 + pz * 2, 0, 2 * math.pi)
        fill(c, (1, 1, 1), 0.85 * a)


def cube(c, x, y, s, t, col=GOLD, a=1.0):
    V = [(i, j, k) for i in (-1, 1) for j in (-1, 1) for k in (-1, 1)]
    E = [(p, q) for p in range(8) for q in range(p + 1, 8) if sum(1 for u, v in zip(V[p], V[q]) if u != v) == 1]
    pts = []
    for v in V:
        p = _rot(v, 0, 2, t * 0.6)
        p = _rot(p, 1, 2, 0.5)
        k = 1 / (4 - p[2])
        pts.append((x + p[0] * k * s * 3, y + p[1] * k * s * 3))
    for i, j in E:
        c.move_to(*pts[i])
        c.line_to(*pts[j])
        stroke(c, 18, INK, a)
        c.move_to(*pts[i])
        c.line_to(*pts[j])
        stroke(c, 9, col, a)


# ----------------------------------------------------------------------------- Flatland plane
def plane_begin(c, cx, cy, tilt=0.42, skew=0.0):
    """enter Flatland coordinates: a sheet seen at an angle (tilt=1 straight down)."""
    c.save()
    c.translate(cx, cy)
    c.transform(cairo.Matrix(1, 0, skew, tilt, 0, 0))


def sheet(c, w=1600, h=1100, col=PAPER, grid=True):
    rrect(c, -w / 2 - 12, -h / 2 - 12, w + 24, h + 24, 30)
    fill(c, INK)
    rrect(c, -w / 2, -h / 2, w, h, 24)
    g = cairo.LinearGradient(-w / 2, -h / 2, w / 2, h / 2)
    g.add_color_stop_rgb(0, *shade(col, 1.05))
    g.add_color_stop_rgb(1, *shade(col, 0.88))
    c.set_source(g)
    c.fill()
    if grid:
        for gx in range(-w // 2 + 100, w // 2, 100):
            c.move_to(gx, -h / 2)
            c.line_to(gx, h / 2)
        for gy in range(-h // 2 + 100, h // 2, 100):
            c.move_to(-w / 2, gy)
            c.line_to(w / 2, gy)
        stroke(c, 2, (0.75, 0.68, 0.55), 0.5)


def flat_house(c, x, y, s=1.0, door=1.0, col=(0.45, 0.35, 0.7)):
    """Sam's house: a pentagon outline. door: 1 open gap, 0 closed."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    pts = [(-200, 150), (-200, -80), (0, -220), (200, -80), (200, 150)]
    c.move_to(-60 * door, 150)
    for p in reversed(pts):
        pass
    c.move_to(-60 * door - 0.01, 150)
    c.line_to(*pts[0])
    c.line_to(*pts[1])
    c.line_to(*pts[2])
    c.line_to(*pts[3])
    c.line_to(*pts[4])
    c.line_to(60 * door + 0.01, 150)
    stroke(c, 26)
    c.move_to(-60 * door - 0.01, 150)
    for p in pts:
        c.line_to(*p)
    c.line_to(60 * door + 0.01, 150)
    stroke(c, 14, col)
    if door < 1:
        c.move_to(-60, 150)
        c.line_to(-60 + 120 * (1 - door), 150)
        stroke(c, 26)
        c.move_to(-60, 150)
        c.line_to(-60 + 120 * (1 - door), 150)
        stroke(c, 14, (0.85, 0.3, 0.3))
    c.restore()


def flat_tree(c, x, y, s=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.arc(0, 0, 70, 0, 2 * math.pi)
    fs(c, (0.4, 0.7, 0.35), 8)
    c.arc(-20, -18, 24, 0, 2 * math.pi)
    fill(c, (0.55, 0.82, 0.45))
    c.restore()


def flat_circle(c, x, y, r, col=(0.4, 0.6, 0.95)):
    c.arc(x, y, r, 0, 2 * math.pi)
    fs(c, col, 7)


def edge_view(c, x0, x1, y, segs, t=0.0, h=60):
    """what Sam sees: a 1D strip of shaded segments."""
    rrect(c, x0 - 16, y - h / 2 - 16, x1 - x0 + 32, h + 32, 20)
    fs(c, (0.15, 0.12, 0.2), 8)
    for (u0, u1, col) in segs:
        c.rectangle(lerp(x0, x1, u0), y - h / 2, lerp(x0, x1, u1) - lerp(x0, x1, u0), h)
        fill(c, col)
    c.rectangle(x0, y - h / 2, x1 - x0, h)
    stroke(c, 5)


# ----------------------------------------------------------------------------- bigger set pieces
def dollhouse(c, x, y, s=1.0, reveal=1.0, t=0.0, keys_on=False, flower=0.0):
    """house with the front wall removed (reveal) / walls folded open like petals (flower)."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    soft_shadow(c, 0, 10, 560, 40, 0.4)
    wall = (0.96, 0.86, 0.66)
    rooms = [(-450, -460, (0.95, 0.75, 0.6)), (-150, -460, (0.7, 0.82, 0.95)), (150, -460, (0.8, 0.9, 0.7)),
             (-450, -230, (0.9, 0.8, 0.95)), (-150, -230, (0.98, 0.9, 0.6)), (150, -230, (0.75, 0.88, 0.85))]
    # roof
    if flower < 0.98:
        c.save()
        c.translate(0, -470)
        c.rotate(-flower * 0.9)
        c.translate(0, -flower * 140)
        poly(c, [(-500, 10), (0, -240), (500, 10)])
        fs(c, (0.78, 0.33, 0.28), 9)
        c.restore()
    for i, (rx, ry, col) in enumerate(rooms):
        dx = (rx + 150) * flower * 0.25
        dy = (ry + 230) * flower * 0.25
        c.rectangle(rx + dx, ry + dy, 300, 230)
        fs(c, col, 8)
        fy = ry + dy + 230
        c.rectangle(rx + dx, fy - 30, 300, 30)
        fs(c, (0.55, 0.38, 0.26), 5)
        X = rx + dx
        if i == 0:  # bedroom
            rrect(c, X + 40, fy - 100, 170, 70, 14)
            fs(c, (0.4, 0.55, 0.9), 6)
            rrect(c, X + 40, fy - 120, 60, 30, 10)
            fs(c, (1, 1, 1), 5)
        if i == 1:  # bathroom
            rrect(c, X + 60, fy - 100, 180, 70, 30)
            fs(c, (1, 1, 1), 6)
        if i == 2:  # study: lamp + desk
            c.rectangle(X + 60, fy - 110, 180, 20)
            fs(c, (0.6, 0.4, 0.25), 5)
            glow(c, X + 220, fy - 160, 70, (1, 0.85, 0.4), 0.5)
        if i == 3:  # living: sofa + tv
            rrect(c, X + 40, fy - 110, 200, 80, 18)
            fs(c, (0.85, 0.4, 0.4), 6)
        if i == 4:  # kitchen: counter (+ keys)
            c.rectangle(X + 30, fy - 120, 240, 90)
            fs(c, (0.95, 0.95, 0.95), 6)
            c.rectangle(X + 30, fy - 130, 240, 16)
            fs(c, (0.5, 0.5, 0.55), 5)
            if keys_on:
                glow(c, X + 150, fy - 150, 60, GOLD, 0.6)
                keys(c, X + 150, fy - 150, 0.45, 0.3)
        if i == 5:  # hallway: door
            rrect(c, X + 110, fy - 190, 90, 160, 8)
            fs(c, (0.55, 0.35, 0.22), 6)
            c.arc(X + 185, fy - 110, 7, 0, 2 * math.pi)
            fill(c, GOLD)
    if reveal < 1:
        c.rectangle(-450, -460, 900, 460)
        c.set_source_rgba(*wall, 1 - reveal)
        c.fill_preserve()
        stroke(c, 9, INK, 1 - reveal)
        for wx in (-330, -30, 270):
            for wy in (-400, -170):
                c.rectangle(wx, wy, 90, 90)
                c.set_source_rgba(0.6, 0.8, 0.95, 1 - reveal)
                c.fill_preserve()
                stroke(c, 6, INK, 1 - reveal)
    c.restore()


def eye_section(c, x, y, s=1.0, t=0.0, rays=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    # object (a little tree) on the left
    c.save()
    c.translate(-620, 0)
    c.rectangle(-14, -10, 28, 120)
    fs(c, (0.55, 0.36, 0.2), 6)
    c.arc(0, -60, 70, 0, 2 * math.pi)
    fs(c, (0.4, 0.75, 0.35), 8)
    c.restore()
    # rays
    if rays > 0:
        for (oy, iy) in ((-130, 120), (110, -95)):
            c.move_to(-620, oy)
            c.line_to(-250, 0)
            c.line_to(lerp(-250, 230, rays), lerp(0, iy, rays))
            stroke(c, 6, (1, 0.9, 0.4), 0.9)
    # eyeball
    c.arc(0, 0, 260, 0, 2 * math.pi)
    g = cairo.RadialGradient(-80, -80, 20, 0, 0, 260)
    g.add_color_stop_rgb(0, 1, 1, 1)
    g.add_color_stop_rgb(1, 0.85, 0.82, 0.9)
    c.set_source(g)
    c.fill_preserve()
    stroke(c, 10)
    # retina (back wall)
    c.arc(0, 0, 238, -0.9, 0.9)
    stroke(c, 26, (0.95, 0.4, 0.45))
    # lens
    ellipse(c, -250, 0, 30, 90)
    fs(c, (0.65, 0.85, 1.0), 7)
    # upside-down image on retina
    c.save()
    c.translate(225, 0)
    c.scale(0.45, -0.45)
    c.rectangle(-14, -10, 28, 120)
    fs(c, (0.55, 0.36, 0.2), 5)
    c.arc(0, -60, 70, 0, 2 * math.pi)
    fs(c, (0.4, 0.75, 0.35), 6)
    c.restore()
    c.restore()


def retina_ladder(c, x, y, s=1.0, hi=0, t=0.0):
    """1D line -> 2D sheet -> 3D block."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    for i, cx in enumerate((-560, 0, 560)):
        a = 1.0 if i <= hi else 0.25
        if i == 0:
            for k in range(9):
                c.arc(cx - 160 + k * 40, 0, 15, 0, 2 * math.pi)
                fill(c, (0.95, 0.4, 0.45), a)
            c.move_to(cx - 180, 0)
            c.line_to(cx + 180, 0)
            stroke(c, 4, INK, a)
        elif i == 1:
            c.save()
            c.translate(cx, 0)
            c.transform(cairo.Matrix(1, 0, -0.5, 0.55, 0, 0))
            for gx in range(7):
                for gy in range(7):
                    c.arc(-150 + gx * 50, -150 + gy * 50, 14, 0, 2 * math.pi)
                    fill(c, (0.95, 0.4, 0.45), a)
            rrect(c, -180, -180, 360, 360, 14)
            stroke(c, 6, INK, a)
            c.restore()
        else:
            for gz in range(5):
                c.save()
                c.translate(cx - gz * 22, -gz * 34 + 60)
                c.transform(cairo.Matrix(1, 0, -0.5, 0.55, 0, 0))
                for gx in range(5):
                    for gy in range(5):
                        c.arc(-110 + gx * 55, -110 + gy * 55, 13, 0, 2 * math.pi)
                        fill(c, shade((0.95, 0.4, 0.45), 0.7 + gz * 0.08), a)
                rrect(c, -140, -140, 280, 280, 12)
                stroke(c, 4, INK, a * 0.6)
                c.restore()
        _font(c, 54)
        lab = ["1D", "2D", "3D"][i]
        e = c.text_extents(lab)
        c.move_to(cx - e.x_advance / 2, 270)
        c.set_source_rgba(1, 1, 1, a)
        c.show_text(lab)
    c.restore()


def person_layers(c, x, y, s=1.0, t=0.0, layer=3, xr=False):
    """skin -> muscle -> bones -> heart, drawn at once (4D sight)."""
    you(c, x, y, s, expr="surprise", t=t, alpha=0.35 if layer > 0 else 1.0)
    hx, hy = chest(x, y, s)
    c.save()
    if layer >= 1:  # muscle
        ellipse(c, x, hy + 10 * s, 52 * s, 80 * s)
        c.set_source_rgba(0.9, 0.45, 0.45, 0.45)
        c.fill()
    if layer >= 2:  # ribs
        for k in range(5):
            ellipse(c, x, hy - 30 * s + k * 18 * s, 44 * s, 10 * s)
            stroke(c, 5 * s, (0.98, 0.96, 0.9), 0.95)
        c.move_to(x, hy - 50 * s)
        c.line_to(x, hy + 80 * s)
        stroke(c, 8 * s, (0.98, 0.96, 0.9))
    if layer >= 3:
        heart(c, hx, hy, 0.42 * s, t)
    c.restore()


def solar(c, x, y, s=1.0, t=0.0, mode="stable", p=0.0, jup=False):
    """mode: stable / wobble / spiral / escape."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    glow(c, 0, 0, 260, (1, 0.7, 0.2), 0.6)
    c.arc(0, 0, 90, 0, 2 * math.pi)
    g = cairo.RadialGradient(-25, -25, 5, 0, 0, 90)
    g.add_color_stop_rgb(0, 1, 0.98, 0.7)
    g.add_color_stop_rgb(1, 1, 0.6, 0.15)
    c.set_source(g)
    c.fill_preserve()
    stroke(c, 8)
    R = 330
    c.save()
    c.scale(1, 0.55)
    c.arc(0, 0, R, 0, 2 * math.pi)
    c.restore()
    c.save()
    c.set_dash([16, 14])
    stroke(c, 4, (1, 1, 1), 0.4)
    c.restore()
    if jup:
        jx, jy = 640 * math.cos(t * 0.3 + 2), 640 * 0.55 * math.sin(t * 0.3 + 2)
        sphere(c, jx, jy, 60, (0.9, 0.7, 0.5))
    ang = t * 1.4
    if mode == "stable":
        r = R
    elif mode == "wobble":
        r = R * (1 + 0.08 * math.sin(t * 3) * (1 - p))
    elif mode == "spiral":
        r = R * (1 - 0.82 * ease(p))
        ang = t * 1.4 + p * 9
    else:
        r = R * (1 + 2.6 * ease(p) ** 1.5)
    ex, ey = r * math.cos(ang), r * 0.55 * math.sin(ang)
    # trail
    for k in range(18):
        tt = k * 0.06
        a2 = ang - tt * 1.4
        rr = r if mode in ("stable", "wobble") else (r + (R - r) * tt * 0.4 if mode == "spiral" else r - (r - R) * tt * 0.4)
        c.arc(rr * math.cos(a2), rr * 0.55 * math.sin(a2), 14 - k * 0.6, 0, 2 * math.pi)
        fill(c, (0.5, 0.75, 1.0), 0.35 * (1 - k / 18))
    sphere(c, ex, ey, 46, (0.35, 0.6, 0.95))
    c.arc(ex - 10, ey - 8, 16, 0, 2 * math.pi)
    fill(c, (0.4, 0.8, 0.4))
    c.restore()


def atom(c, x, y, s=1.0, t=0.0, collapse=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    for k, (dx, dy, col) in enumerate(((-14, -10, (0.9, 0.3, 0.3)), (14, -8, (0.4, 0.5, 0.95)), (0, 14, (0.9, 0.3, 0.3)),
                                       (-16, 12, (0.4, 0.5, 0.95)), (16, 14, (0.9, 0.3, 0.3)))):
        sphere(c, dx, dy, 20, col)
    for k in range(3):
        c.save()
        c.rotate(k * math.pi / 3)
        c.scale(1, 0.35)
        c.arc(0, 0, 280, 0, 2 * math.pi)
        c.restore()
        stroke(c, 4, (0.7, 0.85, 1.0), 0.5 * (1 - collapse))
    r = 280 * (1 - 0.92 * ease(collapse))
    for k in range(3):
        ang = t * (3 + collapse * 8) + k * 2.1
        ex, ey = r * math.cos(ang), r * 0.35 * math.sin(ang)
        ex, ey = ex * math.cos(k * math.pi / 3) - ey * math.sin(k * math.pi / 3), ex * math.sin(k * math.pi / 3) + ey * math.cos(k * math.pi / 3)
        glow(c, ex, ey, 40, NEON, 0.5)
        sphere(c, ex, ey, 16, NEON)
    c.restore()


def molecule_hand(c, x, y, s=1.0, mirror=False, col=(0.55, 0.85, 0.6)):
    """a 'handed' molecule drawn as a cartoon hand-shaped cluster (L vs R)."""
    c.save()
    c.translate(x, y)
    c.scale(-s if mirror else s, s)
    for (dx, dy, r, cc) in ((0, 0, 50, (0.3, 0.3, 0.35)), (-80, -60, 32, (0.95, 0.95, 0.95)), (90, -40, 36, (0.9, 0.3, 0.3)),
                            (-30, 90, 34, (0.4, 0.55, 0.95)), (70, 70, 26, (0.95, 0.95, 0.95))):
        c.move_to(0, 0)
        c.line_to(dx, dy)
        stroke(c, 12)
        sphere(c, dx, dy, r, cc)
    c.restore()


def plate(c, x, y, s=1.0, gray=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    soft_shadow(c, 10, 30, 220, 30, 0.4)
    ellipse(c, 0, 0, 220, 70)
    fs(c, (0.97, 0.97, 0.97), 8)
    for (dx, dy, r, col) in ((-70, -10, 45, (0.95, 0.75, 0.3)), (40, -14, 40, (0.4, 0.75, 0.35)), (0, 18, 38, (0.85, 0.35, 0.3))):
        cc = mix(col, (0.55, 0.55, 0.55), gray)
        ellipse(c, dx, dy, r, r * 0.6)
        fs(c, cc, 6)
    c.restore()


def chain_icons(f, items, y=540, hi=99, t0=0.0):
    """row of 3D words joined by arrows."""
    c = f.ctx
    n = len(items)
    xs = [lerp(300, 1620, i / max(1, n - 1)) for i in range(n)]
    for i, s in enumerate(items):
        if i:
            arrow(c, xs[i - 1] + 150, y, xs[i] - 150, y, (1, 1, 1), 12, 0.85 if i <= hi else 0.25, 34)
        text3d(f, s, xs[i], y, 76, t=f.lt - t0 - i * 0.18, max_w=300,
               top=GOLD if i <= hi else (0.6, 0.6, 0.65), alpha=1.0 if i <= hi else 0.5)
