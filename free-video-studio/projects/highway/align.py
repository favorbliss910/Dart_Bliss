"""Word timings from transcript + silence detection (no speech model needed)."""
import json, re
DUR = 153.30
segs = json.load(open('segments.json'))
sil = [l.split() for l in open('silences.txt')]
pairs = []
for i in range(0, len(sil) - 1, 2):
    pairs.append((float(sil[i][1]), float(sil[i + 1][1])))
# speech intervals
speech, t = [], 0.0
for a, b in pairs:
    if a > t: speech.append((t, a))
    t = b
if t < DUR: speech.append((t, DUR))
total = sum(b - a for a, b in speech)

def syl(w):
    w = re.sub(r'[^a-z0-9]', '', w.lower())
    if w.isdigit(): return 2 * len(w)
    return max(1, len(re.findall(r'[aeiouy]+', w)))

words = []
for s in segs:
    for w in s['text'].split():
        words.append({'w': w, 'k': syl(w) + 0.6})
W = sum(x['k'] for x in words)

def speech_to_real(p):  # p = position in speech-seconds
    for a, b in speech:
        if p <= b - a: return a + p
        p -= b - a
    return DUR

acc = 0
for x in words:
    x['t'] = round(speech_to_real(acc / W * total), 3)
    acc += x['k']
    x['e'] = round(speech_to_real(acc / W * total), 3)
# snap sentence starts after punctuation to the nearest silence end within 0.7s
ends = [b for a, b in pairs]
for i in range(1, len(words)):
    if re.search(r'[.,:;?!—\']$', words[i - 1]['w']):
        near = min(ends, key=lambda e: abs(e - words[i]['t']))
        if abs(near - words[i]['t']) < 0.7 and near > words[i - 1]['t']:
            words[i]['t'] = round(near, 3)
for i in range(len(words) - 1):
    words[i]['e'] = min(words[i]['e'], words[i + 1]['t'])
for x in words: del x['k']
json.dump(words, open('words.json', 'w'), indent=0)
print(len(words), 'words; speech', round(total, 1), 's')
for x in words[::40]: print(x)
