"""Stickman character cards following the pack's Style DNA:
big round off-white head (#FBF5EA) with thick ink outline, violet core shadow lower-right,
glossy cartoon eyes, tapered brows, tiny hooked nose, blush; trapezoid garment with 3-tone
shading, gold-buckle belt, trim band; stick limbs with round caps, round hands, brown oval
shoes; hat/hair defines the character; sticker outer contour; violet drop shadow.
"""
import math
import cairo
from engine import (INK, rgb, shade, mix, fill, stroke, fs, ellipse, poly, rrect, soft_shadow, clamp, wob, lerp)

SKIN = rgb("#FBF5EA")
VIOLET = (0.55, 0.42, 0.78)
SHOE = rgb("#5A3A22")

BODY = {
    "adult": dict(leg=70, torso=118, sh=34, hem=62, head=66),
    "tall": dict(leg=94, torso=134, sh=34, hem=60, head=64),
    "thin": dict(leg=76, torso=122, sh=28, hem=50, head=64),
    "heavy": dict(leg=64, torso=122, sh=46, hem=88, head=68),
    "kid": dict(leg=44, torso=78, sh=25, hem=44, head=62),
    "elder": dict(leg=62, torso=110, sh=32, hem=60, head=64),
}

CAST = {
    # potato king
    "king": dict(body="heavy", outfit="robe", tunic=(170, 35, 60), trim=(250, 205, 70), hat="crown", hatc=(250, 200, 60), face="beard", hairc=(120, 80, 50), extras=["cape"], iris=(70, 110, 190)),
    "guard": dict(body="adult", outfit="armor", tunic=(70, 95, 150), trim=(200, 205, 215), hat="helmet", hatc=(170, 178, 190), face="plain", iris=(80, 60, 40)),
    "farmer": dict(body="adult", outfit="tunic", tunic=(115, 145, 70), trim=(160, 110, 60), hat="straw", hatc=(235, 200, 110), face="stache", hairc=(110, 70, 40), iris=(90, 70, 40)),
    "n1": dict(body="adult", outfit="tunic", tunic=(200, 120, 60), trim=(120, 70, 40), hat="hair", hatc=(70, 45, 30), face="plain", iris=(70, 60, 40)),
    "n2": dict(body="thin", outfit="dress", tunic=(110, 160, 200), trim=(250, 250, 240), hat="bun", hatc=(150, 90, 50), face="lady", iris=(60, 120, 90)),
    "n3": dict(body="heavy", outfit="tunic", tunic=(150, 110, 170), trim=(240, 220, 160), hat="cap", hatc=(90, 70, 60), face="beard", hairc=(80, 55, 35), iris=(80, 60, 40)),
    "n4": dict(body="adult", outfit="dress", tunic=(220, 150, 170), trim=(255, 255, 255), hat="scarf", hatc=(240, 200, 90), face="lady", iris=(70, 100, 160)),
    "kid": dict(body="kid", outfit="tunic", tunic=(250, 160, 40), trim=(200, 80, 40), hat="hair", hatc=(230, 170, 70), face="kid", iris=(60, 110, 200)),
    "granny": dict(body="elder", outfit="dress", tunic=(160, 130, 200), trim=(250, 245, 230), hat="bun", hatc=(225, 225, 230), face="glasses", iris=(90, 90, 120)),
    "worker": dict(body="adult", outfit="apron", tunic=(150, 110, 80), trim=(240, 235, 220), hat="cap", hatc=(110, 90, 70), face="stache", hairc=(60, 40, 30), iris=(80, 60, 40)),
    # coin ridges
    "merchant": dict(body="adult", outfit="tunic", tunic=(120, 50, 120), trim=(240, 190, 70), hat="beret", hatc=(60, 30, 70), face="stache", hairc=(40, 30, 30), iris=(60, 140, 90)),
    "vendor": dict(body="heavy", outfit="apron", tunic=(70, 140, 90), trim=(250, 245, 235), hat="scarf", hatc=(200, 70, 60), face="lady", iris=(90, 70, 40)),
    "newton": dict(body="tall", outfit="robe", tunic=(50, 50, 70), trim=(230, 230, 240), hat="long", hatc=(235, 235, 240), face="glasses", iris=(70, 90, 140)),
    "newton_hood": dict(body="tall", outfit="robe", tunic=(80, 60, 45), trim=(120, 95, 70), hat="hood", hatc=(85, 62, 45), face="stache", hairc=(30, 25, 25), iris=(70, 90, 140)),
    "minter": dict(body="heavy", outfit="apron", tunic=(90, 90, 110), trim=(220, 215, 205), hat="cap", hatc=(60, 60, 70), face="beard", hairc=(90, 60, 40), iris=(80, 60, 40)),
    "customer": dict(body="adult", outfit="tunic", tunic=(80, 150, 180), trim=(240, 230, 200), hat="hair", hatc=(120, 70, 40), face="plain", iris=(70, 60, 40)),
    # convict ships
    "captain": dict(body="heavy", outfit="tunic", tunic=(30, 50, 100), trim=(250, 200, 40), hat="tricorn", hatc=(20, 20, 30), face="stache", hairc=(50, 35, 30), extras=["sash"], sash=(180, 30, 40), iris=(60, 60, 70)),
    "prisoner": dict(body="thin", outfit="tunic", tunic=(150, 150, 150), trim=(100, 100, 100), hat="hair", hatc=(60, 45, 40), face="plain", iris=(80, 70, 50)),
    "prisoner2": dict(body="adult", outfit="tunic", tunic=(135, 135, 140), trim=(95, 95, 100), hat="cap", hatc=(90, 90, 95), face="beard", hairc=(70, 50, 40), iris=(60, 90, 120)),
    "prisoner3": dict(body="thin", outfit="dress", tunic=(145, 140, 135), trim=(100, 95, 90), hat="scarf", hatc=(120, 115, 110), face="lady", iris=(70, 110, 90)),
    "doctor": dict(body="thin", outfit="robe", tunic=(240, 240, 245), trim=(60, 120, 200), hat="cap", hatc=(250, 250, 250), face="glasses", extras=["satchel"], iris=(70, 110, 160)),
    "official": dict(body="adult", outfit="robe", tunic=(40, 90, 70), trim=(240, 230, 200), hat="wig", hatc=(245, 245, 245), face="plain", iris=(70, 60, 50)),
}

