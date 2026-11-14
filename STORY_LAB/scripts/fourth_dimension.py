"""'What If You Could See the Fourth Dimension?' - full-length landscape YouTube video (2560x1440).

Every phrase of the am_michael voiceover gets a scene picked by keyword (ROUTES), and each scene is cut
into ~0.75 s shots with a different camera framing (fd_kit.cv), so the picture never sits still.
"""
import math, os, re, random
from engine import *
from engine import _font
import cast
import fd_kit as K
from fd_kit import cv, you, sam, hand, big_eye, heart, arrow, sphere, tag

ROOT = os.path.dirname(HERE)
story = Story("fourth_dimension", ROOT)
story.music_style = "ambient"
story.whoosh_gain = 0.16
SHOT_LEN = float(os.environ.get("SHOT_LEN", 0.74))
MAX_SHOTS = 1000


# ============================================================================ scene templates
# each: fn(f, k, ph)  k = shot index inside the phrase-scene (camera variant), ph = phrase info

def T_point(f, k, ph):
    K.bg_paper(f, k)
    cv(f, k, ((960, 560), (960, 420)))
    c = f.ctx
    word = ph["text"].lower()
    dirs = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0), "forward": (0.6, 0.5), "back": (-0.6, -0.5)}
    d = (0, -1)
    for w, v in dirs.items():
        if re.search(r"\b%s\b" % w, word):
            d = v
    arms = "up" if d[1] < -0.5 else ("down" if d[1] > 0.5 else "point")
    K.you(f.ctx, 960, 900, 1.6, expr="happy", arms=arms, t=f.t, fd=1 if d[0] >= 0 else -1, look=(d[0], d[1]))
    if d[1] > 0.5:
        arrow(c, 1180, 560, 1180, 960, K.GOLD, 22)
    elif d[1] < -0.5:
        arrow(c, 960, 260, 960, 60, K.GOLD, 22)
    else:
        arrow(c, 960 + d[0] * 260, 600 + d[1] * 200, 960 + d[0] * 600, 600 + d[1] * 420, K.GOLD, 22)
    vignette(f, 0.3)


def T_axes(f, k, ph):
    K.bg_space(f, k)
    cv(f, k, ((960, 540),))
    c = f.ctx
    t = f.t
    for i, (dx, dy, col) in enumerate(((1, 0, (1, 0.4, 0.4)), (-1, 0, (1, 0.4, 0.4)), (0, -1, (0.4, 1, 0.5)), (0, 1, (0.4, 1, 0.5)),
                                       (0.62, 0.42, (0.45, 0.65, 1)), (-0.62, -0.42, (0.45, 0.65, 1)))):
        g = pop(f.plt - i * 0.06, 0.3)
        arrow(c, 960, 560, 960 + dx * 380 * g, 560 + dy * 330 * g, col, 18)
    K.you(c, 960, 700, 0.9, expr="smile", t=t)
    if "three" in ph["text"].lower():
        text3d(f, "3 DIMENSIONS", 960, 140, 90, t=f.plt)
    elif "six" in ph["text"].lower():
        text3d(f, "6 DIRECTIONS", 960, 140, 90, t=f.plt)


def T_seventh(f, k, ph):
    K.bg_space(f, k + 3)
    cv(f, k, ((960, 540), (1300, 380)))
    c = f.ctx
    for dx, dy in ((1, 0), (-1, 0), (0, -1), (0, 1)):
        arrow(c, 960, 560, 960 + dx * 300, 560 + dy * 260, (0.7, 0.7, 0.8), 14, 0.5)
    a = 0.5 + 0.5 * math.sin(f.t * 3)
    K.dashed_arrow(c, 960, 560, 1450, 260, K.VIO, 16, 0.6 + 0.4 * a, f.t)
    K.qmark(f, 1520, 230, 150, f.plt)
    K.you(c, 960, 760, 0.8, expr="doubt", arms="shrug", t=f.t)


def T_safe(f, k, ph):
    K.bg_room(f)
    cv(f, k, ((960, 560), (980, 520)))
    c = f.ctx
    see = ease(f.plt / 0.6)
    K.safe(c, 960, 640, 1.5, see, f.t)
    K.you(c, 450, 900, 1.25, expr="surprise", t=f.t, fd=1, look=(1, 0))
    vignette(f, 0.35)


def T_dollhouse(f, k, ph):
    K.bg(f, "#9FD3F2", "#FCEFD6")
    cv(f, k, ((960, 560), (800, 500), (1100, 520)))
    c = f.ctx
    c.rectangle(-2000, 900, 6000, 2000)
    fill(c, (0.5, 0.75, 0.4))
    K.dollhouse(c, 960, 920, 1.0, ease(f.plt / 0.7), f.t)
    vignette(f, 0.25)


def T_heart_chest(f, k, ph):
    K.bg(f, "#1A1030", "#3A2050")
    cv(f, k, ((960, 560), (980, 430)))
    K.person_layers(f.ctx, 960, 980, 2.1, f.t, layer=3)
    vignette(f, 0.4)


def T_steal_heart(f, k, ph):
    K.bg_dark(f)
    cv(f, k, ((960, 540), (1000, 420)))
    c = f.ctx
    x, y, s = 960, 1000, 2.0
    you(c, x, y, s, expr="worried", t=f.t, alpha=0.6)
    hx, hy = K.chest(x, y, s)
    lift = ease(clamp((f.plt - 0.2) / 0.8))
    K.heart(c, hx + lift * 260, hy - lift * 200, 0.8, f.t)
    K.hand(c, hx + 150 + lift * 260, hy - 110 - lift * 200, 0.9, 0.75, lift, a=0.9)
    vignette(f, 0.55)


def T_title(f, k, ph):
    K.bg_space(f, 9)
    cv(f, k, ((960, 540),), wide=True)
    c = f.ctx
    K.tesseract(c, 960, 360, 220, f.t, K.NEON)
    f.screen()
    text3d(f, "THE FOURTH DIMENSION", 960, 760, 120, t=f.plt, max_w=1600)


def T_not_time(f, k, ph):
    K.bg_paper(f, 2)
    cv(f, k, ((700, 540), (1200, 540)), wide=True)
    c = f.ctx
    # clock with red X
    c.arc(620, 520, 230, 0, 2 * math.pi)
    fs(c, (1, 1, 1), 12)
    for i in range(12):
        a = i * math.pi / 6
        c.move_to(620 + math.cos(a) * 190, 520 + math.sin(a) * 190)
        c.line_to(620 + math.cos(a) * 210, 520 + math.sin(a) * 210)
        stroke(c, 8)
    for ln, sp in ((150, 0.5), (110, 0.06)):
        a = f.t * sp * 2 * math.pi
        c.move_to(620, 520)
        c.line_to(620 + math.sin(a) * ln, 520 - math.cos(a) * ln)
        stroke(c, 12)
    g = ease(f.plt / 0.3)
    for sgn in (-1, 1):
        c.move_to(620 - 220 * g, 520 + sgn * 220 * g)
        c.line_to(620 + 220 * g, 520 - sgn * 220 * g)
        stroke(c, 46)
        c.move_to(620 - 220 * g, 520 + sgn * 220 * g)
        c.line_to(620 + 220 * g, 520 - sgn * 220 * g)
        stroke(c, 28, (0.9, 0.2, 0.25))
    K.dashed_arrow(c, 1150, 760, 1550, 330, K.VIO, 16, 1, f.t)
    text3d(f, "SPACE", 1400, 180, 90, t=f.plt - 0.2)


