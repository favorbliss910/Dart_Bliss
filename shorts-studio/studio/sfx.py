"""Procedural sound-effects library.

Every sound here is synthesized from noise and oscillators, so it is original
and royalty-free. All functions return float32 stereo arrays shaped (N, 2) at
SR Hz, peak-normalized to roughly -3 dBFS. Levels are set later in the mix.

You can override any effect with your own recording: drop a WAV named after
the effect into `sfx_library/` (e.g. `sfx_library/whoosh.wav`, or several
variants `whoosh_1.wav`, `whoosh_2.wav`) and the mixer will pick it instead.
"""
from __future__ import annotations

import numpy as np
from scipy import signal

SR = 48000
_rng = np.random.default_rng()


# --------------------------------------------------------------------------- helpers
def _t(dur: float) -> np.ndarray:
    return np.arange(int(dur * SR)) / SR


def _norm(x: np.ndarray, peak_db: float = -3.0) -> np.ndarray:
    m = np.max(np.abs(x)) + 1e-9
    return (x / m * 10 ** (peak_db / 20)).astype(np.float32)


def _stereo(mono: np.ndarray, pan: float | np.ndarray = 0.0) -> np.ndarray:
    """Equal-power pan. pan in [-1, 1]; may be an array for moving pans."""
    p = (np.asarray(pan) + 1) * np.pi / 4
    return np.stack([mono * np.cos(p), mono * np.sin(p)], axis=1)


def _width(st: np.ndarray, ms: float = 12.0) -> np.ndarray:
    """Haas widening: delay the right channel slightly."""
    d = int(ms / 1000 * SR)
    out = st.copy()
    out[d:, 1] = st[:-d, 1] if d else st[:, 1]
    return out


