"""Audio post: voice chain, SFX placement, music ducking, loudness mastering."""
from __future__ import annotations

import json
import random
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

from . import config, sfx

# Broadcast-style narrator chain (ffmpeg). Kokoro is clean, so this is about
# presence and consistency: trim rumble/mud, lift intelligibility, tame 's',
# then glue with a compressor so every word sits at the same loudness.
VOICE_CHAIN = ",".join([
    "highpass=f=70",
    "equalizer=f=220:t=q:w=1.0:g=-2.0",     # de-mud
    "equalizer=f=3200:t=q:w=1.2:g=2.5",     # presence
    "treble=g=2.0:f=9500",                  # air
    "deesser=i=0.35",
    "acompressor=threshold=-20dB:ratio=3:attack=4:release=90:makeup=2.5:knee=4",
])


def ffmpeg(*args: str) -> str:
    r = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-y", *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-3000:])
    return r.stderr


def process_voice(voice: np.ndarray) -> np.ndarray:
    with tempfile.TemporaryDirectory() as d:
        src, dst = Path(d) / "in.wav", Path(d) / "out.wav"
        sf.write(src, voice, config.SR)
        ffmpeg("-i", str(src), "-af", VOICE_CHAIN, "-ar", str(config.SR), str(dst))
        out, _ = sf.read(dst, dtype="float32")
    return out[: len(voice)] if len(out) >= len(voice) else np.pad(out, (0, len(voice) - len(out)))


def _load_library_sfx(name: str) -> np.ndarray | None:
    """Prefer a user-supplied recording from sfx_library/ if one exists."""
    lib = config.SFX_LIBRARY
    if not lib.exists():
        return None
    cands = sorted(lib.glob(f"{name}.wav")) + sorted(lib.glob(f"{name}_*.wav"))
    if not cands:
        return None
    a, sr = sf.read(random.choice(cands), dtype="float32", always_2d=True)
    if a.shape[1] == 1:
        a = np.repeat(a, 2, 1)
    if sr != config.SR:
        a = resample_poly(a, config.SR, sr, axis=0).astype(np.float32)
    return a / (np.abs(a).max() + 1e-9) * 0.7


def place_sfx(cues: list[dict], total: float, voice_peak: float) -> np.ndarray:
    """cues: [{"name", "time", "gain_db"?, "params"?}] -> stereo SFX bus."""
    bus = np.zeros((int(total * config.SR) + config.SR * 6, 2), np.float32)
    for c in cues:
        name = c["name"]
        clip = _load_library_sfx(name)
        if clip is None:
            clip = sfx.render(name, **c.get("params", {}))
        anchor = sfx.ANCHOR.get(name, "start")
        if anchor == "peak":
            env = np.abs(clip).max(1)
            offset = int(np.argmax(env))
        elif anchor == "end":
            offset = len(clip)
        else:
            offset = 0
        start = int(c["time"] * config.SR) - offset
        if start < 0:
            clip, start = clip[-start:], 0
        g = 10 ** ((c.get("gain_db", sfx.DEFAULT_GAIN_DB.get(name, -14)) + 6) / 20) * voice_peak
        end = min(len(bus), start + len(clip))
        bus[start:end] += clip[: end - start] * g
    return bus[: int(total * config.SR) + config.SR * 2]


def duck_envelope(voice: np.ndarray, depth_db: float, attack: float = 0.04, release: float = 0.35) -> np.ndarray:
    """Sidechain-style gain curve that dips when the narrator talks."""
    hop = 240
    n = len(voice) // hop + 1
    rms = np.array([np.sqrt(np.mean(voice[i * hop:(i + 1) * hop] ** 2) + 1e-12) for i in range(n)])
    active = (20 * np.log10(rms + 1e-9) > 20 * np.log10(rms.max() + 1e-9) - 32).astype(float)
    target = 1 - active * (1 - 10 ** (-depth_db / 20))
    g = np.ones(n)
    a = np.exp(-hop / (attack * config.SR))
    r = np.exp(-hop / (release * config.SR))
    for i in range(1, n):
        coef = a if target[i] < g[i - 1] else r
        g[i] = coef * g[i - 1] + (1 - coef) * target[i]
    return np.repeat(g, hop)[: len(voice)]


def load_music_file(path: str, total: float) -> np.ndarray:
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "m.wav"
        ffmpeg("-i", path, "-ac", "2", "-ar", str(config.SR), "-t", f"{total + 0.5:.3f}", str(out))
        a, _ = sf.read(out, dtype="float32", always_2d=True)
    n = int(total * config.SR)
    if len(a) < n:  # loop to length
        a = np.tile(a, (n // len(a) + 1, 1))
    a = a[:n]
    fo = int(1.5 * config.SR)
    a[-fo:] *= np.linspace(1, 0, fo)[:, None]
    return a


def master(voice: np.ndarray, music: np.ndarray | None, sfx_bus: np.ndarray, out_wav: Path,
           music_db: float = config.MUSIC_DB, duck_db: float = config.DUCK_DB) -> dict:
    total = len(voice)
    v_rms = np.sqrt(np.mean(voice[np.abs(voice) > 0.01] ** 2) + 1e-12)
    mix = np.repeat(voice[:, None], 2, 1).astype(np.float32)
    stems_dir = out_wav.parent / "stems"
    stems_dir.mkdir(exist_ok=True)
    sf.write(stems_dir / "voice.wav", mix, config.SR)
    if music is not None:
        m = music[:total]
        if len(m) < total:
            m = np.vstack([m, np.zeros((total - len(m), 2), np.float32)])
        m_rms = np.sqrt(np.mean(m ** 2) + 1e-12)
        m = m * (v_rms / m_rms) * 10 ** (music_db / 20)
        m = m * duck_envelope(voice, duck_db)[:, None]
        sf.write(stems_dir / "music.wav", m, config.SR)
        mix += m
    s = sfx_bus[:total]
    if len(s) < total:
        s = np.vstack([s, np.zeros((total - len(s), 2), np.float32)])
    sf.write(stems_dir / "sfx.wav", s, config.SR)
    mix += s

    with tempfile.TemporaryDirectory() as d:
        raw = Path(d) / "raw.wav"
        sf.write(raw, mix, config.SR, subtype="FLOAT")
        # pass 1: measure
        log = ffmpeg("-i", str(raw), "-af",
                     f"loudnorm=I={config.TARGET_LUFS}:TP={config.TRUE_PEAK}:LRA=9:print_format=json", "-f", "null", "-")
        js = json.loads(log[log.rfind("{"): log.rfind("}") + 1])
        # pass 2: linear normalisation + true-peak limiter
        ln = (f"loudnorm=I={config.TARGET_LUFS}:TP={config.TRUE_PEAK}:LRA=9:"
              f"measured_I={js['input_i']}:measured_TP={js['input_tp']}:measured_LRA={js['input_lra']}:"
              f"measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
        ffmpeg("-i", str(raw), "-af", f"{ln},alimiter=limit=0.89:level=false,aresample={config.SR}",
               "-c:a", "pcm_s24le", str(out_wav))
    # final check
    log = ffmpeg("-i", str(out_wav), "-af", "ebur128=peak=true", "-f", "null", "-")
    summ = log[log.rfind("Summary:"):]
    def grab(key):
        import re
        mm = re.search(key + r":\s+(-?[\d.]+)", summ)
        return float(mm.group(1)) if mm else None
    return {"integrated_lufs": grab("I"), "true_peak_dbfs": grab("Peak"), "lra": grab("LRA")}
