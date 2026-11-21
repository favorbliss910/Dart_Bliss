"""Magpie / cuckoo 'mafia' story: transcript (matches the voiceover), word timing, shots."""
import math, random
from PIL import Image, ImageDraw
import story as base
from story import ss, mix, pop_scale, clean, clip_put, tumble, dust
from toon import *
from toon2 import nest, ladder, notebook, flask, fox, snake, badge, magnifier, _egg
from chars import Char
import bgs

DW, DH = 1440, 2560
DURATION = 125.60
DEC_FILE = "mdec_words.json"

SEGS = [
    (0.18, 4.73, "A scientist took one egg out of a magpie nest, and by morning the whole nest was smashed."),
    (5.02, 8.19, "No fox. No storm. No footprints."),
    (8.70, 22.17, "It's a dry valley in southern Spain, and every morning he climbs a ladder to count eggs in magpie nests. Some nests have one egg too many. A cuckoo sneaked it in, then flew off without looking back. No rent. No chores. No regrets."),
    (22.68, 24.80, "So he does something no sane scientist would do."),
    (25.07, 33.05, "In some nests, he plucks out the stranger's egg. In others, he leaves it alone. Then he writes the nest number in a little notebook, and climbs down. He won't say why."),
    (33.60, 36.98, "His colleagues think he's lost it. So you're robbing the robber? says one."),
    (37.23, 42.12, "Another asks if he'd like a badge. A third says the only crime here is his handwriting. He just smiles."),
    (42.61, 54.68, "The next morning, the first nest is wrecked. Eggs smashed. Twigs everywhere. By the end of the week, it's happening again and again. And there's a pattern. Nests where he took the egg get destroyed. Nests where he left it alone? Not a feather out of place."),
    (55.18, 62.96, "So, obviously, it's predators. Crows. Snakes. Bad luck. Case closed, say his colleagues, and they go to lunch. But wait."),
    (63.23, 64.63, "Crows can't read his notebook."),
    (64.93, 68.44, "Nothing in that valley knows which nests he touched. So who does?"),
    (68.96, 81.27, "He hides in the bushes with a flask of coffee. Day one, nothing. Day two, nothing. On day three, his boss says the money ends Friday. Meanwhile, down the hall, a rival publishes a paper called Magpies Are Just Unlucky."),
    (81.56, 84.70, "Everyone claps. Honestly, a fox would be less embarrassing."),
    (85.19, 91.08, "Then, on Friday morning, a long grey bird lands on a nest he emptied the day before. She looks inside. Her egg is gone."),
    (91.63, 92.53, "Twigs."),
    (92.85, 94.05, "Eggs. Feathers."),
    (94.57, 98.36, "The magpie parents watch from a branch. They don't fight. They just watch. Next door,"),
    (98.64, 101.50, "another nest still holds a stranger's egg. Untouched."),
    (102.03, 109.66, "You see, the cuckoo does look back. She checks every nest she's used. And she's running a protection racket. Raise my chick, and your nest stays standing."),
    (109.91, 111.58, "Throw it out, and I wreck everything."),
    (111.84, 122.82, "Magpies that give in lose very little, because this chick doesn't shove their eggs out. Scientists call it the mafia hypothesis, and they still argue about it. But in real life, magpies that say no often lose the whole nest."),
    (123.35, 125.60, "He hadn't just taken an egg. He'd refused to pay."),
]
WORDS = base._align(SEGS, DEC_FILE)


def W(seg, word=None, n=0):
    if word is None: return SEGS[seg][0]
    hits = [x for x in WORDS if x[3] == seg and clean(x[0]) == word.lower()]
    return hits[n][1]


def E(seg): return SEGS[seg][1]


# ------------------------------------------------------------------ cast
SCI = Char(skin=(238, 196, 160), coat=(96, 124, 76), coat2=(220, 190, 80), pants=(150, 130, 96), hair=(110, 70, 40), hat=(196, 166, 112), long_coat=False, build=1.0)
COL1 = Char(skin=(230, 186, 146), coat=(240, 240, 246), coat2=(220, 60, 60), pants=(70, 80, 100), bald=True, stache=True, hair=(60, 40, 30))
COL2 = Char(skin=(246, 206, 170), coat=(240, 240, 246), coat2=(60, 120, 200), pants=(60, 60, 70), hair=(190, 110, 50))
COL3 = Char(skin=(200, 150, 110), coat=(240, 240, 246), coat2=(60, 160, 100), pants=(60, 60, 70), hair=(30, 24, 24), chops=True)
BOSS = Char(skin=(236, 190, 150), coat=(44, 46, 58), coat2=(200, 40, 50), pants=(40, 40, 50), hair=(170, 170, 176), stache=True, build=1.1)
RIVAL = Char(skin=(244, 206, 170), coat=(110, 60, 140), coat2=(250, 210, 80), pants=(50, 40, 70), hair=(40, 30, 30), long_coat=False, chops=True)


def HM(cv, ch, x, y, sc=1.5, d=1, **pose):
    im, (ox, oy), pts = ch.render(pose, d, sc)
    cv.alpha_composite(im, (int(x - ox), int(y - oy)))
    return {k: (x - ox + v[0], y - oy + v[1]) for k, v in pts.items()}


