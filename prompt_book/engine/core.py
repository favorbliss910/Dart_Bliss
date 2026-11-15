# Core helpers: timing, easing, colors, skia drawing utilities, noise.
import os, json, math, re, functools
import numpy as np
import skia
from PIL import Image

W, H = 1920, 1080
FPS = 60
HERE = os.path.dirname(os.path.abspath(__file__))
# PROJECT = folder holding this video's words.json + scenes*.py (set JV_PROJECT, default: current dir)
PROJECT = os.path.abspath(os.environ.get('JV_PROJECT', os.getcwd()))
CACHE = os.path.join(PROJECT, 'cache')
os.makedirs(CACHE, exist_ok=True)
SAFE_BOTTOM = int(H * 0.85)  # keep critical info above this line

# ---------------------------------------------------------------- timing
_WORDS = json.load(open(os.path.join(PROJECT, 'words.json')))
_NORM = [re.sub(r"[^a-z0-9]", "", w.lower()) for w, _ in _WORDS]
_TIMES = [t for _, t in _WORDS]

def at(phrase, after=0.0, end=False):
    """Start time (s) of first occurrence of phrase in narration at/after `after`.
    end=True returns the start time of the word following the phrase."""
    toks = [re.sub(r"[^a-z0-9]", "", p.lower()) for p in phrase.split()]
    toks = [t for t in toks if t]
    n = len(toks)
    for i in range(len(_NORM) - n + 1):
        if _TIMES[i] < after - 1e-6:
            continue
        if _NORM[i:i + n] == toks:
            if end:
                j = i + n
                return _TIMES[j] if j < len(_TIMES) else _TIMES[-1] + 0.6
            return _TIMES[i]
    raise KeyError(f"phrase not found: {phrase!r} after {after}")

# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x

def lerp(a, b, t):
    return a + (b - a) * t

def prog(t, t0, t1):
    if t1 <= t0:
        return 1.0 if t >= t1 else 0.0
    return clamp((t - t0) / (t1 - t0))

def e_in(x):  return x * x * x
def e_out(x): return 1 - (1 - x) ** 3
def e_io(x):  return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def e_sine(x): return -(math.cos(math.pi * x) - 1) / 2
def e_back(x, s=1.70158):
    x -= 1
    return x * x * ((s + 1) * x + s) + 1
def e_expo_out(x): return 1 if x >= 1 else 1 - 2 ** (-10 * x)

def tw(t, t0, t1, a, b, ease=e_io):
    return lerp(a, b, ease(prog(t, t0, t1)))

def fade_window(t, t0, t1, fin=0.35, fout=0.35):
    """1 inside [t0,t1] with fades at both ends."""
    if t < t0 or t > t1:
        return 0.0
    a = e_out(prog(t, t0, t0 + fin)) if fin > 0 else 1.0
    b = 1 - e_in(prog(t, t1 - fout, t1)) if fout > 0 else 1.0
    return min(a, b)

def keys(t, kf, ease=e_io):
    """Piecewise interpolation through [(time, value), ...]. value may be tuple."""
    if t <= kf[0][0]:
        return kf[0][1]
    for (t0, v0), (t1, v1) in zip(kf, kf[1:]):
        if t <= t1:
            x = ease(prog(t, t0, t1))
            if isinstance(v0, (tuple, list)):
                return tuple(lerp(a, b, x) for a, b in zip(v0, v1))
            return lerp(v0, v1, x)
    return kf[-1][1]

def shake(t, t0, dur, amp, freq=22.0, seed=1):
    """Damped shake offset (dx, dy) starting at t0."""
    if t < t0 or t > t0 + dur:
        return 0.0, 0.0
    x = (t - t0)
    d = math.exp(-4.0 * x / dur) * (1 - prog(t, t0 + dur * .8, t0 + dur))
    return (amp * d * math.sin(x * freq * 6.283 + seed),
            amp * d * math.sin(x * freq * 1.37 * 6.283 + seed * 2.1) * .7)

def wobble(t, amp, f=0.2, seed=0.0):
    return amp * (math.sin(t * f * 6.283 + seed) * .6 + math.sin(t * f * 2.71 * 6.283 + seed * 1.7) * .4)

# ---------------------------------------------------------------- color
def hexc(h, a=1.0):
    h = h.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return skia.Color(r, g, b, int(clamp(a) * 255))

def rgba(r, g, b, a=1.0):
    return skia.Color(int(r), int(g), int(b), int(clamp(a) * 255))

def mixc(h1, h2, x, a=1.0):
    h1, h2 = h1.lstrip('#'), h2.lstrip('#')
    c1 = [int(h1[i:i + 2], 16) for i in (0, 2, 4)]
    c2 = [int(h2[i:i + 2], 16) for i in (0, 2, 4)]
    return skia.Color(*[int(lerp(a_, b_, clamp(x))) for a_, b_ in zip(c1, c2)], int(clamp(a) * 255))