EXPR = {
    #          brow lift, brow angle(+ angry), eyes, mouth
    "smile": (0.0, 0.0, "open", "smile"),
    "happy": (0.4, -0.2, "closed", "grin"),
    "laugh": (0.6, -0.3, "closed", "laugh"),
    "smug": (0.2, 0.25, "half", "smirk"),
    "sly": (0.0, 0.45, "half", "smirk"),
    "shock": (1.2, -0.5, "wide", "O"),
    "surprise": (0.9, -0.3, "wide", "o"),
    "sad": (0.3, -0.8, "open", "frown"),
    "worried": (0.4, -0.7, "open", "wavy"),
    "angry": (-0.3, 1.0, "half", "grit"),
    "disgust": (-0.1, 0.7, "squint", "sneer"),
    "flat": (-0.1, 0.0, "half", "flat"),
    "whisper": (0.3, -0.2, "open", "o"),
    "tired": (0.0, -0.4, "half", "frown"),
    "wink": (0.3, 0.0, "wink", "grin"),
    "doubt": (0.2, 0.5, "half", "flat"),
    "determined": (-0.1, 0.6, "open", "smirk"),
}


class Painter:
    """two passes: mode 0 = fat ink sticker contour, mode 1 = paint."""

    def __init__(self, c, mode, sticker=13):
        self.c, self.mode, self.k = c, mode, sticker

    def shape(self, build, col, w=6, a=1.0):
        c = self.c
        build(c)
        if self.mode == 0:
            stroke(c, w + self.k, INK, a)
        else:
            c.set_source_rgba(*rgb(col), a)
            c.fill_preserve()
            stroke(c, w, INK, a)

    def line(self, pts, w, col=INK, hl=True, a=1.0):
        c = self.c
        c.move_to(*pts[0])
        if len(pts) == 3:
            c.curve_to(*pts[1], *pts[1], *pts[2])
        else:
            for p in pts[1:]:
                c.line_to(*p)
        if self.mode == 0:
            stroke(c, w + self.k, INK, a)
        else:
            stroke(c, w, col, a)
            if hl:
                c.move_to(pts[0][0] - 1.5, pts[0][1] - 1.5)
                if len(pts) == 3:
                    c.curve_to(pts[1][0] - 1.5, pts[1][1] - 1.5, pts[1][0] - 1.5, pts[1][1] - 1.5, pts[2][0] - 1.5, pts[2][1] - 1.5)
                else:
                    for p in pts[1:]:
                        c.line_to(p[0] - 1.5, p[1] - 1.5)
                stroke(c, w * 0.22, (0.55, 0.55, 0.6), 0.55 * a)


# ----------------------------------------------------------------------------- limbs
def leg_pose(legs, t, dirx):
    """returns (lfoot, rfoot, lift_l, lift_r, bob, lean)."""
    if legs in ("walk", "run", "tiptoe", "march"):
        hz = {"walk": 2.0, "run": 3.4, "tiptoe": 1.1, "march": 1.8}[legs]
        amp = {"walk": 24, "run": 36, "tiptoe": 22, "march": 14}[legs]
        lift = {"walk": 16, "run": 30, "tiptoe": 34, "march": 26}[legs]
        ph = t * hz * 2 * math.pi
        sx = dirx if dirx else 0.0
        lx = -16 + math.sin(ph) * amp * (sx if sx else 0.35)
        rx = 16 + math.sin(ph + math.pi) * amp * (sx if sx else 0.35)
        ll = max(0, math.cos(ph)) * lift
        rl = max(0, math.cos(ph + math.pi)) * lift
        bob = abs(math.sin(ph)) * (10 if legs == "run" else 5)
        lean = {"walk": 0.0, "run": 0.12, "tiptoe": -0.05, "march": 0.0}[legs] * (dirx or 0)
        return lx, rx, ll, rl, bob, lean
    if legs == "wide":
        return -34, 34, 0, 0, 0, 0
    if legs == "jump":
        j = abs(math.sin(t * 2.4 * math.pi)) * 40
        return -14, 14, 6, 6, -j, 0
    return -18, 18, 0, 0, 0, 0