def BD(cv, x, y, sc=1.4, d=1, sp="magpie", **pose): put(cv, drongo(dict(sp=sp, **pose), d, sc), x, y)
def NS(cv, x, y, sc=1.0, **kw): put(cv, nest(scale=sc, **kw), x, y)
def BG(cv, name, dx=0, dy=0, zoom=1.0): cv.alpha_composite(bgs.crop(name, dx, dy, zoom))
def egg(cv, x, y, sc=1.0, glow=False, col=None):
    p = Pen(260, 260, 130, 130, sc)
    kw = dict(col=(222, 238, 226), spk=(70, 110, 90)) if col == "cuckoo" else {}
    _egg(p, 0, 0, 44, glow=glow, **kw); put(cv, p.done(), x, y)
def LAD(cv, x, y, h=1000, sc=1.0): put(cv, ladder(h, sc), x, y)
def NB(cv, x, y, sc=1.0): put(cv, notebook(sc), x, y)


def calm(t, ph=0, **kw):
    d = dict(bob=math.sin(t * 2 + ph) * 4, armF=(8, 8), armB=(8, 8), look=(1, 0), eyes="dot", mouth="smile", tilt=math.sin(t * 1.3 + ph) * 3)
    d.update(kw); return d


def debris(cv, x, y, t, seed=0, n=12, feather=False, spread=420):
    rnd = random.Random(seed); g = ImageDraw.Draw(cv)
    for i in range(n):
        a = rnd.uniform(-math.pi, 0); sp = rnd.uniform(0.4, 1.0) * spread
        px = x + math.cos(a) * sp * t; py = y + math.sin(a) * sp * t * 1.2 + (400 if feather else 1300) * t * t
        if feather:
            g.ellipse([px - 26, py - 9, px + 26, py + 9], fill=(250, 250, 250, 230), outline=(80, 80, 90, 230), width=3)
        else:
            r = rnd.uniform(0, 6.28) + t * 10
            g.line([(px, py), (px + math.cos(r) * 70, py + math.sin(r) * 70)], fill=(126, 86, 52, 255), width=12)


def cloud(cv, x, y, s=1.0):
    g = ImageDraw.Draw(cv)
    for dx, dy, r in ((-90, 10, 70), (0, -30, 90), (100, 10, 72), (30, 30, 70), (-40, 36, 62)):
        g.ellipse([x + (dx - r) * s - 8, y + (dy - r) * s - 8, x + (dx + r) * s + 8, y + (dy + r) * s + 8], fill=OUT)
    for dx, dy, r in ((-90, 10, 70), (0, -30, 90), (100, 10, 72), (30, 30, 70), (-40, 36, 62)):
        g.ellipse([x + (dx - r) * s, y + (dy - r) * s, x + (dx + r) * s, y + (dy + r) * s], fill=(236, 240, 248))


def calendar(cv, text, x=720, y=1000, s=1.0):
    g = ImageDraw.Draw(cv)
    g.rounded_rectangle([x - 420 * s, y - 330 * s, x + 420 * s, y + 330 * s], 50, fill=(255, 255, 255), outline=OUT, width=14)
    g.rounded_rectangle([x - 420 * s, y - 330 * s, x + 420 * s, y - 160 * s], 50, fill=(220, 60, 60), outline=OUT, width=14)
    label(cv, text, x, y + 40 * s, int(230 * s), col=(30, 24, 40), stroke=0)


def stamp(cv, text, x, y, u, rot=-12, col=(220, 40, 50)):
    if u <= 0: return
    s = 1.0 + 0.8 * max(0, 1 - u / 0.14)
    lay = Image.new("RGBA", (1100, 400), (0, 0, 0, 0)); g = ImageDraw.Draw(lay)
    g.rounded_rectangle([20, 40, 1080, 360], 40, outline=col + (255,), width=26)
    f = ImageFont.truetype(FONT, int(190 * s)); bb = g.textbbox((0, 0), text, font=f)
    g.text((550 - (bb[2] - bb[0]) / 2 - bb[0], 200 - (bb[3] - bb[1]) / 2 - bb[1]), text, font=f, fill=col + (255,))
    lay = lay.rotate(rot, resample=Image.BICUBIC, expand=True)
    cv.alpha_composite(lay, (int(x - lay.width / 2), int(y - lay.height / 2)))


SHOTS = []


def shot(t0, cam=(1.0, 1.07, 0.5, 0.5)):
    def deco(fn): SHOTS.append((t0, fn, cam)); return fn
    return deco


# ------------------------------------------------------------------ shots
@shot(W(0), cam=(1.0, 1.1, 0.55, 0.5))
def m01(cv, t, u):
    BG(cv, "tree")
    LAD(cv, 330, 2500, 1500)
    NS(cv, 900, 1460, 1.6, state="ok", eggs=2, extra=False)
    up = ss(u / 1.4)
    HM(cv, SCI, 360, 1180, 1.05, 1, bob=math.sin(t * 5) * 3, armF=(mix(20, 140, up), mix(30, 168, up)), armB=(40, 60), look=(0.8, -0.2), eyes="dot", mouth="smile", tilt=-5)
    egg(cv, 360 + 150 * math.sin(math.radians(mix(20, 140, up))), mix(1280, 740, up) if u > 1.0 else 1100, 1.0)


