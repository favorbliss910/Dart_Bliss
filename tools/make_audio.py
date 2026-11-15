"""Audio for shot P01: Kokoro dialogue + procedural (original) ambience, Foley, FX and sting.

Every sound is generated here from code (no third-party samples), so rights are clear.
Event timing is read from manifests/p01_animation_events.json (exported by the Blender build),
so footsteps land on actual contact frames and the neon buzz follows the actual flicker keys.

Usage:
  python tools/make_audio.py --kokoro-model <kokoro-v1.0.int8.onnx> --kokoro-voices <voices-v1.0.bin>

Outputs (48 kHz, 24-bit WAV): assets/audio/p01/{dialogue,ambience,foley,fx,music,mix}.wav
          manifests/p01_audio_timing.json
"""
import argparse
import json
import os
import subprocess
import tempfile

import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
FPS = 24
DUR = 5.0
N = int(SR * DUR)
rng = np.random.default_rng(11)

ap = argparse.ArgumentParser()
ap.add_argument("--kokoro-model", required=True)
ap.add_argument("--kokoro-voices", required=True)
ap.add_argument("--voice", default="am_michael")
ap.add_argument("--line", default="Last stop tonight... please, still be open.")
ap.add_argument("--line-start", type=float, default=0.45)
ap.add_argument("--speed", type=float, default=1.0)
args = ap.parse_args()

OUT = os.path.join(ROOT, "assets", "audio", "p01")
os.makedirs(OUT, exist_ok=True)
events = json.load(open(os.path.join(ROOT, "manifests", "p01_animation_events.json")))


def t_of(frame):
    return (frame - 1) / FPS


def db(x):
    return 10 ** (x / 20)


def onepole_lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):  # small buffers only
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def fft_filter(x, lo=None, hi=None, tilt_db_per_oct=0.0):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    g = np.ones_like(f)
    if lo:
        g *= 1 / np.sqrt(1 + (lo / np.maximum(f, 1)) ** 4)
    if hi:
        g *= 1 / np.sqrt(1 + (f / hi) ** 4)
    if tilt_db_per_oct:
        g *= (np.maximum(f, 20) / 1000) ** (tilt_db_per_oct / 6.0206)
    return np.fft.irfft(X * g, n=len(x))


