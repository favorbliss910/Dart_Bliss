"""Procedural SFX + music bed + mix with the Kokoro VO (no sample libraries needed)."""
import math, os
import numpy as np
import soundfile as sf

SR = 48000
rng = np.random.default_rng(7)


def _t(d):
    return np.arange(int(d * SR)) / SR


def env(n, a=0.005, r=0.2, curve=4.0):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / max(r, 1e-4) * (curve / 4))
    return e




def lp_fast(x, cutoff):
    from numpy.fft import rfft, irfft, rfftfreq
    X = rfft(x)
    f = rfftfreq(len(x), 1 / SR)
    X *= 1 / np.sqrt(1 + (f / cutoff) ** 4)
    return irfft(X, len(x))


def hp_fast(x, cutoff):
    from numpy.fft import rfft, irfft, rfftfreq
    X = rfft(x)
    f = rfftfreq(len(x), 1 / SR)
    X *= 1 / np.sqrt(1 + (cutoff / np.maximum(f, 1)) ** 4)
    return irfft(X, len(x))


def bp_sweep(noise, f0, f1):
    """crude swept band: split in blocks, band-filter each."""
    n = len(noise)
    out = np.zeros(n)
    B = 2048
    for i in range(0, n, B):
        seg = noise[i:i + B]
        fc = f0 + (f1 - f0) * (i / n)
        out[i:i + B] = hp_fast(lp_fast(seg, fc * 1.6), fc * 0.6)
    return out


def norm(x, peak=0.9):
    m = np.abs(x).max()
    return x / m * peak if m > 0 else x


# ----------------------------------------------------------------------------- sfx bank
def s_whoosh(d=0.35):
    n = int(d * SR)
    x = rng.standard_normal(n)
    x = bp_sweep(x, 500, 3500)
    e = np.sin(np.linspace(0, np.pi, n)) ** 2
    return norm(x * e, 0.5)


def s_pop():
    t = _t(0.18)
    f = 900 * np.exp(-t * 25) + 250
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.002, 0.05), 0.7)


def s_sting(root=523.25):
    t = _t(1.2)
    x = sum(np.sin(2 * np.pi * root * r * t) * env(len(t), 0.003, 0.35) for r in (1, 1.26, 1.5, 2))
    return norm(x, 0.5)


def s_hit():
    t = _t(1.4)
    f = 110 * np.exp(-t * 6) + 40
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.002, 0.45)
    nz = lp_fast(rng.standard_normal(len(t)), 2500) * env(len(t), 0.001, 0.08)
    return norm(body + nz * 0.6, 0.9)


def s_braam():
    t = _t(2.2)
    x = np.zeros(len(t))
    for fr in (55, 55.6, 82.4, 110.3):
        x += 2 * ((t * fr) % 1) - 1
    x = lp_fast(x, 700)
    e = np.minimum(1, t / 0.04) * np.exp(-t * 1.4)
    return norm(x * e, 0.85)


def s_snip():
    out = np.zeros(int(0.25 * SR))
    for k, d in enumerate((0, 0.07)):
        n = int(0.04 * SR)
        x = hp_fast(rng.standard_normal(n), 3000) * env(n, 0.0005, 0.012)
        i = int(d * SR)
        out[i:i + n] += x
    t = _t(0.25)
    out += np.sin(2 * np.pi * 4200 * t) * env(len(t), 0.001, 0.04) * 0.3
    return norm(out, 0.6)


def s_coin():
    t = _t(1.2)
    x = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * dcy) * a for f, dcy, a in ((2093, 3.5, 1), (2960, 5, 0.6), (4186, 7, 0.4), (5590, 9, 0.3)))
    return norm(x, 0.45)


def s_ting():
    return s_coin()[: int(0.5 * SR)]


def s_drums():
    out = np.zeros(int(1.5 * SR))
    for k in range(6):
        t = _t(0.3)
        f = 140 * np.exp(-t * 15) + 70
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.002, 0.12)
        i = int(k * 0.24 * SR)
        out[i:i + len(t)] += x * (0.6 + 0.08 * k)
    return norm(out, 0.8)


def s_wind(d=3.0):
    n = int(d * SR)
    x = lp_fast(rng.standard_normal(n), 600)
    m = 0.6 + 0.4 * np.sin(np.linspace(0, 5, n))
    e = np.sin(np.linspace(0, np.pi, n))
    return norm(x * m * e, 0.35)


def s_riser(d=1.6):
    n = int(d * SR)
    x = bp_sweep(rng.standard_normal(n), 300, 5000)
    return norm(x * np.linspace(0, 1, n) ** 2, 0.45)


