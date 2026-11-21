"""Clean sound design v2.  VO is passed through UNTOUCHED (only resampled + level matched).
No ambience/noise bed. Tonal, sparse SFX; smooth-ducked music; two-pass loudnorm master.
  CUES=<cues module> python3 sound2.py <voiceover.wav> <out_master.wav>"""
import os, sys, math, json, re, subprocess, importlib
import numpy as np

cues = importlib.import_module(os.environ.get("CUES", "cues"))
SR = 48000
RNG = np.random.default_rng(3)


def T(d): return np.arange(int(d * SR)) / SR


# ---------------------------------------------------------------- smooth (ring-free) filters
def _resp(n, fc, kind):
    f = np.fft.rfftfreq(n, 1 / SR); f[0] = 1e-3
    lp = 1 / np.sqrt(1 + (f / fc) ** 8)
    return lp if kind == "lp" else np.sqrt(1 - lp ** 2)


def lp(x, fc): return np.fft.irfft(np.fft.rfft(x) * _resp(len(x), fc, "lp"), len(x))
def hp(x, fc): return np.fft.irfft(np.fft.rfft(x) * _resp(len(x), fc, "hp"), len(x))
def band(x, lo, hi): return hp(lp(x, hi), lo)


def sine(f, d, amp=1.0):
    ph = 2 * np.pi * np.cumsum(f(T(d)) if callable(f) else np.full(int(d * SR), f)) / SR
    return np.sin(ph) * amp


def ad(d, a=0.004, r=0.15):               # smooth attack / exponential release
    t = T(d); return np.minimum(1, t / a) * np.exp(-t / r)



def place(items, total):
    out = np.zeros(int(total * SR))
    for off, sig in items:
        q = int(off * SR); n = min(len(sig), len(out) - q)
        if n > 0: out[q:q + n] += sig[:n]
    return out

def norm(x): return x / (np.abs(x).max() + 1e-9)


# ---------------------------------------------------------------- SFX (all tonal, peak-normalised to 1)
def bell(f, d, r):
    t = T(d); return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * 2.76 * f * t) * np.exp(-t * 3) + 0.2 * np.sin(2 * np.pi * 5.4 * f * t) * np.exp(-t * 6)) * ad(d, 0.002, r)