@shot(W(0, "morning"), cam=(1.0, 1.08, 0.55, 0.5))
def m02(cv, t, u):
    BG(cv, "gloom")
    NS(cv, 760, 1700, 2.3, state="smashed")
    debris(cv, 760, 1650, min(1, u * 1.4), seed=2, n=14)
    k = abs(math.sin(u * 40)) * math.exp(-u * 4) * 8
    label(cv, "!", 760 + k, 980, 330)


@shot(W(1, "fox"), cam=(1.0, 1.06, 0.5, 0.65))
def m03(cv, t, u):
    BG(cv, "valley", dx=-60)
    put(cv, fox(1, 1.5), 640, 2350)
    bubble(cv, "NOT ME", 960, 1400, 100, tail=(-180, 180), scale=pop_scale(u - 0.15))
    label(cv, "(shrug)", 720, 1130, 1) if False else None


@shot(W(1, "storm"), cam=(1.0, 1.08, 0.5, 0.4))
def m04(cv, t, u):
    BG(cv, "valley")
    cloud(cv, 720, 900 + math.sin(t * 4) * 10, 2.0)
    g = ImageDraw.Draw(cv)
    bubble(cv, "NOT ME", 720, 1420, 96, tail=(0, 140), scale=pop_scale(u - 0.1))
    for k in range(3): g.line([(520 + k * 200, 1150), (500 + k * 200, 1190)], fill=(150, 190, 255, 120), width=8) if u > 0.9 else None


@shot(W(1, "footprints"), cam=(1.0, 1.1, 0.5, 0.7))
def m05(cv, t, u):
    BG(cv, "close")
    x = mix(1500, -100, ss(u / 1.2))
    put(cv, magnifier(2.0), x, 2100 + 40 * math.sin(u * 8))
    label(cv, "NOTHING", 720, 1100, 150) if u > 0.5 else None


@shot(W(2), cam=(1.0, 1.08, 0.5, 0.5))
def m06(cv, t, u):
    BG(cv, "valley")
    label(cv, "SOUTHERN SPAIN", 720, 560, 110) if u > 0.2 else None
    HM(cv, SCI, mix(200, 620, ss(u / 4.0)), 2350, 1.1, 1, bob=-abs(math.sin(t * 8)) * 12, walk=math.sin(t * 8), armF=(30 * math.sin(t * 8), 6), armB=(-30 * math.sin(t * 8), 6), mouth="smile")


@shot(W(2, "every"), cam=(1.0, 1.1, 0.4, 0.4))
def m07(cv, t, u):
    BG(cv, "tree")
    LAD(cv, 420, 2500, 1700)
    y = mix(2450, 1380, ss(u / 3.0))
    HM(cv, SCI, 430, y, 1.0, 1, bob=math.sin(t * 9) * 4 * (u < 3), armF=(mix(30, 120, ss((u - 3) / 0.5)), 90), look=(1, -0.2), mouth="smile")
    NS(cv, 960, 1420, 1.5, state="ok", eggs=3)
    for k in range(3):
        if u > 3.0 + k * 0.4: label(cv, str(k + 1), 840 + k * 120, 1130, int(130 * pop_scale(u - 3.0 - k * 0.4)) + 1)


@shot(W(2, "some"), cam=(1.0, 1.12, 0.5, 0.55))
def m08(cv, t, u):
    BG(cv, "tree")
    NS(cv, 720, 1650, 2.8, state="ok", eggs=3, extra=True, glow_extra=True)
    label(cv, "ONE TOO MANY", 720, 920, 120) if u > 0.5 else None
    g = ImageDraw.Draw(cv)
    if u > 0.5: g.polygon([(700, 1060), (740, 1060), (740, 1200), (790, 1200), (720, 1280), (650, 1200), (700, 1200)], fill=(255, 220, 60), outline=OUT)


@shot(W(2, "cuckoo"), cam=(1.0, 1.08, 0.5, 0.55))
def m09(cv, t, u):
    BG(cv, "tree")
    NS(cv, 780, 1700, 2.0, state="ok", eggs=2)
    f = ss(u / 1.0)
    if u < 1.5:
        BD(cv, mix(-300, 700, f), mix(900, 1300, f) + 60 * math.sin(t * 8), 1.2, 1, sp="cuckoo", wing=45 * math.sin(t * 11), rot=mix(-12, 8, f))
        if u > 0.9: egg(cv, 780, mix(1300, 1560, ss((u - 0.9) / 0.5)), 1.4, col="cuckoo")
    else:
        g2 = ss((u - 1.5) / 0.7)
        BD(cv, mix(700, 1900, g2), mix(1300, 600, g2), 1.2, 1, sp="cuckoo", wing=45 * math.sin(t * 11), rot=-14)
        NS(cv, 780, 1700, 2.0, state="ok", eggs=2, extra=True)
        label(cv, "BYE!", 720, 1000, 160) if u > 2.0 else None