def T_roadmap(f, k, ph):
    K.bg(f, "#221636", "#3B2650")
    cv(f, k, ((960, 540),), wide=True)
    c = f.ctx
    txt = ph["text"].lower()
    hi = 0
    for i, w in enumerate(("fewer", "eyes", "do", "something else", "stuck")):
        if w in txt:
            hi = i
    xs = [260, 610, 960, 1310, 1660]
    for i, x in enumerate(xs):
        on = i == hi
        rrect(c, x - 150, 330, 300, 300, 40)
        fs(c, (0.98, 0.93, 0.8) if on else (0.45, 0.4, 0.55), 9)
        if i == 0:
            sam(c, x, 470, 0.9, "smile", f.t)
        elif i == 1:
            K.big_eye(c, x, 480, 0.4, f.t, col=(0.4, 0.6, 1.0))
        elif i == 2:
            K.cube(c, x, 480, 60, f.t)
        elif i == 3:
            K.big_eye(c, x, 480, 0.4, f.t)
        else:
            K.solar(c, x, 480, 0.3, f.t)
        if on:
            glow(c, x, 480, 260, K.GOLD, 0.25)
    text3d(f, ["FLATLAND", "YOUR EYES", "POWERS", "THE WATCHER", "WHY THREE?"][hi], 960, 800, 90, t=f.plt)


def T_chapter(f, k, ph):
    K.bg_space(f, 20 + k)
    cv(f, k, ((960, 540),), wide=True)
    c = f.ctx
    K.tesseract(c, 960, 540, 420, f.t * 0.6, K.VIO, a=0.25)
    m = re.match(r"(Part \w+|Epilogue)\.?\s*(.*)", ph["chunk"])
    head = m.group(1).upper() if m else "PART"
    sub = (m.group(2) if m else "").rstrip(".").upper()
    f.screen()
    tag(c, head, 960, 380, 54, (0.98, 0.93, 0.8))
    if sub:
        text3d(f, sub, 960, 600, 120, t=f.plt - 0.1, max_w=1600)


def T_book(f, k, ph):
    K.bg_room(f)
    cv(f, k, ((960, 540), (760, 500), (1250, 520)))
    c = f.ctx
    txt = ph["text"].lower()
    cast.draw(c, "abbott", 520, 960, 1.5, expr="smile", arms="hold", t=f.t, fd=1)
    K.book(c, 1200, 560, 1.0, 1.0 if ("flat" in txt or "called" in txt) else 0.0)
    if "eighteen" in txt:
        text3d(f, "1884", 1500, 200, 120, t=f.plt)
    vignette(f, 0.35)


def _flatland(f, k, tilt=0.42, sam_x=0, sam_expr="smile", walk=0.0, door=1.0, extra=None, pts=((960, 560),)):
    K.bg_space(f, 4) if k % 3 == 2 else K.bg(f, "#1E2244", "#4B3A6E")
    cv(f, k, pts)
    c = f.ctx
    K.plane_begin(c, 960, 600, tilt, -0.15)
    K.sheet(c)
    K.flat_house(c, 380, -60, 0.9, door)
    K.flat_tree(c, -480, -250, 1.0)
    K.flat_tree(c, -560, 220, 0.8)
    K.flat_circle(c, 600, 280, 60)
    sam(c, sam_x, 120, 1.0, sam_expr, f.t, walk=walk)
    if extra:
        extra(c)
    c.restore()


def T_flatland(f, k, ph):
    _flatland(f, k, tilt=[0.42, 0.55, 0.35][k % 3], sam_x=wob(f.t, 0.1, 200), walk=1.0)


def T_sam_intro(f, k, ph):
    K.bg(f, "#F8E9C8", "#E5C99A")
    cv(f, k, ((960, 520),))
    c = f.ctx
    sam(c, 960, 560, 2.6, ["happy", "smile", "wink"][k % 3], f.t)
    if "sam" in ph["text"].lower():
        text3d(f, "SAM", 960, 160, 130, t=f.plt)
    else:
        tag(f.ctx, "a small square", 960, 160, 56)


def T_sam_moves(f, k, ph):
    K.bg(f, "#F3E3C3", "#E0C192")
    cv(f, k, ((960, 540),))
    c = f.ctx
    txt = ph["text"].lower()
    if "up" in txt:
        sam(c, 960, 600, 2.0, "doubt", f.t)
        K.qmark(f, 1300, 300, 220, f.plt)
        K.dashed_arrow(c, 960, 420, 960, 120, (0.6, 0.6, 0.7), 14, 0.6, f.t)
    else:
        lr = "left" in txt or "right" in txt
        dx = wob(f.t, 0.6, 160) if lr else 0
        dy = 0 if lr else wob(f.t, 0.6, 120)
        sam(c, 960 + dx, 600 + dy, 1.8, "happy", f.t, walk=1)
        if lr:
            arrow(c, 760, 600, 360, 600, K.GOLD)
            arrow(c, 1160, 600, 1560, 600, K.GOLD)
        else:
            arrow(c, 960, 420, 960, 140, K.GOLD)
            arrow(c, 960, 800, 960, 1040, K.GOLD)


def T_sam_view(f, k, ph):
    K.bg(f, "#1D1A33", "#3A2E58")
    cv(f, k, ((960, 540),), wide=True)
    c = f.ctx
    # top: the world from above, Sam's eye-line ray
    K.plane_begin(c, 960, 360, 0.5, 0)
    K.sheet(c, 1500, 560, grid=False)
    K.flat_house(c, 300, 0, 0.6)
    K.flat_circle(c, -300, -40, 70)
    sam(c, -650, 60, 0.8, "smile", f.t)
    c.restore()
    segs = [(0.0, 0.12, (0.3, 0.25, 0.45)), (0.12, 0.32, (0.35, 0.5, 0.85)), (0.32, 0.55, (0.28, 0.25, 0.4)),
            (0.55, 0.82, (0.45, 0.35, 0.7)), (0.82, 1.0, (0.3, 0.25, 0.45))]
    shift = wob(f.t, 0.2, 0.04)
    segs = [(clamp(a + shift), clamp(b + shift), col) for a, b, col in segs]
    K.edge_view(c, 260, 1660, 840, segs, f.t, 90)
    tag(c, "what Sam sees", 960, 700, 40, (0.98, 0.93, 0.8))


def T_sam_house(f, k, ph):
    txt = ph["text"].lower()
    closing = "lock" in txt or "gap" in txt or "enough" in txt or "nothing" in txt
    door = 1 - ease(f.plt / 0.6) if closing else 1.0

    def extra(c):
        if closing:
            K.padlock(c, 380, 160, 0.6)
    _flatland(f, k, 0.6, sam_x=380, sam_expr="happy", door=door, extra=extra, pts=((1150, 560), (960, 560)))


def T_hand_flatland(f, k, ph):
    K.bg(f, "#1E2244", "#4B3A6E")
    cv(f, k, ((1150, 500), (960, 540)))
    c = f.ctx
    K.plane_begin(c, 960, 640, 0.45, -0.15)
    K.sheet(c)
    K.flat_house(c, 380, -60, 0.9, 0)
    sam(c, 380, -40, 0.9, "shock", f.t)
    c.restore()
    d = ease(f.plt / 0.6)
    if "vanish" in ph["text"].lower():
        d = 1 - ease(f.plt / 0.5)
    K.hand(c, 1360, -200 + d * 640, 1.0, 0.05)
    vignette(f, 0.35)


def T_you_are_sam(f, k, ph):
    K.bg_dark(f)
    cv(f, k, ((960, 600), (960, 500)), wide=True)
    c = f.ctx
    big_eye(c, 960, 230, 0.8, f.t, look=(0, 1), a=ease(f.plt / 0.8))
    you(c, 760, 1000, 1.3, expr="worried", t=f.t, look=(0, -1))
    sam(c, 1180, 880, 1.2, "worried", f.t, look=(0, -1))