def s_bells():
    t = _t(2.5)
    out = np.zeros(int(3.2 * SR))
    for k, f in enumerate((1046.5, 1318.5, 1568, 2093)):
        x = sum(np.sin(2 * np.pi * f * r * t) * np.exp(-t * (2 + r)) * a for r, a in ((1, 1), (2.76, 0.4), (5.4, 0.2)))
        i = int(k * 0.15 * SR)
        out[i:i + len(t)] += x
    return norm(out, 0.4)


def s_shimmer():
    t = _t(1.6)
    out = np.zeros(len(t))
    for k, f in enumerate((1568, 1976, 2349, 3136, 3951)):
        i = int(k * 0.07 * SR)
        tt = t[: len(t) - i]
        out[i:] += np.sin(2 * np.pi * f * tt) * np.exp(-tt * 3)
    return norm(out, 0.3)


def s_pizz(notes=(392, 330, 392, 330), gap=0.2):
    out = np.zeros(int((len(notes) * gap + 0.4) * SR))
    for k, f in enumerate(notes):
        t = _t(0.35)
        x = (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)) * env(len(t), 0.002, 0.08)
        i = int(k * gap * SR)
        out[i:i + len(t)] += x
    return norm(out, 0.5)


def s_boing():
    t = _t(0.6)
    f = 220 + 120 * np.sin(2 * np.pi * 9 * t) * np.exp(-t * 5)
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.003, 0.25), 0.5)


def s_buzzer():
    t = _t(0.6)
    x = np.sign(np.sin(2 * np.pi * 140 * t)) * 0.6 + np.sign(np.sin(2 * np.pi * 147 * t)) * 0.4
    x = lp_fast(x, 2500) * (t < 0.55)
    return norm(x, 0.35)


def s_slam():
    h = s_hit()
    nz = hp_fast(rng.standard_normal(int(0.2 * SR)), 800) * env(int(0.2 * SR), 0.001, 0.03)
    h[: len(nz)] += nz * 0.8
    return norm(h, 0.95)


def s_creak():
    t = _t(0.9)
    f = 180 + 60 * np.sin(2 * np.pi * 1.3 * t)
    x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * (rng.random(len(t)) < 0.35)
    x = lp_fast(x.astype(float), 1500) * np.sin(np.linspace(0, np.pi, len(t)))
    return norm(x, 0.3)


def s_chalk():
    n = int(0.7 * SR)
    x = hp_fast(rng.standard_normal(n), 2500) * (0.5 + 0.5 * np.sign(np.sin(np.linspace(0, 40, n))))
    return norm(x * np.sin(np.linspace(0, np.pi, n)), 0.25)


def s_scratch():
    t = _t(0.7)
    f = 300 + 900 * np.abs(np.sin(2 * np.pi * 3 * t))
    x = lp_fast(np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.5 + rng.standard_normal(len(t)) * 0.3, 3000)
    return norm(x * env(len(t), 0.005, 0.4), 0.5)


def s_sizzle():
    n = int(1.4 * SR)
    x = hp_fast(rng.standard_normal(n), 4000) * (rng.random(n) < 0.4)
    return norm(x * np.sin(np.linspace(0, np.pi, n)), 0.3)


def s_storm():
    n = int(4.5 * SR)
    x = lp_fast(rng.standard_normal(n), 400)
    th = s_hit()
    x[int(0.4 * SR): int(0.4 * SR) + len(th)] += lp_fast(th, 300) * 0.9
    return norm(x * np.minimum(1, np.linspace(0, 6, n)) * np.minimum(1, np.linspace(6, 0, n)), 0.6)


def s_stamp():
    return s_slam()


def s_grumble():
    t = _t(1.2)
    x = np.zeros(len(t))
    for f0 in (120, 150, 95):
        f = f0 + 20 * np.sin(2 * np.pi * (3 + f0 / 100) * t)
        x += np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR))
    x = lp_fast(x, 700) * np.sin(np.linspace(0, np.pi, len(t))) * (0.6 + 0.4 * np.sin(2 * np.pi * 6 * t))
    return norm(x, 0.3)


def s_final():
    t = _t(3.0)
    h = np.zeros(len(t))
    hit = s_hit()
    h[: len(hit)] += hit
    ch = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * 1.0) for f in (130.8, 196, 261.6, 329.6, 392))
    return norm(h + ch * 0.35, 0.95)


def s_tick():
    t = _t(0.08)
    return norm(np.sin(2 * np.pi * 3000 * t) * env(len(t), 0.0005, 0.01), 0.4)


def s_gulp():
    t = _t(0.25)
    f = 300 + 500 * t / 0.25
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.005, 0.08), 0.4)


