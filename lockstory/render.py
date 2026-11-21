"""Stage A: render the drongo story video (silent) at 2K 60fps, captions burned in.
  python3 render.py sheet           -> contact sheet of every shot (preview)
  python3 render.py still <t>       -> one frame
  python3 render.py video [W H FPS] -> silent mp4 (then mix.py adds sound)"""
import math, subprocess, sys
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFont
import os, importlib
story = importlib.import_module(os.environ.get('STORY', 'story'))
SHOTS, WORDS, DW, DH, DURATION = story.SHOTS, story.WORDS, story.DW, story.DH, story.DURATION
from story import ss
from toon import FONT

SHAKES = []        # (time, amplitude px) camera impacts, filled from sound cue list
try:
    SHAKES = importlib.import_module(os.environ.get('CUES', 'cues')).SHAKES
except Exception:
    pass


def draw_caption(frame, t):
    cur = [x for x in WORDS if x[1] - 0.02 <= t < x[2] + 0.03]
    if not cur: return
    w, t0, t1, _ = cur[0]
    pop = ss((t - t0) / 0.07)
    sc = 0.6 + 0.4 * pop + 0.12 * math.sin(min(1, (t - t0) / 0.18) * math.pi)
    txt = w.strip(".,?!\"")
    txt = txt.upper() if len(txt) <= 3 and txt.lower() in ("a", "i") else txt
    f = ImageFont.truetype(FONT, int(160 * sc))
    g = ImageDraw.Draw(frame)
    bb = g.textbbox((0, 0), txt, font=f, stroke_width=16)
    x = (DW - (bb[2] - bb[0])) / 2 - bb[0]
    y = 1800 - (bb[3] - bb[1]) / 2 - bb[1]
    g.text((x + 6, y + 10), txt, font=f, fill=(0, 0, 0, 150), stroke_width=16, stroke_fill=(0, 0, 0, 150))
    g.text((x, y), txt, font=f, fill=(255, 255, 255), stroke_width=16, stroke_fill=(20, 16, 28))


def frame_at(t, caption=True):
    k = story.shot_at(t)
    t0, fn, cam = SHOTS[k]
    t_end = SHOTS[k + 1][0] if k + 1 < len(SHOTS) else DURATION
    cv = Image.new("RGBA", (DW, DH), (0, 0, 0, 255))
    fn(cv, t, t - t0)
    z0, z1, fx, fy = cam
    q = min(1.0, max(0.0, (t - t0) / max(0.1, t_end - t0)))
    p = ss(q) * 0.6 + 0.4 * q
    z = max(1.0, z0 + (z1 - z0) * p)
    sh = 0.0
    for ts, amp in SHAKES:
        if ts <= t < ts + 0.45:
            sh += amp * math.exp(-(t - ts) * 9) * math.sin((t - ts) * 62)
    cw, ch = DW / z, DH / z
    F = (fx * DW + math.sin(t * 0.8) * 7 + sh, fy * DH + math.cos(t * 0.65) * 7 + sh * 0.6)
    left = F[0] - fx * cw; top = F[1] - fy * ch
    left = min(max(left, 0), DW - cw); top = min(max(top, 0), DH - ch)
    cv = cv.resize((DW, DH), Image.BICUBIC, box=(left, top, left + cw, top + ch))
    # tiny flash on cuts
    dt = t - t0
    if dt < 0.07 and k > 0:
        ov = Image.new("RGBA", (DW, DH), (255, 255, 255, int(70 * (1 - dt / 0.07))))
        cv.alpha_composite(ov)
    if caption: draw_caption(cv, t)
    return cv.convert("RGB")


def _job(a):
    i, fps, W, H = a
    im = frame_at(i / fps)
    if (W, H) != (DW, DH): im = im.resize((W, H), Image.LANCZOS)
    return im.tobytes()


if __name__ == "__main__":
    m = sys.argv[1]
    if m == "still":
        t = float(sys.argv[2]); frame_at(t).resize((540, 960), Image.LANCZOS).save(sys.argv[3] if len(sys.argv) > 3 else "still.png")
    elif m == "sheet":
        idx = [int(x) for x in sys.argv[2:]] or range(len(SHOTS))
        tiles = []
        for k in idx:
            t0 = SHOTS[k][0]; t_end = SHOTS[k + 1][0] if k + 1 < len(SHOTS) else DURATION
            tm = t0 + (t_end - t0) * 0.55
            im = frame_at(tm).resize((270, 480), Image.LANCZOS)
            ImageDraw.Draw(im).text((8, 8), f"{k + 1} {tm:.1f}s", fill=(255, 255, 0), font=ImageFont.truetype(FONT, 26))
            tiles.append(im)
        cols = 8
        rows = math.ceil(len(tiles) / cols)
        sheet = Image.new("RGB", (cols * 270, rows * 480))
        for i, im in enumerate(tiles): sheet.paste(im, ((i % cols) * 270, (i // cols) * 480))
        sheet.save("sheet_all.png" if not sys.argv[2:] else "sheet_part.png"); print(len(tiles), "shots")
    else:
        W, H, fps = (int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (DW, DH, 60)
        out = sys.argv[5] if len(sys.argv) > 5 else "drongo_silent.mp4"
        n = int(DURATION * fps)
        ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps),
                               "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p", out],
                              stdin=subprocess.PIPE)
        with Pool(4) as p:
            for k, b in enumerate(p.imap(_job, [(i, fps, W, H) for i in range(n)], chunksize=4)):
                ff.stdin.write(b)
                if k % 300 == 0: print(f"{k}/{n}", flush=True)
        ff.stdin.close(); ff.wait(); print("done", out)
