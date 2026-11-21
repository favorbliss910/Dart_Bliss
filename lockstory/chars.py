"""Procedural 2D cartoon characters (round head, dot eyes, stick-ish limbs).
Everything is drawn with PIL at 2x supersampling, so there are no image
files to supply. Coordinates: origin at feet centre, y up is negative,
character is ~1000 units tall. `d` = +1 faces right, -1 faces left."""
import math
from PIL import Image, ImageDraw

OUT = (28, 22, 36)          # outline colour
SS = 2                      # supersample factor


def rot(a):                 # angle from straight down; + = toward facing dir
    r = math.radians(a)
    return math.sin(r), math.cos(r)


class Char:
    def __init__(self, **kw):
        self.skin = kw.get("skin", (244, 200, 160))
        self.coat = kw.get("coat", (40, 52, 96))
        self.coat2 = kw.get("coat2", (200, 60, 50))
        self.pants = kw.get("pants", (60, 60, 70))
        self.hair = kw.get("hair", (90, 60, 40))
        self.hat = kw.get("hat", None)        # colour or None
        self.bald = kw.get("bald", False)
        self.stache = kw.get("stache", False)
        self.chops = kw.get("chops", False)
        self.apron = kw.get("apron", None)
        self.long_coat = kw.get("long_coat", True)
        self.build = kw.get("build", 1.0)     # torso width scale
        self.hat_style = kw.get("hat_style", "top")

    # ------------------------------------------------------------------
    def render(self, pose, d=1, scale=1.6):
        """Return (RGBA image, (ox, oy)) where (ox, oy) is feet-centre in px."""
        W, H = int(760 * scale), int(1180 * scale)
        S = scale * SS
        im = Image.new("RGBA", (int(W * SS), int(H * SS)), (0, 0, 0, 0))
        g = ImageDraw.Draw(im)
        cx, cy = 380, 1090          # feet centre inside the 760x1180 box

        def P(x, y):
            return ((cx + x * d) * S, (cy + y) * S)

        def line(p, q, w, col):
            a, b = P(*p), P(*q)
            r = w * S / 2
            g.line([a, b], fill=col, width=int(w * S))
            for c in (a, b):
                g.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=col)

        def circ(p, r, col, outline=True, w=7):
            c = P(*p)
            R = r * S
            if outline:
                g.ellipse([c[0] - R - w * S, c[1] - R - w * S, c[0] + R + w * S, c[1] + R + w * S], fill=OUT)
            g.ellipse([c[0] - R, c[1] - R, c[0] + R, c[1] + R], fill=col)

        def poly(pts, col, outline=True, w=7):
            pp = [P(*p) for p in pts]
            if outline:
                g.line(pp + [pp[0]], fill=OUT, width=int(2 * w * S), joint="curve")
                for p in pp:
                    r = w * S
                    g.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=OUT)
            g.polygon(pp, fill=col)

        def limb(p, q, wd, col):
            line(p, q, wd + 14, OUT)
            line(p, q, wd, col)

        bob = pose.get("bob", 0)
        lean = pose.get("lean", 0)
        walk = pose.get("walk", 0)         # -1..1 leg swing
        b = self.build
        hip_y = -390 + bob * 0.4
        sh_y = -700 + bob
        shx = lean                           # shoulder line x shift

        # ---- legs ----------------------------------------------------
        for side, ph in ((-1, 1), (1, -1)):
            sw = walk * 70 * ph
            top = (side * 42 * b, hip_y)
            foot = (side * 46 * b + sw, -22)
            limb(top, foot, 44, self.pants)
            sx0 = foot[0]
            shoe = [(sx0 - 40, -44), (sx0 + 85, -44), (sx0 + 92, 0), (sx0 - 40, 0)]
            poly(shoe, (30, 26, 30), w=6)

        # ---- back arm (character's left, drawn behind torso) ----------
        def arm(side, key):
            a1, a2 = pose.get(key, (4, 6))
            shoulder = (side * 112 * b + shx, sh_y + 30)
            sx, sy = rot(a1)
            elbow = (shoulder[0] + sx * 150, shoulder[1] + sy * 150)
            ex, ey = rot(a2)
            hand = (elbow[0] + ex * 140, elbow[1] + ey * 140)
            return shoulder, elbow, hand

        sB, eB, hB = arm(-1, "armB")
        limb(sB, eB, 40, self.coat)
        limb(eB, hB, 36, self.coat)
        circ(hB, 26, self.skin, w=6)

        # ---- torso / coat ---------------------------------------------
        hem = -170 if self.long_coat else -380
        torso = [(-118 * b + shx, sh_y), (118 * b + shx, sh_y),
                 (150 * b + shx * 0.3, hem), (-150 * b + shx * 0.3, hem)]
        poly(torso, self.coat)
        # lapel / buttons / apron
        line((shx, sh_y + 20), (shx * 0.6, hem - 10), 6, OUT)
        for i in range(3):
            y = sh_y + 110 + i * 90
            circ((shx * (1 - i * 0.2) + 24, y), 9, self.coat2, w=3)
        if self.apron:
            ap = [(-95 * b + shx * 0.4, sh_y + 170), (95 * b + shx * 0.4, sh_y + 170),
                  (120 * b, -120), (-120 * b, -120)]
            poly(ap, self.apron)
            line((-95 * b + shx * 0.4, sh_y + 170), (95 * b + shx * 0.4, sh_y + 170), 10, OUT)

        # ---- front arm --------------------------------------------------
        sF, eF, hF = arm(1, "armF")
        limb(sF, eF, 40, self.coat)
        limb(eF, hF, 36, self.coat)
        circ(hF, 26, self.skin, w=6)
        if pose.get("finger"):               # pointing-up index finger
            fx, fy = rot(pose.get("finger_angle", 180))
            tip = (hF[0] + fx * 58, hF[1] + fy * 58)
            limb(hF, tip, 14, self.skin)
        if pose.get("fist_hold"):
            pass

        # ---- head -------------------------------------------------------
        hx, hy = shx * 1.15, sh_y - 150 + pose.get("head_dy", 0)
        tilt = math.radians(pose.get("tilt", 0))

        def HL(x, y):                        # head-local -> character coords
            xr = x * math.cos(tilt) - y * math.sin(tilt)
            yr = x * math.sin(tilt) + y * math.cos(tilt)
            return (hx + xr, hy + yr)

        # neck
        limb((shx, sh_y + 5), (hx, hy + 110), 46, self.skin)
        circ((hx, hy), 150, self.skin, w=8)
        circ(HL(-146 * 1, 10), 28, self.skin, w=6)       # back ear
        circ(HL(146, 10), 28, self.skin, w=6)             # front ear
        if not self.bald:
            hair = [HL(-146, -30), HL(-130, -110), HL(-60, -150), HL(60, -150), HL(130, -110), HL(146, -30),
                    HL(110, -70), HL(0, -100), HL(-110, -70)]
            poly(hair, self.hair, w=6)
        if self.chops:
            for sgn in (-1, 1):
                poly([HL(sgn * 120, -20), HL(sgn * 148, -20), HL(sgn * 150, 70), HL(sgn * 110, 100), HL(sgn * 100, 40)],
                     self.hair, w=5)
        look = pose.get("look", (1, 0))
        eye = pose.get("eyes", "dot")
        for sgn in (-1, 1):
            ex, ey = 52 * sgn, -8
            if eye == "closed":
                line(HL(ex - 24, ey), HL(ex + 24, ey), 8, OUT)
            else:
                rr = 34 if eye == "wide" else 28
                c = HL(ex, ey)
                R = rr * S
                cc = P(*c)
                g.ellipse([cc[0] - R - 6 * S, cc[1] - R - 6 * S, cc[0] + R + 6 * S, cc[1] + R + 6 * S], fill=OUT)
                g.ellipse([cc[0] - R, cc[1] - R, cc[0] + R, cc[1] + R], fill=(255, 255, 255))
                pr = (9 if eye != "wide" else 7) * S
                px, py = cc[0] + look[0] * 11 * S * d, cc[1] + look[1] * 11 * S
                g.ellipse([px - pr, py - pr, px + pr, py + pr], fill=OUT)
                if eye == "squint":
                    g.rectangle([cc[0] - R - 8 * S, cc[1] - R - 8 * S, cc[0] + R + 8 * S, cc[1] - 4 * S], fill=self.skin)
                    line(HL(ex - 28, ey - 4), HL(ex + 28, ey - 4), 8, OUT)
            br = pose.get("brow", 0)           # -1 angry .. +1 raised/worried
            by = -62 - br * 16
            tl = pose.get("brow_tilt", 0) * sgn * d * d
            line(HL(ex - 28, by + tl * 12), HL(ex + 28, by - tl * 12), 9, OUT)
        # nose
        circ(HL(8, 38), 15, self.skin, w=5)
        # moustache
        if self.stache:
            poly([HL(-60, 62), HL(0, 52), HL(60, 62), HL(30, 84), HL(0, 70), HL(-30, 84)], self.hair, w=4)
        # mouth
        m = pose.get("mouth", "smile")
        o = pose.get("open", 0.0)
        if m == "smile":
            pts = [HL(-44 + 88 * t, 92 + 22 * math.sin(math.pi * t)) for t in [i / 10 for i in range(11)]]
            g.line([P(*p) for p in pts], fill=OUT, width=int(8 * S), joint="curve")
        elif m == "flat":
            line(HL(-36, 98), HL(36, 98), 8, OUT)
        elif m in ("open", "laugh", "o"):
            w_ = 52 if m == "laugh" else (30 if m == "o" else 44)
            h_ = (28 + 52 * o) if m != "o" else 46
            mp = [HL(-w_, 86), HL(w_, 86), HL(w_ * 0.8, 86 + h_), HL(-w_ * 0.8, 86 + h_)]
            poly(mp, (110, 30, 40), w=5)
            if m == "laugh":
                poly([HL(-w_ * 0.8, 88), HL(w_ * 0.8, 88), HL(w_ * 0.7, 106), HL(-w_ * 0.7, 106)], (255, 255, 255), outline=False)
        # hat
        if self.hat:
            tilt_pts = lambda pts: [HL(*p) for p in pts]
            if self.hat_style == "hard":
                poly(tilt_pts([(-175, -112), (175, -112), (175, -88), (-175, -88)]), self.hat, w=6)
                poly(tilt_pts([(-135, -108), (-125, -190), (-75, -255), (0, -280), (75, -255), (125, -190), (135, -108)]), self.hat, w=6)
                poly(tilt_pts([(-14, -112), (14, -112), (14, -275), (-14, -275)]), (230, 180, 40), outline=False)
            else:
                poly(tilt_pts([(-170, -118), (170, -118), (170, -92), (-170, -92)]), self.hat, w=6)
                poly(tilt_pts([(-100, -118), (100, -118), (92, -300), (-92, -300)]), self.hat, w=6)
                poly(tilt_pts([(-100, -150), (100, -150), (100, -125), (-100, -125)]), (190, 50, 50), outline=False)

        pts = {k: (P(*v)[0] / SS, P(*v)[1] / SS) for k, v in
               {"handF": hF, "handB": hB, "head": (hx, hy)}.items()}
        im = im.resize((int(W), int(H)), Image.LANCZOS)
        return im, (cx * scale, cy * scale), pts