def T_eye_section(f, k, ph):
    K.bg(f, "#14213D", "#2B3F6B")
    cv(f, k, ((960, 540), (1150, 540), (700, 540)))
    K.eye_section(f.ctx, 1060, 540, 1.1, f.t, ease(f.plt / 0.6))
    if "retina" in ph["text"].lower():
        tag(f.ctx, "RETINA", 1390, 200, 54)
    if "flat" in ph["text"].lower() or "screen" in ph["text"].lower():
        tag(f.ctx, "a 2D screen", 1390, 200, 54)


def T_brain(f, k, ph):
    K.bg(f, "#2B1E40", "#4E3A6E")
    cv(f, k, ((960, 540),), wide=True)
    c = f.ctx
    # brain blob
    for dx, dy, r in ((-90, -20, 150), (90, -30, 150), (0, -110, 140), (0, 60, 130)):
        c.arc(960 + dx, 480 + dy, r, 0, 2 * math.pi)
        fs(c, (0.98, 0.7, 0.75), 9)
    for i in range(6):
        c.move_to(860 + i * 40, 380)
        c.curve_to(820 + i * 40, 460, 900 + i * 40, 520, 860 + i * 40, 600)
        stroke(c, 6, (0.8, 0.45, 0.55))
    items = ["two eyes", "shadows", "experience"]
    for i, s in enumerate(items):
        if f.plt > i * 0.2:
            tag(c, s, 420 + i * 540, 800, 48, [(0.6, 0.8, 1.0), (0.8, 0.8, 0.85), (1.0, 0.85, 0.5)][i])
    text3d(f, "DEPTH = A GUESS", 960, 140, 80, t=f.plt)


def T_ladder(f, k, ph):
    K.bg(f, "#1A1730", "#33285A")
    cv(f, k, ((960, 500),), wide=True)
    txt = ph["text"].lower()
    hi = 1
    if "one" in txt and "sam" in txt:
        hi = 0
    if "solid" in txt or "block" in txt or "four" in txt or "further" in txt or "through" in txt:
        hi = 2
    K.retina_ladder(f.ctx, 960, 470, 1.0, hi, f.t)


def T_box_inside(f, k, ph):
    K.bg(f, "#F4E3C0", "#D9B98A")
    cv(f, k, ((960, 560), (1000, 520)))
    c = f.ctx
    txt = ph["text"].lower()
    see = 0.0 if "surface" in txt else ease(f.plt / 0.5)

    def inside(c):
        K.gold_bar(c, 900, 700, 1.4)
        sphere(c, 1060, 640, 60, (0.9, 0.3, 0.35))
        K.keys(c, 960, 560, 0.6)
    K.box(c, 700, 420, 520, 400, 120, (0.82, 0.6, 0.35), see, inside)
    if see > 0.5:
        K.big_eye(c, 1560, 300, 0.35, f.t, look=(-1, 1))


def T_xray(f, k, ph):
    K.bg(f, "#101A2A", "#24364F")
    cv(f, k, ((960, 560),), wide=True)
    c = f.ctx
    # left: x-ray (faint, see-through)
    c.rectangle(80, 120, 820, 860)
    fs(c, (0.1, 0.2, 0.3), 7)
    you(c, 490, 880, 1.6, expr="flat", t=f.t, alpha=0.25, tint=((0.6, 0.9, 1.0), 0.8))
    tag(c, "X-RAY: faint", 490, 200, 42, (0.6, 0.85, 1.0))
    # right: 4D sight (everything, full colour)
    c.rectangle(1020, 120, 820, 860)
    fs(c, (0.98, 0.93, 0.8), 7)
    K.person_layers(c, 1430, 900, 1.6, f.t, layer=3)
    tag(c, "4D: everything", 1430, 200, 42)


def T_layers(f, k, ph):
    K.bg(f, "#1E1430", "#3C2756")
    cv(f, k, ((960, 560), (960, 480)), wide=True)
    txt = ph["text"].lower()
    layer = 3
    for i, w in enumerate(("skin", "muscle", "bones", "heart")):
        if w in txt:
            layer = i
    K.person_layers(f.ctx, 960, 1010, 2.3, f.t, layer=max(layer, int(clamp(f.plt / 0.25, 0, 3))))


def T_hidden(f, k, ph):
    K.bg(f, "#2A1C3E", "#46305F")
    cv(f, k, ((960, 560),), wide=True)
    c = f.ctx
    t = f.plt
    # pocket, vault, body
    rrect(c, 260, 380, 320, 340, 40)
    fs(c, (0.35, 0.45, 0.7), 8)
    K.cash(c, 420, 560, 1.0)
    K.safe(c, 960, 600, 0.9, 1.0, f.t)
    K.person_layers(c, 1560, 820, 1.3, f.t, 3)
    K.big_eye(c, 960, 170, 0.35, f.t, look=(0, 1))
    tags = ["pocket", "vault", "body"]
    for i, s in enumerate(tags):
        if t > i * 0.2:
            tag(c, s, [420, 960, 1560][i], 860, 44)


def T_ball_plane(f, k, ph):
    K.bg(f, "#1C2340", "#3D4778")
    cv(f, k, ((760, 540), (1350, 560), (960, 540)), wide=True)
    c = f.ctx
    # side view: plane as a line, ball moving down through it
    p = clamp(f.plt / max(f.pdur, 0.6) * 0.9 + 0.05 + (ph["idx"] % 3) * 0.3) % 1.0
    by = lerp(150, 950, p)
    R = 130
    c.move_to(150, 560)
    c.line_to(1100, 560)
    stroke(c, 22)
    c.move_to(150, 560)
    c.line_to(1100, 560)
    stroke(c, 10, (0.98, 0.9, 0.7))
    sphere(c, 620, by, R, (0.5, 0.75, 1.0))
    # Sam's view inset: circle of slice
    d = abs(by - 560)
    r = math.sqrt(max(0, R * R - d * d))
    rrect(c, 1200, 220, 600, 600, 40)
    fs(c, K.PAPER, 9)
    if r > 0:
        K.flat_circle(c, 1500, 520, r * 1.4, (0.5, 0.75, 1.0))
    else:
        c.arc(1500, 520, 6, 0, 2 * math.pi)
        fill(c, INK, 0.3)
    sam(c, 1320, 760, 0.5, "shock" if r > 0 else "smile", f.t)
    tag(c, "Sam's world", 1500, 260, 36, (0.98, 0.93, 0.8))


def T_miracle(f, k, ph):
    K.bg(f, "#F7E6C4", "#E2C390")
    cv(f, k, ((960, 540),))
    c = f.ctx
    sam(c, 760, 620, 2.0, ["shock", "surprise", "happy"][k % 3], f.t)
    r = 160 * math.sin(clamp(f.plt / 1.2) * math.pi)
    K.flat_circle(c, 1300, 560, max(4, r), (0.5, 0.75, 1.0))
    for i in range(8):
        a = i * math.pi / 4 + f.t
        c.move_to(1300 + math.cos(a) * (r + 40), 560 + math.sin(a) * (r + 40))
        c.line_to(1300 + math.cos(a) * (r + 80), 560 + math.sin(a) * (r + 80))
        stroke(c, 8, K.GOLD)


def T_hypersphere(f, k, ph):
    K.bg_room(f, night=k % 2 == 1)
    cv(f, k, ((1060, 460), (960, 540)))
    c = f.ctx
    u = clamp(f.plt / max(f.pdur, 0.5))
    seq = ph["idx"] % 4
    w = lerp(-1, 1, (u + seq * 0.25) % 1.0)
    r = 220 * math.sqrt(max(0, 1 - w * w))
    glow(c, 1100, 420, 260, (0.6, 0.8, 1.0), 0.35)
    sphere(c, 1100, 420, r, (0.65, 0.55, 1.0))
    if r < 10:
        c.arc(1100, 420, 6, 0, 2 * math.pi)
        fill(c, (1, 1, 1))
    you(c, 520, 900, 1.3, expr="shock", t=f.t, fd=1, look=(1, -0.4))


