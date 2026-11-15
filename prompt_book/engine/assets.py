# Procedural assets: Jupiter/Earth textures + sphere renderer, cloud sprites, stars, overlays.
import math, functools
import numpy as np
import skia
from PIL import Image
from core import *

TH, TW = 2048, 4096

def _hex3(h):
    h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255

JUP_BANDS = [
    (90, '#5f5650'), (70, '#6f645a'), (62, '#8c7c6a'), (57, '#c2a27c'), (52, '#a27650'),
    (47, '#dcc39d'), (42, '#b08158'), (37, '#ecd8b4'), (33, '#9a6942'), (29, '#f2dfbd'),
    (24, '#e8cfa4'), (19.5, '#a86a3d'), (15, '#8a4e2b'), (10, '#9c5c34'), (7.5, '#e9d6b4'),
    (3, '#fff1d6'), (-2, '#f6e6c8'), (-6.5, '#e3c9a0'), (-8.5, '#a0623a'), (-13, '#8a4e2b'),
    (-17.5, '#b9773e'), (-20.5, '#efdcb9'), (-25, '#f3e2c2'), (-28.5, '#e3b47a'), (-31, '#a8774c'),
    (-35, '#ead6b2'), (-40, '#ddc19a'), (-44, '#ad8258'), (-49, '#d6b88f'), (-55, '#a88a6b'),
    (-62, '#8a7b6c'), (-72, '#6c6158'), (-90, '#5c534d')]

def _band_lookup(lat):
    lats = np.array([b[0] for b in JUP_BANDS][::-1], np.float32)
    cols = np.stack([_hex3(b[1]) for b in JUP_BANDS][::-1])
    out = np.empty(lat.shape + (3,), np.float32)
    for k in range(3):
        out[..., k] = np.interp(lat, lats, cols[:, k])
    return out

def _make_jupiter_tex():
    H_, W_ = TH, TW
    yy = (np.arange(H_, dtype=np.float32) + .5) / H_
    xx = (np.arange(W_, dtype=np.float32) + .5) / W_
    lat = (0.5 - yy)[:, None] * 180.0 * np.ones((1, W_), np.float32)
    lon = xx[None, :] * 360.0 * np.ones((H_, 1), np.float32)
    # elongated turbulence (stretched in longitude)
    n1 = noise2(H_, W_, 90, 22, seed=3, wrap_x=True, octaves=5, persistence=.55) - .5
    n2 = noise2(H_, W_, 40, 10, seed=7, wrap_x=True, octaves=4) - .5
    # stronger turbulence near belt edges
    amp = 1.1 + 1.6 * (np.abs(np.sin(np.radians(lat) * 9.0)))
    lat_e = lat + n1 * amp * 2.2 + n2 * 2.0
    # festoons / plumes at the north edge of the equatorial zone
    fest = np.exp(-((lat - 7.0) / 3.5) ** 2) * (np.sin(np.radians(lon) * 13 + n2 * 4) ** 12) * 2.6
    lat_e = lat_e + fest
    # Great Red Spot vortex swirl: lat -22, lon 180
    g_lat, g_lon, a_ax, b_ax = -22.0, 180.0, 7.6, 4.7
    dx = (lon - g_lon) * math.cos(math.radians(g_lat))
    dy = lat - g_lat
    rr = np.sqrt((dx / a_ax) ** 2 + (dy / b_ax) ** 2)
    ang = 2.6 * np.exp(-rr ** 2 * 0.8)
    ca, sa = np.cos(ang), np.sin(ang)
    sdx = dx * ca - dy * sa * (a_ax / b_ax) * .6
    sdy = dx * sa / (a_ax / b_ax) * .6 + dy * ca
    lat_e = np.where(rr < 2.4, g_lat + sdy + (lat_e - lat) * np.clip(rr / 2.4, 0, 1), lat_e)
    col = _band_lookup(lat_e)
    # fine streak detail
    n3 = noise2(H_, W_, 420, 60, seed=11, wrap_x=True, octaves=3) - .5
    col *= (1.0 + n3[..., None] * 0.16 + n1[..., None] * 0.10)
    # GRS colour
    rr2 = np.sqrt(((lon - g_lon) * math.cos(math.radians(g_lat)) / a_ax) ** 2 + ((lat - g_lat) / b_ax) ** 2)
    rr2 = rr2 + (n1 * 0.25)
    core_c = _hex3('#c0502e'); rim_c = _hex3('#d98a5a'); collar = _hex3('#f6e7cc')
    m_core = np.clip((1.0 - rr2) / 0.35, 0, 1)[..., None]
    m_rim = np.clip((1.18 - rr2) / 0.2, 0, 1)[..., None]
    m_col = (np.exp(-((rr2 - 1.32) / 0.16) ** 2))[..., None]
    swirl = (np.sin(rr2 * 22 + np.arctan2(lat - g_lat, (lon - g_lon) * .5) * 2) * .5 + .5)[..., None]
    col = col * (1 - m_col * .6) + collar * m_col * .6
    col = col * (1 - m_rim) + rim_c * m_rim * (0.92 + 0.08 * swirl)
    col = col * (1 - m_core) + core_c * m_core * (0.9 + 0.12 * swirl)
    # white ovals in southern temperate region
    rng = np.random.default_rng(5)
    for k in range(9):
        olon = rng.uniform(0, 360); olat = rng.choice([-41, -33.5, 39.5, -46]) + rng.uniform(-1, 1)
        oa, ob = rng.uniform(2.2, 4.0), rng.uniform(1.2, 2.0)
        d = np.sqrt((((lon - olon + 180) % 360 - 180) * math.cos(math.radians(olat)) / oa) ** 2 + ((lat - olat) / ob) ** 2)
        m = np.clip(1.3 - d, 0, 1)[..., None] ** 1.5
        col = col * (1 - m * .85) + _hex3('#fbf2e2') * m * .85
    # small dark barges in NEB
    for k in range(7):
        olon = rng.uniform(0, 360); olat = 15.5 + rng.uniform(-1, 1)
        d = np.sqrt((((lon - olon + 180) % 360 - 180) / 3.0) ** 2 + ((lat - olat) / 1.0) ** 2)
        m = np.clip(1.2 - d, 0, 1)[..., None]
        col = col * (1 - m * .5) + _hex3('#5a2c18') * m * .5
    return np.clip(col, 0, 1).astype(np.float16)

