"""Drongo & meerkats: transcript, word timing and the shot-by-shot animation.
Transcript is a BEST GUESS from a rough speech-to-text pass; send the real script
to fix captions (timings come from the audio's pauses, so only the text changes)."""
import math, random
from PIL import Image, ImageDraw
from toon import *
import bgs
from chars import Char

DW, DH = 1440, 2560
DURATION = 153.61

# (speech start, speech end, text): boundaries measured from the audio's pauses
SEGS = [
    (0.42, 5.98, "There's a little black bird in the Kalahari Desert that never hunts. It just screams, and other animals drop their lunch."),
    (6.56, 13.77, "Meerkats. They spend all day with their noses in the sand, digging for beetles, scorpions, and the occasional very unlucky lizard."),
    (14.19, 16.75, "But a meerkat with its head in a hole can't see the sky."),
    (17.18, 24.59, "The sky is full of hawks, so one meerkat always stands guard. The second he spots trouble, he barks a warning, and everyone dives underground."),
    (25.30, 34.22, "Then one morning, a new guy shows up. A small black bird with a forked tail, called the drongo. He doesn't dig. He doesn't hunt. He just sits on a branch above the meerkats, and watches."),
    (34.58, 40.77, "He does impressions. He chirps like a starling. He squawks like a hornbill. He even barks so well, he sounds like a meerkat."),
    (41.52, 48.65, "The meerkats think he's ridiculous. One of them looks up and goes, get your own family, birdbrain! The drongo just tilts his head, and keeps watching."),
    (49.55, 56.11, "Then a hawk shows up. Before the meerkat guard even sees it, the drongo screams. Everyone dives. The hawk gets nothing."),
    (56.50, 61.24, "Next day, same thing. And the next. By the end of the week, the meerkats barely bother looking out."),
    (61.92, 64.54, "Why would they? They've got a free security guard with wings."),
    (65.20, 74.64, "Now, the weird part. One afternoon, a meerkat digs up the juiciest beetle grub, best meal all week, and the drongo screams. Everyone bolts. But there's no hawk."),
    (75.08, 79.47, "The drongo floats down, snatches the grub, and flies back to his branch. He winked."),
    (80.18, 87.14, "Okay, so he's the bird who cried wolf. Easy. Everyone knows how that story ends. Lie too many times, and nobody believes you."),
    (87.64, 97.76, "And sure enough, it starts happening. A meerkat digs up a scorpion. The drongo screams. And this time, nobody moves. They just keep eating. One of them even laughs, and goes, nice try."),
    (98.02, 99.31, "The drongo's out of tricks."),
    (99.82, 100.42, "Or is he?"),
    (100.68, 101.76, "Nobody sees it coming."),
    (102.47, 108.91, "Then the drongo opens his beak, and out comes a sound. It's the meerkats' own alarm call. Perfect. Every note."),
    (109.52, 113.31, "Every head snaps up. Every meerkat runs for the burrow. The sand swallows them in seconds."),
    (113.75, 115.46, "The scorpion is alone in the sand."),
    (115.90, 118.06, "The bird lands, picks it up, and flies away."),
    (118.79, 128.62, "Drongos are some of the best copycats in nature. They can mimic the alarm calls of dozens of other animals, and most of the time, their warnings are real. That's the trick."),
    (129.42, 137.84, "Every honest warning builds trust. Then one big lie cashes it in. When you stop believing one call, you switch to another. Even their own."),
    (138.35, 146.38, "It's like a friend who's right about the weather nine days out of ten. When he yells rain, you run. Scientists in the Kalahari have watched drongos do exactly this."),
    (147.13, 153.55, "Every warning he gives saves their lives. And everyone makes the next lie work. The best guard in the desert is also its best bandit."),
]


def clean(w): return w.strip(".,?!'\"").lower()


def _align():
    """Words get times from the audio's pauses (segment bounds) and are then snapped to
    words the speech-to-text pass actually heard (dec_words.json), interpolating in between."""
    import json, os
    import numpy as np
    dec = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "dec_words.json")))
    words = []
    for si, (a, b, text) in enumerate(SEGS):
        toks = text.split()
        wts, gaps = [], []
        for tk in toks:
            w = len(tk.strip(".,?!'\"")) + 2.6
            gap = 3.0 if tk[-1] in ".?!" else (1.4 if tk[-1] == "," else 0.0)
            wts.append(w); gaps.append(gap)
        gaps[-1] = 0.0                                   # no pause after the last word of a segment
        cw = [0.0]
        for w, g in zip(wts, gaps): cw.append(cw[-1] + w + g)
        tot = cw[-1]
        xs, ts = [0.0], [a]                              # anchors in cumulative-weight space
        last = a
        for i, tk in enumerate(toks):
            c = clean(tk)
            if len(c) < 4: continue
            guess = a + (b - a) * cw[i] / tot
            cands = [d for d in dec if d[0] == c and a - 0.3 <= d[1] <= b + 0.3 and abs(d[1] - guess) < 1.0]
            if not cands: continue
            d = min(cands, key=lambda d: abs(d[1] - guess))
            if d[1] > last + 0.08 and d[1] < b - 0.05:
                xs.append(cw[i]); ts.append(d[1]); last = d[1]
        xs.append(tot); ts.append(b)
        for i, tk in enumerate(toks):
            t0 = float(np.interp(cw[i], xs, ts))
            t1 = float(np.interp(cw[i] + wts[i], xs, ts))
            words.append((tk, t0, t1, si))
    return words


WORDS = _align()


def clean(w): return w.strip(".,?!'\"").lower()


def W(seg, word=None, n=0):
    """Start time of the nth occurrence of `word` in segment `seg` (or the segment start)."""
    if word is None: return SEGS[seg][0]
    hits = [x for x in WORDS if x[3] == seg and clean(x[0]) == word.lower()]
    return hits[n][1]


def E(seg): return SEGS[seg][1]


# ------------------------------------------------------------------ helpers
def ss(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)


def mix(a, b, u): return a + (b - a) * u


def MK(cv, x, y, sc=1.3, d=1, **pose): put(cv, meerkat(pose, d, sc), x, y)
def DR(cv, x, y, sc=1.4, d=1, **pose): put(cv, drongo(pose, d, sc), x, y)
def HK(cv, x, y, sc=1.0, d=1, **pose): put(cv, hawk(pose, d, sc), x, y)
def PR(cv, kind, x, y, sc=1.0, rot=0): put(cv, prop(kind, sc, rot), x, y)


def BG(cv, name, dx=0, dy=0, zoom=1.0):
    cv.alpha_composite(bgs.crop(name, dx, dy, zoom))


def clip_put(cv, res, x, y, ground):
    im, (ox, oy) = res
    top = y - oy
    cut = int(ground - top)
    if cut <= 0: return
    if cut < im.height: im = im.crop((0, 0, im.width, cut))
    cv.alpha_composite(im, (int(x - ox), int(top)))