SFX = {
    "pop": lambda: norm(sine(lambda t: 320 + 520 * np.exp(-t * 45), 0.14) * ad(0.14, 0.002, 0.04)),
    "ting": lambda: norm(bell(1760, 1.1, 0.35)),
    "ding": lambda: norm(bell(988, 0.9, 0.3)),
    "sparkle": lambda: norm(place([(k * 0.07, bell(f, 0.5, 0.12)) for k, f in enumerate((1568, 1976, 2349, 2794, 3136))], 1.0)),
    "tick": lambda: norm(sine(2600, 0.04) * ad(0.04, 0.001, 0.008)),
    "click": lambda: norm(sine(lambda t: 900 + 500 * np.exp(-t * 80), 0.06) * ad(0.06, 0.001, 0.012)),
    "thud": lambda: norm(sine(lambda t: 48 + 90 * np.exp(-t * 22), 0.5) * ad(0.5, 0.003, 0.12)),
    "hit": lambda: norm(sine(lambda t: 38 + 110 * np.exp(-t * 16), 1.2) * ad(1.2, 0.002, 0.3) * 1.0 + 0.25 * lp(RNG.standard_normal(int(1.2 * SR)), 1200) * ad(1.2, 0.001, 0.02)),
    "boom": lambda: norm(sine(lambda t: 30 + 60 * np.exp(-t * 3), 2.2) * ad(2.2, 0.004, 0.6) + 0.3 * sine(lambda t: 70 * np.exp(-t * 1.2) + 25, 2.2) * ad(2.2, 0.004, 0.9)),
    "stamp": lambda: norm(sine(lambda t: 46 + 100 * np.exp(-t * 25), 0.6) * ad(0.6, 0.002, 0.14) + 0.3 * lp(RNG.standard_normal(int(0.6 * SR)), 2500) * ad(0.6, 0.0005, 0.01)),
    "crack": lambda: norm(0.6 * band(RNG.standard_normal(int(0.25 * SR)), 1800, 5000) * ad(0.25, 0.0005, 0.015) + sine(lambda t: 190 * np.exp(-t * 30) + 70, 0.25) * ad(0.25, 0.001, 0.05) + 0.4 * bell(2400, 0.25, 0.03)),
    "stinger": lambda: norm((sine(293.7, 1.0) + sine(349.2, 1.0) * 0.8 + sine(440, 1.0) * 0.7 + sine(146.8, 1.0)) * ad(1.0, 0.01, 0.35)),
    "riser": lambda: norm(sine(lambda t: 110 * (1 + 7 * (t / 2.6) ** 2), 2.6) * (T(2.6) / 2.6) ** 2 + 0.2 * lp(RNG.standard_normal(int(2.6 * SR)), 3500) * (T(2.6) / 2.6) ** 3),
    "swell": lambda: norm((sine(196, 2.4) + sine(247, 2.4) * 0.7 + sine(294, 2.4) * 0.6) * np.sin(np.pi * T(2.4) / 2.4) ** 2),
    "fill": lambda: norm(sine(lambda t: 300 + 520 * (t / 1.6), 1.6) * np.minimum(1, T(1.6) / 0.1) * np.minimum(1, (1.6 - T(1.6)) / 0.2)),
    "sadslide": lambda: norm(sine(lambda t: 392 * np.exp(-t * 0.55) + 6 * np.sin(2 * np.pi * 6 * t), 1.0) * ad(1.0, 0.02, 0.5)),
    "boing": lambda: norm(sine(lambda t: 280 + 200 * np.sin(2 * np.pi * 8 * t) * np.exp(-t * 6) + 120 * np.exp(-t * 4), 0.5) * ad(0.5, 0.004, 0.15)),
    "nope": lambda: norm(place([(0.0, sine(620, 0.1) * ad(0.1, 0.002, 0.05)), (0.1, sine(440, 0.18) * ad(0.18, 0.002, 0.08))], 0.3)),
    "scratch": lambda: norm(sine(lambda t: 500 + 1100 * np.abs(np.sin(2 * np.pi * 3.2 * t)), 0.45) * ad(0.45, 0.004, 0.25)),
    "coins": lambda: norm(place([(k * 0.09, bell(f, 0.35, 0.09)) for k, f in enumerate((2637, 3136, 2349, 3520))], 0.9)),
    "pluck": lambda: norm(sine(lambda t: 1100 * np.exp(-t * 18) + 380, 0.4) * ad(0.4, 0.002, 0.07)),
    "dive": lambda: norm(sine(lambda t: 320 * np.exp(-t * 5) + 50, 0.7) * ad(0.7, 0.004, 0.22)),
    "drain": lambda: norm(sine(lambda t: 800 * np.exp(-t * 2.2) + 90, 0.9) * ad(0.9, 0.01, 0.4)),
    "alert": lambda: norm(sine(lambda t: 1300 + 1500 * np.minimum(1, t / 0.18) + 80 * np.sin(2 * np.pi * 22 * t), 0.5) * ad(0.5, 0.006, 0.2)),
    "alarm": lambda: norm(place([(k * 0.2, sine(lambda t: 1000 - 250 * t / 0.1, 0.1) * ad(0.1, 0.003, 0.05)) for k in range(3)], 0.9)),
    "chirp": lambda: norm(place([(k * 0.13, sine(lambda t: 2600 + 1400 * t / 0.09, 0.09) * np.sin(np.pi * T(0.09) / 0.09)) for k in range(4)], 0.8)),
    "cuckoo": lambda: norm(np.concatenate([(np.sin(2 * np.pi * 780 * T(0.24)) + 0.2 * np.sin(2 * np.pi * 1560 * T(0.24))) * np.sin(np.pi * T(0.24) / 0.24) ** 0.8, np.zeros(int(0.06 * SR)),
                                            (np.sin(2 * np.pi * 620 * T(0.3)) + 0.2 * np.sin(2 * np.pi * 1240 * T(0.3))) * np.sin(np.pi * T(0.3) / 0.3) ** 0.8])),
}

# old cue kind -> (new kind, gain, peak dBFS)  ; anything not listed is DROPPED (noise textures, whooshes, synth voices)
MAP = {
    "stinger": ("stinger", 1.0, -13), "hit": ("hit", 1.0, -9), "boom": ("boom", 1.0, -8), "pop": ("pop", 0.8, -21), "ting": ("ting", 0.8, -22),
    "ding": ("ding", 0.8, -22), "sparkle": ("sparkle", 0.7, -24), "thud": ("thud", 0.8, -14), "stamp": ("stamp", 1.0, -11), "cuckoo": ("cuckoo", 0.9, -20),
    "riser": ("riser", 1.0, -17), "crack": ("crack", 1.0, -15), "click": ("click", 0.7, -24), "sadslide": ("sadslide", 0.6, -24), "scratch": ("scratch", 0.7, -20),
    "coins": ("coins", 0.6, -25), "tick": ("tick", 0.5, -27), "pluck": ("pluck", 0.8, -21), "boing": ("boing", 0.5, -25), "scream": ("alert", 0.9, -21),
    "alarm": ("alarm", 0.9, -20), "chirp": ("chirp", 0.6, -26), "buzz": ("nope", 0.6, -24), "fill": ("fill", 0.5, -27), "dive": ("dive", 0.8, -17),
    "swell": ("swell", 0.6, -26), "drain": ("drain", 0.5, -25), "bark": ("pop", 0.9, -20),
}


