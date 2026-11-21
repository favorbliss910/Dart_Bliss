"""Sound design for the drongo story. Everything is synthesised (no sample library):
VO chain (ffmpeg) + music bed + ambience + ~180 cue-synced SFX, sidechain-ducked under
the voice, then mastered to -14 LUFS / -1.5 dBTP for TikTok/Shorts.
  python3 sound.py <voiceover.wav> out_master.wav"""
import subprocess, sys, math
import numpy as np
import cues

SR = 48000
RNG = np.random.default_rng(7)


def t_(d): return np.arange(int(d * SR)) / SR


def env_ad(n, a=0.005, d=0.2, curve=3.0):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / max(d, 1e-4) * curve / 3)
    return e


def noise(d): return RNG.standard_normal(int(d * SR))


def lp(x, fc):                      # FFT low-pass (brickwall, fine for sfx)
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X[f > fc] = 0; return np.fft.irfft(X, len(x))


def hp(x, fc):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X[f < fc] = 0; return np.fft.irfft(X, len(x))


def bp(x, lo, hi): return hp(lp(x, hi), lo)


def sweep_noise(d, f0, f1, q=0.5):
    """noise whose band moves from f0 to f1 (vectorised: crossfade of fixed bands)."""
    n = noise(d); steps = 8
    fs = np.geomspace(f0, f1, steps)
    out = np.zeros(len(n)); t = np.linspace(0, 1, len(n))
    for i, f in enumerate(fs):
        band = bp(n, f * (1 - q * 0.5), f * (1 + q))
        w = np.exp(-((t - i / (steps - 1)) ** 2) / (2 * (0.5 / steps) ** 2))
        out += band * w
    return out / (np.abs(out).max() + 1e-9)


def tone(d, f, shape="sin", fm=None):
    t = t_(d)
    ph = 2 * np.pi * np.cumsum(f(t) if callable(f) else np.full(len(t), f)) / SR
    if fm is not None: ph = ph + fm(t)
    return np.sin(ph) if shape == "sin" else np.sign(np.sin(ph)) * 0.6 + np.sin(ph) * 0.4