@shot(W(2, "rent"), cam=(1.0, 1.08, 0.5, 0.55))
def m10(cv, t, u):
    BG(cv, "valley", dx=40)
    g = ImageDraw.Draw(cv)
    g.polygon([(420, 2260), (1020, 2260), (1100, 1900), (500, 1980)], fill=(230, 90, 80), outline=OUT)
    g.line([(500, 1980), (440, 1700)], fill=OUT, width=24)
    BD(cv, 760, 2000, 1.8, 1, sp="cuckoo", tilt=-10 + math.sin(t * 2) * 3, eyes="closed", open=0.0, tail=math.sin(t * 2) * 6)
    g.rectangle([800, 1700, 940, 1740], fill=(20, 20, 28))                          # shades
    for k, wd in enumerate(("RENT", "CHORES", "REGRETS")):
        a = pop_scale(u - 0.2 - k * 1.1)
        if a > 0.3:
            x = 360 + k * 360; y = 1000 + 30 * k
            bubble(cv, wd, x, y, 70, tail=(0, 90), scale=a)
            ImageDraw.Draw(cv).line([(x - 140, y - 50), (x + 140, y + 50)], fill=(230, 50, 60), width=14)


@shot(W(3), cam=(1.0, 1.12, 0.5, 0.35))
def m11(cv, t, u):
    BG(cv, "bush")
    HM(cv, SCI, 720, 2500, 1.9, 1, **calm(t, mouth="smile", brow=-0.4, eyes="squint", tilt=-3, armF=(30, 90)))


@shot(W(4, "plucks"), cam=(1.0, 1.1, 0.5, 0.6))
def m12(cv, t, u):
    BG(cv, "tree")
    NS(cv, 720, 1900, 2.9, state="ok", eggs=2, extra=u < 0.8)
    f = ss((u - 0.8) / 0.7)
    if u >= 0.8:
        ex, ey = 720, mix(1720, 900, f)
        egg(cv, ex, ey, 1.8, col="cuckoo", glow=True)
    g = ImageDraw.Draw(cv)
    hy = mix(1300, 760, ss(u / 0.8)) if u < 0.8 else mix(760, 560, f)
    g.ellipse([640, hy, 800, hy + 190], fill=(238, 196, 160), outline=OUT, width=10)
    g.rounded_rectangle([660, hy + 150, 780, 1500], 30, fill=(96, 124, 76), outline=OUT, width=10)
    sparkle(cv, 860, 800, 40 * pop_scale(u - 1.1)) if u > 1.1 else None


@shot(W(4, "others"), cam=(1.0, 1.06, 0.5, 0.5))
def m13(cv, t, u):
    BG(cv, "tree")
    NS(cv, 400, 1500, 1.5, state="ok", eggs=2, extra=False)
    NS(cv, 1040, 1500, 1.5, state="ok", eggs=2, extra=True, glow_extra=True)
    g = ImageDraw.Draw(cv)
    label(cv, "TAKE", 400, 880, 120); label(cv, "LEAVE", 1040, 880, 120)
    if u > 1.1: stamp(cv, "OK", 1040, 1950, u - 1.1, rot=8, col=(60, 170, 90))


@shot(W(4, "writes"), cam=(1.0, 1.1, 0.5, 0.5))
def m14(cv, t, u):
    BG(cv, "office")
    NB(cv, 720, 1400, 3.0)
    n = min(1.0, u / 2.4)
    label(cv, "NEST 14", 540, 1260, int(76 * min(1, n * 3)) + 1, col=(60, 60, 130), stroke=0)
    g = ImageDraw.Draw(cv)
    x = 380 + 340 * n; y = 1330 + 18 * math.sin(u * 22)
    g.polygon([(x, y), (x + 150, y - 150), (x + 180, y - 120), (x + 30, y + 30)], fill=(240, 200, 60), outline=OUT)


@shot(W(4, "won't"), cam=(1.0, 1.12, 0.5, 0.35))
def m15(cv, t, u):
    BG(cv, "bush")
    HM(cv, SCI, 720, 2500, 2.0, 1, **calm(t, armF=(150, 175), eyes="closed" if u > 0.5 else "dot", mouth="flat", tilt=-5))
    g = ImageDraw.Draw(cv)
    label(cv, "shhh", 1020, 900, int(110 * pop_scale(u - 0.2)) + 1)


@shot(W(5), cam=(1.0, 1.08, 0.5, 0.6))
def m16(cv, t, u):
    BG(cv, "office")
    for i, (ch, x) in enumerate(((COL1, 330), (COL2, 720), (COL3, 1110))):
        HM(cv, ch, x, 2420, 1.25, 1 if x < 720 else (-1 if x > 720 else 1), bob=math.sin(t * 3 + i) * 4, armF=(30, 120), armB=(30, 120), eyes="squint", mouth="flat", brow=-0.6, tilt=math.sin(t * 2 + i) * 6)
    label(cv, "HE'S LOST IT", 720, 700, 100) if u > 0.6 else None


@shot(W(5, "robbing"), cam=(1.0, 1.1, 0.5, 0.55))
def m17(cv, t, u):
    BG(cv, "office")
    k = abs(math.sin(t * 12))
    HM(cv, COL1, 640, 2480, 1.8, 1, eyes="wide", mouth="open", open=0.3 + 0.7 * k, brow=1, armF=(120, 150), tilt=-6)
    bubble(cv, "ROBBING THE ROBBER?", 720, 800, 86, tail=(-60, 220), scale=pop_scale(u - 0.2))


@shot(W(6), cam=(1.0, 1.08, 0.5, 0.55))
def m18(cv, t, u):
    BG(cv, "office")
    HM(cv, COL2, 330, 2480, 1.5, 1, **calm(t, armF=(100, 140), mouth="open", open=0.4, brow=0.8))
    HM(cv, SCI, 1100, 2480, 1.5, -1, **calm(t, eyes="dot", mouth="smile"))
    x = mix(520, 960, ss(u / 1.0)); y = 1450 + 30 * math.sin(u * 5)
    put(cv, badge(1.3), x, y); sparkle(cv, x + 90, y - 80, 36)


