"""Toon 2.5D Short renderer (Cairo) - the Blender-free stand-in for the COBRA_KING pipeline.

World units are a 1080x1920 portrait canvas; frames render at OUT_W x OUT_H (2K = 1440x2560).
A story module defines shots with @shot(start) and SFX with sfx(t, name); engine.render() does
frames -> whip-pans -> captions -> ffmpeg (x264) + VO/music/SFX mix.
"""
import json, math, os, subprocess, sys, time
import multiprocessing as mp
import numpy as np
import cairo

LANDSCAPE = os.environ.get("ASPECT", "portrait") == "landscape"
W, H = (1920, 1080) if LANDSCAPE else (1080, 1920)
OUT_W = int(os.environ.get("OUT_W", 2560 if LANDSCAPE else 1440))
OUT_H = int(os.environ.get("OUT_H", 1440 if LANDSCAPE else 2560))
FPS = int(os.environ.get("FPS", 30))
S = OUT_W / W
INK = (0x16 / 255, 0x10 / 255, 0x1E / 255)
GOLD = (1.0, 0.80, 0.25)
FONT_TITLE = "Lilita One"
FONT_CAP = "Lilita One"
HERE = os.path.dirname(os.path.abspath(__file__))


# ----------------------------------------------------------------------------- math
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lerp(a, b, t):
    return a + (b - a) * t