@functools.lru_cache(None)
def jupiter_tex():
    return cached_npy('jup_tex_v5', _make_jupiter_tex).astype(np.float32)

def _make_earth_tex():
    H_, W_ = 512, 1024
    n = noise2(H_, W_, 6, 12, seed=21, wrap_x=True, octaves=6, persistence=.5)
    yy = (np.arange(H_) + .5) / H_
    lat = (0.5 - yy)[:, None] * 180 * np.ones((1, W_))
    land = n > 0.56
    ocean = np.array([0.05, 0.22, 0.48]) * (0.8 + 0.3 * n[..., None])
    green = np.array([0.18, 0.42, 0.16]); desert = np.array([0.72, 0.58, 0.36])
    dry = np.clip((np.abs(np.abs(lat) - 24) < 9) * 1.0 * (n > .62), 0, 1)[..., None]
    landc = green * (1 - dry) + desert * dry
    col = np.where(land[..., None], landc * (0.85 + 0.3 * n[..., None]), ocean)
    ice = (np.abs(lat) > 68)[..., None]
    col = np.where(ice, np.array([0.93, 0.95, 0.98]), col)
    cl = noise2(H_, W_, 10, 24, seed=33, wrap_x=True, octaves=5)
    cm = np.clip((cl - 0.55) * 3.2, 0, 1)[..., None] * 0.85
    col = col * (1 - cm) + cm * 0.97
    return np.clip(col, 0, 1).astype(np.float32)

@functools.lru_cache(None)
def earth_tex():
    return cached_npy('earth_tex_v1', _make_earth_tex)

_LIGHT = np.array([-0.62, -0.38, 0.69], np.float32)
_LIGHT /= np.linalg.norm(_LIGHT)