def _bp(x, lo, hi, order=4):
    sos = signal.butter(order, [lo, min(hi, SR / 2 - 100)], "bandpass", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def _lp(x, f, order=4):
    sos = signal.butter(order, min(f, SR / 2 - 100), "lowpass", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def _hp(x, f, order=4):
    sos = signal.butter(order, f, "highpass", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def _env_ad(n: int, attack: float, decay_curve: float = 4.0) -> np.ndarray:
    """Attack (fraction of length) then exponential-ish decay."""
    a = max(1, int(n * attack))
    up = np.linspace(0, 1, a) ** 2
    down = np.exp(-decay_curve * np.linspace(0, 1, n - a))
    return np.concatenate([up, down])


def _sweep_filter(noise: np.ndarray, f0: float, f1: float, q_oct: float = 0.8,
                  curve: str = "exp") -> np.ndarray:
    """Band-pass a signal with a centre frequency gliding from f0 to f1 (STFT)."""
    nper = 1024
    f, _, Z = signal.stft(noise, fs=SR, nperseg=nper)
    frames = Z.shape[1]
    pos = np.linspace(0, 1, frames)
    if curve == "exp":
        fc = f0 * (f1 / f0) ** pos
    else:
        fc = f0 + (f1 - f0) * pos
    logf = np.log2(np.maximum(f, 1))[:, None]
    gain = np.exp(-0.5 * ((logf - np.log2(fc)[None, :]) / q_oct) ** 2)
    _, y = signal.istft(Z * gain, fs=SR, nperseg=nper)
    return y[: len(noise)]


def reverb(st: np.ndarray, decay: float = 1.6, mix: float = 0.3,
           predelay_ms: float = 15, tone_hz: float = 6000) -> np.ndarray:
    """Cheap, smooth stereo reverb: convolution with decaying filtered noise."""
    n = int(decay * SR)
    t = np.arange(n) / SR
    env = np.exp(-6.9 * t / decay)
    irs = []
    for _ in range(2):
        ir = _lp(_rng.standard_normal(n), tone_hz, 2) * env
        ir = np.concatenate([np.zeros(int(predelay_ms / 1000 * SR)), ir])
        irs.append(ir / np.sqrt(np.sum(ir ** 2)))
    wet = np.stack([signal.fftconvolve(st[:, c], irs[c])[: len(st) + len(irs[c])] for c in range(2)], 1)
    dry = np.vstack([st, np.zeros((len(wet) - len(st), 2))])
    return (dry * (1 - mix) + wet * mix * 0.6).astype(np.float32)


def _sat(x, drive=2.0):
    return np.tanh(x * drive) / np.tanh(drive)


# --------------------------------------------------------------------------- transitions
def whoosh(dur: float = 0.45, direction: str = "lr", bright: float = 1.0) -> np.ndarray:
    """Air whoosh for whip-pans / scene changes. Peak lands ~60% through."""
    n = int(dur * SR)
    noise = _rng.standard_normal(n)
    x = _sweep_filter(noise, 350 * bright, 3500 * bright, 0.7)
    x = x + 0.5 * _sweep_filter(_rng.standard_normal(n), 3500 * bright, 900 * bright, 0.5)
    tt = np.linspace(0, 1, n)
    env = np.exp(-((tt - 0.6) / 0.22) ** 2)
    pan = np.linspace(-0.8, 0.8, n) if direction == "lr" else np.linspace(0.8, -0.8, n)
    return _norm(_stereo(x * env, pan))


def swish(dur: float = 0.22) -> np.ndarray:
    """Short, bright swish for fast cuts, text slides and object flicks."""
    n = int(dur * SR)
    x = _sweep_filter(_rng.standard_normal(n), 1500, 7000, 0.5)
    env = np.sin(np.linspace(0, np.pi, n)) ** 3
    return _norm(_stereo(x * env, np.linspace(-0.5, 0.5, n)))


def riser(dur: float = 1.6, top: float = 7000) -> np.ndarray:
    """Tension riser that ENDS at its peak - schedule it to end on the hit."""
    n = int(dur * SR)
    tt = np.linspace(0, 1, n)
    noise = _sweep_filter(_rng.standard_normal(n), 250, top, 0.6)
    f = 110 * (2 ** (tt * 3))  # 3 octaves up
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.5 * np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR)
    trem = 1 + 0.35 * np.sin(2 * np.pi * np.cumsum(4 + 18 * tt) / SR)
    env = tt ** 2.2
    x = (noise * 0.8 + 0.25 * tone * trem) * env
    st = _width(_stereo(x))
    st[-int(0.01 * SR):] *= np.linspace(1, 0, int(0.01 * SR))[:, None]
    return _norm(st)


def reverse_swell(dur: float = 1.2) -> np.ndarray:
    """Reversed-reverb 'sucking' swell into a moment."""
    n = int(dur * SR)
    burst = np.zeros((int(0.08 * SR), 2))
    burst[:, 0] = _bp(_rng.standard_normal(len(burst)), 300, 6000)
    burst[:, 1] = _bp(_rng.standard_normal(len(burst)), 300, 6000)
    tail = reverb(burst, decay=dur, mix=1.0)[:n]
    return _norm(tail[::-1].copy())


# --------------------------------------------------------------------------- hits
def impact(dur: float = 0.9, weight: float = 1.0) -> np.ndarray:
    """Punchy cinematic impact: sub thump + body + transient click."""
    t = _t(dur)
    f = 40 + 110 * np.exp(-t * 18)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.5 / weight)
    body = _bp(_rng.standard_normal(len(t)), 80, 900) * np.exp(-t * 14)
    click = _hp(_rng.standard_normal(len(t)), 2500) * np.exp(-t * 120)
    x = _sat(sub * 1.0 + body * 0.6 + click * 0.35, 1.8)
    return _norm(reverb(_stereo(x), decay=1.2, mix=0.18))


def boom(dur: float = 2.6) -> np.ndarray:
    """Huge trailer boom / sub drop for the biggest reveal of the video."""
    t = _t(dur)
    f = 28 + 70 * np.exp(-t * 3.5)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.6)
    crack = _lp(_rng.standard_normal(len(t)), 2500) * np.exp(-t * 9)
    x = _sat(sub + 0.5 * crack, 2.2)
    return _norm(reverb(_stereo(x), decay=2.4, mix=0.3, tone_hz=3000))