def ease(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_in(t):
    t = clamp(t)
    return t ** 3


def back(t, k=1.70158):
    t = clamp(t) - 1
    return t * t * ((k + 1) * t + k) + 1


def pop(t, d=0.35):
    """0->1 overshoot pop over d seconds."""
    return back(t / d, 2.2) if t < d else 1.0


def wob(t, f=1.0, a=1.0, ph=0.0):
    return math.sin((t * f + ph) * 2 * math.pi) * a


def rgb(c):
    if isinstance(c, str):
        c = c.lstrip("#")
        return tuple(int(c[i:i + 2], 16) / 255 for i in (0, 2, 4))
    if max(c) > 1.0:
        return tuple(v / 255 for v in c)
    return tuple(c)


def shade(c, k):
    """k<1 darker, k>1 lighter (towards white)."""
    c = rgb(c)
    if k <= 1:
        return tuple(v * k for v in c)
    return tuple(v + (1 - v) * (k - 1) for v in c)


def mix(a, b, t):
    a, b = rgb(a), rgb(b)
    return tuple(lerp(x, y, t) for x, y in zip(a, b))


# ----------------------------------------------------------------------------- frame
class Frame:
    def __init__(self, ctx, t, t0, t1, story):
        self.ctx, self.t, self.t0, self.t1 = ctx, t, t0, t1
        self.lt = t - t0
        self.dur = t1 - t0
        self.p = clamp(self.lt / max(self.dur, 1e-6))
        self.story = story
        self.cx, self.cy, self.z, self.rot = W / 2, H / 2, 1.0, 0.0
        self.base = ctx.get_matrix()

    # camera ------------------------------------------------------------------
    def cam(self, x=W / 2, y=H / 2, z=1.0, rot=0.0, shake=0.0):
        if shake:
            x += (math.sin(self.t * 71) + math.sin(self.t * 113)) * shake
            y += (math.cos(self.t * 83) + math.sin(self.t * 97)) * shake
            rot += math.sin(self.t * 61) * shake * 0.0008
        self.cx, self.cy, self.z, self.rot = x, y, z, rot
        self.layer(1.0)

    def layer(self, d=1.0):
        """parallax layer: d=0 fixed backdrop, d=1 main plane, d>1 foreground."""
        c = self.ctx
        c.set_matrix(self.base)
        c.translate(W / 2, H / 2)
        c.scale(1 + (self.z - 1) * d, 1 + (self.z - 1) * d)
        c.rotate(self.rot * d)
        c.translate(-(W / 2 + (self.cx - W / 2) * d), -(H / 2 + (self.cy - H / 2) * d))

    def screen(self):
        self.ctx.set_matrix(self.base)

    def at(self, word, n=1):
        return self.story.at(word, n)


# ----------------------------------------------------------------------------- drawing helpers
def fill(c, col, a=1.0):
    col = rgb(col)
    c.set_source_rgba(*col, a)
    c.fill()


def fill_keep(c, col, a=1.0):
    c.set_source_rgba(*rgb(col), a)
    c.fill_preserve()


def stroke(c, w=8, col=INK, a=1.0):
    c.set_source_rgba(*rgb(col), a)
    c.set_line_width(w)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.stroke()


def fs(c, col, w=8, a=1.0, ink=INK):
    """fill then ink-stroke current path."""
    c.set_source_rgba(*rgb(col), a)
    c.fill_preserve()
    stroke(c, w, ink)


def rrect(c, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    c.new_sub_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    c.close_path()


def ellipse(c, x, y, rx, ry):
    c.save()
    c.translate(x, y)
    c.scale(max(rx, 0.01), max(ry, 0.01))
    c.new_sub_path()
    c.arc(0, 0, 1, 0, 2 * math.pi)
    c.restore()


def poly(c, pts, close=True):
    c.move_to(*pts[0])
    for p in pts[1:]:
        c.line_to(*p)
    if close:
        c.close_path()


def vgrad(c, y0, y1, stops):
    g = cairo.LinearGradient(0, y0, 0, y1)
    for o, col in stops:
        g.add_color_stop_rgb(o, *rgb(col))
    return g


def soft_shadow(c, x, y, rx, ry, a=0.35, col=(0.36, 0.25, 0.55)):
    g = cairo.RadialGradient(0, 0, 0, 0, 0, 1)
    g.add_color_stop_rgba(0, *col, a)
    g.add_color_stop_rgba(0.6, *col, a * 0.75)
    g.add_color_stop_rgba(1, *col, 0)
    c.save()
    c.translate(x, y)
    c.scale(rx, ry)
    c.arc(0, 0, 1, 0, 2 * math.pi)
    c.set_source(g)
    c.fill()
    c.restore()


def glow(c, x, y, r, col, a=0.6):
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, *rgb(col), a)
    g.add_color_stop_rgba(1, *rgb(col), 0)
    c.arc(x, y, r, 0, 2 * math.pi)
    c.set_source(g)
    c.fill()


def screen_fill(f, col, a=1.0):
    f.screen()
    f.ctx.rectangle(0, 0, W, H)
    fill(f.ctx, col, a)


def vignette(f, a=0.45):
    c = f.ctx
    f.screen()
    g = cairo.RadialGradient(W / 2, H * 0.45, H * 0.32, W / 2, H * 0.45, H * 0.78)
    g.add_color_stop_rgba(0, 0.08, 0.04, 0.12, 0)
    g.add_color_stop_rgba(1, 0.08, 0.04, 0.12, a)
    c.rectangle(0, 0, W, H)
    c.set_source(g)
    c.fill()


def flash(f, a, col=(1, 1, 1)):
    if a > 0:
        screen_fill(f, col, clamp(a))


# ----------------------------------------------------------------------------- text
def _font(c, size, face=FONT_TITLE):
    c.select_font_face(face, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    c.set_font_size(size)


def text_w(c, s, size, face=FONT_TITLE):
    _font(c, size, face)
    return c.text_extents(s).x_advance


def text3d(f, s, x, y, size=150, t=None, depth=16, top=GOLD, side=(0.62, 0.36, 0.06),
           tilt=0.0, scale=1.0, alpha=1.0, face=FONT_TITLE, max_w=980):
    """extruded 3D title, centered at (x, y) in current transform. t: local time for pop-in."""
    c = f.ctx
    if t is not None:
        if t < 0:
            return
        scale *= pop(t, 0.32)
    if scale <= 0.01:
        return
    m0 = c.get_matrix()
    c.set_matrix(f.base)
    lines = s.split("\n")
    _font(c, size, face)
    wmax = max(c.text_extents(l).x_advance for l in lines)
    k = min(1.0, max_w / max(wmax, 1))
    c.save()
    c.translate(x, y)
    c.rotate(tilt)
    c.scale(scale * k, scale * k)
    lh = size * 1.0
    y0 = -lh * (len(lines) - 1) / 2
    for li, line in enumerate(lines):
        _font(c, size, face)
        ext = c.text_extents(line)
        bx = -ext.x_advance / 2
        by = y0 + li * lh + size * 0.36
        # outer ink contour
        for d in range(depth, -1, -2):
            c.move_to(bx + d * 0.55, by + d)
            c.text_path(line)
        c.set_source_rgba(*INK, alpha)
        c.set_line_width(size * 0.16)
        c.set_line_join(cairo.LINE_JOIN_ROUND)
        c.stroke()
        # extrusion
        for d in range(depth, 0, -1):
            c.move_to(bx + d * 0.55, by + d)
            c.text_path(line)
            c.set_source_rgba(*shade(side, 0.75 + 0.25 * (1 - d / depth)), alpha)
            c.fill()
        # face
        c.move_to(bx, by)
        c.text_path(line)
        g = cairo.LinearGradient(0, by - size * 0.75, 0, by + size * 0.05)
        g.add_color_stop_rgba(0, *shade(top, 1.45), alpha)
        g.add_color_stop_rgba(0.55, *rgb(top), alpha)
        g.add_color_stop_rgba(1, *shade(top, 0.82), alpha)
        c.set_source(g)
        c.fill_preserve()
        c.set_source_rgba(*INK, alpha)
        c.set_line_width(size * 0.035)
        c.stroke()
        # glint
        c.move_to(bx, by)
        c.text_path(line)
        c.save()
        c.clip()
        c.rectangle(bx - 20, by - size * 0.8, ext.x_advance + 40, size * 0.18)
        c.set_source_rgba(1, 1, 1, 0.28 * alpha)
        c.fill()
        c.restore()
    c.restore()
    c.set_matrix(m0)


def label(c, s, x, y, size=40, col=INK, face="Inter", weight=cairo.FONT_WEIGHT_BOLD, align="c", a=1.0):
    c.select_font_face(face, cairo.FONT_SLANT_NORMAL, weight)
    c.set_font_size(size)
    e = c.text_extents(s)
    ox = {"c": -e.x_advance / 2, "l": 0, "r": -e.x_advance}[align]
    c.move_to(x + ox, y + size * 0.35)
    c.set_source_rgba(*rgb(col), a)
    c.show_text(s)


def chalk_text(c, s, x, y, size=70, col=(0.95, 0.95, 0.92), a=1.0, reveal=1.0):
    c.select_font_face("Lilita One", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(size)
    e = c.text_extents(s)
    c.save()
    c.rectangle(x - e.x_advance / 2 - 10, y - size, (e.x_advance + 20) * clamp(reveal), size * 2)
    c.clip()
    c.move_to(x - e.x_advance / 2, y + size * 0.35)
    c.set_source_rgba(*rgb(col), a)
    c.show_text(s)
    c.restore()


# ----------------------------------------------------------------------------- story
class Story:
    def __init__(self, slug, root):
        self.slug = slug
        self.dir = os.path.join(root, "stories", slug)
        tj = json.load(open(os.path.join(self.dir, "audio", "timing.json")))
        self.timing = tj
        self.words = tj["words"]
        self.duration = tj["duration"]
        self.shots = []      # (start, fn, whip)
        self.sfx = []        # (t, name, gain)
        self.no_caption = []  # (t0, t1)

    def norm(self, w):
        return "".join(ch for ch in w.lower() if ch.isalnum() or ch == "'")

    def at(self, word, n=1, end=False):
        """start time of the n-th occurrence of word (or a phrase 'a b c')."""
        toks = [self.norm(x) for x in word.split()]
        k = 0
        for i in range(len(self.words) - len(toks) + 1):
            if all(self.norm(self.words[i + j]["w"]) == toks[j] for j in range(len(toks))):
                k += 1
                if k == n:
                    return self.words[i + len(toks) - 1]["e"] if end else self.words[i]["s"]
        raise KeyError(f"{word!r} #{n} not in VO")

    def shot(self, start, whip=True):
        def deco(fn):
            st = self.at(start) if isinstance(start, str) else float(start)
            self.shots.append((st, fn, whip))
            return fn
        return deco

    def add_sfx(self, t, name, gain=1.0):
        t = self.at(t) if isinstance(t, str) else t
        self.sfx.append((t, name, gain))

    def finalize(self):
        self.shots.sort(key=lambda s: s[0])
        self.shots[0] = (0.0,) + self.shots[0][1:]
        self.spans = []
        for i, (st, fn, wh) in enumerate(self.shots):
            en = self.shots[i + 1][0] if i + 1 < len(self.shots) else self.duration
            self.spans.append((st, en, fn, wh))
        self.cuts = [(st, wh) for st, _, wh in self.shots[1:]]
        # caption groups
        groups, cur = [], []
        for w in self.words:
            cur.append(w)
            txt = w["w"]
            if len(cur) >= 3 or txt.endswith((",", ".", "?", "!", "...")) or (len(cur) >= 2 and len("".join(x["w"] for x in cur)) > 13):
                groups.append(cur)
                cur = []
        if cur:
            groups.append(cur)
        self.groups = []
        for i, g in enumerate(groups):
            s0 = g[0]["s"]
            s1 = groups[i + 1][0]["s"] if i + 1 < len(groups) else g[-1]["e"] + 0.5
            s1 = min(s1, g[-1]["e"] + 0.6)
            self.groups.append((s0, s1, g))


# ----------------------------------------------------------------------------- captions
def captions(f, story):
    t = f.t
    for t0, t1 in story.no_caption:
        if t0 <= t < t1:
            return
    for s0, s1, g in story.groups:
        if s0 <= t < s1:
            break
    else:
        return
    c = f.ctx
    f.screen()
    size = 64 if LANDSCAPE else 92
    _font(c, size, FONT_CAP)
    toks = []
    for w in g:
        s = w["w"].replace("...", "").rstrip(",.;:")
        toks.append((s, w))
    space = c.text_extents(" ").x_advance
    widths = [c.text_extents(s).x_advance for s, _ in toks]
    total = sum(widths) + space * (len(toks) - 1)
    sc = pop(t - s0, 0.22) if t - s0 < 0.22 else 1.0
    sc = 0.6 + 0.4 * sc
    k = min(1.0, (W * 0.8 if LANDSCAPE else 940) / max(total, 1))
    c.save()
    c.translate(W / 2, H * (0.905 if LANDSCAPE else 0.72))
    c.scale(sc * k, sc * k)
    x = -total / 2
    started = [w for w in g if w["s"] <= t]
    cur = started[-1] if started else None
    for (s, w), wd in zip(toks, widths):
        c.move_to(x, size * 0.35)
        c.text_path(s)
        c.set_source_rgb(*INK)
        c.set_line_width(14 if LANDSCAPE else 20)
        c.set_line_join(cairo.LINE_JOIN_ROUND)
        c.stroke_preserve()
        c.set_source_rgb(*(rgb("#FFD84A") if w is cur else (1, 1, 1)))
        c.fill()
        x += wd + space
    c.restore()


# ----------------------------------------------------------------------------- post: whip pan
def whip(arr, amount, direction):
    """arr HxWx4 uint8; amount 0..1 -> shift + horizontal motion blur."""
    if amount <= 0.001:
        return arr
    h, w, _ = arr.shape
    shift = int(direction * amount * w * 0.45)
    out = np.roll(arr, shift, axis=1)
    r = int(4 + amount * 110)
    a = out[:, :, :3].astype(np.float32)
    cs = np.cumsum(np.pad(a, ((0, 0), (r + 1, r), (0, 0)), mode="edge"), axis=1)
    bl = (cs[:, 2 * r + 1:] - cs[:, :-2 * r - 1]) / (2 * r + 1)
    out = out.copy()
    out[:, :, :3] = bl[:, :w].clip(0, 255).astype(np.uint8)
    return out


WHIP = 0.12


# ----------------------------------------------------------------------------- render
_STORY = None


def render_frame(i):
    story = _STORY
    t = i / FPS
    # which shot (with whip borrow)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, OUT_W, OUT_H)
    ctx = cairo.Context(surf)
    ctx.scale(S, S)
    amt, direction = 0.0, 1
    idx = 0
    for k, (st, en, fn, wh) in enumerate(story.spans):
        if st <= t < en:
            idx = k
            break
    else:
        idx = len(story.spans) - 1
    st, en, fn, wh = story.spans[idx]
    if wh and idx > 0 and t - st < WHIP:
        amt = 1 - (t - st) / WHIP
        direction = 1
    elif idx + 1 < len(story.spans) and story.spans[idx + 1][3] and en - t < WHIP:
        amt = 1 - (en - t) / WHIP
        direction = -1
    f = Frame(ctx, t, st, en, story)
    ctx.save()
    fn(f)
    ctx.restore()
    f.screen()
    surf.flush()
    arr = np.ndarray((OUT_H, OUT_W, 4), np.uint8, surf.get_data()).copy()
    if amt > 0:
        arr = whip(arr, ease_in(amt) * 0.9 + 0.1 * amt, direction)
        surf2 = cairo.ImageSurface.create_for_data(memoryview(arr), cairo.FORMAT_RGB24, OUT_W, OUT_H)
        ctx2 = cairo.Context(surf2)
        ctx2.scale(S, S)
        f2 = Frame(ctx2, t, st, en, story)
        captions(f2, story)
        surf2.flush()
        return arr.tobytes()
    captions(f, story)
    surf.flush()
    return bytes(surf.get_data())


def _init(story):
    global _STORY
    _STORY = story


def render(story, out_path, t0=None, t1=None, stills=None, workers=None):
    global _STORY
    story.finalize()
    _STORY = story
    if stills:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        from PIL import Image
        ims = []
        for t in stills:
            data = render_frame(int(t * FPS))
            a = np.frombuffer(data, np.uint8).reshape(OUT_H, OUT_W, 4)[:, :, 2::-1]
            ims.append(Image.fromarray(a.copy()))
        tw, th = OUT_W // 4, OUT_H // 4
        cols = 6
        rows = (len(ims) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * tw, rows * th), (30, 20, 40))
        for k, im in enumerate(ims):
            sheet.paste(im.resize((tw, th)), ((k % cols) * tw, (k // cols) * th))
        sheet.save(out_path)
        return out_path
    n0 = int((t0 or 0) * FPS)
    n1 = int((t1 if t1 is not None else story.duration) * FPS)
    audio = os.path.join(story.dir, "audio", "mix.wav")
    tmp = out_path + ".video.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
           "-s", f"{OUT_W}x{OUT_H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
           "-profile:v", "high", "-level", "5.1", tmp]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    ctx = mp.get_context("fork")
    workers = workers or os.cpu_count()
    t_start = time.time()
    with ctx.Pool(workers, initializer=_init, initargs=(story,)) as pool:
        for k, data in enumerate(pool.imap(render_frame, range(n0, n1), chunksize=4)):
            p.stdin.write(data)
            if k % 150 == 0:
                el = time.time() - t_start
                print(f"  frame {k}/{n1 - n0}  {el:.0f}s", flush=True)
    p.stdin.close()
    p.wait()
    ss = n0 / FPS
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-ss", f"{ss}", "-t", f"{(n1 - n0) / FPS}",
                    "-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", out_path], check=True)
    os.remove(tmp)
    print(f"wrote {out_path} in {time.time() - t_start:.0f}s")
