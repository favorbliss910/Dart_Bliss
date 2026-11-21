"""Cue sheet for the highway / Braess story (kept sparse; sound2.py filters to clean tonal kinds)."""
import story_highway as S
from story_highway import W, E, SHOT_TIMES

CUES, SHAKES = [], []
STYLE = "savanna"


def c(t, kind, g=1.0, pan=0.0): CUES.append((float(t), kind, g, pan))


c(0.10, "stinger", 0.6)
c(W(0, "delete") + 0.4, "hit", 0.7); SHAKES.append((W(0, "delete") + 0.4, 10))
c(W(1, "skyway") - 0.2, "pop", 0.8)
c(W(2) + 0.3, "pop", 0.8); c(W(2, "shortcut") + 0.1, "ting", 0.8); c(W(2, "shortcut") + 0.2, "sparkle", 0.7)
c(W(2, "five") + 0.2, "pop", 0.8); c(W(2, "forty") + 0.1, "thud", 0.7)
c(W(2, "ambulances") + 0.2, "pop", 0.7); c(W(2, "pizza") + 0.6, "thud", 0.6); c(W(2, "whole") + 0.5, "pop", 0.7)
c(W(3) + 0.3, "pop", 0.7); c(W(3, "sits") + 0.2, "pluck", 0.6)
for k in range(4): c(W(3, "weird") + 0.4 + k * 0.6, "ding", 0.6)
c(W(4) + 1.4, "hit", 0.9); SHAKES.append((W(4) + 1.4, 12))
c(W(5, "spills"), "thud", 0.7); c(W(5), "pop", 0.6)
c(W(6) + 0.3, "pop", 0.8); c(W(6, "fix") + 0.8, "thud", 0.7); c(W(6, "smiles") + 0.7, "ting", 0.7)
c(W(7) + 0.05, "hit", 1.0); SHAKES.append((W(7) + 0.05, 14))
c(W(8) + 0.2, "pop", 0.7)
c(W(9) + 1.2, "sparkle", 0.6); c(W(9, "radio") + 0.2, "pop", 0.8)
c(W(10) + 0.3, "thud", 0.6)
c(W(11), "scratch", 0.9); c(W(11) + 0.05, "hit", 0.8); SHAKES.append((W(11), 12))
c(W(11, "everybody") + 0.2, "pop", 0.8); c(W(11, "doesn't") + 0.7, "ting", 0.7); c(W(11, "wants", 1) + 1.0, "pluck", 0.6)
c(W(11, "how") + 0.1, "hit", 0.9); SHAKES.append((W(11, "how") + 0.1, 12))
c(W(12) + 0.2, "pop", 0.7); c(W(12, "cranes") + 0.3, "thud", 0.6); c(W(12, "engineer") + 0.3, "pop", 0.7)
c(W(12, "boss") + 0.4, "pop", 0.8); c(W(12, "over") + 0.2, "stamp", 1.0); SHAKES.append((W(12, "over") + 0.2, 12))
c(W(13) + 0.05, "boom", 1.0); SHAKES.append((W(13) + 0.05, 20)); c(W(13, "highway") + 0.2, "stamp", 0.9)
c(W(14), "hit", 1.0); SHAKES.append((W(14), 16))
c(W(15) + 0.2, "pop", 0.8); c(W(15, "city"), "riser", 0.9)
c(W(16) + 0.5, "ting", 0.8)
c(W(17), "sparkle", 0.6); c(W(17, "ambulances") + 0.6, "pop", 0.8); c(W(17, "five") + 0.5, "ding", 0.8)
c(W(17, "down") + 0.3, "pluck", 0.6); c(W(17, "nobody's") + 0.3, "thud", 0.5)
c(W(18) - 0.02, "boom", 1.0); SHAKES.append((W(18), 18))
c(W(18) + 0.5, "pop", 0.7); c(W(18, "one") + 0.3, "pop", 0.7)
c(W(18, "take") + 0.4, "sparkle", 0.8); c(W(18, "take") + 1.4, "stamp", 0.8)
c(W(18, "stadium") + 0.3, "pop", 0.7); c(W(18, "called") + 0.2, "ting", 0.9)
c(W(18, "real") + 1.0, "sparkle", 0.8); c(W(18, "real") + 1.7, "ding", 0.8)
c(W(19) - 0.02, "stinger", 0.8); c(W(19) + 1.6, "stamp", 1.0); c(W(19) + 1.62, "boom", 1.0); SHAKES.append((W(19) + 1.62, 18))
CUES.sort()

MUSIC = [
    (0.0, 5.0, 0.55, 0), (5.0, 22.0, 0.7, 1), (22.0, 68.0, 0.75, 2), (68.0, 82.0, 0.6, 1), (82.0, 99.0, 0.8, 2),
    (99.0, 105.2, 0.7, 2), (105.2, 106.3, 0.0, 0), (106.3, 112.0, 0.5, 4), (112.0, 113.4, 0.0, 0),
    (113.4, 123.4, 0.85, 2), (123.4, 149.4, 0.65, 1), (149.4, 154.0, 0.9, 2),
]