@shot(W(6, "third"), cam=(1.0, 1.1, 0.5, 0.5))
def m19(cv, t, u):
    BG(cv, "office")
    NB(cv, 1000, 1500, 2.4)
    for k in range(4): ImageDraw.Draw(cv).line([(760 + k * 90, 1380 + (k % 2) * 40), (800 + k * 90, 1480 - (k % 2) * 50)], fill=(60, 60, 130), width=8)
    HM(cv, COL3, 420, 2480, 1.7, 1, eyes="squint", mouth="smile", armF=mix_arm(u), brow=-0.5, tilt=-4)
    label(cv, "HANDWRITING", 720, 800, 100) if u > 0.5 else None


def mix_arm(u): return (mix(20, 110, ss(u / 0.6)), mix(30, 100, ss(u / 0.6)))


@shot(W(6, "just"), cam=(1.0, 1.25, 0.5, 0.35))
def m20(cv, t, u):
    BG(cv, "bush")
    HM(cv, SCI, 720, 2520, 2.0, 1, **calm(t, mouth="smile", eyes="dot", armF=(8, 8)))
    sparkle(cv, 900, 900, 40 * pop_scale(u - 0.6)) if u > 0.6 else None


@shot(W(7), cam=(1.0, 1.08, 0.5, 0.55))
def m21(cv, t, u):
    BG(cv, "dawn")
    NS(cv, 720, 1850, 2.4, state="smashed"); debris(cv, 720, 1800, min(1, u * 1.2), seed=5, n=10)
    HM(cv, SCI, 260, 2480, 1.3, 1, eyes="wide", mouth="open", open=0.6, brow=1, armF=(30, 40), armB=(30, 40), bob=math.sin(t * 20) * 2)
    label(cv, "WRECKED", 720, 800, 130) if u > 0.4 else None


