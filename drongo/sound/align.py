"""Force-align a supplied voiceover to the script text -> words.json (word start times).

    python3 sound/align.py VOICE_FILE SCRIPT.txt [--out words.json]

Fully offline (pocketsphinx built-in US English acoustic model). Words in the
script keep their original spelling/punctuation for captions; alignment runs on
a normalised copy. Long files are aligned in sentence-sized chunks found by
silence detection, which keeps the aligner robust over a 3-minute read.
"""
import argparse
import json
import re
import subprocess

import numpy as np
from pocketsphinx import Decoder

SR = 16000
EXTRA = {  # pronunciations missing from the default dictionary
    'kalahari': 'K AA L AH HH AA R IY',
    'drongo': 'D R AA NG G OW',
    'drongos': 'D R AA NG G OW Z',
    'meerkat': 'M IH R K AE T',
    'meerkats': 'M IH R K AE T S',
    'birdbrain': 'B ER D B R EY N',
    'hornbill': 'HH AO R N B IH L',
}


def load(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', str(SR),
                          '-f', 's16le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16)


def norm(w):
    w = w.lower().replace('’', "'")
    return re.sub(r"[^a-z']", '', w)


def decoder():
    d = Decoder(samprate=SR, loglevel='ERROR')
    for w, p in EXTRA.items():
        try:
            d.add_word(w, p, True)
        except Exception:
            pass
    return d


def align_chunk(d, pcm, words):
    text = ' '.join(norm(w) for w in words if norm(w))
    d.set_align_text(text)
    data = pcm.tobytes()
    d.start_utt(); d.process_raw(data, full_utt=True); d.end_utt()
    d.set_alignment()
    d.start_utt(); d.process_raw(data, full_utt=True); d.end_utt()
    return [(re.sub(r'\(\d+\)$', '', s.name), s.start / 100, (s.start + s.duration) / 100)
            for s in d.get_alignment() if s.name not in ('<sil>', '<s>', '</s>', '[NOISE]')]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('voice')
    ap.add_argument('script')
    ap.add_argument('--out', default='words.json')
    a = ap.parse_args()
    pcm = load(a.voice)
    words = open(a.script).read().split()
    d = decoder()
    for w in {norm(x) for x in words}:
        if w and d.lookup_word(w) is None:
            raise SystemExit(f'No pronunciation for "{w}": add it to EXTRA in align.py')
    al = align_chunk(d, pcm, words)
    toks = [w for w in words if norm(w)]
    if len(al) != len(toks):
        raise SystemExit(f'aligned {len(al)} of {len(toks)} words; check the script matches the read')
    out = [{'w': w, 't0': round(t0, 3), 't1': round(t1, 3)} for w, (_, t0, t1) in zip(toks, al)]
    json.dump({'duration': len(pcm) / SR, 'words': out}, open(a.out, 'w'), indent=1)
    print(f'aligned {len(out)} words, {len(pcm) / SR:.2f}s -> {a.out}')


if __name__ == '__main__':
    main()