DROP = {"boing", "sadslide", "click", "tick", "buzz", "fill", "drain", "swell", "coins", "bark"}


# ---------------------------------------------------------------- music (clean: pad + sine bass + soft arpeggio, no noise)
PROG = {"savanna": (100, [(57, [57, 60, 64]), (53, [53, 57, 60]), (48, [48, 52, 55]), (55, [55, 59, 62])]),
        "noir": (88, [(50, [50, 53, 57]), (55, [55, 58, 62]), (57, [57, 61, 64]), (50, [50, 53, 57])])}


def mf(m): return 440.0 * 2 ** ((m - 69) / 12)


def pluck_note(f, d=0.5):
    t = T(d); return (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 12)) * np.exp(-t * 7) * np.minimum(1, t / 0.004)


def music(total):
    style = "noir" if getattr(cues, "STYLE", "") == "noir" else "savanna"
    bpm, prog = PROG[style]; beat = 60 / bpm; bar = 4 * beat
    N = int((total + 3) * SR)
    pad, bass, arp, pulse = (np.zeros(N) for _ in range(4))
    def add(buf, q, sig, g=1.0):
        n = min(len(sig), N - q)
        if n > 0 and q >= 0: buf[q:q + n] += sig[:n] * g
    nb = int(total / bar) + 2
    for b in range(nb):
        root, tones = prog[b % 4]; t0 = b * bar
        s = int(t0 * SR); n = int((bar + 0.6) * SR)
        tt = np.arange(n) / SR
        env = np.minimum(1, tt / 0.5) * np.minimum(1, (bar + 0.6 - tt) / 0.6)
        for m in tones:                                                     # soft detuned pad
            for det in (0.997, 1.003):
                seg = (np.sin(2 * np.pi * mf(m) * det * tt) + 0.3 * np.sin(2 * np.pi * 2 * mf(m) * det * tt)) * env
                add(pad, s, seg, 0.12)
        for k in range(4):                                                  # bass on each beat (softer on 2 and 4)
            bn = sine(mf(root - 24 + (0 if k % 2 == 0 else 7 if style == "noir" else 0)), beat * 0.95) * ad(beat * 0.95, 0.01, 0.35)
            q = int((t0 + k * beat) * SR); add(bass, q, bn, 0.5 if k % 2 == 0 else 0.3)
        for k in range(8):                                                  # arpeggio, eighth notes
            m = tones[[0, 1, 2, 1, 2, 1, 0, 2][k] % 3] + 12
            pn = pluck_note(mf(m), 0.45); q = int((t0 + k * beat / 2) * SR)
            add(arp, q, pn, 0.35 if k % 2 == 0 else 0.22)
        pk = sine(lambda t: 52 + 60 * np.exp(-t * 30), 0.3) * ad(0.3, 0.002, 0.08); q = int(t0 * SR)
        add(pulse, q, pk, 0.7)
    # smooth section gates (crossfade ~0.6 s) from cues.MUSIC: (start, end, level, intensity)
    t = np.arange(N) / SR
    def curve(fn):
        c = np.zeros(N)
        for a, e, lv, it in cues.MUSIC: c[(t >= a) & (t < e)] = fn(lv, it)
        k = int(0.6 * SR); return np.convolve(np.pad(c, (k, k), mode="edge"), np.ones(k) / k, "same")[k:-k]
    g_pad = curve(lambda lv, it: lv if it >= 0 else 0)
    g_bass = curve(lambda lv, it: lv if it >= 1 else 0)
    g_arp = curve(lambda lv, it: lv if it >= 1 else 0)
    g_pulse = curve(lambda lv, it: lv if it in (3, 4) else 0)
    m = pad * g_pad * 0.9 + bass * g_bass * 1.0 + arp * g_arp * 0.9 + pulse * g_pulse * 0.8
    m = lp(m, 5500)
    return m - 0.45 * band(m, 900, 3800)           # carve the voice range


# ---------------------------------------------------------------- helpers
def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-af", "aresample=resampler=soxr:precision=28", "-ar", str(SR), "-ac", "1", "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def lufs(x, stereo=False):
    a = np.stack([x, x], 1) if x.ndim == 1 else x
    pcm = (np.clip(a, -1, 1) * 32767).astype("<i2").tobytes()
    r = subprocess.run(["ffmpeg", "-v", "info", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "-", "-af", "ebur128=peak=true", "-f", "null", "-"], input=pcm, capture_output=True).stderr.decode()
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", r); p = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r)
    return float(m[-1]), float(p[-1]) if p else None