def hole(cv, x, y, rx=170, ry=40):
    g = ImageDraw.Draw(cv)
    g.ellipse([x - rx - 12, y - ry - 8, x + rx + 12, y + ry + 12], fill=(190, 140, 90))
    g.ellipse([x - rx, y - ry, x + rx, y + ry], fill=(38, 22, 22))


def tumble(cv, x, y, r, rot):
    lay = Image.new("RGBA", (int(r * 2.6), int(r * 2.6)), (0, 0, 0, 0))
    g = ImageDraw.Draw(lay); c = r * 1.3
    for k in range(7):
        a = math.radians(rot + k * 26)
        g.arc([c - r, c - r * abs(math.cos(a)) - 2, c + r, c + r * abs(math.cos(a)) + 2], 0, 360, fill=(120, 84, 52, 255), width=7)
    g.ellipse([c - r, c - r, c + r, c + r], outline=(120, 84, 52, 255), width=8)
    cv.alpha_composite(lay, (int(x - c), int(y - c)))


def sand_puffs(cv, x, y, t, seed=0, n=5):
    rnd = random.Random(seed)
    g = ImageDraw.Draw(cv)
    for i in range(n):
        ph = (t * 3.2 + rnd.random()) % 1.0
        ang = rnd.uniform(-2.6, -0.5)
        px = x + math.cos(ang) * 150 * ph; py = y + math.sin(ang) * 190 * ph + 340 * ph * ph
        r = 14 + 10 * (1 - ph)
        g.ellipse([px - r, py - r, px + r, py + r], fill=(226, 190, 138, int(240 * (1 - ph))))


def alert(t, ph=0, **kw):
    d = dict(bob=math.sin(t * 2.1 + ph) * 4, arm=12 + math.sin(t * 1.3) * 3, look=(math.cos(t * 1.1 + ph), -0.15),
             eyes="dot", mouth="flat", tilt=math.sin(t * 1.1 + ph) * 4)
    d.update(kw); return d


def dig(t, ph=0, **kw):
    s = math.sin(t * 15 + ph)
    d = dict(lean=60 + s * 3, tilt=46, arm=34 + 30 * s, armB=34 - 30 * s, eyes="closed", mouth="flat", bob=abs(s) * -6)
    d.update(kw); return d


def pop_scale(u, dur=0.18):
    return ss(u / dur) * (1 + 0.15 * math.sin(min(1, u / (dur * 2.5)) * math.pi))


# ------------------------------------------------------------------ shots
SHOTS = []


def shot(t0, cam=(1.0, 1.07, 0.5, 0.5)):
    def deco(fn):
        SHOTS.append((t0, fn, cam)); return fn
    return deco


@shot(W(0))
def s01(cv, t, u):
    BG(cv, "branch")
    DR(cv, 720, 1560, 2.1, -1, tilt=math.sin(t * 1.4) * 6, tail=math.sin(t * 2) * 12, eyes="dot", brow=0)


@shot(W(0, "it"), cam=(1.0, 1.12, 0.35, 0.6))
def s02(cv, t, u):
    BG(cv, "branch", dx=-60)
    for k in range(4):                                    # lunches drop
        tt = t - W(0, "screams") - 0.5 - k * 0.32
        if tt > 0:
            PR(cv, "lunch", 900 + k * 130 + 40 * math.sin(k), -100 + 1900 * tt * tt + 400 * tt, 1.1, tt * 300)
    op = ss((t - W(0, "screams")) * 8) * (0.7 + 0.3 * math.sin(t * 28))
    DR(cv, 420, 1560, 2.0, 1, open=op, tilt=-8, eyes="wide", tail=math.sin(t * 20) * 14)
    if t > W(0, "screams"): rings(cv, 780, 1290, t - W(0, "screams"), d=1)


@shot(W(1))
def s03(cv, t, u):
    BG(cv, "wide")
    for i, (x, y, sc, d) in enumerate(((330, 2300, 1.45, 1), (860, 2090, 1.1, -1), (1130, 2380, 1.5, -1))):
        hole(cv, x + 150 * d, y - 6, 150 * sc / 1.4, 34)
        MK(cv, x, y, sc, d, **dig(t, i * 2))
        sand_puffs(cv, x + 380 * sc / 1.4 * d, y - 30, t, i)


@shot(W(1, "beetles"), cam=(1.0, 1.1, 0.5, 0.65))
def s04(cv, t, u):
    BG(cv, "close")
    hole(cv, 800, 2330, 230, 50)
    MK(cv, 380, 2420, 1.9, 1, **dig(t, 0))
    for word, kind, x in (("beetles", "beetle", 760), ("scorpions", "scorpion", 960), ("lizard", "lizard", 1000)):
        tt = t - W(1, word)
        if tt > -0.05:
            h = 640 * min(1, max(0, tt)) - 1500 * max(0, tt - 0.5) ** 2
            PR(cv, kind, x + 60 * math.sin(tt * 3), 2250 - max(0, h), 1.5 if kind != "lizard" else 1.3, tt * 120)
            if tt < 0.6: sparkle(cv, x + 160, 2120 - h * 0.4, 36, 220)


@shot(W(2))
def s05(cv, t, u):
    BG(cv, "wide", dx=120)
    hole(cv, 1020, 2330, 190, 40)
    MK(cv, 580, 2380, 1.55, 1, lean=84, tilt=52, arm=52 + 8 * math.sin(t * 9), armB=40, eyes="wide", mouth="flat",
       bob=math.sin(t * 6) * 3)
    g = ImageDraw.Draw(cv)
    bubble(cv, "?", 660, 1250, 120, tail=(40, 100))
    # hawk shadow passes
    x = mix(-200, 1700, ss(u / 2.4)); g.ellipse([x - 160, 2400, x + 160, 2450], fill=(0, 0, 0, 80))


@shot(W(3), cam=(1.0, 1.1, 0.5, 0.3))
def s06(cv, t, u):
    BG(cv, "sky")
    for i, (cx, cy, sc) in enumerate(((420, 700, 0.8), (1000, 450, 0.6), (780, 1050, 0.5))):
        a = t * (0.9 + 0.3 * i) + i * 2
        HK(cv, cx + math.cos(a) * 240, cy + math.sin(a * 0.8) * 90, sc, 1 if math.sin(a) > 0 else -1,
           wing=30 * math.sin(t * 3 + i) + 10, rot=math.sin(a) * 6)


def scene_guard(cv, t, barking=False, dive_u=None):
    BG(cv, "wide")
    for i, (x, y, sc, d) in enumerate(((230, 2370, 1.3, 1), (1220, 2360, 1.3, -1))):
        hole(cv, x + 140 * d, y - 6, 120, 30)
        if dive_u is None:
            pose = dig(t, i * 2) if not barking else alert(t, i, eyes="wide", look=(0, -1))
            MK(cv, x, y, sc, d, **pose)
    g = ImageDraw.Draw(cv)
    g.ellipse([430, 2130, 1010, 2290], fill=(150, 120, 96), outline=OUT, width=8)
    g.rectangle([430, 2210, 1010, 2290], fill=(130, 100, 80))
    g.ellipse([430, 2210, 1010, 2330], fill=(130, 100, 80), outline=OUT, width=8)
    g.ellipse([450, 2132, 990, 2270], fill=(168, 138, 110))