def braam(dur: float = 2.2, root_hz: float = 55.0) -> np.ndarray:
    """Dark brassy 'BWAAM' (detuned saw stack) for ominous reveals."""
    t = _t(dur)
    x = np.zeros_like(t)
    for mult in (1, 2, 3):
        for det in (-0.12, 0.0, 0.11):
            x += signal.sawtooth(2 * np.pi * root_hz * mult * (1 + det / 100) * t + _rng.uniform(0, 6)) / mult
    cutoff_env = 300 + 1600 * np.exp(-t * 1.2) * (1 - np.exp(-t * 25))
    # time-varying low-pass via short blocks
    out = np.zeros_like(x)
    blk = 1024
    zi = None
    for i in range(0, len(x), blk):
        sos = signal.butter(2, cutoff_env[i], "lowpass", fs=SR, output="sos")
        if zi is None:
            zi = signal.sosfilt_zi(sos) * 0
        out[i:i + blk], zi = signal.sosfilt(sos, x[i:i + blk], zi=zi)
    env = (1 - np.exp(-t * 30)) * np.exp(-t * 1.0)
    return _norm(reverb(_width(_stereo(_sat(out * env, 1.5))), decay=2.0, mix=0.3))


def thud(dur: float = 0.35) -> np.ndarray:
    """Soft body thud: footsteps on wood, a book on a table, a fall."""
    t = _t(dur)
    f = 55 + 90 * np.exp(-t * 30)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 16)
    x += 0.3 * _lp(_rng.standard_normal(len(t)), 700) * np.exp(-t * 40)
    return _norm(_stereo(x))


def heartbeat(beats: int = 2, bpm: float = 70) -> np.ndarray:
    period = 60 / bpm
    out = np.zeros((int(period * beats * SR) + SR // 2, 2), np.float32)
    for b in range(beats):
        for off, g in ((0.0, 1.0), (0.18, 0.7)):
            s = thud(0.3) * g
            i = int((b * period + off) * SR)
            out[i:i + len(s)] += s
    return _norm(out)


# --------------------------------------------------------------------------- UI / text
def pop(pitch: float = 1.0) -> np.ndarray:
    """Bubbly pop for captions, emojis, icons, number counters."""
    t = _t(0.09)
    f = (900 - 500 * (t / t[-1])) * pitch
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 45)
    x += 0.2 * _hp(_rng.standard_normal(len(t)), 3000) * np.exp(-t * 300)
    return _norm(_stereo(x), -6)


def click() -> np.ndarray:
    t = _t(0.03)
    x = _bp(_rng.standard_normal(len(t)), 2000, 9000) * np.exp(-t * 250)
    return _norm(_stereo(x), -6)


def tick() -> np.ndarray:
    """Clock tick - good under countdowns or a 'thinking' beat."""
    t = _t(0.05)
    x = np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 180) + 0.4 * _hp(_rng.standard_normal(len(t)), 4000) * np.exp(-t * 400)
    return _norm(_stereo(x), -8)


def ticking(dur: float = 3.0, bpm: float = 120) -> np.ndarray:
    out = np.zeros((int(dur * SR), 2), np.float32)
    step = 60 / bpm
    for i, s in enumerate(np.arange(0, dur - 0.06, step)):
        k = tick() * (1.0 if i % 2 == 0 else 0.7)
        j = int(s * SR)
        out[j:j + len(k)] += k[: len(out) - j]
    return out


def typing(n_keys: int = 8, rate: float = 14.0) -> np.ndarray:
    out = np.zeros((int(n_keys / rate * SR) + 2000, 2), np.float32)
    for k in range(n_keys):
        c = click() * _rng.uniform(0.6, 1.0)
        j = int((k / rate + _rng.uniform(0, 0.02)) * SR)
        out[j:j + len(c)] += c
    return _norm(out, -6)


def ding(freq: float = 1318.5) -> np.ndarray:
    """Bell 'ding' - realisations, correct answers, lightbulb moments."""
    t = _t(2.0)
    x = np.zeros_like(t)
    for ratio, amp, dec in ((1, 1, 2.2), (2.76, 0.5, 3.5), (5.4, 0.25, 6), (8.93, 0.12, 9)):
        x += amp * np.sin(2 * np.pi * freq * ratio * t) * np.exp(-t * dec)
    x *= 1 - np.exp(-t * 800)
    return _norm(reverb(_stereo(x), decay=1.5, mix=0.25), -5)