def with_alpha(c, a):
    return skia.ColorSetA(c, int(clamp(a) * skia.ColorGetA(c)))

PAL = dict(
    jbg='#2A1810', jmid='#B9773E', jlight='#E3B47A', jhi='#FFF1D6',
    sp0='#070B1A', sp1='#1C2A55', sp2='#3D5A9E', white='#FFFFFF',
    danger='#FF3B30', cyan='#6FD3FF', blue='#4C8DFF', purple='#8A5CFF',
    hud='#9FE3FF', ok='#58E08A', warm='#FFB347', grs='#B5502A',
)

# ---------------------------------------------------------------- fonts
@functools.lru_cache(None)
def font(size, weight='bold', family='Inter Display'):
    st = {'black': skia.FontStyle(900, 5, skia.FontStyle.kUpright_Slant),
          'xbold': skia.FontStyle(800, 5, skia.FontStyle.kUpright_Slant),
          'bold': skia.FontStyle.Bold(),
          'semi': skia.FontStyle(600, 5, skia.FontStyle.kUpright_Slant),
          'medium': skia.FontStyle(500, 5, skia.FontStyle.kUpright_Slant),
          'regular': skia.FontStyle.Normal(),
          'light': skia.FontStyle(300, 5, skia.FontStyle.kUpright_Slant)}[weight]
    f = skia.Font(skia.Typeface(family, st), size)
    f.setSubpixel(True)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    return f

def mono(size, weight='medium'):
    return font(size, weight, 'JetBrains Mono')

def text_w(s, f):
    return f.measureText(s)

def draw_text(c, s, x, y, f, color, align='left', alpha=1.0, glow=0.0, glow_color=None,
              shadow=0.0, spacing=0.0):
    if alpha <= 0.003 or not s:
        return
    if spacing:
        # manual letter spacing
        widths = [f.measureText(ch) for ch in s]
        total = sum(widths) + spacing * (len(s) - 1)
        x0 = x - total / 2 if align == 'center' else x - total if align == 'right' else x
        for ch, w_ in zip(s, widths):
            draw_text(c, ch, x0, y, f, color, 'left', alpha, glow, glow_color, shadow)
            x0 += w_ + spacing
        return
    w = f.measureText(s)
    if align == 'center':
        x -= w / 2
    elif align == 'right':
        x -= w
    if shadow > 0:
        p = skia.Paint(AntiAlias=True, Color=rgba(0, 0, 0, .55 * alpha * shadow),
                       MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 6))
        c.drawString(s, x + 2, y + 4, f, p)
    if glow > 0:
        gc = glow_color if glow_color is not None else color
        p = skia.Paint(AntiAlias=True, Color=with_alpha(gc, alpha * glow),
                       MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, f.getSize() * .18))
        c.drawString(s, x, y, f, p)
    p = skia.Paint(AntiAlias=True, Color=with_alpha(color, alpha))
    c.drawString(s, x, y, f, p)

def text_pop(c, s, x, y, f, color, t, t0, dur=0.35, align='center', alpha=1.0, **kw):
    """Text that pops in with slight scale overshoot (0.25-0.42s)."""
    if t < t0:
        return
    k = prog(t, t0, t0 + dur)
    sc = lerp(0.82, 1.0, e_back(k, 2.2)) if k < 1 else 1.0
    c.save()
    c.translate(x, y)
    c.scale(sc, sc)
    draw_text(c, s, 0, 0, f, color, align, alpha * e_out(min(1, k * 1.6)), **kw)
    c.restore()

# ---------------------------------------------------------------- paints
def P(color=None, stroke=None, aa=True, blur=0, blend=None, shader=None, cap=None, join=None, alpha=None):
    p = skia.Paint(AntiAlias=aa)
    if color is not None:
        p.setColor(color)
    if alpha is not None:
        p.setAlphaf(alpha)
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if blend is not None:
        p.setBlendMode(blend)
    if shader is not None:
        p.setShader(shader)
    if cap == 'round':
        p.setStrokeCap(skia.Paint.kRound_Cap)
    if join == 'round':
        p.setStrokeJoin(skia.Paint.kRound_Join)
    return p

def lin(p0, p1, colors, pos=None):
    return skia.GradientShader.MakeLinear([skia.Point(*p0), skia.Point(*p1)], colors, pos)

def rad(cx, cy, r, colors, pos=None):
    return skia.GradientShader.MakeRadial(skia.Point(cx, cy), max(r, 0.01), colors, pos)

def path_from(points, close=False):
    pa = skia.Path()
    pa.moveTo(*points[0])
    for p in points[1:]:
        pa.lineTo(*p)
    if close:
        pa.close()
    return pa