# ============================================================ SFX
def sfx(kind):
    if kind == "whoosh":
        d = 0.42; x = sweep_noise(d, 500, 4200) * np.sin(np.pi * np.linspace(0, 1, int(d * SR))) ** 1.6; return x * 0.7
    if kind == "swoop":
        d = 0.9; x = sweep_noise(d, 3500, 400) * np.sin(np.pi * np.linspace(0, 1, int(d * SR))) ** 1.3; return x * 0.9
    if kind == "stinger":
        d = 1.0; t = t_(d)
        return (tone(d, 220) + tone(d, 277.2) * 0.8 + tone(d, 329.6) * 0.7) * np.exp(-t * 3.2) * 0.25 + sweep_noise(d, 800, 6000) * np.exp(-t * 6) * 0.25
    if kind == "hit":
        d = 1.4; t = t_(d)
        body = tone(d, lambda t: 110 * np.exp(-t * 3.5) + 38) * np.exp(-t * 2.6)
        return (body * 0.95 + lp(noise(d), 2400) * np.exp(-t * 18) * 0.7 + tone(d, 70) * np.exp(-t * 1.5) * 0.3) * 0.9
    if kind == "boom":
        d = 2.0; t = t_(d)
        return (tone(d, lambda t: 80 * np.exp(-t * 1.6) + 30) * np.exp(-t * 1.5) * 1.1 + lp(noise(d), 1600) * np.exp(-t * 7) * 0.8
                + sweep_noise(d, 3000, 200) * np.exp(-t * 3) * 0.3) * 0.9
    if kind == "thud":
        d = 0.5; t = t_(d); return tone(d, lambda t: 90 * np.exp(-t * 14) + 45) * np.exp(-t * 9) + lp(noise(d), 800) * np.exp(-t * 30) * 0.5
    if kind == "pop":
        d = 0.16; t = t_(d); return tone(d, lambda t: 900 * np.exp(-t * 40) + 260) * np.exp(-t * 28) * 0.8
    if kind == "ting":
        d = 1.2; t = t_(d); return (tone(d, 1760) + tone(d, 2637) * 0.5 + tone(d, 3520) * 0.25) * np.exp(-t * 5) * 0.45
    if kind == "ding":
        d = 0.9; t = t_(d); return (tone(d, 988) + tone(d, 1976) * 0.4) * np.exp(-t * 6) * 0.5
    if kind == "sparkle":
        d = 1.2; x = np.zeros(int(d * SR))
        for k in range(7):
            s = int((k * 0.06 + RNG.uniform(0, 0.03)) * SR); f = 1800 * (1.25 ** k)
            tt = tone(0.35, f) * np.exp(-t_(0.35) * 9) * 0.35
            x[s:s + len(tt)] += tt[:len(x) - s]
        return x
    if kind == "tick":
        d = 0.08; t = t_(d); return tone(d, 2400) * np.exp(-t * 90) * 0.5 + noise(d) * np.exp(-t * 150) * 0.2
    if kind == "click":
        d = 0.12; t = t_(d); return (bp(noise(d), 1500, 6000) * np.exp(-t * 90) * 0.9 + tone(d, 600) * np.exp(-t * 80) * 0.4)
    if kind == "boing":
        d = 0.5; t = t_(d); return tone(d, lambda t: 300 + 220 * np.sin(2 * np.pi * 9 * t) * np.exp(-t * 6) + 120 * np.exp(-t * 4)) * np.exp(-t * 6) * 0.7
    if kind == "buzz":
        d = 0.35; t = t_(d); return tone(d, 140, "sq") * (np.sin(2 * np.pi * 30 * t) > -0.2) * np.exp(-t * 6) * 0.5
    if kind == "sadslide":
        d = 1.2; t = t_(d); return tone(d, lambda t: 420 * np.exp(-t * 0.9) * (1 - 0.0 * t), "sq") * np.exp(-t * 2.2) * 0.35 * (1 + 0.15 * np.sin(2 * np.pi * 6 * t))
    if kind == "scratch":
        d = 0.5; t = t_(d); f = lambda t: 900 * np.sin(2 * np.pi * 5 * t) + 1200
        return bp(noise(d), 600, 5000) * (0.6 + 0.4 * np.sin(2 * np.pi * 11 * t)) * np.exp(-t * 4) * 1.0 + tone(d, f) * np.exp(-t * 6) * 0.2
    if kind == "page":
        d = 0.35; t = t_(d); return bp(noise(d), 1000, 7000) * np.sin(np.pi * t / d) ** 2 * 0.7
    if kind == "wind":
        d = 3.0; t = t_(d); return lp(noise(d), 900) * np.sin(np.pi * t / d) ** 1.5 * 0.9
    if kind == "dig":
        d = 6.5; x = np.zeros(int(d * SR)); k = 0.0
        while k < d - 0.2:
            s = int(k * SR); c = bp(noise(0.12), 800, 5000) * np.exp(-t_(0.12) * 28) * RNG.uniform(0.3, 0.6)
            x[s:s + len(c)] += c[:len(x) - s]; k += RNG.uniform(0.07, 0.13)
        return x * np.minimum(1, np.minimum(t_(d) / 0.3, (d - t_(d)) / 0.5))
    if kind == "munch":
        d = 0.4; x = np.zeros(int(d * SR))
        for k in range(3):
            s = int(k * 0.12 * SR); c = bp(noise(0.08), 400, 3500) * np.exp(-t_(0.08) * 40) * 0.8
            x[s:s + len(c)] += c
        return x
    if kind == "dive":
        d = 1.0; t = t_(d); sw = sweep_noise(d, 2500, 200) * np.exp(-t * 3) * 0.7
        th = tone(d, lambda t: 70 * np.exp(-t * 6) + 40) * np.exp(-t * 7) * 0.8 * (t > 0.0)
        sand = bp(noise(d), 600, 3000) * np.exp(-t * 6) * 0.5
        return sw + th + sand
    if kind == "scurry":
        d = 1.4; x = np.zeros(int(d * SR)); k = 0.0
        while k < d - 0.1:
            s = int(k * SR); c = bp(noise(0.05), 500, 4000) * np.exp(-t_(0.05) * 60) * RNG.uniform(0.3, 0.7) * (1 - k / d)
            x[s:s + len(c)] += c[:len(x) - s]; k += 0.045
        return x
    if kind == "skitter":
        d = 1.2; x = np.zeros(int(d * SR)); k = 0.0
        while k < d - 0.1:
            s = int(k * SR); c = bp(noise(0.02), 3000, 9000) * np.exp(-t_(0.02) * 140) * 0.5
            x[s:s + len(c)] += c[:len(x) - s]; k += RNG.uniform(0.03, 0.08)
        return x
    if kind == "flap":
        d = 2.0; x = np.zeros(int(d * SR)); k = 0.0
        while k < d - 0.15:
            s = int(k * SR); c = lp(noise(0.12), 700) * np.sin(np.pi * t_(0.12) / 0.12) * 0.6
            x[s:s + len(c)] += c[:len(x) - s]; k += 0.17
        return x * np.minimum(1, (d - t_(d)) / 0.4)
    if kind in ("scream", "hawk", "yell", "bark", "yip", "chirp", "squawk", "ha", "gasp", "alarm", "howl", "yawn"):
        return voice_sfx(kind)
    if kind == "riser":
        d = 2.65; t = t_(d); u = t / d
        return (sweep_noise(d, 300, 9000) * u ** 2 * 0.9 + tone(d, lambda t: 110 + 600 * (t / d) ** 2, "sq") * u ** 2 * 0.25
                + tone(d, 55) * np.minimum(1, t / 0.5) * 0.35)
    if kind == "swell":
        d = 2.4; t = t_(d); return (tone(d, 196) + tone(d, 247) * 0.7 + tone(d, 294) * 0.6) * np.sin(np.pi * t / d) ** 2 * 0.25
    if kind == "fill":
        d = 2.8; t = t_(d); return tone(d, lambda t: 300 + 800 * (t / d)) * (0.3 + 0.7 * t / d) * 0.3 * np.minimum(1, (d - t) / 0.3)
    if kind == "drain":
        d = 1.0; t = t_(d); return tone(d, lambda t: 900 * np.exp(-t * 2.4) + 100) * np.exp(-t * 2) * 0.4 + bp(noise(d), 300, 2000) * np.exp(-t * 4) * 0.4
    if kind == "coins":
        d = 1.6; x = np.zeros(int(d * SR))
        for k in range(9):
            s = int((k * 0.1 + RNG.uniform(0, 0.04)) * SR); f = RNG.uniform(2400, 4200)
            c = (tone(0.4, f) + tone(0.4, f * 1.5) * 0.4) * np.exp(-t_(0.4) * 12) * 0.4
            x[s:s + len(c)] += c[:len(x) - s]
        return x
    raise KeyError(kind)


