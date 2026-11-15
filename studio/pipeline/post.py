"""Post-production: join shots, grade, burn captions, mix audio -> phone-ready MP4.

    python post.py edit.json out.mp4

edit.json:
{
  "shots": [ {"file": "renders/s01/s01.mp4", "transition": "fade", "t": 0.4},
             {"file": "renders/s02/s02.mp4", "transition": "whipdown", "t": 0.35} ],
  "grade":    {"bloom": 0.35, "vignette": 0.35, "grain": 6},
  "captions": "captions.json" | [ {"start":0.0,"end":0.3,"text":"He"}, ... ]
              | {"text": "full narration ...", "audio": "vo.wav"}   (auto-timed),
  "audio": [ {"file":"vo.wav","gain":0}, {"file":"music.wav","gain":-14},
             {"file":"rain.wav","gain":-20,"start":0} ]
}

Transitions: fade | whipdown | whipup | whipleft | whipright | cut
(The reference video hides almost every cut inside a camera move: a slow
 dolly that crossfades, or a fast vertical whip-pan with motion blur.)
"""
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
STUDIO = os.path.dirname(HERE)
W, H, FPS = 1080, 1920, 30
FONT = os.path.join(STUDIO, "assets", "fonts", "Montserrat-ExtraBold.ttf")

CAPTION_STYLE = {
    "size": 74,            # px at 1080 wide
    "y": 0.705,            # vertical centre as fraction of height
    "fill": "#FFFFFF",
    "stroke": "#000000",
    "stroke_w": 7,
    "shadow": 0.55,        # soft drop-shadow opacity
    "pop": True,           # 3-frame scale pop when a new word appears
}


def run(cmd):
    print("+", " ".join(cmd[:6]), "...")
    subprocess.run(cmd, check=True)


def duration(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                   "-of", "default=nw=1:nk=1", path])
    return float(out)


# ------------------------------------------------------------------ shots
XFADE = {"fade": "fade", "whipdown": "slidedown", "whipup": "slideup",
         "whipleft": "slideleft", "whipright": "slideright"}


def join_shots(shots, out):
    if len(shots) == 1:
        run(["ffmpeg", "-v", "error", "-y", "-i", shots[0]["file"], "-c", "copy", out])
        return
    inputs, fc, prev, offset = [], [], "[0:v]", 0.0
    for i, s in enumerate(shots):
        inputs += ["-i", s["file"]]
    for i in range(1, len(shots)):
        s = shots[i]
        tr = s.get("transition", "fade")
        t = 0.04 if tr == "cut" else s.get("t", 0.4)
        offset += duration(shots[i - 1]["file"]) - t
        src = f"[{i}:v]"
        if tr.startswith("whip"):  # motion-blur the incoming/outgoing edges
            fc.append(f"{prev}tmix=frames=3[a{i}];{src}tmix=frames=3[b{i}]")
            prev, src = f"[a{i}]", f"[b{i}]"
        name = f"[v{i}]"
        fc.append(f"{prev}{src}xfade=transition={XFADE.get(tr, 'fade')}:duration={t}:offset={offset:.3f}{name}")
        prev = name
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fc),
         "-map", prev, "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", out])


# ------------------------------------------------------------------ grade
def grade_filter(g):
    """Bloom + vignette + light film grain: the 'expensive cartoon film' finish."""
    b = g.get("bloom", 0.35)
    v = g.get("vignette", 0.35)
    n = g.get("grain", 6)
    f = (f"format=gbrp,split[o][g];[g]scale=iw/4:ih/4,gblur=sigma=12,scale={W}:{H},"
         f"colorlevels=rimin=0.55:gimin=0.55:bimin=0.55[gl];"
         f"[o][gl]blend=all_mode=screen:all_opacity={b}")
    if v:
        f += f",vignette=angle={0.35 + v * 0.5:.2f}"
    if n:
        f += f",noise=alls={n}:allf=t"
    return f + ",format=yuv420p"