@shot(W(3, "so"))
def s07(cv, t, u):
    scene_guard(cv, t)
    MK(cv, 720, 2230, 1.7, 1, **alert(t, 0, eyes="wide", arm=8, look=(math.cos(t * 1.4), -0.25)))


@shot(W(3, "second"), cam=(1.0, 1.1, 0.5, 0.6))
def s08(cv, t, u):
    scene_guard(cv, t, barking=True)
    k = abs(math.sin(t * 14))
    MK(cv, 720, 2230, 1.7, 1, **alert(t, 0, eyes="wide", mouth="open", open=0.4 + 0.6 * k, arm=40, lean=-6, brow=1))
    if u > 0.9:
        rings(cv, 960, 1300, u - 0.9, d=1, col=(255, 240, 160))
        bubble(cv, "BARK!", 1020, 900, 100, tail=(-80, 140), scale=pop_scale(u - 0.9))


@shot(W(3, "everyone"), cam=(1.0, 1.08, 0.5, 0.75))
def s09(cv, t, u):
    BG(cv, "wide")
    spots = ((300, 2280, 1.35, 1), (720, 2230, 1.6, 1), (1130, 2290, 1.35, -1))
    for i, (x, y, sc, d) in enumerate(spots):
        uu = u - i * 0.18
        hole(cv, x + 150 * d * sc / 1.4, y, 150, 36)
        if uu < 1.0:
            sink = 1180 * ss((uu - 0.05) / 0.5) if uu > 0.05 else 0
            res = meerkat(alert(t, i, eyes="wide", arm=60), d, sc)
            clip_put(cv, res, x, y + sink, y + 20)
            if uu > 0.2: dust(cv, x, y, min(1, (uu - 0.2) / 0.8), seed=i)


@shot(W(4))
def s10(cv, t, u):
    BG(cv, "morning", zoom=1.0)
    x = mix(-300, 1200, ss(u / 4.5)); y = 1300 - 250 * math.sin(ss(u / 4.5) * math.pi) * 0.6 + 40 * math.sin(t * 6)
    DR(cv, x, y, 1.15, 1, wing=45 * math.sin(t * 11), rot=-8, tail=math.sin(t * 5) * 14)


@shot(W(4, "small"), cam=(1.0, 1.12, 0.3, 0.75))
def s11(cv, t, u):
    BG(cv, "branch")
    DR(cv, 760, 1560, 2.4, 1, tilt=-4, tail=10 + math.sin(t * 3) * 8, brow=0.3)
    g = ImageDraw.Draw(cv)
    if u > 0.8:
        a = ss((u - 0.8) / 0.4)
        g.ellipse([180, 1180, 560, 1500], outline=(255, 240, 120, int(255 * a)), width=14)
        label(cv, "FORKED TAIL", 360, 1080, 84)


@shot(W(4, "doesn't"), cam=(1.0, 1.08, 0.5, 0.7))
def s12(cv, t, u):
    BG(cv, "branch", dx=40)
    DR(cv, 720, 1560, 2.0, -1, tilt=math.sin(t * 9) * 12, eyes="dot", brow=0.5)
    for k, (word, nm) in enumerate((("dig", "DIG"), ("hunt", "HUNT"))):
        a = ss((t - W(4, word, 0 if word == "dig" else 0) + 0.1) * 6)
        if a > 0:
            g = ImageDraw.Draw(cv); x = 360 + k * 700; y = 760
            g.ellipse([x - 150, y - 150, x + 150, y + 150], fill=(255, 255, 255, int(255 * a)), outline=(220, 40, 50, int(255 * a)), width=26)
            g.line([(x - 106, y - 106), (x + 106, y + 106)], fill=(220, 40, 50, int(255 * a)), width=30)
            label(cv, nm, x, y + 230, 90)


@shot(W(4, "sits"), cam=(1.05, 1.0, 0.7, 0.4))
def s13(cv, t, u):
    BG(cv, "wide")
    DR(cv, 1000, 1180, 1.25, -1, tilt=math.sin(t * 1.3) * 6, eyes="dot", brow=0.4)
    g = ImageDraw.Draw(cv)
    g.line([(300, 1230), (1500, 1230)], fill=(86, 58, 40), width=42)
    for i, (x, y, sc, d) in enumerate(((330, 2290, 1.4, 1), (820, 2180, 1.2, -1), (1180, 2330, 1.4, -1))):
        hole(cv, x + 150 * d, y, 130, 32)
        MK(cv, x, y, sc, d, **dig(t, i * 2))
    ex = 1000 - 60
    for k in range(3):
        g.line([(ex, 1420), (ex - 170 + k * 170, 1920)], fill=(255, 255, 255, 80), width=6)


@shot(W(5), cam=(1.0, 1.1, 0.5, 0.65))
def s14(cv, t, u):
    BG(cv, "branch", dx=-30)
    sp = (W(5, "chirps"), W(5, "squawks"))
    op = 0.5 + 0.5 * math.sin(t * 20) if (sp[0] < t < sp[0] + 1.0 or sp[1] < t < sp[1] + 1.1) else 0
    DR(cv, 420, 1560, 2.0, 1, open=op, tilt=-4 + 3 * math.sin(t * 8) * (op > 0), eyes="dot")
    if t > sp[0]:
        bubble(cv, "TWEET!", 900, 1060, 100, tail=(-200, 150), scale=pop_scale(t - sp[0]))
    if t > sp[1]:
        bubble(cv, "SQUAAWK!", 960, 760, 100, tail=(-250, 200), scale=pop_scale(t - sp[1]))


@shot(W(5, "even"), cam=(1.0, 1.1, 0.4, 0.5))
def s15(cv, t, u):
    BG(cv, "wide")
    g = ImageDraw.Draw(cv)
    g.line([(560, 1150), (1500, 1150)], fill=(86, 58, 40), width=42)
    op = abs(math.sin(t * 16))
    DR(cv, 1060, 1110, 1.2, -1, open=op, tilt=4, eyes="dot")
    MK(cv, 380, 2320, 1.7, 1, **alert(t, 0, eyes="wide", look=(0.5, -0.9), tilt=-14, brow=1))
    bubble(cv, "YIP!", 700, 700, 120, tail=(220, 160), scale=pop_scale(u - 0.2))
    bubble(cv, "?", 420, 1100, 100, tail=(0, 100), scale=pop_scale(u - 1.4))