BANK = {
    "whoosh": s_whoosh, "pop": s_pop, "sting": s_sting, "hit": s_hit, "braam": s_braam, "snip": s_snip,
    "coin": s_coin, "ting": s_ting, "drums": s_drums, "wind": s_wind, "riser": s_riser, "bells": s_bells,
    "shimmer": s_shimmer, "pizz": s_pizz, "boing": s_boing, "buzzer": s_buzzer, "slam": s_slam, "creak": s_creak,
    "chalk": s_chalk, "scratch": s_scratch, "sizzle": s_sizzle, "storm": s_storm, "stamp": s_stamp,
    "grumble": s_grumble, "final": s_final, "tick": s_tick, "gulp": s_gulp,
    "sting_low": lambda: s_sting(392.0), "pizz_up": lambda: s_pizz((392, 440, 494, 523), 0.12),
    "tiptoe": lambda: s_pizz((196, 0.0001, 247, 0.0001, 196, 0.0001, 262), 0.22),
}


# ----------------------------------------------------------------------------- music
NOTE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def hz(midi):
    return 440 * 2 ** ((midi - 69) / 12)


def marimba(f, d=0.5):
    t = _t(d)
    return (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 20)) * env(len(t), 0.002, 0.18)


def bass(f, d=0.5):
    t = _t(d)
    x = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)
    return x * env(len(t), 0.01, 0.35)


def music(duration, moods, bpm=112, outro_at=None):
    """moods: list of (t0, t1, mood). bright arpeggio loop; 'dread' bars go minor and sparse."""
    out = np.zeros(int((duration + 2) * SR))
    beat = 60 / bpm
    bright = [[60, 64, 67, 72], [57, 60, 64, 69], [53, 57, 60, 65], [55, 59, 62, 67]]   # C Am F G
    dark = [[57, 60, 64, 69], [53, 57, 60, 65], [50, 53, 57, 62], [52, 56, 59, 64]]     # Am F Dm E
    n_beats = int(duration / beat)

    def mood_at(t):
        for t0, t1, m in moods:
            if t0 <= t < t1:
                return m
        return "normal"

    for b in range(n_beats):
        t = b * beat
        if outro_at and t >= outro_at:
            break
        m = mood_at(t)
        bar = b // 4
        prog = dark if m in ("dread",) else bright
        chord = prog[bar % 4]
        i = int(t * SR)
        # bass on beats 1 and 3
        if b % 2 == 0:
            x = bass(hz(chord[0] - 24), beat * 1.8)
            out[i:i + len(x)] += x * 0.55
        # arpeggio eighths
        for e in range(2):
            if m == "dread" and e == 1:
                continue
            note = chord[(b * 2 + e) % 4] + (12 if m == "final" else 0)
            x = marimba(hz(note + 12), beat)
            j = i + int(e * beat / 2 * SR)
            out[j:j + len(x)] += x * (0.32 if m != "dread" else 0.28)
        # hat
        if m != "dread":
            n = int(0.03 * SR)
            hh = hp_fast(rng.standard_normal(n), 7000) * env(n, 0.0005, 0.01)
            j = i + int(beat / 2 * SR)
            out[j:j + n] += hh * 0.12
    return out


def build_mix(story, gain_db_music=-19):
    vo, sr = sf.read(os.path.join(story.dir, "audio", "voice.wav"))
    if sr != SR:
        idx = np.arange(int(len(vo) * SR / sr)) * sr / SR
        vo = np.interp(idx, np.arange(len(vo)), vo)
    dur = len(vo) / SR
    total = dur + 0.0
    out = np.zeros(int(total * SR) + SR * 4)
    out[: len(vo)] += vo * 1.0
    moods = [(ch["s"], ch["e"] + 0.4, ch["mood"]) for ch in story.timing["chunks"]]
    last = story.timing["chunks"][-1]["s"]
    mus = music(total, moods, outro_at=None)
    g = 10 ** (gain_db_music / 20)
    # music swell at the very end
    ramp = np.ones(len(mus))
    se = int(story.timing["speech_end"] * SR)
    ramp[se:] = np.linspace(1, 2.2, len(ramp) - se)
    mus = mus * ramp
    n = min(len(mus), len(out))
    out[:n] += mus[:n] * g
    cache = {}
    events = list(story.sfx)
    for st, wh in story.cuts:
        if wh:
            events.append((st - 0.17, "whoosh", 0.32))
    for t, name, gain in events:
        if name not in cache:
            cache[name] = BANK[name]()
        x = cache[name]
        i = max(0, int(t * SR))
        j = min(len(out), i + len(x))
        out[i:j] += x[: j - i] * gain * 0.55
    out = out[: int(total * SR)]
    # fade tail
    fade = int(0.5 * SR)
    out[-fade:] *= np.linspace(1, 0, fade)
    # soft limiter
    out = np.tanh(out * 1.1) / np.tanh(1.1)
    out = norm(out, 0.95)
    stereo = np.stack([out, out], axis=1)
    path = os.path.join(story.dir, "audio", "mix.wav")
    sf.write(path, stereo, SR)
    return path
