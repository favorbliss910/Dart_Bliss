"""Procedural background-music beds.

The reference Shorts all sit a soft, sustained music bed 10-15 dB under the
voice (a constant tonal pad is visible in every spectrogram). This module
writes original beds in that role, one per mood, so a video never ships
silent underneath. For channel-defining music, put a licensed track in the
spec (`"music_file": "path.mp3"`) and the mixer uses it instead.

Each bed supports two story-driven events from the spec:
  * "drop"  - music cuts out for a beat right before a reveal, then returns
  * "lift"  - music gains an extra layer (arp / pulse) from this point on
"""
from __future__ import annotations

import numpy as np
from scipy import signal

from .sfx import SR, _lp, _hp, _norm, _width, reverb

_rng = np.random.default_rng(7)

NOTE = {n: i for i, n in enumerate("C C# D D# E F F# G G# A A# B".split())}


def _hz(name: str, octave: int) -> float:
    return 440.0 * 2 ** ((NOTE[name] + 12 * (octave + 1) - 69) / 12)


def _chord(root: str, quality: str, octave: int = 3) -> list[float]:
    iv = {"min": [0, 3, 7, 10], "maj": [0, 4, 7, 11], "sus": [0, 5, 7, 10],
          "dim": [0, 3, 6, 9], "min9": [0, 3, 7, 14], "maj9": [0, 4, 7, 14], "pow": [0, 7, 12]}[quality]
    base = _hz(root, octave)
    return [base * 2 ** (i / 12) for i in iv]


MOODS = {
    # Mysteries, secrets, "nobody knows why" (v3 button town, v6 well)
    "mystery": dict(bpm=78, prog=[("D", "min9"), ("A#", "maj9"), ("G", "min"), ("A", "sus")],
                    pad_cut=1400, pluck=True, pluck_oct=5, pluck_density=0.35, pulse=False, tick=True, bright=0.6),
    # Curious explainers, clever-trick stories (v5 mirror, v7 coaster, v8 railroad)
    "curious": dict(bpm=96, prog=[("C", "maj9"), ("A", "min"), ("F", "maj9"), ("G", "sus")],
                    pad_cut=2200, pluck=True, pluck_oct=5, pluck_density=0.6, pulse=False, tick=False, bright=1.0),
    # Danger, chases, countdowns (v1 zombies)
    "tension": dict(bpm=104, prog=[("E", "min"), ("C", "maj"), ("E", "min"), ("D#", "dim")],
                    pad_cut=900, pluck=False, pulse=True, tick=False, bright=0.5),
    # Chaos comedy (v4 grandma's recipe)
    "comedy": dict(bpm=122, prog=[("F", "maj"), ("D", "min"), ("A#", "maj"), ("C", "maj")],
                   pad_cut=2600, pluck=True, pluck_oct=4, pluck_density=0.9, pulse=False, tick=False, bright=1.2, bounce=True),
    # Philosophy, leadership, life lessons (v9 Alexander)
    "reflective": dict(bpm=70, prog=[("E", "min9"), ("C", "maj9"), ("G", "maj"), ("D", "sus")],
                       pad_cut=1800, pluck=True, pluck_oct=4, pluck_density=0.4, pulse=False, tick=False, bright=0.8),
    # Big historical / economic stakes (v2 chickens)
    "epic": dict(bpm=84, prog=[("A", "min"), ("F", "maj"), ("C", "maj"), ("G", "maj")],
                 pad_cut=1600, pluck=False, pulse=True, tick=False, bright=0.9, drums=True),
}


def _pad(freqs, dur, cutoff):
    t = np.arange(int(dur * SR)) / SR
    x = np.zeros_like(t)
    for f in freqs:
        for det in (-0.08, 0.0, 0.09):
            x += signal.sawtooth(2 * np.pi * f * (1 + det / 100) * t + _rng.uniform(0, 6.28))
    x = _lp(x, cutoff, 2) / (len(freqs) * 3)
    a = int(0.35 * SR)
    env = np.ones_like(t)
    env[:a] = np.linspace(0, 1, a)
    env[-a:] = np.linspace(1, 0, a)
    return x * env


def _pluck(f, dur=1.4, bright=1.0):
    """Additive plucked string / soft piano-ish note."""
    t = np.arange(int(dur * SR)) / SR
    x = np.zeros_like(t)
    for k in range(1, 9):
        x += (1 / k ** (1.6 / bright)) * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (2.2 + 1.3 * k))
    x *= 1 - np.exp(-t * 600)
    return x


def _kick(dur=0.45):
    t = np.arange(int(dur * SR)) / SR
    f = 45 + 80 * np.exp(-t * 35)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)