@shot(W(6), cam=(1.0, 1.08, 0.5, 0.7))
def s16(cv, t, u):
    BG(cv, "wide")
    for i, (x, y, sc, d) in enumerate(((330, 2300, 1.45, 1), (760, 2150, 1.2, 1), (1130, 2330, 1.45, -1))):
        k = abs(math.sin(t * 17 + i))
        MK(cv, x, y, sc, d, bob=-k * 14, tilt=-10 + 4 * math.sin(t * 17 + i), eyes="closed", mouth="open", open=0.3 + 0.7 * k,
           arm=40 + 20 * math.sin(t * 17 + i), look=(1, 0))
        bubble(cv, "HA!", x + 20, y - 1180 - 20 * (i % 2), 80, tail=(0, 80), scale=pop_scale(u - 0.15 * i))


@shot(W(6, "one"), cam=(1.0, 1.15, 0.45, 0.45))
def s17(cv, t, u):
    BG(cv, "wide", dx=-100)
    k = abs(math.sin(t * 15))
    MK(cv, 560, 2480, 2.1, 1, bob=-k * 6, tilt=-12, eyes="squint", mouth="open", open=0.3 + 0.7 * k, brow=-1, angry=1,
       arm=70, armB=60, look=(1, -0.3))
    bubble(cv, "BIRDBRAIN!", 760, 760, 112, tail=(-80, 220), scale=pop_scale(u - 0.2))


@shot(W(6, "drongo"), cam=(1.0, 1.09, 0.5, 0.6))
def s18(cv, t, u):
    BG(cv, "branch", dx=60)
    tl = ss(u / 0.7)
    DR(cv, 720, 1560, 2.1, -1, tilt=-22 * tl + math.sin(t * 2) * 2, eyes="squint" if u > 1.2 else "dot", brow=0.3)
    if u > 1.2:
        bubble(cv, "...", 560, 1000, 110, tail=(80, 160), scale=pop_scale(u - 1.2))


@shot(W(7), cam=(1.0, 1.1, 0.5, 0.35))
def s19(cv, t, u):
    BG(cv, "sky")
    x = mix(-500, 1900, ss(u / 2.2))
    HK(cv, x, 900 + 80 * math.sin(u * 2), 1.2, 1, wing=36 * math.sin(t * 5), rot=6)
    g = ImageDraw.Draw(cv)
    g.ellipse([x - 280, 2350, x + 280, 2430], fill=(0, 0, 0, 70))


@shot(W(7, "before"), cam=(1.0, 1.1, 0.4, 0.5))
def s20(cv, t, u):
    BG(cv, "wide")
    g = ImageDraw.Draw(cv)
    g.line([(0, 1250), (780, 1250)], fill=(86, 58, 40), width=44)
    ts = W(7, "drongo")
    op = ss((t - ts) * 8) * (0.6 + 0.4 * math.sin(t * 26))
    DR(cv, 340, 1210, 1.5, 1, open=op, eyes="wide", tilt=-10, tail=math.sin(t * 18) * 14)
    if t > ts: rings(cv, 640, 1000, t - ts, d=1)
    MK(cv, 1040, 2300, 1.7, -1, **alert(t, 1, eyes="dot", look=(-1, 0.1), mouth="smile"))


@shot(W(7, "everyone"), cam=(1.0, 1.09, 0.5, 0.5))
def s21(cv, t, u):
    BG(cv, "wide")
    spots = ((300, 2280, 1.35, 1), (720, 2230, 1.6, 1), (1130, 2290, 1.35, -1))
    for i, (x, y, sc, d) in enumerate(spots):
        uu = u - i * 0.12
        hole(cv, x + 150 * d * sc / 1.4, y, 150, 36)
        if uu < 1.0:
            sink = 1180 * ss((uu - 0.02) / 0.45) if uu > 0.02 else 0
            clip_put(cv, meerkat(alert(t, i, eyes="wide", arm=60), d, sc), x, y + sink, y + 20)
            if uu > 0.15: dust(cv, x, y, min(1, (uu - 0.15) / 0.8), seed=i + 3)
    x = mix(-400, 1800, ss(u / 1.8))
    HK(cv, x, 700 + 600 * math.sin(ss(u / 1.8) * math.pi), 1.0, 1, wing=28 * math.sin(t * 6), rot=14, claws=1)


@shot(W(7, "hawk", 1), cam=(1.0, 1.1, 0.5, 0.7))
def s22(cv, t, u):
    BG(cv, "close")
    land = ss(u / 0.5)
    HK(cv, 640, mix(700, 1860, land), 1.15, 1, wing=40 * (1 - land) * math.sin(t * 8), rot=6, claws=1 - land * 0.4)
    if u > 0.45: dust(cv, 760, 2200, min(1, (u - 0.45) / 1.0), seed=4, n=12)
    tumble(cv, mix(-200, 1700, u / 2.4), 2400, 120, u * 320)
    if u > 0.9: bubble(cv, "NOTHING.", 720, 1000, 108, tail=(0, 140), scale=pop_scale(u - 0.9))


@shot(W(8))
def s23(cv, t, u):
    BG(cv, "paper")
    d2 = t > W(8, "and")
    page = ss(((t - W(8, "and")) if d2 else 0) * 6) if d2 else 0
    g = ImageDraw.Draw(cv)
    g.rounded_rectangle([280, 620, 1160, 1480], 50, fill=(255, 255, 255), outline=OUT, width=14)
    g.rounded_rectangle([280, 620, 1160, 800], 50, fill=(220, 60, 60), outline=OUT, width=14)
    label(cv, "DAY 3" if d2 else "DAY 2", 720, 1150, 260, col=(30, 24, 40), stroke=0)
    for k in range(4): g.ellipse([360 + k * 230, 580, 420 + k * 230, 640], fill=(80, 80, 90), outline=OUT, width=6)
    uu = (t - W(8, "and")) if d2 else u
    sink = abs(math.sin(uu * 5)) * 0
    MK(cv, 380, 2330, 1.3, 1, **alert(t, 0, eyes="wide", arm=60))
    MK(cv, 1000, 2330, 1.3, -1, **alert(t, 2, eyes="dot", arm=14))
    rings(cv, 720, 1800, uu * 0.6, d=1, col=(255, 120, 120)) if uu < 1.2 else None


@shot(W(8, "by"), cam=(1.0, 1.08, 0.5, 0.65))
def s24(cv, t, u):
    BG(cv, "wide")
    for i, (x, y, sc, d) in enumerate(((330, 2290, 1.4, 1), (760, 2160, 1.2, -1), (1150, 2330, 1.4, -1))):
        if i == 1:
            MK(cv, x, y, sc, d, eyes="closed", mouth="flat", tilt=-14 + math.sin(t * 1.4) * 4, arm=10, bob=math.sin(t * 1.4) * 5)
            label(cv, "Z z z", x + 150, y - 1000 - 40 * math.sin(t * 2), 90)
        else:
            MK(cv, x, y, sc, d, eyes="closed", mouth="smile", shades=True, tilt=-10, arm=-10, armB=-8, bob=math.sin(t * 1.2 + i) * 5)