def arm_target(pose, side, t, B, look):
    """hand position relative to shoulder + bend (+ = elbow outwards)."""
    sh = B["sh"]
    s = side  # -1 left (screen), +1 right
    if pose == "down":
        return (s * 16, 92, 10 * s)
    if pose == "hips":
        return (s * 8, 74, 60 * s)
    if pose == "up":
        return (s * 48, -88 + wob(t, 1.6, 6), -16 * s)
    if pose == "cheer":
        return (s * 40, -95 + wob(t, 3.0, 12, 0.25 * s), -12 * s)
    if pose == "wave":
        if s > 0:
            return (52 + wob(t, 2.5, 18), -70, -14)
        return (s * 16, 92, 10 * s)
    if pose == "point":
        d = look if look else 1
        if s == d:
            return (s * 112, -6, -6 * s)
        return (s * 14, 90, 10 * s)
    if pose == "hold":
        return (-s * 10, 60, 30 * s)
    if pose == "holdup":
        return (-s * 4, -40, 26 * s)
    if pose == "shrug":
        return (s * 62, 8 - abs(wob(t, 0.8, 8)), 30 * s)
    if pose == "carry":  # sack over right shoulder
        if s > 0:
            return (10, -26, 40)
        return (s * 18, 88, 10 * s)
    if pose == "cross":
        return (-s * 28, 52, 40 * s)
    if pose == "sneak":
        return (s * 10 + 26, 30 + wob(t, 1.1, 6), 34 * s)
    if pose == "whisper":
        if s < 0:
            return (36, -38, -30)
        return (s * 16, 92, 10 * s)
    if pose == "chin":
        if s > 0:
            return (-20, -10, 40)
        return (-s * 10, 50, 30 * s)
    if pose == "count":  # right hand out, palm up
        if s > 0:
            return (78, 34 + abs(wob(t, 1.5, 10)), 20)
        return (s * 16, 92, 10 * s)
    if pose == "wag":
        if s > 0:
            return (40 + wob(t, 2.6, 14), -60, -10)
        return (-s * 8, 74, 60 * s)
    if pose == "eat":
        if s > 0:
            return (-26, -30 + abs(wob(t, 1.4, 22)), 40)
        return (s * 16, 92, 10 * s)
    if pose == "snip":
        return (-s * 14 + 22, 34, 30 * s)
    if pose == "hammer":
        a = abs(wob(t, 1.8, 1.0))
        return (s * 30 - 6, lerp(-90, 40, a), 20 * s)
    return (s * 16, 92, 10 * s)


# ----------------------------------------------------------------------------- hats
def hat_back(P, hat, r, col):
    c = P.c
    if hat == "hood":
        P.shape(lambda c: c.arc(0, -0.05 * r, r * 1.28, 0, 2 * math.pi), col, 6)
    if hat == "long":
        def curls(c):
            for sx in (-1, 1):
                for k in range(5):
                    c.new_sub_path()
                    c.arc(sx * r * (0.92 + 0.05 * (k % 2)), -0.25 * r + k * 0.33 * r, r * 0.3, 0, 2 * math.pi)
        P.shape(curls, col, 5)
    if hat == "wig":
        def rolls(c):
            for sx in (-1, 1):
                for k in range(3):
                    c.new_sub_path()
                    c.arc(sx * r * 0.95, -0.05 * r + k * 0.3 * r, r * 0.22, 0, 2 * math.pi)
        P.shape(rolls, col, 5)
    if hat == "bun":
        P.shape(lambda c: c.arc(0, -r * 1.12, r * 0.36, 0, 2 * math.pi), col, 6)
    if hat == "scarf":
        P.shape(lambda c: poly(c, [(-0.5 * r, 0.6 * r), (0.5 * r, 0.6 * r), (0.15 * r, 1.25 * r)]), col, 6)


