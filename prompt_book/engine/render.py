# Timeline assembly, transitions, post-processing, frame rendering, encoding.
import sys, os, math, subprocess, time
import numpy as np
import skia
from core import *
from assets import *
import glob, importlib
sys.path.insert(0, PROJECT)
SHOTS, _ends = [], []
for _f in sorted(glob.glob(os.path.join(PROJECT, 'scenes*.py'))):
    _m = importlib.import_module(os.path.splitext(os.path.basename(_f))[0])
    for _k, _v in vars(_m).items():
        if _k.startswith('SHOTS') and isinstance(_v, list):
            SHOTS += _v
    if hasattr(_m, 'END_T'):
        _ends.append(_m.END_T)
SHOTS.sort(key=lambda s: s[0])
END_T = max(_ends) if _ends else SHOTS[-1][0] + 8

_surfs = {}
def surf(key):
    if key not in _surfs:
        _surfs[key] = skia.Surface(W, H)
    return _surfs[key]

def shot_index(t):
    i = 0
    for k, s in enumerate(SHOTS):
        if s[0] <= t:
            i = k
    return i

def render_shot(c, k, t):
    c.save()
    try:
        SHOTS[k][1](c, t)
    finally:
        c.restore()

def post(c, t):
    draw_img(c, vignette_img(), 0, 0, W, H, 1.0)
    g = grain_imgs()[int(t * 24) % 6]
    p = skia.Paint(); p.setAlphaf(.045); p.setBlendMode(skia.BlendMode.kOverlay)
    c.drawImageRect(g, skia.Rect(0, 0, W, H), LIN, p)
    # global fade in/out
    if t < 0.0:
        c.drawPaint(P(rgba(0, 0, 0, 1)))
    if t > END_T - 1.6:
        c.drawPaint(P(rgba(0, 0, 0, e_io(prog(t, END_T - 1.6, END_T)))))

def render_frame(t):
    s = surf('main'); c = s.getCanvas()
    c.clear(skia.ColorBLACK)
    k = shot_index(t)
    start, fn, (ttype, tdur) = SHOTS[k]
    lt = t - start
    if k > 0 and ttype != 'cut' and lt < tdur:
        x = lt / tdur
        if ttype == 'fade':
            render_shot(c, k - 1, t)
            s2 = surf('b'); c2 = s2.getCanvas(); c2.clear(skia.ColorBLACK)
            render_shot(c2, k, t)
            p = skia.Paint(); p.setAlphaf(e_sine(x))
            c.drawImage(s2.makeImageSnapshot(), 0, 0, LIN, p)
        elif ttype == 'black':
            if x < .5:
                render_shot(c, k - 1, t)
                c.drawPaint(P(rgba(0, 0, 0, e_io(x * 2))))
            else:
                render_shot(c, k, t)
                c.drawPaint(P(rgba(0, 0, 0, 1 - e_io((x - .5) * 2))))
        elif ttype == 'flash':
            render_shot(c, k, t)
            c.drawPaint(P(hexc('#FFF1D6', (1 - e_out(x)) * .85)))
        elif ttype == 'whip':
            s2 = surf('b'); c2 = s2.getCanvas(); c2.clear(skia.ColorBLACK)
            if x < .5:
                render_shot(c2, k - 1, t); off = -e_in(x * 2) * W * .6
            else:
                render_shot(c2, k, t); off = (1 - e_out((x - .5) * 2)) * W * .6
            img = s2.makeImageSnapshot()
            blur = math.sin(math.pi * x)
            for j in range(7):
                p = skia.Paint(); p.setAlphaf(1 / (j + 1) if j else 1.0)
                c.drawImage(img, off - j * 40 * blur, 0, LIN, p) if j == 0 else c.drawImage(img, off - (j - 3) * 45 * blur, 0, LIN, p)
        else:
            render_shot(c, k, t)
    else:
        render_shot(c, k, t)
    post(c, t)
    return s

def frame_bytes(t):
    s = render_frame(t)
    return s.toarray()  # native BGRA

def still(t, path, scale=1.0):
    s = render_frame(t)
    img = s.makeImageSnapshot()
    if scale != 1.0:
        img = img.resize(int(W * scale), int(H * scale), skia.SamplingOptions(skia.FilterMode.kLinear))
    img.save(path, skia.kPNG)

def contact(times, path, cols=4, sc=.25):
    from PIL import Image
    tiles = []
    for t in times:
        s = render_frame(t)
        a = s.toarray(colorType=skia.kRGBA_8888_ColorType)
        im = Image.fromarray(a[..., :3]).resize((int(W * sc), int(H * sc)), Image.BILINEAR)
        from PIL import ImageDraw
        ImageDraw.Draw(im).text((6, 4), f'{t:.1f}', fill=(255, 255, 0))
        tiles.append(im)
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * int(W * sc), rows * int(H * sc)))
    for i, im in enumerate(tiles):
        sheet.paste(im, ((i % cols) * int(W * sc), (i // cols) * int(H * sc)))
    sheet.save(path)

def encode_segment(f0, f1, out, fps=FPS, crf=18, preset='faster'):
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', str(fps), '-i', '-',
           '-c:v', 'libx264', '-preset', preset, '-crf', str(crf), '-pix_fmt', 'yuv420p', '-threads', '2', '-tune', 'animation', out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    for f in range(f0, f1):
        t = f / fps
        p.stdin.write(frame_bytes(t).tobytes())
        if (f - f0) % 600 == 0:
            el = time.time() - t0
            print(f'[{out}] frame {f - f0}/{f1 - f0} {el:.0f}s', flush=True)
    p.stdin.close(); p.wait()

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'contact':
        a, b, step = float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
        times = list(np.arange(a, b, step))
        contact(times, sys.argv[5], cols=int(sys.argv[6]) if len(sys.argv) > 6 else 4)
    elif cmd == 'still':
        still(float(sys.argv[2]), sys.argv[3])
    elif cmd == 'seg':
        encode_segment(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], fps=int(sys.argv[5]) if len(sys.argv) > 5 else FPS)
    elif cmd == 'bench':
        ts = [float(x) for x in sys.argv[2:]]
        for t in ts:
            t0 = time.time(); frame_bytes(t); print(t, f'{(time.time() - t0) * 1000:.0f} ms')
