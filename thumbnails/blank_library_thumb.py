"""Thumbnail + matching first frame for "The Blank Library".

One subject (the reader) in extreme close-up with a shocked face, lit from below by the
glowing book (the object of curiosity); the threat (the silent librarian) looms right
behind. Warm vs cold complementary light. No text in the image.

    python3 thumbnails/blank_library_thumb.py  ->  thumbnails/out/*.png
"""
import math
import os
import random
import sys

import cairo
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'library'))
sys.path.insert(0, os.path.join(HERE, '..', 'drongo'))
from people import person, librarian, book_open  # noqa: E402
from chars import C, INK, src, ellipse, soft_ellipse, stick  # noqa: E402
import scenes  # noqa: E402

OUT = os.path.join(HERE, 'out')
WARM = C('#ffcf6e')
COLD = C('#7fb6ff')


def surf(w, h):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    return s, cairo.Context(s)


def to_img(s):
    s.flush()
    w, h = s.get_width(), s.get_height()
    a = np.ndarray((h, w, 4), np.uint8, s.get_data())
    return Image.fromarray(a[..., [2, 1, 0, 3]].copy(), 'RGBA')


def layer_bg(w, h, k):
    """Dark library behind everything (blurred later)."""
    s, c = surf(w, h)
    g = cairo.LinearGradient(0, 0, 0, h)
    g.add_color_stop_rgb(0, *C('#0d0a12'))
    g.add_color_stop_rgb(1, *C('#2a1a12'))
    c.rectangle(0, 0, w, h)
    c.set_source(g)
    c.fill()
    c.save()
    c.scale(k, k)
    for i in range(-1, int(w / k / 260) + 2):
        scenes.bookshelf(c, i * 260 - 40, h / k + 40, 250, h / k * 1.1, seed=70 + i, lit=0.3)
    c.restore()
    # cold moonlight wash from upper right, warm lamp pool lower left
    soft_ellipse(c, w * 0.85, h * 0.15, w * 0.7, h * 0.4, COLD, 0.22)
    soft_ellipse(c, w * 0.2, h * 0.75, w * 0.6, h * 0.35, WARM, 0.12)
    c.rectangle(0, 0, w, h)
    src(c, (0.03, 0.04, 0.10, 0.45))
    c.fill()
    return s


def layer_librarian(w, h, x, y, sc, flip=False):
    s, c = surf(w, h)
    # cold rim halo so the dark silhouette separates from the dark background
    soft_ellipse(c, x, y - sc * 330, sc * 170, sc * 200, COLD, 0.35)
    librarian(c, x, y, sc, arms='whisper', lean=-0.38 if not flip else 0.38, tilt=-0.22 if not flip else 0.22,
              look=(0, 0), lid=0.2, flip=flip)  # eye contact with the viewer
    return s


def layer_reader(w, h, x, y, sc, tilt=0.06):
    s, c = surf(w, h)
    person(c, x, y, sc, body=C('#c0623c'), hair='short', hair_col=C('#4a3426'), eyes='huge', mouth='scream',
           brows='shock', arms='cheeks', underlight=WARM, sweat=2, tilt=tilt, shadow=False)
    return s


def layer_rays(w, h, x, y, sc, rot=0):
    s, c = surf(w, h)
    for i in range(9):
        a = -math.pi / 2 + (i - 3) * 0.16
        c.move_to(x, y - 40 * sc)
        c.line_to(x + math.cos(a - 0.05) * 1400, y + math.sin(a - 0.05) * 1400)
        c.line_to(x + math.cos(a + 0.05) * 1400, y + math.sin(a + 0.05) * 1400)
        c.close_path()
        g = cairo.LinearGradient(x, y, x, y - 1200)
        g.add_color_stop_rgba(0, *WARM, 0.30)
        g.add_color_stop_rgba(1, *WARM, 0)
        c.set_source(g)
        c.fill()
    return s


def layer_book(w, h, x, y, sc, rot=-0.06):
    s, c = surf(w, h)
    soft_ellipse(c, x, y - 60 * sc, 340 * sc, 200 * sc, WARM, 0.45)
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    book_open(c, 0, 0, sc, text=1.0, glow=1.0, seed=11, ink=C('#b8860b'),
              drawing=lambda cc: (stick(cc, [(90, 30), (90, -10), (130, -40), (170, -10), (170, 30), (90, 30)], 3, C('#8a5a10'))))
    c.restore()
    # motes
    rnd = random.Random(4)
    for i in range(46):
        mx = x + rnd.uniform(-420, 420) * sc / 2
        my = y - rnd.uniform(60, 900) * sc / 2
        soft_ellipse(c, mx, my, rnd.uniform(3, 9), rnd.uniform(3, 9), C('#ffe9a8'), rnd.uniform(0.4, 0.9))
    return s


def finish(img, vignette=0.55):
    w, h = img.size
    a = np.asarray(img.convert('RGB')).astype(np.float32)
    yy, xx = np.mgrid[0:h, 0:w]
    d = ((xx - w * 0.5) / (w * 0.62)) ** 2 + ((yy - h * 0.45) / (h * 0.62)) ** 2
    a *= (1 - vignette * np.clip(d - 0.25, 0, 1))[..., None]
    a += np.random.default_rng(1).normal(0, 2.5, a.shape)  # fine grain
    out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    out = ImageEnhance.Contrast(out).enhance(1.08)
    out = ImageEnhance.Color(out).enhance(1.15)
    return out


def compose(w, h, spec):
    bg = to_img(layer_bg(w, h, spec['shelf_k'])).filter(ImageFilter.GaussianBlur(spec['bg_blur']))
    lib = to_img(layer_librarian(w, h, *spec['lib'])).filter(ImageFilter.GaussianBlur(spec['lib_blur']))
    rdr = to_img(layer_reader(w, h, *spec['reader']))
    bk = to_img(layer_book(w, h, *spec['book']))
    rays = to_img(layer_rays(w, h, *spec['book'][:3])).filter(ImageFilter.GaussianBlur(6))
    img = bg
    for L in (rays, lib, rdr, bk):
        img = Image.alpha_composite(img, L)
    return finish(img)


SPECS = {
    # 9:16 Shorts/TikTok: face centred in the upper-middle, clear of the bottom 25% UI and right-side icons
    'blank_library_thumb_9x16': (1080, 1920, dict(shelf_k=2.2, bg_blur=14, lib_blur=2.5,
                                                    lib=(880, 1190, 2.9), reader=(480, 2150, 5.6, 0.05),
                                                    book=(500, 1360, 1.55, -0.05))),
    # 16:9 YouTube browse: face left third, librarian right third, timestamp corner (bottom-right) kept empty
    'blank_library_thumb_16x9': (1920, 1080, dict(shelf_k=1.7, bg_blur=12, lib_blur=2.0,
                                                    lib=(1360, 1120, 2.5), reader=(700, 1500, 4.6, 0.07),
                                                    book=(690, 985, 1.2, -0.04))),
}

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for name, (w, h, spec) in SPECS.items():
        img = compose(w, h, spec)
        img.save(os.path.join(OUT, name + '.png'))
        if w > h:
            img.resize((1280, 720), Image.LANCZOS).save(os.path.join(OUT, name.replace('16x9', '16x9_1280') + '.jpg'),
                                                       quality=95)
        # glance test: what the feed shows (~ 1/6 size)
        img.resize((w // 6, h // 6), Image.LANCZOS).save(os.path.join(OUT, name + '_glance.png'))
        print('->', name)