def place(buf, clip, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= len(buf):
        return
    clip = clip[: len(buf) - i]
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buf[i : i + len(clip), 0] += clip * gain * l
    buf[i : i + len(clip), 1] += clip * gain * r


# ------------------------------------------------------------------ dialogue (Kokoro)
from kokoro_onnx import Kokoro  # noqa: E402

kok = Kokoro(args.kokoro_model, args.kokoro_voices)
voices = kok.get_voices()
assert args.voice in voices, f"{args.voice} not installed; have {voices}"
samples, ksr = kok.create(args.line, voice=args.voice, speed=args.speed, lang="en-us")
with tempfile.TemporaryDirectory() as td:
    raw = os.path.join(td, "v.wav")
    sf.write(raw, samples, ksr)
    rs = os.path.join(td, "v48.wav")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", raw, "-ar", str(SR), "-ac", "1", rs], check=True)
    voice, _ = sf.read(rs, dtype="float64")
voice_raw_path = os.path.join(OUT, f"line01_{args.voice}.wav")
sf.write(voice_raw_path, voice, SR, subtype="PCM_24")

# measured phrase boundaries from the energy envelope (10 ms hop, -38 dBFS gate, >=120 ms gaps)
hop = SR // 100
env = np.array([np.sqrt(np.mean(voice[i : i + hop] ** 2) + 1e-12) for i in range(0, len(voice), hop)])
active = 20 * np.log10(env + 1e-9) > -38
segments, start, gap = [], None, 0
for i, a in enumerate(active):
    if a and start is None:
        start, gap = i, 0
    elif a:
        gap = 0
    elif start is not None:
        gap += 1
        if gap >= 12:
            segments.append((start, i - gap + 1))
            start = None
if start is not None:
    segments.append((start, len(active)))
segments = [(s / 100, e / 100) for s, e in segments if e - s > 5]
voice_dur = len(voice) / SR

dialogue = np.zeros((N, 2))
place(dialogue, voice * db(-1.0) / (np.max(np.abs(voice)) + 1e-9), args.line_start, gain=db(-3))

# ------------------------------------------------------------------ ambience: rain bed + drips + shop room tone
rain = rng.standard_normal((N, 2))
rain[:, 0] = fft_filter(rain[:, 0], lo=250, hi=9000, tilt_db_per_oct=-2.5)
rain[:, 1] = fft_filter(rain[:, 1], lo=250, hi=9000, tilt_db_per_oct=-2.5)
rain /= np.max(np.abs(rain))
amb = rain * db(-14)
for _ in range(220):  # individual droplet ticks
    t = rng.uniform(0, DUR)
    n = int(SR * rng.uniform(0.004, 0.012))
    tick = rng.standard_normal(n) * np.exp(-np.linspace(0, 8, n))
    tick = fft_filter(tick, lo=1500, hi=7000)
    place(amb, tick / (np.max(np.abs(tick)) + 1e-9), t, gain=db(rng.uniform(-34, -22)), pan=rng.uniform(-0.9, 0.9))
# shop room tone grows as camera approaches the window (camera keys at f1 -> f120)
tt = np.arange(N) / SR
hum = (np.sin(2 * np.pi * 60 * tt) * 0.6 + np.sin(2 * np.pi * 120 * tt) * 0.3) * db(-38)
hum *= np.clip(tt / DUR, 0, 1) ** 1.5
amb[:, 0] += hum * 0.8
amb[:, 1] += hum

# ------------------------------------------------------------------ foley: wet footsteps on contact frames
foley = np.zeros((N, 2))


def footstep(strength=1.0):
    n = int(SR * 0.16)
    x = np.linspace(0, 1, n)
    thud = np.sin(2 * np.pi * 95 * x * 0.16) * np.exp(-x * 30)
    slap = fft_filter(rng.standard_normal(n), lo=900, hi=6000) * np.exp(-x * 22)
    splash = fft_filter(rng.standard_normal(n), lo=2500, hi=11000) * np.exp(-((x - 0.12) ** 2) / 0.004) * 0.6
    s = thud * 0.9 + slap * 0.5 + splash * 0.45
    return s / np.max(np.abs(s)) * strength


contacts = events["footstep_contacts"]
first, last = contacts[0]["frame"], 120
foot_log = []
for c in contacts:
    # walk-in steps are farther from the camera; turn-in-place steps are lighter shuffles
    dist_gain = np.interp(c["frame"], [first, 60, last], [-14, -6, -4])
    shuffle = c["frame"] > 70
    g = db(dist_gain - (5 if shuffle else 0))
    pan = -0.25 if c["foot"] == "L" else -0.1
    place(foley, footstep(), t_of(c["frame"]), gain=g, pan=pan)
    foot_log.append({"frame": c["frame"], "time_s": round(t_of(c["frame"]), 4), "gain_db": round(float(dist_gain - (5 if shuffle else 0)), 1)})

# cloth rustle on the turn (frames 72-88)
n = int(SR * (88 - 72) / FPS)
rustle = fft_filter(rng.standard_normal(n), lo=1200, hi=8000) * np.sin(np.linspace(0, np.pi, n)) ** 2
place(foley, rustle / np.max(np.abs(rustle)), t_of(72), gain=db(-30))

# ------------------------------------------------------------------ fx: neon flicker buzz gated by the actual flicker keys
fx = np.zeros((N, 2))
keys = events["sign_flicker_keys"]
gate = np.zeros(N)
for i, k in enumerate(keys):
    s = int(t_of(k["frame"]) * SR)
    e = int(t_of(keys[i + 1]["frame"]) * SR) if i + 1 < len(keys) else N
    gate[s:e] = min(1.0, k["emission"] / 8.0)
gate = onepole_lp(gate, 60.0)
buzz = sum(np.sign(np.sin(2 * np.pi * 120 * h * tt)) / h for h in (1, 2, 3, 5)) * 0.3
buzz = fft_filter(buzz, lo=150, hi=5000)
fx[:, 0] += buzz * gate * db(-30)
fx[:, 1] += buzz * gate * db(-27)
prev = 0.0
clicks = []
for k in keys:
    if k["emission"] > 2 and prev <= 2:
        n = int(SR * 0.03)
        click = rng.standard_normal(n) * np.exp(-np.linspace(0, 12, n))
        place(fx, click / np.max(np.abs(click)), t_of(k["frame"]), gain=db(-22), pan=0.4)
        clicks.append(k["frame"])
    prev = k["emission"]

# ------------------------------------------------------------------ music: a small hopeful sting when the sign holds (original, synthesized)
music = np.zeros((N, 2))
sting_frame = 92
notes = [(523.25, 0.0), (659.25, 0.09), (783.99, 0.18), (1046.5, 0.30)]  # C major arpeggio
for f0, dt in notes:
    n = int(SR * 1.6)
    x = np.arange(n) / SR
    tone = (np.sin(2 * np.pi * f0 * x) + 0.35 * np.sin(2 * np.pi * 2 * f0 * x) + 0.12 * np.sin(2 * np.pi * 3.01 * f0 * x)) * np.exp(-x * 2.6)
    tone *= np.minimum(1, x / 0.004)
    place(music, tone, t_of(sting_frame) + dt, gain=db(-24), pan=0.15)

# ------------------------------------------------------------------ mix with dialogue ducking
duck = np.ones(N)
vs, ve = args.line_start, args.line_start + voice_dur
duck[int(vs * SR) : int(min(ve, DUR) * SR)] = db(-6)
duck = onepole_lp(duck, 8.0)
stems = {"dialogue": dialogue, "ambience": amb * duck[:, None], "foley": foley, "fx": fx, "music": music}
mix = sum(stems.values())
fade = np.minimum(1, np.arange(N) / (0.15 * SR))[:, None] * np.minimum(1, (N - np.arange(N)) / (0.2 * SR))[:, None]
mix *= fade
for name, s in stems.items():
    sf.write(os.path.join(OUT, f"{name}.wav"), s, SR, subtype="PCM_24")
pre = os.path.join(OUT, "mix_prenorm.wav")
sf.write(pre, mix / max(1.0, np.max(np.abs(mix))), SR, subtype="PCM_24")

# loudness: measure with ffmpeg ebur128, gain to -16 LUFS (short-form, headroom for platform norm), true-peak check
def measure(path):
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True)
    tail = p.stderr[p.stderr.rfind("Summary:"):]
    lufs = float(tail.split("I:")[1].split("LUFS")[0])
    tp = float(tail.split("Peak:")[1].split("dBFS")[0])
    return lufs, tp


