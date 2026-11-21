"""Test scene: lock story shots 1-2 (first voiceover paragraph).
Usage:  python3 scene_test.py still <t_seconds> [out.png]
        python3 scene_test.py render [W H FPS] [out.mp4]
Backgrounds below are procedural PLACEHOLDERS: swap `shop_bg()` for a photo."""
import math, random, subprocess, sys
import numpy as np
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from chars import Char

DW, DH = 1440, 2560                      # design space (final 2K portrait)
FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"

SCRIPT = [
    ("A stranger asked for sixteen days alone with a lock that nobody had opened in sixty years.", 1),
    ("The shop that made it laughed so hard a clerk dropped his tea.", 2),
]

# ---------------------------------------------------------------- timing
def word_times():
    words, shot_of = [], []
    for text, shot in SCRIPT:
        for w in text.split():
            words.append(w); shot_of.append(shot)
    wt = [len(w.strip('.,')) + 3.2 for w in words]
    sec_per_unit = 0.29 / (sum(wt) / len(wt))
    t, out = 0.0, []
    for w, k, s in zip(words, wt, shot_of):
        out.append((w, t, t + k * sec_per_unit, s))
        t += k * sec_per_unit
    return out

WORDS = word_times()
TOTAL = WORDS[-1][2] + 0.5
T_CUT = [x for x in WORDS if x[3] == 2][0][1]       # shot 2 starts here

def wt_of(word, occurrence=0):
    hits = [x for x in WORDS if x[0].strip('.,') == word]
    return hits[occurrence][1]

# ---------------------------------------------------------------- helpers
def ss(x):  # smoothstep clamp
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)

def key(t, ks):
    """Interpolate between (time, value) keys; values may be numbers or tuples."""
    if t <= ks[0][0]: return ks[0][1]
    for (t0, v0), (t1, v1) in zip(ks, ks[1:]):
        if t <= t1:
            u = ss((t - t0) / (t1 - t0))
            if isinstance(v0, (tuple, list)):
                return tuple(a + (b - a) * u for a, b in zip(v0, v1))
            return v0 + (v1 - v0) * u
    return ks[-1][1]

def paste_char(canvas, char, pose, x, y, d=1, scale=1.5):
    im, (ox, oy), pts = char.render(pose, d, scale)
    canvas.alpha_composite(im, (int(x - ox), int(y - oy)))
    return {k: (x - ox + v[0], y - oy + v[1]) for k, v in pts.items()}