def sparkle(dur: float = 1.2) -> np.ndarray:
    """Magic shimmer: scattered high bell notes from a pentatonic scale."""
    out = np.zeros((int(dur * SR), 2), np.float32)
    scale = [1046.5, 1174.7, 1318.5, 1568.0, 1760.0, 2093.0, 2349.3, 2637.0]
    for _ in range(14):
        f = _rng.choice(scale)
        s = ding(f)[: int(0.6 * SR)] * _rng.uniform(0.2, 0.6)
        pan = _rng.uniform(-0.8, 0.8)
        s = s * np.array([np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)]) * 1.4
        j = int(_rng.uniform(0, dur * 0.7) * SR)
        e = min(len(out), j + len(s))
        out[j:e] += s[: e - j]
    return _norm(reverb(out, decay=1.8, mix=0.35), -5)


def coin(n: int = 1) -> np.ndarray:
    """Retro coin / cash chime - money, gains, rewards."""
    seg = []
    for _ in range(n):
        t1, t2 = _t(0.07), _t(0.35)
        a = signal.square(2 * np.pi * 987.8 * t1) * 0.3
        b = signal.square(2 * np.pi * 1318.5 * t2) * 0.3 * np.exp(-t2 * 8)
        seg.append(np.concatenate([a, b]))
    x = _lp(np.concatenate(seg), 6000)
    return _norm(reverb(_stereo(x), decay=0.8, mix=0.15), -6)


def glitch(dur: float = 0.4) -> np.ndarray:
    """Digital glitch/stutter - for 'something is wrong', simulations, errors."""
    n = int(dur * SR)
    x = np.zeros(n)
    i = 0
    while i < n:
        L = int(_rng.uniform(0.01, 0.05) * SR)
        kind = _rng.integers(0, 3)
        t = np.arange(L) / SR
        if kind == 0:
            seg = signal.square(2 * np.pi * _rng.uniform(80, 1200) * t)
        elif kind == 1:
            seg = np.round(_rng.standard_normal(L) * 3) / 3
        else:
            seg = np.zeros(L)
        x[i:i + L] = seg[: n - i] * _rng.uniform(0.3, 1)
        i += L
    return _norm(_stereo(_lp(x, 9000), _rng.uniform(-0.4, 0.4)), -6)


def boing() -> np.ndarray:
    """Cartoon boing - comedy beats, bounces, 'oops'."""
    t = _t(0.7)
    f = 180 + 120 * np.exp(-t * 3) * (1 + 0.5 * np.sin(2 * np.pi * 14 * t) * np.exp(-t * 4))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5)
    return _norm(_stereo(x), -5)


def slide_down() -> np.ndarray:
    """Descending slide - failure, disappointment, 'womp'."""
    t = _t(0.9)
    f = 700 * (0.35 ** (t / t[-1]))
    x = (np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * np.sin(4 * np.pi * np.cumsum(f) / SR))
    x *= np.minimum(1, t * 30) * np.exp(-t * 1.5)
    return _norm(_stereo(_lp(x, 4000)), -5)


def tape_stop(dur: float = 0.8) -> np.ndarray:
    """Tape-stop / power-down - time freezes, record stops, plan fails."""
    t = _t(dur)
    f = 220 * (1 - t / dur) ** 2 + 20
    x = signal.sawtooth(2 * np.pi * np.cumsum(f) / SR) * (1 - t / dur)
    return _norm(_stereo(_lp(x, 2500)), -6)


# --------------------------------------------------------------------------- textures
def rumble(dur: float = 3.0) -> np.ndarray:
    """Low earth rumble - earthquakes, crowds stampeding, machinery, dread."""
    n = int(dur * SR)
    brown = np.cumsum(_rng.standard_normal(n))
    brown = _hp(brown - np.mean(brown), 20, 2)
    x = _lp(brown, 160)
    lfo = 0.7 + 0.3 * np.sin(2 * np.pi * 0.7 * np.arange(n) / SR)
    fade = np.minimum(1, np.minimum(np.arange(n), n - np.arange(n)) / (0.4 * SR))
    return _norm(_width(_stereo(x * lfo * fade), 18))


def wind(dur: float = 4.0) -> np.ndarray:
    n = int(dur * SR)
    tt = np.arange(n) / SR
    fc = 600 + 400 * np.sin(2 * np.pi * 0.15 * tt) + 200 * np.sin(2 * np.pi * 0.37 * tt)
    lo, hi = fc.min(), fc.max()
    x = _sweep_filter(_rng.standard_normal(n), lo, hi, 0.5, curve="lin")
    amp = 0.6 + 0.4 * np.sin(2 * np.pi * 0.23 * tt)
    fade = np.minimum(1, np.minimum(np.arange(n), n - np.arange(n)) / (0.6 * SR))
    return _norm(_width(_stereo(x * amp * fade), 20), -6)