def speech_gate(vo):
    k = int(0.02 * SR); e = np.sqrt(np.convolve(vo ** 2, np.ones(k) / k, "same"))
    on = (e > 10 ** (-42 / 20)).astype(float)
    # fast attack, slow release smoothing
    out = np.zeros_like(on); a = 1 - math.exp(-1 / (0.03 * SR)); r = 1 - math.exp(-1 / (0.35 * SR)); y = 0.0
    for i in range(0, len(on), 1):
        pass
    # vectorised via exponential smoothing in chunks (release dominated)
    y = 0.0; ds = 48
    xs = on[::ds]; ys = np.zeros_like(xs)
    for i, v in enumerate(xs):
        c = (1 - math.exp(-ds / (0.03 * SR))) if v > y else (1 - math.exp(-ds / (0.35 * SR)))
        y += (v - y) * c; ys[i] = y
    return np.interp(np.arange(len(on)), np.arange(0, len(on), ds), ys)


def main(vo_path, out_path):
    vo = load(vo_path)
    vo = vo - vo.mean()
    total = len(vo) / SR; N = len(vo) + int(1.0 * SR)
    vo = np.concatenate([vo, np.zeros(N - len(vo))])
    vo_l, vo_pk = lufs(vo)
    g_vo = 10 ** ((-16 - vo_l) / 20)                         # level-match only: no dynamics processing
    vo *= g_vo
    gate = speech_gate(vo)
    # music: set integrated level 13 dB under the voice, then duck 9 dB under speech
    mus = music(total)[:N]
    ml, _ = lufs(mus[: int(total * SR)])
    mus *= 10 ** ((-16 - 13 - ml) / 20)
    mus *= 10 ** (-(9 * gate) / 20)
    mus *= np.minimum(1, (N / SR - np.arange(N) / SR) / 1.0)            # tail fade
    # sfx
    sfx_bus = np.zeros(N); used = []; last = {}
    prio = {"hit": 3, "boom": 3, "stamp": 3, "stinger": 3, "riser": 2, "cuckoo": 2, "crack": 2}
    kept = 0
    for t0, kind, g, pan in sorted(cues.CUES):
        if kind not in MAP or kind in DROP: continue
        nk, gm, pk = MAP[kind]
        if t0 - last.get(nk, -9) < 0.6: continue                       # no machine-gunning
        if any(abs(t0 - u) < 0.18 and prio.get(nk, 0) < 3 for u in used): continue
        x = SFX[nk]()
        x = x / (np.abs(x).max() + 1e-9) * 10 ** (pk / 20) * min(1.0, g * gm + 0.15)
        s = int(max(0, t0) * SR); n = min(len(x), N - s)
        if n <= 0: continue
        near = gate[min(N - 1, s)]
        x = x[:n] * (10 ** (-3.0 * near / 20))                          # a touch lower over speech
        sfx_bus[s:s + n] += x; used.append(t0); last[nk] = t0; kept += 1
    mix = vo + mus + sfx_bus
    pk = np.abs(mix).max(); print("pre-master peak %.2f dBFS" % (20 * math.log10(pk)))
    st = np.stack([mix, mix], 1)
    pcm = (np.clip(st, -1, 1) * 32767).astype("<i2")
    open("mix2_raw.raw", "wb").write(pcm.tobytes())
    p1 = subprocess.run(["ffmpeg", "-v", "info", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "mix2_raw.raw", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = json.loads(re.search(r"\{[^{}]*\}", p1[p1.rindex("input_i") - 20:], re.S).group(0))
    af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
          f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample={SR}")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "mix2_raw.raw", "-af", af, out_path], check=True)
    # ---- verification report
    fin, fpk = lufs(load_st(out_path))
    sp = gate > 0.5; gp = gate < 0.05
    def rms(x, m): return 20 * math.log10(np.sqrt(np.mean(x[m] ** 2)) + 1e-12)
    hf = lambda x: 20 * math.log10(np.sqrt(np.mean(hp(x[: SR * 20], 9000) ** 2)) + 1e-12)
    print(f"VO loudness before/after level-match: {vo_l:.1f} -> -16.0 LUFS (gain {20 * math.log10(g_vo):+.1f} dB, no other processing)")
    print(f"music under speech: {rms(mus, sp) - rms(vo, sp):+.1f} dB vs voice | music in gaps: {rms(mus, gp):.1f} dBFS | sfx kept: {kept} (was {len(cues.CUES)} cues)")
    print(f"mix content >9 kHz (noise check, first 20 s): {hf(mix):.1f} dBFS vs voice {hf(vo):.1f} dBFS")
    print(f"FINAL: {fin:.1f} LUFS, true peak {fpk} dBFS")


def load_st(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ar", str(SR), "-ac", "2", "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64).reshape(-1, 2)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
