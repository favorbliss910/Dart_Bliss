"""Word-level timing for captions and SFX cues.

Uses faster-whisper (word timestamps) on each narrated line, then maps the
recognised words back onto the script's own words, so captions always show
exactly what you wrote. Falls back to a syllable-weighted estimate when
faster-whisper isn't installed.
"""
from __future__ import annotations

import difflib
import re
from functools import lru_cache

import numpy as np
from scipy.signal import resample_poly

from . import config


def script_words(text: str) -> list[str]:
    return [w for w in re.split(r"\s+", text.replace("—", " ").replace("–", " ").strip()) if w]


def _norm(w: str) -> str:
    return re.sub(r"[^a-z0-9]", "", w.lower())


def _syllables(w: str) -> int:
    w = _norm(w)
    if not w:
        return 1
    if w.isdigit():
        return max(2, len(w) * 2)
    return max(1, len(re.findall(r"[aeiouy]+", w)))


@lru_cache(maxsize=1)
def _whisper():
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return None
    try:
        return WhisperModel(config.WHISPER_MODEL, device="cpu", compute_type="int8")
    except Exception as e:  # model download blocked, etc.
        print(f"[align] faster-whisper unavailable ({e}); using estimated timings")
        return None


def estimate(words: list[str], dur: float) -> list[tuple[float, float]]:
    weights = np.array([_syllables(w) + (0.6 if w[-1:] in ",.;:!?" else 0) for w in words], float)
    edges = np.concatenate([[0], np.cumsum(weights)]) / weights.sum() * dur
    return [(edges[i], edges[i + 1]) for i in range(len(words))]


def align(text: str, audio: np.ndarray) -> list[dict]:
    """Return [{"word", "start", "end"}] relative to the start of `audio`."""
    words = script_words(text)
    dur = len(audio) / config.SR
    model = _whisper()
    if model is None or not words:
        return [{"word": w, "start": s, "end": e} for w, (s, e) in zip(words, estimate(words, dur))]

    a16 = resample_poly(audio, 1, config.SR // 16000).astype(np.float32)
    # no initial_prompt: it makes Whisper skip words it believes were already said
    segs, _ = model.transcribe(a16, word_timestamps=True, beam_size=5)
    rec = [(w.word, w.start, w.end) for s in segs for w in (s.words or [])]
    times: list[tuple[float, float] | None] = [None] * len(words)
    sm = difflib.SequenceMatcher(a=[_norm(w) for w in words], b=[_norm(r[0]) for r in rec], autojunk=False)
    for a0, b0, n in sm.get_matching_blocks():
        for k in range(n):
            times[a0 + k] = (rec[b0 + k][1], rec[b0 + k][2])
    est = estimate(words, dur)
    if sum(t is not None for t in times) < 0.6 * len(words):
        print(f"[align] low match ({sum(t is not None for t in times)}/{len(words)}) for: {text[:50]}... using estimate")
        return [{"word": w, "start": s, "end": e} for w, (s, e) in zip(words, est)]
    # fill gaps (numbers read as several words, etc.) by interpolation
    i = 0
    while i < len(words):
        if times[i] is not None:
            i += 1
            continue
        j = i
        while j < len(words) and times[j] is None:
            j += 1
        lo = times[i - 1][1] if i > 0 else 0.0
        hi = times[j][0] if j < len(words) else dur
        span = est[i:j]
        s0, s1 = span[0][0], span[-1][1]
        for k, (s, e) in enumerate(span):
            f0 = (s - s0) / max(s1 - s0, 1e-6)
            f1 = (e - s0) / max(s1 - s0, 1e-6)
            times[i + k] = (lo + f0 * (hi - lo), lo + f1 * (hi - lo))
        i = j
    out, prev = [], 0.0
    for w, (s, e) in zip(words, times):
        s = max(prev, min(s, dur))          # timings must never go backwards
        e = max(s + 0.04, min(e, dur))
        out.append({"word": w, "start": float(s), "end": float(e)})
        prev = s + 0.04
    return out