def T_tesseract(f, k, ph):
    K.bg_space(f, 30 + k)
    cv(f, k, ((960, 540),))
    c = f.ctx
    K.tesseract(c, 960, 520, 330, f.t, [K.NEON, K.VIO, (1, 0.8, 0.4)][k % 3])
    txt = ph["text"].lower()
    if "tesseract" in txt:
        text3d(f, "TESSERACT", 960, 110, 100, t=f.plt)
    elif "shadow" in txt:
        tag(c, "only a shadow", 960, 110, 50)


def T_shadow_hand(f, k, ph):
    K.bg(f, "#E9D7B8", "#C9AF86")
    cv(f, k, ((960, 540),))
    c = f.ctx
    # wall with shadow of a tesseract cast from a lamp
    c.rectangle(1050, 100, 760, 820)
    fs(c, (0.9, 0.85, 0.75), 8)
    glow(c, 300, 300, 300, (1, 0.9, 0.5), 0.6)
    c.arc(300, 300, 40, 0, 2 * math.pi)
    fs(c, (1, 0.95, 0.6), 6)
    K.cube(c, 650, 520, 90, f.t)
    c.save()
    c.push_group()
    K.cube(c, 1430, 520, 170, f.t, (0.2, 0.15, 0.25))
    c.pop_group_to_source()
    c.paint_with_alpha(0.55)
    c.restore()


def T_bed(f, k, ph):
    K.bg(f, "#F6C98B", "#F9E7C5")
    cv(f, k, ((960, 560), (800, 520)))
    c = f.ctx
    c.rectangle(1300, 160, 380, 300)
    fs(c, (0.75, 0.88, 1.0), 9)
    K.glow(c, 1490, 330, 300, (1, 0.85, 0.5), 0.5)
    rrect(c, 300, 680, 900, 160, 30)
    fs(c, (0.55, 0.38, 0.26), 9)
    rrect(c, 320, 600, 860, 120, 40)
    fs(c, (0.4, 0.6, 0.95), 8)
    rrect(c, 340, 560, 200, 80, 30)
    fs(c, (1, 1, 1), 6)
    sit = ease(f.plt / 0.5)
    you(c, 560, 720 - 60 * sit, 1.0, expr="surprise", arms="up" if sit > 0.5 else "down", t=f.t, fd=1)
    if "changed" in ph["text"].lower():
        for i in range(6):
            a = i * 1.05 + f.t
            sphere(c, 900 + math.cos(a) * 200, 400 + math.sin(a) * 120, 14, K.VIO)


def T_hinton(f, k, ph):
    K.bg_room(f)
    cv(f, k, ((960, 520), (1250, 460)))
    c = f.ctx
    K.chalkboard(c, 1220, 430, 900, 520)
    rv = ease(f.plt / 0.35)
    txt = ph["text"].lower()
    K.chalk(c, "ANA", 1050, 330, 110, reveal=rv)
    K.chalk(c, "KATA", 1050, 560, 110, reveal=rv)
    K.dashed_arrow(c, 1300, 520, 1500, 250, (0.95, 0.95, 0.9), 10, 0.9, f.t)
    K.dashed_arrow(c, 1300, 300, 1500, 600, (0.95, 0.95, 0.9), 10, 0.9, f.t)
    cast.draw(c, "hinton", 420, 960, 1.5, expr="smile", arms="point", t=f.t, fd=1)
    if "century" in txt:
        tag(c, "Charles Hinton", 420, 200, 50)


def T_step_ana(f, k, ph):
    K.bg_space(f, 40 + k)
    cv(f, k, ((960, 540),))
    c = f.ctx
    p = ease(f.plt / 0.8)
    for i in range(10):
        r = 100 + i * 90 + (f.t * 120) % 90
        c.arc(960, 600, r, 0, 2 * math.pi)
        stroke(c, 4, K.VIO, 0.4 * (1 - i / 10))
    you(c, 960, 900 - 120 * p, 1.4, expr="happy", legs="walk", t=f.t, fd=1, tint=(K.VIO, 0.25 * p))
    text3d(f, "ANA", 960, 160, 110, t=f.plt, top=K.VIO, side=shade(K.VIO, 0.5))


def T_flower(f, k, ph):
    K.bg_space(f, 50)
    cv(f, k, ((960, 560), (960, 420), (760, 520)))
    c = f.ctx
    fl = ease((f.t - ph["run_t0"]) / 1.2)
    K.dollhouse(c, 960, 860, 0.9, 1.0, f.t, keys_on="keys" in ph["text"].lower(), flower=fl)
    vignette(f, 0.35)


def T_keys(f, k, ph):
    K.bg_room(f)
    cv(f, k, ((960, 560), (1100, 520)))
    c = f.ctx
    c.rectangle(560, 640, 900, 360)
    fs(c, (0.95, 0.95, 0.95), 9)
    c.rectangle(540, 610, 940, 40)
    fs(c, (0.55, 0.55, 0.6), 7)
    glow(c, 1000, 580, 140, K.GOLD, 0.6)
    K.keys(c, 1000, 580, 0.9, 0.2)
    txt = ph["text"].lower()
    if "kata" in txt or "standing" in txt or "beside" in txt:
        a = ease(f.plt / 0.4)
        you(c, 1400, 1000, 1.4, expr="happy", arms="point", t=f.t, fd=-1, alpha=a)
        for i in range(8):
            ang = i * math.pi / 4
            c.move_to(1400 + math.cos(ang) * 200 * a, 700 + math.sin(ang) * 200 * a)
            c.line_to(1400 + math.cos(ang) * 260 * a, 700 + math.sin(ang) * 260 * a)
            stroke(c, 8, K.VIO, 1 - a * 0.5)
    if "locked" in txt:
        K.padlock(c, 400, 400, 1.0)


def T_door(f, k, ph):
    K.bg_room(f)
    cv(f, k, ((960, 520),))
    c = f.ctx
    rrect(c, 760, 160, 400, 640, 12)
    fs(c, (0.55, 0.35, 0.22), 10)
    for yy in (220, 460):
        rrect(c, 810, yy, 300, 200, 10)
        stroke(c, 6, (0.35, 0.22, 0.14))
    K.padlock(c, 1080, 500, 0.6)
    txt = ph["text"].lower()
    if "suggestion" in txt:
        you(c, 960, 1000, 1.4, expr="smug", t=f.t, alpha=0.75, tint=(K.VIO, 0.3))
        text3d(f, "JUST A SUGGESTION", 960, 120, 70, t=f.plt)
    else:
        tag(c, "never opened" if "door" in txt else "never turned", 960, 90, 50)


def T_shoe(f, k, ph):
    K.bg(f, "#CDE7F5", "#F7EEDB")
    cv(f, k, ((960, 560), (900, 480)))
    c = f.ctx
    c.rectangle(-2000, 760, 6000, 2000)
    fill(c, (0.6, 0.6, 0.62))
    txt = ph["text"].lower()
    knot = 1.0
    if "apart" in txt or "again" in txt or "slides" in txt:
        knot = 1 - ease((f.t - ph["run_t0"]) / 0.6) if "apart" in txt else 1 - ease(f.plt / 0.6)
    K.shoe(c, 960, 640, 1.4, knot, f.t)
    if "again" in txt:
        tag(c, "again.", 1500, 200, 60)


def T_knot(f, k, ph):
    K.bg(f, "#1F2A44", "#3A4E7A")
    cv(f, k, ((960, 540),))
    c = f.ctx
    txt = ph["text"].lower()
    loose = 0.0 if "only holds" in txt or "cannot pass" in txt else ease((f.t - ph["run_t0"]) / 1.2)
    K.rope_knot(c, 960, 560, 1.4, loose, f.t)
    if loose > 0.05:
        K.dashed_arrow(c, 960, 560, 1250, 230, K.VIO, 12, loose, f.t)
        tag(c, "+1 direction", 1400, 200, 44, K.VIO, (1, 1, 1))
    if "nothing stays" in txt:
        text3d(f, "NOTHING STAYS TIED", 960, 800, 80, t=f.plt)