def formant(f0, d, formants, jitter=0.0, shape=None):
    """glottal-ish buzz through resonant band-passes -> animal-ish voice."""
    t = t_(d)
    f0t = f0(t) if callable(f0) else np.full(len(t), f0)
    ph = 2 * np.pi * np.cumsum(f0t) / SR
    src = sum(np.sin(h * ph) / h for h in range(1, 14))
    out = np.zeros(len(t))
    for fc, bw, g in formants: out += bp(src, fc - bw, fc + bw) * g
    return out / (np.abs(out).max() + 1e-9)


def voice_sfx(kind):
    if kind == "scream":      # drongo shriek: harsh, rising, with vibrato
        d = 0.85; t = t_(d)
        f = lambda t: 1500 + 1400 * np.sin(np.pi * np.minimum(1, t / 0.5) * 0.5) + 160 * np.sin(2 * np.pi * 32 * t)
        x = tone(d, f, "sq") * 0.5 + tone(d, lambda t: f(t) * 1.5) * 0.25 + noise(d) * 0.12
        return lp(x, 7500) * np.minimum(1, t / 0.03) * np.exp(-np.maximum(0, t - 0.55) * 7) * 0.9
    if kind == "hawk":        # screech
        d = 1.3; t = t_(d)
        f = lambda t: 3300 - 1900 * np.minimum(1, t / 1.1)
        x = tone(d, f) * 0.6 + tone(d, lambda t: f(t) * 2) * 0.2 + noise(d) * 0.1 * np.exp(-t * 3)
        return lp(x, 8500) * np.sin(np.pi * np.minimum(1, t / d)) ** 0.5 * np.exp(-t * 1.8) * 0.85
    if kind in ("bark", "yip", "yell", "alarm"):
        n = 3 if kind == "alarm" else 1
        d = 0.35 + 0.28 * (n - 1) + (0.5 if kind == "alarm" else 0.0); x = np.zeros(int(d * SR))
        for k in range(n):
            f0 = 520 if kind != "yell" else 360; dd = 0.22
            s = int(k * 0.3 * SR)
            c = formant(lambda t: f0 * (1.35 - 1.5 * t) , dd, [(900, 200, 1.0), (2300, 400, 0.6)]) * np.exp(-t_(dd) * 9) * np.minimum(1, t_(dd) / 0.01)
            x[s:s + len(c)] += c
        return x * (0.9 if kind != "yip" else 0.6)
    if kind == "chirp":
        d = 0.9; x = np.zeros(int(d * SR))
        for k in range(5):
            s = int((k * 0.14) * SR); c = tone(0.1, lambda t: 3000 + 1800 * np.sin(2 * np.pi * 6 * t) * 0.5 + 800 * k * 0.1) * np.sin(np.pi * t_(0.1) / 0.1) * 0.4
            x[s:s + len(c)] += c
        return x
    if kind == "squawk":
        d = 0.7; t = t_(d)
        return formant(lambda t: 260 - 90 * t, d, [(700, 200, 1.0), (1500, 300, 0.7)]) * np.minimum(1, t / 0.04) * np.exp(-np.maximum(0, t - 0.3) * 6) * 0.9
    if kind == "ha":
        d = 0.22; t = t_(d)
        return formant(lambda t: 330 - 120 * t, d, [(800, 150, 1.0), (1200, 200, 0.6)]) * (0.25 + 0.75 * np.exp(-t * 18)) * np.minimum(1, t / 0.02) * 0.7
    if kind == "gasp":
        d = 0.45; t = t_(d); return bp(noise(d), 800, 5000) * np.sin(np.pi * t / d) ** 2 * 0.7
    if kind == "howl":
        d = 1.5; t = t_(d); return tone(d, lambda t: 380 + 240 * np.sin(np.pi * t / d)) * np.sin(np.pi * t / d) ** 1.5 * 0.3
    if kind == "yawn":
        d = 1.0; t = t_(d); return formant(lambda t: 200 - 60 * t, d, [(600, 150, 1.0), (1000, 200, 0.5)]) * np.sin(np.pi * t / d) * 0.25
    raise KeyError(kind)