@shot(W(9), cam=(1.0, 1.12, 0.5, 0.6))
def s25(cv, t, u):
    BG(cv, "wide", dx=-80)
    MK(cv, 700, 2480, 2.1, 1, tilt=-8 + math.sin(t * 3) * 3, arm=58 + math.sin(t * 5) * 4, armB=58, eyes="dot", mouth="open", open=0.35,
       brow=1, look=(0.6, -0.3))
    bubble(cv, "WHY WOULD WE?", 720, 760, 96, tail=(-80, 200), scale=pop_scale(u - 0.15))


@shot(W(9, "free"), cam=(1.0, 1.1, 0.5, 0.65))
def s26(cv, t, u):
    BG(cv, "branch")
    DR(cv, 720, 1560, 2.2, 1, cap=True, tilt=-4 + math.sin(t * 4) * 2, eyes="dot", brow=0.4, tail=math.sin(t * 3) * 8)
    bubble(cv, "FREE!", 1080, 920, 120, tail=(-180, 250), scale=pop_scale(u - 0.1), col=(255, 240, 150))
    for k in range(3): sparkle(cv, 420 + k * 130, 1120 - 40 * k + 20 * math.sin(t * 6 + k), 34 + 8 * math.sin(t * 6 + k))
    label(cv, "SECURITY", 720, 2050, 120)


@shot(W(10), cam=(1.0, 1.0, 0.5, 0.5))
def s27(cv, t, u):
    BG(cv, "branch")
    DR(cv, 720, 1560, 2.2, -1, tilt=8, eyes="squint", brow=-0.2, angry=0)
    sh = 18 * math.exp(-u * 8) * math.sin(u * 90) if u < 0.5 else 0
    bubble(cv, "?", 720 + sh, 800, 260, tail=(0, 200), scale=pop_scale(u - 0.05, 0.12))
    label(cv, "THE WEIRD PART", 720, 2050, 100)


@shot(W(10, "one"), cam=(1.0, 1.12, 0.5, 0.7))
def s28(cv, t, u):
    BG(cv, "close")
    hole(cv, 700, 2380, 260, 52)
    k = ss(u / 0.5)
    MK(cv, 520, 2440, 2.0, 1, bob=0, lean=mix(60, 8, k), tilt=mix(46, -8, k), arm=mix(34, 140, k), armB=mix(34, 130, k),
       eyes="wide" if k > 0.5 else "closed", mouth="open" if k > 0.6 else "flat", open=0.8)
    if k > 0.2:
        PR(cv, "grub", 1030, mix(2300, 1300, k) + 10 * math.sin(t * 7), 1.7, 8 * math.sin(t * 5))
        for j in range(4): sparkle(cv, 900 + j * 120, 1180 + 80 * math.sin(t * 5 + j) - 30 * j, 34 + 8 * math.sin(t * 7 + j))


@shot(W(10, "drongo"), cam=(1.0, 1.08, 0.5, 0.5))
def s29(cv, t, u):
    BG(cv, "wide")
    g = ImageDraw.Draw(cv)
    g.line([(0, 1250), (700, 1250)], fill=(86, 58, 40), width=44)
    op = 0.6 + 0.4 * math.sin(t * 26)
    DR(cv, 330, 1210, 1.5, 1, open=op, eyes="wide", tilt=-10, tail=math.sin(t * 18) * 14)
    rings(cv, 640, 1000, u, d=1)
    for i, (x0, y, sc) in enumerate(((560, 2330, 1.35), (900, 2200, 1.1), (1300, 2340, 1.35))):
        run = max(0, u - 0.7 - i * 0.12)
        MK(cv, x0 - 900 * run * run - 90 * run, y, sc, -1, bob=-abs(math.sin(t * 22 + i)) * 28 * (run > 0), lean=28 if run > 0 else 0,
           arm=70, eyes="wide", mouth="open", open=0.8)


@shot(W(10, "but"), cam=(1.0, 1.1, 0.5, 0.3))
def s30(cv, t, u):
    BG(cv, "sky")
    tumble(cv, mix(-200, 1700, u / 2.0), 2150, 130, u * 300)
    bubble(cv, "NO HAWK?", 720, 900, 120, tail=(0, 150), scale=pop_scale(u - 0.2))


@shot(W(11), cam=(1.0, 1.1, 0.5, 0.6))
def s31(cv, t, u):
    BG(cv, "wide")
    g = ImageDraw.Draw(cv)
    g.line([(0, 1250), (700, 1250)], fill=(86, 58, 40), width=44)
    f = ss(u / 1.6)
    x = mix(330, 1020, f); y = mix(1210, 2250, f) - 300 * math.sin(f * math.pi)
    if f < 1 and u < 2.1:
        DR(cv, x, y, 1.5, 1, wing=40 * math.sin(t * 11), rot=mix(-10, 24, f), tail=math.sin(t * 6) * 10)
        PR(cv, "grub", 1060, 2330, 1.1)
    else:
        sp = ss((u - 2.1) / 0.8)
        DR(cv, mix(1020, 1400, sp), mix(2250, 1500, sp), 1.5, 1, wing=40 * math.sin(t * 11), rot=-14 * sp)
        PR(cv, "grub", mix(1060, 1480, sp) , mix(2330, 1560, sp), 1.1)
    sparkle(cv, 1070, 2230, 30 + 8 * math.sin(t * 8), 200 if f < 1 else 0)


@shot(W(11, "flies"), cam=(1.0, 1.1, 0.4, 0.7))
def s32(cv, t, u):
    BG(cv, "branch")
    DR(cv, 720, 1560, 2.2, -1, tilt=-6, eyes="closed" if u > 1.0 else "dot", tail=math.sin(t * 3) * 8)
    PR(cv, "grub", 420, 1260, 0.9)
    if u > 1.0:
        sparkle(cv, 440, 1240, 52 * pop_scale(u - 1.0, 0.25))
        sparkle(cv, 560, 1120, 30 * pop_scale(u - 1.15, 0.25))
        label(cv, "ting!", 620, 1000, 90)


@shot(W(12), cam=(1.0, 1.12, 0.5, 0.6))
def s33(cv, t, u):
    BG(cv, "paper")
    DR(cv, 720, 1750, 2.4, 1, tilt=-4 + math.sin(t * 6) * 3, open=0.5 + 0.5 * math.sin(t * 14), eyes="wide")
    g = ImageDraw.Draw(cv)
    for ex in (780, 970):                                      # wolf ears headband
        g.polygon([(ex, 1030), (ex + 80, 780), (ex + 150, 1050)], fill=(120, 120, 130), outline=OUT)
        g.polygon([(ex + 28, 1030), (ex + 80, 860), (ex + 116, 1040)], fill=(220, 160, 170))
    bubble(cv, "WOLF!", 540, 600, 150, tail=(220, 220), scale=pop_scale(u - 0.2, 0.2) * (1 + 0.04 * math.sin(t * 22)))
    label(cv, "THE BIRD WHO CRIED WOLF", 720, 2300, 76)