def T_footprint(f, k, ph):
    K.bg(f, "#1E2244", "#4B3A6E")
    cv(f, k, ((960, 560), (1100, 520)))
    c = f.ctx
    txt = ph["text"].lower()
    flip = 0.0
    if "flip" in txt or "lay it back" in txt or "now a right" in txt or "stares" in txt or "impossible" in txt:
        flip = ease(f.plt / 0.7) if "flip" in txt else 1.0
    lift = math.sin(flip * math.pi)
    K.plane_begin(c, 960, 640, 0.5, -0.1)
    K.sheet(c)
    sam(c, -380, 60, 1.0, "shock" if flip > 0.5 else "smile", f.t)
    c.restore()
    # footprint: flips via x-scale through zero, lifted above the sheet
    c.save()
    c.translate(1120, 620 - lift * 300)
    sx = math.cos(flip * math.pi)
    c.scale(sx if abs(sx) > 0.02 else 0.02, 0.6)
    K.footprint(c, 0, 0, 1.6)
    c.restore()
    if lift > 0.05:
        K.hand(c, 1120, 620 - lift * 300 - 330, 0.8, 0, 0.5)
    tag(c, "LEFT" if flip < 0.5 else "RIGHT", 1120, 120, 50, (0.98, 0.93, 0.8))


def T_powers(f, k, ph):
    K.bg(f, "#25183A", "#4A2E66")
    cv(f, k, ((960, 540),), wide=True)
    c = f.ctx
    xs = (380, 960, 1540)
    for i, x in enumerate(xs):
        g = pop(f.plt - i * 0.12, 0.3)
        if g <= 0:
            continue
        c.save()
        c.translate(x, 470)
        c.scale(g, g)
        rrect(c, -230, -230, 460, 460, 50)
        fs(c, (0.98, 0.93, 0.8), 10)
        if i == 0:
            K.dollhouse(c, 0, 120, 0.3, 1.0, f.t)
        elif i == 1:
            K.rope_knot(c, 0, 0, 0.4, 0.6 + 0.4 * math.sin(f.t), f.t)
        else:
            K.footprint(c, -70, 30, 0.8)
            K.footprint(c, 80, 30, 0.8, mirror=True)
        c.restore()
        tag(c, ["WALLS", "KNOTS", "MIRRORS"][i], x, 820, 50)


def T_comment(f, k, ph):
    K.bg(f, "#F2E4C8", "#DCC197")
    cv(f, k, ((960, 540),), wide=True)
    c = f.ctx
    K.bubble(c, 960, 420, 1300, 380)
    _font(c, 64)
    msg = "Which ONE would you keep?"
    e = c.text_extents(msg)
    c.move_to(960 - e.x_advance / 2, 330)
    c.set_source_rgb(*INK)
    c.show_text(msg)
    for i, (s, col) in enumerate((("Walls", (0.5, 0.75, 1.0)), ("Knots", (0.98, 0.75, 0.35)), ("Mirrors", K.VIO))):
        x = 560 + i * 400
        tag(c, s, x, 470, 48, col)
    you(c, 400, 1040, 1.1, expr="smile", arms="chin", t=f.t, fd=1)
    sam(c, 1560, 900, 1.0, "happy", f.t)
    text3d(f, "TELL ME IN THE COMMENTS", 960, 730, 64, t=f.plt, max_w=1100)


def T_watcher(f, k, ph):
    K.bg_dark(f)
    cv(f, k, ((960, 420), (960, 600)))
    c = f.ctx
    big_eye(c, 960, 260, 0.9, f.t, look=(0, 1), a=ease(f.plt / 0.5))
    you(c, 960, 1020, 1.3, expr="worried", t=f.t, look=(0, -1))
    vignette(f, 0.6)


def T_outline(f, k, ph):
    K.bg(f, "#F4E6CB", "#D7BC90")
    cv(f, k, ((960, 560), (980, 440)))
    c = f.ctx
    # you as an outline drawing on paper, heart drawn inside
    c.save()
    c.translate(960, 560)
    c.scale(1.0, 1.0)
    rrect(c, -380, -460, 760, 920, 20)
    fs(c, K.PAPER, 9)
    c.restore()
    you(c, 960, 960, 1.8, expr="flat", t=f.t, alpha=0.18)
    hx, hy = K.chest(960, 960, 1.8)
    heart(c, hx, hy, 0.6, f.t)
    big_eye(c, 1600, 220, 0.3, f.t, look=(-1, 1))


def T_coin_sam(f, k, ph):
    K.bg(f, "#1E2244", "#4B3A6E")
    cv(f, k, ((960, 540),))
    c = f.ctx
    K.plane_begin(c, 960, 640, 0.55, -0.1)
    K.sheet(c, 1300, 900)
    sam(c, 0, 0, 2.2, "surprise", f.t)
    c.restore()
    lift = ease(f.plt / 0.7)
    sphere(c, 960, 600 - lift * 330, 40, K.GOLD)
    K.hand(c, 960, 600 - lift * 330 - 260, 0.6, 0, lift)


def T_no_trace(f, k, ph):
    K.bg_dark(f)
    cv(f, k, ((960, 540),))
    c = f.ctx
    you(c, 640, 1000, 1.7, expr="flat", t=f.t)
    hx, hy = K.chest(640, 1000, 1.7)
    lift = ease(f.plt / 0.6)
    heart(c, hx + lift * 600, hy - lift * 200, 0.7, f.t)
    words = ["NO INCISION", "NO WOUND", "NO TRACE"]
    txt = ph["text"].lower()
    for i, w in enumerate(words):
        if w.split()[1].lower() in txt:
            text3d(f, w, 1300, 200 + i * 130, 70, t=f.plt, top=(0.95, 0.3, 0.35), side=(0.4, 0.05, 0.1))


def T_flip_you(f, k, ph):
    K.bg_dark(f)
    cv(f, k, ((960, 540),))
    c = f.ctx
    p = ease(f.plt / 0.45)
    c.save()
    c.translate(960, 0)
    sx = math.cos(p * math.pi)
    c.scale(sx if abs(sx) > 0.03 else 0.03, 1)
    c.translate(-960, 0)
    you(c, 960, 960 - math.sin(p * math.pi) * 120, 1.7, expr="worried", arms="up", t=f.t)
    c.restore()
    big_eye(c, 960, 160, 0.45, f.t, look=(0, 1))
    K.dashed_arrow(c, 600, 500, 1320, 500, K.VIO, 10, 0.7, f.t)


def T_heart_side(f, k, ph):
    K.bg(f, "#2A1630", "#4A2440")
    cv(f, k, ((960, 540),))
    c = f.ctx
    # torso diagram
    rrect(c, 640, 180, 640, 760, 160)
    fs(c, (0.98, 0.9, 0.82), 10)
    c.move_to(960, 200)
    c.line_to(960, 920)
    c.save()
    c.set_dash([16, 14])
    stroke(c, 5, (0.6, 0.5, 0.5))
    c.restore()
    p = ease(f.plt / 0.8) if "right side" in ph["text"].lower() or "mirror" in ph["text"].lower() else 0.0
    heart(c, lerp(1100, 820, p), 470, 1.0, f.t)
    tag(c, "LEFT", 1120, 120, 40, (0.85, 0.85, 0.9))
    tag(c, "RIGHT", 800, 120, 40, (0.85, 0.85, 0.9))


