"""Turn a script into a finished short-video soundtrack in the reference style.

    python make_short.py script.txt -o out/my_video          # -> my_video.mp3/.wav/.srt + stems
    python make_short.py script.txt -o out/v1 --video clip.mp4   # also puts the audio on a video
    python make_short.py script.txt -o out/v2 --seed 7       # different (but on-style) variation

Pipeline (every number comes from style_profile.json, picked inside its range per video):
  1. Abel voice (Kokoro), sentence by sentence, speed auto-tuned to ~220 words/min,
     short fixed gaps between sentences, voice starts at 0 s.
  2. Voice chain: high-pass, warm body, presence, air, de-ess, compression, -14.5 LUFS, mono.
  3. Music bed: dark minor-key loop (sub drone + plucks + soft tick), low-passed so it
     never fights the voice, constant level 12-18 dB under the voice, no ducking.
  4. SFX: pops / impacts / shimmers / glitches / ticks / whooshes / thuds placed on the
     exact word (Whisper word timing), 3-5 per 10 s, kept well under the voice.
  5. Master: -14 LUFS integrated, -2 dBTP, 44.1 kHz stereo (near-mono), short tail.
Also writes word-by-word captions (.srt), like the reference videos.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile

import librosa
import numpy as np
import pyloudnorm as pyln
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 44100
KOKORO_SR = 24000


# ---------------------------------------------------------------- helpers
def pick(rng, v):
    return float(rng.uniform(min(v), max(v))) if isinstance(v, list) and len(v) == 2 and all(
        isinstance(x, (int, float)) for x in v) else v


def db2lin(d):
    return 10 ** (d / 20)


def lufs(y):
    return pyln.Meter(SR).integrated_loudness(y)


def set_lufs(y, target):
    return y * db2lin(target - lufs(y))


def ffmpeg(args):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args], check=True)


# ---------------------------------------------------------------- 1. voice
def split_sentences(text):
    text = re.sub(r"\s+", " ", text.strip())
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def make_voice(text, prof, rng, voice_file, model, voices):
    from kokoro_onnx import Kokoro
    tts = Kokoro(model, voices)
    abel = np.load(voice_file).astype(np.float32)
    v = prof["voice"]
    target_wpm = pick(rng, v["words_per_minute"])
    sents = split_sentences(text)
    nwords = len(text.split())

    def render(speed):
        parts = [np.zeros(int(KOKORO_SR * pick(rng, v["start_offset_s"])), np.float32)]
        for i, s in enumerate(sents):
            a, _ = tts.create(s, voice=abel, speed=speed, lang="en-us")
            a, _ = librosa.effects.trim(a, top_db=40)
            parts.append(a.astype(np.float32))
            if i < len(sents) - 1:
                g = v["gap_after_question_s"] if s.endswith("?") else v["gap_after_sentence_s"]
                parts.append(np.zeros(int(KOKORO_SR * pick(rng, g)), np.float32))
        return np.concatenate(parts)

    speed = 1.1
    for _ in range(3):  # tune speed until words/min lands on target
        y = render(speed)
        wpm = nwords / (len(y) / KOKORO_SR) * 60
        if abs(wpm - target_wpm) < 4:
            break
        speed = float(np.clip(speed * target_wpm / wpm, 0.8, 1.5))
    print(f"  voice: {len(sents)} sentences, speed {speed:.2f}, {wpm:.0f} words/min")
    return librosa.resample(y, orig_sr=KOKORO_SR, target_sr=SR)


def process_voice(y, prof, rng, tmp):
    v = prof["voice"]
    c = v["compressor"]
    src, dst = os.path.join(tmp, "v_raw.wav"), os.path.join(tmp, "v_fx.wav")
    sf.write(src, y, SR)
    chain = ",".join([
        f"highpass=f={v['highpass_hz']}:poles=2",
        f"equalizer=f=200:t=q:w=1:g={pick(rng, v['body_boost_db_at_200hz']):.1f}",
        f"equalizer=f=500:t=q:w=1.2:g={pick(rng, v['mud_cut_db_at_500hz']):.1f}",
        f"equalizer=f=3500:t=q:w=1:g={pick(rng, v['presence_boost_db_at_3500hz']):.1f}",
        f"highshelf=f=9000:g={pick(rng, v['air_shelf_db_at_9000hz']):.1f}",
        f"deesser=i={v['deesser_strength']}",
        f"acompressor=threshold={c['threshold_db']}dB:ratio={c['ratio']}:attack={c['attack_ms']}"
        f":release={c['release_ms']}:makeup={c['makeup_db']}dB",
    ])
    ffmpeg(["-i", src, "-af", chain, "-ar", str(SR), dst])
    out, _ = sf.read(dst)
    return set_lufs(out, v["target_lufs"])


# ---------------------------------------------------------------- 2. music bed
NOTE = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}


def midi_hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def pluck(freq, dur, rng):
    """Karplus-Strong plucked string: soft, woody, cartoon-mystery feel."""
    n = int(SR * dur)
    period = max(2, int(SR / freq))
    buf = rng.uniform(-1, 1, period)
    out = np.empty(n)
    for i in range(n):
        out[i] = buf[i % period]
        buf[i % period] = 0.996 * 0.5 * (buf[i % period] + buf[(i + 1) % period])
    return out * np.exp(-np.linspace(0, 4, n))


def make_music(dur, prof, rng):
    m = prof["music"]
    key = m["keys"][rng.integers(len(m["keys"]))]
    root = 36 + NOTE[key.split()[0]]                      # low octave root
    bpm = pick(rng, m["bpm"])
    beat = 60 / bpm
    bar = 4 * beat
    # i - VI - III - VII  (natural minor), one chord per bar, 4-bar loop
    prog = [(0, [0, 3, 7]), (8, [0, 4, 7]), (3, [0, 4, 7]), (10, [0, 4, 7])]
    n = int(SR * (dur + 1))
    sub, plk, tck = np.zeros(n), np.zeros(n), np.zeros(n)
    t_all = np.arange(n) / SR
    pattern = [0, 2, 1, 2, 0, 2, 1, 2]                    # chord-tone order per 8th note
    t = 0.0
    bar_i = 0
    while t < dur + 1:
        off, tri = prog[bar_i % 4]
        # sub drone: sine on chord root, swells over the bar
        s0, s1 = int(t * SR), min(n, int((t + bar) * SR))
        tt = t_all[s0:s1] - t
        f = midi_hz(root + off)
        env = np.sin(np.pi * np.clip(tt / bar, 0, 1)) ** 0.5
        sub[s0:s1] += np.sin(2 * np.pi * f * tt) * env
        # plucks on 8th notes, an octave or two up
        for k in range(8):
            if rng.random() < 0.2:                        # leave some holes, feels less robotic
                continue
            st = t + k * beat / 2
            if int(st * SR) >= n:
                break
            note = root + 24 + off + tri[pattern[k]] + (12 if k == 6 and rng.random() < 0.5 else 0)
            p = pluck(midi_hz(note), beat * 1.5, rng) * (0.8 if k % 2 else 1.0)
            a = int(st * SR)
            b = min(n, a + len(p))
            plk[a:b] += p[: b - a]
        # soft clock tick on quarter notes
        for k in range(4):
            a = int((t + k * beat) * SR)
            L = int(0.015 * SR)
            if a + L < n:
                tck[a:a + L] += rng.uniform(-1, 1, L) * np.exp(-np.linspace(0, 8, L))
        t += bar
        bar_i += 1
    tck = librosa.effects.preemphasis(tck, coef=0.95)
    mix = (sub / (np.abs(sub).max() + 1e-9) * db2lin(pick(rng, m["sub_drone_level_db"]))
           + plk / (np.abs(plk).max() + 1e-9) * db2lin(pick(rng, m["pluck_level_db"]))
           + tck / (np.abs(tck).max() + 1e-9) * db2lin(pick(rng, m["tick_level_db"])))
    # low-pass: reference beds have <1% energy above 2 kHz
    from scipy.signal import butter, sosfilt
    mix = sosfilt(butter(4, pick(rng, m["lowpass_hz"]), "low", fs=SR, output="sos"), mix)
    print(f"  music: {key}, {bpm:.0f} BPM, 4-bar loop")
    return mix[: int(SR * dur)]


# ---------------------------------------------------------------- 3. SFX
def sfx(kind, rng):
    def noise(d):
        return rng.uniform(-1, 1, int(SR * d))

    def env(n, a, r):
        e = np.ones(n)
        A = max(1, int(a * SR))
        e[:A] = np.linspace(0, 1, A)
        e[A:] = np.exp(-np.linspace(0, r, n - A))
        return e

    from scipy.signal import butter, sosfilt
    if kind == "pop":
        d = 0.09; tt = np.arange(int(SR * d)) / SR
        f = 900 * np.exp(-tt * 30) + 350
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(tt), 0.002, 9)
    if kind == "impact":
        d = 0.9; tt = np.arange(int(SR * d)) / SR
        body = np.sin(2 * np.pi * (55 + 60 * np.exp(-tt * 18)) * tt) * env(len(tt), 0.003, 5)
        crack = sosfilt(butter(2, 2500, "low", fs=SR, output="sos"), noise(d)) * env(len(tt), 0.001, 25)
        return body + 0.4 * crack
    if kind == "thud":
        d = 0.35; tt = np.arange(int(SR * d)) / SR
        return np.sin(2 * np.pi * (80 + 70 * np.exp(-tt * 25)) * tt) * env(len(tt), 0.002, 10)
    if kind == "shimmer":
        d = 1.0; tt = np.arange(int(SR * d)) / SR
        y = sum(np.sin(2 * np.pi * f * tt + rng.uniform(0, 6)) for f in (1760, 2217, 2637, 3520))
        return y * env(len(tt), 0.08, 4) * (1 + 0.3 * np.sin(2 * np.pi * 9 * tt))
    if kind == "glitch":
        d = 0.3; y = np.zeros(int(SR * d)); i = 0
        while i < len(y):
            L = int(rng.uniform(0.008, 0.03) * SR)
            if rng.random() < 0.6:
                y[i:i + L] = np.sign(np.sin(2 * np.pi * rng.uniform(300, 2500) * np.arange(min(L, len(y) - i)) / SR))
            i += L
        return y * 0.5
    if kind == "tick":
        L = int(0.025 * SR)
        y = sosfilt(butter(2, [2000, 7000], "band", fs=SR, output="sos"), noise(0.025)) * env(L, 0.0005, 12)
        return np.concatenate([y, np.zeros(int(0.12 * SR)), y * 0.7])
    if kind == "whoosh":
        d = 0.55; n = int(SR * d)
        y = noise(d); out = np.zeros(n); seg = int(0.01 * SR)
        for i in range(0, n, seg):                          # sweeping band-pass
            fc = 400 + 3500 * np.sin(np.pi * i / n)
            out[i:i + seg] = sosfilt(butter(2, [fc * 0.7, fc * 1.3], "band", fs=SR, output="sos"), y[i:i + seg])
        return out * np.sin(np.pi * np.linspace(0, 1, n)) ** 2
    raise ValueError(kind)


def word_times(voice, tmp):
    from faster_whisper import WhisperModel
    model_dir = os.environ.get("WHISPER_MODEL", "/root/whisper-small")
    m = WhisperModel(model_dir, device="cpu", compute_type="int8")
    y16 = librosa.resample(voice.astype(np.float32), orig_sr=SR, target_sr=16000)
    segs, _ = m.transcribe(y16, language="en", word_timestamps=True)
    return [(w.word.strip(), w.start, w.end) for s in segs for w in s.words]


def place_sfx(words, dur, prof, rng):
    s = prof["sfx"]
    lookup = {w: k for k, ws in s["keyword_map"].items() for w in ws}
    budget = int(round(pick(rng, s["density_per_10s"]) * dur / 10))
    cands = []
    for i, (w, st, en) in enumerate(words):
        key = re.sub(r"[^a-z]", "", w.lower())
        if key in lookup:
            cands.append((st, lookup[key], w))
        elif i > 0 and words[i - 1][0][-1:] in ".?!" and rng.random() < s["on_sentence_start_whoosh_chance"]:
            cands.append((max(0, st - 0.25), "whoosh", w))
    rng.shuffle(cands)
    chosen = []
    for c in cands:
        if len(chosen) >= budget:
            break
        if all(abs(c[0] - x[0]) >= s["min_spacing_s"] for x in chosen):
            chosen.append(c)
    # Not enough keywords in this script? Fill up to the measured density:
    # whooshes into new sentences first, then pops on the longest (most "visual") words.
    fill = [(max(0, st - 0.25), "whoosh", w) for i, (w, st, en) in enumerate(words)
            if i > 0 and words[i - 1][0][-1:] in ".?!"]
    fill += sorted(((st, "pop", w) for w, st, en in words if len(re.sub(r"[^a-z]", "", w.lower())) >= 6),
                   key=lambda c: -len(c[2]))
    for c in fill:
        if len(chosen) >= budget:
            break
        if all(abs(c[0] - x[0]) >= s["min_spacing_s"] for x in chosen):
            chosen.append(c)
    return sorted(chosen)


# ---------------------------------------------------------------- 4. master
def master(mix, prof, tmp, out_base):
    ms = prof["master"]
    pre = os.path.join(tmp, "premaster.wav")
    sf.write(pre, mix, SR)
    meas = subprocess.run(["ffmpeg", "-hide_banner", "-i", pre, "-af",
                           f"loudnorm=I={ms['integrated_lufs']}:TP={ms['true_peak_dbtp']}:LRA=11:print_format=json",
                           "-f", "null", "-"], capture_output=True, text=True).stderr
    j = json.loads(meas[meas.rindex("{"):meas.rindex("}") + 1])
    af = (f"loudnorm=I={ms['integrated_lufs']}:TP={ms['true_peak_dbtp']}:LRA=11:measured_I={j['input_i']}"
          f":measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}"
          f":offset={j['target_offset']}:linear=true")
    ffmpeg(["-i", pre, "-af", af, "-ar", str(SR), "-ac", "2", out_base + ".wav"])
    ffmpeg(["-i", out_base + ".wav", "-b:a", "192k", out_base + ".mp3"])


def write_srt(words, path, offset=0.0):
    def ts(t):
        h, r = divmod(max(0, t), 3600)
        m, s = divmod(r, 60)
        return f"{int(h):02}:{int(m):02}:{int(s):02},{int(round((s % 1) * 1000)):03}"
    with open(path, "w", encoding="utf-8") as f:
        for i, (w, st, en) in enumerate(words, 1):
            nxt = words[i][1] if i < len(words) else en + 0.3
            f.write(f"{i}\n{ts(st + offset)} --> {ts(max(en, nxt) + offset)}\n{w}\n\n")


# ---------------------------------------------------------------- main
def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("script", help="text file with the voiceover script (or the text itself)")
    p.add_argument("-o", "--out", default="out/short", help="output path without extension")
    p.add_argument("--seed", type=int, default=None, help="variation seed (default: from the script)")
    p.add_argument("--video", help="optional video to put the finished audio on")
    p.add_argument("--voice", default=os.path.join(HERE, "..", "abel_voice.npy"))
    p.add_argument("--profile", default=os.path.join(HERE, "style_profile.json"))
    p.add_argument("--model", default=os.environ.get("KOKORO_MODEL", "/root/kokoro/kokoro-q8.onnx"))
    p.add_argument("--voices", default=os.environ.get("KOKORO_VOICES", "/root/kokoro/voices.npz"))
    p.add_argument("--music", help="use your own music file instead of the generated bed")
    p.add_argument("--no-sfx", action="store_true")
    a = p.parse_args()

    text = open(a.script, encoding="utf-8").read() if os.path.isfile(a.script) else a.script
    prof = json.load(open(a.profile))
    seed = a.seed if a.seed is not None else int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
    rng = np.random.default_rng(seed)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    print(f"seed {seed}")

    with tempfile.TemporaryDirectory() as tmp:
        voice = process_voice(make_voice(text, prof, rng, a.voice, a.model, a.voices), prof, rng, tmp)
        tail = pick(rng, prof["voice"]["tail_after_last_word_s"])
        dur = len(voice) / SR + tail
        voice = np.pad(voice, (0, int(SR * dur) - len(voice)))
        v_lufs = prof["voice"]["target_lufs"]

        if a.music:
            mus, _ = librosa.load(a.music, sr=SR, mono=True)
            mus = np.tile(mus, int(np.ceil(len(voice) / len(mus))))[: len(voice)]
        else:
            mus = make_music(dur, prof, rng)
        mus = set_lufs(mus, v_lufs - pick(rng, prof["music"]["level_below_voice_db"]))
        fo = int(SR * pick(rng, prof["music"]["fade_out_s"]))
        mus[-fo:] *= np.linspace(1, 0, fo)
        fi = int(SR * prof["music"]["fade_in_s"])
        mus[:fi] *= np.linspace(0, 1, fi)

        words = word_times(voice, tmp)
        fx = np.zeros_like(voice)
        hits = [] if a.no_sfx else place_sfx(words, dur, prof, rng)
        vpk = np.abs(voice).max()
        for t, kind, w in hits:
            s = sfx(kind, rng)
            s = s / (np.abs(s).max() + 1e-9) * vpk * db2lin(-pick(rng, prof["sfx"]["level_below_voice_peak_db"]))
            i = int(t * SR)
            j = min(len(fx), i + len(s))
            fx[i:j] += s[: j - i]
        print(f"  sfx: {len(hits)} -> " + ", ".join(f"{k}@{t:.1f}s('{w}')" for t, k, w in hits))

        mix = voice + mus + fx
        stereo = np.stack([mix, mix], 1)
        master(stereo, prof, tmp, a.out)
        stems = a.out + "_stems"
        os.makedirs(stems, exist_ok=True)
        for name, y in [("voice", voice), ("music", mus), ("sfx", fx)]:
            sf.write(os.path.join(stems, name + ".wav"), y, SR)
        write_srt(words, a.out + ".srt")

    if a.video:
        ffmpeg(["-i", a.video, "-i", a.out + ".wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                "-c:a", "aac", "-b:a", prof["master"]["aac_bitrate"], "-shortest", a.out + ".mp4"])
    print(f"done: {a.out}.mp3 / .wav / .srt ({dur:.1f}s)" + (f" / {a.out}.mp4" if a.video else ""))


if __name__ == "__main__":
    main()