@shot(W(12, "everyone"), cam=(1.0, 1.08, 0.5, 0.65))
def s34(cv, t, u):
    BG(cv, "wide")
    for i, (x, y, sc, d) in enumerate(((330, 2290, 1.4, 1), (760, 2170, 1.2, -1), (1150, 2330, 1.4, -1))):
        MK(cv, x, y, sc, d, eyes="squint", mouth="flat", tilt=math.sin(t * 5 + i) * 10, arm=28, armB=26, brow=-0.5)
    DR(cv, 220, 1000, 0.7, 1, open=0.8, eyes="wide", tail=math.sin(t * 20) * 14)
    label(cv, "! ! !", 520, 780, 70)


@shot(W(13))
def s35(cv, t, u):
    BG(cv, "close")
    hole(cv, 780, 2400, 250, 52)
    MK(cv, 420, 2450, 1.9, 1, **dig(t, 0) if u < 1.3 else dict(lean=8, tilt=-6, arm=50, eyes="wide", mouth="open", open=0.8))
    if u > 1.3:
        k = u - 1.3
        PR(cv, "scorpion", 960, 2230 - 720 * min(1, k * 3) + 300 * max(0, k - 0.35) ** 2, 1.7, math.sin(t * 9) * 12)
        sparkle(cv, 1120, 1750, 40)


@shot(W(13, "drongo"), cam=(1.0, 1.08, 0.5, 0.6))
def s36(cv, t, u):
    BG(cv, "wide")
    g = ImageDraw.Draw(cv)
    g.line([(0, 1250), (700, 1250)], fill=(86, 58, 40), width=44)
    DR(cv, 330, 1210, 1.5, 1, open=0.6 + 0.4 * math.sin(t * 26), eyes="wide", tilt=-10, tail=math.sin(t * 18) * 14)
    rings(cv, 640, 1000, u, d=1)
    for i, (x, y, sc, d) in enumerate(((560, 2330, 1.35, -1), (940, 2180, 1.15, -1), (1300, 2340, 1.35, -1))):
        MK(cv, x, y, sc, d, eyes="dot", mouth="munch", munch=t * 14 + i, arm=40 + 6 * math.sin(t * 14 + i), look=(1, 0.2), bob=math.sin(t * 7 + i) * 3)


@shot(W(13, "one"), cam=(1.0, 1.12, 0.5, 0.6))
def s37(cv, t, u):
    BG(cv, "wide", dx=100)
    k = abs(math.sin(t * 16))
    MK(cv, 700, 2480, 2.0, -1, bob=-k * 10, tilt=10, eyes="closed", mouth="open", open=0.3 + 0.7 * k, arm=80 + 10 * math.sin(t * 8), armB=40)
    bubble(cv, "NICE TRY!", 720, 780, 118, tail=(100, 220), scale=pop_scale(u - 0.4))


@shot(W(14), cam=(1.0, 1.08, 0.5, 0.5))
def s38(cv, t, u):
    BG(cv, "branch")
    DR(cv, 720, 1560, 2.2, -1, tilt=20, eyes="squint", brow=0.8, tail=-10)
    tumble(cv, mix(1700, -200, u / 1.8), 1980, 110, -u * 300)
    g = ImageDraw.Draw(cv)
    g.ellipse([430, 1180, 470, 1260], fill=(120, 200, 255), outline=OUT, width=5)


@shot(W(15), cam=(1.0, 1.7, 0.42, 0.52))
def s39(cv, t, u):
    BG(cv, "branch")
    DR(cv, 720, 1560, 2.4, -1, tilt=-4, eyes="squint", angry=1, brow=-1, open=0.15)


@shot(W(16), cam=(1.0, 1.14, 0.35, 0.5))
def s40(cv, t, u):
    BG(cv, "wide")
    g = ImageDraw.Draw(cv)
    g.line([(0, 1250), (700, 1250)], fill=(86, 58, 40), width=44)
    DR(cv, 330, 1210, 1.5, 1, tilt=-4, eyes="squint", angry=1, open=0.1)
    for i, (x, y, sc, d) in enumerate(((680, 2330, 1.35, -1), (1010, 2190, 1.15, -1), (1320, 2340, 1.35, -1))):
        MK(cv, x, y, sc, d, eyes="dot", mouth="munch", munch=t * 12 + i, arm=40, look=(1, 0.2))


@shot(W(17), cam=(1.0, 1.12, 0.3, 0.55))
def s41(cv, t, u):
    BG(cv, "branch")
    op = ss(u / 0.35)
    DR(cv, 620, 1560, 2.2, 1, open=op, tilt=-12, eyes="wide", tail=math.sin(t * 18) * 6)
    if u > 0.5: rings(cv, 960, 1250, u - 0.5, d=1, col=(255, 240, 160))
    if u > 0.5:
        for k in range(3): label(cv, "~", 1100 + k * 130, 1120 + 50 * math.sin(u * 9 + k), 120)


@shot(W(17, "it's"), cam=(1.0, 1.1, 0.5, 0.65))
def s42(cv, t, u):
    BG(cv, "wide")
    rings(cv, 400, 1500, u, d=1, col=(255, 240, 160))
    MK(cv, 940, 2330, 1.9, -1, **alert(t, 0, eyes="wide", mouth="open", open=0.4, brow=1, look=(-1, -0.2), arm=30))
    bubble(cv, "THAT'S OUR CALL?!", 720, 760, 92, tail=(160, 250), scale=pop_scale(u - 0.2))


@shot(W(18), cam=(1.0, 1.1, 0.5, 0.6))
def s43(cv, t, u):
    BG(cv, "wide")
    for i, (x, y, sc, d) in enumerate(((330, 2290, 1.4, 1), (760, 2190, 1.2, 1), (1130, 2300, 1.4, -1))):
        hole(cv, 720 + 0 * i, 2400, 0, 0) if False else None
        snap = ss((u - 0.05 * i) / 0.1)
        if u < 1.0:
            MK(cv, x, y, sc, d, **dig(t, i) if u < 0.05 * (i + 1) else alert(t, i, eyes="wide", arm=20, brow=1, tilt=0))
            if u > 0.05 * (i + 1): label(cv, "!", x, y - 1000 - 30 * snap, 160)
        else:
            run = u - 1.0
            MK(cv, x + (500 - x) * min(1, run * 1.6) * (1 if True else 0), y, sc, 1 if x < 500 else -1,
               bob=-abs(math.sin(t * 22)) * 24, lean=28, arm=70, eyes="wide", mouth="open", open=0.7)


@shot(W(18, "sand"), cam=(1.0, 1.1, 0.5, 0.7))
def s44(cv, t, u):
    BG(cv, "wide")
    hole(cv, 720, 2200, 260, 60)
    for i, (x0, sc, d) in enumerate(((260, 1.3, 1), (1180, 1.3, -1), (720, 1.5, 1))):
        uu = u - i * 0.12
        x = x0 + (720 - x0) * min(1, max(0, uu) * 1.6)
        sink = 1150 * ss((uu - 0.55) / 0.5) if uu > 0.55 else 0
        if uu < 1.2:
            clip_put(cv, meerkat(dict(bob=-abs(math.sin(t * 22)) * 20, lean=24, arm=70, eyes="wide", mouth="open", open=0.6), d, sc), x, 2260 + sink, 2230)
    dust(cv, 720, 2200, min(1, u / 1.4), seed=7, n=14)