def hat_front(P, hat, r, col, t):
    c = P.c
    col = rgb(col)
    if hat == "crown":
        def crown(c):
            y0, y1 = -0.72 * r, -1.42 * r
            pts = [(-0.62 * r, y0)]
            n = 5
            for k in range(n):
                xa = -0.62 * r + (k + 0.5) * 1.24 * r / n
                xb = -0.62 * r + (k + 1) * 1.24 * r / n
                pts += [(xa, y1 + (0.12 * r if k % 2 else 0)), (xb, y0 - 0.32 * r)]
            pts[-1] = (0.62 * r, y0)
            poly(c, pts)
        P.shape(crown, col, 6)
        if P.mode:
            c.rectangle(-0.62 * r, -0.86 * r, 1.24 * r, 0.16 * r)
            fs(c, shade(col, 0.8), 4)
            for k, jc in enumerate([(0.85, 0.15, 0.2), (0.2, 0.4, 0.9), (0.85, 0.15, 0.2)]):
                c.arc(-0.36 * r + k * 0.36 * r, -0.78 * r, 0.075 * r, 0, 2 * math.pi)
                fs(c, jc, 3)
            c.arc(-0.42 * r, -1.0 * r, 0.06 * r, 0, 2 * math.pi)
            fill(c, (1, 1, 1), 0.6)
    elif hat == "helmet":
        def dome(c):
            c.arc(0, -0.12 * r, r * 1.04, math.pi, 2 * math.pi)
            c.close_path()
        P.shape(dome, col, 6)
        P.shape(lambda c: ellipse(c, 0, -0.12 * r, r * 1.26, r * 0.17), shade(col, 0.85), 6)
        P.shape(lambda c: poly(c, [(-0.08 * r, -1.1 * r), (0.08 * r, -1.1 * r), (0.0, -1.45 * r)]), (0.85, 0.2, 0.2), 4)
        if P.mode:
            c.arc(-0.42 * r, -0.62 * r, 0.14 * r, 0, 2 * math.pi)
            fill(c, (1, 1, 1), 0.45)
    elif hat == "straw":
        P.shape(lambda c: ellipse(c, 0, -0.6 * r, r * 1.4, r * 0.26), col, 6)
        def dome(c):
            c.arc(0, -0.66 * r, r * 0.64, math.pi, 2 * math.pi)
            c.close_path()
        P.shape(dome, shade(col, 1.05), 6)
        if P.mode:
            c.rectangle(-0.63 * r, -0.8 * r, 1.26 * r, 0.12 * r)
            fill(c, (0.75, 0.2, 0.2))
    elif hat == "hair":
        def tuft(c):
            c.move_to(-0.98 * r, -0.2 * r)
            c.curve_to(-1.05 * r, -1.2 * r, 1.05 * r, -1.25 * r, 0.98 * r, -0.2 * r)
            c.curve_to(0.6 * r, -0.62 * r, 0.2 * r, -0.5 * r, 0.1 * r, -0.75 * r)
            c.curve_to(-0.2 * r, -0.5 * r, -0.6 * r, -0.62 * r, -0.98 * r, -0.2 * r)
            c.close_path()
        P.shape(tuft, col, 6)
    elif hat == "bun":
        def top(c):
            c.move_to(-0.99 * r, -0.12 * r)
            c.curve_to(-1.0 * r, -1.25 * r, 1.0 * r, -1.25 * r, 0.99 * r, -0.12 * r)
            c.curve_to(0.5 * r, -0.62 * r, -0.5 * r, -0.62 * r, -0.99 * r, -0.12 * r)
            c.close_path()
        P.shape(top, col, 6)
    elif hat == "scarf":
        def sc(c):
            c.move_to(-1.06 * r, 0.25 * r)
            c.curve_to(-1.15 * r, -1.35 * r, 1.15 * r, -1.35 * r, 1.06 * r, 0.25 * r)
            c.curve_to(0.8 * r, -0.4 * r, -0.8 * r, -0.4 * r, -1.06 * r, 0.25 * r)
            c.close_path()
        P.shape(sc, col, 6)
        if P.mode:
            for k in range(3):
                c.arc(-0.4 * r + k * 0.4 * r, -0.72 * r, 0.06 * r, 0, 2 * math.pi)
                fill(c, (1, 1, 1), 0.8)
    elif hat == "cap":
        def cap(c):
            c.arc(0, -0.45 * r, r * 0.86, math.pi * 1.05, math.pi * 1.95)
            c.close_path()
        P.shape(cap, col, 6)
        P.shape(lambda c: ellipse(c, 0.42 * r, -0.5 * r, r * 0.55, r * 0.12), shade(col, 0.8), 5)
    elif hat == "beret":
        P.shape(lambda c: ellipse(c, -0.1 * r, -0.86 * r, r * 0.95, r * 0.32), col, 6)
        P.shape(lambda c: c.arc(-0.1 * r, -1.2 * r, 0.08 * r, 0, 2 * math.pi), col, 4)
    elif hat == "tricorn":
        def lobes(c):
            poly(c, [(-1.3 * r, -0.95 * r), (-0.9 * r, -0.62 * r), (0.0, -0.55 * r), (0.9 * r, -0.62 * r),
                     (1.3 * r, -0.95 * r), (0.6 * r, -0.85 * r), (0.0, -1.25 * r), (-0.6 * r, -0.85 * r)])
        def crown(c):
            c.arc(0, -0.72 * r, 0.62 * r, math.pi, 2 * math.pi)
            c.close_path()
        P.shape(crown, shade(col, 1.2), 6)
        P.shape(lobes, col, 6)
        if P.mode:
            c.move_to(-1.24 * r, -0.92 * r)
            c.line_to(-0.6 * r, -0.82 * r)
            c.line_to(0, -1.18 * r)
            c.line_to(0.6 * r, -0.82 * r)
            c.line_to(1.24 * r, -0.92 * r)
            stroke(c, 5, (0.98, 0.78, 0.16))
    elif hat == "long":
        def top(c):
            c.move_to(-1.0 * r, 0.0)
            c.curve_to(-1.05 * r, -1.35 * r, 1.05 * r, -1.35 * r, 1.0 * r, 0.0)
            c.curve_to(0.7 * r, -0.55 * r, -0.7 * r, -0.55 * r, -1.0 * r, 0.0)
            c.close_path()
        P.shape(top, col, 6)
    elif hat == "wig":
        def top(c):
            c.move_to(-0.95 * r, -0.1 * r)
            c.curve_to(-1.0 * r, -1.3 * r, 1.0 * r, -1.3 * r, 0.95 * r, -0.1 * r)
            c.curve_to(0.6 * r, -0.6 * r, -0.6 * r, -0.6 * r, -0.95 * r, -0.1 * r)
            c.close_path()
        P.shape(top, col, 6)
    elif hat == "hood":
        def rim(c):
            c.arc(0, -0.05 * r, r * 1.28, math.pi * 0.98, math.pi * 2.02)
            c.arc_negative(0, 0.0, r * 0.98, math.pi * 2.0, math.pi * 1.0)
            c.close_path()
        P.shape(rim, shade(col, 1.15), 5)