def rrect(c, x, y, w, h, r, paint):
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r), paint)

PLUS = skia.BlendMode.kPlus
SCREEN = skia.BlendMode.kScreen
MULT = skia.BlendMode.kMultiply
LIN = skia.SamplingOptions(skia.FilterMode.kLinear)
MIP = skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear)

# ---------------------------------------------------------------- images
def to_img(arr, alpha=None):
    """arr: HxWx3 or HxWx4, float 0..1 or uint8, RGB order. Returns premul BGRA skia.Image."""
    a = np.asarray(arr)
    if a.dtype != np.float32:
        a = a.astype(np.float32) / (255.0 if a.dtype == np.uint8 else 1.0)
    h, w = a.shape[:2]
    out = np.empty((h, w, 4), np.uint8)
    if a.shape[2] == 4:
        al = np.clip(a[..., 3], 0, 1)
    elif alpha is not None:
        al = np.clip(alpha, 0, 1)
    else:
        al = np.ones((h, w), np.float32)
    rgb = np.clip(a[..., :3], 0, 1) * al[..., None]
    out[..., 0] = (rgb[..., 2] * 255 + .5).astype(np.uint8)
    out[..., 1] = (rgb[..., 1] * 255 + .5).astype(np.uint8)
    out[..., 2] = (rgb[..., 0] * 255 + .5).astype(np.uint8)
    out[..., 3] = (al * 255 + .5).astype(np.uint8)
    return skia.Image.fromarray(out, colorType=skia.kBGRA_8888_ColorType, alphaType=skia.kPremul_AlphaType)

def draw_img(c, img, x, y, w=None, h=None, alpha=1.0, blend=None, cf=None):
    if alpha <= 0.003:
        return
    w = img.width() if w is None else w
    h = img.height() if h is None else h
    p = skia.Paint(AntiAlias=True)
    p.setAlphaf(clamp(alpha))
    if blend is not None:
        p.setBlendMode(blend)
    if cf is not None:
        p.setColorFilter(cf)
    c.drawImageRect(img, skia.Rect.MakeXYWH(x, y, w, h), LIN, p)

def draw_img_c(c, img, cx, cy, scale=1.0, alpha=1.0, rot=0.0, blend=None, cf=None, sx=None, sy=None):
    """Draw image centered at (cx,cy) with scale and rotation (deg)."""
    if alpha <= 0.003:
        return
    c.save()
    c.translate(cx, cy)
    if rot:
        c.rotate(rot)
    sxx = scale if sx is None else sx
    syy = scale if sy is None else sy
    w, h = img.width() * sxx, img.height() * syy
    draw_img(c, img, -w / 2, -h / 2, w, h, alpha, blend, cf)
    c.restore()

def tint_cf(r, g, b, amount=1.0, bright=1.0):
    """Color filter: multiply RGB by color (0..1 floats)."""
    m = [r * bright, 0, 0, 0, 0,
         0, g * bright, 0, 0, 0,
         0, 0, b * bright, 0, 0,
         0, 0, 0, 1, 0]
    return skia.ColorFilters.Matrix(m)

# ---------------------------------------------------------------- noise
def noise2(h, w, cells_y, cells_x, seed=0, wrap_x=False, octaves=1, persistence=0.5):
    """Smooth value noise in [0,1] via bicubic upsampling, fractal octaves."""
    rng = np.random.default_rng(seed)
    total = np.zeros((h, w), np.float32)
    amp, norm = 1.0, 0.0
    cy, cx = cells_y, cells_x
    for o in range(octaves):
        cyi, cxi = max(2, int(cy)), max(2, int(cx))
        g = rng.random((cyi + 3, cxi + 3)).astype(np.float32)
        if wrap_x:
            g[:, cxi:cxi + 3] = g[:, 0:3]
        im = Image.fromarray(g, mode='F')
        # resize so that cell grid maps exactly with 1 cell padding on each side
        big = im.resize((int(w * (cxi + 3) / cxi), int(h * (cyi + 3) / cyi)), Image.BICUBIC)
        arr = np.asarray(big)
        ox = int(w / cxi * 1)
        oy = int(h / cyi * 1)
        total += amp * arr[oy:oy + h, ox:ox + w]
        norm += amp
        amp *= persistence
        cy *= 2
        cx *= 2
    total /= norm
    lo, hi = np.percentile(total, 1), np.percentile(total, 99)
    return np.clip((total - lo) / (hi - lo + 1e-6), 0, 1)

def cached_npy(name, fn):
    p = os.path.join(CACHE, name + '.npy')
    if os.path.exists(p):
        return np.load(p)
    a = fn()
    np.save(p, a)
    return a