@shot(W(19), cam=(1.0, 1.1, 0.5, 0.75))
def s45(cv, t, u):
    BG(cv, "close")
    PR(cv, "scorpion", 720, 2150, 2.4, math.sin(t * 5) * 6)
    tumble(cv, mix(1700, -200, u / 2.0), 1500, 130, -u * 300)


@shot(W(20), cam=(1.0, 1.08, 0.5, 0.6))
def s46(cv, t, u):
    BG(cv, "wide")
    PR(cv, "scorpion", 880, 2300, 1.2) if u < 1.2 else None
    f = ss(u / 1.0)
    x = mix(-250, 880, f) if u < 1.2 else mix(880, 1800, ss((u - 1.2) / 0.9))
    y = mix(900, 2180, f) if u < 1.2 else mix(2180, 900, ss((u - 1.2) / 0.9))
    DR(cv, x, y, 1.4, 1, wing=40 * math.sin(t * 11), rot=mix(18, -14, f) if u < 1.2 else -16, tail=math.sin(t * 6) * 10)
    if u >= 1.2: PR(cv, "scorpion", x + 180, y + 160, 0.9, 20)


def paper_title(cv, text, y=420, size=110):
    label(cv, text, 720, y, size, col=(255, 255, 255), stroke=14)


@shot(W(21), cam=(1.0, 1.06, 0.5, 0.5))
def s47(cv, t, u):
    BG(cv, "paper")
    DR(cv, 720, 1650, 2.0, 1, open=0.4 + 0.4 * math.sin(t * 8), tilt=math.sin(t * 2) * 6, eyes="dot")
    words = ["TWEET", "SQUAWK", "YIP", "HISS", "CAW", "MEOW"]
    for i, wd in enumerate(words):
        a = t * 1.1 + i * math.pi / 3
        bubble(cv, wd, 720 + math.cos(a) * 480, 1080 + math.sin(a) * 260, 62, tail=(0, 70), scale=pop_scale(u - i * 0.15))
    label(cv, "COPYCATS", 720, 2220, 130)


@shot(W(21, "they"), cam=(1.0, 1.06, 0.5, 0.5))
def s48(cv, t, u):
    BG(cv, "paper")
    g = ImageDraw.Draw(cv)
    names = ["starling", "hornbill", "babbler", "shrike", "plover", "sparrow", "weaver", "lark", "finch", "dove", "wren", "crow"]
    for i, nm in enumerate(names):
        r, c = divmod(i, 3)
        x = 340 + c * 380; y = 700 + r * 330
        a = pop_scale(u - i * 0.1)
        if a > 0:
            R = 120 * a
            g.ellipse([x - R, y - R, x + R, y + R], fill=(255, 255, 255), outline=OUT, width=10)
            label(cv, nm, x, y, 42 if a > 0.5 else 1, col=(40, 30, 50), stroke=0)
            for k in range(2): g.arc([x - R - 24 - k * 20, y - R - 24 - k * 20, x + R + 24 + k * 20, y + R + 24 + k * 20], -40, 40, fill=(255, 140, 60), width=8)
    label(cv, "DOZENS OF ALARM CALLS", 720, 2150, 84)


@shot(W(21, "most"), cam=(1.0, 1.06, 0.5, 0.5))
def s49(cv, t, u):
    BG(cv, "paper")
    g = ImageDraw.Draw(cv)
    real = ss(u / 1.2) * 0.9
    g.rounded_rectangle([200, 1000, 1240, 1180], 60, fill=(235, 235, 235), outline=OUT, width=12)
    g.rounded_rectangle([200, 1000, 200 + 1040 * real, 1180], 60, fill=(80, 190, 110), outline=OUT, width=12)
    g.rounded_rectangle([200 + 1040 * 0.9, 1000, 1240, 1180], 30, fill=(230, 70, 70), outline=OUT, width=12) if u > 1.3 else None
    label(cv, "REAL WARNINGS", 720, 900, 90, col=(255, 255, 255))
    if u > 1.3: label(cv, "ONE LIE", 1160, 1300, 70)
    label(cv, "THE TRICK", 720, 1850, 150) if t > W(21, "that's") else None


@shot(W(22), cam=(1.0, 1.06, 0.5, 0.5))
def s50(cv, t, u):
    BG(cv, "paper")
    g = ImageDraw.Draw(cv)
    lvl = min(1.0, u / 3.0)
    g.rounded_rectangle([560, 520, 880, 1900], 80, fill=(245, 245, 245), outline=OUT, width=14)
    top = 1860 - 1300 * lvl
    g.rounded_rectangle([580, top, 860, 1880], 60, fill=(80, 190, 110))
    for i in range(4):
        a = pop_scale(u - 0.5 - i * 0.7)
        if a > 0: label(cv, "OK!", 1060, 1700 - i * 270, int(90 * a) or 1, col=(120, 255, 150))
    label(cv, "TRUST", 720, 400, 130)


@shot(W(22, "then"), cam=(1.0, 1.06, 0.5, 0.5))
def s51(cv, t, u):
    BG(cv, "paper")
    g = ImageDraw.Draw(cv)
    lvl = 1.0 - ss((u - 0.8) / 0.4) * 0.92
    g.rounded_rectangle([200, 520, 520, 1900], 80, fill=(245, 245, 245), outline=OUT, width=14)
    g.rounded_rectangle([220, 1860 - 1300 * lvl, 500, 1880], 60, fill=(80, 190, 110) if lvl > 0.3 else (230, 70, 70))
    label(cv, "ONE BIG LIE", 940, 800, 110) if u > 0.6 else None
    if u > 1.1:
        for k in range(8):
            f = (u - 1.1 - k * 0.1)
            if f > 0:
                g.ellipse([780 + 40 * k, 1200 + f * 700 - 800 * f * 0 , 860 + 40 * k, 1280 + f * 700], fill=(250, 200, 60), outline=OUT, width=7)
    DR(cv, 1060, 2300, 1.2, -1, open=0.2, eyes="squint", angry=1) if u > 1.4 else None


@shot(W(22, "when"), cam=(1.0, 1.06, 0.5, 0.5))
def s52(cv, t, u):
    BG(cv, "paper")
    g = ImageDraw.Draw(cv)
    sw = ss((u - 1.0) / 0.5)
    for k, (x, nm) in enumerate(((380, "CALL A"), (1060, "CALL B"))):
        col = (255, 255, 255) if (k == 1 or sw < 0.5) else (230, 230, 230)
        g.rounded_rectangle([x - 260, 900, x + 260, 1300], 60, fill=col, outline=OUT, width=12)
        label(cv, nm, x, 1100, 90, col=(40, 30, 50), stroke=0)
    if sw > 0.4:
        g.line([(160, 880), (600, 1320)], fill=(230, 60, 60), width=34)
        g.line([(600, 880), (160, 1320)], fill=(230, 60, 60), width=34)
    ax = mix(480, 880, sw)
    g.polygon([(ax - 40, 1500), (ax + 40, 1500), (ax + 40, 1600), (ax + 90, 1600), (ax, 1700), (ax - 90, 1600), (ax - 40, 1600)], fill=(80, 190, 110), outline=OUT)
    label(cv, "SWITCH!", 720, 1900, 130) if sw > 0.3 else None
    label(cv, "EVEN THEIR OWN", 720, 2150, 84) if t > W(22, "even") else None