def T_molecules(f, k, ph):
    K.bg(f, "#122A2A", "#21474A")
    cv(f, k, ((960, 540),), wide=True)
    c = f.ctx
    K.molecule_hand(c, 620, 520, 1.6)
    K.molecule_hand(c, 1300, 520, 1.6, mirror=True)
    c.move_to(960, 160)
    c.line_to(960, 900)
    c.save()
    c.set_dash([20, 16])
    stroke(c, 6, (0.8, 0.95, 1.0), 0.7)
    c.restore()
    txt = ph["text"].lower()
    tag(c, "LEFT-HANDED", 620, 880, 44, (0.6, 0.9, 0.7))
    tag(c, "RIGHT-HANDED", 1300, 880, 44, (0.9, 0.75, 0.95))
    if "amino" in txt:
        text3d(f, "AMINO ACIDS: LEFT", 960, 120, 64, t=f.plt)
    elif "sugar" in txt:
        text3d(f, "SUGARS: RIGHT", 960, 120, 64, t=f.plt)


def T_food(f, k, ph):
    K.bg(f, "#3A2A2A", "#5A3F3A")
    cv(f, k, ((960, 560), (700, 600)))
    c = f.ctx
    c.rectangle(-500, 700, 3000, 600)
    fs(c, (0.55, 0.38, 0.26), 8)
    gray = ease(f.plt / 0.8)
    K.plate(c, 960, 740, 1.4, gray)
    txt = ph["text"].lower()
    starving = "starve" in txt or "waste" in txt or "every single day" in txt
    you(c, 400, 1000, 1.4, expr="sad" if starving else "worried", arms="eat" if "eat" in txt else "down", t=f.t, fd=1)
    if gray > 0.5:
        tag(c, "wrong shape", 1250, 420, 50, (0.85, 0.85, 0.85))


def T_why(f, k, ph):
    K.bg_space(f, 60 + k)
    cv(f, k, ((960, 540),))
    c = f.ctx
    K.qmark(f, 960, 420, 340, f.plt)
    txt = ph["text"].lower()
    text3d(f, "WHY THREE?" if "three" in txt or "four" in txt else "WHY NOT FOUR?", 960, 860, 100, t=f.plt - 0.15)


def T_solar(f, k, ph):
    K.bg_space(f, 70)
    cv(f, k, ((960, 540), (1200, 560), (700, 520)))
    c = f.ctx
    txt = ph["text"].lower()
    mode, jup = "stable", False
    if "nudge" in txt or "tug" in txt or "jupiter" in txt or "wobble" in txt:
        mode, jup = "wobble", True
    if "spiral" in txt or "closer" in txt or "fire" in txt or "grows" in txt or "harder" in txt:
        mode = "spiral"
    if "loose" in txt or "dark" in txt or "forever" in txt or "away" in txt:
        mode = "escape"
    if "no forgiving" in txt or "disappear" in txt:
        mode = "spiral"
    p = clamp(f.plt / max(1.2, f.pdur))
    K.solar(c, 960, 540, 1.3, f.t, mode, p, jup)
    if "forgiving" in txt and "no" not in txt:
        tag(c, "3D: forgiving", 960, 110, 46, (0.6, 0.9, 0.6))
    if "no forgiving" in txt:
        tag(c, "4D: no forgiving orbits", 960, 110, 46, (0.95, 0.5, 0.5))


def T_gravity(f, k, ph):
    K.bg(f, "#14213D", "#2B3F6B")
    cv(f, k, ((960, 540),), wide=True)
    c = f.ctx
    for cx, n, lab in ((560, 14, "3D"), (1360, 30, "4D")):
        sphere(c, cx, 540, 50, (1, 0.75, 0.3))
        for i in range(n):
            a = i * 2 * math.pi / n + f.t * 0.2
            c.move_to(cx + math.cos(a) * 70, 540 + math.sin(a) * 70)
            c.line_to(cx + math.cos(a) * 340, 540 + math.sin(a) * 340)
            stroke(c, 4, (1, 0.85, 0.5), 0.8 if lab == "3D" else 0.35)
        tag(c, lab, cx, 940, 52)
    text3d(f, "GRAVITY FADES FASTER", 960, 110, 72, t=f.plt)


def T_ehrenfest(f, k, ph):
    K.bg_room(f)
    cv(f, k, ((960, 520), (1250, 460)))
    c = f.ctx
    K.chalkboard(c, 1220, 430, 900, 520)
    rv = ease(f.plt / 0.35)
    K.chalk(c, "1917", 1220, 300, 120, reveal=rv)
    K.chalk(c, "3D + 1 = ?", 1220, 520, 90, reveal=rv)
    cast.draw(c, "ehrenfest", 420, 960, 1.5, expr="doubt", arms="chin", t=f.t, fd=1)
    tag(c, "Paul Ehrenfest", 420, 200, 50)


def T_atom(f, k, ph):
    K.bg(f, "#0F1A2E", "#1F3354")
    cv(f, k, ((960, 540), (960, 480)))
    c = f.ctx
    txt = ph["text"].lower()
    col = 0.0
    if "no stable" in txt or "could not" in txt or "same problem" in txt:
        col = ease(f.plt / 0.9)
    K.atom(c, 960, 520, 1.4, f.t, col)
    if "zoom" in txt:
        tag(c, "a single atom", 960, 110, 50)


def T_chain(f, k, ph):
    K.bg(f, "#1A1432", "#2E2458")
    cv(f, k, ((960, 540),), wide=True)
    txt = ph["text"].lower()
    if "life" in txt or "chemistry" in txt:
        K.chain_icons(f, ["NO ATOMS", "NO CHEMISTRY", "NO LIFE"], 540, 2)
    else:
        K.chain_icons(f, ["KNOTS", "PLANETS", "ATOMS"], 540, 2)


def T_untied(f, k, ph):
    K.bg_space(f, 80 + k)
    cv(f, k, ((960, 540), (560, 520), (1360, 520)), wide=True)
    c = f.ctx
    K.rope_knot(c, 480, 500, 0.5, 0.5 + 0.5 * math.sin(f.t * 2), f.t)
    K.solar(c, 960, 500, 0.45, f.t, "escape", (f.t * 0.4) % 1)
    K.atom(c, 1460, 500, 0.6, f.t, (f.t * 0.5) % 1)
    text3d(f, "NOTHING STAYS TIED", 960, 110, 84, t=f.plt)


def T_sam_tube(f, k, ph):
    K.bg(f, "#F5E3C3", "#DFC08F")
    cv(f, k, ((960, 540), (900, 540)))
    c = f.ctx
    txt = ph["text"].lower()
    cut = "two" in txt or "cut" in txt or "split" in txt or "lunch" in txt
    gap = ease(f.plt / 0.6) * 90 if cut else 0
    for side in (-1, 1):
        c.save()
        c.translate(side * gap, 0)
        c.rectangle(960 if side > 0 else 0, 0, 960, 1080)
        c.clip()
        sam(c, 960, 560, 2.6, "shock" if cut else "smile", f.t)
        c.restore()
    if "tube" in txt or cut or "eat" in txt:
        c.rectangle(940, 300, 40, 520)
        c.set_source_rgba(0.95, 0.5, 0.5, 0.8)
        c.fill()
    if "lunch" in txt:
        tag(c, "no lunch for Sam", 960, 110, 52)
    if "hawking" in txt:
        cast.draw(c, "scholar", 1600, 1000, 1.1, expr="smile", arms="point", t=f.t, fd=-1)
        tag(c, "Stephen Hawking", 1500, 300, 40)


def T_goldilocks(f, k, ph):
    K.bg(f, "#1E1A36", "#3B2E62")
    cv(f, k, ((960, 540),), wide=True)
    c = f.ctx
    txt = ph["text"].lower()
    for i, (n, lab, col) in enumerate(((2, "falls apart", (0.9, 0.5, 0.5)), (3, "just right", (0.55, 0.9, 0.55)),
                                       (4, "won't hold", (0.9, 0.5, 0.5)))):
        x = 420 + i * 540
        on = (n == 3) or ("too few" in txt and n == 2) or ("too many" in txt and n == 4)
        rrect(c, x - 220, 230, 440, 520, 40)
        fs(c, (0.98, 0.93, 0.8) if on else (0.4, 0.36, 0.5), 9)
        text3d(f, f"{n}D", x, 420, 140, t=f.plt - i * 0.1,
               top=K.GOLD if n == 3 else (0.85, 0.85, 0.9))
        tag(c, lab, x, 640, 40, col)
    glow(c, 960, 490, 330, K.GOLD, 0.15 + 0.08 * math.sin(f.t * 3))


