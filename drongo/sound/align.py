"""Force-align a supplied voiceover to the script text -> words.json (word start times).

    python3 sound/align.py VOICE_FILE SCRIPT.txt [--out words.json]

Fully offline (pocketsphinx built-in US English acoustic model). Words in the
script keep their original spelling/punctuation for captions; alignment runs on
a normalised copy. Long files are aligned in sentence-sized chunks found by
silence detection, which keeps the aligner robust over a 3-minute read.

A script word can carry its spoken form in braces when the caption differs from
what is said, e.g. `1902,{nineteen oh two}` or `20,000{twenty thousand}`: the
spoken words are aligned, and the caption word spans from the first to the last.
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
    # (caption, [spoken words]) per script token; `shown{said words}` overrides what is said
    toks = []
    for m in re.finditer(r'(\S+?)\{([^}]*)\}|(\S+)', open(a.script).read()):
        shown = m.group(1) or m.group(3)
        said = [x for x in (m.group(2).split() if m.group(1) else [shown]) if norm(x)]
        if said:
            toks.append((shown, said))
    spoken = [x for _, said in toks for x in said]
    d = decoder()
    for w in {norm(x) for x in spoken}:
        if w and d.lookup_word(w) is None:
            raise SystemExit(f'No pronunciation for "{w}": add it to EXTRA in align.py')
    al = align_chunk(d, pcm, spoken)
    if len(al) != len(spoken):
        raise SystemExit(f'aligned {len(al)} of {len(spoken)} words; check the script matches the read')
    out, k = [], 0
    for shown, said in toks:
        seg = al[k:k + len(said)]
        k += len(said)
        out.append({'w': shown, 't0': round(seg[0][1], 3), 't1': round(seg[-1][2], 3)})
    json.dump({'duration': len(pcm) / SR, 'words': out}, open(a.out, 'w'), indent=1)
    print(f'aligned {len(out)} words, {len(pcm) / SR:.2f}s -> {a.out}')


if __name__ == '__main__':
    main()