# ----------------------------------------------------------------------------- face
def draw_face(c, L, r, expr, look, fd, t, blink=True):
    lift, ang, eyes, mouth = EXPR.get(expr, EXPR["smile"])
    lx, ly = look
    face = L.get("face", "plain")
    fx = fd * r * 0.18
    iris = rgb(L.get("iris", (80, 60, 40)))
    # blink every ~3.7 s
    bl = blink and (t * 1.0 % 3.7) < 0.12 and eyes in ("open", "wide")
    # blush
    for sx in (-1, 1):
        ellipse(c, sx * r * 0.55 + fx * 0.7, r * 0.25, r * 0.14, r * 0.085)
        fill(c, (1.0, 0.55, 0.62), 0.42)
    for sx in (-1, 1):
        ex, ey = sx * r * 0.33 + fx, -r * 0.03
        rx, ry = r * 0.19, r * 0.25
        mode = eyes
        if eyes == "wink" and sx > 0:
            mode = "closed"
        elif eyes == "wink":
            mode = "open"
        if bl:
            mode = "closed_flat"
        if mode in ("closed", "closed_flat", "squint"):
            if mode == "closed":
                c.move_to(ex - rx, ey + 0.05 * r)
                c.curve_to(ex - rx * 0.5, ey - ry * 0.9, ex + rx * 0.5, ey - ry * 0.9, ex + rx, ey + 0.05 * r)
            elif mode == "squint" and sx < 0:
                c.move_to(ex - rx, ey - 0.06 * r)
                c.line_to(ex + rx, ey + 0.04 * r)
            else:
                c.move_to(ex - rx, ey)
                c.curve_to(ex - rx * 0.4, ey + ry * 0.35, ex + rx * 0.4, ey + ry * 0.35, ex + rx, ey)
            if not (mode == "squint" and sx > 0):
                stroke(c, r * 0.075)
                # brows
                _brow(c, sx, ex, ey, r, lift, ang, expr)
                continue
        if mode == "wide":
            rx, ry = rx * 1.12, ry * 1.12
        ellipse(c, ex, ey, rx, ry)
        c.set_source_rgb(1, 1, 1)
        c.fill_preserve()
        c.save()
        c.clip()
        ir = r * (0.09 if mode == "wide" else 0.135)
        ix = ex + lx * r * 0.08 + fd * r * 0.04
        iy = ey + ly * r * 0.08 + r * 0.03
        g = cairo.RadialGradient(ix, iy + ir * 0.4, 0, ix, iy, ir)
        g.add_color_stop_rgb(0, *shade(iris, 1.5))
        g.add_color_stop_rgb(1, *shade(iris, 0.6))
        c.arc(ix, iy, ir, 0, 2 * math.pi)
        c.set_source(g)
        c.fill()
        c.arc(ix, iy, ir * 0.5, 0, 2 * math.pi)
        fill(c, INK)
        c.arc(ix - ir * 0.35, iy - ir * 0.4, ir * 0.3, 0, 2 * math.pi)
        fill(c, (1, 1, 1))
        c.arc(ix + ir * 0.3, iy + ir * 0.3, ir * 0.14, 0, 2 * math.pi)
        fill(c, (1, 1, 1))
        # lids
        lid = {"half": 0.45, "squint": 0.6}.get(mode, 0.0)
        if lid:
            c.rectangle(ex - rx - 2, ey - ry - 2, 2 * rx + 4, 2 * ry * lid + 2)
            fill(c, SKIN)
        c.restore()
        ellipse(c, ex, ey, rx, ry)
        stroke(c, r * 0.045)
        # upper lid line + lash
        ly0 = ey - ry + 2 * ry * (lid if lid else 0)
        if lid:
            c.move_to(ex - rx, ly0)
            c.line_to(ex + rx, ly0 - (0.0 if sx > 0 else 0))
            stroke(c, r * 0.07)
        else:
            c.arc(ex, ey, rx * 1.0, math.pi * 1.1, math.pi * 1.9) if False else None
            c.save()
            c.translate(ex, ey)
            c.scale(rx, ry)
            c.arc(0, 0, 1, math.pi * 1.12, math.pi * 1.88)
            c.restore()
            stroke(c, r * 0.07)
        c.move_to(ex + sx * rx * 0.85, ly0 + ry * 0.25 * (0 if lid else 1))
        c.line_to(ex + sx * rx * 1.25, ly0 - ry * 0.05)
        stroke(c, r * 0.04)
        _brow(c, sx, ex, ey, r, lift, ang, expr)
    if face == "glasses":
        for sx in (-1, 1):
            c.arc(sx * r * 0.33 + fx, -r * 0.03, r * 0.27, 0, 2 * math.pi)
            stroke(c, r * 0.05, (0.25, 0.2, 0.25))
        c.move_to(-r * 0.07 + fx, -r * 0.05)
        c.line_to(r * 0.07 + fx, -r * 0.05)
        stroke(c, r * 0.05, (0.25, 0.2, 0.25))
    # nose
    nx, ny = fx * 1.5 + fd * r * 0.04, r * 0.14
    c.move_to(nx - r * 0.02, ny - r * 0.07)
    c.curve_to(nx + r * 0.1 * (1 if fd >= 0 else -1), ny - r * 0.02, nx + r * 0.06 * (1 if fd >= 0 else -1), ny + r * 0.07, nx - r * 0.03, ny + r * 0.05)
    stroke(c, r * 0.04)
    # facial hair under mouth
    hc = rgb(L.get("hairc", (90, 60, 40)))
    if face == "beard":
        c.move_to(-0.62 * r + fx * 0.5, 0.2 * r)
        c.curve_to(-0.55 * r, 1.15 * r, 0.55 * r, 1.15 * r, 0.62 * r + fx * 0.5, 0.2 * r)
        c.curve_to(0.3 * r, 0.42 * r, -0.3 * r, 0.42 * r, -0.62 * r + fx * 0.5, 0.2 * r)
        c.close_path()
        fs(c, hc, r * 0.05)
    mx, my = fx * 1.2, r * 0.44
    _mouth(c, mouth, mx, my, r, t)
    if face in ("stache", "beard"):
        for sx in (-1, 1):
            c.move_to(mx, my - r * 0.14)
            c.curve_to(mx + sx * r * 0.12, my - r * 0.24, mx + sx * r * 0.3, my - r * 0.18, mx + sx * r * 0.34, my - r * 0.06)
            c.curve_to(mx + sx * r * 0.22, my - r * 0.1, mx + sx * r * 0.1, my - r * 0.06, mx, my - r * 0.1)
            c.close_path()
            fs(c, hc, r * 0.035)
    if face == "lady":
        pass