# ------------------------------------------------------------------ captions
def auto_time(text, total):
    words = text.split()
    weights = [len(w.strip(".,!?;:")) + 2 + (6 if w[-1] in ".!?" else 3 if w[-1] in ",;:" else 0) for w in words]
    scale = total / sum(weights)
    t, out = 0.0, []
    for w, k in zip(words, weights):
        out.append({"start": round(t, 3), "end": round(t + k * scale, 3), "text": w})
        t += k * scale
    return out


def load_captions(c):
    if c is None:
        return []
    if isinstance(c, str):
        return json.load(open(c))
    if isinstance(c, dict):
        return auto_time(c["text"], duration(c["audio"]))
    return c


def render_caption(text, scale=1.0, st=CAPTION_STYLE):
    font = ImageFont.truetype(FONT, int(st["size"] * scale))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    sw = int(st["stroke_w"] * scale)
    bbox = d.textbbox((0, 0), text, font=font, stroke_width=sw)
    x = (W - (bbox[2] - bbox[0])) // 2 - bbox[0]
    y = int(H * st["y"]) - (bbox[3] - bbox[1]) // 2 - bbox[1]
    if st["shadow"]:
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((x + 4, y + 6), text, font=font, fill=(0, 0, 0, int(255 * st["shadow"])),
                                stroke_width=sw, stroke_fill=(0, 0, 0, int(255 * st["shadow"])))
        layer = Image.alpha_composite(layer, sh.filter(ImageFilter.GaussianBlur(6)))
        d = ImageDraw.Draw(layer)
    d.text((x, y), text, font=font, fill=st["fill"], stroke_width=sw, stroke_fill=st["stroke"])
    return layer


def caption_stream(caps, total_frames):
    """Yield one RGBA frame per video frame (cached per word)."""
    blank = Image.new("RGBA", (W, H), (0, 0, 0, 0)).tobytes()
    cache = {}
    for f in range(total_frames):
        t = f / FPS
        cur = next((c for c in caps if c["start"] <= t < c["end"]), None)
        if not cur:
            yield blank
            continue
        age = int((t - cur["start"]) * FPS)
        scale = (1.12, 1.06, 1.0)[min(age, 2)] if CAPTION_STYLE["pop"] else 1.0
        key = (cur["text"], scale)
        if key not in cache:
            cache[key] = render_caption(cur["text"], scale).tobytes()
        yield cache[key]


# ------------------------------------------------------------------ main
def main():
    edit = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    base = os.path.dirname(os.path.abspath(sys.argv[1]))
    for s in edit["shots"]:
        s["file"] = s["file"] if os.path.isabs(s["file"]) else os.path.join(base, s["file"])
    tmp = out + ".joined.mp4"
    join_shots(edit["shots"], tmp)
    total = duration(tmp)
    frames = int(round(total * FPS))
    caps = load_captions(edit.get("captions"))

    audio = edit.get("audio", [])
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", tmp,
           "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
    for a in audio:
        cmd += ["-i", a["file"] if os.path.isabs(a["file"]) else os.path.join(base, a["file"])]
    fc = f"[0:v]{grade_filter(edit.get('grade', {}))}[g];[g][1:v]overlay=format=auto[v]"
    amap = []
    if audio:
        parts = []
        for i, a in enumerate(audio):
            delay = int(a.get("start", 0) * 1000)
            parts.append(f"[{i + 2}:a]adelay={delay}|{delay},volume={a.get('gain', 0)}dB[a{i}]")
        fc += ";" + ";".join(parts) + ";" + "".join(f"[a{i}]" for i in range(len(audio)))
        fc += f"amix=inputs={len(audio)}:normalize=0,alimiter=limit=0.89,loudnorm=I=-14:TP=-1.5[aout]"
        amap = ["-map", "[aout]", "-c:a", "aac", "-b:a", "192k"]
    cmd += ["-filter_complex", fc, "-map", "[v]", *amap, "-t", f"{total:.3f}",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", out]
    print("+ ffmpeg final pass ...")
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fr in caption_stream(caps, frames):
        p.stdin.write(fr)
    p.stdin.close()
    if p.wait() != 0:
        raise SystemExit("ffmpeg failed")
    os.remove(tmp)
    print("wrote", out)


if __name__ == "__main__":
    main()
