"""Generate narration with Kokoro, phrase by phrase, and emit word timings."""
import json, sys, re, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
VOICE = sys.argv[1] if len(sys.argv) > 1 else "am_michael"
SPEED = float(sys.argv[2]) if len(sys.argv) > 2 else 1.08
SEGS = json.load(open("script_sample.json"))
k = Kokoro("/opt/tts/kokoro-v1.0.onnx", "/opt/tts/voices-v1.0.bin")
SR = 24000
out, words, t = [], [], 0.25
out.append(np.zeros(int(SR * 0.25), np.float32))
for seg in SEGS:
    audio, sr = k.create(seg["text"], voice=VOICE, speed=seg.get("speed", SPEED), lang="en-us")
    # trim leading/trailing silence
    a = np.abs(audio); thr = 0.01
    nz = np.where(a > thr)[0]
    audio = audio[max(0, nz[0] - 240): nz[-1] + 480]
    dur = len(audio) / SR
    toks = seg["text"].split()
    # weight words by syllable-ish length, punctuation adds a small pause weight
    wts = []
    for w in toks:
        core = re.sub(r"[^A-Za-z']", "", w)
        v = max(1, len(re.findall(r"[aeiouy]+", core.lower())))
        wts.append(v * 1.0 + len(core) * 0.12 + (0.9 if re.search(r"[,.!?]$", w) else 0))
    tot = sum(wts); acc = 0
    for w, wt in zip(toks, wts):
        words.append({"w": w, "t0": round(t + dur * acc / tot, 3)})
        acc += wt
    out.append(audio.astype(np.float32)); t += dur
    p = seg.get("pause", 0.2)
    out.append(np.zeros(int(SR * p), np.float32)); t += p
    print(f"{dur:5.2f}s  {seg['text'][:60]}")
wav = np.concatenate(out)
sf.write("voice.wav", wav, SR)
json.dump({"duration": len(wav) / SR, "words": words}, open("words.json", "w"), indent=1)
print("total", len(wav) / SR)
