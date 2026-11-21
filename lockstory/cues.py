"""Sound cue sheet for the drongo story (times come from the audio-aligned transcript)."""
import story
from story import W, E, SHOT_TIMES

CUES = []     # (time, kind, gain, pan)
SHAKES = []   # camera impacts (time, px) for render.py


def c(t, kind, g=1.0, pan=0.0):
    CUES.append((float(t), kind, g, pan))


# --- every cut gets a soft whoosh (alternate pan) -------------------------------------
for i, t in enumerate(SHOT_TIMES[1:], 1):
    c(t - 0.05, "whoosh", 0.32, -0.35 if i % 2 else 0.35)

# --- hook and opening ------------------------------------------------------------------
c(0.40, "stinger", 0.55)
c(W(0, "screams") - 0.05, "scream", 0.9, -0.2)
for k in range(4): c(W(0, "screams") + 0.95 + k * 0.33, "pop", 0.45, 0.3)
# --- meerkats ---------------------------------------------------------------------------
c(W(1), "dig", 0.7, 0.0)
c(W(1, "beetles"), "pop", 0.8); c(W(1, "scorpions"), "pop", 0.8, 0.2); c(W(1, "lizard"), "pop", 0.8, 0.3)
c(W(1, "occasional") - 0.1, "boing", 0.6)
c(W(2, "hole"), "pop", 0.7); c(W(2, "sky") - 0.2, "whoosh", 0.7, 0.6)
c(W(3, "hawks"), "hawk", 0.45, 0.5)
c(W(3, "barks"), "bark", 0.9, 0.0); c(W(3, "barks") + 0.9, "pop", 0.6, 0.3)
c(W(3, "everyone"), "dive", 1.0, 0.0); SHAKES.append((W(3, "everyone") + 0.15, 10))
# --- drongo arrives ---------------------------------------------------------------------
c(W(4), "flap", 0.7, 0.0)
c(W(4, "small") + 0.8, "ting", 0.6)
c(W(4, "dig"), "buzz", 0.55, -0.4); c(W(4, "hunt"), "buzz", 0.55, 0.4)
c(W(5, "chirps"), "chirp", 0.9, -0.3); c(W(5, "squawks"), "squawk", 0.85, 0.3)
c(W(5, "even"), "yip", 0.9, 0.0); c(W(5, "even") + 1.4, "pop", 0.5)
for k in range(5): c(W(6) + 0.25 + k * 0.28, "ha", 0.55, (k - 2) * 0.3)
c(W(6, "birdbrain") - 0.1, "yell", 0.8, 0.0); c(W(6, "birdbrain") + 0.3, "pop", 0.7)
# --- hawk ---------------------------------------------------------------------------------
c(W(7), "hawk", 0.85, -0.5); c(W(7), "flap", 0.5, -0.3)
c(W(7, "drongo"), "scream", 1.0, -0.4)
c(W(7, "everyone"), "dive", 1.0, 0.0); SHAKES.append((W(7, "everyone") + 0.15, 12))
c(W(7, "hawk", 1) + 0.3, "thud", 0.9); c(W(7, "nothing"), "sadslide", 0.7); SHAKES.append((W(7, "hawk", 1) + 0.55, 14))
# --- routine ------------------------------------------------------------------------------
c(W(8, "and") - 0.1, "page", 0.8)
c(W(8, "barely"), "yawn", 0.4)
c(W(9), "pop", 0.7); c(W(9, "free") + 0.1, "ting", 0.7)
# --- the weird part -----------------------------------------------------------------------
c(W(10), "scratch", 1.0); c(W(10), "hit", 0.9); SHAKES.append((W(10), 16))
c(W(10, "one") + 0.4, "sparkle", 0.7, 0.2)
c(W(10, "drongo"), "scream", 1.0, -0.4); c(W(10, "drongo") + 0.8, "scurry", 0.9, 0.3)
c(W(10, "but"), "wind", 0.7)
c(W(11), "swoop", 0.9, 0.0); c(W(11, "flies"), "flap", 0.6, 0.3)
c(W(11, "winked"), "ting", 0.9); c(W(11, "winked") + 0.1, "sparkle", 0.7)
c(W(12, "wolf") - 0.2, "pop", 0.8); c(W(12, "wolf") + 0.1, "howl", 0.4)
c(W(12, "everyone") + 0.5, "buzz", 0.45)
# --- the lie stops working ------------------------------------------------------------
c(W(13, "scorpion", 0) if False else W(13) + 1.2, "sparkle", 0.6)
c(W(13, "drongo"), "scream", 0.9, -0.4)
for k in range(6): c(W(13, "nobody") + 0.6 + k * 0.4, "munch", 0.5, 0.3)
c(W(13, "laughs"), "ha", 0.6); c(W(13, "laughs") + 0.35, "ha", 0.6); c(W(13, "laughs") + 0.7, "pop", 0.7)
c(W(14), "sadslide", 0.9)
c(W(15), "hit", 1.0); SHAKES.append((W(15), 12))
c(W(16), "riser", 0.9)
# --- the payoff -----------------------------------------------------------------------------
c(W(17) - 0.02, "boom", 1.0); SHAKES.append((W(17), 22))
c(W(17, "comes"), "alarm", 1.0, 0.3)
c(W(17, "perfect"), "ting", 0.8); c(W(17, "perfect") + 0.2, "pop", 0.5)
c(W(18), "gasp", 0.8); c(W(18) + 0.3, "scurry", 1.0, 0.0)
c(W(18, "sand"), "dive", 1.0); SHAKES.append((W(18, "sand") + 0.1, 12))
c(W(19), "wind", 0.9); c(W(19) + 0.2, "skitter", 0.6, -0.2)
c(W(20), "swoop", 0.9, -0.3); c(W(20) + 0.9, "flap", 0.7, 0.4)
# --- explainer ---------------------------------------------------------------------------------
c(W(21), "pop", 0.6)
for k in range(5): c(W(21, "copycats") + 0.15 * k + 0.2, "pop", 0.35, (k - 2) * 0.3)
for k in range(8): c(W(21, "dozens") + 0.1 + k * 0.14, "tick", 0.5, (k % 4 - 1.5) * 0.3)
c(W(21, "real") - 0.4, "fill", 0.6); c(W(21, "real") + 1.3, "buzz", 0.5)
c(W(21, "that's") if False else E(21) - 1.0, "hit", 0.7)
c(W(22, "trust") - 1.2, "fill", 0.7)
for k in range(4): c(W(22) + 1.1 + k * 0.7, "ding", 0.55, 0.2)
c(W(22, "lie"), "drain", 0.9); c(W(22, "lie") + 0.8, "coins", 0.9, 0.3); SHAKES.append((W(22, "lie") + 0.5, 10))
c(W(22, "switch"), "click", 0.8); c(W(22, "switch") + 0.5, "click", 0.8, 0.3)
for k in range(10): c(W(23) + 0.9 + k * 0.4, "pop", 0.3, (k % 5 - 2) * 0.2)
c(W(23, "rain"), "yell", 0.5); c(W(23, "rain") + 0.7, "scurry", 0.7)
c(W(23, "scientists"), "click", 0.7)
c(W(24), "swell", 0.8)
c(W(24, "bandit") - 0.05, "stinger", 0.9); c(W(24, "bandit") + 0.1, "ting", 0.9)
c(E(24) - 0.45, "boom", 0.9); SHAKES.append((E(24) - 0.4, 14))

CUES.sort()

# music section volumes: (start, end, level 0..1, intensity)
MUSIC = [
    (0.0, 6.5, 0.55, 0), (6.5, 25.0, 0.75, 1), (25.0, 56.0, 0.85, 2), (56.0, 65.0, 0.8, 1),
    (65.0, 74.7, 0.9, 2), (74.7, 87.5, 0.8, 2), (87.5, 97.8, 0.85, 2),
    (97.8, 99.8, 0.0, 0),                       # the drop: music cuts out on "out of tricks"
    (99.8, 102.4, 0.7, 4),                      # tension riser
    (102.4, 118.8, 1.0, 3),                     # payoff, full groove
    (118.8, 146.5, 0.7, 1),                     # explainer
    (146.5, 153.7, 0.9, 2),
]
