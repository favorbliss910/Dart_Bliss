"""Reusable sound-design library: synthesized SFX, music cue placement, VO-keyed ducking,
bus mixing and loudness finishing. Import it from a per-project cue sheet (see example_jupiter/mix.py).
All buffers are float32 stereo arrays at SR=48 kHz, shape (n, 2)."""
import subprocess, math, wave, json, re
import numpy as np
SR = 48000
rng = np.random.default_rng(1)

def load(path, filt=None):
    cmd = ['ffmpeg', '-v', 'error', '-i', path]
    if filt: cmd += ['-af', filt]
    cmd += ['-ac', '2', '-ar', str(SR), '-f', 'f32le', '-']
    a = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32)
    return a.reshape(-1, 2).copy()

def db(x): return 10 ** (x / 20)

def fade_env(n, fin, fout):
    e = np.ones(n, np.float32)
    fi, fo = int(fin * SR), int(fout * SR)
    if fi > 0: e[:fi] = np.linspace(0, 1, fi) ** 2 if fi <= n else e[:fi]
    if fo > 0: e[-fo:] *= np.linspace(1, 0, fo) ** 1.5
    return e

def place(bus, clip, t0, gain=1.0):
    i0 = int(t0 * SR)
    if i0 < 0: clip = clip[-i0:]; i0 = 0
    n = min(len(clip), len(bus) - i0)
    if n > 0: bus[i0:i0 + n] += clip[:n] * gain


# simple filters via FFT (offline, fine for clips)
def fft_filter(x, lo=None, hi=None):
    n = len(x); X = np.fft.rfft(x, axis=0); f = np.fft.rfftfreq(n, 1 / SR)
    m = np.ones_like(f)
    if lo: m *= 1 / (1 + (lo / np.maximum(f, 1)) ** 4)
    if hi: m *= 1 / (1 + (f / hi) ** 4)
    return np.fft.irfft(X * (m[:, None] if x.ndim == 2 else m), n=n, axis=0).astype(np.float32)

def noise(dur, st=True):
    n = int(dur * SR)
    return rng.standard_normal((n, 2) if st else n).astype(np.float32)

def st(x): return np.stack([x, x], 1)

def tvec(dur): return np.arange(int(dur * SR)) / SR

# ------------------------------------------------------------------ SFX generators
def boom(dur=3.0, f0=70, f1=28, amp=1.0, noise_amt=.5, hi=900):
    t = tvec(dur)
    f = f1 + (f0 - f1) * np.exp(-t * 3)
    ph = 2 * np.pi * np.cumsum(f) / SR
    sub = np.sin(ph) * np.exp(-t * 1.6)
    nz = fft_filter(noise(dur, False), hi=hi) * np.exp(-t * 6) * noise_amt
    x = (sub + nz) * amp
    x[:200] *= np.linspace(0, 1, 200)
    return st(x.astype(np.float32))

def whoosh(dur=0.6, lo=300, hi=4000, amp=.5, peak=.55):
    t = tvec(dur)
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2
    env = np.where(t / dur < peak, (t / dur / peak) ** 2, ((1 - t / dur) / (1 - peak)) ** 1.5)
    n = fft_filter(noise(dur), lo=lo, hi=hi)
    n /= np.abs(n).max() + 1e-9
    pan = np.stack([1 - .3 * t / dur, .7 + .3 * t / dur], 1)
    return (n * env[:, None] * pan * amp).astype(np.float32)

def riser(dur=4.0, amp=.35):
    t = tvec(dur)
    f = 120 * (2 ** (3 * t / dur))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * .5 + np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR) * .3
    n = fft_filter(noise(dur, False), lo=800, hi=9000) * .6
    env = (t / dur) ** 2.2
    x = (s + n * (t / dur)) * env * amp
    x[-400:] *= np.linspace(1, 0, 400)
    return st(x.astype(np.float32))

def blip(f=1200, dur=.09, amp=.25):
    t = tvec(dur)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t * 40) * amp
    return st(x.astype(np.float32))

def ui_pop(amp=.18):
    return blip(1800, .06, amp) + np.pad(blip(2400, .05, amp * .6), ((int(.03 * SR), 0), (0, 0)))[:int(.06 * SR)]