def T_earth(f, k, ph):
    K.bg_space(f, 90)
    cv(f, k, ((960, 540),))
    c = f.ctx
    sphere(c, 960, 540, 300, (0.35, 0.6, 0.95))
    for dx, dy, r in ((-90, -80, 90), (110, 40, 110), (-40, 140, 60)):
        c.arc(960 + dx, 540 + dy, r, 0, 2 * math.pi)
        fill(c, (0.4, 0.78, 0.4), 0.9)
    glow(c, 960, 540, 420, (0.5, 0.8, 1.0), 0.25)
    txt = ph["text"].lower()
    if "price" in txt:
        text3d(f, "THE PRICE OF BEING ALIVE", 960, 110, 74, t=f.plt)
    elif "exist" in txt:
        text3d(f, "3D LETS US EXIST", 960, 110, 80, t=f.plt)


def T_sam_watched(f, k, ph):
    K.bg(f, "#120A1E", "#2C1840")
    cv(f, k, ((960, 600), (960, 360)))
    c = f.ctx
    K.plane_begin(c, 960, 760, 0.42, -0.1)
    K.sheet(c, 1600, 700)
    K.flat_house(c, 400, -40, 0.7)
    sam(c, wob(f.t, 0.08, 300), 80, 1.0, "smile", f.t, walk=1)
    c.restore()
    big_eye(c, 960 + wob(f.t, 0.08, 300) * 0.6, 260, 0.6, f.t, look=(wob(f.t, 0.08, 1), 1), a=0.9)
    vignette(f, 0.6)


def T_room_eye(f, k, ph):
    K.bg_room(f, night=True)
    cv(f, k, ((960, 560), (700, 600)))
    c = f.ctx
    txt = ph["text"].lower()
    a = 0.12 + 0.3 * ease(f.plt / 1.0) if ("everything" in txt or "closer" in txt) else 0.08
    big_eye(c, 1200, 380, 0.8, f.t, look=(-1, 0.4), a=a)
    you(c, 640, 1000, 1.5, expr="worried", t=f.t, look=(1, 0), fd=1)
    vignette(f, 0.7)


def T_end(f, k, ph):
    K.bg_space(f, 99)
    cv(f, k, ((960, 540),), wide=True)
    c = f.ctx
    K.tesseract(c, 960, 360, 230, f.t, K.VIO)
    sam(c, 520, 760, 0.9, "happy", f.t)
    you(c, 1400, 900, 0.9, expr="happy", arms="wave", t=f.t, fd=-1)
    text3d(f, "SUBSCRIBE", 960, 720, 110, t=f.plt, top=(0.95, 0.3, 0.35), side=(0.45, 0.05, 0.1))


def T_word(f, k, ph):
    """kinetic word card: the key word of the line, big and gold."""
    pal = [("#221636", "#3B2650"), ("#14213D", "#2B3F6B"), ("#2B1424", "#4A2440"), ("#123030", "#21474A")]
    a, b = pal[(ph["idx"] + k) % 4]
    K.bg(f, a, b)
    cv(f, k, ((960, 540),))
    w = ph.get("word") or ""
    if w:
        text3d(f, w.upper(), 960, 520, 150, t=f.plt, max_w=1600)



# ============================================================================ routing
# (regex on the phrase, template).  First match wins; section defaults fill the rest.
ROUTES = [
    (r"just like sam's footprint", T_heart_side),
    (r"food goes", T_sam_tube),
    (r"through a direction you cannot see", T_flip_you),
    (r"a lot more out there|keep exploring", T_end),
    (r"step kata", T_keys),
    (r"reach inside you", T_steal_heart),
    (r"^and no,", T_not_time),
    (r"point (up|down)|^(now,? )?(left|right|forward|back)\.", T_point),
    (r"six directions|three dimensions\.", T_axes),
    (r"whole world", T_axes),
    (r"another direction|right angle|cannot point|cannot picture|cannot see", T_seventh),
    (r"inside out", T_tesseract),
    (r"walking through walls", T_powers),
    (r"cash|safe", T_safe),
    (r"every room of your home", T_dollhouse),
    (r"heart beating", T_heart_chest),
    (r"remove your heart|single mark|take your heart|breaking your skin", T_steal_heart),
    (r"exactly how", T_steal_heart),
    (r"what it would mean to see the fourth", T_title),
    (r"we do not mean time|fourth direction of space|like up, or left|never been able to visit", T_not_time),
    (r"where we are going|one dimension fewer|what your eyes|what you could do|something else could do|stuck here|not entirely comfortable", T_roadmap),
    (r"^(part \w+|epilogue)", T_chapter),
    (r"eighteen eighty|headmaster|strange little book|completely flat|called it flatland", T_book),
    (r"sheet of paper|stretching", T_flatland),
    (r"residents|small square|call him sam", T_sam_intro),
    (r"forward and back|left and right|but up|no word for it|no up", T_sam_moves),
    (r"how sam sees|look down on|eyes sit inside|only sees edges|single line|brighter|darker", T_sam_view),
    (r"sam's home|walls|simply lines|locks his door|closes a gap|that is enough|nothing can get in", T_sam_house),
    (r"except, of course|reach down from above|hand would appear|sealed room|vanish", T_hand_flatland),
    (r"hold on to that image|you are sam|looking down on you", T_you_are_sam),
    (r"sees only lines|what do we see|we do not\.|we believe", T_eye_section),
    (r"retina|light-sensitive cells\. essentially|light lands|paints a flat", T_eye_section),
    (r"rebuilds depth|two eyes|shadows, and a lifetime", T_brain),
    (r"you see in two|sees in one|pattern one step|not a sheet|block of light|filled all the way", T_ladder),
    (r"changes everything", T_tesseract),
    (r"image of a box|surface|every point within|outside, and the inside|closed box|what it holds", T_box_inside),
    (r"x-ray|faint and transparent|from above\. every|every wall|every interior|full detail", T_xray),
    (r"another person|their skin|their muscle|beating heart|same time|every side", T_layers),
    (r"nothing could be hidden|pocket|vault|inside a body", T_hidden),
    (r"lowering a ball|would not see a ball|single point|grow into a circle|out of nothing|circle would widen|then shrink|disappear entirely", T_ball_plane),
    (r"miracle|passing through", T_miracle),
    (r"one level higher|hypersphere|empty air|swell|larger|smaller|be gone|no door|direction of arrival|presence", T_hypersphere),
    (r"tesseract|cube inside|folding|only its shadow|perfectly simple|strangeness", T_tesseract),
    (r"let us try|wake up tomorrow|something has changed|move in the fourth direction", T_bed),
    (r"has a name|hinton|century|\bkata\b|like up|and down\.|pointed somewhere|own words", T_hinton),
    (r"you try it|step ana", T_step_ana),
    (r"opens like a flower|not above it|not beside it|outside of it|every drawer|plain sight|outside of anything", T_flower),
    (r"keys|kitchen|counter|locked last night|need them|step kata|standing beside", T_keys),
    (r"door never opened|lock never turned|suggestions", T_door),
    (r"head outside|tie your shoes|laces|knot slides|try again|happens again", T_shoe),
    (r"knot only holds|rope|extra direction to slip|takes it|nothing stays tied\.$", T_knot),
    (r"remember sam|lean over|never could before|footprint|slide it anywhere|spin it|lift it out|flip it over|lay it back|stares|impossible|always could|flat world could|front of his eyes", T_footprint),
    (r"walking through walls|untying every knot|into its reflection", T_powers),
    (r"keep only one|comments|think about it carefully|would you choose", T_comment),
    (r"that last ability|matter a great deal", T_powers),
    (r"reverse it|something else already", T_watcher),
    (r"to that creature|you are sam\.|not a barrier|an outline|drawn on paper", T_outline),
    (r"lift a coin|center of sam|touching his edges", T_coin_sam),
    (r"exactly the same way|remove your heart|no incision|no wound|no trace", T_no_trace),
    (r"matter of reflections|lifts you|turns you|sets you back", T_flip_you),
    (r"feel nothing unusual|right side of your chest|mirror image of what|just like sam's footprint", T_heart_side),
    (r"molecules|mirror-image forms|left-handed, and right|particular|amino|sugars|every one of those", T_molecules),
    (r"starve|food|wrong shape|eat every|waste away|single turn|no longer feed", T_food),
    (r"so powerful|why don't we live|why do we live", T_why),
    (r"run an experiment|solar system|extra direction\.|nothing seems wrong|sun still|earth still|nudge|jupiter|happens all the time|barely matters|wobbles|forgiving|grows|drifts|grips|spirals|into the fire|slips loose|into the dark|forever", T_solar),
    (r"gravity spreads|fades far faster", T_gravity),
    (r"nineteen seventeen|ehrenfest|worked out", T_ehrenfest),
    (r"zoom in|single atom|electron|stable place|could not hold together", T_atom),
    (r"no atoms|no chemistry|no life", T_chain),
    (r"remember your shoelaces|not knots|not planets|not atoms", T_untied),
    (r"fewer dimensions|what about sam|problem of his own|means to eat|food goes|tube|cut him in two|hawking|digestive|never have eaten lunch", T_sam_tube),
    (r"too few|too many|narrow space|room for life|comes undone|not a limitation", T_goldilocks),
    (r"allows us to exist|price of being alive|blindness", T_earth),
    (r"one thought remains|being watched|could not have known|hair's width|no word for", T_sam_watched),
    (r"something were watching|how would you ever know|could not see it|could not point|closer to you|see everything", T_room_eye),
    (r"keep exploring|subscribe|cannot see\. yet", T_end),
]
SECTION_DEFAULT = {
    "hook": [T_seventh, T_tesseract, T_axes], "one": [T_flatland, T_sam_intro], "two": [T_eye_section, T_ladder],
    "three": [T_hypersphere, T_tesseract], "four": [T_flower, T_powers], "five": [T_watcher, T_outline],
    "six": [T_solar, T_earth], "epilogue": [T_sam_watched, T_room_eye],
}
KEYWORDS = ["flatland", "sam", "up", "edges", "retina", "solid", "hypersphere", "tesseract", "shadow", "ana", "kata",
            "flower", "keys", "knot", "footprint", "reflection", "outline", "heart", "mirror", "starve", "orbits",
            "atoms", "chemistry", "life", "three", "four", "everything"]