# ---------------------------------------------------------------- placeholder backgrounds
_BG = {}
def shop_bg(variant):
    if variant in _BG: return _BG[variant]
    rnd = random.Random(variant)
    W, H = int(DW * 1.12), int(DH * 1.12)
    base = [(70, 96, 92), (92, 58, 52)][variant - 1]
    im = Image.new("RGB", (W, H), base)
    g = ImageDraw.Draw(im)
    for y in range(H):                                  # wall gradient
        k = y / H
        g.line([(0, y), (W, y)], fill=tuple(int(c * (1.15 - 0.5 * k)) for c in base))
    wood = (96, 62, 38)
    g.rectangle([0, int(H * 0.60), W, H], fill=wood)       # wainscot + floor
    for i in range(12):
        y = int(H * 0.60) + i * 8 + i * i * 6
        g.line([(0, y), (W, y)], fill=(70, 44, 26), width=3 + i // 2)
    g.rectangle([0, int(H * 0.58), W, int(H * 0.60)], fill=(150, 108, 64))
    for row in range(3):                                   # shelves of keys/locks
        y = int(H * (0.14 + 0.13 * row))
        g.rectangle([60, y, W - 60, y + 16], fill=(60, 38, 22))
        for x in range(90, W - 90, 52):
            h = rnd.randint(40, 90)
            col = rnd.choice([(212, 170, 70), (190, 150, 60), (150, 150, 160), (120, 80, 50)])
            g.rounded_rectangle([x, y - h, x + 30, y], 8, fill=col, outline=(40, 28, 20), width=3)
            g.ellipse([x + 8, y - h + 10, x + 22, y - h + 24], fill=(40, 28, 20))
    wx = int(W * 0.08) if variant == 1 else int(W * 0.62)           # arched window
    g.rounded_rectangle([wx, int(H * 0.40), wx + 330, int(H * 0.60)], 10, fill=(40, 28, 20))
    g.rounded_rectangle([wx + 14, int(H * 0.41), wx + 316, int(H * 0.60) - 8], 6, fill=(255, 226, 170))
    for i in range(5):
        g.rectangle([wx + 30 + i * 56, int(H * 0.47), wx + 70 + i * 56, int(H * 0.60) - 8],
                    fill=(120, 80, 70) if i % 2 else (96, 66, 60))
    g.line([(wx + 165, int(H * 0.41)), (wx + 165, int(H * 0.60))], fill=(40, 28, 20), width=8)
    im = im.filter(ImageFilter.GaussianBlur(5))           # photo-like depth
    v = Image.new("L", (W, H), 0)                           # vignette
    ImageDraw.Draw(v).ellipse([-W * 0.25, -H * 0.1, W * 1.25, H * 1.1], fill=255)
    v = v.filter(ImageFilter.GaussianBlur(250))
    im = Image.composite(im, Image.new("RGB", (W, H), (10, 8, 12)), v.point(lambda p: 90 + p * 165 // 255))
    _BG[variant] = im.convert("RGBA")
    return _BG[variant]

# ---------------------------------------------------------------- props
def draw_lock_on_cushion(canvas, x, y, glow=0.0):
    ov = Image.new("RGBA", (700, 700), (0, 0, 0, 0))
    g = ImageDraw.Draw(ov)
    g.ellipse([60, 520, 640, 620], fill=(0, 0, 0, 80))
    g.rounded_rectangle([110, 380, 590, 560], 60, fill=(168, 30, 44), outline=(28, 22, 36), width=10)
    g.rounded_rectangle([140, 390, 560, 440], 24, fill=(206, 56, 70))
    for tx in (96, 604):
        g.line([(tx, 520), (tx, 600)], fill=(230, 190, 80), width=8)
        g.ellipse([tx - 16, 590, tx + 16, 622], fill=(230, 190, 80), outline=(28, 22, 36), width=4)
    g.arc([240, 70, 460, 330], 180, 360, fill=(28, 22, 36), width=40)       # shackle
    g.arc([252, 82, 448, 330], 180, 360, fill=(190, 192, 205), width=18)
    g.rectangle([240, 200, 270, 300], fill=(190, 192, 205), outline=(28, 22, 36), width=5)
    g.rectangle([430, 200, 460, 300], fill=(190, 192, 205), outline=(28, 22, 36), width=5)
    g.rounded_rectangle([180, 280, 520, 440], 36, fill=(224, 176, 66), outline=(28, 22, 36), width=10)
    g.rounded_rectangle([200, 296, 500, 330], 14, fill=(244, 214, 120))
    g.ellipse([326, 340, 374, 388], fill=(28, 22, 36))
    g.polygon([(340, 380), (360, 380), (368, 420), (332, 420)], fill=(28, 22, 36))
    if glow > 0:
        gl = Image.new("RGBA", (700, 700), (0, 0, 0, 0))
        ImageDraw.Draw(gl).ellipse([60, 20, 640, 600], fill=(255, 230, 140, int(70 * glow)))
        ov = Image.alpha_composite(gl.filter(ImageFilter.GaussianBlur(40)), ov)
    canvas.alpha_composite(ov, (int(x - 350), int(y - 620)))

def draw_counter(canvas, x0, y0):
    ov = Image.new("RGBA", (DW, DH), (0, 0, 0, 0))
    g = ImageDraw.Draw(ov)
    g.rectangle([x0, y0, DW + 100, DH + 100], fill=(120, 76, 44), outline=(28, 22, 36), width=10)
    g.rectangle([x0 - 24, y0 - 40, DW + 100, y0 + 14], fill=(168, 112, 66), outline=(28, 22, 36), width=10)
    for i in range(1, 5):
        g.line([(x0 + i * 150, y0 + 14), (x0 + i * 150, DH)], fill=(90, 56, 32), width=6)
    canvas.alpha_composite(ov)

def draw_cup(canvas, x, y, ang, broken=False, tshard=0.0):
    ov = Image.new("RGBA", (260, 260), (0, 0, 0, 0))
    g = ImageDraw.Draw(ov)
    g.polygon([(50, 80), (210, 80), (180, 190), (80, 190)], fill=(255, 255, 255), outline=(28, 22, 36))
    g.line([(50, 80), (210, 80), (180, 190), (80, 190), (50, 80)], fill=(28, 22, 36), width=8, joint="curve")
    g.arc([180, 96, 240, 160], 270, 100, fill=(28, 22, 36), width=10)
    g.rectangle([56, 90, 204, 112], fill=(120, 70, 40))
    g.ellipse([60, 188, 200, 220], fill=(236, 236, 242), outline=(28, 22, 36), width=6)
    ov = ov.rotate(ang, resample=Image.BICUBIC, expand=True)
    canvas.alpha_composite(ov, (int(x - ov.width / 2), int(y - ov.height / 2)))

def draw_shards(canvas, x, y, t):
    rnd = random.Random(5)
    g = ImageDraw.Draw(canvas)
    for i in range(14):
        a = rnd.uniform(-math.pi, 0); sp = rnd.uniform(260, 760)
        px = x + math.cos(a) * sp * t; py = y + math.sin(a) * sp * t + 1500 * t * t
        s = rnd.randint(14, 34)
        r = rnd.uniform(0, 6.28) + t * 12
        pts = [(px + s * math.cos(r + k * 2.1), py + s * math.sin(r + k * 2.1)) for k in range(3)]
        g.polygon(pts, fill=(255, 255, 255) if i % 3 else (120, 70, 40), outline=(28, 22, 36))

# ---------------------------------------------------------------- characters
HOBBS = Char(skin=(238, 196, 160), coat=(34, 46, 84), coat2=(214, 168, 60), pants=(54, 54, 64),
             hair=(150, 150, 156), hat=(30, 28, 36), chops=True)
SMITH = Char(skin=(236, 190, 150), coat=(86, 62, 44), coat2=(214, 168, 60), pants=(60, 60, 70),
             hair=(70, 46, 30), bald=True, stache=True, apron=(214, 200, 170), long_coat=False, build=1.15)
CLERK = Char(skin=(244, 206, 170), coat=(70, 120, 90), coat2=(214, 168, 60), pants=(50, 50, 60),
             hair=(190, 110, 50), long_coat=False, build=0.9)

# ---------------------------------------------------------------- scene frames
def shot1(canvas, t):
    k = t / T_CUT
    canvas.alpha_composite(shop_bg(1).crop((60, 40, 60 + DW, 40 + DH)))
    t_ask, t_16, t_nob, t_60 = wt_of("asked"), wt_of("sixteen"), wt_of("nobody"), wt_of("sixty")
    # locksmith behind the counter
    sm = dict(bob=math.sin(t * 3) * 6, lean=-4,
              armF=(10, 8), armB=(10, 8), look=(-1, 0), eyes="dot", mouth="smile",
              brow=key(t, [(0, 0), (t_nob, 0), (t_nob + 0.25, 0.9), (t_60 + 0.4, 0.9), (t_60 + 0.9, 0)]),
              tilt=key(t, [(0, 0), (t_nob, 0), (t_nob + 0.4, -7), (t_60 + 0.6, -7), (t_60 + 1.0, 0)]))
    if t > t_60: sm.update(eyes="wide", mouth="o")
    paste_char(canvas, SMITH, sm, 1040, 2250, d=-1, scale=1.3)
    draw_counter(canvas, 640, 1930)
    draw_lock_on_cushion(canvas, 1010, 1960, glow=0.5 + 0.5 * math.sin(t * 2.2))
    # Hobbs: walks in, then points one finger up on "sixteen"
    xh = key(t, [(0, 190), (t_ask - 0.2, 440), (T_CUT, 440)])
    walking = ss((t_ask - 0.4 - t) / 0.4) if t < t_ask - 0.2 else 0
    hb = dict(bob=math.sin(t * 9) * 12 * walking + math.sin(t * 2.6) * 5, walk=math.sin(t * 9) * walking,
              lean=key(t, [(0, 16), (t_ask, 6), (t_16, -6), (T_CUT, -6)]),
              armF=key(t, [(0, (-22, -8)), (t_ask - 0.2, (8, 10)), (t_16 - 0.35, (8, 10)), (t_16, (92, 96)),
                           (t_nob + 0.2, (92, 96)), (t_nob + 0.7, (60, 90))]),
              armB=(-12 * walking + 8, -4), finger=t >= t_16 - 0.1 and t < t_nob + 0.7, finger_angle=104,
              tilt=key(t, [(0, 4), (t_16, -4), (t_nob, 6)]), look=(1, -0.1),
              eyes="dot", mouth="smile" if t < t_16 else "flat",
              brow=0.2)
    paste_char(canvas, HOBBS, hb, xh, 2480, d=1, scale=1.55)

def shot2(canvas, t):
    s = t - T_CUT
    canvas.alpha_composite(shop_bg(2).crop((100, 60, 100 + DW, 60 + DH)))
    t_laugh, t_drop, t_tea = wt_of("laughed"), wt_of("dropped"), wt_of("tea")
    laugh = ss((t - t_laugh + 0.15) / 0.25)
    shake = math.sin(t * 38) * 9 * laugh
    sm = dict(bob=abs(math.sin(t * 16)) * -18 * laugh, lean=shake * 0.6 + 6,
              armF=key(t, [(0, (14, 10)), (t_laugh, (40, 70)), (t_laugh + 0.3, (30, 20))]),
              armB=(30 + math.sin(t * 16) * 8 * laugh, 60),
              tilt=-14 * laugh + math.sin(t * 16) * 3 * laugh, look=(1, 0),
              eyes="closed" if laugh > 0.5 else "dot", mouth="laugh", open=0.5 + 0.5 * math.sin(t * 20) * laugh,
              brow=0.6 * laugh)
    paste_char(canvas, SMITH, sm, 470, 2360, d=1, scale=1.55)
    # clerk, right, holding a teacup
    cut = ss((t - t_drop) / 0.12)
    cl = dict(bob=math.sin(t * 3) * 5, lean=-4 + 14 * cut,
              armF=key(t, [(0, (56, 92)), (t_laugh, (56, 92)), (t_drop - 0.05, (56, 92)), (t_drop + 0.12, (150, 170))]),
              armB=(20, 30), look=(-1, 0), tilt=-3 + 8 * cut,
              eyes="wide" if t > t_drop - 0.05 else "dot", mouth="o" if t > t_drop - 0.05 else "smile",
              brow=1.0 if t > t_drop - 0.05 else 0)
    hands = paste_char(canvas, CLERK, cl, 1040, 2360, d=-1, scale=1.45)
    t_rel = t_drop + 0.12
    if t < t_rel:
        hx, hy = hands["handF"]
        draw_cup(canvas, hx - 30, hy - 60, 0)
    else:
        u = t - t_rel
        floor_y = 2330
        u_land = (500 + math.sqrt(500 ** 2 + 4 * 1800 * (floor_y - 1500))) / 3600
        if u < u_land:
            draw_cup(canvas, 880 - 90 * u, 1500 - 500 * u + 1800 * u * u, u * 520)
        else:
            draw_shards(canvas, 880 - 90 * u_land, floor_y, min(0.9, u - u_land))

def draw_caption(frame, t):
    cur = [x for x in WORDS if x[1] <= t < x[2] + 0.02]
    if not cur: return
    w, t0, t1, _ = cur[0]
    pop = ss((t - t0) / 0.07)
    sc = 0.55 + 0.45 * pop + 0.15 * math.sin(min(1, (t - t0) / 0.2) * math.pi)
    size = int(168 * sc)
    f = ImageFont.truetype(FONT, size)
    g = ImageDraw.Draw(frame)
    txt = w.strip(".,")
    bb = g.textbbox((0, 0), txt, font=f, stroke_width=16)
    x = (DW - (bb[2] - bb[0])) / 2 - bb[0]
    y = 1790 - (bb[3] - bb[1]) / 2 - bb[1]
    g.text((x + 6, y + 10), txt, font=f, fill=(0, 0, 0, 160), stroke_width=16, stroke_fill=(0, 0, 0, 160))
    g.text((x, y), txt, font=f, fill=(255, 255, 255), stroke_width=16, stroke_fill=(20, 16, 28))

def frame_at(t):
    canvas = Image.new("RGBA", (DW, DH), (0, 0, 0, 255))
    if t < T_CUT:
        shot1(canvas, t); local = t / T_CUT
    else:
        shot2(canvas, t); local = (t - T_CUT) / (TOTAL - T_CUT)
    # camera: slow push-in + handheld drift (+ impact shake on the crash)
    z = 1.0 + 0.07 * local
    shake = 0
    t_hit = wt_of("dropped") + 0.12 + (500 + math.sqrt(500 ** 2 + 4 * 1800 * 830)) / 3600
    if t > t_hit and t < t_hit + 0.35:
        shake = math.exp(-(t - t_hit) * 9) * math.sin((t - t_hit) * 70) * 22
    cw, ch = DW / z, DH / z
    cx = DW / 2 + math.sin(t * 0.8) * 8 + shake
    cy = DH / 2 + math.cos(t * 0.6) * 8 + shake * 0.6
    cx = min(max(cx, cw / 2), DW - cw / 2); cy = min(max(cy, ch / 2), DH - ch / 2)
    box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
    canvas = canvas.resize((DW, DH), Image.BICUBIC, box=box)
    draw_caption(canvas, t)
    return canvas.convert("RGB")

# ---------------------------------------------------------------- cli
def render_chunk(args):
    i, fps, W, H = args
    im = frame_at(i / fps)
    if (W, H) != (DW, DH): im = im.resize((W, H), Image.LANCZOS)
    return im.tobytes()

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "still":
        t = float(sys.argv[2]); out = sys.argv[3] if len(sys.argv) > 3 else f"still_{t:.2f}.png"
        frame_at(t).resize((720, 1280), Image.LANCZOS).save(out)
        print(out, "T_CUT=%.2f TOTAL=%.2f" % (T_CUT, TOTAL))
    else:
        W, H, fps = (int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (DW, DH, 60)
        out = sys.argv[5] if len(sys.argv) > 5 else "test_scene.mp4"
        n = int(TOTAL * fps)
        ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                               "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                               "-crf", "16", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        with Pool(4) as p:
            for k, b in enumerate(p.imap(render_chunk, [(i, fps, W, H) for i in range(n)], chunksize=4)):
                ff.stdin.write(b)
                if k % 60 == 0: print(f"{k}/{n}", flush=True)
        ff.stdin.close(); ff.wait(); print("done", out)