# ============================================================ MUSIC
def pluck(f, d=0.5, bright=1.0):
    t = t_(d)
    return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 14) + 0.25 * np.sin(2 * np.pi * 3.9 * f * t) * np.exp(-t * 20)
            ) * np.exp(-t * 8 / bright) * np.minimum(1, t / 0.004)


def marimba(f, d=0.6):
    t = t_(d)
    return (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t * 30)) * np.exp(-t * 9) * np.minimum(1, t / 0.003)


def music(total):
    out = np.zeros(int((total + 2) * SR))
    bpm = 104; beat = 60 / bpm
    root = [110.0, 110.0, 130.8, 98.0]                       # Am  Am  C  G  (bass roots)
    scale = [220, 261.6, 293.7, 329.6, 392, 440, 523.3, 587.3]  # A minor pentatonic-ish
    riff = [0, 2, 3, 2, 4, 3, 2, 0]
    nb = int(total / beat) + 4
    for b in range(nb):
        t0 = b * beat
        sect = next(((lv, it) for a, e, lv, it in cues.MUSIC if a <= t0 < e), (0.8, 1))
        lv, it = sect
        if lv <= 0: continue
        bar = (b // 4) % 4
        def put(sig, t, g):
            s = int(t * SR); out[s:s + len(sig)] += sig[:len(out) - s] * g * lv
        if it >= 0:                                         # bass pluck on 1 and the 'and' of 2
            if b % 4 == 0: put(pluck(root[bar], 0.55), t0, 0.5)
            if b % 4 == 2 and it >= 1: put(pluck(root[bar] * 1.5, 0.4), t0 + beat * 0.5, 0.35)
        if it >= 1:                                         # marimba riff, eighth notes
            for h in range(2):
                n = riff[(b * 2 + h) % len(riff)]
                if (b * 2 + h) % 8 not in (3, 7) or it >= 3:
                    put(marimba(scale[n] * (1 if bar < 2 else 1.122), 0.5), t0 + h * beat / 2, 0.22 + 0.06 * it)
        if it >= 2:                                         # shaker / off-beat tick
            for h in range(4):
                c = bp(noise(0.05), 4000, 9000) * np.exp(-t_(0.05) * 80)
                put(c, t0 + h * beat / 4, 0.1 * (1.4 if h % 2 else 0.8))
        if it >= 3 and b % 2 == 0:                          # kick on the beat in the payoff
            put(tone(0.25, lambda t: 120 * np.exp(-t * 20) + 45) * np.exp(-t_(0.25) * 12), t0, 0.7)
        if it >= 4:                                         # tension: sparse low pulse
            put(tone(0.3, 55) * np.exp(-t_(0.3) * 6), t0, 0.7)
    # sustained pad under everything (very quiet)
    t = t_(total + 2)
    pad = (np.sin(2 * np.pi * 110 * t) + 0.6 * np.sin(2 * np.pi * 164.8 * t) + 0.4 * np.sin(2 * np.pi * 220 * t)) * 0.035
    lvl = np.interp(t, [a for a, *_ in cues.MUSIC] + [153.7], [lv for _, _, lv, _ in cues.MUSIC] + [0.9])
    out += pad * lvl
    return out


def ambience(total):
    t = t_(total + 2)
    w = lp(noise(total + 2), 700) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t + 1) ** 2) * 0.22
    w += lp(noise(total + 2), 2500) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.11 * t) ** 2) * 0.04
    return w


