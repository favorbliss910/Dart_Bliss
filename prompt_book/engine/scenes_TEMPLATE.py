# Copy into a new project folder as scenes1.py (add scenes2.py, scenes3.py ... as the video grows).
# Every time value comes from at('<exact words from the voiceover>') - never hard-coded seconds.
from common import *

T_HOOK = 0.0
T_TITLE = at('what if you')            # first words of the narration
T_REVEAL = at('<a phrase from words.txt>')
END_T = T_REVEAL + 8.0                 # only the LAST scenes file defines END_T (VO end + ~8 s end card)

def s01(c, t):
    """SHOT 01 - hook. Focal point: the giant subject + tiny vehicle for scale. Change within 5 s."""
    space(c, t, zoom=tw(t, 0, 6, 1.0, 1.07, e_sine))           # background + slow push-in
    draw_jupiter(c, 1430, 610, 720, rot=2.4 + t * 0.012)        # replace with the topic's hero object
    a = fade_window(t, T_TITLE + .1, T_TITLE + 3.2)             # title in/out
    draw_text(c, 'WHAT IF YOU ...', 110, 250, font(76, 'black'), hexc('#FFF1D6'), alpha=a, shadow=1)
    draw_tag(c, 'CONCEPTUAL ILLUSTRATION', 40, 36, 'concept')   # honesty tag, top-left, always

def s02(c, t):
    """SHOT 02 - first reveal, synced to T_REVEAL."""
    space(c, t)
    big_number(c, '1,300', 960, 520, 150, hexc('#FFF1D6'), t, T_REVEAL)

SHOTS1 = [            # (start_time, shot_function, (transition, duration))
    (0.0, s01, ('cut', 0)),
    (T_REVEAL - .3, s02, ('fade', .4)),   # transitions: cut | fade | black | flash | whip
]
