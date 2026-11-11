"""Kokoro text-to-speech with the am_michael voice (cached per line).

Voice strings:
  "am_michael"                      - the house narrator
  "am_michael:0.8,am_onyx:0.2"      - blend styles (slightly deeper Michael)
"""
from __future__ import annotations

import hashlib
import re
from functools import lru_cache
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

from . import config

_CACHE = config.OUTPUT / "_tts_cache"


@lru_cache(maxsize=1)
def _engine():
    from kokoro_onnx import Kokoro
    if not config.KOKORO_MODEL.exists() or not config.KOKORO_VOICES.exists():
        raise FileNotFoundError(
            f"Kokoro model not found ({config.KOKORO_MODEL}, {config.KOKORO_VOICES}). "
            "Run scripts/setup.sh first.")
    return Kokoro(str(config.KOKORO_MODEL), str(config.KOKORO_VOICES))


def _voice(spec: str):
    if ":" not in spec:
        return spec
    k = _engine()
    total, acc = 0.0, None
    for part in spec.split(","):
        name, w = part.split(":")
        style = k.get_voice_style(name.strip()) * float(w)
        acc = style if acc is None else acc + style
        total += float(w)
    return (acc / total).astype(np.float32)


_ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
_TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def _n2w(n: int) -> str:
    if n < 20:
        return _ONES[n]
    t, o = divmod(n, 10)
    return _TENS[t] + ("" if o == 0 else "-" + _ONES[o])


def _clock(m: re.Match) -> str:
    h, mm = int(m.group(1)), int(m.group(2))
    if mm == 0:
        return f"{_n2w(h)} o'clock"
    return f"{_n2w(h)} {'oh-' + _ONES[mm] if mm < 10 else _n2w(mm)}"


def clean_for_speech(text: str) -> str:
    """Small fixes that make Kokoro read narration naturally."""
    t = text.replace("—", ", ").replace("–", ", ").replace("…", "...")
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"(\d),(\d{3})", r"\1\2", t)   # 1,000 -> 1000 (reads as 'one thousand')
    t = re.sub(r"\b(\d{1,2}):(\d{2})\b", _clock, t)  # 8:14 -> eight fourteen
    return t


def synth(text: str, voice: str = config.DEFAULT_VOICE, speed: float = config.DEFAULT_SPEED) -> np.ndarray:
    """Return mono float32 audio at config.SR for one line of narration."""
    text = clean_for_speech(text)
    key = hashlib.sha1(f"{voice}|{speed:.3f}|{text}|{config.KOKORO_MODEL.name}".encode()).hexdigest()[:16]
    _CACHE.mkdir(parents=True, exist_ok=True)
    path = _CACHE / f"{key}.wav"
    if path.exists():
        a, _ = sf.read(path, dtype="float32")
        return a
    audio, sr = _engine().create(text, voice=_voice(voice), speed=speed, lang="en-us")
    audio = resample_poly(audio, config.SR, sr).astype(np.float32)
    audio = _trim(audio)
    sf.write(path, audio, config.SR)
    return audio


def _trim(a: np.ndarray, thresh_db: float = -50, pad_s: float = 0.02) -> np.ndarray:
    """Trim leading/trailing silence (keeps a tiny pad so plosives aren't clipped)."""
    env = np.abs(a)
    thr = 10 ** (thresh_db / 20) * env.max()
    idx = np.where(env > thr)[0]
    if len(idx) == 0:
        return a
    pad = int(pad_s * config.SR)
    return a[max(0, idx[0] - pad): idx[-1] + pad]


def save(path: Path, audio: np.ndarray) -> None:
    sf.write(path, audio, config.SR)
