"""Word-level transcription of the voiceover (offline, NVIDIA Parakeet TDT 0.6B v2 via sherpa-onnx).
Usage: python3 transcribe.py <voiceover.(mp3|wav)> <model_dir> <project_dir>
Writes project_dir/tokens.json, words.json ([word, start_s]) and words.txt (10 words per line with times).
Model: https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8.tar.bz2
"""
import sherpa_onnx, numpy as np, json, sys, os, subprocess
src, M, proj = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(proj, exist_ok=True)
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-ac', '1', '-ar', '16000', '-f', 's16le', '-'], capture_output=True, check=True).stdout
a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
sr = 16000
rec = sherpa_onnx.OfflineRecognizer.from_transducer(
    encoder=f"{M}/encoder.int8.onnx", decoder=f"{M}/decoder.int8.onnx", joiner=f"{M}/joiner.int8.onnx",
    tokens=f"{M}/tokens.txt", model_type="nemo_transducer", num_threads=os.cpu_count() or 4)
# Split into ~10-26 s chunks at the quietest 200 ms window (never mid-word).
fl = 320; n = len(a) // fl
e = np.sqrt((a[:n * fl].reshape(n, fl) ** 2).mean(1) + 1e-12)
cuts = [0]; pos = 0
while True:
    if pos + int(18 / 0.02) >= n: break
    lo, hi = pos + int(10 / 0.02), min(n, pos + int(26 / 0.02))
    seg = np.convolve(e[lo:hi], np.ones(10), 'valid'); k = lo + int(seg.argmin()) + 5
    cuts.append(k); pos = k
cuts.append(n)
tokens = []
for i in range(len(cuts) - 1):
    s, t = cuts[i] * fl, cuts[i + 1] * fl
    st = rec.create_stream(); st.accept_waveform(sr, a[s:t]); rec.decode_stream(st)
    r = st.result; off = s / sr
    tokens += [[tok, round(ts + off, 3)] for tok, ts in zip(r.tokens, r.timestamps)]
    print(f"{off:7.2f} {r.text}", flush=True)
json.dump(tokens, open(os.path.join(proj, 'tokens.json'), 'w'))
words, cur = [], None
for tok, ts in tokens:            # tokens starting with a space begin a new word
    if tok.startswith(' ') or cur is None:
        if cur: words.append(cur)
        cur = [tok.strip(), ts]
    else:
        cur[0] += tok
words.append(cur)
json.dump(words, open(os.path.join(proj, 'words.json'), 'w'))
with open(os.path.join(proj, 'words.txt'), 'w') as f:
    for i in range(0, len(words), 10):
        f.write(f"{words[i][1]:7.2f} " + " ".join(w for w, _ in words[i:i + 10]) + "\n")
print(len(words), 'words')