@shot(W(7, "by"), cam=(1.0, 1.06, 0.5, 0.5))
def m22(cv, t, u):
    BG(cv, "paper")
    calendar(cv, "DAY 7" if u > 1.5 else "DAY 3", 720, 800, 0.9)
    for k in range(6):
        a = pop_scale(u - k * 0.3)
        if a > 0.1: NS(cv, 260 + (k % 3) * 460, 1800 + (k // 3) * 380, 0.9 * a, state="smashed")


@shot(W(7, "pattern"), cam=(1.0, 1.06, 0.5, 0.5))
def m23(cv, t, u):
    BG(cv, "office")
    g = ImageDraw.Draw(cv)
    g.rounded_rectangle([100, 700, 1340, 2000], 40, fill=(252, 250, 240), outline=OUT, width=12)
    g.line([(720, 760), (720, 1940)], fill=OUT, width=8)
    label(cv, "EGG TAKEN", 410, 840, 70, col=(200, 40, 50), stroke=6)
    label(cv, "EGG LEFT", 1030, 840, 70, col=(60, 160, 90), stroke=6)
    for k in range(4):
        a = pop_scale(u - 0.3 - k * 0.35)
        if a > 0.1:
            NS(cv, 410, 1100 + k * 210, 0.5 * a, state="smashed"); NS(cv, 1030, 1100 + k * 210, 0.5 * a, state="ok", eggs=2, extra=True)


@shot(W(7, "took"), cam=(1.0, 1.08, 0.5, 0.55))
def m24(cv, t, u):
    BG(cv, "gloom")
    NS(cv, 720, 1750, 2.6, state="smashed"); debris(cv, 720, 1700, min(1, u * 1.1), seed=8, n=10)
    stamp(cv, "DESTROYED", 720, 1000, u - 0.3, rot=-8)


@shot(W(7, "left"), cam=(1.0, 1.08, 0.5, 0.55))
def m25(cv, t, u):
    BG(cv, "tree")
    NS(cv, 720, 1750, 2.6, state="ok", eggs=3, extra=True)
    for k in range(5): sparkle(cv, 420 + k * 150, 1200 - 50 * (k % 2) + 20 * math.sin(t * 5 + k), 30 + 8 * math.sin(t * 6 + k))
    ImageDraw.Draw(cv).ellipse([540, 940, 900, 1010], outline=(255, 235, 120), width=16)
    label(cv, "UNTOUCHED", 720, 820, 110)


@shot(W(8), cam=(1.0, 1.06, 0.5, 0.6))
def m26(cv, t, u):
    BG(cv, "valley")
    BD(cv, 280, 2150, 1.4, 1, sp="crow", tilt=math.sin(t * 3) * 6, open=0.3)
    put(cv, snake(1.3, t), 760, 2300)
    put(cv, fox(-1, 1.2), 1180, 2400)
    HM(cv, COL1, 720, 1500, 0.7, 1, **calm(t, armF=(150, 175), mouth="open", open=0.5, brow=1)) if False else None
    bubble(cv, "PREDATORS!", 720, 900, 120, tail=(0, 160), scale=pop_scale(u - 0.15))


@shot(W(8, "case"), cam=(1.0, 1.08, 0.5, 0.6))
def m27(cv, t, u):
    BG(cv, "office")
    run = max(0, u - 0.8)
    for i, (ch, x0) in enumerate(((COL1, 330), (COL2, 640), (COL3, 950))):
        HM(cv, ch, x0 + 900 * run * run + 50 * run, 2420, 1.2, 1, bob=-abs(math.sin(t * 8)) * 10 * (run > 0), walk=math.sin(t * 8) * (run > 0), mouth="smile", armF=(20, 30))
    HM(cv, SCI, 1180, 2420, 1.25, -1, **calm(t, eyes="squint", mouth="flat"))
    label(cv, "CASE CLOSED", 720, 760, 130) if u > 0.2 else None


@shot(W(8, "but"), cam=(1.0, 1.18, 0.5, 0.35))
def m28(cv, t, u):
    BG(cv, "bush")
    HM(cv, SCI, 720, 2520, 2.0, 1, **calm(t, armF=(150, 175), eyes="wide", mouth="flat", brow=1, tilt=-4, bob=0))
    label(cv, "WAIT!", 1020, 900, int(170 * pop_scale(u - 0.1)) + 1)


@shot(W(9), cam=(1.0, 1.1, 0.5, 0.6))
def m29(cv, t, u):
    BG(cv, "valley")
    BD(cv, 560, 2180, 2.0, 1, sp="crow", tilt=12 * math.sin(t * 1.5), eyes="wide", open=0.2, brow=0.8)
    NB(cv, 1000, 1700, 1.6)
    label(cv, "???", 720, 900, 200) if u > 0.4 else None


@shot(W(10), cam=(1.0, 1.25, 0.5, 0.5))
def m30(cv, t, u):
    BG(cv, "valley")
    g = ImageDraw.Draw(cv)
    g.ellipse([1050, 1160, 1090, 1190], fill=(20, 20, 28)); g.polygon([(1070, 1170), (1100, 1160), (1090, 1180)], fill=(20, 20, 28))
    label(cv, "WHO?", 720, 700, int(200 * pop_scale(u - 1.5)) + 1) if u > 1.5 else None
    g.rectangle([0, 0, DW, DH], outline=None)


@shot(W(11), cam=(1.0, 1.1, 0.5, 0.6))
def m31(cv, t, u):
    BG(cv, "bush")
    HM(cv, SCI, 720, 2560, 1.7, 1, **calm(t, armF=(100, 130), eyes="squint", mouth="flat"))
    put(cv, flask(1.2), 1080, 2460 - 20 * math.sin(t * 2))
    g = ImageDraw.Draw(cv)
    rnd = random.Random(2)
    for _ in range(14):
        x = rnd.randint(-80, 1500); y = rnd.randint(2100, 2640); r = rnd.randint(150, 260)
        g.ellipse([x - r, y - r, x + r, y + r * 0.8], fill=(54 + rnd.randint(0, 24), 104 + rnd.randint(0, 36), 58), outline=(30, 70, 40), width=6)


@shot(W(11, "day"), cam=(1.0, 1.05, 0.5, 0.5))
def m32(cv, t, u):
    BG(cv, "paper")
    d2 = t > W(11, "two")
    d3 = t > W(11, "three")
    calendar(cv, "DAY 3" if d3 else ("DAY 2" if d2 else "DAY 1"), 720, 950, 1.0)
    label(cv, "nothing", 720, 1500, 150, col=(255, 255, 255))
    label(cv, "z z z" if d2 else "...", 720, 1750, 110)


@shot(W(11, "boss"), cam=(1.0, 1.1, 0.5, 0.55))
def m33(cv, t, u):
    BG(cv, "office")
    k = abs(math.sin(t * 13))
    HM(cv, BOSS, 700, 2500, 1.9, 1, eyes="squint", mouth="open", open=0.3 + 0.7 * k, brow=-1, angry=1, armF=(140, 170), armB=(80, 100), tilt=-6, bob=-k * 6)
    bubble(cv, "FRIDAY!", 760, 800, 150, tail=(-80, 220), scale=pop_scale(u - 0.2))
    ImageDraw.Draw(cv).ellipse([1020, 1300, 1260, 1540], fill=(250, 200, 60), outline=OUT, width=10) if u > 0.5 else None
    label(cv, "$", 1140, 1420, 180, col=(120, 80, 20), stroke=0) if u > 0.5 else None


@shot(W(11, "meanwhile"), cam=(1.0, 1.1, 0.5, 0.55))
def m34(cv, t, u):
    BG(cv, "office")
    HM(cv, RIVAL, 720, 2500, 1.7, 1, eyes="squint", mouth="smile", brow=-0.5, armF=(150, 170), tilt=-5)
    g = ImageDraw.Draw(cv)
    ap = pop_scale(u - 0.6)
    g.polygon([(780, 1050), (1380, 1010), (1400, 1500), (800, 1540)], fill=(255, 255, 255), outline=OUT)
    label(cv, "MAGPIES ARE", 1090, 1180, 56, col=(40, 30, 50), stroke=0); label(cv, "JUST UNLUCKY", 1090, 1280, 56, col=(40, 30, 50), stroke=0)


@shot(W(12), cam=(1.0, 1.08, 0.5, 0.6))
def m35(cv, t, u):
    BG(cv, "office")
    for i, (ch, x) in enumerate(((COL1, 300), (COL2, 720), (COL3, 1140))):
        k = abs(math.sin(t * 12 + i))
        HM(cv, ch, x, 2430, 1.25, 1 if x < 720 else -1, armF=(50 + 60 * k, 120 + 40 * k), armB=(50 + 60 * (1 - k), 120), mouth="smile", eyes="closed", bob=-k * 8)
    label(cv, "*clap clap*", 720, 780, 100)


@shot(W(12, "honestly"), cam=(1.0, 1.1, 0.5, 0.6))
def m36(cv, t, u):
    BG(cv, "valley")
    put(cv, fox(1, 1.4), mix(-300, 700, ss(u / 0.8)), 2350)
    label(cv, "...", 720, 1000, 200) if u > 0.9 else None
    bubble(cv, "I'D HAVE DONE IT BETTER", 720, 700, 70, tail=(0, 150), scale=pop_scale(u - 0.9)) if u > 0.9 else None


@shot(W(13), cam=(1.0, 1.1, 0.5, 0.5))
def m37(cv, t, u):
    BG(cv, "dawn")
    NS(cv, 900, 1850, 1.7, state="empty" if False else "ok", eggs=0)
    f = ss(u / 2.0)
    BD(cv, mix(-300, 900, f), mix(900, 1650, f) + 40 * math.sin(t * 7), 1.3, 1, sp="cuckoo", wing=40 * math.sin(t * 10) * (1 - f * 0.7), rot=mix(-8, 10, f))
    label(cv, "FRIDAY", 720, 500, 130)


@shot(W(13, "she"), cam=(1.0, 1.15, 0.45, 0.55))
def m38(cv, t, u):
    BG(cv, "tree")
    NS(cv, 1050, 1800, 2.0, state="ok", eggs=0)
    BD(cv, 480, 1800, 2.6, 1, sp="cuckoo", tilt=mix(-4, 22, ss(u / 1.0)), look=(1, 0.4), eyes="wide", open=0.0)


@shot(W(13, "her"), cam=(1.0, 1.1, 0.5, 0.55))
def m39(cv, t, u):
    BG(cv, "tree")
    NS(cv, 1000, 1700, 2.4, state="ok", eggs=0)
    BD(cv, 460, 1750, 2.6, 1, sp="cuckoo", tilt=22, look=(1, 0.4), eyes="squint", brow=-1, angry=1)
    label(cv, "GONE", 760, 900, 220) if u > 0.3 else None


@shot(W(14), cam=(1.0, 1.1, 0.5, 0.55))
def m40(cv, t, u):
    BG(cv, "gloom")
    NS(cv, 760, 1800, 2.6, state="torn")
    debris(cv, 760, 1700, min(1, u * 1.5), seed=11, n=18, spread=600)
    BD(cv, 420, 1700, 2.2, 1, sp="cuckoo", open=abs(math.sin(u * 16)), tilt=20, eyes="squint", angry=1, bob=math.sin(u * 16) * 8)


@shot(W(15), cam=(1.0, 1.1, 0.5, 0.55))
def m41(cv, t, u):
    BG(cv, "gloom")
    for k in range(4):
        tt = u - k * 0.18
        if tt > 0:
            egg(cv, 360 + k * 240, -100 + 2300 * min(1, tt * 1.0) ** 2, 1.6)
            if tt > 0.95: debris(cv, 360 + k * 240, 2150, min(1, tt - 0.95), seed=k, n=6, spread=200)
    debris(cv, 720, 700, min(1, u * 0.8), seed=12, n=14, feather=True, spread=300)


@shot(W(16), cam=(1.0, 1.08, 0.5, 0.55))
def m42(cv, t, u):
    BG(cv, "gloom")
    g = ImageDraw.Draw(cv)
    g.line([(0, 1560), (1440, 1520)], fill=(70, 48, 36), width=60)
    for i, x in enumerate((440, 940)):
        BD(cv, x, 1540, 2.1, 1 if i == 0 else -1, sp="magpie", tilt=-10, eyes="wide", open=0.0, brow=1, bob=math.sin(t * 2 + i) * 3)
    label(cv, "...", 720, 900, 220)


@shot(W(17), cam=(1.0, 1.08, 0.5, 0.55))
def m43(cv, t, u):
    BG(cv, "tree")
    NS(cv, 720, 1750, 2.6, state="ok", eggs=3, extra=True, glow_extra=True)
    for k in range(5): sparkle(cv, 380 + k * 170, 1200 + 20 * math.sin(t * 4 + k), 28 + 6 * math.sin(t * 5 + k))
    label(cv, "UNTOUCHED", 720, 860, 110) if u > 0.7 else None


@shot(W(18), cam=(1.0, 1.06, 0.5, 0.5))
def m44(cv, t, u):
    BG(cv, "paper")
    g = ImageDraw.Draw(cv)
    pts = [(300, 1500), (760, 1250), (1140, 1700), (560, 1900)]
    for i, (x, y) in enumerate(pts): NS(cv, x, y, 0.7, state="ok", eggs=2, extra=True)
    prog = (u * 0.5) % 1.0
    seq = pts + [pts[0]]
    k = int(prog * 4); f = prog * 4 - k
    x = mix(seq[k][0], seq[k + 1][0], f); y = mix(seq[k][1], seq[k + 1][1], f) - 200
    BD(cv, x, y, 0.8, 1, sp="cuckoo", wing=30 * math.sin(t * 9), rot=-6)
    label(cv, "SHE LOOKS BACK", 720, 560, 110)


@shot(W(18, "protection"), cam=(1.0, 1.08, 0.5, 0.55))
def m45(cv, t, u):
    BG(cv, "gloom")
    g = ImageDraw.Draw(cv)
    g.rounded_rectangle([200, 2000, 1240, 2100], 30, fill=(110, 76, 50), outline=OUT, width=10)
    BD(cv, 360, 2000, 2.0, 1, sp="cuckoo", tilt=-4, eyes="squint", brow=-0.5, open=0.0)
    g.polygon([(230, 1390), (500, 1390), (440, 1250), (290, 1250)], fill=(40, 40, 48), outline=OUT)        # fedora
    g.rectangle([210, 1380, 520, 1410], fill=(40, 40, 48), outline=OUT, width=6)
    BD(cv, 1080, 2000, 2.0, -1, sp="magpie", tilt=6, eyes="wide", brow=1)
    env = Image.new("RGBA", (200, 130), (0, 0, 0, 0)); ed = ImageDraw.Draw(env)
    ed.rectangle([0, 0, 200, 130], fill=(250, 240, 210), outline=OUT, width=8); ed.polygon([(0, 0), (100, 70), (200, 0)], outline=OUT, fill=(240, 228, 190))
    cv.alpha_composite(env, (int(mix(520, 860, ss((u - 0.6) / 1.0))), 1900))
    label(cv, "PROTECTION RACKET", 720, 700, 100)


@shot(W(18, "raise"), cam=(1.0, 1.08, 0.5, 0.55))
def m46(cv, t, u):
    BG(cv, "tree")
    NS(cv, 720, 1700, 2.4, state="ok", eggs=2, extra=True, chicks=0)
    ImageDraw.Draw(cv).ellipse([480, 1000, 960, 1080], outline=(255, 235, 120), width=16)
    label(cv, "RAISE MY CHICK", 720, 800, 100)
    label(cv, "NEST STAYS STANDING", 720, 2200, 80)
    stamp(cv, "SAFE", 720, 2050, u - 1.5, rot=-8, col=(60, 170, 90))


@shot(W(19), cam=(1.0, 1.08, 0.5, 0.55))
def m47(cv, t, u):
    BG(cv, "gloom")
    NS(cv, 720, 1800, 2.4, state="smashed"); debris(cv, 720, 1750, min(1, u * 1.2), seed=21, n=12)
    label(cv, "THROW IT OUT", 720, 820, 110)
    stamp(cv, "WRECKED", 720, 1100, u - 0.4, rot=-8)


@shot(W(20), cam=(1.0, 1.08, 0.5, 0.55))
def m48(cv, t, u):
    BG(cv, "tree")
    NS(cv, 720, 1750, 2.6, state="ok", eggs=0, chicks=2)
    p = Pen(300, 300, 150, 150, 1.2)
    p.ell(0, 0, 100, 90, (250, 220, 140), 0, 7); p.ell(30, -10, 10, 10, OUT, 0, 0); p.poly([(70, 0), (140, 14), (70, 34)], (240, 150, 60), 5)
    put(cv, p.done(), 720, 1620)
    label(cv, "LOSE VERY LITTLE", 720, 800, 100)


@shot(W(20, "scientists"), cam=(1.0, 1.06, 0.5, 0.5))
def m49(cv, t, u):
    BG(cv, "paper")
    label(cv, "MAFIA HYPOTHESIS", 720, 1200, 120, col=(255, 255, 255))
    put(cv, magnifier(2.8), 900 + 40 * math.sin(t * 2), 1500 + 20 * math.cos(t * 2))
    HM(cv, COL1, 260, 2450, 1.1, 1, **calm(t, mouth="open", open=0.5, armF=(120, 150), brow=0.6))
    HM(cv, COL2, 1180, 2450, 1.1, -1, **calm(t, mouth="open", open=0.5, armF=(120, 150), brow=-0.6, ph=1))
    label(cv, "?!", 720, 2000, 160)


@shot(W(20, "but"), cam=(1.0, 1.08, 0.5, 0.55))
def m50(cv, t, u):
    BG(cv, "gloom")
    for k in range(3):
        a = pop_scale(u - k * 0.35)
        if a > 0.1: NS(cv, 280 + k * 440, 1950, 0.95 * a, state="smashed")
    BD(cv, 720, 1300, 1.4, 1, sp="magpie", tilt=-12, eyes="wide", brow=1) if u > 0.4 else None
    label(cv, "SAID NO", 720, 800, 130)


@shot(W(21), cam=(1.0, 1.12, 0.5, 0.5))
def m51(cv, t, u):
    BG(cv, "tree")
    HM(cv, SCI, 560, 2520, 1.9, 1, **calm(t, armF=(120, 170), mouth="smile", eyes="dot", tilt=-4))
    egg(cv, 560 + 180, 1250, 1.8, col="cuckoo", glow=True)
    stamp(cv, "REFUSED", 900, 1000, t - W(21, "refused") + 0.05, rot=-10)


# ------------------------------------------------------------------
SHOT_TIMES = [s[0] for s in SHOTS]


def shot_at(t):
    i = 0
    for k, (t0, fn, cam) in enumerate(SHOTS):
        if t >= t0: i = k
    return i
