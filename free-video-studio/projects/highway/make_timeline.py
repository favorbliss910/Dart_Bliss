import json, re
W = json.load(open('words.json'))
txt = [re.sub(r"[^a-z0-9]", "", w['w'].lower()) for w in W]

def at(phrase, after=0.0):
    """time of first word of phrase (first occurrence after `after`)"""
    p = [re.sub(r"[^a-z0-9]", "", x.lower()) for x in phrase.split()]
    for i in range(len(txt) - len(p) + 1):
        if txt[i:i + len(p)] == p and W[i]['t'] >= after:
            return W[i]['t']
    raise ValueError(phrase)

scenes = [
    ("hook", "remotion", 0.0),
    ("skyway", "remotion", at("It all started")),
    ("jam", "remotion", at("Instead, a 5-mile")),
    ("engineer", "remotion", at("So the city hires")),
    ("sidestreets", "revideo", at("but he doesn't time")),
    ("cityhall", "motioncanvas", at("Then he walks into")),
    ("famous", "motioncanvas", at("By the end of the month")),
    ("weird", "manim", at("Now, here's the weird")),
    ("doubles", "remotion", at("Meanwhile, the city")),
    ("burst", "remotion", at("Then one morning")),
    ("flow", "revideo", at("It never comes")),
    ("braess", "manim", at("You see, every driver")),
    ("outro", "remotion", at("It's called Braess's")),
]
DUR = 153.4
out = []
for i, (sid, eng, t) in enumerate(scenes):
    end = scenes[i + 1][2] if i + 1 < len(scenes) else DUR
    out.append({"id": sid, "engine": eng, "start": round(t, 3), "end": round(end, 3)})

beats = {k: at(v, a) for k, v, a in [
    ("blowup", "blow up its busiest", 0), ("sixlanes", "six lanes", 0), ("shortcut1", "great shortcut", 0),
    ("ambulance", "Ambulances sit", 0), ("pizza", "Pizza shows", 0), ("marriage", "Whole marriages", 0),
    ("bridge", "He sits on a bridge", 0), ("stopwatch", "with a stopwatch", 0), ("sidestreets", "He times the little", 0),
    ("weirdthing", "and the only weird", 0), ("everydriver", "Every single driver", 0),
    ("tear", "Tear the skyway", 0), ("laughs", "The council laughs", 0), ("coffee", "spills coffee", 0), ("greatidea", "One guy leans", 0),
    ("hunger", "And to fix hunger", 0), ("smiles", "The engineer just smiles", 0), ("samecars", "Same cars, fewer", 0),
    ("newspaper", "The newspaper draws", 0), ("radio", "Radio hosts", 0), ("honk", "Strangers honk", 0),
    ("buses", "that he wants people", 0), ("doesnt", "He doesn't.", 70), ("sametraffic", "He wants the exact", 0),
    ("faster", "and somehow he thinks", 0), ("howpossible", "How is that possible", 0),
    ("widen", "The council votes", 0), ("cranes", "Cranes everywhere", 0), ("basement", "The engineer gets moved", 0),
    ("box", "His boss drops", 0), ("takestop", "Take your stopwatch", 0), ("skywaywon", "It's over.", 0),
    ("watermain", "a water main bursts", 0), ("shutdown", "The whole highway shuts", 0), ("cars160", "160,000 cars", 0),
    ("noshortcut", "and no shortcut", 0), ("braces", "The city braces", 0),
    ("spill", "Cars spill onto", 0), ("arriveearly", "Ambulances arrive early", 0), ("fifteen", "The 5-mile drive takes 15", 0),
    ("click", "Down in the basement", 0), ("nobody", "Nobody's laughing", 0),
    ("fastestthem", "You see, every driver", 0), ("everyone", "not the road that's fastest for everyone", 0),
    ("piles", "So when there's one", 0), ("jams", "and jams every", 0), ("takeaway", "Take the shortcut away", 0),
    ("stadium", "It's like a stadium", 0), ("sidedoors", "while five side doors", 0),
    ("paradox", "It's called Braess's", 0), ("seoul", "And in real life", 0), ("stream", "put a stream there", 0),
    ("fastestway", "The fastest way across town:", 0), ("blowingup", "blowing up the fastest", 0),
]}
json.dump({"fps": 60, "width": 1440, "height": 2560, "duration": DUR, "scenes": out, "beats": beats, "words": W},
          open('timeline.json', 'w'), indent=1)
for s in out: print(s)
print(len(beats), 'beats')