def _brow(c, sx, ex, ey, r, lift, ang, expr):
    by = ey - r * 0.36 - lift * r * 0.11
    if expr in ("smug", "doubt") and sx > 0:
        by -= r * 0.1
        ang = -0.2
    ix, ox = ex - sx * r * 0.13, ex + sx * r * 0.19
    iy, oy = by + ang * r * 0.09, by - ang * r * 0.03
    c.move_to(ix, iy - r * 0.05)
    c.curve_to(lerp(ix, ox, 0.5), lerp(iy, oy, 0.5) - r * 0.09, ox, oy - r * 0.02, ox, oy)
    c.curve_to(lerp(ix, ox, 0.5), lerp(iy, oy, 0.5) - r * 0.03, ix, iy + r * 0.04, ix, iy + r * 0.04)
    c.close_path()
    c.set_source_rgb(*INK)
    c.fill_preserve()
    stroke(c, r * 0.02)


def _mouth(c, m, x, y, r, t):
    dark = (0.42, 0.08, 0.14)
    if m == "smile":
        c.move_to(x - r * 0.2, y - r * 0.03)
        c.curve_to(x - r * 0.08, y + r * 0.13, x + r * 0.08, y + r * 0.13, x + r * 0.2, y - r * 0.03)
        stroke(c, r * 0.06)
    elif m in ("grin", "laugh"):
        k = 1.25 if m == "laugh" else 1.0
        if m == "laugh":
            k *= 1 + 0.12 * abs(math.sin(t * 9))
        c.move_to(x - r * 0.24 * k, y - r * 0.04)
        c.line_to(x + r * 0.24 * k, y - r * 0.04)
        c.curve_to(x + r * 0.2 * k, y + r * 0.3 * k, x - r * 0.2 * k, y + r * 0.3 * k, x - r * 0.24 * k, y - r * 0.04)
        c.close_path()
        c.save()
        c.set_source_rgb(*dark)
        c.fill_preserve()
        c.clip_preserve()
        c.new_path()
        c.rectangle(x - r * 0.3 * k, y - r * 0.05, r * 0.6 * k, r * 0.08)
        fill(c, (1, 1, 1))
        ellipse(c, x, y + r * 0.24 * k, r * 0.14 * k, r * 0.08 * k)
        fill(c, (0.95, 0.45, 0.5))
        c.restore()
        c.move_to(x - r * 0.24 * k, y - r * 0.04)
        c.line_to(x + r * 0.24 * k, y - r * 0.04)
        c.curve_to(x + r * 0.2 * k, y + r * 0.3 * k, x - r * 0.2 * k, y + r * 0.3 * k, x - r * 0.24 * k, y - r * 0.04)
        c.close_path()
        stroke(c, r * 0.05)
    elif m in ("o", "O"):
        k = 1.5 if m == "O" else 1.0
        ellipse(c, x, y + r * 0.04, r * 0.09 * k, r * 0.12 * k)
        fs(c, dark, r * 0.05)
    elif m == "frown":
        c.move_to(x - r * 0.17, y + r * 0.08)
        c.curve_to(x - r * 0.06, y - r * 0.05, x + r * 0.06, y - r * 0.05, x + r * 0.17, y + r * 0.08)
        stroke(c, r * 0.06)
    elif m == "flat":
        c.move_to(x - r * 0.13, y + r * 0.02)
        c.line_to(x + r * 0.13, y + r * 0.02)
        stroke(c, r * 0.06)
    elif m == "smirk":
        c.move_to(x - r * 0.14, y + r * 0.03)
        c.curve_to(x, y + r * 0.1, x + r * 0.12, y + r * 0.06, x + r * 0.22, y - r * 0.07)
        stroke(c, r * 0.06)
    elif m in ("wavy", "sneer"):
        c.move_to(x - r * 0.2, y + r * 0.03)
        for k in range(1, 5):
            c.line_to(x - r * 0.2 + k * r * 0.1, y + r * (0.03 + (0.05 if k % 2 else -0.0)) - (r * 0.05 if m == "sneer" and k > 2 else 0))
        stroke(c, r * 0.05)
    elif m == "grit":
        rrect(c, x - r * 0.2, y - r * 0.05, r * 0.4, r * 0.14, r * 0.04)
        fs(c, (1, 1, 1), r * 0.045)
        for k in (-1, 0, 1):
            c.move_to(x + k * r * 0.1, y - r * 0.05)
            c.line_to(x + k * r * 0.1, y + r * 0.09)
        c.move_to(x - r * 0.2, y + r * 0.02)
        c.line_to(x + r * 0.2, y + r * 0.02)
        stroke(c, r * 0.025)