def splash() -> np.ndarray:
    """Water splash with bubbles."""
    t = _t(1.2)
    burst = _bp(_rng.standard_normal(len(t)), 400, 7000) * np.exp(-t * 7)
    bub = np.zeros_like(t)
    for _ in range(20):
        s = int(_rng.uniform(0.02, 0.8) * SR)
        L = int(0.04 * SR)
        tt = np.arange(L) / SR
        f = _rng.uniform(500, 1600) * (1 + 3 * tt)
        bub[s:s + L] += np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 70) * 0.3
    return _norm(reverb(_stereo(burst + bub), decay=0.9, mix=0.2))


def crowd_gasp(dur: float = 1.2) -> np.ndarray:
    """Abstract 'crowd reaction' - layered breathy formant noise swells."""
    n = int(dur * SR)
    out = np.zeros(n)
    for _ in range(10):
        f = _rng.uniform(500, 1100)
        x = _bp(_rng.standard_normal(n), f * 0.8, f * 1.4, 2)
        env = np.exp(-((np.linspace(0, 1, n) - _rng.uniform(0.15, 0.35)) / 0.18) ** 2)
        out += x * env
    return _norm(_width(_stereo(out), 20), -6)


def silence(dur: float = 0.5) -> np.ndarray:
    return np.zeros((int(dur * SR), 2), np.float32)


# --------------------------------------------------------------------------- registry
REGISTRY = {
    # transitions / motion
    "whoosh": whoosh, "swish": swish, "riser": riser, "reverse_swell": reverse_swell,
    # hits
    "impact": impact, "boom": boom, "braam": braam, "thud": thud, "heartbeat": heartbeat,
    # UI / text
    "pop": pop, "click": click, "tick": tick, "ticking": ticking, "typing": typing,
    "ding": ding, "sparkle": sparkle, "coin": coin, "glitch": glitch,
    # comedy
    "boing": boing, "slide_down": slide_down, "tape_stop": tape_stop,
    # textures
    "rumble": rumble, "wind": wind, "splash": splash, "crowd_gasp": crowd_gasp,
}

# How each effect should be aligned to its cue time:
#   "start"  - sound starts at the cue
#   "peak"   - sound's loudest point lands on the cue (whooshes)
#   "end"    - sound ends on the cue (risers, reverse swells)
ANCHOR = {"whoosh": "peak", "swish": "peak", "riser": "end", "reverse_swell": "end"}

# Default level (dB relative to the voice bus) for each effect.
DEFAULT_GAIN_DB = {
    "whoosh": -12, "swish": -15, "riser": -14, "reverse_swell": -13,
    "impact": -8, "boom": -7, "braam": -10, "thud": -12, "heartbeat": -10,
    "pop": -16, "click": -18, "tick": -18, "ticking": -20, "typing": -16,
    "ding": -14, "sparkle": -15, "coin": -14, "glitch": -14,
    "boing": -13, "slide_down": -13, "tape_stop": -12,
    "rumble": -12, "wind": -18, "splash": -12, "crowd_gasp": -16,
}


def render(name: str, **kw) -> np.ndarray:
    if name not in REGISTRY:
        raise KeyError(f"Unknown SFX '{name}'. Available: {', '.join(sorted(REGISTRY))}")
    return REGISTRY[name](**kw)


if __name__ == "__main__":
    # Audition every effect:  python -m studio.sfx  ->  output/sfx_preview/
    import soundfile as sf
    from .config import OUTPUT
    out = OUTPUT / "sfx_preview"
    out.mkdir(parents=True, exist_ok=True)
    reel = []
    for name in REGISTRY:
        clip = render(name)
        sf.write(out / f"{name}.wav", clip, SR)
        reel += [clip, silence(0.6)]
        print(f"{name:14s} {len(clip) / SR:4.1f}s")
    sf.write(out / "_all_effects_reel.wav", np.vstack(reel), SR)
    print(f"-> {out}")
