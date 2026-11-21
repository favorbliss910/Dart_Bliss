"""Sound cue sheet for the magpie/cuckoo 'mafia' story."""
import story_mafia as S
from story_mafia import W, E, SHOT_TIMES

CUES, SHAKES = [], []
STYLE = "noir"


def c(t, kind, g=1.0, pan=0.0): CUES.append((float(t), kind, g, pan))


for i, t in enumerate(SHOT_TIMES[1:], 1):
    c(t - 0.05, "whoosh", 0.3, -0.35 if i % 2 else 0.35)

# hook
c(0.20, "stinger", 0.5)
c(W(0, "morning") + 0.05, "crack", 1.0); c(W(0, "morning") + 0.08, "hit", 0.9); SHAKES.append((W(0, "morning") + 0.1, 14))
c(W(1, "fox") + 0.2, "pop", 0.7); c(W(1, "storm") + 0.1, "wind", 0.7); c(W(1, "storm") + 0.15, "pop", 0.7)
for k in range(5): c(W(1, "footprints") + 0.2 + k * 0.22, "tick", 0.5, (k - 2) * 0.3)
# setup
c(W(2), "wind", 0.8)
c(W(2, "every"), "creak", 0.7, -0.3)
for k in range(3): c(W(2, "every") + 3.0 + k * 0.4, "pop", 0.7, 0.2)
c(W(2, "some") + 0.3, "sparkle", 0.7); c(W(2, "some") + 0.5, "ting", 0.5)
c(W(2, "cuckoo"), "cuckoo", 0.9, -0.4); c(W(2, "cuckoo") + 0.1, "flap", 0.6, -0.2)
c(W(2, "cuckoo") + 1.35, "pop", 0.6); c(W(2, "cuckoo") + 1.6, "flap", 0.6, 0.4); c(W(2, "cuckoo") + 2.0, "cuckoo", 0.8, 0.5)
for k in range(3): c(W(2, "rent") + 0.2 + k * 1.1 + 0.25, "buzz", 0.5, (k - 1) * 0.4); c(W(2, "rent") + 0.2 + k * 1.1, "pop", 0.6, (k - 1) * 0.4)
c(W(3) + 0.3, "ting", 0.6)
# the experiment
c(W(4, "plucks") + 0.8, "pluck", 0.9); c(W(4, "plucks") + 1.1, "sparkle", 0.6)
c(W(4, "others"), "click", 0.7); c(W(4, "others") + 1.1, "ding", 0.6)
c(W(4, "writes"), "scribble", 0.8)
c(W(4, "won't") + 0.2, "shh", 0.7); c(W(4, "won't") + 0.5, "ting", 0.7)
c(W(5, "robbing"), "pop", 0.7)
c(W(6) + 0.5, "ting", 0.6)
c(W(6, "third") + 0.2, "scribble", 0.5)
c(W(6, "just") + 0.6, "sparkle", 0.6)
# wrecked
c(W(7), "crack", 1.0); c(W(7), "thud", 0.8); SHAKES.append((W(7) + 0.05, 14))
for k in range(6): c(W(7, "by") + k * 0.3, "pop", 0.5, (k % 3 - 1) * 0.4)
c(W(7, "by") + 1.5, "page", 0.7)
for k in range(4): c(W(7, "pattern") + 0.3 + k * 0.35, "tick", 0.5)
c(W(7, "took") + 0.3, "stamp", 1.0); SHAKES.append((W(7, "took") + 0.3, 12))
c(W(7, "left"), "sparkle", 0.8); c(W(7, "left") + 0.1, "ting", 0.8)
# denial
c(W(8), "pop", 0.8)
c(W(8, "case") + 0.8, "scurry", 0.7)
c(W(8, "but"), "scratch", 0.9); c(W(8, "but") + 0.05, "hit", 0.8)
c(W(9) + 0.4, "boing", 0.7)
c(W(10), "wind", 0.8); c(W(10) + 1.5, "riser", 0.6)
# stakeout
c(W(11), "rustle", 0.7)
c(W(11) + 2.2, "slurp", 0.6)
for k, w in enumerate(("day", "two", "three")): c(W(11, w), "page", 0.6)
c(W(11, "boss"), "yell", 0.8); c(W(11, "boss") + 0.6, "coins", 0.5)
c(W(11, "meanwhile") + 0.7, "pop", 0.6)
c(W(12), "applause", 0.9)
c(W(12, "honestly") + 0.4, "sadslide", 0.5); c(W(12, "honestly") + 0.9, "boing", 0.6)
# the visit
c(W(13), "cuckoo", 0.9, -0.3); c(W(13), "flap", 0.7, -0.2); c(W(13) + 2.1, "thud", 0.7)
c(W(13, "her") + 0.1, "gasp", 0.6); c(W(13, "her") + 0.4, "boom", 0.9); SHAKES.append((W(13, "her") + 0.4, 14))
c(W(14) - 0.02, "tear", 1.0); c(W(14), "hit", 0.9); SHAKES.append((W(14), 18))
for k in range(4): c(W(15) + 0.18 * k + 0.95, "crack", 0.7, (k - 1.5) * 0.3)
c(W(15), "feather", 0.6)
c(W(16), "wind", 0.9); c(W(16) + 0.2, "sadslide", 0.6)
c(W(17), "sparkle", 0.7); c(W(17) + 0.1, "ting", 0.7)
# reveal
c(W(18) - 0.02, "boom", 1.0); SHAKES.append((W(18), 18))
c(W(18) + 0.1, "cuckoo", 0.8, 0.3)
c(W(18, "protection") - 0.05, "stinger", 0.9); c(W(18, "protection") + 0.9, "feather", 0.7)
c(W(18, "raise") + 0.4, "ding", 0.7); c(W(18, "raise") + 1.5, "stamp", 0.8)
c(W(19), "crack", 0.9); c(W(19), "hit", 0.9); c(W(19) + 0.5, "stamp", 1.0); SHAKES.append((W(19) + 0.5, 14))
c(W(20) + 0.3, "pop", 0.6)
c(W(20, "scientists"), "click", 0.7); c(W(20, "scientists") + 0.4, "boing", 0.5)
c(W(20, "but") - 0.05, "sadslide", 0.8)
for k in range(3): c(W(20, "but") + k * 0.35, "thud", 0.6, (k - 1) * 0.4)
c(W(21, "refused") + 0.0, "stamp", 1.0); c(W(21, "refused") + 0.02, "boom", 0.9); SHAKES.append((W(21, "refused") + 0.02, 16))
CUES.sort()

MUSIC = [
    (0.0, 5.0, 0.55, 0), (5.0, 25.0, 0.75, 1), (25.0, 55.0, 0.85, 2), (55.0, 68.5, 0.7, 1),
    (68.5, 85.0, 0.85, 2), (85.0, 98.5, 0.5, 1), (98.5, 100.2, 0.7, 4), (100.2, 102.0, 0.0, 0),
    (102.0, 111.8, 1.0, 3), (111.8, 123.3, 0.75, 1), (123.3, 126.0, 0.9, 2),
]