def _add(buf: np.ndarray, j: int, x: np.ndarray, gain: float = 1.0) -> None:
    """Add x into buf at sample j, clipping to the buffer bounds."""
    if j >= len(buf) or j + len(x) <= 0:
        return
    if j < 0:
        x, j = x[-j:], 0
    e = min(len(buf), j + len(x))
    buf[j:e] += x[: e - j] * gain


def generate(mood: str, duration: float, drops: list[float] | None = None,
             lifts: list[float] | None = None, seed: int | None = None) -> np.ndarray:
    """Return a stereo bed (N, 2) of `duration` seconds."""
    global _rng
    if seed is not None:
        _rng = np.random.default_rng(seed)
    if mood not in MOODS:
        raise KeyError(f"Unknown mood '{mood}'. Choose: {', '.join(MOODS)}")
    m = MOODS[mood]
    n = int((duration + 1.0) * SR)
    beat = 60 / m["bpm"]
    bar = 4 * beat
    chord_len = 2 * bar
    pad = np.zeros(n)
    bass = np.zeros(n)
    lead = np.zeros(n)
    perc = np.zeros(n)
    lift_t = min(lifts) if lifts else duration * 0.45

    t0, ci = 0.0, 0
    while t0 < duration + 1.0:
        root, q = m["prog"][ci % len(m["prog"])]
        freqs = _chord(root, q, 3)
        seg = _pad(freqs, chord_len + 0.4, m["pad_cut"])
        i = int(t0 * SR)
        _add(pad, i, seg)
        # sub bass drone on the root
        tt = np.arange(int(chord_len * SR)) / SR
        b = np.sin(2 * np.pi * _hz(root, 1) * tt) * np.minimum(1, tt * 4) * np.minimum(1, (chord_len - tt) * 4)
        _add(bass, i, b, 0.22)
        # arpeggio plucks
        if m.get("pluck"):
            notes = _chord(root, q, m.get("pluck_oct", 5))
            steps = int(chord_len / (beat / 2))
            for s in range(steps):
                ts = t0 + s * beat / 2
                dens = m["pluck_density"] * (1.0 if ts >= lift_t else 0.55)
                if _rng.random() < dens:
                    f = notes[(s * 3 + ci) % len(notes)] * (2 if _rng.random() < 0.15 else 1)
                    p = _pluck(f, 1.2, m["bright"]) * _rng.uniform(0.5, 0.9)
                    if m.get("bounce"):
                        p = p[: int(0.25 * SR)] * np.linspace(1, 0, int(0.25 * SR))
                    _add(lead, int(ts * SR), p)
        # pulse (8ths) and drums
        if m.get("pulse"):
            for s in range(int(chord_len / (beat / 2))):
                ts = t0 + s * beat / 2
                if ts < lift_t * 0.6:
                    continue
                L = int(0.18 * SR)
                tt = np.arange(L) / SR
                p = signal.sawtooth(2 * np.pi * _hz(root, 2) * tt) * np.exp(-tt * 14)
                _add(lead, int(ts * SR), _lp(p, 1200), 0.35)
        if m.get("drums") or m.get("bounce"):
            for s in range(int(chord_len / beat)):
                ts = t0 + s * beat
                if ts < lift_t * 0.5:
                    continue
                k = _kick() * (0.9 if s % 2 == 0 else 0.5)
                _add(perc, int(ts * SR), k)
        if m.get("tick"):
            for s in range(int(chord_len / beat)):
                ts = t0 + s * beat
                L = int(0.03 * SR)
                tt = np.arange(L) / SR
                k = np.sin(2 * np.pi * 2800 * tt) * np.exp(-tt * 250) * (0.25 if s % 2 else 0.4)
                _add(perc, int(ts * SR), k)
        t0 += chord_len
        ci += 1

    mix = (pad * 0.55 + bass * 0.5)[:, None] * np.ones((1, 2))
    lead_st = _width(np.stack([lead, lead], 1) * 0.45, 9)
    out = mix + lead_st + np.stack([perc, perc], 1) * 0.5
    out = reverb(out.astype(np.float32), decay=2.2, mix=0.28, tone_hz=5000)[:n]
    out = _hp(out.T, 55, 2).T

    # Story events: drops (hard cut for ~0.6 s then quick return) ------------
    gain = np.ones(len(out))
    for d in drops or []:
        a, b = int((d - 0.05) * SR), int((d + 0.65) * SR)
        a = max(0, a)
        gain[a:b] = 0.0
        r = int(0.25 * SR)
        gain[b:b + r] = np.linspace(0, 1, len(gain[b:b + r]))
    out = out * gain[:, None]
    # master fade in / out
    fi, fo = int(0.15 * SR), int(1.2 * SR)
    out[:fi] *= np.linspace(0, 1, fi)[:, None]
    end = int(duration * SR)
    out = out[: end]
    out[-fo:] *= np.linspace(1, 0, fo)[:, None]
    return _norm(out, -3)