@shot(W(23), cam=(1.0, 1.06, 0.5, 0.45))
def s53(cv, t, u):
    BG(cv, "paper")
    g = ImageDraw.Draw(cv)
    friend = Char(skin=(244, 200, 160), coat=(70, 120, 180), pants=(60, 60, 70), hair=(90, 60, 40), long_coat=False)
    im, (ox, oy), _ = friend.render(dict(bob=math.sin(t * 3) * 5, armF=(30, 70), armB=(10, 10), mouth="smile", look=(1, 0)), 1, 1.2)
    cv.alpha_composite(im, (int(330 - ox), int(2400 - oy)))
    for i in range(10):
        r, c = divmod(i, 5)
        x = 560 + c * 170; y = 900 + r * 200
        a = pop_scale(u - 0.3 - i * 0.2)
        if a <= 0: continue
        R = 60 * a
        if i < 9:
            g.ellipse([x - R, y - R, x + R, y + R], fill=(255, 220, 70), outline=OUT, width=8)
        else:
            g.ellipse([x - R, y - R * 0.7, x + R, y + R * 0.7], fill=(150, 160, 180), outline=OUT, width=8)
    label(cv, "NINE SUNNY, ONE RAIN", 880, 1500, 70)


@shot(W(23, "when"), cam=(1.0, 1.08, 0.5, 0.55))
def s54(cv, t, u):
    BG(cv, "paper")
    friend = Char(skin=(244, 200, 160), coat=(70, 120, 180), pants=(60, 60, 70), hair=(90, 60, 40), long_coat=False)
    k = abs(math.sin(t * 14))
    im, (ox, oy), _ = friend.render(dict(armF=(160, 175), armB=(150, 170), mouth="open", open=0.3 + 0.7 * k, eyes="wide", brow=1, look=(1, -0.5)), 1, 1.4)
    cv.alpha_composite(im, (int(380 - ox), int(2400 - oy)))
    bubble(cv, "RAIN!", 520, 800, 150, tail=(-40, 250), scale=pop_scale(u - 0.15))
    for i in range(3):
        run = max(0, u - 0.9 - i * 0.12)
        MK(cv, 1050 + 130 * i + 1000 * run * run, 2300 + i * 0, 1.0, 1, bob=-abs(math.sin(t * 20 + i)) * 18 * (run > 0), lean=26 if run > 0 else 0, arm=70, eyes="wide", mouth="open", open=0.6)


@shot(W(23, "scientists"), cam=(1.0, 1.08, 0.6, 0.5))
def s55(cv, t, u):
    BG(cv, "wide")
    g = ImageDraw.Draw(cv)
    g.line([(500, 1250), (1500, 1250)], fill=(86, 58, 40), width=44)
    DR(cv, 1120, 1210, 1.3, -1, tilt=math.sin(t * 1.4) * 5, eyes="dot")
    sci = Char(skin=(236, 190, 150), coat=(240, 240, 240), pants=(60, 80, 100), hair=(70, 46, 30), hat=(200, 170, 110), long_coat=True, chops=False)
    im, (ox, oy), pts = sci.render(dict(bob=math.sin(t * 2) * 4, armF=(120, 150), armB=(100, 140), look=(1, -0.2), mouth="smile"), 1, 1.5)
    cv.alpha_composite(im, (int(380 - ox), int(2400 - oy)))
    hx, hy = 380 - ox + pts["head"][0], 2400 - oy + pts["head"][1]
    g.ellipse([hx + 60, hy - 24, hx + 130, hy + 36], fill=(30, 30, 40), outline=OUT, width=5)       # binoculars
    g.ellipse([hx + 50, hy + 10, hx + 120, hy + 70], fill=(30, 30, 40), outline=OUT, width=5)
    label(cv, "KALAHARI RESEARCH", 720, 500, 84)


@shot(W(24), cam=(1.0, 1.08, 0.5, 0.65))
def s56(cv, t, u):
    BG(cv, "dusk")
    for i, (x, y, sc, d) in enumerate(((300, 2300, 1.3, 1), (700, 2200, 1.1, 1), (1130, 2320, 1.3, -1))):
        MK(cv, x, y, sc, d, eyes="dot", mouth="smile", arm=-10 + 30 * abs(math.sin(t * 4 + i)), armB=-10 + 30 * abs(math.sin(t * 4 + i + 1)), bob=-abs(math.sin(t * 4 + i)) * 12)
    DR(cv, 720, 1160, 1.5, 1, tilt=-4, eyes="dot", brow=0.3)
    g = ImageDraw.Draw(cv)
    g.line([(300, 1220), (1200, 1220)], fill=(60, 40, 30), width=46)


@shot(W(24, "and"), cam=(1.0, 1.1, 0.5, 0.5))
def s57(cv, t, u):
    BG(cv, "dusk")
    for i, (x, y, sc, d) in enumerate(((330, 2300, 1.3, 1), (1100, 2300, 1.3, -1))):
        MK(cv, x, y, sc, d, eyes="dot", mouth="flat", tilt=-6, arm=14, look=(0, -1))
    DR(cv, 720, 1200, 1.7, -1, tilt=6 * math.sin(t * 2), eyes="squint", angry=1, open=0.1)
    g = ImageDraw.Draw(cv)
    g.line([(280, 1260), (1240, 1260)], fill=(60, 40, 30), width=46)


@shot(W(24, "best"), cam=(1.0, 1.18, 0.5, 0.55))
def s58(cv, t, u):
    BG(cv, "dusk")
    g = ImageDraw.Draw(cv)
    g.line([(200, 1560), (1240, 1560)], fill=(60, 40, 30), width=52)
    DR(cv, 720, 1500, 2.5, 1, tilt=-4 + math.sin(t * 2) * 2, eyes="dot", brow=0.2, tail=math.sin(t * 2) * 6)
    tb = W(24, "bandit")
    if t < tb:
        g.ellipse([470, 520, 860, 620], outline=(255, 235, 120), width=18)       # halo
    else:
        a = ss((t - tb) * 10)
        g.rounded_rectangle([680, 940, 990, 1030], 40, fill=(30, 26, 36), outline=OUT, width=6)    # bandit mask
        sparkle(cv, 1000, 820, 48 * a)


SHOT_TIMES = [s[0] for s in SHOTS]


def shot_at(t):
    i = 0
    for k, (t0, fn, cam) in enumerate(SHOTS):
        if t >= t0: i = k
    return i
