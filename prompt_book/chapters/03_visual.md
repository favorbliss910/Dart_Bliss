# PART III — VISUAL LANGUAGE

## 3.1 Composition and framing

- **One clear focal point** per shot, identifiable in about 0.5 s. Use value contrast (light subject on dark space, dark silhouette on bright glow).
- Use the **full 16:9 width**. Rule of thirds when helpful. Give characters and moving vehicles looking room.
- **Layer foreground / midground / background** in every environment shot.
- **Always include a scale reference** when scale matters (Earth to scale, a tiny probe, a labeled depth bar).
- **Rotate the shot types:** extreme wide, wide, medium, close-up, extreme close-up, POV, over-the-shoulder, **cross-section/cutaway**, **split screen** (Earth vs. subject), **diagram**, **instrument close-up**.
- **Safe areas:** nothing critical below y = 918 px (bottom 15%) or within 40 px of the edges. Callout labels must auto-shift inside the frame (the engine's `label_line` does this).
- **Tests:** squint test, thumbnail-size test, grayscale readability test, mute test, 2× playback test, mobile-size test.

## 3.2 Color script

Use 3–5 dominant colors per scene. Avoid long stretches of oversaturation. Keep the light direction consistent (the engine lights spheres from the **upper left**) and keep rim lighting restrained.

**Semantic colors (channel-wide; never change these meanings):**

| Meaning | Color | Hex |
|---|---|---|
| Danger / alarm / lethal / lost | Red | `#FF3B30` |
| Science / instruments / cold / fictional tech | Cyan / cool blue | `#9FE3FF`, `#6FD3FF` |
| Mystery / models / hypotheses | Purple / violet | `#8A5CFF`, `#B79BFF` |
| Historical / real mission data | Amber | `#FFB347` |
| Success / OK | Green | `#58E08A` |
| Primary text | Warm white | `#FFF1D6` |

**Deep space baseline:** `#070B1A`, `#1C2A55`, `#3D5A9E`, `#FFFFFF`.

**Topic baseline (Jupiter example):** background `#2A1810`, midtones `#B9773E` and `#E3B47A`, highlight `#FFF1D6`.

**Progress the palette with depth or distance.** Each new layer of the journey gets its own palette and the shift is **gradual** (interpolate colors over the descent). Jupiter's progression: amber cloud tops → warm-to-red-brown deep clouds → dark red dense fluid → electric blue-violet metallic hydrogen → warm cream fuzzy core → back to deep-space navy for the ending.

**Building a new topic's color script:** pick (a) a hero baseline of four hues for the subject, (b) its "deep" or "far" palette, (c) a contrast palette for the strangest place in the story, and (d) keep the semantic colors above unchanged.

## 3.3 Character design system: the explorer

One original explorer avatar, **reused across all films** for channel continuity:

- **Silhouette:** round white helmet with a top lamp, large rounded visor, a face visible behind lightly tinted glass, a white suit with **amber shoulder stripes**, a dark chest panel with three status lights (green / amber / cyan).
- **Face:** warm brown skin (`#B87A56`), dark hair line under the helmet, large expressive eyes with catchlights, thick brows, a simple mouth.
- **Rig parameters** (engine `draw_explorer_face` / `draw_explorer_bust`):
  - `look=(x, y)`: pupil direction, −1…1 (for looking up, down, beside).
  - `blink`: 0…1. Auto blink: 0.16 s every 3.7 s (`explorer_look_default`).
  - `brow`: +1 = raised (awe or surprise), 0 = neutral, −1 = worried or fear (the eyes also widen).
  - `mouth`: `neutral`, `smile`, `o` (awe), `grit` (strain), `frown`.
  - `sweat`, `light` (visor reflection color), `light_amt`.
- **Vehicle:** the **fictional capsule**: a graphite ovoid pod, amber band, large round porthole with the explorer visible inside, a dark heat-shield nose, two amber-trimmed fins, and a blinking red top lamp. Options: `heat` (entry glow), `shield` (energy bubble for "imaginary, indestructible"), `ambient` (environment bounce color).
- **Real spacecraft** are drawn in a different visual language (gold thermal blankets, realistic shapes) and are always tagged historical, so the viewer never confuses them with the fictional capsule.
- **Expression sheet to use:** curiosity (`brow .3, look toward subject`), awe (`brow 1, mouth 'o'`), relief (`smile`), worry (`brow −1, frown`), strain (`brow −1, grit`), determination (`brow .6, neutral`).

## 3.4 Twelve principles of motion (apply selectively, and name them per action)

1. Squash and stretch (parachute bloom, number pop; **never** rigid spacecraft)
2. Anticipation (riser and darkening before an impact)
3. Staging (one focal point)
4. Straight-ahead vs. pose-to-pose (particles straight-ahead, characters pose-to-pose via keyframes)
5. Follow-through and overlap (label line draws, then the text fades in; parachute lines lag)
6. Slow in / slow out (`e_io`, `e_sine` on every camera move)
7. Arcs (orbits, swirl motion, head looks)
8. Secondary action (blinking lamp, drifting clouds, twinkling stars, blinking eyes)
9. Timing (table §3.5)
10. Exaggeration (only for what the viewer must notice: 228 g shake, "NO." scale-in)
11. Solid drawing / volume (lit spheres, gradient-shaded hulls)
12. Appeal (the explorer's design and restrained reactions)

**Never make rigid spacecraft rubbery, and never let serious instruments bounce comically.** Instruments ease with controlled `e_out`.

## 3.5 Timing table (seconds; convert to 60 fps frames × 60)

| Action | Duration |
|---|---|
| Text / label pop | 0.25–0.42 (engine `text_pop` 0.35, `e_back` overshoot) |
| Blink | 0.125–0.21 |
| Head or eye turn | 0.25–0.5 |
| Gesture | 0.33–0.58 |
| Whip pan transition | 0.17–0.35 |
| Shake | 0.25–0.5 normal; 1–2.2 for big impacts (damped) |
| Slow push-in | 5–10 |
| Scale pull-out | 2–4 |
| Number counter | 0.5–1.5 (can extend to match a spoken number) |
| Key emotional hold | 0.5–1+ |
| Dissolve | 0.35–0.7 |
| Dip to black | 0.3–0.8 |

Characters may move on twos; camera, compositing and instrument displays always move smoothly at 60 fps. **Ease-in** for acceleration, **ease-out** for arrivals, **ease-in-out** for natural moves. Overshoot (`e_back`) only for text pops and arrivals that should feel snappy.

## 3.6 The 2.5D camera engine

Every camera move must state: start/end framing, direction, duration, speed curve, focal point, layers, and narrative purpose. **No random camera movement.**

**Available moves and how the engine implements them:**

| Move | Implementation |
|---|---|
| Slow dolly in | `c.translate(cx,cy); c.scale(z,z); c.translate(-cx,-cy)` with `z = tw(t, t0, t1, 1.0, 1.07, e_sine)` |
| Extreme scale reveal / pull-out | Keyframe `z` from about 9 → 1 (`keys(t, [(t0,9),(t1,1)])`), track the focal point |
| Zoom to a feature on a sphere | Animate radius R and center so the feature's screen position lands at frame center (Jupiter Great Red Spot: `cy = 540 − sin(22°)·R`) |
| Lateral tracking / parallax | Pass `ox, oy` offsets scaled by layer depth (stars `depth`, clouds `dep`) |
| Vertical descent | Clouds and particles move **upward** (`fall` px/s) while the vehicle stays near center |
| Look up / beside / below | Shift the cloud world by `cam_x, cam_y` while the explorer's pupils move the same way |
| Damped impact shake | `shake(t, t0, dur, amp, freq)` with exponential decay |
| Zoom-through / plunge | Exponential scale-up with a flash at the end into the next shot |
| Whip pan | Transition type `whip` (horizontal slide with multi-copy motion blur) |
| Orbit simulation | Rotate the planet texture (`rot`) and move the satellite on an ellipse |

Do not fake unsupported 3D angles. Draw a new perspective variant instead.

## 3.7 Multiplane depth system

Separate layers: foreground particles → foreground clouds → vehicle/explorer → near clouds → far clouds → background gradient → lighting/glow. **Nearer layers move faster** (`speed × depth`). The engine's `cloud_world` uses four depth layers (0.25, 0.45, 0.75, 1.30) with increasing scale, opacity and brightness, wrapped seamlessly by modulo arithmetic. Add **atmospheric haze** (`haze`) and **depth darkening** (`depth_dark`) as the journey deepens. Never move every layer identically.

## 3.8 Transitions

Choose by meaning; avoid repeating generic crossfades.

| Type (engine) | When |
|---|---|
| `cut` | Continuity, or impact (cut on the hit) |
| `fade` (0.35–0.7 s) | Same place or time, a gentle topic shift |
| `black` (dip, 0.3–0.8 s) | Chapter change, time jump, solemn moment |
| `flash` (0.25–0.35 s) | Impact, entry, energy, zoom-through landing |
| `whip` (0.35 s) | Comparison or contrast ("but first…", "on Earth…") |
| In-shot | Scale pull-out, cutaway opening, palette morph, cloud wipe, object transformation (compact core → fuzzy core) |

## 3.9 Recurring instrument display (HUD) system

- Panels: dark navy glass (`#06101f` at 62%), cyan hairline border, **corner brackets**, JetBrains Mono labels. Red border and red value when in warning.
- **Readouts:** PRESSURE (bar), TEMPERATURE (°C), DEPTH (≈ km, *relative to a stated reference*, e.g. "below the 1-bar level"), SPEED, SIGNAL, DENSITY, G-LOAD.
- **Widgets:** `hud_readout` (label + big value + unit + sub-label), `draw_gauge` (270° dial with a red warning arc and tick labels), `draw_thermo` (thermometer with marks), `signal_bars`, depth ruler, comparison bars.
- Show only the relevant instruments. **Update numbers in sync with the spoken number** (counter finishes on the word). Labels of 1–5 words. Keep the display above the bottom 15% and away from emotional close-ups.
- Values must be correct and their reference conditions stated. Approximations use ≈.

## 3.10 Scientific visualization and honesty

Make the invisible visible with honest diagrams: pressure arrows and gauges, thermometers, trajectories, to-scale Earth comparisons, dipole magnetic field lines, radiation belts, depth indicators, conductivity diagrams (protons + free electrons + current arrow), cutaway cross-sections, gravity-measurement contours.

**Distinguish the three kinds of content visually and with tags:**

| Content | Tag (`draw_tag` kind) | Treatment |
|---|---|---|
| Real history / measured data | `hist` (amber) | Realistic spacecraft, slight warm sepia, real dates |
| Fiction (the capsule, "you") | `fict` (cyan) | The channel capsule and explorer |
| Scientific models / predictions | `model` (purple) | Cutaways, "MODEL-BASED", "NOT TO SCALE" |
| Teaching device | `concept` (pale cyan) | Diagrams, analogies, "ILLUSTRATIVE" |

**Never depict:** a confirmed surface that does not exist, literal "metal rocks" for metallic hydrogen, a "photographed" core or interior, a present-day human-survivable vehicle for impossible conditions, or exact numbers where only ranges exist (use "schematic · not exact values").

## 3.11 Typography

- **Display:** Inter Display Black/ExtraBold (titles, big numbers, chapter titles), warm white `#FFF1D6`, soft shadow, optional glow.
- **Data and labels:** JetBrains Mono SemiBold/Bold (instruments, tags, units), letter-spaced for small caps labels.
- **Sizes at 1080p:** title 76–96, big number 110–150, card headline 40–56, callout 30–40, instrument value 40–64, tag 19, small print 16–22.
- Chapter marker: "CHAPTER 0N" in mono amber + title in Inter Display Black, top left, with an animated underline.