def alarm(dur=1.2, amp=.18):
    t = tvec(dur)
    f = np.where((t * 4) % 1 < .5, 880, 660)
    x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * .3 + np.sin(2 * np.pi * np.cumsum(f) / SR) * .7
    x = fft_filter(x, hi=3000) * amp * fade_env(len(t), .02, .1)
    return st(x.astype(np.float32))

def tone(f, dur, amp, fin=.01, fout=.2):
    t = tvec(dur)
    return st((np.sin(2 * np.pi * f * t) * amp * fade_env(len(t), fin, fout)).astype(np.float32))

def static(dur, amp=.25):
    n = fft_filter(noise(dur), lo=1500, hi=8000)
    n /= np.abs(n).max()
    gate = (rng.random(int(dur * 60)) > .3).repeat(SR // 60)[:len(n)]
    gate = np.pad(gate, (0, len(n) - len(gate)))
    return (n * gate[:, None] * amp * fade_env(len(n), .005, .1)[:, None]).astype(np.float32)

def rumble(dur, amp, lo=25, hi=220, mod=.5):
    t = tvec(dur)
    n = fft_filter(noise(dur), lo=lo, hi=hi); n /= np.abs(n).max()
    m = 1 + mod * np.sin(2 * np.pi * .7 * t)[:, None]
    return (n * m * amp).astype(np.float32)

def creak(dur=1.4, amp=.3, f0=90):
    t = tvec(dur)
    f = f0 * (1 + .25 * np.sin(2 * np.pi * .6 * t)) * (1 - .2 * t / dur)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = (np.sin(ph) + .5 * np.sin(2 * ph * 1.01) + .3 * np.sin(3.7 * ph)) * (1 + .5 * np.sin(2 * np.pi * 23 * t))
    x = x * fade_env(len(t), .08, .5) * amp
    return st(fft_filter(x.astype(np.float32), lo=60, hi=1500))

def shimmer(dur, amp=.12):
    t = tvec(dur); x = np.zeros(len(t), np.float32)
    for f in (1760, 2217, 2637, 3520, 4186):
        x += np.sin(2 * np.pi * f * t + rng.random() * 6) * (0.5 + .5 * np.sin(2 * np.pi * rng.uniform(.3, 1.2) * t))
    x = x / 5 * amp * fade_env(len(t), dur * .3, dur * .4)
    return np.stack([x, np.roll(x, 900)], 1).astype(np.float32)

def crackle(dur, amp=.2, rate=25):
    n = int(dur * SR); x = np.zeros((n, 2), np.float32)
    k = int(rate * dur)
    for i in range(k):
        p = rng.integers(0, n - 2000); L = rng.integers(200, 1500)
        b = fft_filter(rng.standard_normal(L).astype(np.float32), lo=2000, hi=12000) * np.exp(-np.arange(L) / (L / 5))
        pan = rng.random()
        x[p:p + L, 0] += b * (1 - pan) * amp; x[p:p + L, 1] += b * pan * amp
    return x * fade_env(n, .5, .8)[:, None]

def hum(dur, amp=.12, f=55):
    t = tvec(dur)
    x = (np.sin(2 * np.pi * f * t) + .5 * np.sin(2 * np.pi * 2 * f * t + 1) + .25 * np.sin(2 * np.pi * 3.01 * f * t)) * (1 + .3 * np.sin(2 * np.pi * .25 * t))
    return st((x * amp * fade_env(len(t), 1.5, 2.0) / 1.75).astype(np.float32))

def drone(dur, amp=.15, fs=(55, 82.4, 110)):
    t = tvec(dur); x = np.zeros(len(t))
    for i, f in enumerate(fs):
        x += np.sin(2 * np.pi * f * t * (1 + .002 * np.sin(2 * np.pi * .1 * t + i)))
    x = x / len(fs)
    n = fft_filter(noise(dur, False), lo=100, hi=600) * .15
    y = (x + n) * amp * fade_env(len(t), 2.5, 3.0)
    return np.stack([y, np.roll(y, 1200)], 1).astype(np.float32)

def wind(dur, amp=.12, hi=1200):
    t = tvec(dur)
    n = fft_filter(noise(dur), lo=150, hi=hi); n /= np.abs(n).max()
    m = (0.6 + .4 * np.sin(2 * np.pi * .13 * t) * np.sin(2 * np.pi * .07 * t + 1))[:, None]
    return (n * m * amp * fade_env(len(t), 1.0, 1.5)[:, None]).astype(np.float32)

def chute_snap(amp=.4):
    w = whoosh(.7, 400, 6000, amp * .7, .8)
    t = tvec(.25); snap = fft_filter(noise(.25, False), lo=200, hi=3000) * np.exp(-t * 25) * amp
    out = np.zeros((int(.95 * SR), 2), np.float32)
    out[:len(w)] += w; out[int(.68 * SR):int(.68 * SR) + len(snap)] += st(snap.astype(np.float32))
    return out

def thud(amp=.25):
    return boom(.5, 140, 60, amp, .3, hi=600)


# ------------------------------------------------------------------ mixing helpers
def cue(bus, track, t_prog, t_track, dur, fin, fout, gain_db):
    """Place a music excerpt: track[t_track : t_track+dur] at program time t_prog, with fades (s) and gain (dB)."""
    seg = track[int(t_track * SR):int((t_track + dur) * SR)]
    seg = seg * fade_env(len(seg), fin, fout)[:, None]
    place(bus, seg, t_prog, db(gain_db))

def music_energy(path, step=4.0):
    """Print RMS dB every `step` s - use it to find each track's intro / build / peak / outro."""
    a = load(path).mean(1); w = int(SR * step); n = len(a) // w
    r = 20 * np.log10(np.sqrt((a[:n * w].reshape(n, w) ** 2).mean(1)) + 1e-9)
    return [(round(i * step, 1), round(float(d), 1)) for i, d in enumerate(r)]

def duck_envelope(voice, depth=.62, attack=.03, release=.45):
    """Gain curve (n,) that dips music under speech. depth .62 = about -8.4 dB at full speech."""
    mono = np.abs(voice[:, 0]); win = int(.02 * SR)
    env = np.sqrt(np.convolve(mono ** 2, np.ones(win) / win, 'same'))
    env = np.clip(env / (np.percentile(env[env > 1e-4], 90) + 1e-9), 0, 1)
    sm = np.empty_like(env); a_att = math.exp(-1 / (attack * SR)); a_rel = math.exp(-1 / (release * SR)); s = 0.0
    step = 48
    for i in range(0, len(env), step):
        v = env[i]; a = a_att if v > s else a_rel
        s = a ** step * s + (1 - a ** step) * v
        sm[i:i + step] = s
    return np.clip(sm * 1.4, 0, 1), depth

VO_CHAIN = 'highpass=f=70,equalizer=f=3000:t=q:w=1.2:g=1.5,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2'

def mixdown(voice, music, sfx, amb, out_wav, music_db=-9, sfx_db=-3, amb_db=-4, duck_depth=.62, amb_duck=.45):
    env, _ = duck_envelope(voice, duck_depth)
    music = music * (1 - duck_depth * env)[:, None]
    amb = amb * (1 - amb_duck * env)[:, None]
    mix = voice + music * db(music_db) + sfx * db(sfx_db) + amb * db(amb_db)
    pcm = (np.clip(mix / max(1.0, np.abs(mix).max()), -1, 1) * 32767).astype(np.int16)
    with wave.open(out_wav, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    return out_wav

def integrated_lufs(path):
    out = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    tail = out[out.rfind('Summary:'):]
    I = float(re.search(r'I:\s+(-?[\d.]+) LUFS', tail).group(1))
    tp = float(re.search(r'Peak:\s+(-?[\d.]+) dBFS', tail).group(1))
    return I, tp

def finish(raw_wav, out_wav, target=-14.0, limit_db=-2.0):
    """Static gain to the target + brick-wall limiter. NOT loudnorm dynamic mode: that would
    lift deliberate silences and flatten the dramatic arc."""
    I, _ = integrated_lufs(raw_wav)
    g = target - I
    lim = 10 ** (limit_db / 20)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw_wav, '-af',
                    f'volume={g:.2f}dB,alimiter=limit={lim:.3f}:attack=3:release=120:level=false,aresample=48000',
                    '-c:a', 'pcm_s16le', out_wav], check=True)
    return integrated_lufs(out_wav)
