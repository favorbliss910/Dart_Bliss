# PART VIII — TEMPLATES

## 8.1 Shot production template (per shot)

```
SHOT ID / CHAPTER:
EXACT NARRATION (start word → end word):
START TC / END TC / DURATION:              (from words.json; never estimated)
STORY OBJECTIVE / EMOTIONAL OBJECTIVE:
SHOT TYPE / FOCAL POINT / COMPOSITION:
CHARACTER (position, look, brow, mouth, timing after trigger):
FOREGROUND / MIDGROUND / BACKGROUND:
COLOR (3–5 hues) / LIGHTING:
VISUAL ACTION + MOTION PRINCIPLES:
MICRO-BEATS (each: phrase → event):
CAMERA (start/end framing, path, duration, easing, purpose):
PARALLAX / ENVIRONMENTAL MOTION:
HUD (readouts, values, reference conditions):
SOUND (SFX cues on phrases; music state; ambience):
TRANSITION IN (type, duration, reason):
HONESTY TAG / SCIENCE ACCURACY NOTES:
RETENTION PURPOSE:
ENGINE IMPLEMENTATION (functions used):
QA SCORE (/10) + notes:
```

## 8.2 Sequence breakdown / batch report

```
CHAPTER N — <title> (TC in → TC out)  palette: <hexes>  music: <cue>  sound palette: <beds>
  Shots: Sxx–Syy   Visual peak? <yes/no + what>
  Real / model / fiction segments: ...
Batch report: completed shot IDs · narration covered / remaining · runtime so far ·
character & environment continuity · camera summary · visual-peak progress ·
science warnings · QA failures and corrections
```

## 8.3 Music cue sheet

```
| Program in | Program out | Track | Track in | Gain | Fade in/out | Purpose / story turn |
```

## 8.4 SFX cue sheet

```
| Phrase constant | Time | Effect + params | Bus | Purpose (principle #) |
```

## 8.5 Color script

```
| Chapter | Baseline (4 hex) | Accent | Mood | Transition to next |
```

## 8.6 Delivery report (send with the video)

```
Title · runtime · resolution/fps · shots · visual peaks
Music cue map (short) · SFX count · loudness (LUFS / dBTP)
Verified: (how: ffprobe, encoded-frame inspection, loudness measurement, sync spot-checks)
Not verified by listening: (state it) · Known minor issues · Offer to adjust
Files: MP4, SRT, source committed at <branch>
```
