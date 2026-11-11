"""Picture assembly: per-beat visuals + camera motion + transitions + captions.

Each beat gets one visual: an image (png/jpg/webp) or a clip (mp4/mov/webm)
named `beat_01.*`, `beat_02.*` ... in the assets folder. Images get a slow
camera move (the references never hold a dead-still frame); clips are fitted,
trimmed, or frozen on their last frame to the beat's exact length.
Missing visuals become labelled placeholder cards, so you can preview timing
before generating any art.
"""
from __future__ import annotations

import math
import subprocess
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from . import config

IMG_EXT = (".png", ".jpg", ".jpeg", ".webp")
VID_EXT = (".mp4", ".mov", ".webm", ".mkv")

# transition name -> (xfade type, duration seconds)
TRANSITIONS = {
    "cut": ("fade", 0.034),
    "whip": ("smoothleft", 0.22),
    "whip_right": ("smoothright", 0.22),
    "whip_up": ("smoothup", 0.22),
    "fade": ("fade", 0.35),
    "flash": ("fadewhite", 0.24),
    "dip": ("fadeblack", 0.45),
    "zoom": ("zoomin", 0.28),
    "glitch": ("pixelize", 0.2),
}

MOTIONS = ("push_in", "pull_out", "pan_left", "pan_right", "pan_up", "pan_down", "shake", "static", "drift")


def find_visual(assets: Path, idx: int) -> Path | None:
    for ext in IMG_EXT + VID_EXT:
        for name in (f"beat_{idx:02d}{ext}", f"beat_{idx}{ext}"):
            p = assets / name
            if p.exists():
                return p
    return None


def placeholder(path: Path, idx: int, beat: dict) -> Path:
    """Labelled card: shows beat number, duration, VO and the visual prompt."""
    W, H = config.WIDTH, config.HEIGHT
    hue = (idx * 47) % 360
    import colorsys
    c1 = tuple(int(v * 255) for v in colorsys.hsv_to_rgb(hue / 360, 0.45, 0.35))
    c2 = tuple(int(v * 255) for v in colorsys.hsv_to_rgb(((hue + 40) % 360) / 360, 0.5, 0.15))
    img = Image.new("RGB", (W, H), c1)
    d = ImageDraw.Draw(img)
    for y in range(H):
        f = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(c1[k] * (1 - f) + c2[k] * f) for k in range(3)))
    fb = ImageFont.truetype(str(config.FONTS / "Inter-Black.otf"), 110)
    fm = ImageFont.truetype(str(config.FONTS / "Inter-ExtraBold.otf"), 44)
    d.text((70, 140), f"BEAT {idx:02d}", font=fb, fill=(255, 255, 255))
    d.text((74, 280), f"{beat['end'] - beat['start']:.2f}s  ·  {beat.get('motion', 'push_in')}  ·  {beat.get('transition', 'cut')}",
           font=fm, fill=(255, 214, 10))
    y = 420
    for line in textwrap.wrap("VISUAL: " + beat.get("visual", ""), 34)[:16]:
        d.text((74, y), line, font=fm, fill=(235, 235, 235))
        y += 58
    img.save(path)
    return path


def _ease(p: str) -> str:
    return f"(({p})*({p})*(3-2*({p})))"


def _zoompan(motion: str, frames: int, intensity: float = 1.0) -> str:
    W, H = config.WIDTH, config.HEIGHT
    N = max(frames - 1, 1)
    p = _ease(f"min(on/{N},1)")
    k = 0.14 * intensity
    cx, cy = "(iw/2-iw/zoom/2)", "(ih/2-ih/zoom/2)"
    if motion == "push_in":
        z, x, y = f"1+{k}*{p}", cx, cy
    elif motion == "pull_out":
        z, x, y = f"1+{k}-{k}*{p}", cx, cy
    elif motion == "pan_left":
        z, x, y = f"{1 + k}", f"(iw-iw/zoom)*(1-{p})", cy
    elif motion == "pan_right":
        z, x, y = f"{1 + k}", f"(iw-iw/zoom)*{p}", cy
    elif motion == "pan_up":
        z, x, y = f"{1 + k}", cx, f"(ih-ih/zoom)*(1-{p})"
    elif motion == "pan_down":
        z, x, y = f"{1 + k}", cx, f"(ih-ih/zoom)*{p}"
    elif motion == "shake":
        amp = 22 * intensity
        z = "1.1"
        x = f"{cx}+{amp}*sin(on*2.3)*exp(-on/9)"
        y = f"{cy}+{amp}*cos(on*1.7)*exp(-on/9)"
    elif motion == "drift":
        z, x, y = f"1.06+0.04*{p}", f"{cx}+40*({p}-0.5)", cy
    else:  # static (still breathes a tiny bit)
        z, x, y = f"1.02+0.015*{p}", cx, cy
    return f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={W}x{H}:fps={config.FPS}"