NUM_WORDS = {"eighteen eighty-four": "1884", "nineteen seventeen": "1917"}


def build():
    words = story.words
    chunks = story.timing["chunks"]
    # phrases: split at punctuation inside each chunk
    phrases, cur = [], []
    for w in words:
        cur.append(w)
        if re.search(r"[,.?!;:]$", w["w"]) and len(cur) >= 1:
            phrases.append(cur)
            cur = []
    if cur:
        phrases.append(cur)
    # merge very short phrases into the previous one (same chunk)
    merged = []
    for p in phrases:
        if merged and (p[-1]["e"] - p[0]["s"]) < 0.45 and merged[-1][0]["chunk"] == p[0]["chunk"]:
            merged[-1] = merged[-1] + p
        else:
            merged.append(p)
    section = "hook"
    plan = []
    last_tpl = None
    rot = {}
    for i, p in enumerate(merged):
        text = " ".join(w["w"] for w in p)
        chunk = chunks[p[0]["chunk"]]["text"]
        low = text.lower()
        m = re.match(r"part (\w+)|epilogue", chunk.lower())
        if m and p[0] is next(w for w in words if w["chunk"] == p[0]["chunk"]):
            section = m.group(1) or "epilogue"
        tpl = None
        if re.match(r"^(part \w+|epilogue)", chunk.lower()):
            tpl = T_chapter
        else:
            for rx, fn in ROUTES:
                if fn is T_chapter:
                    continue
                if re.search(rx, low):
                    tpl = fn
                    break
        if tpl is None and plan and plan[-1]["section"] == section and plan[-1]["tpl"] not in (T_chapter,):
            tpl = plan[-1]["tpl"]          # fragments ("Then,", "it turns out,") continue the scene
        if tpl is None:
            lst = SECTION_DEFAULT.get(section, [T_tesseract])
            rot[section] = rot.get(section, -1) + 1
            tpl = lst[rot[section] % len(lst)]
        t0 = p[0]["s"]
        t1 = merged[i + 1][0]["s"] if i + 1 < len(merged) else story.duration
        word = None
        for nw, rep in NUM_WORDS.items():
            if nw in low:
                word = rep
        if not word:
            for kw in KEYWORDS:
                if re.search(r"\b%s\b" % kw, low):
                    word = kw
                    break
        run_t0 = t0 if (tpl is not last_tpl) else plan[-1]["run_t0"]
        plan.append(dict(t0=t0, t1=t1, text=text, chunk=chunk, tpl=tpl, idx=i, section=section, word=word,
                         new=tpl is not last_tpl, run_t0=run_t0))
        last_tpl = tpl
    # cut every phrase-scene into ~SHOT_LEN shots
    shots = []
    for ph in plan:
        dur = ph["t1"] - ph["t0"]
        n = max(1, int(round(dur / SHOT_LEN)))
        for j in range(n):
            st = ph["t0"] + dur * j / n
            # every 4th inner shot of a long scene becomes a kinetic word card (if the line has a key word)
            fn = ph["tpl"]
            if ph["word"] and n >= 3 and j == 1 and ph["tpl"] not in (T_chapter, T_title, T_end):
                fn = T_word
            shots.append((st, fn, j, ph))
    shots = shots[:MAX_SHOTS] if len(shots) > MAX_SHOTS else shots
    for st, fn, j, ph in shots:
        def mk(fn=fn, j=j, ph=ph):
            def run(f):
                f.plt = f.t - ph["t0"]          # phrase-local time: animations run across all shots of a line
                f.pdur = ph["t1"] - ph["t0"]
                fn(f, j + ph["idx"] * 7, ph)
            return run
        whip = j == 0 and ph["new"] and ph["idx"] % 3 == 0
        story.shot(st, whip=whip)(mk())
    # sound design
    for ph in plan:
        tx = ph["text"].lower()
        if ph["tpl"] is T_chapter and ph["text"].lower().startswith(("part", "epilogue")):
            story.add_sfx(ph["t0"] - 0.1, "shimmer", 0.6)
        if "remove your heart" in tx or "take your heart" in tx:
            story.add_sfx(ph["t0"] + 0.3, "heart", 1.0)
        if "begin to starve" in tx:
            story.add_sfx(ph["t0"], "drone", 0.8)
        if "ana." in tx or "step kata" in tx:
            story.add_sfx(ph["t0"], "riser", 0.4)
        if "slides apart" in tx:
            story.add_sfx(ph["t0"] + 0.4, "boing", 0.4)
        if "into the fire" in tx:
            story.add_sfx(ph["t0"] + 0.4, "braam", 0.5)
        if "never have eaten lunch" in tx:
            story.add_sfx(ph["t0"] + 0.2, "pizz", 0.5)
        if "see everything" in tx:
            story.add_sfx(ph["t0"] + 0.5, "heart", 0.9)
    story.plan = plan
    return len(shots)


N_SHOTS = build()