def sphere_layer(tex, cx, cy, R, rot=0.0, light=None, ambient=0.035, alpha=1.0, max_grid=1150,
                 limb=0.35, bilinear=None, screen=(W, H)):
    """Render a textured, lit sphere; returns (skia.Image, rect) or None."""
    if R < 1:
        return None
    L = _LIGHT if light is None else np.asarray(light, np.float32) / np.linalg.norm(light)
    x0, y0 = max(0, cx - R - 2), max(0, cy - R - 2)
    x1, y1 = min(screen[0], cx + R + 2), min(screen[1], cy + R + 2)
    if x1 <= x0 or y1 <= y0:
        return None
    vw, vh = x1 - x0, y1 - y0
    g = min(1.0, max_grid / max(vw, vh))
    gw, gh = max(2, int(vw * g)), max(2, int(vh * g))
    xs = x0 + (np.arange(gw, dtype=np.float32) + .5) * (vw / gw)
    ys = y0 + (np.arange(gh, dtype=np.float32) + .5) * (vh / gh)
    nx = ((xs - cx) / R)[None, :]
    ny = ((ys - cy) / R)[:, None]
    r2 = nx * nx + ny * ny
    inside = r2 < 1.0
    nz = np.sqrt(np.clip(1 - r2, 0, 1))
    th, twd = tex.shape[:2]
    lat = np.arcsin(np.clip(-ny * np.ones_like(nx), -1, 1))
    lon = np.arctan2(nx * np.ones_like(ny), nz) + rot
    fy = (0.5 - lat / math.pi) * th - .5
    fx = (lon / (2 * math.pi)) * twd - .5
    texels_per_px = (twd / (2 * math.pi * R)) * (vw / gw)
    if bilinear is None:
        bilinear = texels_per_px < 1.0
    if bilinear:
        ix = np.floor(fx).astype(np.int64); iy = np.floor(fy).astype(np.int64)
        tx = (fx - ix)[..., None]; ty = (fy - iy)[..., None]
        ix0 = ix % twd; ix1 = (ix + 1) % twd
        iy0 = np.clip(iy, 0, th - 1); iy1 = np.clip(iy + 1, 0, th - 1)
        col = ((tex[iy0, ix0] * (1 - tx) + tex[iy0, ix1] * tx) * (1 - ty) +
               (tex[iy1, ix0] * (1 - tx) + tex[iy1, ix1] * tx) * ty)
    else:
        ix = np.round(fx).astype(np.int64) % twd
        iy = np.clip(np.round(fy).astype(np.int64), 0, th - 1)
        col = tex[iy, ix]
    ndl = nx * L[0] + ny * L[1] + nz * L[2]
    lit = np.clip(ndl * 1.15 + 0.05, 0, 1) ** 0.85
    mu = nz
    shade = lit * (1 - limb + limb * mu ** 0.5) + ambient
    col = col * shade[..., None]
    # faint warm terminator scattering
    term = np.exp(-((ndl - 0.02) / 0.09) ** 2) * 0.05
    col[..., 0] += term; col[..., 1] += term * .45
    edge = np.clip((1 - np.sqrt(r2)) * R * g * 1.0 + 0.5, 0, 1)
    a = edge * inside * alpha
    img = to_img(col, alpha=a)
    return img, skia.Rect(x0, y0, x1, y1)

def draw_sphere(c, tex, cx, cy, R, rot=0.0, alpha=1.0, atmo=None, **kw):
    r = sphere_layer(tex, cx, cy, R, rot, alpha=alpha, **kw)
    if r is None:
        return
    img, rect = r
    p = skia.Paint(AntiAlias=True)
    c.drawImageRect(img, rect, LIN, p)
    if atmo is not None and alpha > 0:
        # thin atmospheric rim glow, brighter on lit side
        col = atmo
        sh = rad(cx, cy, R * 1.06, [skia.ColorTRANSPARENT, skia.ColorTRANSPARENT, with_alpha(col, .45 * alpha), skia.ColorTRANSPARENT],
                 [0, 0.90, 0.945, 1.0])
        c.drawCircle(cx, cy, R * 1.06, P(shader=sh))

def draw_jupiter(c, cx, cy, R, rot=0.0, alpha=1.0, **kw):
    draw_sphere(c, jupiter_tex(), cx, cy, R, rot, alpha, atmo=hexc('#ffd9a0'), **kw)

def draw_earth(c, cx, cy, R, rot=0.0, alpha=1.0, **kw):
    kw.setdefault('limb', 0.2)
    draw_sphere(c, earth_tex(), cx, cy, R, rot, alpha, atmo=hexc('#7fb8ff'), **kw)

# ---------------------------------------------------------------- simple vector Earth (for many small copies)
def draw_earth_icon(c, x, y, r, alpha=1.0):
    c.drawCircle(x, y, r, P(shader=rad(x - r * .35, y - r * .35, r * 1.5, [hexc('#5fa8ff', alpha), hexc('#1d4f9a', alpha), hexc('#0b1d3d', alpha)], [0, .55, 1])))
    if r > 3:
        c.drawCircle(x - r * .25, y - r * .1, r * .38, P(hexc('#4f9a4a', .9 * alpha)))
        c.drawCircle(x + r * .3, y + r * .3, r * .22, P(hexc('#4f9a4a', .9 * alpha)))

# ---------------------------------------------------------------- clouds
def _make_cloud(seed, w=512, h=300):
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    D = np.zeros((h, w), np.float32)
    nb = int(rng.integers(16, 24))
    for i in range(nb):
        u = rng.uniform(.15, .85)
        bx = u * w
        br = rng.uniform(.05, .11) * w * (1.25 - abs(u - .5) * 1.2)
        by = h * .72 - br * rng.uniform(.2, 1.6) * (1.3 - abs(u - .5) * 1.6)
        D += np.exp(-(((xx - bx) ** 2 + (yy - by) ** 2) / (br * br)))
    n = noise2(h, w, 4, 7, seed=seed + 100, octaves=3, persistence=.45)
    D = D * (0.85 + 0.3 * n)
    D *= np.clip((h * .78 - yy) / (h * .18), 0, 1) ** .7
    a = np.clip((D - 0.30) / 0.35, 0, 1)
    a = a * a * (3 - 2 * a)
    gy = np.gradient(a, axis=0)
    top_rim = np.clip(-gy * 0 + gy * 6, 0, 1)  # gy>0 at upper edges (alpha grows downward)
    vert = 1 - yy / h
    v = 0.62 + 0.42 * vert ** .8 + 0.3 * top_rim + (n - .5) * .1
    col = np.stack([v, v, v], -1)
    return to_img(np.clip(col, 0, 1.1), alpha=a * .97)