def render(timeline: dict, assets: Path, ass_path: Path, audio_path: Path, out_path: Path,
           work: Path, preview: bool = False) -> None:
    W, H, FPS = config.WIDTH, config.HEIGHT, config.FPS
    beats = timeline["beats"]
    total = timeline["duration"]
    work.mkdir(parents=True, exist_ok=True)

    inputs, chains = [], []
    clip_spans = []
    for i, b in enumerate(beats):
        t_in = TRANSITIONS.get(b.get("transition", "cut"), TRANSITIONS["cut"])[1] if i > 0 else 0.0
        t_out = TRANSITIONS.get(beats[i + 1].get("transition", "cut"), TRANSITIONS["cut"])[1] if i + 1 < len(beats) else 0.0
        s = max(0.0, b["start"] - t_in / 2)
        e = (beats[i + 1]["start"] + t_out / 2) if i + 1 < len(beats) else total
        clip_spans.append((s, e))
        L = e - s + 0.12          # pad: xfade needs the outgoing clip to outlast the transition;
        frames = max(2, math.ceil(L * FPS))   # the extra frames are discarded by xfade
        vis = find_visual(assets, i + 1) or placeholder(work / f"placeholder_{i + 1:02d}.png", i + 1, b)
        idx = len(inputs) // 2   # ffmpeg input number (inputs holds "-i", path pairs)
        if vis.suffix.lower() in VID_EXT:
            inputs += ["-i", str(vis)]
            chains.append(
                f"[{idx}:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},"
                f"setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration={L:.3f},trim=duration={L:.3f},"
                f"setsar=1,format=yuv420p[v{i}]")
        else:
            inputs += ["-i", str(vis)]
            scale = 1.0 if preview else 1.5   # oversample to keep slow moves smooth
            chains.append(
                f"[{idx}:v]scale={int(W * scale)}:{int(H * scale)}:force_original_aspect_ratio=increase,"
                f"crop={int(W * scale)}:{int(H * scale)},setsar=1,"
                f"{_zoompan(b.get('motion', 'push_in'), frames, b.get('motion_intensity', 1.0))},"
                f"trim=duration={L:.3f},setpts=PTS-STARTPTS,format=yuv420p[v{i}]")

    # chain transitions; each transition is centred on the beat boundary
    last = "v0"
    for i in range(1, len(beats)):
        kind, dur = TRANSITIONS.get(beats[i].get("transition", "cut"), TRANSITIONS["cut"])
        offset = clip_spans[i][0]
        chains.append(f"[{last}][v{i}]xfade=transition={kind}:duration={dur:.3f}:offset={offset:.3f}[x{i}]")
        last = f"x{i}"
    ass = str(ass_path).replace("\\", "/").replace(":", "\\:")
    fonts = str(config.FONTS).replace(":", "\\:")
    chains.append(f"[{last}]ass='{ass}':fontsdir='{fonts}',trim=duration={total:.3f}[vout]")

    aidx = len(inputs) // 2
    cmd = ["ffmpeg", "-nostdin", "-hide_banner", "-y", *inputs, "-i", str(audio_path),
           "-filter_complex", ";".join(chains), "-map", "[vout]", "-map", f"{aidx}:a",
           "-c:v", "libx264", "-preset", "veryfast" if preview else "medium", "-crf", "23" if preview else "18",
           "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
           "-movflags", "+faststart", "-shortest", str(out_path)]
    (work / "ffmpeg_cmd.txt").write_text(" ".join(f"'{c}'" if " " in c or ";" in c else c for c in cmd))
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-4000:])
