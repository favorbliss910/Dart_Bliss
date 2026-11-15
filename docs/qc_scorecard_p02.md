# P02 "Be Seen": QC and scorecard

## Measured (final file `out/p02_be_seen.mp4`)
| Check | Result |
|---|---|
| Size / fps | 1080×1920, 24 fps, h264 CRF 18 + AAC |
| Frames / duration | 3,643 frames, 151.79 s (audio 151.81 s, drift 0.4 frame) |
| Loudness | −16.1 LUFS integrated, −1.4 dBTP true peak |
| Black segments | none (blackdetect d≥0.3 s) |
| Validator | all 1,834 rendered frames present, correct size, none near-empty |
| Render | 24 shots, 360×640, 16 spp, on twos; ~7.5 s/frame mean, ~4 h 15 min total |

## Self-scorecard (1-5; my review from stills and the contact sheet, not from real-time playback)
| Category | Score | Reason |
|---|---|---|
| Character consistency | 4 | Same rigs and materials in every shot; Quill switches to undershirt after the suit comes off, by design |
| Silhouette | 4 | Tall noodle + box head vs short pear + braids vs ball-cart are distinct |
| Motion mechanics | 3 | Planted feet, bob, blinks and overlap present; rigid stretch arms, no knees, animation on twos |
| Genuine parallax | 4 | Every shot is a real 3D camera move with near props |
| Composition | 3 | Most payoffs land; a few frames sit behind heads (S20 end, S21 middle) |
| Lighting | 4 | Fluorescent + tungsten, red strobes, warm corridor, flash |
| Materials | 4 | Glass, water shell, holograms, brushed metal read well |
| Environment detail | 3 | Lab is clean and sparse; no clutter decals, simple corridor |
| Sound sync | 4 | 119 cues driven from exported animation events (not human-auditioned) |
| Storytelling clarity | 4 | Every narrated beat has a matching visual payoff |
| Variety vs registry | 5 | New cast and world; no axis overlap with P01 beyond "night" |

## Not checked
- Real-time playback and listening by a human (audio was measured, not auditioned).
- QC script foot-slide / parallax numbers were not run for P02 (`tools/qc_p01.py` is P01-specific).

## Fixes for categories below 4 (not applied; ask before doing)
1. Motion: render at 24 fps (`STEP=1`, ~doubles render time) and add 2-bone IK arms/legs with elbows and knees.
2. Composition: move the S20 end camera higher over Juno; make S21 a side view throughout.
3. Environment: add wet-floor puddles in S20-S24, labels, cables and posters, and a busier corridor.
4. Full quality-lock render at 540×960 / 24 spp (~31 h on this CPU, much less on a GPU).
