"""Stage 2 for P02: synthesise the narration with Kokoro and derive every shot's length from it.

Usage: python tools/p02/vo.py [--voice am_michael] [--speed 1.0]
Writes assets/audio/p02/<shot>_line.wav (48 kHz mono) and manifests/p02_audio_timing.json.
"""
import argparse
import json
import math
import os
import subprocess
import sys
import tempfile

import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from script import SHOTS, SPOKEN  # noqa: E402

SR, FPS = 48000, 24
PRE_ROLL, HOLD = 0.45, 1.0
GAP, GAP_ELLIPSIS = 0.30, 0.60

ap = argparse.ArgumentParser()
ap.add_argument("--voice", default="am_michael")
ap.add_argument("--speed", type=float, default=1.0)
args = ap.parse_args()

from kokoro_onnx import Kokoro  # noqa: E402

kok = Kokoro(os.path.join(ROOT, ".models/kokoro-v1.0.int8.onnx"), os.path.join(ROOT, ".models/voices-v1.0.bin"))
assert args.voice in kok.get_voices()
OUT = os.path.join(ROOT, "assets", "audio", "p02")
os.makedirs(OUT, exist_ok=True)


def synth(text):
    s, ksr = kok.create(SPOKEN.get(text, text), voice=args.voice, speed=args.speed, lang="en-us")
    with tempfile.TemporaryDirectory() as td:
        a, b = os.path.join(td, "a.wav"), os.path.join(td, "b.wav")
        sf.write(a, s, ksr)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", a, "-ar", str(SR), "-ac", "1", b], check=True)
        v, _ = sf.read(b, dtype="float64")
    # trim leading/trailing silence with the -38 dBFS gate (10 ms hop)
    hop = SR // 100
    env = np.array([np.sqrt(np.mean(v[i:i + hop] ** 2) + 1e-12) for i in range(0, len(v), hop)])
    on = np.where(20 * np.log10(env + 1e-9) > -38)[0]
    s0, s1 = max(0, on[0] - 2) * hop, min(len(v), (on[-1] + 4) * hop)
    return v[s0:s1]


timing = {"project": "P02", "fps": FPS, "voice": args.voice, "speed": args.speed,
          "engine": "kokoro-onnx 0.6.1 (Kokoro-82M v1.0 int8)", "pre_roll_s": PRE_ROLL, "hold_s": HOLD, "shots": []}
t_film = 0.0
for sid, sentences in SHOTS:
    clips, phrases, t = [], [], 0.0
    for i, text in enumerate(sentences):
        v = synth(text)
        phrases.append({"text": text, "start_s": round(PRE_ROLL + t, 3), "end_s": round(PRE_ROLL + t + len(v) / SR, 3)})
        clips.append(v)
        t += len(v) / SR
        if i < len(sentences) - 1:
            gap = GAP_ELLIPSIS if text.endswith("...") else GAP
            clips.append(np.zeros(int(gap * SR)))
            t += gap
    line = np.concatenate(clips)
    line = line / (np.max(np.abs(line)) + 1e-9) * 10 ** (-1 / 20)  # peak -1 dBFS
    path = os.path.join(OUT, f"{sid}_line.wav")
    sf.write(path, line, SR, subtype="PCM_24")
    dur = len(line) / SR
    frames = math.ceil((PRE_ROLL + dur + HOLD) * FPS)
    frames = max(frames, 4 * FPS)
    timing["shots"].append({"id": sid, "frames": frames, "duration_s": round(frames / FPS, 3),
                            "line_file": os.path.relpath(path, ROOT), "line_start_s": PRE_ROLL,
                            "line_end_s": round(PRE_ROLL + dur, 3), "film_start_s": round(t_film, 3),
                            "phrases": phrases, "timing_source": "measured_energy_envelope"})
    t_film += frames / FPS
    print(f"{sid}: line {dur:5.2f}s -> {frames} frames ({frames / FPS:.2f}s)", flush=True)
timing["total_frames"] = sum(s["frames"] for s in timing["shots"])
timing["total_s"] = round(timing["total_frames"] / FPS, 2)
json.dump(timing, open(os.path.join(ROOT, "manifests", "p02_audio_timing.json"), "w"), indent=2)
print("total", timing["total_frames"], "frames", timing["total_s"], "s")