# ----------------------------------------------------------------------------- body
def draw(c, who, x, y, s=1.0, expr="smile", arms="down", legs="stand", t=0.0, look=(0, 0), fd=0,
         hold=None, shadow=True, lean=0.0, sticker=True, alpha=1.0, tint=None, squash=0.0):
    """who: CAST key or look dict. (x, y) = point between the feet on the ground."""
    L = CAST[who] if isinstance(who, str) else who
    B = BODY[L.get("body", "adult")]
    tun = rgb(L["tunic"])
    if tint:
        tun = mix(tun, tint[0], tint[1])
    trim = rgb(L["trim"])
    hatc = rgb(L.get("hatc", (80, 60, 40)))
    if shadow:
        soft_shadow(c, x + 14 * s, y + 4 * s, 78 * s, 15 * s, 0.38 * alpha)
    if alpha < 1:
        c.push_group()
    c.save()
    c.translate(x, y)
    c.scale(s, s * (1 - squash))
    lf, rf, ll, rl, bob, lean2 = leg_pose(legs, t, fd)
    lean += lean2
    breathe = math.sin(t * 2.1) * 2.0 if legs == "stand" else 0
    hip = -B["leg"] - bob * 0.6
    top = hip - B["torso"] + breathe
    hr = B["head"]
    hy = top - hr * 0.78
    outfit = L.get("outfit", "tunic")
    long = outfit in ("robe", "dress")
    hem_y = -B["leg"] * 0.3 if long else hip + 10
    hem = B["hem"] + (16 if outfit == "dress" else 0)
    elder = L.get("body") == "elder"
    c.rotate(lean)
    for mode in ((0, 1) if sticker else (1,)):
        P = Painter(c, mode)
        # cape behind
        if "cape" in L.get("extras", []):
            P.shape(lambda c: poly(c, [(-B["sh"] + 4, top + 10), (B["sh"] - 4, top + 10), (hem + 16, -6), (-hem - 16, -6)]), shade(tun, 0.7), 6)
        # legs
        for fx, lift, side in ((lf, ll, -1), (rf, rl, 1)):
            hx = side * 12
            kx = (hx + fx) / 2 + (8 * (fd or side) if lift > 2 else 0)
            ky = (hip - lift) / 2 + hip * 0.0 - 4
            P.line([(hx, hip - 4), (kx, ky), (fx, -lift - 8)], 9)
        for fx, lift, side in ((lf, ll, -1), (rf, rl, 1)):
            sx = fx + (8 * fd if fd else side * 5)
            P.shape(lambda c, sx=sx, lift=lift: ellipse(c, sx, -lift - 5, 21, 11.5), SHOE, 5)
            if mode:
                ellipse(c, sx - 7, -lift - 9, 6, 3)
                fill(c, (1, 1, 1), 0.5)
        # torso
        def torso(c):
            sw = B["sh"]
            c.move_to(-sw, top + 12)
            c.curve_to(-sw, top, -sw + 6, top, -sw + 14, top)
            c.line_to(sw - 14, top)
            c.curve_to(sw - 6, top, sw, top, sw, top + 12)
            c.line_to(hem, hem_y)
            c.curve_to(hem * 0.5, hem_y + 8, -hem * 0.5, hem_y + 8, -hem, hem_y)
            c.close_path()
        P.shape(torso, tun, 7)
        if mode:
            c.save()
            torso(c)
            c.clip()
            # 3-tone: highlight left, shadow right
            poly(c, [(B["sh"] * 0.25, top - 5), (B["sh"] + 40, top - 5), (hem + 40, hem_y + 20), (hem * 0.3, hem_y + 20)])
            fill(c, shade(tun, 0.74))
            poly(c, [(-B["sh"] - 30, top - 5), (-B["sh"] * 0.45, top - 5), (-hem * 0.62, hem_y + 20), (-hem - 30, hem_y + 20)])
            fill(c, shade(tun, 1.22))
            # folds
            for fxk in (-0.3, 0.32):
                c.move_to(hem * fxk * 0.6, top + B["torso"] * 0.55)
                c.curve_to(hem * fxk * 0.8, top + B["torso"] * 0.75, hem * fxk, hem_y - 10, hem * fxk * 1.05, hem_y)
                stroke(c, 3.5, shade(tun, 0.62), 0.8)
            if outfit == "apron":
                rrect(c, -hem * 0.55, top + B["torso"] * 0.3, hem * 1.1, hem_y - top, 10)
                fs(c, trim, 5)
                c.move_to(-B["sh"] * 0.5, top)
                c.line_to(-hem * 0.45, top + B["torso"] * 0.32)
                c.move_to(B["sh"] * 0.5, top)
                c.line_to(hem * 0.45, top + B["torso"] * 0.32)
                stroke(c, 6, trim)
            if outfit == "armor":
                rrect(c, -B["sh"] + 6, top + 8, 2 * B["sh"] - 12, B["torso"] * 0.5, 14)
                g = cairo.LinearGradient(-B["sh"], 0, B["sh"], 0)
                g.add_color_stop_rgb(0, *shade(trim, 1.2))
                g.add_color_stop_rgb(1, *shade(trim, 0.7))
                c.set_source(g)
                c.fill_preserve()
                stroke(c, 5)
                for rx in (-B["sh"] * 0.5, B["sh"] * 0.5):
                    c.arc(rx, top + 20, 3.5, 0, 2 * math.pi)
                    fill(c, INK)
            if outfit == "robe":
                c.rectangle(-9, top, 18, hem_y - top + 10)
                fill(c, trim)
                c.move_to(-9, top)
                c.line_to(-9, hem_y + 10)
                c.move_to(9, top)
                c.line_to(9, hem_y + 10)
                stroke(c, 3)
            # trim band at hem
            c.rectangle(-hem - 10, hem_y - 13, 2 * hem + 20, 30)
            fill(c, trim)
            c.move_to(-hem - 10, hem_y - 13)
            c.line_to(hem + 10, hem_y - 13)
            stroke(c, 3.5)
            # sash
            if "sash" in L.get("extras", []):
                poly(c, [(-B["sh"], top + 4), (-B["sh"] + 24, top), (hem, hem_y - 30), (hem - 26, hem_y - 14)])
                fs(c, L.get("sash", (180, 30, 40)), 4)
            # belt
            by = top + B["torso"] * (0.62 if not long else 0.48)
            c.rectangle(-hem - 10, by - 7, 2 * hem + 20, 14)
            fill(c, (0.32, 0.2, 0.14))
            c.move_to(-hem - 10, by - 7)
            c.line_to(hem + 10, by - 7)
            c.move_to(-hem - 10, by + 7)
            c.line_to(hem + 10, by + 7)
            stroke(c, 3)
            c.restore()
            rrect(c, -10, by - 10, 20, 20, 4)
            fs(c, (0.98, 0.8, 0.25), 4)
            rrect(c, -4, by - 4, 8, 8, 2)
            fill(c, shade((0.98, 0.8, 0.25), 0.6))
            torso(c)
            stroke(c, 7)
        # satchel
        if "satchel" in L.get("extras", []):
            if mode:
                c.move_to(B["sh"] - 6, top + 4)
                c.line_to(-hem * 0.7, hem_y - 40)
                stroke(c, 6, (0.45, 0.28, 0.16))
            P.shape(lambda c: rrect(c, -hem * 0.95, hem_y - 60, 46, 38, 8), (0.55, 0.34, 0.18), 5)
        # neck
        P.line([(0, top + 2), (0, top - 14)], 9, hl=False)
        # arms
        hands = []
        for side in (-1, 1):
            sx0, sy0 = side * (B["sh"] - 6), top + 16
            hx, hy2, bend = arm_target(arms, side, t, B, fd if fd else 1)
            ex, ey = sx0 + hx, sy0 + hy2
            mx, my = (sx0 + ex) / 2, (sy0 + ey) / 2
            dx, dy = ex - sx0, ey - sy0
            ln = math.hypot(dx, dy) or 1
            cx_, cy_ = mx + (-dy / ln) * bend * (-side), my + (dx / ln) * bend * (-side)
            cx_ = mx + side * abs(bend) * (1 if bend * side > 0 else -1)
            P.line([(sx0, sy0), (cx_, cy_), (ex, ey)], 9)
            hands.append((ex, ey))
        if hold and mode:
            hx = (hands[0][0] + hands[1][0]) / 2
            hy3 = (hands[0][1] + hands[1][1]) / 2
            if arms in ("carry", "count", "wave", "point", "eat", "chin", "wag", "whisper"):
                hx, hy3 = hands[1]
            c.save()
            hold(c, hx, hy3)
            c.restore()
        for (hx, hy3) in hands:
            P.shape(lambda c, hx=hx, hy3=hy3: c.arc(hx, hy3, 12.5, 0, 2 * math.pi), SKIN, 5)
        # head
        c.save()
        c.translate(fd * 4, hy)
        hat = L.get("hat")
        hat_back(P, hat, hr, hatc)
        P.shape(lambda c: c.arc(0, 0, hr, 0, 2 * math.pi), SKIN, 9)
        if mode:
            c.save()
            c.arc(0, 0, hr, 0, 2 * math.pi)
            c.clip()
            g = cairo.RadialGradient(hr * 0.55, hr * 0.6, 0, hr * 0.4, hr * 0.45, hr * 1.25)
            g.add_color_stop_rgba(0, *VIOLET, 0.0)
            g.add_color_stop_rgba(0.55, *VIOLET, 0.0)
            g.add_color_stop_rgba(0.85, *VIOLET, 0.22)
            g.add_color_stop_rgba(1.0, *VIOLET, 0.42)
            c.set_source(g)
            c.paint()
            g = cairo.RadialGradient(-hr * 0.45, -hr * 0.5, 0, -hr * 0.45, -hr * 0.5, hr * 0.6)
            g.add_color_stop_rgba(0, 1, 1, 1, 0.75)
            g.add_color_stop_rgba(1, 1, 1, 1, 0)
            c.set_source(g)
            c.paint()
            c.restore()
            c.arc(0, 0, hr - 5, math.pi * 0.05, math.pi * 0.7)
            stroke(c, 4, (0.35, 0.25, 0.45), 0.35)
            c.arc(0, 0, hr, 0, 2 * math.pi)
            stroke(c, 9)
            draw_face(c, L, hr, expr, look, fd, t)
        hat_front(P, hat, hr, hatc, t)
        c.restore()
    c.restore()
    if alpha < 1:
        c.pop_group_to_source()
        c.paint_with_alpha(alpha)


def height(who, s=1.0):
    L = CAST[who] if isinstance(who, str) else who
    B = BODY[L.get("body", "adult")]
    return (B["leg"] + B["torso"] + B["head"] * 1.8) * s


def head_y(who, s=1.0):
    """y offset (negative) from feet to head center."""
    L = CAST[who] if isinstance(who, str) else who
    B = BODY[L.get("body", "adult")]
    return -(B["leg"] + B["torso"] + B["head"] * 0.78) * s