lufs0, tp0 = measure(pre)
target = -16.0
g = target - lufs0
if tp0 + g > -1.0:
    g = -1.0 - tp0
final = mix / max(1.0, np.max(np.abs(mix))) * db(g)
mix_path = os.path.join(OUT, "mix.wav")
sf.write(mix_path, final, SR, subtype="PCM_24")
os.remove(pre)
lufs1, tp1 = measure(mix_path)

timing = {
    "shot_id": "P01",
    "sample_rate": SR,
    "duration_s": DUR,
    "dialogue": [{
        "id": "line01", "voice": args.voice, "engine": "kokoro-onnx (Kokoro-82M v1.0, int8 ONNX)",
        "text": args.line, "speed": args.speed, "start_s": args.line_start,
        "measured_duration_s": round(voice_dur, 3), "end_s": round(args.line_start + voice_dur, 3),
        "file": os.path.relpath(voice_raw_path, ROOT),
        "measured_phrases_s": [{"start": round(args.line_start + s, 2), "end": round(args.line_start + e, 2)} for s, e in segments],
    }],
    "footsteps": foot_log,
    "neon_click_frames": clicks,
    "music_sting_frame": sting_frame,
    "loudness": {"prenorm_lufs_i": lufs0, "prenorm_true_peak_dbfs": tp0, "final_lufs_i": lufs1, "final_true_peak_dbfs": tp1, "target_lufs_i": target},
    "stems": [os.path.relpath(os.path.join(OUT, f"{k}.wav"), ROOT) for k in stems] + [os.path.relpath(mix_path, ROOT)],
}
json.dump(timing, open(os.path.join(ROOT, "manifests", "p01_audio_timing.json"), "w"), indent=2)
print(json.dumps(timing, indent=2))