@functools.lru_cache(None)
def cloud_sprites():
    return [_make_cloud(s) for s in range(1, 9)]

def _make_haze(seed, w=1024, h=220):
    yy = (np.arange(h, dtype=np.float32) / h)[:, None]
    n = noise2(h, w, 3, 14, seed=seed, octaves=4, wrap_x=True)
    prof = np.exp(-((yy - .5) / .22) ** 2)
    a = np.clip(prof * (0.4 + 0.9 * n) - 0.15, 0, 1)
    v = 0.8 + 0.2 * n
    return to_img(np.stack([v, v, v], -1), alpha=a)

@functools.lru_cache(None)
def haze_sprites():
    return [_make_haze(s) for s in range(40, 46)]

# ---------------------------------------------------------------- stars
@functools.lru_cache(None)
def star_field(seed=1, n=900):
    rng = np.random.default_rng(seed)
    xs = rng.uniform(-200, W + 200, n); ys = rng.uniform(-200, H + 200, n)
    mag = rng.power(3.2, n)[::-1]  # many faint
    mag = rng.random(n) ** 3.5
    tw_ = rng.uniform(0, 6.28, n)
    depth = rng.uniform(.2, 1.0, n)
    tint = rng.random(n)
    return xs, ys, mag, tw_, depth, tint

def draw_stars(c, t, alpha=1.0, ox=0.0, oy=0.0, zoom=1.0, seed=1, n=900, cx=W / 2, cy=H / 2):
    if alpha <= 0:
        return
    xs, ys, mag, tw_, depth, tint = star_field(seed, n)
    for i in range(len(xs)):
        x = cx + (xs[i] - cx + ox * depth[i]) * (1 + (zoom - 1) * depth[i])
        y = cy + (ys[i] - cy + oy * depth[i]) * (1 + (zoom - 1) * depth[i])
        if x < -5 or x > W + 5 or y < -5 or y > H + 5:
            continue
        m = mag[i]
        a = alpha * (0.25 + 0.75 * m) * (0.85 + 0.15 * math.sin(t * 1.3 + tw_[i]))
        r = 0.6 + 1.6 * m
        col = rgba(255, 244, 230, a) if tint[i] > .7 else rgba(200, 220, 255, a) if tint[i] < .25 else rgba(255, 255, 255, a)
        c.drawCircle(x, y, r, P(col))
        if m > .8:
            c.drawCircle(x, y, r * 4, P(rgba(180, 200, 255, a * .18), blur=4))

# ---------------------------------------------------------------- overlays
@functools.lru_cache(None)
def vignette_img(strength=0.55):
    yy, xx = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32)
    nx = (xx / (W / 4) - .5) * 2; ny = (yy / (H / 4) - .5) * 2
    d = np.sqrt(nx ** 2 * .8 + ny ** 2 * 1.0)
    a = np.clip((d - 0.55) / 0.9, 0, 1) ** 1.6 * strength
    return to_img(np.zeros((H // 4, W // 4, 3), np.float32), alpha=a)

@functools.lru_cache(None)
def grain_imgs(n=6):
    rng = np.random.default_rng(9)
    out = []
    for i in range(n):
        g = rng.normal(0.5, 0.18, (H // 2, W // 2)).astype(np.float32)
        out.append(to_img(np.stack([g, g, g], -1)))
    return out

@functools.lru_cache(None)
def glow_sprite(r=128):
    yy, xx = np.mgrid[0:2 * r, 0:2 * r].astype(np.float32)
    d = np.sqrt((xx - r + .5) ** 2 + (yy - r + .5) ** 2) / r
    a = np.clip(np.exp(-d * d * 4.0) - np.exp(-4.0), 0, 1)
    return to_img(np.ones((2 * r, 2 * r, 3), np.float32), alpha=a)

def glow(c, x, y, radius, color, alpha=1.0, blend=PLUS):
    """Additive soft glow using a cached sprite and tint."""
    if alpha <= 0:
        return
    r = skia.ColorGetR(color) / 255; g = skia.ColorGetG(color) / 255; b = skia.ColorGetB(color) / 255
    img = glow_sprite()
    draw_img(c, img, x - radius, y - radius, radius * 2, radius * 2, alpha, blend, tint_cf(r, g, b))