# ============================================================ MIX
def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ar", str(SR), "-ac", "1", "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def smooth_env(x, win=0.06):
    k = int(win * SR); a = np.abs(x)
    c = np.cumsum(np.insert(a, 0, 0)); e = (c[k:] - c[:-k]) / k
    e = np.concatenate([e, np.zeros(len(x) - len(e))]); return e


def main(vo_path, out_path):
    # 1) VO chain
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", vo_path, "-af",
                    "highpass=f=85,lowpass=f=15000,equalizer=f=220:t=q:w=1.2:g=-2.5,equalizer=f=3200:t=q:w=1.1:g=3,equalizer=f=9000:t=q:w=0.8:g=1.5,"
                    "acompressor=threshold=-21dB:ratio=3.2:attack=4:release=90:makeup=5,deesser=i=0.35,"
                    "aecho=0.85:0.5:38:0.10,alimiter=limit=0.95:level=disabled",
                    "-ar", str(SR), "-ac", "1", "vo_proc.wav"], check=True)
    vo = load("vo_proc.wav"); total = len(vo) / SR
    N = len(vo) + SR
    vo = np.concatenate([vo, np.zeros(N - len(vo))])
    # 2) beds
    mus = music(total)[:N]; amb = ambience(total)[:N]
    # 3) SFX (stereo)
    sL = np.zeros(N); sR = np.zeros(N); cache = {}
    for t, kind, g, pan in cues.CUES:
        if kind not in cache: cache[kind] = sfx(kind)
        x = cache[kind]
        x = x * g * RNG.uniform(0.93, 1.05)
        s = int(max(0, t) * SR); n = min(len(x), N - s)
        if n <= 0: continue
        pl, pr = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
        sL[s:s + n] += x[:n] * pl; sR[s:s + n] += x[:n] * pr
    # 4) sidechain ducking from the VO envelope
    env = smooth_env(vo, 0.08); env = np.convolve(env, np.ones(int(0.18 * SR)) / int(0.18 * SR), "same")
    e = np.clip(env / (np.percentile(env, 95) + 1e-9), 0, 1)
    duck_m = 1 - 0.62 * e; duck_a = 1 - 0.5 * e; duck_s = 1 - 0.28 * e
    big = {"hit", "boom", "stinger", "scratch", "riser", "swell"}
    L = vo * 1.0 + mus * 0.55 * duck_m + amb * 0.9 * duck_a + sL * 0.85 * duck_s
    R = vo * 1.0 + mus * 0.55 * duck_m + amb * 0.9 * duck_a + sR * 0.85 * duck_s
    # gentle stereo width on the music/ambience
    d = int(0.012 * SR); R[d:] = R[d:] * 0.5 + R[:-d] * 0.0 + R[d:] * 0.5
    st = np.stack([L, R], axis=1)
    st = np.tanh(st * 0.9) / 0.9                              # soft clip glue
    pk = np.abs(st).max(); st = st / max(1.0, pk / 0.97)
    pcm = (st * 32767).astype(np.int16)
    open("mix_raw.raw", "wb").write(pcm.tobytes())
    # 5) master: two-pass loudnorm to -14 LUFS / -1.5 dBTP, then a final true-peak safety limiter
    import json, re
    p1 = subprocess.run(["ffmpeg", "-v", "info", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "mix_raw.raw",
                         "-af", "loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = json.loads(re.search(r"\{[^{}]*\}", p1[p1.rindex("input_i") - 20:], re.S).group(0))
    af = (f"loudnorm=I=-14:TP=-1.5:LRA=9:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
          f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample={SR},alimiter=limit=0.82:level=disabled:attack=2:release=40")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "mix_raw.raw", "-af", af, out_path], check=True)
    print("master written", out_path, "%.1fs" % total, "%d cues" % len(cues.CUES))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
