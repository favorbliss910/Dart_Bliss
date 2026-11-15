# WHAT IF YOU…? — CINEMATIC 2D SCIENCE DOCUMENTARY PROMPT BOOK

**Production Bible & Master Prompt · Version 1.0**

*Build-from-code 2D/2.5D animation · Narration-synced sound design · 1920×1080 · 60 fps · 16:9*

Compiled from the channel's *Jupiter 2D Animation Master Prompt V2.0*, the *300 Principles of Sound Design*, and the production of **"What If You Actually Fell Into Jupiter?"** (12:28, 54 shots, 44,892 frames).

## How this book is organized

| Part | Contents | Use it when |
|---|---|---|
| **I. Master Prompt** | The paste-ready instructions and the project card | Start of every new video |
| **II. Story & Retention System** | Retention director, the opening five seconds, structure, pacing, visual peaks | Planning the sequence breakdown |
| **III. Visual Language** | Composition, color script, characters, motion principles, timing, camera, depth, transitions, HUD, science honesty | Designing shots |
| **IV. The 2D Animation Engine** | How the film is built from code, module by module, with techniques, recipes, performance and QA | Writing and rendering the shots |
| **V. The Sound Design Engine** | VO processing, music analysis and cue mapping, effects synthesis, cue sheets, ducking, loudness | Building the soundtrack |
| **VI. The 300 Principles of Sound Design** | The full reference list, with how each chapter was applied | Every audio decision |
| **VII. Quality Control & Scoring** | Checklists, retention rubric, lessons learned / known failure modes | Before render and before delivery |
| **VIII. Templates** | Shot template, batch report, cue sheet, color script, delivery report | Producing documentation |
| **IX. Worked Example: Jupiter** | Complete shot map, peaks, palette, music map, effects cue list | Matching the quality bar |
| **X. Topic Playbooks** | Ready-made plans for galaxy, universe, parallel universe and more | Starting a new topic |
| **Appendices** | A: full engine source code · B: environment setup · C: commands · D: glossary | Implementation |

> **Golden rule of the channel:** *Make the viewer FEEL the journey. Every shot must support curiosity, comprehension, emotion or discovery; every camera movement needs a reason; every sound serves the story; every reveal is earned. Stay scientifically honest.*


---

# PART I — THE MASTER PROMPT (PASTE THIS)

> **How to use:** Start a new Claude Code session in a cloud environment that has a repository attached. Paste everything from **"BEGIN MASTER PROMPT"** to **"END MASTER PROMPT"**. Then fill in the **PROJECT CARD** at the end and upload the voiceover and background-music files. You can also paste the whole book: the prompt tells the session to treat the rest of the book as its reference manual.

---

**BEGIN MASTER PROMPT**

## 0. Identity of this job

You are the full production team for a channel of **cinematic 2D animated science documentaries** in the format **"What If You…?"** Examples: *What If You Fell Into Jupiter?*, *What If You Traveled to Another Galaxy?*, *What If You Entered a Parallel Universe?*. You act at the same time as:

animation director · cinematographer · 2D character animator · motion-graphics designer · storyboard artist · scientific-visualization specialist · VFX supervisor · **sound designer and re-recording mixer** · YouTube retention editor · QA supervisor · **creative-coding engineer who builds and renders the film from code**.

You do not stop at describing a video. **You build it.** You write the rendering engine and the shots, render real frames, design and mix the soundtrack, and deliver a finished MP4. You are given a voiceover, background music, and this book. Nothing else is needed.

## 1. Inputs you will receive

1. **Voiceover** (MP3/WAV). This is the **final narration**. It is the timing master for everything. Never rewrite it, re-record it, skip it or reorder it.
2. **Background music**: one to four tracks (MP3/WAV), already licensed by the channel owner.
3. **Project card** (end of this prompt): title, topic, optional notes.
4. **This book.** It contains the visual and motion rules (Part III), the 2D animation engine and its complete source code (Part IV and Appendix A), the sound-design method (Part V), all 300 sound-design principles (Part VI), QA (Part VII), templates (Part VIII) and the finished Jupiter project as a worked example (Part IX).

## 2. Non-negotiable rules

1. **Narration is sacred.** Use the supplied voiceover exactly. Every shot, reveal, number, label, impact and sound effect is placed on **word timestamps taken from the voiceover**, never on guessed seconds.
2. **Scientific honesty.** Every shot carries a small top-left **honesty tag**: `HISTORICAL RECONSTRUCTION`, `FICTIONAL …`, `MODEL-BASED ILLUSTRATION`, `CONCEPTUAL ILLUSTRATION`, `ANALOGY` or `HYPOTHESIS`. Mark approximate numbers with **≈ / ~**. Label anything not to scale `NOT TO SCALE` or `SCHEMATIC`. Draw size comparisons **to scale** whenever you claim scale. Never present speculation, fiction or a model as an observation. Never show a fabricated photograph of something nobody has photographed.
3. **Clarity beats decoration.** One primary idea and one focal point per shot, readable in about half a second. Animate the **idea**, not the words.
4. **Safe areas.** No critical text or instrument display in the **bottom 15%** of the frame (y > 918 px at 1080p) or within about 40 px of the edges.
5. **Original work only.** Never copy artwork, characters or the voice of a reference video.
6. **Licensing.** Use only the music supplied, plus sound effects **you synthesize yourself**. No downloaded stock sound effects.
7. **Report faithfully.** Never claim to have watched or listened to something you only measured. Say what you verified and how.

## 3. Approval mode (optional)

- **Default: DIRECT RENDER.** Run the whole pipeline in §4 and deliver the finished video. Before rendering, review your own contact sheets (§4 step 7) and fix problems.
- **REVIEW MODE** (only if the project card says `REVIEW MODE: ON`): stop after step 5. Send the sequence breakdown, visual-peak map, palette and contact sheets of the first ~20 shots. Wait for **CONTINUE**, then render.

## 4. The production pipeline (follow in order)

**Step 1 — Environment and engine.** The engine lives in the channel repository at `prompt_book/engine/` (branch with this book). If the repository is attached, use it directly. If not, recreate every file exactly from **Appendix A**. Set up the toolchain from Appendix B: Python with `skia-python`, `numpy`, `pillow` and `sherpa-onnx`, plus `ffmpeg`. If `import skia` fails with `libEGL.so.1`, run `apt-get update && apt-get install -y libegl1 libgl1`. Download the speech model from **GitHub releases**, not Hugging Face, which may be blocked. Run `nproc` and record the core count; it sets the render budget.

**Step 2 — Transcribe with word timestamps.** Run `engine/transcribe.py <voiceover> <model_dir> <project_dir>`. It writes `words.json` (word, start time) and `words.txt`. Read **all** of `words.txt` before designing anything. Write down the runtime, the total word count and every phrase that carries a number, a reveal, a turn, a joke or a question.

**Step 3 — Analyze the music.** For each track, run `sfxlib.music_energy(path)` (RMS in 4-second steps). Label each track's **soft intro / build / full / outro** sections and its overall mood. Build a **music cue map**: which track carries which story section, where it enters and exits, and **where there is deliberately no music** (Part V §5.4).

**Step 4 — Story analysis and sequence breakdown.** Split the narration into chapters and sequences. For every sequence, answer the five **Retention Director** questions (Part II §2.1). Mark **3–5 visual peaks** (the moments to spend the most effort on) and smaller surprises every 30–60 s. Mark every place where the story moves between **real/historical**, **model-based** and **fictional** content; each gets a different visual treatment and tag.

**Step 5 — Visual design.** Build the **color script** (Part III §3.2): a baseline palette for the topic, a danger color, a science/cold color and a mystery color, with the palette progressing as the story deepens. Design the **hero assets**: the main celestial object(s), the explorer avatar (reuse the channel explorer for continuity), vehicles, and the instrument-display set. Plan **one shot per narrative beat**: typically one shot every 6–15 s, with a meaningful visual change every 2–5 s inside each shot.

**Step 6 — Write the shots as code.** Copy `engine/` into the project. Create `scenes1.py`, `scenes2.py` and so on, using `scenes_TEMPLATE.py` and the Jupiter example (Appendix A) as models. Each shot is a pure function `shot(canvas, t)` that draws one frame at global time `t`. Look up every timing with `at('<exact words>')`. Register shots in a `SHOTS` list with a transition. The last file defines `END_T` (end of voiceover + about 8 s for the end card).

**Step 7 — Contact-sheet QA (mandatory, before the full render).** Render contact sheets (`python3 render.py contact <t0> <t1> <step> sheet.png 5`) covering the **entire** timeline, at about one frame every 1–3 s for the first minute and every 6–8 s after that. Look at every tile. Check: focal point, label clipping at frame edges, overlap, safe areas, black or empty frames, wrong honesty tags, numbers out of sync with the narration, and blocky textures from over-zoom. Fix, re-render the sheet, repeat. Then benchmark (`python3 render.py bench t1 t2 …`) to estimate render time.

**Step 8 — Full render.** Run `engine/render_all.sh <project> <out> 8 <cores> 60`: 1920×1080, 60 fps, libx264 CRF 18, in parallel segments. Watch progress with a background monitor; do not poll in a loop. Spot-check frames from finished segments.

**Step 9 — Sound design and mix.** Write the project cue sheet `mix.py`, modelled on `example_jupiter/mix.py`, following Part V. Process the voiceover → place music cues → place synthesized effects on narration timestamps → ambience beds → VO-keyed ducking → bus mix → **static gain + limiter to −14 LUFS integrated, ≤ −1.5 dBTP**. Measure and report: integrated loudness, true peak, and short-term level at the 3–5 biggest moments.

**Step 10 — Mux and captions.** Concatenate the segments, mux with the final mix (AAC 256 kbps, `+faststart`), and generate an `.srt` from `words.json`. Verify with `ffprobe`: 1920×1080, 60 fps, expected frame count, duration ≈ `END_T`.

**Step 11 — Final verification.** Extract frames at the visual peaks from the **encoded** file and inspect them. Confirm audio and video sync at 3 points: a number reveal, an impact, the end card.

**Step 12 — Deliver.** Send the MP4 and SRT to the user. Write a short report: runtime, shot count, visual peaks, music cue map, loudness numbers, what you verified and how, known minor issues, and an offer to adjust. The rendered MP4 is usually over GitHub's 100 MB file limit, so `.gitignore` it and commit the source, scenes, cue sheet and captions.

## 5. Quality bar

The reference is the finished Jupiter film (Part IX): a 12:28, 54-shot, 1080p60 documentary with a hook within 5 s, five earned visual peaks, a consistent explorer character, honest tags throughout, a three-track music arc with a deliberate silence, about 120 synthesized sound-effect cues, and a −14 LUFS mix. Every new film must match or beat it.

## 6. PROJECT CARD (fill in for every new video)

```
TITLE:            What If You ________________?
TOPIC / SCIENCE:  (one or two sentences)
VOICEOVER FILE:   (uploaded)
MUSIC FILES:      (uploaded; optional notes on mood of each)
REVIEW MODE:      OFF   (ON = stop for storyboard approval before rendering)
SPECIAL NOTES:    (e.g., recurring character name, things to avoid, thumbnail moment)
FORMAT:           1920x1080 · 60 fps · 16:9   (default)
LOUDNESS:         -14 LUFS integrated, <= -1.5 dBTP (default)
```

**END MASTER PROMPT**


---

# PART II — STORY & RETENTION SYSTEM

## 2.1 The Retention Director (ask before every shot)

Before designing any shot, answer these five questions in one line each. If a shot cannot answer them, redesign or merge it.

1. **What must viewers understand?** (one primary idea)
2. **What is the single focal point?** (identifiable in about 0.5 s)
3. **What changes?** (there must be a visible development)
4. **What should viewers feel?** (curiosity, awe, dread, relief, surprise, wonder)
5. **Why keep watching?** (the open question or promise that carries into the next shot)

**Animate the idea, not the words.** For "pressure rises", show a gauge climbing and arrows squeezing the capsule, not the word PRESSURE. For "1,300 Earths fit inside", fill the planet with Earth icons while a counter runs. For "the signal was lost", show a waveform flatlining into red.

## 2.2 The opening five seconds

- **First frame = the thumbnail promise.** Never black, a logo or generic stars. Show the enormous subject and a tiny vehicle or explorer, so scale and danger read immediately. *(Jupiter: Jupiter fills two-thirds of the frame; a tiny probe with a glowing trail drifts toward it.)*
- **Title on screen in the first second**, for about 3 s, then out of the way.
- **A meaningful development within 5 s** (a date label, a label pop, the vehicle moving, a cut to a closer view).
- **A sonic event on the first frame**: soft sub-boom plus a low drone (sound principle 011).
- **Do not overload.** One title, one subject, one movement.
- Put a **thumbnail-worthy moment** in the first minute, and give every major new sequence its own **mini-hook** (a surprising composition, a scale change, a discovery or a physical consequence).

## 2.3 Structure: chapter → shot → micro-beat

| Level | Definition | Typical count (12-min film) |
|---|---|---|
| **Chapter** | A narrative section with its own palette and sound palette | 4–8 |
| **Shot** | One continuous composition (one draw function) | 45–70 (Jupiter: 54) |
| **Micro-beat** | One animated development inside a shot: a label pop, a number counter, a head turn, a gauge move, a reframe, a light change | 400–900 |

Plan **one shot per narrative beat** (usually 6–15 s). Inside each shot, schedule a micro-beat **every 2–5 s**, all keyed to word timestamps. Do not invent filler beats. The master format supports up to 2,000 micro-beats, but every one must carry meaning.

## 2.4 Sequence template for "What If You…?" films

Follow the **actual narration order**. This is the usual dramatic shape:

1. **Hook question** + the real historical precedent (the probe, the telescope, the observation).
2. **The disturbing twist**: how little we actually know, or how extreme it is.
3. **The three questions** (what would you hit / find / reach?).
4. **The plan**: "follow the real thing as far as it went, then go where nothing has gone". Show **real** (solid amber line) versus **imagined** (dashed blue line) visually.
5. **Establish the subject from outside** (beauty, scale, motion), with scale comparisons to Earth.
6. **Approach and entry**: speed, danger, physical consequence (the visual peak).
7. **Arrival in the fictional vehicle**: the world from inside, what is missing, the instruments.
8. **Deeper layers**: each new layer gets its own palette shift, instrument readouts and a misconception debunked ("don't imagine X").
9. **The historical data moment** (what real missions actually measured, and what surprised scientists).
10. **The deepest mystery** (what models predict, what remains unknown, competing hypotheses).
11. **The answer** to the opening question (a one-word punch: "NO.") + recap of the journey.
12. **Cosmic pull-back**: back to the viewer's own sky, the humbling final line, the end card.

## 2.5 Pacing engine

- **Danger:** fast cuts, shakes, short shots (3–6 s), dense sound.
- **Awe / explanation:** long compositions (8–20 s) with internal motion (drifting clouds, parallax, slow push-in, counters).
- **Suspense:** deliberate stillness, near-silence, one small moving detail.
- **Never cut on a rigid timer.** Cut on narrative beats: sentence starts, the key noun, the number.
- **The 2–5 s rule:** something meaningful changes every 2–5 s (new shot, label, reaction, reframe, lighting, environmental event, scale, diagram).

## 2.6 Visual peak engine

Pick **3–5 standout moments** that get extra production effort, and space them through the film. Add **smaller story-driven surprises every 30–60 s**. Give each peak time to register (hold 1–2 s after the payoff). Use **callbacks**: an image or sound from early in the film that returns with new meaning later.

**Jupiter's peaks (reference):**

1. Tiny probe against giant Jupiter (opening).
2. Atmospheric entry: darkness becomes a brilliant glow, then the deceleration hits at **228 g**.
3. Clouds with no ground and no horizon ("HORIZON: NOT FOUND").
4. **METALLIC HYDROGEN** reveal (palette flips from red-brown to electric blue-violet).
5. The compact core dissolves into the **fuzzy core**.

**Callbacks used:** the opening composition returns for "Would you eventually land? — NO."; the magnetic field from the beginning is explained by the metallic hydrogen in the interior.

## 2.7 Emotional arc and character acting

- The explorer reacts **after** the trigger, never before. Hold key emotions **0.5–1 s or longer**.
- Use reactions with restraint: a few strong ones (awe, smile, worry, gritted teeth), not constant mugging.
- The arc of a typical film: curiosity → awe → dread → relief → dread → wonder → humility.


---

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


---

# PART IV — THE 2D ANIMATION ENGINE (HOW THE FILM IS BUILT)

This part documents exactly how the Jupiter film was animated: the architecture, every technique, the reasons behind the choices, and the mistakes to avoid. The complete source is in **Appendix A**. A new film **reuses the engine unchanged** and only writes new `scenes*.py` files, plus new hero assets if the topic needs them (Part X).

## 4.1 Philosophy: the film is a pure function of time

Every frame is drawn from scratch by code: `frame = draw(t)`, where `t` is the **global program time in seconds** (the same clock as the voiceover). There is no timeline editor, no keyframe file and no stored animation state. This gives:

- **Perfect narration sync**: every event is written as `at('exact words')`, so timings come from the transcript, not from guesses.
- **Free parallel rendering**: any frame can be rendered independently, so the film splits into segments across CPU cores.
- **Instant iteration**: change a number, re-render one still or a contact sheet in seconds.
- **Resolution independence**: everything is vector drawing (Skia) plus procedural textures (NumPy), crisp at 1080p.

## 4.2 Toolchain

| Tool | Role |
|---|---|
| **Python 3** | Everything |
| **skia-python** | Anti-aliased 2D vector rendering: paths, gradients, blur mask filters, image draws, text (Google's Skia, the Chrome renderer) |
| **NumPy** | Procedural textures (noise, planet bands, clouds), sphere projection, audio DSP |
| **Pillow** | Bicubic upsampling for value noise; contact sheets |
| **ffmpeg / libx264** | Encoding raw BGRA frames piped from Python; concatenation; muxing |
| **sherpa-onnx + Parakeet TDT 0.6B v2 (int8)** | Offline word-level transcription of the voiceover |
| **Fonts** | Inter / Inter Display (all weights), JetBrains Mono |

## 4.3 Architecture (module map)

```
engine/
  core.py        timing (at), easing, tweening, shake, colors, palette, fonts, text, paints,
                 gradients, image conversion (premultiplied BGRA), value noise, cache
  assets.py      procedural textures + renderers: Jupiter band texture with Great Red Spot,
                 Earth texture, lit textured sphere renderer, cloud & haze sprites,
                 starfield, vignette, film grain, additive glow sprite
  elements.py    vector props & UI: arrows, animated X/check, dashed paths, honesty tags,
                 callout labels (auto-clamped), cards, big numbers, chapter cards,
                 HUD panels/readouts/gauges/thermometer/signal bars, Galileo entry probe,
                 parachute + descent module, Juno, explorer face/bust rig, capsule,
                 Jupiter cutaway cross-section, dipole field lines, H2 molecules
  common.py      environments: gradient backgrounds (cached), space(), multiplane
                 cloud_world(), speed_lines(), particles(), flash, depth ruler, texture strips
  render.py      timeline assembly (auto-discovers scenes*.py), transitions, post (vignette,
                 grain, final fade), still/contact/bench/segment-encode commands
  transcribe.py  voiceover -> words.json / words.txt
  sfxlib.py      the sound engine (Part V)
  render_all.sh  parallel segment render + concat
  scenes_TEMPLATE.py
  example_jupiter/  scenes1-3.py (54 shots), mix.py (cue sheet), words.json
```

A project folder (`JV_PROJECT`) contains `words.json`, `scenes1.py … scenesN.py`, `mix.py`, and a `cache/` directory created automatically for textures.

## 4.4 Narration-locked timing: `at()`

`core.at(phrase, after=0, end=False)` normalizes words (lowercase, alphanumerics only) and returns the **start time of the first occurrence of the phrase at or after `after`**. With `end=True` it returns the start of the word after the phrase, which is useful for "right after X is said".

```python
T_DECEL  = at('Then the deceleration hits')     # 168.82 s
T_228B   = at('two hundred and twenty eight')   # 180.54 s
T_NO     = at('No', after=649)                  # disambiguate repeated words with after=
T_LOST   = at('the signal was lost', end=True) - .15
```

**Rules:**

- Define all phrase constants at the top of each scenes file. They double as **the sound-effect cue points** (the mixer imports the same constants), so picture and sound can never drift apart.
- Numbers are transcribed as spoken words ("two hundred twenty eight"), except where the model writes digits ("3000"). Always check `words.txt`.
- A missing phrase raises `KeyError` at import, so bad sync fails loudly.

## 4.5 Motion vocabulary (core.py)

| Function | Purpose |
|---|---|
| `prog(t, t0, t1)` | 0→1 progress, clamped |
| `e_in, e_out, e_io, e_sine, e_back, e_expo_out` | Easing curves (cubic in/out, sine, back-overshoot) |
| `tw(t, t0, t1, a, b, ease)` | Tween a value |
| `keys(t, [(t, v), …], ease)` | Multi-keyframe interpolation (numbers or tuples) |
| `fade_window(t, t0, t1, fin, fout)` | 0→1→0 visibility window for labels and cards |
| `shake(t, t0, dur, amp, freq, seed)` | Damped camera shake (exponential decay + tail fade) |
| `wobble(t, amp, f)` | Organic idle sway (two sines) |
| `text_pop(...)`, `big_number(...)` | Text that scales in with back-overshoot (0.35–0.4 s) |

**Pattern: a micro-beat is one line.**

```python
k = prog(t, T_GRS, T_GRS + .6)                       # starts on the spoken word
label_line(c, x0, y0, x1, y1, 'GREAT RED SPOT', k=k, sub='A GIANT STORM · WIDER THAN EARTH')
```

## 4.6 Rendering fundamentals and performance lessons

- **Canvas:** `skia.Surface(1920, 1080)`. Each shot draws onto `c` (a `skia.Canvas`). Use `c.save()/c.restore()` around transforms.
- **Images must be premultiplied BGRA** (`to_img()`): drawing an unpremultiplied RGBA image cost about 23 ms per full frame versus about 1 ms for premultiplied BGRA (native byte order). Scaled draws were about 67 ms versus 6 ms. **This was the single biggest performance win.**
- **Readback:** `surface.toarray()` (native BGRA, about 4 ms), piped straight to ffmpeg with `-pix_fmt bgra`.
- **Full-screen gradients are slow (~20 ms).** Cache them as small images (64×256) and stretch-draw them (`grad_img` / `bg()`).
- **Blur mask filters** are fine on small shapes; for glows use the cached additive sprite (`glow()`, plus blend).
- **Sphere renders cost 20–100 ms.** Cap the compute grid (`max_grid≈1150`) and let Skia upscale with linear filtering.
- **Measured average:** about 190 ms per frame per core (range 100–650 ms). 44,892 frames on 4 cores took about 60 min including x264 encoding.

## 4.7 Procedural textures (assets.py)

### Value noise
`noise2(h, w, cells_y, cells_x, seed, wrap_x, octaves, persistence)` builds smooth noise by **bicubic-upsampling random grids** (Pillow) and summing octaves (fractal). `wrap_x=True` copies the first grid columns to the end so the texture tiles around a planet's longitude. Using **more cells in Y than X** stretches the features horizontally, which gives the banded, wind-sheared look of a gas giant.

### Gas-giant band texture (equirectangular, 2048×4096)
1. A **band table** of (latitude, color) control points, interpolated per channel (`_band_lookup`): zones are cream (`#FFF1D6`, `#F2DFBD`), belts are brown (`#B9773E`, `#8A4E2B`), poles are grey-brown.
2. **Turbulent latitude:** `lat_e = lat + n1·amp·2.2 + n2·2`, with turbulence amplitude larger near belt edges (`|sin(9·lat)|`).
3. **Festoons** at the equatorial-belt edge: `exp(-((lat-7)/3.5)²) · sin(13·lon + noise)^12 · 2.6`. Keep the amplitude small; large values look like drips.
4. **Vortex (Great Red Spot)** at lat −22°, lon 180°: rotate local coordinates by `2.6·exp(−0.8 r²)` (a swirl), then paint a core / rim / light collar with spiral streaks. **Size it realistically** (semi-axes 7.6° × 4.7°, about 17,000 × 11,000 km) so an Earth comparison is honest.
5. White ovals and dark barges as small elliptical stamps; fine streak noise multiplies brightness ±8%.
6. Cache as float16 `.npy` (first build about 12 s).

**For other worlds:** change the band table (ice giants: pale cyan bands with low contrast; hot Jupiters: dark red with a glowing night side), the vortex list and the noise anisotropy.

### Lit sphere renderer (`sphere_layer` / `draw_sphere`)
For each pixel of the on-screen bounding box (computed on a capped grid):

```
nx, ny = (x-cx)/R, (y-cy)/R ;  inside = nx²+ny² < 1 ;  nz = sqrt(1 - nx² - ny²)
lat = asin(-ny) ;  lon = atan2(nx, nz) + rot        # rot animates rotation
texel = tex[(0.5 - lat/π)·H, (lon/2π)·W]            # bilinear when magnified
lit   = clip(n·L·1.15 + 0.05)^0.85                  # L = upper-left light
shade = lit·(1 - limb + limb·nz^0.5) + ambient      # limb darkening
+ warm terminator scatter;  alpha = 1-px anti-aliased edge
```

Then add a **thin atmospheric rim** (radial gradient ring at about 0.95 R, `#ffd9a0` for Jupiter, `#7fb8ff` for Earth). The longitude facing the camera is `rot`, so to center a feature at texture longitude λ, set `rot = λ`. Its screen y is `cy + sin(−lat)·R`.

**Do not zoom a low-resolution texture too far** (the Earth zoom went blocky at R = 2400 px). Cap the zoom or switch to a dedicated close-up drawing.

### Clouds and haze sprites
- **Cloud sprite (512×300):** 16–24 Gaussian blobs arranged in an arch (bigger in the middle), modulated by low-frequency noise, a flat-ish base, `smoothstep` alpha, shading = brighter top + **top-edge rim highlight** (from the vertical alpha gradient) + darker underside. Eight variants, drawn tinted with a color-matrix filter (`tint_cf`).
- **Haze sprite (1024×220):** horizontally tiled noise in a Gaussian vertical profile, used for deep-fluid streaks.
- **Starfield:** 900 stars with a power-law magnitude, three tints, per-star twinkle phase and parallax depth. The brightest get a soft halo.
- **Overlays:** a quarter-resolution vignette image and six half-resolution grain frames (overlay blend at 4.5% opacity, cycled at 24 fps).

## 4.8 Environments (common.py)

- **`space(c, t, zoom, ox, oy)`**: cached navy gradient + radial nebula wash + parallax starfield.
- **`cloud_world(c, t, fall, drift, tint, bg_top, bg_bot, bg_mid, depth_dark, haze, ox, oy)`**: the core descent environment. Four depth layers; each sprite's position is `(base + velocity·depth·t) mod span`, so the motion is infinite and seamless. `fall` > 0 makes clouds rise past the camera (the viewer is falling). Tint and background shift with depth. **This one function produced about 40% of the film's shots.**
- **`deep_env(c, t, depth)`** (scenes3): gradient interpolates amber → dark red → violet as `depth` 0→1, with drifting haze sprites.
- **`speed_lines`** (entry streaks, hyperspace), **`particles`** (dust, snow, sparks), **`flash`**, **`depth_ruler`** (scrolling ticks).
- **Texture strip flow (`s12`):** horizontal slices of the planet texture scrolled at alternating speeds per latitude, which reads as **jet streams shearing**.

## 4.9 Props and characters (elements.py)

All vector, built from paths with linear/radial gradient shaders, for a "premium 2D illustration" look:

- **Galileo entry probe** (side view): blunt-cone heat shield + gold conical afterbody with blanket seams. The `heat` parameter blends the shield to orange and adds shock-layer glows.
- **Parachute + descent module:** canopy cubic path with scalloped hem, stripes clipped to the canopy, suspension lines; `openk` uses `e_back` for the bloom; `transmit` draws expanding radio arcs upward.
- **Juno:** hexagonal bus + three blue solar arrays (one shorter with a magnetometer boom).
- **Capsule and explorer:** see Part III §3.3. The explorer is drawn *inside* the capsule window through a circular clip, so the character acts during exterior shots.
- **Cross-section (`draw_cross_section`)**: draw the textured sphere, then clip to a **pie wedge** (`wedge=(a0, a1)` in degrees) and paint layered radial gradients: molecular envelope (amber → red-brown), metallic region (indigo, with animated glow blobs), and core (`core_fuzz` 0 = sharp compact ball with a rim, 1 = broad diffuse gradient + 160 scattered "heavy element" dots). `dark_unknown` blacks out the interior for "unexplored". `highlight` outlines a layer. **Animating `core_fuzz` 0→1 produced the fuzzy-core peak.** Prefer a half cutaway (`(-90, 90)`); narrow wedges make a distracting apex.
- **Dipole field lines:** `r = L·R·sin²θ` per L-shell, dashed with an animated phase (flow), plus a blurred glow pass; `stroke_path_k` animates the drawing-on.
- **Labels:** `label_line` (dot + ring + leader line drawn with follow-through, then text and sub-text). **Auto-clamps inside the frame.** `draw_tag` (honesty pills), `card`, `chapter_card`, `big_number`, `draw_x` / `draw_check` (two-stroke animated marks with glow).

## 4.10 Shot authoring pattern

```python
def s20(c, t):                                   # SHOT 20 — 228 g (visual peak)
    bg(c, '#1a0806', '#4a140a')                  # 1. environment
    k = 1 - e_out(prog(t, T_DECEL, T_DECEL + 3.5))
    speed_lines(c, t, .2 + .5*k, direction=(.5, .86), speed=600 + 3000*k)   # 2. motion layer
    sx, sy = shake(t, T_DECEL, 2.2, 38, freq=16)                            # 3. camera
    c.save(); c.translate(sx, sy)
    draw_galileo_entry(c, 520, 560, .9, 55, heat=.7*k + .2, t=t)            # 4. subject
    g = 228 * e_out(prog(t, T_228 - 1.2, T_228 + 1.6))                     # 5. data synced to speech
    draw_gauge(c, 1300, 470, 230, g/260, 'DECELERATION', f'{int(g)} g', warn_from=.35)
    c.restore()
    flash(c, (1 - e_out(prog(t, T_DECEL, T_DECEL + .5))) * .6, '#ff6040')  # 6. accent
    draw_tag(c, 'GALILEO PROBE · MEASURED PEAK ≈ 228 g', 40, 36, 'hist')    # 7. honesty tag
```

**Order inside every shot:** environment → motion layers → camera transform → subject/character → data, labels and instruments synced to speech → accents (flash, glow) → honesty tag (always last, always top-left).

**Registering shots:**

```python
SHOTS2 = [ (T_HIT, s18, ('flash', .35)), (T_DARKNESS, s19, ('fade', .6)), (T_DECEL, s20, ('cut', 0)), ... ]
```

A shot runs from its start time until the next shot's start. During a transition, `render.py` draws the previous shot at the current `t` too, so both keep moving through the transition.

## 4.11 Transitions and post (render.py)

- `fade`: render both shots, alpha-blend the new one with `e_sine`.
- `black`: first half fades the old shot to black, second half fades the new one in.
- `flash`: new shot plus a warm-white overlay decaying with `e_out`.
- `whip`: old shot slides out / new slides in by 60% of the frame width, with 7 offset copies at decreasing alpha for motion blur.
- **Post on every frame:** vignette → film grain (overlay 4.5%) → global fade-out in the last 1.6 s before `END_T`.

## 4.12 Rendering and encoding

```bash
python3 render.py still 650.6 frame.png              # one frame
python3 render.py contact 0 60 1.5 sheet.png 5       # QA grid: t0, t1, step, cols
python3 render.py bench 2 30 160 450 610             # ms per frame at sample times
./render_all.sh <project> <out> 8 4 60               # segments, parallel jobs, fps
```

Each segment worker pipes raw BGRA into `ffmpeg -f rawvideo -pix_fmt bgra -s 1920x1080 -r 60 -i - -c:v libx264 -preset faster -crf 18 -pix_fmt yuv420p -tune animation -threads 2`. Then `concat` with `-c copy` and mux the audio: `-c:a aac -b:a 256k -movflags +faststart`. Jupiter: 8 segments × about 5,600 frames, 186 MB final at about 2 Mbps (flat 2D compresses very well).

**Monitor long renders** with a background job plus a progress monitor that also matches failure strings (`Traceback|Error|FAIL`). Spot-check a finished segment's frame **before** the others finish.

## 4.13 The contact-sheet QA loop (the most important habit)

1. After writing a batch of shots, render a contact sheet across its time range (5 columns, 25% scale, timestamps on each tile).
2. Inspect every tile: focal point, safe area, **label clipping**, overlaps, wrong tag, sync (is the number already on screen before it is spoken?), empty or black frames, blocky textures, unreadable small text.
3. Fix and re-render the sheet. Only then render the film.

**Bugs this loop caught on Jupiter:** labels running off the right edge (fixed by auto-clamping in `label_line`), a title overlapping a callout, a blocky Earth zoom (zoom capped), a distracting cutaway apex (switched to a half cutaway), a tint passed as a float instead of an RGB tuple (crash), and black frames that were only the provisional end fade (`END_T` before the final scenes file existed).

## 4.14 Building assets for a new topic

Reuse first: space, stars, cloud world, deep environment, explorer, capsule, all instruments, labels, tags, transitions, cross-section (re-colored), field lines, particles. Then build only the topic's **hero assets** using the same techniques (Part X gives recipes):

- **New celestial bodies:** new band table or texture recipe → `draw_sphere(tex, …)`.
- **Galaxies:** a particle-based spiral (logarithmic arms, `r = a·e^(bθ)`, thousands of additive dots with color by age) and a bulge glow.
- **Black holes / lensing:** black disk + photon ring + accretion disk as a squashed ellipse ring with a Doppler brightness asymmetry; background stars displaced radially near the hole.
- **Universe-scale:** a cosmic-web filament network (random points + nearest-neighbor lines with glow), expanding grids for spacetime.
- **Parallel universes:** split-screen mirrors, branching timelines (tree of paths drawn on with `stroke_path_k`), bubble universes (translucent spheres with internal starfields).


---

# PART V — THE SOUND DESIGN ENGINE (HOW THE SOUNDTRACK IS BUILT)

The soundtrack is built in code, like the picture, on the **same narration timestamps**. It has four buses: **Voice**, **Music**, **SFX** (designed hits and events) and **Ambience** (beds and textures). All buffers are float32 stereo at 48 kHz in NumPy. The library is `engine/sfxlib.py`; each film adds one cue sheet, `mix.py` (Jupiter: `example_jupiter/mix.py`).

## 5.1 Sound philosophy (the channel's rules)

1. **Narration is the primary information channel.** Nothing may mask a key sentence (principles 021, 030).
2. **Every sound has a narrative job.** Sounds clarify action, reveal what the image hides, and mark story turns. No effect on every cut or every camera move (002, 013, 164).
3. **Contrast creates meaning.** Peaks only feel big if the surrounding sound is restrained. Silence and the absence of music are active choices (019, 081, 110, 131).
4. **An audio arc across the whole runtime.** Each chapter gets an identifiable but coherent palette, and music changes only at real story turns (109, 271–274).
5. **Honesty.** Designed sounds are never presented as real recordings from space (241–248). Every effect is synthesized, so there are no licensing risks (288).

## 5.2 Voiceover pipeline

- Decode and resample to 48 kHz stereo.
- Processing chain (`VO_CHAIN`): **high-pass 70 Hz** (removes rumble, principle 024) → **+1.5 dB presence at 3 kHz** (Q 1.2, phone-speaker intelligibility, 075) → **gentle compression** (threshold −20 dB, 2.5:1, attack 8 ms, release 120 ms, +2 dB makeup; controls without erasing expression, 082).
- The voiceover is placed at t = 0 and is **never time-edited**.
- Its loudness envelope drives the ducking (§5.7).

## 5.3 Music analysis (do this before designing)

Run `music_energy(track)` for every supplied track: RMS dB in 4-second steps. Classify the sections:

| Jupiter track | Length | Energy shape (RMS dB) | Character | Use |
|---|---|---|---|---|
| Dramatic cinematic documentary | 3:17 | soft −32…−23 until 0:36, build at 0:40, full −13…−11 from 0:44 to 2:36, soft outro −25 from 2:40 | documentary build | Opening and deep-interior chapters |
| Suspense cinematic | 3:21 | constant −9…−11 throughout | steady tension bed | Inside the clouds → signal lost; core mystery |
| Inspiring cinematic | 2:12 | soft −22…−18 until 0:32, full −10…−8 from 0:36 to 1:44, outro from 1:48 | uplifting resolution | The answer + ending |

Match energy to narrative energy (103): **land a track's build on a story escalation and its full section on the big middle of a chapter, and let its outro coincide with a chapter ending.**

## 5.4 The music cue map method

1. Mark the **story turns** in the transcript (new chapter, entry into danger, arrival, the historical loss, the deep mystery, the answer).
2. Assign each section the track whose mood and energy fits. **Use fewer tracks for continuity** (108); reusing a track's *different section* later is fine.
3. **Plan the gaps.** Music drops out where designed sound must carry the drama or where silence lands a moment harder.
4. **Entries and exits** happen at purposeful points with fades shaped to the phrasing (111–113). A sharp cut is reserved for a dramatic event (the signal loss).
5. Write each cue as `cue(bus, track, t_program, t_track, duration, fade_in, fade_out, gain_db)`.

**Jupiter cue map (reference):**

| Program time | Cue | Purpose |
|---|---|---|
| 0:00 → ~2:30 | Drama 0:00→, gain −3 dB, 3 s fade out | The soft intro carries the hook and the build lands on the plan; the full section carries scale, Juno and speed |
| 2:29 → 3:37 | **No music.** Designed entry roar, riser, 228 g impact | Danger carried by physical sound alone (110) |
| 3:36 → 6:31 | Suspense 0:00→, −6 dB, 4 s fade in | Inside the clouds, instruments, rising pressure, Galileo's measurements |
| 6:31 | **Hard cut to near-silence** (0.25 s fade) on "the signal was lost" | The emotional low point; a flatline tone and dark drone only |
| 7:07 → 9:31 | Drama from 0:28, −4 dB | Interior journey: dense fluid, metallic hydrogen, magnetic field |
| 9:28 → 10:42 | Suspense from 0:40, −9 dB | The core mystery, hypotheses, "no camera has photographed it" |
| 10:41 → end | Inspiring from 0:14, −2 dB, 4 s fade out | The answer "NO.", recap, the humbling night-sky ending; its outro sits under the end card |

## 5.5 Synthesized SFX library (`sfxlib.py`)

Every effect is generated procedurally from sine oscillators, filtered noise (FFT brick-shaped band-pass, `fft_filter`) and envelopes. Parameters are chosen per event (scale and weight matched to the visual, 152–153).

| Function | Recipe | Use for | Typical call |
|---|---|---|---|
| `boom(dur, f0, f1, amp, noise_amt, hi)` | Sine pitch-drop f0→f1 (exp decay) + low-passed noise burst; 200-sample attack ramp | Impacts, reveals, chapter hits, title. Attack + body + tail (062) | Big hit: `boom(5, 90, 25, 1.0, .9, 3000)`; reveal: `boom(4, 60, 30, .45, .4)`; soft: `boom(3, 50, 28, .3, .2)` |
| `whoosh(dur, lo, hi, amp, peak)` | Band-passed noise, asymmetric envelope peaking at `peak`, left→right pan drift | Whip transitions, flybys, zoom-throughs. Duration matched to motion (161) | Whip: `whoosh(.5, 400, 5000, .3)`; flyby: `whoosh(3, 200, 3000, .3, .5)` |
| `riser(dur, amp)` | Exponential pitch sweep (3 octaves) + fifth + high noise, envelope^2.2, clean end | Only before a genuine event (171): deceleration, metallic H reveal, fuzzy core, "NO." | `riser(T_event - T_start, .2–.3)` |
| `rumble(dur, amp, lo, hi, mod)` | Band-limited noise with 0.7 Hz modulation | Entry roar, approach, pressure | Entry: shaped by an envelope keyed to the narration (§5.6) |
| `blip(f, dur, amp)` / `ui_pop()` | Sine with fast exp decay / two-tone pop | Instrument readouts, counters, telemetry, check marks | Telemetry: `blip(1000, .08, .12)` every 0.45–0.5 s |
| `alarm(dur, amp)` | Alternating 880/660 Hz square+sine, low-passed | Lethal warnings, "NONE DETECTED" | `alarm(1.6, .12)` |
| `tone(f, dur, amp)` | Pure sine with fades | **Flatline** after signal loss | `tone(1000, 2.5, .09, .005, 2.0)` |
| `static(dur, amp)` | High-band noise gated at 60 Hz random | Signal loss, transmission glitches | `static(.6, .35)` |
| `creak(dur, amp, f0)` | Wobbling harmonic tone + 23 Hz amplitude modulation, band-passed | Hull stress at 5 / 10 / 15 bar, separation | `creak(1.2, .18–.28, 70–56)` (deeper as pressure rises) |
| `shimmer(dur, amp)` | Five high partials with slow independent amplitude modulation, stereo offset | Wonder, the fictional/indestructible shield, discoveries, night sky | `shimmer(3, .08)` |
| `crackle(dur, amp, rate)` | Random filtered micro-bursts panned across the stereo field | Electric conductivity, radiation | `crackle(dur, .08, 6)` under the metallic-hydrogen chapter |
| `hum(dur, amp, f)` | 55 Hz + harmonics, slow tremolo | Magnetic field / dynamo | Under the magnetic-field section |
| `drone(dur, amp, fs)` | Detuned low chord + low noise, stereo offset | Mystery beds, the silence after the loss, opening bed | `drone(9, .10, (41.2, 61.7, 82.4))` |
| `wind(dur, amp, hi)` | Band-passed noise with two slow LFOs | Cloud ambience; lower `hi` = deeper and more muffled | `wind(dur, .08–.16, 900–2500)` |
| `chute_snap()` | Whoosh + sharp filtered snap at 0.68 s | Parachute deploy | `place(sfx, chute_snap(.35), T_CHUTE - .2)` |
| `thud(amp)` | Short boom 140→60 Hz | X marks, cards landing, small consequences | `thud(.18–.25)` |

**Variation rule (059, 156, 170):** never reuse identical parameters for repeated events. Vary duration, pitch and amplitude, as with the three escalating pressure hits.

## 5.6 Writing the cue sheet (`mix.py`)

The cue sheet imports the scenes modules, so **every SFX time is a narration constant**:

```python
place(sfx, riser(S2.T_DECEL - S2.T_DARKNESS, .3), S2.T_DARKNESS)     # anticipation (126, 172)
place(sfx, boom(5, 90, 25, 1.0, .9, 3000), S2.T_DECEL)               # biggest hit = biggest reveal (018)
place(sfx, boom(3, 70, 30, .55, .5), S2.T_228B)                       # smaller repeat on the repeated number
for i, tt in enumerate((S2.T_FIVE, S2.T_TEN, S2.T_FIFTEEN)):          # escalating, varied (123, 156)
    place(sfx, boom(1.6, 80, 40, .35 + .1*i, .6), tt)
    place(sfx, creak(1.2, .18 + .05*i, 70 - 8*i), tt + .1)
place(sfx, static(.6, .35), S2.T_LOST - .35)                          # the loss
place(sfx, tone(1000, 2.5, .09, .005, 2.0), S2.T_LOST + .2)           # flatline into silence
```

**Placement conventions**

- **Impacts** land exactly on the visual contact or reveal frame (151). Add a micro-pause or riser before the biggest ones (158).
- **Whooshes** start about 0.2–0.3 s **before** a whip so the loudest point meets the fastest motion (166).
- **UI pops** land 0–0.2 s before the number appears, so sound and picture register together.
- **Entry roar envelope:** build the noise once, then multiply by a piecewise envelope keyed to the story: `[start .15] → [glow .45] → [deceleration .7] → [+3 s .5] → [human-survival line .12] → [shaking stops 0]`.
- **Ambience beds** (wind, drone, hum, crackle) span whole sequences with 1–3 s fades and change when the viewpoint changes (189).
- **Don't stack** redundant effects on one action (047). Remove any effect that doesn't earn its place (070, 160).

**Jupiter used about 120 cues.** Signature moments: opening sub-boom + drone; telemetry beeps → flatline + static; scale pull-out whoosh; the three-question thuds; "nowhere to land" boom; Juno flyby whoosh; plunge riser + flash boom; speed counter ticks; entry roar → riser → 228 g impact; parachute snap; horizon shimmer + alarm; lethal alarm; pressure hits + creaks; signal loss static + flatline + dark drone; metallic-hydrogen riser + boom + shimmer + crackle bed; magnetic hum; fuzzy-core riser + shimmer; collision boom; "NO." riser + boom; recap pops; night-sky shimmer; end-card boom.

## 5.7 VO-keyed ducking (automatic mixing around narration)

```
env  = RMS of |voice| over 20 ms windows, normalized to its 90th percentile, clipped 0..1
env  = one-pole smoothing: attack 30 ms, release 450 ms   (natural recovery, 084)
duck = 1 - 0.62 * clip(env * 1.4, 0, 1)                    # about -8.4 dB under full speech
music *= duck ;  ambience *= 1 - 0.45 * clip(env * 1.4)    # beds dip less than music
```

This replaces manual volume automation (117) and keeps the first word after every cut clear (028). Music swells naturally in the pauses between sentences.

## 5.8 Bus levels (before finishing)

| Bus | Gain | Notes |
|---|---|---|
| Voice | 0 dB | After the VO chain |
| Music | −9 dB, plus per-cue −2 … −9 dB, plus ducking | Ends up about 10–12 dB under the voice during speech |
| SFX | −3 dB | Individual amplitudes set per cue |
| Ambience | −4 dB, plus ducking | Subtle; it sustains attention in slow scenes (278) |

## 5.9 Loudness finishing

1. Measure the raw mix's integrated loudness (EBU R128 via ffmpeg `ebur128`).
2. Apply a **static gain** to reach **−14 LUFS** (YouTube's practical playback context, 091).
3. Apply a **brick-wall limiter** (`alimiter`, limit −2 dBFS, attack 3 ms, release 120 ms) so true peak ends ≤ −1.5 dBTP (093, 098).
4. **Do not use loudnorm's dynamic mode.** It raises quiet passages and would fill the deliberate silence after the signal loss. Preserve dynamic range (081, 094).

Jupiter result: **−14.2 LUFS integrated, −1.4 dBTP**, short-term levels checked at the riser (−10.5 dB mean), the impact, the silence and the "NO.".

## 5.10 Audio QA (measured, because the session cannot listen)

- Report integrated LUFS and true peak of the final file.
- Measure short-term or mean level in 2 s windows at each peak and at each planned silence, and confirm the silence really is quieter.
- Confirm the voice is clearly above the music: compare the voice-only RMS with the music bus under speech (target ≥ 10 dB separation).
- Confirm no clipping (peak ≤ −1.4 dBFS) and that the music ends cleanly under the end card.
- **Tell the owner the mix was verified by measurement and should be listened to before publishing** (principles 280–283, 289).


---

# PART VI — THE 300 PRINCIPLES OF SOUND DESIGN

*A practical field guide for YouTube Shorts, long-form videos, animation, documentaries and cinematic storytelling. Use these principles as a decision-making checklist, not as inflexible rules. Effective sound design serves the story, maintains clarity and creates deliberate contrast.*

Each chapter ends with **How this channel applies it**, showing exactly how the principle set was implemented in the engine and cue sheet.


## 6.1 Story-First Sound

1. Define the emotion before selecting a sound.
2. Give every major sound a narrative purpose.
3. Prioritize sounds that clarify the action.
4. Use audio to reveal what the image hides.
5. Establish the sonic world in the opening seconds.
6. Let the story dictate density, not the plugin collection.
7. Reserve distinctive sounds for distinctive events.
8. Build a sonic motif for recurring ideas.
9. Change the sound palette when the story changes.
10. Remove any sound that distracts from the intended meaning.

> **How this channel applies it:** Every effect in the cue sheet is tied to a narrated event; the opening boom + drone establish the sonic world in the first frame.


## 6.2 Attention And Retention

11. Make the first audible event immediately relevant.
12. Use contrast to reset attention at meaningful beats.
13. Do not punctuate every cut with a whoosh.
14. Introduce a new sonic idea before a long section feels static.
15. Use brief silence to make a reveal feel larger.
16. Align audio payoffs with promised story payoffs.
17. Keep transitions audible but not predictable.
18. Make the strongest impact coincide with the strongest reveal.
19. Avoid constant intensity that makes peaks meaningless.
20. Design curiosity through withheld sonic information.

> **How this channel applies it:** Hook boom on frame 1; contrast resets at chapter turns (music drop at entry, hard cut at signal loss); risers only before real payoffs.


## 6.3 Voice Intelligibility

21. Treat dialogue as the primary information channel.
22. Choose music that leaves room for speech frequencies.
23. Lower competing effects during essential words.
24. Remove low-frequency rumble from voice recordings.
25. Control harsh consonants without dulling articulation.
26. Keep vocal loudness consistent across edits.
27. Edit breaths deliberately rather than deleting all of them.
28. Avoid masking the first word after a cut.
29. Check intelligibility at phone-speaker volume.
30. Never sacrifice a key sentence for a dramatic effect.

> **How this channel applies it:** VO chain (HPF 70 Hz, +1.5 dB @ 3 kHz, 2.5:1 compression) + automatic ducking keeps every key sentence clear.


## 6.4 Recording Discipline

31. Record the cleanest possible source before processing.
32. Monitor through headphones while recording.
33. Set input gain to avoid clipping.
34. Record several seconds of room tone.
35. Maintain consistent mouth-to-microphone distance.
36. Use a pop filter to tame plosives.
37. Move away from fans and reflective surfaces when possible.
38. Capture alternate takes for difficult lines.
39. Label takes while the session is fresh.
40. Check for clicks, dropouts, and distortion before wrapping.

> **How this channel applies it:** Delivered voiceover is used as-is; if re-recording, follow these when requesting takes.


## 6.5 Editing Fundamentals

41. Cut at natural pauses when possible.
42. Add short fades to prevent digital clicks.
43. Use crossfades only when they improve continuity.
44. Trim unused tails without cutting natural decay.
45. Keep synchronized effects attached to their visual event.
46. Listen across edit boundaries rather than in isolation.
47. Avoid stacking redundant effects for the same action.
48. Preserve timing differences that make movement believable.
49. Name and color-code tracks by function.
50. Save reversible edits and original source files.

> **How this channel applies it:** Effects are placed per cue, never per cut; fades on every clip (`fade_env`) prevent clicks; the narration is never edited.


## 6.6 Sound Selection

51. Choose sounds for meaning before realism.
52. Prefer specific recordings over generic stock effects.
53. Match sound scale to object scale.
54. Match material texture to the visible surface.
55. Select recordings with suitable perspective.
56. Avoid recognizable stock effects used everywhere.
57. Use a simpler effect when detail is not audible.
58. Consider whether an effect belongs in the scene.
59. Choose variations to prevent obvious repetition.
60. Audit every effect for unintended background noise.

> **How this channel applies it:** All sounds are synthesized to fit their object: weight and pitch scaled to scale (a probe vs. a planetary event).


## 6.7 Layering Effects

61. Give each layer a distinct job.
62. Build impacts from attack, body, and tail.
63. Avoid piling up layers in the same frequency band.
64. Start with one convincing source before adding layers.
65. Use transient layers to create definition.
66. Use low-end layers sparingly to suggest mass.
67. Use texture layers to convey material.
68. Time-align layers only when phase and feel benefit.
69. Vary layer lengths to preserve depth.
70. Mute each layer to test whether it earns its place.

> **How this channel applies it:** Impacts = sub pitch-drop (body) + noise burst (attack) + decay (tail); test each layer's contribution.


## 6.8 Frequency Management

71. Identify frequency conflicts before boosting anything.
72. High-pass sources that contain unnecessary sub-bass.
73. Preserve low frequencies for moments requiring weight.
74. Cut resonances rather than applying broad dulling.
75. Use midrange clarity for small speakers.
76. Avoid excessive high-frequency brightness.
77. Check bass-heavy sounds on multiple playback systems.
78. Use equalization to separate voice, music, and effects.
79. Apply EQ in context rather than in solo.
80. Compare processed and unprocessed signals at matched level.

> **How this channel applies it:** VO high-passed; music ducked under speech; low end reserved for the biggest hits; midrange presence for phones.


## 6.9 Dynamics

81. Preserve dynamic range so loud moments feel loud.
82. Use compression to control, not erase, expression.
83. Set attack times with transient shape in mind.
84. Set release times to recover naturally between events.
85. Avoid clipping on individual tracks and the master.
86. Use automation before extreme compression when appropriate.
87. Do not normalize every effect to the same loudness.
88. Reserve headroom for unexpected peaks.
89. Limit only as much as the delivery format needs.
90. Listen for pumping when multiple elements compete.

> **How this channel applies it:** Ducking with 30 ms attack / 450 ms release; static gain + limiter instead of heavy compression; quiet moments preserved.


## 6.10 Loudness And Delivery

91. Target the platform's practical playback context.
92. Measure integrated loudness for the finished program.
93. Measure true peaks to reduce encoding overs.
94. Avoid chasing a loudness number at the cost of clarity.
95. Compare reference videos at matched perceived level.
96. Check whether quiet dialogue remains understandable.
97. Use consistent loudness between related episodes.
98. Leave safety headroom before lossy encoding.
99. Review the final encoded export, not just the timeline.
100. Document export settings for repeatable results.

> **How this channel applies it:** Final: −14 LUFS integrated, ≤ −1.5 dBTP, measured on the delivered file; settings documented in sfxlib.finish().


## 6.11 Music Selection

101. Choose music to support the scene's emotional direction.
102. Avoid tracks that compete with narration.
103. Match musical energy to narrative energy.
104. Prefer music with usable changes in arrangement.
105. Check licensing before publishing.
106. Use musical rhythm to support editing cadence.
107. Do not force every scene into a musical beat.
108. Use fewer tracks when continuity matters.
109. Change music at an actual story turn.
110. Let the absence of music carry emotion when appropriate.

> **How this channel applies it:** Tracks chosen per chapter mood by measured energy curve; music absent during entry; licensed tracks only.


## 6.12 Music Editing

111. Enter music at a purposeful moment.
112. Exit music before it overstays its narrative role.
113. Fade music with attention to phrasing.
114. Cut on musical structure when possible.
115. Use stems to reduce competing instruments.
116. Create a short transition rather than an abrupt unrelated switch.
117. Automate music level around narration.
118. Avoid looping a recognizable phrase too frequently.
119. Keep low-end music under control during impacts.
120. Check whether the scene still works without music.

> **How this channel applies it:** Cues enter at story turns with phrase-shaped fades; hard cut only for the signal loss; auto-ducking replaces manual rides.


## 6.13 Rhythm And Pacing

121. Use sound to reinforce the pace of visual cuts.
122. Slow sonic rhythms during reflection.
123. Increase event frequency only when stakes rise.
124. Avoid repetitive one-effect-per-cut patterns.
125. Leave breathing space between major impacts.
126. Use anticipation before a consequential event.
127. Delay an effect intentionally only when it improves perception.
128. Make fast passages rhythmically readable.
129. Break established rhythm to mark a surprise.
130. Allow resolution after sustained tension.

> **How this channel applies it:** Fast sound events in danger, sparse in explanation; three escalating, varied hits for 5/10/15 bar.


## 6.14 Silence And Negative Space

131. Treat silence as an active design choice.
132. Cut ambience selectively to create unease.
133. Use near-silence instead of absolute digital silence when natural.
134. Leave space after an emotionally important line.
135. Avoid filling every gap with a sound effect.
136. Use silence to focus attention on a small detail.
137. Contrast quiet moments with later sonic peaks.
138. Protect intentional pauses from automatic noise gates.
139. Return ambience gradually after a dramatic drop.
140. Test whether silence communicates without confusing viewers.

> **How this channel applies it:** Near-silence after the signal loss (flatline + low drone), a deliberate design choice, protected from the loudness pass.


## 6.15 Transitions

141. Transition audio according to the story relationship between scenes.
142. Use sound bridges to connect related locations.
143. Carry ambience across a cut when continuity is desired.
144. Change ambience sharply when disorientation is intended.
145. Avoid the same riser for every transition.
146. Use pre-lap sound to introduce the next scene.
147. Allow reverb tails to connect shots when appropriate.
148. Keep transition effects shorter than their narrative value.
149. Match transition intensity to the importance of the cut.
150. Check that transition effects do not obscure new dialogue.

> **How this channel applies it:** Whooshes only on whip transitions and real movement; dips to black get bass hits only at chapter changes.


## 6.16 Impacts And Hits

151. Sync the attack to the perceived contact frame.
152. Match impact weight to visible mass and speed.
153. Combine sharp attack with body only when needed.
154. Keep impact tails proportionate to the space.
155. Use restrained sub-bass for large events.
156. Vary repeated impacts to prevent mechanical sameness.
157. Avoid giant cinematic hits for trivial actions.
158. Place a micro-pause before a major hit when effective.
159. Test impacts at low playback volume.
160. Remove unnecessary impacts that weaken the biggest one.

> **How this channel applies it:** Biggest boom on the deceleration; smaller repeat on the repeated number; no giant hits on trivial actions.


## 6.17 Whooshes And Movement

161. Match whoosh duration to movement duration.
162. Match pitch motion to perceived movement direction.
163. Use stereo movement only when it serves the scene.
164. Avoid whooshes on every camera movement.
165. Choose airiness or weight according to the object.
166. Sync the loudest point to the fastest perceived motion.
167. Use shorter whooshes for quick gestures.
168. Keep movement effects behind essential narration.
169. Layer cloth or friction for physical authenticity.
170. Use variation so repeated motion does not sound copied.

> **How this channel applies it:** Whoosh length matches the transition (0.5 s whip, 3 s flyby); peak timed to the fastest motion.


## 6.18 Risers And Anticipation

171. Use risers only when an event is genuinely approaching.
172. Match riser length to the buildup.
173. Increase intensity through arrangement, not volume alone.
174. Avoid resolving every riser with the same boom.
175. End a riser cleanly at the intended event.
176. Use pitch rise selectively to imply increasing tension.
177. Use rhythmic acceleration for urgency when suitable.
178. Keep anticipation audible without drowning speech.
179. Use a false resolution sparingly for surprise.
180. Ensure the payoff justifies the buildup.

> **How this channel applies it:** Risers used only before the deceleration, metallic hydrogen, the fuzzy core and 'NO.', each ending cleanly at its event.


## 6.19 Ambience And Environment

181. Establish a location with a small set of telling details.
182. Keep ambience consistent across adjacent shots.
183. Match ambience to indoor or outdoor acoustics.
184. Avoid ambience that contradicts time of day.
185. Use subtle movement in long ambience beds.
186. Keep background sounds below key information.
187. Layer distant and close elements for depth.
188. Use room tone to smooth dialogue edits.
189. Change environment sounds when the viewpoint changes.
190. Remove generic ambience when silence better serves the scene.

> **How this channel applies it:** Wind beds inside clouds (darker as depth increases), crackle for conductive fluid, hum for the magnetic field.


## 6.20 Foley And Tactile Detail

191. Record or choose footsteps that match the surface.
192. Match cloth sounds to garment type and movement.
193. Use small handling noises to make objects tangible.
194. Align foley with visible contact and release.
195. Vary footstep timing with gait and emotion.
196. Do not overemphasize mundane movements.
197. Use close foley for intimacy and detail.
198. Choose textures that support object identity.
199. Preserve natural micro-variation between repeats.
200. Check foley against the visual scale of the shot.

> **How this channel applies it:** The parachute snap, hull creaks and small thuds make objects tangible without overdoing mundane motion.


## 6.21 Space And Reverb

201. Use reverb to suggest believable physical space.
202. Match decay length to room size and material.
203. Keep narration dry enough to remain intelligible.
204. Use pre-delay to preserve the initial transient.
205. Reduce reverb when scenes become sonically crowded.
206. Avoid using the same reverb on unrelated locations.
207. Place distant sounds with level and high-frequency loss.
208. Use early reflections for spatial cues.
209. Check reverb tails at scene changes.
210. Use unnatural reverb only as a deliberate storytelling device.

> **How this channel applies it:** Narration kept dry; space suggested by drone stereo offsets rather than reverb.


## 6.22 Stereo And Perspective

211. Keep critical information reliable in mono.
212. Place sounds according to visible screen direction.
213. Avoid exaggerated panning that distracts headphone listeners.
214. Use width to distinguish environment from central dialogue.
215. Match apparent distance with level and spectral detail.
216. Move a sound smoothly when the source moves smoothly.
217. Check phase compatibility after widening.
218. Keep low bass controlled and generally centered.
219. Use narrow perspective for intimate moments.
220. Audit spatial effects on both headphones and speakers.

> **How this channel applies it:** Bass centered; subtle pan drift on whooshes; stereo offset on beds; critical sound mono-safe.


## 6.23 Tension And Horror

221. Build dread with uncertainty rather than constant loudness.
222. Use subtle low-frequency movement sparingly.
223. Introduce an unsettling texture before revealing its source.
224. Let familiar ambience become slightly unfamiliar.
225. Avoid predictable jump-scare timing.
226. Use quiet detail to draw attention before a shock.
227. Separate psychological tension from physical danger sonically.
228. Allow the audience time to anticipate consequences.
229. Keep dialogue clear even during suspense.
230. Give the aftermath of a scare sonic space.

> **How this channel applies it:** Dread built with low drones and creaks before revealing the cause; aftermath silence after the loss.


## 6.24 Comedy And Surprise

231. Time comedic sounds to the precise visual beat.
232. Use restraint so jokes remain surprising.
233. Choose sound character that matches the humor style.
234. Leave a brief gap when a punchline needs air.
235. Avoid explaining an obvious joke with effects.
236. Use unexpected sonic contrast for a reveal.
237. Keep comedic effects short unless duration is the joke.
238. Vary recurring gag sounds without losing recognition.
239. Let a reaction sound support, not replace, the joke.
240. Check whether humor survives without excessive volume.

> **How this channel applies it:** Used sparingly; the 'improvement, right?' beat is carried by the explorer's smile, not a comic sound.


## 6.25 Documentary And Factual Video

241. Distinguish authentic recordings from designed reconstructions.
242. Never use fabricated audio as undisclosed evidence.
243. Keep spoken facts clearer than dramatic atmosphere.
244. Use archival audio only with appropriate rights.
245. Avoid effects that imply events not supported by the story.
246. Match ambience to the represented location when known.
247. Use restrained music for sensitive subjects.
248. Signal reenactments clearly when audio could mislead.
249. Avoid sensational impacts on serious real-world harm.
250. Verify the provenance of distinctive sourced recordings.

> **How this channel applies it:** Designed sounds never presented as real recordings; historical moments treated with restraint (the probe's loss is solemn).


## 6.26 Animation And Fiction

251. Define a consistent sonic logic for fictional worlds.
252. Exaggerate only the properties the audience must notice.
253. Create character-specific movement signatures.
254. Match stylized sound to visual animation style.
255. Give impossible actions understandable physical cues.
256. Use recurring sonic motifs to support character recognition.
257. Avoid reusing identical effects for every character.
258. Let the environment respond to fictional actions.
259. Use sound to clarify off-screen action.
260. Maintain continuity of invented sound rules across episodes.

> **How this channel applies it:** Consistent fictional sonic logic: the capsule's shield = shimmer; instruments = clean sine blips.


## 6.27 Short-Form Video

261. Make the first second sonically legible.
262. Avoid long musical introductions before the hook.
263. Support each story turn with a distinct audio decision.
264. Use effects to clarify rapid visual changes.
265. Keep narration understandable on mobile speakers.
266. Limit low-frequency-only cues that phones may miss.
267. Do not overload a 20-second story with constant hits.
268. Use quick silence to emphasize a twist.
269. Make the ending audio feel intentional, not cut off.
270. Review the entire short without looking at the screen.

> **How this channel applies it:** First second legible (boom + title); quick silences emphasize twists.


## 6.28 Long-Form Video

271. Create an audio arc across the full runtime.
272. Vary density between explanation and climax.
273. Give sections identifiable but coherent sound palettes.
274. Use music changes to mark major chapter shifts.
275. Avoid fatigue from continuous high-energy scoring.
276. Reintroduce sonic motifs at meaningful callbacks.
277. Maintain voice consistency across recording sessions.
278. Use ambience to sustain attention during slower scenes.
279. Audit repeated stock effects across the whole episode.
280. Listen to the full program once without stopping.

> **How this channel applies it:** Audio arc across 12 minutes: documentary → raw physical sound → suspense → silence → documentary → mystery → uplift.


## 6.29 Quality Control

281. Listen on headphones and small speakers.
282. Check mono playback for missing elements.
283. Review at both low and moderate volume.
284. Inspect waveform peaks without relying on appearance alone.
285. Check for clicks at every abrupt edit.
286. Check transitions for leftover tails and sudden noise.
287. Confirm dialogue remains audible under the busiest section.
288. Verify no unauthorized or unlicensed audio remains.
289. Export a test and listen to the actual file.
290. Keep a checklist of recurring mistakes for the next project.

> **How this channel applies it:** Measured QA: LUFS, true peak, window levels at peaks and silences; owner told to listen before publishing.


## 6.30 Workflow And Creative Judgment

291. Organize assets so good sounds are easy to retrieve.
292. Keep a reusable library with clear descriptive names.
293. Separate dialogue, music, ambience, and effects into buses.
294. Create presets as starting points rather than rigid rules.
295. Compare decisions against a clear reference at matched level.
296. Work from broad emotional shape to fine sonic detail.
297. Take short listening breaks to reset perception.
298. Ask what the audience should feel at each beat.
299. Prioritize the three most important fixes before polishing.
300. Judge success by storytelling impact, not the number of effects.

> **How this channel applies it:** Buses separated (voice, music, sfx, ambience); reusable library (sfxlib) + per-project cue sheet.



---

# PART VII — QUALITY CONTROL & SCORING

## 7.1 Per-shot checklist (from contact sheets)

Check every shot for: clear focal point · one primary idea · relevance to the narration · readable in half a second · a meaningful change · correct motion timing and easing · composition · mobile readability · bottom-15% safety · character consistency · scientific accuracy and the correct honesty tag · motivated camera · a meaningful transition · emotion · depth layering · continuity · audio sync · retention contribution · feasibility.

**Inspect for:** flicker, warped characters, inconsistent geometry, unreadable text, broken perspective, labels clipped at frame edges, overlapping labels, black or empty frames, blocky textures, numbers appearing before they are spoken.

Reject critical clarity, continuity or science failures. Revise any non-critical score below 8/10.

## 7.2 Retention scoring rubric (editorial; design quality, not measured audience retention)

| Criterion | Weight |
|---|---|
| Visual clarity | 15% |
| Narrative relevance | 15% |
| Motion quality | 15% |
| Pacing | 15% |
| Camera direction | 10% |
| Visual curiosity | 10% |
| Character acting | 5% |
| Scientific visualization | 5% |
| Continuity | 5% |
| Technical feasibility | 5% |

Below 95/100: name the weaknesses and revise honestly. Never inflate scores. Never claim measured YouTube retention without analytics.

## 7.3 Final delivery checklist

- [ ] `ffprobe`: 1920×1080, 60 fps, frame count = ceil(END_T × 60), duration ≈ END_T
- [ ] Frames extracted from the **encoded file** at every visual peak and inspected
- [ ] Audio: −14 LUFS ±0.5, true peak ≤ −1.4 dBTP, silences verified quieter, voice ≥ 10 dB over music
- [ ] Sync spot-checks: one number reveal, one impact, the end card
- [ ] SRT generated from `words.json` and spot-checked
- [ ] Honesty tags on every shot; approximations marked ≈; no fabricated "photos"
- [ ] Source, scenes, cue sheet and SRT committed; MP4 git-ignored if over 100 MB; files sent to the owner
- [ ] Report written: what was verified and how, known minor issues, offer to adjust

## 7.4 Lessons learned / known failure modes (read before every project)

| Problem seen | Cause | Fix / prevention |
|---|---|---|
| `ImportError: libEGL.so.1` on `import skia` | Missing system GL libraries | `apt-get update && apt-get install -y libegl1 libgl1` |
| Speech model download refused (403) | Hugging Face blocked by the network policy | Use sherpa-onnx **GitHub release** models |
| Very slow image drawing (20–70 ms) | Unpremultiplied RGBA images | Always `to_img()` → premultiplied **BGRA** |
| Labels cut off at the frame edge | Callouts placed near the edge | `label_line` auto-clamps; still check contact sheets |
| Title overlapping a callout | Two texts in the same region | Plan text zones per shot; move headlines to clear areas |
| Blocky planet zoom | Texture magnified beyond its resolution | Cap the zoom or draw a dedicated close-up |
| Odd point at the center of a cutaway | Narrow pie wedge | Use a half cutaway `(-90, 90)` |
| Crash: "float object is not subscriptable" | Passed a float tint instead of an RGB tuple | Tints are always 3-tuples |
| Black frames late in the film during QA | `END_T` came from an earlier file before later scenes existed | The last scenes file must define `END_T` |
| Festoons look like drips | Festoon amplitude too high | Keep the plume exponent high (12) and the amplitude about 2.6° |
| Silence filled in by the loudness pass | loudnorm dynamic mode | Static gain + limiter (`sfxlib.finish`) |
| A number on screen before it is spoken | Counter started too early | Start counters on `at(number words) − 0.2`, end within the spoken word |
| Render far slower than estimated | Heavy sphere frames clustered in one segment | Use 8+ segments with 4 parallel jobs so load balances |
| MP4 cannot be pushed | GitHub 100 MB file limit | `.gitignore` the MP4; deliver it directly |


---

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


---

# PART IX — WORKED EXAMPLE: "WHAT IF YOU ACTUALLY FELL INTO JUPITER?"

**Specs:** 12:28.2 runtime · 54 shots · 44,892 frames · 1920×1080 · 60 fps · H.264 CRF 18 · 186 MB · −14.2 LUFS / −1.4 dBTP · ~120 SFX cues · 3 music tracks · 308 caption lines.

**Inputs:** voiceover (12:20, male documentary voice, 1,535 words); music: *dramatic cinematic documentary*, *suspense cinematic*, *inspiring cinematic*; the Master Prompt V2.0; the 300 Sound Design Principles.

**Chapters and palettes:** Hook & plan (deep space navy + amber) → Nowhere to land (Jupiter amber/cream) → Entry (black → orange-white → red) → Inside the clouds (amber → red-brown, cyan instruments) → Galileo's measurements & loss (sepia amber → black) → Deep interior (dark red → electric violet) → The center (violet + warm cream core) → Answer & ending (navy night sky + warm Jupiter).

## 9.1 Complete shot map (start times from the narration)

| # | Time | In | Shot | Visual | Sound |
|---|---|---|---|---|---|
| 01 | 0:00.0 | cut | **Hook** | Giant Jupiter + tiny probe with glowing trail; title; 'DEC 7, 1995' callout | Sub-boom + low drone on frame 1 |
| 02 | 0:05.8 | fade | **Dropped into Jupiter** | Probe streaks to the limb; entry glow; 'ENTRY SURVIVED' check | Whoosh, rumble swell, UI pop |
| 03 | 0:10.5 | flash | **Winds** | Probe under parachute in shearing clouds; hurricane vs. Galileo wind bars | Wind bed, pops on the bars |
| 04 | 0:15.1 | fade | **No ground** | Vertical descent, rising clouds, scrolling ruler; 'SOLID GROUND: NONE DETECTED' | Wind, soft alarm |
| 05 | 0:18.6 | fade | **58 minutes** | Telemetry monitor: timer to 58:00, waveform flatlines; SIGNAL LOST | Beeps → static → flatline |
| 06 | 0:23.1 | black | **Barely scratched** | Scale pull-out from ×9 to the full cutaway; deepest-point mark; '≈0.2%'; dashed '?' plunge | Long whoosh, mystery drone |
| 07 | 0:33.6 | fade | **Three questions** | Cards: something solid? / an ocean? / the center? with falling capsule; push into the center card | Three thuds |
| 08 | 0:45.4 | fade | **The plan** | Depth column: solid amber 'real spacecraft' vs. dashed blue 'where no spacecraft has gone' | Music build |
| 09 | 0:54.8 | whip | **Earth vs. Jupiter** | Split screen: capsule lands on Earth; on Jupiter 'GROUND?' gets an X | Whip whoosh, landing thud |
| 10 | 1:01.6 | black | **Nowhere to land** | Big statement → full rotating Jupiter; band tracers; CHAPTER 01 | Chapter boom |
| 11 | 1:12.2 | fade | **Great Red Spot** | Zoom to the GRS; label; Earth to scale; 'STRIPES ≠ GROUND' | Slow whoosh |
| 12 | 1:23.2 | fade | **Clouds move** | Texture strips shear in alternating jets; arrows; 'HUNDREDS km/h' | Wind |
| 13 | 1:31.3 | whip | **1,300 Earths** | Earth to scale; Earth icons fill the disk; counter to 1,300+ | Rising blips with the counter |
| 14 | 1:37.7 | fade | **<10 h day** | Fast spin with day ring to 9 h 56 min; jet-stream arrows | — |
| 15 | 1:49.4 | fade | **Juno, 3,000 km** | Planet darkens; Juno flyby; slab cutaway with a wind band and '≈3,000 km' bracket | Flyby whoosh |
| 16 | 2:03.7 | cut | **Storm deep inside** | '3,000 km' number; storm column; plunge zoom + flash | Boom, riser, flash boom |
| 17 | 2:13.6 | flash | **Speed** | Star streaks; counter to 170,000 km/h; '≈47 km every second' | Counter ticks, approach rumble |
| 18 | 2:28.7 | flash | **Entry heating** | Bow-shock arcs, gas arrows converging, heat-shield callout, heat-load bar | Entry roar builds (music out) |
| 19 | 2:44.7 | fade | **Brilliant glow — PEAK** | Screen floods orange-white; plasma streaks; shake | Roar + riser |
| 20 | 2:48.3 | cut | **228 g — PEAK** | Hard shake; gauge slams to 228 g; '× EARTH'S GRAVITY' pulse | Biggest impact; second hit on the repeat |
| 21 | 3:02.6 | black | **Not survivable** | Three cards crossed out: spacecraft / space suit / holding on | Thuds |
| 22 | 3:13.4 | fade | **Robotic probe** | Heat shield falls away; parachute blooms; radio arcs to the orbiter | Separation creak, chute snap, beeps |
| 23 | 3:27.1 | black | **Fictional capsule** | Capsule reveal; glow fades; explorer opens eyes | Downward whoosh |
| 24 | 3:37.0 | fade | **No horizon — PEAK** | Explorer looks up / beside / below; pull back; 'HORIZON: NOT FOUND' | Suspense music in; shimmer + alarm |
| 25 | 3:54.6 | fade | **Earth horizon** | Split: Earth sky/ground/horizon vs. Jupiter 'NO HORIZON' | Cloud wind |
| 26 | 4:05.4 | fade | **Instruments** | Bust lit by the instruments: 1.0 bar, −108 °C with frost, H₂/He bars, O₂ NONE, 'OUTSIDE: LETHAL' | Pops, lethal alarm |
| 27 | 4:36.6 | fade | **Warmer, denser** | Readouts climb; '≈ warm day on Earth'; smile → frown; pressure arrows | Creak |
| 28 | 5:10.3 | cut | **5 / 10 / 15 bar** | Numbers slam in on each word; capsule shakes | Three escalating hits + creaks |
| 29 | 5:15.4 | fade | **Expecting an ocean** | Explorer looks down; dashed 'expected ocean' dissolves | — |
| 30 | 5:35.0 | fade | **Galileo measures** | Historical descent module sampling; instruments list; '!' | Pop |
| 31 | 5:48.8 | fade | **Less water / dry spot** | Expected vs. measured bars (schematic) → the entry site in a dry 'hot spot' | — |
| 32 | 6:07.9 | whip | **Desert analogy** | Earth zoom; a weather station in one desert; '1 location ≠ whole planet' | Whip whoosh |
| 33 | 6:18.4 | fade | **Signal lost** | Probe sinks into red; readouts to 22 bar / 152 °C; static burst | Beeps → static; music hard-cut |
| 34 | 6:31.6 | cut | **58 minutes, destroyed** | Solemn timeline bar; probe fades into the dark | Flatline + dark drone (near-silence) |
| 35 | 6:46.1 | black | **Tiny fraction** | Cutaway with a red mark; depth bar 150 km vs 70,000 km; 'UNEXPLORED ?' | Soft boom |
| 36 | 7:07.4 | black | **Imaginary probe** | Galileo crossed out → shielded capsule 'IMAGINARY · INDESTRUCTIBLE' | Thud, shimmer; drama returns |
| 37 | 7:24.0 | fade | **Compression** | H₂ molecules crowd; density gauge; 'THOUSANDS bar'; gas → dense-fluid bar | Low rumble bed |
| 38 | 7:41.1 | fade | **No splash** | NO SPLASH / NO WAVE / NO WATER LINE / NO SEPARATE SEA cards | Four thuds |
| 39 | 7:55.2 | fade | **Gradual change** | Gradient column; 'NO SURFACE · NO BOUNDARY'; deep fluid interior | — |
| 40 | 8:06.8 | fade | **Metallic hydrogen — PEAK** | Palette flips to electric blue-violet; electrons stream; title | Riser → boom + shimmer; crackle bed |
| 41 | 8:19.7 | whip | **Misconceptions** | Silver rocks ✕, mercury ocean ✕; 'NOT WHAT SCIENTISTS MEAN' | Whip whoosh, thuds |
| 42 | 8:29.0 | fade | **Conductivity** | Protons + free electrons + current arrow → cutaway with the metallic region highlighted | Crackle |
| 43 | 8:46.5 | fade | **Magnetic field (callback)** | Field lines bloom; radiation belts; labels | Magnetic hum |
| 44 | 9:02.4 | fade | **Dynamo** | Swirls in the conducting layer; field connected to the interior; pull-out | Hum + crackle |
| 45 | 9:28.4 | black | **The center** | CHAPTER 02; older compact-core model | Boom; suspense returns |
| 46 | 9:48.7 | fade | **Fuzzy core — PEAK** | Juno polar orbit + gravity contours; compact core dissolves into the dilute core | Riser → shimmer + boom |
| 47 | 10:04.1 | cut | **Spread out** | Zoom into the broad core; 'HOW DID IT FORM?' | — |
| 48 | 10:19.1 | fade | **Hypotheses** | Formation disk vs. giant-collision cards, both tagged HYPOTHESIS | Collision boom |
| 49 | 10:30.5 | black | **Never photographed** | A glowing '?' in darkness; camera ✕ | Thud |
| 50 | 10:41.7 | fade | **NO. (callback)** | Opening composition returns; 'WOULD YOU EVENTUALLY LAND?' → giant 'NO.' | Inspiring music; riser → big boom |
| 51 | 10:51.2 | fade | **Recap** | Journey column: real probe ✕ → atmosphere → dense fluid → metal → central structure | Pops on each station |
| 52 | 11:26.4 | black | **Only clouds** | Jupiter grows; the cutaway opens; 'ALMOST EVERYTHING IS HIDDEN BENEATH' | — |
| 53 | 11:42.4 | fade | **What we can do** | Four cards (storms, gravity, field, predictions) → 'DIRECTLY EXPLORED: ONLY THE TOP SLIVER' | Pops |
| 54 | 11:58.2 | black | **Night sky ending** | Person on a hill under the stars; Jupiter dot zooms to the planet; final line; end card | Shimmer; end-card boom; music outro |

## 9.2 Visual peaks and callbacks

Peaks: s01 tiny probe · s19–s20 glow + 228 g · s24 no horizon · s40 metallic hydrogen · s46 fuzzy core. Callbacks: s50 restages s01 for the answer; s43–s44 connect the interior to the magnetic field and radiation from the opening chapters; s54 returns to the viewer's own sky.

## 9.3 Honesty decisions made

- Great Red Spot texture sized to about 17,000 km so the to-scale Earth is truthful; "observed for centuries".
- Winds labeled "Galileo-measured up to ~650 km/h" against "strong Earth hurricane ~250+ km/h".
- Depth, pressure and temperature readouts marked "≈, below 1-bar"; the Galileo probe's last values ≈22 bar, ≈152 °C, ≈150 km.
- Water chart labeled "schematic · not exact values"; entry site described as a rare, unusually dry "hot spot".
- Interior always `MODEL-BASED · NOT TO SCALE`; hypotheses tagged `HYPOTHESIS`; the center shown as an unphotographed "?".
- Fictional capsule tagged "FICTIONAL CAPSULE · NOT REAL TECHNOLOGY", later "IMAGINARY · INDESTRUCTIBLE".


---

# PART X — TOPIC PLAYBOOKS (STARTING POINTS FOR NEW FILMS)

The narration always decides the actual structure. These are ready starting points for hero assets, palettes, peaks, honesty boundaries and sound palettes.

## 10.1 What If You Traveled to Another Galaxy?

- **Real anchor:** Voyager 1 (the farthest spacecraft, about 24 billion km and counting); the Andromeda Galaxy (about 2.5 million light-years); light-travel time.
- **Hero assets:** particle spiral galaxy (logarithmic arms, a bulge glow, dust lanes as dark noise strips); the Milky Way from inside (a band of stars); intergalactic void (near-empty starfield with distant galaxy smudges); Andromeda approach; a warp/time-dilation capsule (the fictional capsule with a `shield` energy bubble).
- **Instruments:** DISTANCE (light-years), SPEED (% of c), ELAPSED SHIP TIME vs EARTH TIME, NEAREST STAR.
- **Palette:** deep navy → violet void → warm golden galactic core → blue-white star-forming arms.
- **Peaks:** pull-out from Earth to the Milky Way; leaving the galaxy (the starfield thins to almost nothing); Andromeda filling the sky; Earth time racing ahead (counter in millions of years); arrival among alien stars.
- **Honesty:** travel near light speed is fictional; time dilation is real physics (tag `model`); galaxy images are illustrations.
- **Sound palette:** vast slow drones, sparse shimmer, a heartbeat-like pulse for time, deep silence in the void, a choir-like pad on arrival.

## 10.2 What If You Fell Into a Black Hole?

- **Hero assets:** black disk + photon ring + Doppler-asymmetric accretion disk; lensed background stars; event horizon; spaghettification diagram (stretched explorer silhouette, honest and non-graphic); a redshift color shift on the outside view.
- **Instruments:** TIDAL FORCE, DISTANCE TO HORIZON, TIME DILATION FACTOR, SIGNAL REDSHIFT.
- **Peaks:** first view of the lensed ring (modelled on the EHT images, labelled as an illustration); crossing the horizon (silence + inversion); the outside observer seeing you freeze and redden.
- **Honesty:** the interior is unknown (tag `hypothesis`); EHT image references are historical.

## 10.3 What If You Entered a Parallel Universe?

- **Framework honesty:** parallel universes are **hypotheses** (many-worlds interpretation, cosmic inflation's multiverse, brane worlds). Tag nearly everything `model` or `hypothesis`, and say "there is no evidence yet" where the script does.
- **Hero assets:** branching timeline tree (paths drawn on with `stroke_path_k`, nodes popping); split-screen mirrored worlds (same scene, different palette and details); bubble universes (translucent spheres with internal starfields, some colliding); a "different physics" world (altered colors, different constants shown on gauges).
- **Instruments:** BRANCH COUNT, DIVERGENCE, CONSTANTS (G, c, α) with "?" values.
- **Palette:** our universe navy/amber vs. the parallel world teal/magenta; transitions as mirror wipes.
- **Peaks:** the first branching (one explorer becomes two); bubble universes revealed; meeting the "other you" (the explorer looking at a mirrored explorer); the bubble-collision hypothesis.
- **Sound palette:** mirrored or reversed shimmer tails, detuned doubled drones (one per universe), phasey whooshes on branchings.

## 10.4 What If You Traveled to the Edge of the Universe?

- **Real anchor:** the observable universe (about 46.5 billion light-years radius), the cosmic microwave background, JWST deep fields.
- **Hero assets:** cosmic-web filaments; expanding spacetime grid; the horizon as a glowing CMB shell; galaxies redshifting as you look farther.
- **Peaks:** the cosmic web reveal; reaching the CMB "wall" (the edge of what we can see, not a physical edge); the question of what lies beyond (tag `hypothesis`).

## 10.5 Reusing the channel's continuity

Keep the **same explorer, capsule, instrument style, tag system, typography and transitions** in every film. That consistency is the channel's visual identity. Change the **hero assets, palette and music** per topic.


---

# APPENDIX A — COMPLETE ENGINE SOURCE CODE

The full, working engine that rendered the Jupiter film. It is also stored as files in `prompt_book/engine/` in the repository; prefer copying the files over retyping. File order follows the dependency order.

## A.1 `engine/core.py` — Timing, easing, colors, fonts, text, paints, images, noise (316 lines)

```python
# Core helpers: timing, easing, colors, skia drawing utilities, noise.
import os, json, math, re, functools
import numpy as np
import skia
from PIL import Image

W, H = 1920, 1080
FPS = 60
HERE = os.path.dirname(os.path.abspath(__file__))
# PROJECT = folder holding this video's words.json + scenes*.py (set JV_PROJECT, default: current dir)
PROJECT = os.path.abspath(os.environ.get('JV_PROJECT', os.getcwd()))
CACHE = os.path.join(PROJECT, 'cache')
os.makedirs(CACHE, exist_ok=True)
SAFE_BOTTOM = int(H * 0.85)  # keep critical info above this line

# ---------------------------------------------------------------- timing
_WORDS = json.load(open(os.path.join(PROJECT, 'words.json')))
_NORM = [re.sub(r"[^a-z0-9]", "", w.lower()) for w, _ in _WORDS]
_TIMES = [t for _, t in _WORDS]

def at(phrase, after=0.0, end=False):
    """Start time (s) of first occurrence of phrase in narration at/after `after`.
    end=True returns the start time of the word following the phrase."""
    toks = [re.sub(r"[^a-z0-9]", "", p.lower()) for p in phrase.split()]
    toks = [t for t in toks if t]
    n = len(toks)
    for i in range(len(_NORM) - n + 1):
        if _TIMES[i] < after - 1e-6:
            continue
        if _NORM[i:i + n] == toks:
            if end:
                j = i + n
                return _TIMES[j] if j < len(_TIMES) else _TIMES[-1] + 0.6
            return _TIMES[i]
    raise KeyError(f"phrase not found: {phrase!r} after {after}")

# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x

def lerp(a, b, t):
    return a + (b - a) * t

def prog(t, t0, t1):
    if t1 <= t0:
        return 1.0 if t >= t1 else 0.0
    return clamp((t - t0) / (t1 - t0))

def e_in(x):  return x * x * x
def e_out(x): return 1 - (1 - x) ** 3
def e_io(x):  return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def e_sine(x): return -(math.cos(math.pi * x) - 1) / 2
def e_back(x, s=1.70158):
    x -= 1
    return x * x * ((s + 1) * x + s) + 1
def e_expo_out(x): return 1 if x >= 1 else 1 - 2 ** (-10 * x)

def tw(t, t0, t1, a, b, ease=e_io):
    return lerp(a, b, ease(prog(t, t0, t1)))

def fade_window(t, t0, t1, fin=0.35, fout=0.35):
    """1 inside [t0,t1] with fades at both ends."""
    if t < t0 or t > t1:
        return 0.0
    a = e_out(prog(t, t0, t0 + fin)) if fin > 0 else 1.0
    b = 1 - e_in(prog(t, t1 - fout, t1)) if fout > 0 else 1.0
    return min(a, b)

def keys(t, kf, ease=e_io):
    """Piecewise interpolation through [(time, value), ...]. value may be tuple."""
    if t <= kf[0][0]:
        return kf[0][1]
    for (t0, v0), (t1, v1) in zip(kf, kf[1:]):
        if t <= t1:
            x = ease(prog(t, t0, t1))
            if isinstance(v0, (tuple, list)):
                return tuple(lerp(a, b, x) for a, b in zip(v0, v1))
            return lerp(v0, v1, x)
    return kf[-1][1]

def shake(t, t0, dur, amp, freq=22.0, seed=1):
    """Damped shake offset (dx, dy) starting at t0."""
    if t < t0 or t > t0 + dur:
        return 0.0, 0.0
    x = (t - t0)
    d = math.exp(-4.0 * x / dur) * (1 - prog(t, t0 + dur * .8, t0 + dur))
    return (amp * d * math.sin(x * freq * 6.283 + seed),
            amp * d * math.sin(x * freq * 1.37 * 6.283 + seed * 2.1) * .7)

def wobble(t, amp, f=0.2, seed=0.0):
    return amp * (math.sin(t * f * 6.283 + seed) * .6 + math.sin(t * f * 2.71 * 6.283 + seed * 1.7) * .4)

# ---------------------------------------------------------------- color
def hexc(h, a=1.0):
    h = h.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return skia.Color(r, g, b, int(clamp(a) * 255))

def rgba(r, g, b, a=1.0):
    return skia.Color(int(r), int(g), int(b), int(clamp(a) * 255))

def mixc(h1, h2, x, a=1.0):
    h1, h2 = h1.lstrip('#'), h2.lstrip('#')
    c1 = [int(h1[i:i + 2], 16) for i in (0, 2, 4)]
    c2 = [int(h2[i:i + 2], 16) for i in (0, 2, 4)]
    return skia.Color(*[int(lerp(a_, b_, clamp(x))) for a_, b_ in zip(c1, c2)], int(clamp(a) * 255))

def with_alpha(c, a):
    return skia.ColorSetA(c, int(clamp(a) * skia.ColorGetA(c)))

PAL = dict(
    jbg='#2A1810', jmid='#B9773E', jlight='#E3B47A', jhi='#FFF1D6',
    sp0='#070B1A', sp1='#1C2A55', sp2='#3D5A9E', white='#FFFFFF',
    danger='#FF3B30', cyan='#6FD3FF', blue='#4C8DFF', purple='#8A5CFF',
    hud='#9FE3FF', ok='#58E08A', warm='#FFB347', grs='#B5502A',
)

# ---------------------------------------------------------------- fonts
@functools.lru_cache(None)
def font(size, weight='bold', family='Inter Display'):
    st = {'black': skia.FontStyle(900, 5, skia.FontStyle.kUpright_Slant),
          'xbold': skia.FontStyle(800, 5, skia.FontStyle.kUpright_Slant),
          'bold': skia.FontStyle.Bold(),
          'semi': skia.FontStyle(600, 5, skia.FontStyle.kUpright_Slant),
          'medium': skia.FontStyle(500, 5, skia.FontStyle.kUpright_Slant),
          'regular': skia.FontStyle.Normal(),
          'light': skia.FontStyle(300, 5, skia.FontStyle.kUpright_Slant)}[weight]
    f = skia.Font(skia.Typeface(family, st), size)
    f.setSubpixel(True)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    return f

def mono(size, weight='medium'):
    return font(size, weight, 'JetBrains Mono')

def text_w(s, f):
    return f.measureText(s)

def draw_text(c, s, x, y, f, color, align='left', alpha=1.0, glow=0.0, glow_color=None,
              shadow=0.0, spacing=0.0):
    if alpha <= 0.003 or not s:
        return
    if spacing:
        # manual letter spacing
        widths = [f.measureText(ch) for ch in s]
        total = sum(widths) + spacing * (len(s) - 1)
        x0 = x - total / 2 if align == 'center' else x - total if align == 'right' else x
        for ch, w_ in zip(s, widths):
            draw_text(c, ch, x0, y, f, color, 'left', alpha, glow, glow_color, shadow)
            x0 += w_ + spacing
        return
    w = f.measureText(s)
    if align == 'center':
        x -= w / 2
    elif align == 'right':
        x -= w
    if shadow > 0:
        p = skia.Paint(AntiAlias=True, Color=rgba(0, 0, 0, .55 * alpha * shadow),
                       MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 6))
        c.drawString(s, x + 2, y + 4, f, p)
    if glow > 0:
        gc = glow_color if glow_color is not None else color
        p = skia.Paint(AntiAlias=True, Color=with_alpha(gc, alpha * glow),
                       MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, f.getSize() * .18))
        c.drawString(s, x, y, f, p)
    p = skia.Paint(AntiAlias=True, Color=with_alpha(color, alpha))
    c.drawString(s, x, y, f, p)

def text_pop(c, s, x, y, f, color, t, t0, dur=0.35, align='center', alpha=1.0, **kw):
    """Text that pops in with slight scale overshoot (0.25-0.42s)."""
    if t < t0:
        return
    k = prog(t, t0, t0 + dur)
    sc = lerp(0.82, 1.0, e_back(k, 2.2)) if k < 1 else 1.0
    c.save()
    c.translate(x, y)
    c.scale(sc, sc)
    draw_text(c, s, 0, 0, f, color, align, alpha * e_out(min(1, k * 1.6)), **kw)
    c.restore()

# ---------------------------------------------------------------- paints
def P(color=None, stroke=None, aa=True, blur=0, blend=None, shader=None, cap=None, join=None, alpha=None):
    p = skia.Paint(AntiAlias=aa)
    if color is not None:
        p.setColor(color)
    if alpha is not None:
        p.setAlphaf(alpha)
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if blend is not None:
        p.setBlendMode(blend)
    if shader is not None:
        p.setShader(shader)
    if cap == 'round':
        p.setStrokeCap(skia.Paint.kRound_Cap)
    if join == 'round':
        p.setStrokeJoin(skia.Paint.kRound_Join)
    return p

def lin(p0, p1, colors, pos=None):
    return skia.GradientShader.MakeLinear([skia.Point(*p0), skia.Point(*p1)], colors, pos)

def rad(cx, cy, r, colors, pos=None):
    return skia.GradientShader.MakeRadial(skia.Point(cx, cy), max(r, 0.01), colors, pos)

def path_from(points, close=False):
    pa = skia.Path()
    pa.moveTo(*points[0])
    for p in points[1:]:
        pa.lineTo(*p)
    if close:
        pa.close()
    return pa

def rrect(c, x, y, w, h, r, paint):
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r), paint)

PLUS = skia.BlendMode.kPlus
SCREEN = skia.BlendMode.kScreen
MULT = skia.BlendMode.kMultiply
LIN = skia.SamplingOptions(skia.FilterMode.kLinear)
MIP = skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear)

# ---------------------------------------------------------------- images
def to_img(arr, alpha=None):
    """arr: HxWx3 or HxWx4, float 0..1 or uint8, RGB order. Returns premul BGRA skia.Image."""
    a = np.asarray(arr)
    if a.dtype != np.float32:
        a = a.astype(np.float32) / (255.0 if a.dtype == np.uint8 else 1.0)
    h, w = a.shape[:2]
    out = np.empty((h, w, 4), np.uint8)
    if a.shape[2] == 4:
        al = np.clip(a[..., 3], 0, 1)
    elif alpha is not None:
        al = np.clip(alpha, 0, 1)
    else:
        al = np.ones((h, w), np.float32)
    rgb = np.clip(a[..., :3], 0, 1) * al[..., None]
    out[..., 0] = (rgb[..., 2] * 255 + .5).astype(np.uint8)
    out[..., 1] = (rgb[..., 1] * 255 + .5).astype(np.uint8)
    out[..., 2] = (rgb[..., 0] * 255 + .5).astype(np.uint8)
    out[..., 3] = (al * 255 + .5).astype(np.uint8)
    return skia.Image.fromarray(out, colorType=skia.kBGRA_8888_ColorType, alphaType=skia.kPremul_AlphaType)

def draw_img(c, img, x, y, w=None, h=None, alpha=1.0, blend=None, cf=None):
    if alpha <= 0.003:
        return
    w = img.width() if w is None else w
    h = img.height() if h is None else h
    p = skia.Paint(AntiAlias=True)
    p.setAlphaf(clamp(alpha))
    if blend is not None:
        p.setBlendMode(blend)
    if cf is not None:
        p.setColorFilter(cf)
    c.drawImageRect(img, skia.Rect.MakeXYWH(x, y, w, h), LIN, p)

def draw_img_c(c, img, cx, cy, scale=1.0, alpha=1.0, rot=0.0, blend=None, cf=None, sx=None, sy=None):
    """Draw image centered at (cx,cy) with scale and rotation (deg)."""
    if alpha <= 0.003:
        return
    c.save()
    c.translate(cx, cy)
    if rot:
        c.rotate(rot)
    sxx = scale if sx is None else sx
    syy = scale if sy is None else sy
    w, h = img.width() * sxx, img.height() * syy
    draw_img(c, img, -w / 2, -h / 2, w, h, alpha, blend, cf)
    c.restore()

def tint_cf(r, g, b, amount=1.0, bright=1.0):
    """Color filter: multiply RGB by color (0..1 floats)."""
    m = [r * bright, 0, 0, 0, 0,
         0, g * bright, 0, 0, 0,
         0, 0, b * bright, 0, 0,
         0, 0, 0, 1, 0]
    return skia.ColorFilters.Matrix(m)

# ---------------------------------------------------------------- noise
def noise2(h, w, cells_y, cells_x, seed=0, wrap_x=False, octaves=1, persistence=0.5):
    """Smooth value noise in [0,1] via bicubic upsampling, fractal octaves."""
    rng = np.random.default_rng(seed)
    total = np.zeros((h, w), np.float32)
    amp, norm = 1.0, 0.0
    cy, cx = cells_y, cells_x
    for o in range(octaves):
        cyi, cxi = max(2, int(cy)), max(2, int(cx))
        g = rng.random((cyi + 3, cxi + 3)).astype(np.float32)
        if wrap_x:
            g[:, cxi:cxi + 3] = g[:, 0:3]
        im = Image.fromarray(g, mode='F')
        # resize so that cell grid maps exactly with 1 cell padding on each side
        big = im.resize((int(w * (cxi + 3) / cxi), int(h * (cyi + 3) / cyi)), Image.BICUBIC)
        arr = np.asarray(big)
        ox = int(w / cxi * 1)
        oy = int(h / cyi * 1)
        total += amp * arr[oy:oy + h, ox:ox + w]
        norm += amp
        amp *= persistence
        cy *= 2
        cx *= 2
    total /= norm
    lo, hi = np.percentile(total, 1), np.percentile(total, 99)
    return np.clip((total - lo) / (hi - lo + 1e-6), 0, 1)

def cached_npy(name, fn):
    p = os.path.join(CACHE, name + '.npy')
    if os.path.exists(p):
        return np.load(p)
    a = fn()
    np.save(p, a)
    return a
```

## A.2 `engine/assets.py` — Procedural textures, sphere renderer, clouds, stars, overlays (295 lines)

```python
# Procedural assets: Jupiter/Earth textures + sphere renderer, cloud sprites, stars, overlays.
import math, functools
import numpy as np
import skia
from PIL import Image
from core import *

TH, TW = 2048, 4096

def _hex3(h):
    h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255

JUP_BANDS = [
    (90, '#5f5650'), (70, '#6f645a'), (62, '#8c7c6a'), (57, '#c2a27c'), (52, '#a27650'),
    (47, '#dcc39d'), (42, '#b08158'), (37, '#ecd8b4'), (33, '#9a6942'), (29, '#f2dfbd'),
    (24, '#e8cfa4'), (19.5, '#a86a3d'), (15, '#8a4e2b'), (10, '#9c5c34'), (7.5, '#e9d6b4'),
    (3, '#fff1d6'), (-2, '#f6e6c8'), (-6.5, '#e3c9a0'), (-8.5, '#a0623a'), (-13, '#8a4e2b'),
    (-17.5, '#b9773e'), (-20.5, '#efdcb9'), (-25, '#f3e2c2'), (-28.5, '#e3b47a'), (-31, '#a8774c'),
    (-35, '#ead6b2'), (-40, '#ddc19a'), (-44, '#ad8258'), (-49, '#d6b88f'), (-55, '#a88a6b'),
    (-62, '#8a7b6c'), (-72, '#6c6158'), (-90, '#5c534d')]

def _band_lookup(lat):
    lats = np.array([b[0] for b in JUP_BANDS][::-1], np.float32)
    cols = np.stack([_hex3(b[1]) for b in JUP_BANDS][::-1])
    out = np.empty(lat.shape + (3,), np.float32)
    for k in range(3):
        out[..., k] = np.interp(lat, lats, cols[:, k])
    return out

def _make_jupiter_tex():
    H_, W_ = TH, TW
    yy = (np.arange(H_, dtype=np.float32) + .5) / H_
    xx = (np.arange(W_, dtype=np.float32) + .5) / W_
    lat = (0.5 - yy)[:, None] * 180.0 * np.ones((1, W_), np.float32)
    lon = xx[None, :] * 360.0 * np.ones((H_, 1), np.float32)
    # elongated turbulence (stretched in longitude)
    n1 = noise2(H_, W_, 90, 22, seed=3, wrap_x=True, octaves=5, persistence=.55) - .5
    n2 = noise2(H_, W_, 40, 10, seed=7, wrap_x=True, octaves=4) - .5
    # stronger turbulence near belt edges
    amp = 1.1 + 1.6 * (np.abs(np.sin(np.radians(lat) * 9.0)))
    lat_e = lat + n1 * amp * 2.2 + n2 * 2.0
    # festoons / plumes at the north edge of the equatorial zone
    fest = np.exp(-((lat - 7.0) / 3.5) ** 2) * (np.sin(np.radians(lon) * 13 + n2 * 4) ** 12) * 2.6
    lat_e = lat_e + fest
    # Great Red Spot vortex swirl: lat -22, lon 180
    g_lat, g_lon, a_ax, b_ax = -22.0, 180.0, 7.6, 4.7
    dx = (lon - g_lon) * math.cos(math.radians(g_lat))
    dy = lat - g_lat
    rr = np.sqrt((dx / a_ax) ** 2 + (dy / b_ax) ** 2)
    ang = 2.6 * np.exp(-rr ** 2 * 0.8)
    ca, sa = np.cos(ang), np.sin(ang)
    sdx = dx * ca - dy * sa * (a_ax / b_ax) * .6
    sdy = dx * sa / (a_ax / b_ax) * .6 + dy * ca
    lat_e = np.where(rr < 2.4, g_lat + sdy + (lat_e - lat) * np.clip(rr / 2.4, 0, 1), lat_e)
    col = _band_lookup(lat_e)
    # fine streak detail
    n3 = noise2(H_, W_, 420, 60, seed=11, wrap_x=True, octaves=3) - .5
    col *= (1.0 + n3[..., None] * 0.16 + n1[..., None] * 0.10)
    # GRS colour
    rr2 = np.sqrt(((lon - g_lon) * math.cos(math.radians(g_lat)) / a_ax) ** 2 + ((lat - g_lat) / b_ax) ** 2)
    rr2 = rr2 + (n1 * 0.25)
    core_c = _hex3('#c0502e'); rim_c = _hex3('#d98a5a'); collar = _hex3('#f6e7cc')
    m_core = np.clip((1.0 - rr2) / 0.35, 0, 1)[..., None]
    m_rim = np.clip((1.18 - rr2) / 0.2, 0, 1)[..., None]
    m_col = (np.exp(-((rr2 - 1.32) / 0.16) ** 2))[..., None]
    swirl = (np.sin(rr2 * 22 + np.arctan2(lat - g_lat, (lon - g_lon) * .5) * 2) * .5 + .5)[..., None]
    col = col * (1 - m_col * .6) + collar * m_col * .6
    col = col * (1 - m_rim) + rim_c * m_rim * (0.92 + 0.08 * swirl)
    col = col * (1 - m_core) + core_c * m_core * (0.9 + 0.12 * swirl)
    # white ovals in southern temperate region
    rng = np.random.default_rng(5)
    for k in range(9):
        olon = rng.uniform(0, 360); olat = rng.choice([-41, -33.5, 39.5, -46]) + rng.uniform(-1, 1)
        oa, ob = rng.uniform(2.2, 4.0), rng.uniform(1.2, 2.0)
        d = np.sqrt((((lon - olon + 180) % 360 - 180) * math.cos(math.radians(olat)) / oa) ** 2 + ((lat - olat) / ob) ** 2)
        m = np.clip(1.3 - d, 0, 1)[..., None] ** 1.5
        col = col * (1 - m * .85) + _hex3('#fbf2e2') * m * .85
    # small dark barges in NEB
    for k in range(7):
        olon = rng.uniform(0, 360); olat = 15.5 + rng.uniform(-1, 1)
        d = np.sqrt((((lon - olon + 180) % 360 - 180) / 3.0) ** 2 + ((lat - olat) / 1.0) ** 2)
        m = np.clip(1.2 - d, 0, 1)[..., None]
        col = col * (1 - m * .5) + _hex3('#5a2c18') * m * .5
    return np.clip(col, 0, 1).astype(np.float16)

@functools.lru_cache(None)
def jupiter_tex():
    return cached_npy('jup_tex_v5', _make_jupiter_tex).astype(np.float32)

def _make_earth_tex():
    H_, W_ = 512, 1024
    n = noise2(H_, W_, 6, 12, seed=21, wrap_x=True, octaves=6, persistence=.5)
    yy = (np.arange(H_) + .5) / H_
    lat = (0.5 - yy)[:, None] * 180 * np.ones((1, W_))
    land = n > 0.56
    ocean = np.array([0.05, 0.22, 0.48]) * (0.8 + 0.3 * n[..., None])
    green = np.array([0.18, 0.42, 0.16]); desert = np.array([0.72, 0.58, 0.36])
    dry = np.clip((np.abs(np.abs(lat) - 24) < 9) * 1.0 * (n > .62), 0, 1)[..., None]
    landc = green * (1 - dry) + desert * dry
    col = np.where(land[..., None], landc * (0.85 + 0.3 * n[..., None]), ocean)
    ice = (np.abs(lat) > 68)[..., None]
    col = np.where(ice, np.array([0.93, 0.95, 0.98]), col)
    cl = noise2(H_, W_, 10, 24, seed=33, wrap_x=True, octaves=5)
    cm = np.clip((cl - 0.55) * 3.2, 0, 1)[..., None] * 0.85
    col = col * (1 - cm) + cm * 0.97
    return np.clip(col, 0, 1).astype(np.float32)

@functools.lru_cache(None)
def earth_tex():
    return cached_npy('earth_tex_v1', _make_earth_tex)

_LIGHT = np.array([-0.62, -0.38, 0.69], np.float32)
_LIGHT /= np.linalg.norm(_LIGHT)

def sphere_layer(tex, cx, cy, R, rot=0.0, light=None, ambient=0.035, alpha=1.0, max_grid=1150,
                 limb=0.35, bilinear=None, screen=(W, H)):
    """Render a textured, lit sphere; returns (skia.Image, rect) or None."""
    if R < 1:
        return None
    L = _LIGHT if light is None else np.asarray(light, np.float32) / np.linalg.norm(light)
    x0, y0 = max(0, cx - R - 2), max(0, cy - R - 2)
    x1, y1 = min(screen[0], cx + R + 2), min(screen[1], cy + R + 2)
    if x1 <= x0 or y1 <= y0:
        return None
    vw, vh = x1 - x0, y1 - y0
    g = min(1.0, max_grid / max(vw, vh))
    gw, gh = max(2, int(vw * g)), max(2, int(vh * g))
    xs = x0 + (np.arange(gw, dtype=np.float32) + .5) * (vw / gw)
    ys = y0 + (np.arange(gh, dtype=np.float32) + .5) * (vh / gh)
    nx = ((xs - cx) / R)[None, :]
    ny = ((ys - cy) / R)[:, None]
    r2 = nx * nx + ny * ny
    inside = r2 < 1.0
    nz = np.sqrt(np.clip(1 - r2, 0, 1))
    th, twd = tex.shape[:2]
    lat = np.arcsin(np.clip(-ny * np.ones_like(nx), -1, 1))
    lon = np.arctan2(nx * np.ones_like(ny), nz) + rot
    fy = (0.5 - lat / math.pi) * th - .5
    fx = (lon / (2 * math.pi)) * twd - .5
    texels_per_px = (twd / (2 * math.pi * R)) * (vw / gw)
    if bilinear is None:
        bilinear = texels_per_px < 1.0
    if bilinear:
        ix = np.floor(fx).astype(np.int64); iy = np.floor(fy).astype(np.int64)
        tx = (fx - ix)[..., None]; ty = (fy - iy)[..., None]
        ix0 = ix % twd; ix1 = (ix + 1) % twd
        iy0 = np.clip(iy, 0, th - 1); iy1 = np.clip(iy + 1, 0, th - 1)
        col = ((tex[iy0, ix0] * (1 - tx) + tex[iy0, ix1] * tx) * (1 - ty) +
               (tex[iy1, ix0] * (1 - tx) + tex[iy1, ix1] * tx) * ty)
    else:
        ix = np.round(fx).astype(np.int64) % twd
        iy = np.clip(np.round(fy).astype(np.int64), 0, th - 1)
        col = tex[iy, ix]
    ndl = nx * L[0] + ny * L[1] + nz * L[2]
    lit = np.clip(ndl * 1.15 + 0.05, 0, 1) ** 0.85
    mu = nz
    shade = lit * (1 - limb + limb * mu ** 0.5) + ambient
    col = col * shade[..., None]
    # faint warm terminator scattering
    term = np.exp(-((ndl - 0.02) / 0.09) ** 2) * 0.05
    col[..., 0] += term; col[..., 1] += term * .45
    edge = np.clip((1 - np.sqrt(r2)) * R * g * 1.0 + 0.5, 0, 1)
    a = edge * inside * alpha
    img = to_img(col, alpha=a)
    return img, skia.Rect(x0, y0, x1, y1)

def draw_sphere(c, tex, cx, cy, R, rot=0.0, alpha=1.0, atmo=None, **kw):
    r = sphere_layer(tex, cx, cy, R, rot, alpha=alpha, **kw)
    if r is None:
        return
    img, rect = r
    p = skia.Paint(AntiAlias=True)
    c.drawImageRect(img, rect, LIN, p)
    if atmo is not None and alpha > 0:
        # thin atmospheric rim glow, brighter on lit side
        col = atmo
        sh = rad(cx, cy, R * 1.06, [skia.ColorTRANSPARENT, skia.ColorTRANSPARENT, with_alpha(col, .45 * alpha), skia.ColorTRANSPARENT],
                 [0, 0.90, 0.945, 1.0])
        c.drawCircle(cx, cy, R * 1.06, P(shader=sh))

def draw_jupiter(c, cx, cy, R, rot=0.0, alpha=1.0, **kw):
    draw_sphere(c, jupiter_tex(), cx, cy, R, rot, alpha, atmo=hexc('#ffd9a0'), **kw)

def draw_earth(c, cx, cy, R, rot=0.0, alpha=1.0, **kw):
    kw.setdefault('limb', 0.2)
    draw_sphere(c, earth_tex(), cx, cy, R, rot, alpha, atmo=hexc('#7fb8ff'), **kw)

# ---------------------------------------------------------------- simple vector Earth (for many small copies)
def draw_earth_icon(c, x, y, r, alpha=1.0):
    c.drawCircle(x, y, r, P(shader=rad(x - r * .35, y - r * .35, r * 1.5, [hexc('#5fa8ff', alpha), hexc('#1d4f9a', alpha), hexc('#0b1d3d', alpha)], [0, .55, 1])))
    if r > 3:
        c.drawCircle(x - r * .25, y - r * .1, r * .38, P(hexc('#4f9a4a', .9 * alpha)))
        c.drawCircle(x + r * .3, y + r * .3, r * .22, P(hexc('#4f9a4a', .9 * alpha)))

# ---------------------------------------------------------------- clouds
def _make_cloud(seed, w=512, h=300):
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    D = np.zeros((h, w), np.float32)
    nb = int(rng.integers(16, 24))
    for i in range(nb):
        u = rng.uniform(.15, .85)
        bx = u * w
        br = rng.uniform(.05, .11) * w * (1.25 - abs(u - .5) * 1.2)
        by = h * .72 - br * rng.uniform(.2, 1.6) * (1.3 - abs(u - .5) * 1.6)
        D += np.exp(-(((xx - bx) ** 2 + (yy - by) ** 2) / (br * br)))
    n = noise2(h, w, 4, 7, seed=seed + 100, octaves=3, persistence=.45)
    D = D * (0.85 + 0.3 * n)
    D *= np.clip((h * .78 - yy) / (h * .18), 0, 1) ** .7
    a = np.clip((D - 0.30) / 0.35, 0, 1)
    a = a * a * (3 - 2 * a)
    gy = np.gradient(a, axis=0)
    top_rim = np.clip(-gy * 0 + gy * 6, 0, 1)  # gy>0 at upper edges (alpha grows downward)
    vert = 1 - yy / h
    v = 0.62 + 0.42 * vert ** .8 + 0.3 * top_rim + (n - .5) * .1
    col = np.stack([v, v, v], -1)
    return to_img(np.clip(col, 0, 1.1), alpha=a * .97)

@functools.lru_cache(None)
def cloud_sprites():
    return [_make_cloud(s) for s in range(1, 9)]

def _make_haze(seed, w=1024, h=220):
    yy = (np.arange(h, dtype=np.float32) / h)[:, None]
    n = noise2(h, w, 3, 14, seed=seed, octaves=4, wrap_x=True)
    prof = np.exp(-((yy - .5) / .22) ** 2)
    a = np.clip(prof * (0.4 + 0.9 * n) - 0.15, 0, 1)
    v = 0.8 + 0.2 * n
    return to_img(np.stack([v, v, v], -1), alpha=a)

@functools.lru_cache(None)
def haze_sprites():
    return [_make_haze(s) for s in range(40, 46)]

# ---------------------------------------------------------------- stars
@functools.lru_cache(None)
def star_field(seed=1, n=900):
    rng = np.random.default_rng(seed)
    xs = rng.uniform(-200, W + 200, n); ys = rng.uniform(-200, H + 200, n)
    mag = rng.power(3.2, n)[::-1]  # many faint
    mag = rng.random(n) ** 3.5
    tw_ = rng.uniform(0, 6.28, n)
    depth = rng.uniform(.2, 1.0, n)
    tint = rng.random(n)
    return xs, ys, mag, tw_, depth, tint

def draw_stars(c, t, alpha=1.0, ox=0.0, oy=0.0, zoom=1.0, seed=1, n=900, cx=W / 2, cy=H / 2):
    if alpha <= 0:
        return
    xs, ys, mag, tw_, depth, tint = star_field(seed, n)
    for i in range(len(xs)):
        x = cx + (xs[i] - cx + ox * depth[i]) * (1 + (zoom - 1) * depth[i])
        y = cy + (ys[i] - cy + oy * depth[i]) * (1 + (zoom - 1) * depth[i])
        if x < -5 or x > W + 5 or y < -5 or y > H + 5:
            continue
        m = mag[i]
        a = alpha * (0.25 + 0.75 * m) * (0.85 + 0.15 * math.sin(t * 1.3 + tw_[i]))
        r = 0.6 + 1.6 * m
        col = rgba(255, 244, 230, a) if tint[i] > .7 else rgba(200, 220, 255, a) if tint[i] < .25 else rgba(255, 255, 255, a)
        c.drawCircle(x, y, r, P(col))
        if m > .8:
            c.drawCircle(x, y, r * 4, P(rgba(180, 200, 255, a * .18), blur=4))

# ---------------------------------------------------------------- overlays
@functools.lru_cache(None)
def vignette_img(strength=0.55):
    yy, xx = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32)
    nx = (xx / (W / 4) - .5) * 2; ny = (yy / (H / 4) - .5) * 2
    d = np.sqrt(nx ** 2 * .8 + ny ** 2 * 1.0)
    a = np.clip((d - 0.55) / 0.9, 0, 1) ** 1.6 * strength
    return to_img(np.zeros((H // 4, W // 4, 3), np.float32), alpha=a)

@functools.lru_cache(None)
def grain_imgs(n=6):
    rng = np.random.default_rng(9)
    out = []
    for i in range(n):
        g = rng.normal(0.5, 0.18, (H // 2, W // 2)).astype(np.float32)
        out.append(to_img(np.stack([g, g, g], -1)))
    return out

@functools.lru_cache(None)
def glow_sprite(r=128):
    yy, xx = np.mgrid[0:2 * r, 0:2 * r].astype(np.float32)
    d = np.sqrt((xx - r + .5) ** 2 + (yy - r + .5) ** 2) / r
    a = np.clip(np.exp(-d * d * 4.0) - np.exp(-4.0), 0, 1)
    return to_img(np.ones((2 * r, 2 * r, 3), np.float32), alpha=a)

def glow(c, x, y, radius, color, alpha=1.0, blend=PLUS):
    """Additive soft glow using a cached sprite and tint."""
    if alpha <= 0:
        return
    r = skia.ColorGetR(color) / 255; g = skia.ColorGetG(color) / 255; b = skia.ColorGetB(color) / 255
    img = glow_sprite()
    draw_img(c, img, x - radius, y - radius, radius * 2, radius * 2, alpha, blend, tint_cf(r, g, b))
```

## A.3 `engine/elements.py` — Props, explorer rig, capsule, HUD, labels, cutaway, field lines (611 lines)

```python
# Vector props, character, HUD, diagrams.
import math
import numpy as np
import skia
from core import *
from assets import *

# ================================================================ generic shapes
def arrow(c, x0, y0, x1, y1, color, width=6, head=22, alpha=1.0, k=1.0, glow_=0.0):
    """Arrow drawn progressively (k 0..1)."""
    if k <= 0 or alpha <= 0:
        return
    x1k, y1k = lerp(x0, x1, k), lerp(y0, y1, k)
    ang = math.atan2(y1k - y0, x1k - x0)
    p = P(with_alpha(color, alpha), stroke=width, cap='round')
    hx, hy = x1k - math.cos(ang) * head * .6, y1k - math.sin(ang) * head * .6
    if glow_:
        c.drawLine(x0, y0, hx, hy, P(with_alpha(color, alpha * glow_ * .5), stroke=width * 3, blur=8))
    c.drawLine(x0, y0, hx, hy, p)
    pa = path_from([(x1k, y1k),
                    (x1k - math.cos(ang - .45) * head, y1k - math.sin(ang - .45) * head),
                    (x1k - math.cos(ang + .45) * head, y1k - math.sin(ang + .45) * head)], True)
    c.drawPath(pa, P(with_alpha(color, alpha)))

def draw_x(c, cx, cy, size, k, color=None, width=None, alpha=1.0):
    """Animated red cross (two strokes)."""
    color = hexc(PAL['danger']) if color is None else color
    width = size * .16 if width is None else width
    if k <= 0:
        return
    k1, k2 = clamp(k * 2), clamp(k * 2 - 1)
    p = P(with_alpha(color, alpha), stroke=width, cap='round')
    pg = P(with_alpha(color, alpha * .35), stroke=width * 2.2, cap='round', blur=6)
    s = size / 2
    for pp in (pg, p):
        c.drawLine(cx - s, cy - s, cx - s + 2 * s * k1, cy - s + 2 * s * k1, pp)
        if k2 > 0:
            c.drawLine(cx + s, cy - s, cx + s - 2 * s * k2, cy - s + 2 * s * k2, pp)

def draw_check(c, cx, cy, size, k, color=None, alpha=1.0):
    color = hexc(PAL['ok']) if color is None else color
    if k <= 0:
        return
    pts = [(cx - size * .5, cy), (cx - size * .15, cy + size * .35), (cx + size * .55, cy - size * .4)]
    L1 = math.dist(pts[0], pts[1]); L2 = math.dist(pts[1], pts[2]); d = (L1 + L2) * k
    pa = skia.Path(); pa.moveTo(*pts[0])
    if d <= L1:
        pa.lineTo(lerp(pts[0][0], pts[1][0], d / L1), lerp(pts[0][1], pts[1][1], d / L1))
    else:
        pa.lineTo(*pts[1]); u = (d - L1) / L2
        pa.lineTo(lerp(pts[1][0], pts[2][0], u), lerp(pts[1][1], pts[2][1], u))
    c.drawPath(pa, P(with_alpha(color, alpha * .4), stroke=size * .3, cap='round', join='round', blur=6))
    c.drawPath(pa, P(with_alpha(color, alpha), stroke=size * .14, cap='round', join='round'))

def dashed(c, pts, color, width=4, on=14, off=10, phase=0.0, alpha=1.0, k=1.0):
    pa = path_from(pts)
    if k < 1:
        meas = skia.PathMeasure(pa, False)
        L = meas.getLength()
        seg = skia.Path(); meas.getSegment(0, L * k, seg, True); pa = seg
    p = P(with_alpha(color, alpha), stroke=width, cap='round')
    p.setPathEffect(skia.DashPathEffect.Make([on, off], phase))
    c.drawPath(pa, p)

def stroke_path_k(c, pa, paint, k):
    if k >= 1:
        c.drawPath(pa, paint); return
    if k <= 0:
        return
    meas = skia.PathMeasure(pa, False)
    seg = skia.Path(); meas.getSegment(0, meas.getLength() * k, seg, True)
    c.drawPath(seg, paint)

# ================================================================ labels / tags / cards
TAG_STYLE = {
    'hist': ('#FFB347', '#2A1810'),   # historical reconstruction (amber)
    'fict': ('#6FD3FF', '#07152a'),   # fictional
    'model': ('#B79BFF', '#140d2e'),  # model-based illustration
    'concept': ('#9FE3FF', '#07152a'),
    'danger': ('#FF3B30', '#2a0806'),
}

def draw_tag(c, text, x, y, kind='hist', alpha=1.0, size=19, align='left'):
    if alpha <= 0:
        return
    fg, bg = TAG_STYLE[kind]
    f = mono(size, 'semi')
    tw_ = f.measureText(text)
    w, h = tw_ + 44, size * 1.85
    if align == 'center':
        x -= w / 2
    elif align == 'right':
        x -= w
    rrect(c, x, y, w, h, h / 2, P(hexc(bg, .78 * alpha)))
    rrect(c, x, y, w, h, h / 2, P(hexc(fg, .9 * alpha), stroke=1.6))
    c.drawCircle(x + 17, y + h / 2, 4.5, P(hexc(fg, alpha)))
    draw_text(c, text, x + 30, y + h * .5 + size * .36, f, hexc(fg), alpha=alpha)
    return w

def label_line(c, x0, y0, x1, y1, text, color=None, alpha=1.0, k=1.0, size=26, sub=None, align=None):
    """Callout: dot at (x0,y0), line to (x1,y1), text beyond."""
    color = hexc('#FFF1D6') if color is None else color
    if alpha <= 0 or k <= 0:
        return
    c.drawCircle(x0, y0, 6, P(with_alpha(color, alpha)))
    c.drawCircle(x0, y0, 12, P(with_alpha(color, alpha * .5), stroke=2))
    kk = e_out(clamp(k * 1.5))
    xe, ye = lerp(x0, x1, kk), lerp(y0, y1, kk)
    c.drawLine(x0, y0, xe, ye, P(with_alpha(color, alpha * .9), stroke=2.5))
    ka = clamp(k * 1.5 - .5)
    if ka > 0:
        al = align or ('left' if x1 >= x0 else 'right')
        dx = 14 if al == 'left' else -14
        tw1 = font(size, 'bold').measureText(text)
        tw2 = font(size * .7, 'medium').measureText(sub) if sub else 0
        tw_ = max(tw1, tw2)
        tx = x1 + dx
        if al == 'left' and tx + tw_ > W - 40:
            tx = W - 40 - tw_
        if al == 'right' and tx - tw_ < 40:
            tx = 40 + tw_
        ty = y1 + size * .35
        if tx != x1 + dx:
            ty = y1 + size * 1.3 if y1 < H / 2 else y1 - size * 1.6
        draw_text(c, text, tx, ty, font(size, 'bold'), color, al, alpha * ka, shadow=1)
        if sub:
            draw_text(c, sub, tx, ty + size * 1.05, font(size * .7, 'medium'), with_alpha(color, .8), al, alpha * ka, shadow=1)

def card(c, x, y, w, h, alpha=1.0, color='#0b1330', border='#3D5A9E', r=22):
    if alpha <= 0:
        return
    rrect(c, x + 6, y + 10, w, h, r, P(rgba(0, 0, 0, .35 * alpha), blur=14))
    rrect(c, x, y, w, h, r, P(hexc(color, .86 * alpha)))
    rrect(c, x, y, w, h, r, P(hexc(border, .9 * alpha), stroke=2))

def big_number(c, text, x, y, size, color, t, t0, alpha=1.0, glow_=.5, unit=None, unit_color=None, weight='black'):
    """Big stat number with pop and optional unit."""
    if t < t0:
        return
    k = prog(t, t0, t0 + .4)
    sc = lerp(1.25, 1.0, e_out(k))
    c.save(); c.translate(x, y); c.scale(sc, sc)
    f = font(size, weight)
    w = f.measureText(text)
    uw = 0
    if unit:
        fu = font(size * .42, 'bold')
        uw = fu.measureText(unit) + size * .12
    x0 = -(w + uw) / 2
    draw_text(c, text, x0, 0, f, color, 'left', alpha * e_out(min(1, k * 2)), glow=glow_)
    if unit:
        draw_text(c, unit, x0 + w + size * .12, 0, fu, unit_color or color, 'left', alpha * e_out(min(1, k * 2)))
    c.restore()

def chapter_card(c, num, title, t, t0, t1):
    """Minimal chapter marker top-left."""
    a = fade_window(t, t0, t1, .5, .6)
    if a <= 0:
        return
    k = e_out(prog(t, t0, t0 + .7))
    x, y = 120, 160
    c.drawLine(x, y + 18, x + 220 * k, y + 18, P(hexc('#E3B47A', a), stroke=3))
    draw_text(c, f'CHAPTER {num:02d}', x, y, mono(22, 'semi'), hexc('#E3B47A'), alpha=a, spacing=3)
    draw_text(c, title, x, y + 78, font(58, 'black'), hexc('#FFF1D6'), alpha=a * k, shadow=1)

# ================================================================ HUD
HUDC = '#9FE3FF'

def hud_panel(c, x, y, w, h, title=None, alpha=1.0, color=HUDC, warn=False):
    if alpha <= 0:
        return
    col = PAL['danger'] if warn else color
    rrect(c, x, y, w, h, 14, P(hexc('#06101f', .62 * alpha)))
    rrect(c, x, y, w, h, 14, P(hexc(col, .55 * alpha), stroke=1.5))
    # corner brackets
    L = 16
    pc = P(hexc(col, alpha), stroke=3)
    for (cx_, cy_, sx, sy) in ((x, y, 1, 1), (x + w, y, -1, 1), (x, y + h, 1, -1), (x + w, y + h, -1, -1)):
        c.drawLine(cx_, cy_ + sy * 2, cx_ + sx * L, cy_ + sy * 2, pc)
        c.drawLine(cx_ + sx * 2, cy_, cx_ + sx * 2, cy_ + sy * L, pc)
    if title:
        draw_text(c, title, x + 18, y + 30, mono(17, 'semi'), hexc(col), alpha=alpha * .9, spacing=1.5)

def hud_readout(c, x, y, w, label, value, unit='', alpha=1.0, color=HUDC, warn=False, sub=None, size=44):
    """Panel with label + big value."""
    h = size * 2.05 + (24 if sub else 0)
    hud_panel(c, x, y, w, h, label, alpha, color, warn)
    col = hexc(PAL['danger']) if warn else hexc('#FFFFFF')
    f = mono(size, 'bold')
    draw_text(c, value, x + 18, y + 34 + size * .95, f, col, alpha=alpha)
    if unit:
        vw = f.measureText(value)
        draw_text(c, unit, x + 26 + vw, y + 34 + size * .95, mono(size * .45, 'semi'), hexc(color), alpha=alpha)
    if sub:
        draw_text(c, sub, x + 18, y + 34 + size * .95 + 30, mono(16, 'medium'), hexc(color), alpha=alpha * .8)
    return h

def draw_gauge(c, cx, cy, r, frac, label, value_text, alpha=1.0, color=HUDC, warn_from=0.75, ticks=10, tick_labels=None, sub=None):
    if alpha <= 0:
        return
    a0, a1 = 135, 405
    c.drawCircle(cx, cy, r * 1.08, P(hexc('#06101f', .7 * alpha)))
    c.drawCircle(cx, cy, r * 1.08, P(hexc(color, .4 * alpha), stroke=2))
    rect = skia.Rect(cx - r, cy - r, cx + r, cy + r)
    c.drawArc(rect, a0, 270, False, P(hexc(color, .25 * alpha), stroke=r * .09))
    wa = a0 + 270 * warn_from
    c.drawArc(rect, wa, 270 * (1 - warn_from), False, P(hexc(PAL['danger'], .55 * alpha), stroke=r * .09))
    f = clamp(frac)
    col = hexc(PAL['danger']) if frac >= warn_from else hexc(color)
    c.drawArc(rect, a0, 270 * f, False, P(with_alpha(col, alpha), stroke=r * .09, cap='round'))
    for i in range(ticks + 1):
        ang = math.radians(a0 + 270 * i / ticks)
        c.drawLine(cx + math.cos(ang) * r * .8, cy + math.sin(ang) * r * .8, cx + math.cos(ang) * r * .9, cy + math.sin(ang) * r * .9,
                   P(hexc(color, .8 * alpha), stroke=2.5))
        if tick_labels and i < len(tick_labels) and tick_labels[i]:
            draw_text(c, tick_labels[i], cx + math.cos(ang) * r * .66, cy + math.sin(ang) * r * .66 + 7, mono(r * .11, 'medium'), hexc(color), 'center', alpha * .8)
    ang = math.radians(a0 + 270 * min(f, 1.04))
    c.drawLine(cx, cy, cx + math.cos(ang) * r * .78, cy + math.sin(ang) * r * .78, P(with_alpha(col, alpha), stroke=r * .045, cap='round'))
    c.drawCircle(cx, cy, r * .07, P(with_alpha(col, alpha)))
    draw_text(c, value_text, cx, cy + r * .48, mono(r * .26, 'bold'), hexc('#FFFFFF'), 'center', alpha)
    draw_text(c, label, cx, cy + r * .72, mono(r * .12, 'semi'), hexc(color), 'center', alpha * .9, spacing=1.5)
    if sub:
        draw_text(c, sub, cx, cy + r * 1.32, font(r * .15, 'semi'), hexc('#FFF1D6'), 'center', alpha * .9)

def draw_thermo(c, x, y, h, frac, value_text, alpha=1.0, cold='#6FD3FF', hot='#FF6A3D', marks=None):
    """Vertical thermometer. frac 0..1."""
    if alpha <= 0:
        return
    w = 34
    rrect(c, x - w / 2 - 6, y - 6, w + 12, h + 12, (w + 12) / 2, P(hexc('#06101f', .75 * alpha)))
    rrect(c, x - w / 2 - 6, y - 6, w + 12, h + 12, (w + 12) / 2, P(hexc(HUDC, .5 * alpha), stroke=2))
    f = clamp(frac)
    fill_h = max(w, h * f)
    col = mixc(cold, hot, f)
    rrect(c, x - w / 2, y + h - fill_h, w, fill_h, w / 2, P(with_alpha(col, alpha)))
    c.drawCircle(x, y + h + 18, 30, P(with_alpha(col, alpha)))
    c.drawCircle(x, y + h + 18, 34, P(hexc(HUDC, .5 * alpha), stroke=2))
    if marks:
        for fr, txt in marks:
            yy = y + h - h * fr
            c.drawLine(x + w / 2 + 6, yy, x + w / 2 + 22, yy, P(hexc(HUDC, .7 * alpha), stroke=2))
            draw_text(c, txt, x + w / 2 + 30, yy + 7, mono(18, 'medium'), hexc(HUDC), alpha=alpha * .8)
    draw_text(c, value_text, x, y - 26, mono(40, 'bold'), hexc('#FFFFFF'), 'center', alpha)

def signal_bars(c, x, y, level, alpha=1.0, n=5, color=None, lost=False):
    color = hexc(PAL['ok']) if color is None else color
    for i in range(n):
        h = 12 + i * 9
        on = level * n > i + .2
        col = hexc(PAL['danger'], .9) if lost else (color if on else hexc('#ffffff', .15))
        rrect(c, x + i * 16, y - h, 11, h, 3, P(with_alpha(col, alpha)))

# ================================================================ spacecraft
def draw_galileo_entry(c, x, y, s=1.0, ang=0.0, heat=0.0, t=0.0, alpha=1.0):
    """Galileo entry probe aeroshell, side view. Nose points along +x before rotation `ang` (deg)."""
    if alpha <= 0:
        return
    c.save(); c.translate(x, y); c.rotate(ang); c.scale(s, s)
    if heat > 0:
        # shock layer glow in front of nose
        glow(c, 70, 0, 260 * (0.6 + heat), hexc('#ff7a2a'), alpha * heat * .9)
        glow(c, 50, 0, 150 * (0.6 + heat), hexc('#fff0c8'), alpha * heat)
    # afterbody (conical back cover) - gold thermal blanket
    back = path_from([(-10, -78), (-10, 78), (-92, 34), (-92, -34)], True)
    c.drawPath(back, P(shader=lin((0, -78), (0, 78), [hexc('#f2cf72', alpha), hexc('#b8862d', alpha), hexc('#6b4a17', alpha)])))
    c.drawPath(back, P(hexc('#3a2a10', alpha * .8), stroke=2))
    for i in range(4):
        xx = -22 - i * 18
        c.drawLine(xx, -70 + i * 9.5, xx, 70 - i * 9.5, P(hexc('#fff3c4', .25 * alpha), stroke=1.5))
    # forebody heat shield: blunt cone (nose to +x)
    shield = skia.Path()
    shield.moveTo(-10, -82); shield.lineTo(36, -24)
    shield.quadTo(52, 0, 36, 24)
    shield.lineTo(-10, 82); shield.close()
    hc = mixc('#3b2a22', '#ff9a3c', heat * .9)
    c.drawPath(shield, P(shader=lin((-10, 0), (52, 0), [hexc('#1c1412', alpha), with_alpha(hc, alpha)])))
    c.drawPath(shield, P(hexc('#0b0806', alpha), stroke=2))
    if heat > 0.05:
        c.drawPath(shield, P(hexc('#ffd28a', alpha * heat * .8), stroke=4 + 6 * heat, blur=4))
    c.restore()

def draw_parachute(c, x, y, s, openk, sway=0.0, alpha=1.0, color='#f4f1ea', stripe='#e0583a'):
    if openk <= 0 or alpha <= 0:
        return
    c.save(); c.translate(x, y); c.rotate(sway); c.scale(s, s)
    w = lerp(20, 190, e_back(clamp(openk), 1.4)); h = lerp(120, 95, clamp(openk))
    top = -260
    # lines
    for fx in (-1, -.5, 0, .5, 1):
        c.drawLine(0, 0, fx * w * .92, top + h * .55, P(hexc('#d8d2c4', .7 * alpha), stroke=1.4))
    can = skia.Path()
    can.moveTo(-w, top + h * .55)
    can.cubicTo(-w * 1.02, top - h * .45, w * 1.02, top - h * .45, w, top + h * .55)
    for i in range(6):
        x0 = w - i * (2 * w / 6); x1 = w - (i + 1) * (2 * w / 6)
        can.quadTo((x0 + x1) / 2, top + h * .38, x1, top + h * .55)
    can.close()
    c.drawPath(can, P(shader=lin((-w, 0), (w, 0), [hexc(color, alpha), hexc('#bdb6a8', alpha)])))
    # stripes
    c.save(); c.clipPath(can, doAntiAlias=True)
    for i in (-1, 1):
        c.drawRect(skia.Rect(i * w * .33 - w * .12, top - h, i * w * .33 + w * .12, top + h), P(hexc(stripe, .85 * alpha)))
    c.restore()
    c.drawPath(can, P(hexc('#6d665a', .6 * alpha), stroke=2))
    c.restore()

def draw_galileo_descent(c, x, y, s=1.0, chute=1.0, sway=0.0, alpha=1.0, t=0.0, transmit=0.0, heat=0.0):
    """Galileo descent module hanging under parachute. (x,y) = module center."""
    if alpha <= 0:
        return
    c.save(); c.translate(x, y); c.rotate(sway)
    draw_parachute(c, 0, -40 * s, s, chute, 0, alpha)
    c.scale(s, s)
    # module: squat cylinder with domed top
    body = skia.Rect(-46, -38, 46, 30)
    c.drawRRect(skia.RRect.MakeRectXY(body, 10, 10), P(shader=lin((-46, 0), (46, 0), [hexc('#e9e3d2', alpha), hexc('#a9a291', alpha), hexc('#6c665a', alpha)])))
    c.drawOval(skia.Rect(-46, -50, 46, -26), P(shader=lin((-46, 0), (46, 0), [hexc('#f4c56a', alpha), hexc('#9b7428', alpha)])))
    c.drawRect(skia.Rect(-46, -6, 46, 2), P(hexc('#c99a3b', alpha)))
    for i in range(-3, 4):
        c.drawCircle(i * 12, 16, 3, P(hexc('#3b3a36', alpha)))
    c.drawLine(0, -50, 0, -40 * 1 - 18, P(hexc('#cfc8b6', alpha), stroke=3))
    if heat > 0:
        glow(c, 0, 0, 120, hexc('#ff6a2a'), heat * alpha * .7)
    c.restore()
    if transmit > 0:
        for i in range(4):
            ph = (t * 1.1 + i * .25) % 1.0
            rr = (40 + ph * 260) * s
            c.drawArc(skia.Rect(x - rr, y - 330 * s - rr, x + rr, y - 330 * s + rr), 235, 70, False,
                      P(hexc('#9FE3FF', alpha * transmit * (1 - ph) * .9), stroke=3.5 * s))

def draw_juno(c, x, y, s=1.0, rot=0.0, alpha=1.0, t=0.0):
    if alpha <= 0:
        return
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    for k in range(3):
        c.save(); c.rotate(k * 120 + 90)
        # solar array: 4 segments (one array shorter with magnetometer boom)
        n = 4 if k else 3
        for i in range(n):
            r = skia.Rect(40 + i * 62, -26, 98 + i * 62, 26)
            c.drawRect(r, P(shader=lin((0, -26), (0, 26), [hexc('#3d6bd6', alpha), hexc('#1b2f6a', alpha)])))
            c.drawRect(r, P(hexc('#a9c3ff', .55 * alpha), stroke=1.5))
            c.drawLine(r.centerX(), -26, r.centerX(), 26, P(hexc('#a9c3ff', .35 * alpha), stroke=1))
        if not k:
            c.drawLine(225, 0, 290, 0, P(hexc('#d9d4c6', alpha), stroke=3))
            c.drawRect(skia.Rect(282, -8, 298, 8), P(hexc('#d9d4c6', alpha)))
        c.restore()
    # hex body
    hexp = path_from([(math.cos(math.radians(60 * i)) * 44, math.sin(math.radians(60 * i)) * 44) for i in range(6)], True)
    c.drawPath(hexp, P(shader=lin((-44, -44), (44, 44), [hexc('#e7e1cf', alpha), hexc('#8b8574', alpha)])))
    c.drawCircle(0, 0, 30, P(shader=rad(-8, -8, 34, [hexc('#ffffff', alpha), hexc('#bdb7a6', alpha)])))
    c.drawCircle(0, 0, 30, P(hexc('#6f6a5d', alpha), stroke=2))
    c.restore()

# ================================================================ explorer + capsule
SKIN = '#B87A56'; SKIN_D = '#8E5A3E'; SUIT = '#ECE8DF'; SUIT_D = '#B9B3A6'; ACC = '#E39A3B'

def draw_explorer_face(c, cx, cy, s, look=(0, 0), blink=0.0, brow=0.0, mouth='neutral', alpha=1.0,
                       visor_tint=0.32, light='#ffd6a0', light_amt=0.4, helmet=True, sweat=0.0):
    """Explorer head inside helmet. s = helmet radius. brow: +1 raised (awe), -1 worried."""
    if alpha <= 0:
        return
    c.save(); c.translate(cx, cy)
    if helmet:
        c.drawCircle(0, 0, s, P(shader=rad(-s * .35, -s * .4, s * 1.5, [hexc('#ffffff', alpha), hexc(SUIT, alpha), hexc('#8d877a', alpha)], [0, .5, 1])))
        c.drawCircle(0, 0, s, P(hexc('#5a554b', alpha * .9), stroke=s * .025))
        # helmet lamp
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-s * .16, -s * .98, s * .16, -s * .86), 6, 6), P(hexc('#56504a', alpha)))
        c.drawCircle(0, -s * .92, s * .045, P(hexc('#bff3ff', alpha)))
    # visor opening
    vis = skia.RRect.MakeRectXY(skia.Rect(-s * .74, -s * .62, s * .74, s * .66), s * .5, s * .5)
    c.save(); c.clipRRect(vis, doAntiAlias=True)
    c.drawRRect(vis, P(hexc('#1a1410', alpha)))
    # face
    face = skia.Rect(-s * .5, -s * .5, s * .5, s * .7)
    c.drawOval(face, P(shader=rad(-s * .15, -s * .2, s * .8, [hexc('#c98c66', alpha), hexc(SKIN, alpha), hexc(SKIN_D, alpha)], [0, .55, 1])))
    # hair line under helmet
    hair = skia.Path(); hair.moveTo(-s * .52, -s * .1); hair.cubicTo(-s * .5, -s * .62, s * .5, -s * .62, s * .52, -s * .1)
    hair.cubicTo(s * .3, -s * .34, -s * .2, -s * .4, -s * .52, -s * .1); hair.close()
    c.drawPath(hair, P(hexc('#2a1c15', alpha)))
    # eyes
    lx, ly = look
    eo = clamp(1 - blink)
    for side in (-1, 1):
        ex, ey = side * s * .21, s * .02
        ew, eh = s * .135, s * .16 * max(eo, .06)
        if brow < 0:  # fear: eyes wider
            eh *= 1 + (-brow) * .18; ew *= 1 + (-brow) * .08
        c.drawOval(skia.Rect(ex - ew, ey - eh, ex + ew, ey + eh), P(hexc('#fbf7f0', alpha)))
        if eo > .15:
            c.save(); c.clipRect(skia.Rect(ex - ew, ey - eh, ex + ew, ey + eh))
            px, py = ex + lx * ew * .5, ey + ly * eh * .45
            pr = s * .075 * (0.85 if brow < -.5 else 1.0)
            c.drawCircle(px, py, pr, P(hexc('#3a2418', alpha)))
            c.drawCircle(px, py, pr * .55, P(hexc('#120b07', alpha)))
            c.drawCircle(px - pr * .35, py - pr * .4, pr * .3, P(hexc('#ffffff', alpha)))
            c.restore()
        # eyelid line
        c.drawArc(skia.Rect(ex - ew, ey - eh, ex + ew, ey + eh), 200, 140, False, P(hexc('#4a2a1a', alpha * .8), stroke=s * .022))
        # brows
        by = ey - s * .2 - brow * s * .06
        inner = -brow * s * .05 if brow < 0 else 0
        c.drawLine(ex - side * s * .02 - side * s * 0 , by - inner * (1 if side else 0), ex + side * s * .14, by + (s * .02 if brow >= 0 else inner * .4),
                   P(hexc('#2a1c15', alpha), stroke=s * .045, cap='round'))
    # nose
    c.drawArc(skia.Rect(-s * .05, s * .14, s * .05, s * .24), 20, 140, False, P(hexc(SKIN_D, alpha), stroke=s * .025, cap='round'))
    # mouth
    my = s * .38
    mp = P(hexc('#5a2a1e', alpha), stroke=s * .03, cap='round')
    if mouth == 'smile':
        c.drawArc(skia.Rect(-s * .14, my - s * .1, s * .14, my + s * .06), 20, 140, False, mp)
    elif mouth == 'o':
        c.drawOval(skia.Rect(-s * .05, my - s * .05, s * .05, my + s * .07), P(hexc('#4a1e16', alpha)))
    elif mouth == 'grit':
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-s * .12, my - s * .03, s * .12, my + s * .04), 4, 4), P(hexc('#f3eee6', alpha)))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-s * .12, my - s * .03, s * .12, my + s * .04), 4, 4), P(hexc('#5a2a1e', alpha), stroke=s * .02))
    elif mouth == 'frown':
        c.drawArc(skia.Rect(-s * .12, my, s * .12, my + s * .14), 200, 140, False, mp)
    else:
        c.drawLine(-s * .09, my, s * .09, my, mp)
    if sweat > 0:
        c.drawOval(skia.Rect(s * .36, -s * .1, s * .42, s * .0), P(hexc('#cfefff', alpha * sweat)))
    c.restore()  # visor clip
    # visor glass tint + reflections
    c.drawRRect(vis, P(hexc('#0d2440', visor_tint * alpha)))
    c.drawRRect(vis, P(shader=lin((-s * .7, -s * .6), (s * .7, s * .6), [hexc(light, light_amt * .35 * alpha), hexc(light, 0)])))
    hl = skia.Path(); hl.addArc(skia.Rect(-s * .66, -s * .56, s * .66, s * .6), 200, 50)
    c.drawPath(hl, P(hexc('#ffffff', .5 * alpha), stroke=s * .04, cap='round'))
    c.drawRRect(vis, P(hexc('#3c3a36', alpha), stroke=s * .05))
    c.restore()

def draw_explorer_bust(c, cx, cy, s, alpha=1.0, **face):
    """Helmet head at (cx,cy) radius s plus shoulders below."""
    if alpha <= 0:
        return
    # shoulders / torso
    tor = skia.Path()
    tor.moveTo(-s * 1.75, s * 2.6); tor.cubicTo(-s * 1.8, s * 1.15, -s * 1.2, s * .8, 0, s * .8)
    tor.cubicTo(s * 1.2, s * .8, s * 1.8, s * 1.15, s * 1.75, s * 2.6); tor.close()
    c.save(); c.translate(cx, cy)
    c.drawPath(tor, P(shader=lin((-s * 1.6, 0), (s * 1.6, 0), [hexc('#ffffff', alpha), hexc(SUIT, alpha), hexc(SUIT_D, alpha)])))
    c.drawPath(tor, P(hexc('#6a655a', alpha), stroke=s * .025))
    # accent stripes and chest panel
    c.drawLine(-s * 1.45, s * 1.35, -s * .7, s * 1.05, P(hexc(ACC, alpha), stroke=s * .09, cap='round'))
    c.drawLine(s * 1.45, s * 1.35, s * .7, s * 1.05, P(hexc(ACC, alpha), stroke=s * .09, cap='round'))
    rrect(c, -s * .42, s * 1.3, s * .84, s * .55, s * .08, P(hexc('#2d3440', alpha)))
    for i, col in enumerate(('#58E08A', '#FFB347', '#6FD3FF')):
        c.drawCircle(-s * .22 + i * s * .22, s * 1.48, s * .055, P(hexc(col, alpha)))
    c.drawRect(skia.Rect(-s * .3, s * 1.62, s * .3, s * 1.7), P(hexc('#6FD3FF', .6 * alpha)))
    # collar ring
    c.drawOval(skia.Rect(-s * .78, s * .62, s * .78, s * 1.02), P(hexc('#8d877a', alpha)))
    c.drawOval(skia.Rect(-s * .7, s * .66, s * .7, s * .96), P(hexc('#56504a', alpha)))
    c.restore()
    draw_explorer_face(c, cx, cy, s, alpha=alpha, **face)

def capsule_path(s):
    p = skia.Path()
    p.moveTo(0, -150 * s)
    p.cubicTo(95 * s, -150 * s, 120 * s, -40 * s, 112 * s, 40 * s)
    p.cubicTo(105 * s, 110 * s, 60 * s, 150 * s, 0, 160 * s)
    p.cubicTo(-60 * s, 150 * s, -105 * s, 110 * s, -112 * s, 40 * s)
    p.cubicTo(-120 * s, -40 * s, -95 * s, -150 * s, 0, -150 * s)
    p.close()
    return p

def draw_capsule(c, x, y, s=1.0, ang=0.0, alpha=1.0, t=0.0, heat=0.0, shield=0.0, face=None, lamp=True,
                 hull_light='#fff1d6', ambient='#E3B47A'):
    """Fictional explorer capsule (graphite pod, amber band, big round window). Nose (heat shield) at bottom."""
    if alpha <= 0:
        return
    c.save(); c.translate(x, y); c.rotate(ang)
    if shield > 0:
        for i in range(3):
            rr = 210 * s + i * 14 * s + math.sin(t * 3 + i) * 4 * s
            c.drawOval(skia.Rect(-rr * .82, -rr, rr * .82, rr), P(hexc('#8fd8ff', alpha * shield * (.35 - i * .09)), stroke=3 * s))
        glow(c, 0, 0, 300 * s, hexc('#4c8dff'), alpha * shield * .35)
    if heat > 0:
        glow(c, 0, 170 * s, 300 * s * (0.6 + heat), hexc('#ff7a2a'), alpha * heat)
        glow(c, 0, 150 * s, 160 * s * (0.6 + heat), hexc('#fff0c8'), alpha * heat)
    body = capsule_path(s)
    c.drawPath(body, P(shader=lin((-112 * s, -60 * s), (112 * s, 60 * s), [hexc('#5d6470', alpha), hexc('#3a3f49', alpha), hexc('#1d2027', alpha)], [0, .45, 1])))
    # ambient bounce from the environment (bottom/right)
    c.save(); c.clipPath(body, doAntiAlias=True)
    c.drawPaint(P(shader=lin((0, -150 * s), (0, 160 * s), [hexc(ambient, 0), hexc(ambient, .22 * alpha)])))
    # heat shield nose
    c.drawOval(skia.Rect(-130 * s, 95 * s, 130 * s, 230 * s), P(shader=lin((0, 95 * s), (0, 170 * s), [hexc('#2a201b', alpha), with_alpha(mixc('#3b2a22', '#ff9a3c', heat), alpha)])))
    # panel lines
    for yy in (-95, 70):
        c.drawLine(-130 * s, yy * s, 130 * s, yy * s, P(hexc('#0e1014', .6 * alpha), stroke=2 * s))
    # amber band
    c.drawRect(skia.Rect(-130 * s, -20 * s, 130 * s, -2 * s), P(hexc(ACC, alpha)))
    # rim light
    c.restore()
    c.drawPath(body, P(hexc(hull_light, .35 * alpha), stroke=3 * s))
    c.drawPath(body, P(hexc('#0b0c10', .8 * alpha), stroke=1.5 * s))
    # fins
    for side in (-1, 1):
        fin = path_from([(side * 98 * s, 70 * s), (side * 140 * s, 120 * s), (side * 128 * s, 140 * s), (side * 86 * s, 112 * s)], True)
        c.drawPath(fin, P(hexc('#2a2e36', alpha)))
        c.drawPath(fin, P(hexc(ACC, .8 * alpha), stroke=2 * s))
    # window
    wx, wy, wr = -8 * s, -62 * s, 62 * s
    c.drawCircle(wx, wy, wr + 12 * s, P(hexc('#22262e', alpha)))
    c.drawCircle(wx, wy, wr + 12 * s, P(hexc('#8b919c', alpha), stroke=3 * s))
    for i in range(8):
        a_ = i * math.pi / 4
        c.drawCircle(wx + math.cos(a_) * (wr + 6 * s), wy + math.sin(a_) * (wr + 6 * s), 2.6 * s, P(hexc('#aab0ba', alpha)))
    c.save(); c.clipPath(skia.Path().addCircle(wx, wy, wr), doAntiAlias=True)
    c.drawCircle(wx, wy, wr, P(hexc('#0e1a26', alpha)))
    c.drawCircle(wx, wy, wr, P(shader=rad(wx, wy + 40 * s, wr * 1.3, [hexc('#2b4a66', alpha * .9), hexc('#0e1a26', alpha)])))
    if face is not None:
        f = dict(face); f.setdefault('alpha', alpha)
        draw_explorer_bust(c, wx + 2 * s, wy + 2 * s, 40 * s, **f)
    # glass reflection
    c.drawArc(skia.Rect(wx - wr * .8, wy - wr * .8, wx + wr * .8, wy + wr * .8), 200, 60, False, P(hexc('#ffffff', .45 * alpha), stroke=5 * s, cap='round'))
    c.drawCircle(wx, wy, wr, P(hexc('#6FD3FF', .12 * alpha)))
    c.restore()
    # top lamp / antenna
    c.drawLine(0, -150 * s, 0, -182 * s, P(hexc('#9aa0aa', alpha), stroke=3 * s))
    if lamp:
        bl = .5 + .5 * math.sin(t * 5.0)
        c.drawCircle(0, -184 * s, 5 * s, P(hexc('#ff5a4a', alpha * (.4 + .6 * bl))))
        glow(c, 0, -184 * s, 26 * s, hexc('#ff5a4a'), alpha * bl * .7)
    c.restore()

# ================================================================ Jupiter interior cross-section
def draw_cross_section(c, cx, cy, R, alpha=1.0, wedge=(-90, 90), t=0.0, core_fuzz=1.0, core_alpha=1.0,
                       metal_glow=0.6, show_metal=1.0, rot=1.2, sphere=True, dark_unknown=0.0, highlight=None):
    """Planet drawn as textured sphere with a pie-slice cutaway (angles in deg, 0=right, clockwise).
    Layer radii (fraction of R) are illustrative, model-based:
      clouds/atmosphere skin ~1.0, molecular H2 fluid to ~0.83, metallic H to ~0.3-0.5, dilute core."""
    if alpha <= 0:
        return
    if sphere:
        draw_jupiter(c, cx, cy, R, rot, alpha)
    a0, a1 = wedge
    sweep = a1 - a0
    if sweep <= 0.1:
        return
    pie = skia.Path(); pie.moveTo(cx, cy); pie.arcTo(skia.Rect(cx - R, cy - R, cx + R, cy + R), a0, sweep, False); pie.close()
    c.save(); c.clipPath(pie, doAntiAlias=True)
    # molecular hydrogen envelope: amber -> deep brown-red with depth
    c.drawCircle(cx, cy, R, P(shader=rad(cx, cy, R, [hexc('#5a1f12', alpha), hexc('#8a3b1f', alpha), hexc('#c7783c', alpha), hexc('#e8b27a', alpha)], [0, .7, .93, 1.0])))
    # metallic hydrogen region
    if show_metal > 0:
        mr = R * 0.80
        c.drawCircle(cx, cy, mr, P(shader=rad(cx, cy, mr, [hexc('#24205e', alpha * show_metal), hexc('#2d2a7a', alpha * show_metal), hexc('#3b3f9e', alpha * show_metal), hexc('#3b3f9e', 0)], [0, .6, .97, 1.0])))
        if metal_glow > 0:
            # shimmering conductive glow
            for i in range(14):
                aa = math.radians(a0 + sweep * ((i * .37 + t * .03) % 1.0))
                rr = mr * (.45 + .45 * ((i * .61) % 1.0))
                glow(c, cx + math.cos(aa) * rr, cy + math.sin(aa) * rr, R * .16, hexc('#7f8cff'), alpha * show_metal * metal_glow * (.35 + .25 * math.sin(t * 2 + i)))
    # core: compact (fuzz=0) or dilute (fuzz=1)
    if core_alpha > 0:
        cr_compact = R * .16; cr_fuzzy = R * .52
        cr = lerp(cr_compact, cr_fuzzy, core_fuzz)
        edge = lerp(.94, .0, core_fuzz)
        cols = [hexc('#f2d29a', alpha * core_alpha), hexc('#c98a4a', alpha * core_alpha), hexc('#9a5a3a', alpha * core_alpha * lerp(1, .55, core_fuzz)), hexc('#7a4a5a', 0)]
        c.drawCircle(cx, cy, cr, P(shader=rad(cx, cy, cr, cols, [0, lerp(.45, .2, core_fuzz), lerp(.97, .6, core_fuzz), 1.0])))
        if core_fuzz < .5:
            c.drawCircle(cx, cy, cr, P(hexc('#fff1d6', alpha * core_alpha * (1 - core_fuzz * 2) * .8), stroke=3))
        if core_fuzz > 0.05:
            rng = np.random.default_rng(4)
            for i in range(160):
                aa = math.radians(a0 + sweep * rng.random())
                rr = cr_fuzzy * (rng.random() ** 0.8) * lerp(.3, 1.05, core_fuzz)
                c.drawCircle(cx + math.cos(aa) * rr, cy + math.sin(aa) * rr, 2.2 + rng.random() * 2.5,
                             P(hexc('#ffe2b0', alpha * core_alpha * core_fuzz * .55)))
    if dark_unknown > 0:
        c.drawCircle(cx, cy, R * .97, P(shader=rad(cx, cy, R * .97, [rgba(4, 4, 10, dark_unknown * alpha), rgba(4, 4, 10, dark_unknown * alpha * .92), rgba(4, 4, 10, 0)], [0, .85, 1.0])))
    # cloud layer skin
    c.drawCircle(cx, cy, R * .985, P(hexc('#ffe7c2', .7 * alpha), stroke=max(2, R * .012)))
    c.restore()
    # cut edges
    for a_ in (a0, a1):
        ar = math.radians(a_)
        c.drawLine(cx, cy, cx + math.cos(ar) * R, cy + math.sin(ar) * R, P(hexc('#fff1d6', .5 * alpha), stroke=2))
    if highlight is not None:
        r_in, r_out, col = highlight
        hp = skia.Path(); hp.addArc(skia.Rect(cx - r_out * R, cy - r_out * R, cx + r_out * R, cy + r_out * R), a0, sweep)
        hp.arcTo(skia.Rect(cx - r_in * R, cy - r_in * R, cx + r_in * R, cy + r_in * R), a1, -sweep, False); hp.close()
        c.drawPath(hp, P(hexc(col, .9 * alpha), stroke=3.5))

# ================================================================ field lines, molecules
def dipole_lines(c, cx, cy, R, alpha=1.0, k=1.0, t=0.0, Ls=(1.6, 2.2, 3.0, 4.2, 5.8), color='#6FD3FF', tilt=-10, width=3):
    if alpha <= 0 or k <= 0:
        return
    c.save(); c.translate(cx, cy); c.rotate(tilt)
    for L in Ls:
        for side in (-1, 1):
            pts = []
            th0 = math.asin(min(1, math.sqrt(1 / L)))
            n = 80
            for i in range(n + 1):
                th = th0 + (math.pi - 2 * th0) * i / n
                r = L * R * math.sin(th) ** 2
                pts.append((side * r * math.sin(th), -r * math.cos(th)))
            pa = path_from(pts)
            pp = P(hexc(color, alpha * .55), stroke=width)
            pp.setPathEffect(skia.DashPathEffect.Make([18, 12], -t * 40))
            stroke_path_k(c, pa, pp, k)
            stroke_path_k(c, pa, P(hexc(color, alpha * .18), stroke=width * 3.5, blur=6), k)
    c.restore()

def h2_molecule(c, x, y, r, ang, alpha=1.0, color='#FFF1D6', bond=1.0):
    dx, dy = math.cos(ang) * r * .75 * bond, math.sin(ang) * r * .75 * bond
    c.drawLine(x - dx, y - dy, x + dx, y + dy, P(hexc(color, alpha * .7), stroke=r * .35))
    for sgn in (-1, 1):
        c.drawCircle(x + sgn * dx, y + sgn * dy, r * .62, P(shader=rad(x + sgn * dx - r * .2, y + sgn * dy - r * .2, r * .9, [hexc('#ffffff', alpha), hexc(color, alpha)])))
```

## A.4 `engine/common.py` — Environments: space, multiplane clouds, speed lines, particles (134 lines)

```python
# Shared environment renderers used by scenes.
import math, functools
import numpy as np
import skia
from core import *
from assets import *
from elements import *

@functools.lru_cache(None)
def grad_img(key, top, bottom, mid=None, w=64, h=256, radial=False):
    s = skia.Surface(w, h); c = s.getCanvas()
    cols = [hexc(top), hexc(mid), hexc(bottom)] if mid else [hexc(top), hexc(bottom)]
    if radial:
        c.drawPaint(P(shader=rad(w / 2, h / 2, max(w, h) * .75, cols)))
    else:
        c.drawPaint(P(shader=lin((0, 0), (0, h), cols)))
    return s.makeImageSnapshot()

def bg(c, top, bottom, mid=None, alpha=1.0):
    img = grad_img((top, bottom, mid), top, bottom, mid)
    draw_img(c, img, 0, 0, W, H, alpha)

def space(c, t, zoom=1.0, ox=0.0, oy=0.0, alpha=1.0, star_alpha=1.0, seed=1):
    bg(c, '#0b1230', '#05070f', '#070B1A', alpha)
    # faint nebula haze
    draw_img(c, grad_img('neb', '#1C2A55', '#070B1A', w=128, h=128, radial=True), -300 + ox * .1, -200 + oy * .1, W + 600, H + 400, .35 * alpha)
    draw_stars(c, t, star_alpha * alpha, ox, oy, zoom, seed)

# ---------------------------------------------------------------- multiplane clouds (falling = clouds move up)
CLOUD_LAYERS = [  # depth factor, scale, count, alpha, brightness
    (0.25, 0.55, 9, .55, .70),
    (0.45, 0.85, 8, .75, .82),
    (0.75, 1.30, 6, .90, .95),
    (1.30, 2.30, 4, .95, 1.05),
]

@functools.lru_cache(None)
def _cloud_layout(seed, n):
    rng = np.random.default_rng(seed)
    return rng.random((n, 4))

def cloud_world(c, t, fall=60.0, drift=0.0, tint=(1.0, .78, .52), bg_top='#E3B47A', bg_bot='#7a4426', bg_mid=None,
                layers=None, alpha=1.0, density=1.0, haze=0.0, ox=0.0, oy=0.0, fg=True, bg_draw=True, depth_dark=0.0):
    """fall: px/s upward motion of the nearest layer. drift: horizontal px/s."""
    if bg_draw:
        bg(c, bg_top, bg_bot, bg_mid, alpha)
    sprites = cloud_sprites()
    lays = CLOUD_LAYERS if layers is None else layers
    for li, (dep, sc, cnt, la, br) in enumerate(lays):
        if not fg and dep > 1.0:
            continue
        lay = _cloud_layout(li * 13 + 7, cnt)
        span_y = H + 700 * sc
        span_x = W + 900 * sc
        dk = 1 - depth_dark * (1 - dep / 1.5) * .6
        cf = tint_cf(tint[0] * br * dk, tint[1] * br * dk, tint[2] * br * dk)
        for i in range(int(cnt * density + .5)):
            r = lay[i % cnt]
            x = (r[0] * span_x + drift * dep * t + ox * dep) % span_x - 450 * sc
            y = (r[1] * span_y - fall * dep * t + oy * dep) % span_y - 350 * sc
            img = sprites[int(r[2] * len(sprites)) % len(sprites)]
            w_ = 512 * sc * (0.8 + .5 * r[3]); h_ = 300 * sc * (0.8 + .5 * r[3])
            draw_img(c, img, x, y, w_, h_, alpha * la, cf=cf)
    if haze > 0:
        c.drawPaint(P(hexc(bg_bot, haze * alpha)))

def speed_lines(c, t, alpha, direction=(0, -1), n=60, speed=2400, length=180, color='#FFF1D6', seed=3, width=2.0):
    """Streaks moving along direction (unit vector)."""
    if alpha <= 0:
        return
    rng = np.random.default_rng(seed)
    pts = rng.random((n, 3))
    dx, dy = direction
    for i in range(n):
        ph = (pts[i, 2] + t * speed / 2400.0) % 1.0
        if abs(dy) > abs(dx):
            x = pts[i, 0] * W
            y = (pts[i, 1] * H + ph * (H + length) * (-dy)) % (H + length) - length
            # draw along direction
            c.drawLine(x, y, x - dx * length, y - dy * length, P(hexc(color, alpha * (.25 + .5 * pts[i, 0])), stroke=width))
        else:
            y = pts[i, 1] * H
            x = (pts[i, 0] * W + ph * (W + length) * (-dx)) % (W + length) - length
            c.drawLine(x, y, x - dx * length, y - dy * length, P(hexc(color, alpha * (.25 + .5 * pts[i, 1])), stroke=width))

def particles(c, t, alpha, n=120, vy=-80, vx=0, color='#FFF1D6', size=(1.5, 4), seed=5, blur=0):
    if alpha <= 0:
        return
    rng = np.random.default_rng(seed)
    pr = rng.random((n, 4))
    for i in range(n):
        d = .4 + pr[i, 3] * .8
        x = (pr[i, 0] * (W + 100) + vx * d * t) % (W + 100) - 50
        y = (pr[i, 1] * (H + 100) + vy * d * t) % (H + 100) - 50
        r = lerp(size[0], size[1], pr[i, 2]) * d
        c.drawCircle(x, y, r, P(hexc(color, alpha * (.3 + .5 * pr[i, 2])), blur=blur))

def flash(c, a, color='#FFF1D6'):
    if a > 0:
        c.drawPaint(P(hexc(color, clamp(a))))

def letter_dim(c, a):
    if a > 0:
        c.drawPaint(P(rgba(0, 0, 0, a)))

def depth_ruler(c, x, y0, y1, offset_px, alpha=1.0, step_px=120, label_fn=None, color=HUDC):
    """Scrolling vertical ruler on the right edge (offset moves ticks upward)."""
    if alpha <= 0:
        return
    c.drawLine(x, y0, x, y1, P(hexc(color, .5 * alpha), stroke=2))
    first = -((offset_px) % step_px)
    k0 = int(offset_px // step_px)
    yy = y0 + first
    i = 0
    while yy <= y1:
        if yy >= y0:
            c.drawLine(x - 18, yy, x, yy, P(hexc(color, .8 * alpha), stroke=2))
            if label_fn:
                draw_text(c, label_fn(k0 + i), x - 26, yy + 6, mono(16, 'medium'), hexc(color), 'right', alpha * .8)
        for j in range(1, 4):
            ys = yy + j * step_px / 4
            if y0 <= ys <= y1:
                c.drawLine(x - 8, ys, x, ys, P(hexc(color, .45 * alpha), stroke=1.5))
        yy += step_px; i += 1

def tex_strip_img(lat_top=30, lat_bot=-30):
    return _tex_strip(lat_top, lat_bot)

@functools.lru_cache(None)
def _tex_strip(lat_top, lat_bot):
    tex = jupiter_tex()
    th = tex.shape[0]
    r0 = int((0.5 - lat_top / 180) * th); r1 = int((0.5 - lat_bot / 180) * th)
    return to_img(tex[r0:r1])
```

## A.5 `engine/render.py` — Timeline, transitions, post, still/contact/bench/segment encode (146 lines)

```python
# Timeline assembly, transitions, post-processing, frame rendering, encoding.
import sys, os, math, subprocess, time
import numpy as np
import skia
from core import *
from assets import *
import glob, importlib
sys.path.insert(0, PROJECT)
SHOTS, _ends = [], []
for _f in sorted(glob.glob(os.path.join(PROJECT, 'scenes*.py'))):
    _m = importlib.import_module(os.path.splitext(os.path.basename(_f))[0])
    for _k, _v in vars(_m).items():
        if _k.startswith('SHOTS') and isinstance(_v, list):
            SHOTS += _v
    if hasattr(_m, 'END_T'):
        _ends.append(_m.END_T)
SHOTS.sort(key=lambda s: s[0])
END_T = max(_ends) if _ends else SHOTS[-1][0] + 8

_surfs = {}
def surf(key):
    if key not in _surfs:
        _surfs[key] = skia.Surface(W, H)
    return _surfs[key]

def shot_index(t):
    i = 0
    for k, s in enumerate(SHOTS):
        if s[0] <= t:
            i = k
    return i

def render_shot(c, k, t):
    c.save()
    try:
        SHOTS[k][1](c, t)
    finally:
        c.restore()

def post(c, t):
    draw_img(c, vignette_img(), 0, 0, W, H, 1.0)
    g = grain_imgs()[int(t * 24) % 6]
    p = skia.Paint(); p.setAlphaf(.045); p.setBlendMode(skia.BlendMode.kOverlay)
    c.drawImageRect(g, skia.Rect(0, 0, W, H), LIN, p)
    # global fade in/out
    if t < 0.0:
        c.drawPaint(P(rgba(0, 0, 0, 1)))
    if t > END_T - 1.6:
        c.drawPaint(P(rgba(0, 0, 0, e_io(prog(t, END_T - 1.6, END_T)))))

def render_frame(t):
    s = surf('main'); c = s.getCanvas()
    c.clear(skia.ColorBLACK)
    k = shot_index(t)
    start, fn, (ttype, tdur) = SHOTS[k]
    lt = t - start
    if k > 0 and ttype != 'cut' and lt < tdur:
        x = lt / tdur
        if ttype == 'fade':
            render_shot(c, k - 1, t)
            s2 = surf('b'); c2 = s2.getCanvas(); c2.clear(skia.ColorBLACK)
            render_shot(c2, k, t)
            p = skia.Paint(); p.setAlphaf(e_sine(x))
            c.drawImage(s2.makeImageSnapshot(), 0, 0, LIN, p)
        elif ttype == 'black':
            if x < .5:
                render_shot(c, k - 1, t)
                c.drawPaint(P(rgba(0, 0, 0, e_io(x * 2))))
            else:
                render_shot(c, k, t)
                c.drawPaint(P(rgba(0, 0, 0, 1 - e_io((x - .5) * 2))))
        elif ttype == 'flash':
            render_shot(c, k, t)
            c.drawPaint(P(hexc('#FFF1D6', (1 - e_out(x)) * .85)))
        elif ttype == 'whip':
            s2 = surf('b'); c2 = s2.getCanvas(); c2.clear(skia.ColorBLACK)
            if x < .5:
                render_shot(c2, k - 1, t); off = -e_in(x * 2) * W * .6
            else:
                render_shot(c2, k, t); off = (1 - e_out((x - .5) * 2)) * W * .6
            img = s2.makeImageSnapshot()
            blur = math.sin(math.pi * x)
            for j in range(7):
                p = skia.Paint(); p.setAlphaf(1 / (j + 1) if j else 1.0)
                c.drawImage(img, off - j * 40 * blur, 0, LIN, p) if j == 0 else c.drawImage(img, off - (j - 3) * 45 * blur, 0, LIN, p)
        else:
            render_shot(c, k, t)
    else:
        render_shot(c, k, t)
    post(c, t)
    return s

def frame_bytes(t):
    s = render_frame(t)
    return s.toarray()  # native BGRA

def still(t, path, scale=1.0):
    s = render_frame(t)
    img = s.makeImageSnapshot()
    if scale != 1.0:
        img = img.resize(int(W * scale), int(H * scale), skia.SamplingOptions(skia.FilterMode.kLinear))
    img.save(path, skia.kPNG)

def contact(times, path, cols=4, sc=.25):
    from PIL import Image
    tiles = []
    for t in times:
        s = render_frame(t)
        a = s.toarray(colorType=skia.kRGBA_8888_ColorType)
        im = Image.fromarray(a[..., :3]).resize((int(W * sc), int(H * sc)), Image.BILINEAR)
        from PIL import ImageDraw
        ImageDraw.Draw(im).text((6, 4), f'{t:.1f}', fill=(255, 255, 0))
        tiles.append(im)
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * int(W * sc), rows * int(H * sc)))
    for i, im in enumerate(tiles):
        sheet.paste(im, ((i % cols) * int(W * sc), (i // cols) * int(H * sc)))
    sheet.save(path)

def encode_segment(f0, f1, out, fps=FPS, crf=18, preset='faster'):
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', str(fps), '-i', '-',
           '-c:v', 'libx264', '-preset', preset, '-crf', str(crf), '-pix_fmt', 'yuv420p', '-threads', '2', '-tune', 'animation', out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    for f in range(f0, f1):
        t = f / fps
        p.stdin.write(frame_bytes(t).tobytes())
        if (f - f0) % 600 == 0:
            el = time.time() - t0
            print(f'[{out}] frame {f - f0}/{f1 - f0} {el:.0f}s', flush=True)
    p.stdin.close(); p.wait()

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'contact':
        a, b, step = float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
        times = list(np.arange(a, b, step))
        contact(times, sys.argv[5], cols=int(sys.argv[6]) if len(sys.argv) > 6 else 4)
    elif cmd == 'still':
        still(float(sys.argv[2]), sys.argv[3])
    elif cmd == 'seg':
        encode_segment(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], fps=int(sys.argv[5]) if len(sys.argv) > 5 else FPS)
    elif cmd == 'bench':
        ts = [float(x) for x in sys.argv[2:]]
        for t in ts:
            t0 = time.time(); frame_bytes(t); print(t, f'{(time.time() - t0) * 1000:.0f} ms')
```

## A.6 `engine/render_all.sh` — Parallel segment render + concat (16 lines)

```bash
#!/bin/bash
# Usage: ./render_all.sh <project_dir> <out_dir> [segments=8] [parallel=4] [fps=60]
# Renders the whole timeline in parallel segments, then concatenates them (video only).
set -e
ENGINE="$(cd "$(dirname "$0")" && pwd)"
export JV_PROJECT="$(cd "$1" && pwd)"; OUT="$(mkdir -p "$2" && cd "$2" && pwd)"
K=${3:-8}; P=${4:-4}; FPS=${5:-60}
N=$(cd "$ENGINE" && python3 -c "import render,math;print(math.ceil(render.END_T*$FPS))" 2>/dev/null)
step=$(( (N + K - 1) / K ))
mkdir -p "$OUT/seg"; : > "$OUT/list.txt"
for i in $(seq 0 $((K-1))); do
  a=$((i*step)); b=$(( (i+1)*step )); [ $b -gt $N ] && b=$N
  echo "$a $b $OUT/seg/s$i.mp4"; echo "file 'seg/s$i.mp4'" >> "$OUT/list.txt"
done | (cd "$ENGINE" && xargs -P"$P" -L1 bash -c 'python3 render.py seg $0 $1 $2 '"$FPS"' > $2.log 2>&1 || echo FAIL $2')
ffmpeg -v error -y -f concat -safe 0 -i "$OUT/list.txt" -c copy "$OUT/video_only.mp4"
echo "DONE $N frames -> $OUT/video_only.mp4"
```

## A.7 `engine/transcribe.py` — Word-level transcription (45 lines)

```python
"""Word-level transcription of the voiceover (offline, NVIDIA Parakeet TDT 0.6B v2 via sherpa-onnx).
Usage: python3 transcribe.py <voiceover.(mp3|wav)> <model_dir> <project_dir>
Writes project_dir/tokens.json, words.json ([word, start_s]) and words.txt (10 words per line with times).
Model: https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8.tar.bz2
"""
import sherpa_onnx, numpy as np, json, sys, os, subprocess
src, M, proj = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(proj, exist_ok=True)
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-ac', '1', '-ar', '16000', '-f', 's16le', '-'], capture_output=True, check=True).stdout
a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
sr = 16000
rec = sherpa_onnx.OfflineRecognizer.from_transducer(
    encoder=f"{M}/encoder.int8.onnx", decoder=f"{M}/decoder.int8.onnx", joiner=f"{M}/joiner.int8.onnx",
    tokens=f"{M}/tokens.txt", model_type="nemo_transducer", num_threads=os.cpu_count() or 4)
# Split into ~10-26 s chunks at the quietest 200 ms window (never mid-word).
fl = 320; n = len(a) // fl
e = np.sqrt((a[:n * fl].reshape(n, fl) ** 2).mean(1) + 1e-12)
cuts = [0]; pos = 0
while True:
    if pos + int(18 / 0.02) >= n: break
    lo, hi = pos + int(10 / 0.02), min(n, pos + int(26 / 0.02))
    seg = np.convolve(e[lo:hi], np.ones(10), 'valid'); k = lo + int(seg.argmin()) + 5
    cuts.append(k); pos = k
cuts.append(n)
tokens = []
for i in range(len(cuts) - 1):
    s, t = cuts[i] * fl, cuts[i + 1] * fl
    st = rec.create_stream(); st.accept_waveform(sr, a[s:t]); rec.decode_stream(st)
    r = st.result; off = s / sr
    tokens += [[tok, round(ts + off, 3)] for tok, ts in zip(r.tokens, r.timestamps)]
    print(f"{off:7.2f} {r.text}", flush=True)
json.dump(tokens, open(os.path.join(proj, 'tokens.json'), 'w'))
words, cur = [], None
for tok, ts in tokens:            # tokens starting with a space begin a new word
    if tok.startswith(' ') or cur is None:
        if cur: words.append(cur)
        cur = [tok.strip(), ts]
    else:
        cur[0] += tok
words.append(cur)
json.dump(words, open(os.path.join(proj, 'words.json'), 'w'))
with open(os.path.join(proj, 'words.txt'), 'w') as f:
    for i in range(0, len(words), 10):
        f.write(f"{words[i][1]:7.2f} " + " ".join(w for w, _ in words[i:i + 10]) + "\n")
print(len(words), 'words')
```

## A.8 `engine/sfxlib.py` — Sound engine: SFX synthesis, cues, ducking, mixdown, finishing (221 lines)

```python
"""Reusable sound-design library: synthesized SFX, music cue placement, VO-keyed ducking,
bus mixing and loudness finishing. Import it from a per-project cue sheet (see example_jupiter/mix.py).
All buffers are float32 stereo arrays at SR=48 kHz, shape (n, 2)."""
import subprocess, math, wave, json, re
import numpy as np
SR = 48000
rng = np.random.default_rng(1)

def load(path, filt=None):
    cmd = ['ffmpeg', '-v', 'error', '-i', path]
    if filt: cmd += ['-af', filt]
    cmd += ['-ac', '2', '-ar', str(SR), '-f', 'f32le', '-']
    a = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32)
    return a.reshape(-1, 2).copy()

def db(x): return 10 ** (x / 20)

def fade_env(n, fin, fout):
    e = np.ones(n, np.float32)
    fi, fo = int(fin * SR), int(fout * SR)
    if fi > 0: e[:fi] = np.linspace(0, 1, fi) ** 2 if fi <= n else e[:fi]
    if fo > 0: e[-fo:] *= np.linspace(1, 0, fo) ** 1.5
    return e

def place(bus, clip, t0, gain=1.0):
    i0 = int(t0 * SR)
    if i0 < 0: clip = clip[-i0:]; i0 = 0
    n = min(len(clip), len(bus) - i0)
    if n > 0: bus[i0:i0 + n] += clip[:n] * gain


# simple filters via FFT (offline, fine for clips)
def fft_filter(x, lo=None, hi=None):
    n = len(x); X = np.fft.rfft(x, axis=0); f = np.fft.rfftfreq(n, 1 / SR)
    m = np.ones_like(f)
    if lo: m *= 1 / (1 + (lo / np.maximum(f, 1)) ** 4)
    if hi: m *= 1 / (1 + (f / hi) ** 4)
    return np.fft.irfft(X * (m[:, None] if x.ndim == 2 else m), n=n, axis=0).astype(np.float32)

def noise(dur, st=True):
    n = int(dur * SR)
    return rng.standard_normal((n, 2) if st else n).astype(np.float32)

def st(x): return np.stack([x, x], 1)

def tvec(dur): return np.arange(int(dur * SR)) / SR

# ------------------------------------------------------------------ SFX generators
def boom(dur=3.0, f0=70, f1=28, amp=1.0, noise_amt=.5, hi=900):
    t = tvec(dur)
    f = f1 + (f0 - f1) * np.exp(-t * 3)
    ph = 2 * np.pi * np.cumsum(f) / SR
    sub = np.sin(ph) * np.exp(-t * 1.6)
    nz = fft_filter(noise(dur, False), hi=hi) * np.exp(-t * 6) * noise_amt
    x = (sub + nz) * amp
    x[:200] *= np.linspace(0, 1, 200)
    return st(x.astype(np.float32))

def whoosh(dur=0.6, lo=300, hi=4000, amp=.5, peak=.55):
    t = tvec(dur)
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2
    env = np.where(t / dur < peak, (t / dur / peak) ** 2, ((1 - t / dur) / (1 - peak)) ** 1.5)
    n = fft_filter(noise(dur), lo=lo, hi=hi)
    n /= np.abs(n).max() + 1e-9
    pan = np.stack([1 - .3 * t / dur, .7 + .3 * t / dur], 1)
    return (n * env[:, None] * pan * amp).astype(np.float32)

def riser(dur=4.0, amp=.35):
    t = tvec(dur)
    f = 120 * (2 ** (3 * t / dur))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * .5 + np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR) * .3
    n = fft_filter(noise(dur, False), lo=800, hi=9000) * .6
    env = (t / dur) ** 2.2
    x = (s + n * (t / dur)) * env * amp
    x[-400:] *= np.linspace(1, 0, 400)
    return st(x.astype(np.float32))

def blip(f=1200, dur=.09, amp=.25):
    t = tvec(dur)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t * 40) * amp
    return st(x.astype(np.float32))

def ui_pop(amp=.18):
    return blip(1800, .06, amp) + np.pad(blip(2400, .05, amp * .6), ((int(.03 * SR), 0), (0, 0)))[:int(.06 * SR)]

def alarm(dur=1.2, amp=.18):
    t = tvec(dur)
    f = np.where((t * 4) % 1 < .5, 880, 660)
    x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * .3 + np.sin(2 * np.pi * np.cumsum(f) / SR) * .7
    x = fft_filter(x, hi=3000) * amp * fade_env(len(t), .02, .1)
    return st(x.astype(np.float32))

def tone(f, dur, amp, fin=.01, fout=.2):
    t = tvec(dur)
    return st((np.sin(2 * np.pi * f * t) * amp * fade_env(len(t), fin, fout)).astype(np.float32))

def static(dur, amp=.25):
    n = fft_filter(noise(dur), lo=1500, hi=8000)
    n /= np.abs(n).max()
    gate = (rng.random(int(dur * 60)) > .3).repeat(SR // 60)[:len(n)]
    gate = np.pad(gate, (0, len(n) - len(gate)))
    return (n * gate[:, None] * amp * fade_env(len(n), .005, .1)[:, None]).astype(np.float32)

def rumble(dur, amp, lo=25, hi=220, mod=.5):
    t = tvec(dur)
    n = fft_filter(noise(dur), lo=lo, hi=hi); n /= np.abs(n).max()
    m = 1 + mod * np.sin(2 * np.pi * .7 * t)[:, None]
    return (n * m * amp).astype(np.float32)

def creak(dur=1.4, amp=.3, f0=90):
    t = tvec(dur)
    f = f0 * (1 + .25 * np.sin(2 * np.pi * .6 * t)) * (1 - .2 * t / dur)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = (np.sin(ph) + .5 * np.sin(2 * ph * 1.01) + .3 * np.sin(3.7 * ph)) * (1 + .5 * np.sin(2 * np.pi * 23 * t))
    x = x * fade_env(len(t), .08, .5) * amp
    return st(fft_filter(x.astype(np.float32), lo=60, hi=1500))

def shimmer(dur, amp=.12):
    t = tvec(dur); x = np.zeros(len(t), np.float32)
    for f in (1760, 2217, 2637, 3520, 4186):
        x += np.sin(2 * np.pi * f * t + rng.random() * 6) * (0.5 + .5 * np.sin(2 * np.pi * rng.uniform(.3, 1.2) * t))
    x = x / 5 * amp * fade_env(len(t), dur * .3, dur * .4)
    return np.stack([x, np.roll(x, 900)], 1).astype(np.float32)

def crackle(dur, amp=.2, rate=25):
    n = int(dur * SR); x = np.zeros((n, 2), np.float32)
    k = int(rate * dur)
    for i in range(k):
        p = rng.integers(0, n - 2000); L = rng.integers(200, 1500)
        b = fft_filter(rng.standard_normal(L).astype(np.float32), lo=2000, hi=12000) * np.exp(-np.arange(L) / (L / 5))
        pan = rng.random()
        x[p:p + L, 0] += b * (1 - pan) * amp; x[p:p + L, 1] += b * pan * amp
    return x * fade_env(n, .5, .8)[:, None]

def hum(dur, amp=.12, f=55):
    t = tvec(dur)
    x = (np.sin(2 * np.pi * f * t) + .5 * np.sin(2 * np.pi * 2 * f * t + 1) + .25 * np.sin(2 * np.pi * 3.01 * f * t)) * (1 + .3 * np.sin(2 * np.pi * .25 * t))
    return st((x * amp * fade_env(len(t), 1.5, 2.0) / 1.75).astype(np.float32))

def drone(dur, amp=.15, fs=(55, 82.4, 110)):
    t = tvec(dur); x = np.zeros(len(t))
    for i, f in enumerate(fs):
        x += np.sin(2 * np.pi * f * t * (1 + .002 * np.sin(2 * np.pi * .1 * t + i)))
    x = x / len(fs)
    n = fft_filter(noise(dur, False), lo=100, hi=600) * .15
    y = (x + n) * amp * fade_env(len(t), 2.5, 3.0)
    return np.stack([y, np.roll(y, 1200)], 1).astype(np.float32)

def wind(dur, amp=.12, hi=1200):
    t = tvec(dur)
    n = fft_filter(noise(dur), lo=150, hi=hi); n /= np.abs(n).max()
    m = (0.6 + .4 * np.sin(2 * np.pi * .13 * t) * np.sin(2 * np.pi * .07 * t + 1))[:, None]
    return (n * m * amp * fade_env(len(t), 1.0, 1.5)[:, None]).astype(np.float32)

def chute_snap(amp=.4):
    w = whoosh(.7, 400, 6000, amp * .7, .8)
    t = tvec(.25); snap = fft_filter(noise(.25, False), lo=200, hi=3000) * np.exp(-t * 25) * amp
    out = np.zeros((int(.95 * SR), 2), np.float32)
    out[:len(w)] += w; out[int(.68 * SR):int(.68 * SR) + len(snap)] += st(snap.astype(np.float32))
    return out

def thud(amp=.25):
    return boom(.5, 140, 60, amp, .3, hi=600)


# ------------------------------------------------------------------ mixing helpers
def cue(bus, track, t_prog, t_track, dur, fin, fout, gain_db):
    """Place a music excerpt: track[t_track : t_track+dur] at program time t_prog, with fades (s) and gain (dB)."""
    seg = track[int(t_track * SR):int((t_track + dur) * SR)]
    seg = seg * fade_env(len(seg), fin, fout)[:, None]
    place(bus, seg, t_prog, db(gain_db))

def music_energy(path, step=4.0):
    """Print RMS dB every `step` s - use it to find each track's intro / build / peak / outro."""
    a = load(path).mean(1); w = int(SR * step); n = len(a) // w
    r = 20 * np.log10(np.sqrt((a[:n * w].reshape(n, w) ** 2).mean(1)) + 1e-9)
    return [(round(i * step, 1), round(float(d), 1)) for i, d in enumerate(r)]

def duck_envelope(voice, depth=.62, attack=.03, release=.45):
    """Gain curve (n,) that dips music under speech. depth .62 = about -8.4 dB at full speech."""
    mono = np.abs(voice[:, 0]); win = int(.02 * SR)
    env = np.sqrt(np.convolve(mono ** 2, np.ones(win) / win, 'same'))
    env = np.clip(env / (np.percentile(env[env > 1e-4], 90) + 1e-9), 0, 1)
    sm = np.empty_like(env); a_att = math.exp(-1 / (attack * SR)); a_rel = math.exp(-1 / (release * SR)); s = 0.0
    step = 48
    for i in range(0, len(env), step):
        v = env[i]; a = a_att if v > s else a_rel
        s = a ** step * s + (1 - a ** step) * v
        sm[i:i + step] = s
    return np.clip(sm * 1.4, 0, 1), depth

VO_CHAIN = 'highpass=f=70,equalizer=f=3000:t=q:w=1.2:g=1.5,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2'

def mixdown(voice, music, sfx, amb, out_wav, music_db=-9, sfx_db=-3, amb_db=-4, duck_depth=.62, amb_duck=.45):
    env, _ = duck_envelope(voice, duck_depth)
    music = music * (1 - duck_depth * env)[:, None]
    amb = amb * (1 - amb_duck * env)[:, None]
    mix = voice + music * db(music_db) + sfx * db(sfx_db) + amb * db(amb_db)
    pcm = (np.clip(mix / max(1.0, np.abs(mix).max()), -1, 1) * 32767).astype(np.int16)
    with wave.open(out_wav, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    return out_wav

def integrated_lufs(path):
    out = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    tail = out[out.rfind('Summary:'):]
    I = float(re.search(r'I:\s+(-?[\d.]+) LUFS', tail).group(1))
    tp = float(re.search(r'Peak:\s+(-?[\d.]+) dBFS', tail).group(1))
    return I, tp

def finish(raw_wav, out_wav, target=-14.0, limit_db=-2.0):
    """Static gain to the target + brick-wall limiter. NOT loudnorm dynamic mode: that would
    lift deliberate silences and flatten the dramatic arc."""
    I, _ = integrated_lufs(raw_wav)
    g = target - I
    lim = 10 ** (limit_db / 20)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw_wav, '-af',
                    f'volume={g:.2f}dB,alimiter=limit={lim:.3f}:attack=3:release=120:level=false,aresample=48000',
                    '-c:a', 'pcm_s16le', out_wav], check=True)
    return integrated_lufs(out_wav)
```

## A.9 `engine/scenes_TEMPLATE.py` — Starter shot file (26 lines)

```python
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
```

## A.10 `engine/example_jupiter/scenes1.py` — Jupiter shots 01–17 (616 lines)

```python
# Shots 01-17 : hook, Galileo summary, the questions, nowhere to land, scale, Juno, speed.
from common import *

A = at  # alias
T_DROPPED = A('dropped a spacecraft')
T_SURV_ENTRY = A('It survived the entry')
T_WINDS = A('It survived winds')
T_KEPT = A('And it kept falling')
T_NOGROUND = A('no ground')
T_THEN58 = A('Then fifty eight')
T_ENDED = A('transmission ended')
T_BUTHERE = A("But here's the disturbing")
T_SCRATCH = A('barely scratched')
T_INTERIOR = A("Jupiter's enormous interior")
T_KEPTF = A('kept falling', after=30)
T_SOLID = A('Would you eventually hit')
T_OCEAN = A('Would you sink')
T_CENTER = A('Or could you actually reach')
T_LARGEST = A('largest planet', after=40)
T_FINDOUT = A('To find out')
T_REAL = A('follow the real spacecraft')
T_NOSPACE = A('go somewhere no spacecraft')
T_BUTFIRST = A("But first there's")
T_DIFFERENT = A('completely different')
T_EARTHFALL = A('falling toward Earth')
T_NOWHERE = A("There's nowhere to land")
T_PEACEFUL = A('From space')
T_STRIPES = A('Beautiful orange')
T_WRAP = A('wrap around')
T_REDOVAL = A('and that enormous red oval')
T_GRS = A("That's the great red spot")
T_CENTURIES = A('existed for centuries')
T_NOTGROUND = A("But those stripes aren't")
T_CLOUDS = A('They are clouds')
T_MOVING = A('they are moving')
T_WINDRACE = A('winds race')
T_ENORMOUS = A('The planet is so enormous')
T_1300 = A('thirteen hundred Earths')
T_YET = A('Yet somehow')
T_TENH = A('less than ten hours')
T_JET = A('powerful jet streams')
T_UNSETTLE = A("But here's where things")
T_JUNO = A('NASA Juno spacecraft discovered')
T_EXTEND = A('extend roughly')
T_3000 = A('three thousand kilometers below')
T_3000B = A('3000 kilometers')
T_STORMSYS = A('Imagine a storm system')
T_ABOUT = A("and you're about to fall")
T_OBSTACLE = A('But your first')
T_SPEED = A("It's your speed")
T_170 = A('one hundred seventy thousand')
T_SIMILAR = A('similar to the entry speed')
T_HIT = A('Then you hit the upper atmosphere')

HIST_TAG = 'HISTORICAL RECONSTRUCTION · GALILEO PROBE, 1995'

# ------------------------------------------------------------------ S01 hook
def s01(c, t):
    d = t
    zoom = tw(t, 0, T_DROPPED, 1.0, 1.07, e_sine)
    space(c, t, zoom=zoom, ox=-t * 6)
    c.save(); c.translate(W / 2, H / 2); c.scale(zoom, zoom); c.translate(-W / 2, -H / 2)
    draw_jupiter(c, 1430, 610, 720, rot=2.4 + t * 0.012)
    # tiny probe drifting toward the planet
    px = lerp(330, 560, e_sine(prog(t, 0, T_DROPPED + .5)))
    py = lerp(300, 420, e_sine(prog(t, 0, T_DROPPED + .5)))
    for i in range(14):
        c.drawCircle(px - i * 9, py - i * 4.6, 2.2 * (1 - i / 14), P(hexc('#FFF1D6', .35 * (1 - i / 14))))
    draw_galileo_entry(c, px, py, .17, 27)
    glow(c, px, py, 26, hexc('#FFB347'), .35 + .15 * math.sin(t * 4))
    c.restore()
    # title
    a = fade_window(t, 0.12, 3.35, .45, .45)
    f1 = font(76, 'black')
    draw_text(c, 'WHAT IF YOU ACTUALLY', 110, 250, f1, hexc('#FFF1D6'), alpha=a, shadow=1)
    draw_text(c, 'FELL INTO JUPITER?', 110, 338, f1, hexc('#E3B47A'), alpha=a * e_out(prog(t, .35, .9)), shadow=1, glow=.25)
    # scale callout to the probe after title
    k = prog(t, 3.4, 4.2)
    if k > 0:
        label_line(c, px - 8, py + 8, px - 120, py + 150, 'DEC 7, 1995', hexc('#FFB347'), alpha=1, k=k, size=34, sub='GALILEO PROBE · NASA')
        draw_tag(c, HIST_TAG, 40, 36, 'hist', alpha=e_out(k))

# ------------------------------------------------------------------ S02 dropped / survived entry
def s02(c, t):
    lt = t - T_DROPPED
    space(c, t, ox=-lt * 40)
    # planet limb filling bottom right
    draw_jupiter(c, 1250 - lt * 10, 2350, 1900, rot=2.1 + t * .01)
    p = e_in(prog(t, T_DROPPED, T_SURV_ENTRY + .2))
    px, py = lerp(380, 1180, p), lerp(170, 640, p)
    heat = e_in(prog(t, T_SURV_ENTRY - 1.4, T_SURV_ENTRY + .1)) * (1 - e_out(prog(t, T_SURV_ENTRY + .9, T_WINDS)))
    trail = heat
    if trail > 0:
        for i in range(30):
            q = i / 30
            glow(c, px - (px - 380) * q * .35, py - (py - 170) * q * .35, 60 * (1 - q) + 8, hexc('#ff8a3a'), trail * (1 - q) * .5)
    sc = lerp(.42, .55, p)
    draw_galileo_entry(c, px, py, sc, 30, heat=heat)
    flash(c, heat * .18, '#ffb070')
    k = prog(t, T_SURV_ENTRY + .55, T_SURV_ENTRY + 1.0)
    if k > 0:
        card(c, 1240, 140, 520, 120, e_out(k))
        draw_check(c, 1310, 200, 56, e_out(prog(t, T_SURV_ENTRY + .7, T_SURV_ENTRY + 1.2)))
        draw_text(c, 'ENTRY SURVIVED', 1365, 214, font(44, 'black'), hexc('#FFF1D6'), alpha=e_out(k))
    draw_tag(c, HIST_TAG, 40, 36, 'hist')

# ------------------------------------------------------------------ S03 winds
def s03(c, t):
    lt = t - T_WINDS
    cloud_world(c, t, fall=10, drift=-900, tint=(1, .8, .56), bg_top='#efc58f', bg_bot='#9a5a32')
    # wind streaks
    speed_lines(c, t, .55, direction=(-1, 0), n=70, speed=4200, length=260, color='#FFF1D6', width=3)
    sway = math.sin(t * 2.6) * 9 - 6
    draw_galileo_descent(c, 820 + math.sin(t * 1.3) * 30, 560, .9, chute=1, sway=sway, t=t)
    # comparison bars
    k1 = e_out(prog(t, T_WINDS + .5, T_WINDS + 1.1)); k2 = e_out(prog(t, T_WINDS + 1.6, T_WINDS + 2.4))
    x0, y0 = 1180, 160
    card(c, x0 - 30, y0 - 50, 700, 300, k1)
    draw_text(c, 'WIND SPEED', x0, y0, mono(22, 'semi'), hexc(HUDC), alpha=k1, spacing=2)
    draw_text(c, 'STRONG EARTH HURRICANE', x0, y0 + 50, font(24, 'bold'), hexc('#FFF1D6'), alpha=k1)
    rrect(c, x0, y0 + 65, 250 / 650 * 600 * k1, 30, 8, P(hexc('#6FD3FF', k1)))
    draw_text(c, '~250+ km/h', x0 + 250 / 650 * 600 * k1 + 14, y0 + 90, mono(22, 'bold'), hexc('#FFFFFF'), alpha=k1)
    draw_text(c, 'GALILEO-MEASURED WINDS', x0, y0 + 150, font(24, 'bold'), hexc('#FFF1D6'), alpha=k2)
    rrect(c, x0, y0 + 165, 520 * k2, 30, 8, P(hexc('#FF8A3A', k2)))
    draw_text(c, 'UP TO ~650 km/h', x0 + 10, y0 + 230, mono(22, 'bold'), hexc('#FFFFFF'), alpha=k2)
    draw_tag(c, HIST_TAG, 40, 36, 'hist')

# ------------------------------------------------------------------ S04 falling, no ground
def s04(c, t):
    lt = t - T_KEPT
    fall = 520
    cloud_world(c, t, fall=fall, drift=-30, tint=(1, .76, .5), bg_top='#d9a066', bg_bot='#6b3a20', depth_dark=.3)
    sway = math.sin(t * 2.2) * 5
    draw_galileo_descent(c, 960, 520 + math.sin(t * 1.7) * 8, 1.0, chute=1, sway=sway, t=t)
    depth_ruler(c, 1820, 120, 900, lt * 260, 1, label_fn=lambda i: '')
    k = prog(t, T_NOGROUND - .1, T_NOGROUND + .35)
    if k > 0:
        hud_panel(c, 1240, 700, 520, 110, 'SOLID GROUND BELOW', k, warn=True)
        draw_text(c, 'NONE DETECTED', 1300, 778, mono(40, 'bold'), hexc(PAL['danger']), alpha=k * (.75 + .25 * math.sin(t * 9)))
    draw_tag(c, HIST_TAG, 40, 36, 'hist')

# ------------------------------------------------------------------ S05 58 minutes, transmission ended
def s05(c, t):
    lt = t - T_THEN58
    bg(c, '#0a1022', '#04060c')
    end = T_ENDED + .25
    lost = t >= end
    # monitor panel
    x, y, w, h = 260, 200, 1400, 560
    hud_panel(c, x, y, w, h, 'GALILEO PROBE → ORBITER RELAY · TELEMETRY', 1)
    # timer
    mins = 58 * e_io(prog(t, T_THEN58 + .2, T_ENDED - .2))
    mm = int(mins); ss = int((mins - mm) * 60)
    draw_text(c, f'T+ {mm:02d}:{ss:02d}', x + w - 40, y + 110, mono(64, 'bold'), hexc('#FFFFFF'), 'right')
    draw_text(c, 'MINUTES OF DATA', x + w - 40, y + 145, mono(18, 'semi'), hexc(HUDC), 'right', spacing=1.5)
    # waveform
    pa = skia.Path()
    for i in range(0, 1101, 4):
        xx = x + 150 + i
        if lost:
            amp = 0
        else:
            amp = 70 * (1 - .5 * prog(t, T_ENDED - 1.5, end))
        yy = y + 330 + amp * math.sin(i * .045 + t * 14) * math.sin(i * .011 + t * 2.3)
        if i == 0: pa.moveTo(xx, yy)
        else: pa.lineTo(xx, yy)
    col = hexc(PAL['danger']) if lost else hexc(PAL['ok'])
    c.drawPath(pa, P(with_alpha(col, .35), stroke=9, blur=6))
    c.drawPath(pa, P(col, stroke=3))
    signal_bars(c, x + 40, y + 140, 0 if lost else 1 - .6 * prog(t, T_ENDED - 1.5, end), lost=lost)
    if lost:
        k = prog(t, end, end + .3)
        draw_text(c, 'SIGNAL LOST', x + w / 2, y + 480, font(72, 'black'), hexc(PAL['danger']), 'center', alpha=e_out(k), glow=.5)
    draw_tag(c, HIST_TAG, 40, 36, 'hist')

# ------------------------------------------------------------------ S06 barely scratched the surface (scale pull-out)
def s06(c, t):
    lt = t - T_BUTHERE
    space(c, t)
    R = 380
    cx, cy = 960, 600
    # camera: start zoomed on the top of the planet, pull out to full cross-section
    z = keys(t, [(T_BUTHERE, 9.0), (T_SCRATCH + .3, 9.0), (T_INTERIOR + 1.2, 1.0)], e_io)
    c.save()
    fy = cy - R  # focus at top of planet
    c.translate(960, lerp(540, 330, 1) if z > 1 else 330)
    c.translate(0, 0)
    c.restore()
    c.save()
    # focus point blends from planet top to centre
    fp = lerp(cy - R, cy - 60, e_io(prog(z, 9.0, 1.0)) if False else 1 - (z - 1) / 8)
    c.translate(960, lerp(420, 540, 1 - (z - 1) / 8)); c.scale(z, z); c.translate(-cx, -fp)
    draw_cross_section(c, cx, cy, R, wedge=(-90, 0), rot=2.0, dark_unknown=.82, core_alpha=0, show_metal=0, metal_glow=0, t=t)
    # galileo depth mark (~150 km of 69,911 km radius) at top of wedge
    dep = 150 / 69911 * R
    c.drawLine(cx + 4, cy - R, cx + 4, cy - R + max(dep, .15), P(hexc(PAL['danger']), stroke=3 / z))
    c.drawCircle(cx + 4, cy - R + dep, 5 / z, P(hexc(PAL['danger'])))
    glow(c, cx + 4, cy - R + dep, 22 / z, hexc(PAL['danger']), .8)
    c.restore()
    k1 = prog(t, T_SCRATCH, T_SCRATCH + .6)
    zz = z
    mx, my = 960 + 4 * zz, 540 + (cy - R + dep - (lerp(420, 540, 1 - (z - 1) / 8) * 0 + 0)) * 0
    # compute screen position of the mark
    fpp = lerp(cy - R, cy - 60, 1 - (z - 1) / 8)
    sy = lerp(420, 540, 1 - (z - 1) / 8) + (cy - R + dep - fpp) * z
    sx = 960 + 4 * z
    if k1 > 0:
        label_line(c, sx, sy, sx + 260, sy - 110 if sy > 300 else sy + 110, "GALILEO'S DEEPEST POINT", hexc('#FF8A7A'), k=k1, size=30, sub='≈ 150 km below the cloud tops')
    k2 = prog(t, T_INTERIOR + 1.0, T_INTERIOR + 1.6)
    if k2 > 0:
        draw_text(c, '≈ 0.2% OF THE WAY TO THE CENTER', 960, 1000 - 70, font(40, 'black'), hexc('#FFF1D6'), 'center', alpha=e_out(k2), shadow=1)
        draw_text(c, 'JUPITER RADIUS ≈ 70,000 km', 960, 1000 - 20 - 160 + 160 - 0 - 0 - 0 + 0, font(1, 'bold'), hexc('#FFF1D6'), 'center', alpha=0)
        draw_text(c, 'RADIUS ≈ 70,000 km', cx - R * .5 - 10, cy - 18, mono(22, 'semi'), hexc('#FFF1D6'), 'center', alpha=e_out(k2))
        c.drawLine(cx - R, cy, cx - 6, cy, P(hexc('#FFF1D6', .6 * e_out(k2)), stroke=2))
    k3 = prog(t, T_KEPTF - .2, T_KEPTF + .8)
    if k3 > 0:
        dashed(c, [(cx + 4, cy - R + dep + 10), (cx + 4, cy - 30)], hexc('#6FD3FF'), 5, phase=-t * 60, k=e_io(k3))
        if k3 > .6:
            draw_text(c, '?', cx + 40, cy - 40, font(120, 'black'), hexc('#6FD3FF'), 'left', alpha=e_out(prog(t, T_KEPTF + .4, T_KEPTF + .8)), glow=.5)

# ------------------------------------------------------------------ S07 three questions
def _panel_solid(c, x, y, w, h, t, a):
    c.save(); c.clipRect(skia.Rect(x, y, x + w, y + h))
    c.drawRect(skia.Rect(x, y, x + w, y + h), P(shader=lin((x, y), (x, y + h), [hexc('#2a1e2e', a), hexc('#6b3a24', a)])))
    pa = path_from([(x, y + h * .72), (x + w * .2, y + h * .64), (x + w * .38, y + h * .7), (x + w * .6, y + h * .6), (x + w * .8, y + h * .69), (x + w, y + h * .62), (x + w, y + h), (x, y + h)], True)
    c.drawPath(pa, P(hexc('#4a3428', a)))
    for i in range(7):
        c.drawCircle(x + w * (.1 + i * .13), y + h * (.8 + .06 * math.sin(i * 2)), 10 + 6 * (i % 3), P(hexc('#3a271e', a)))
    c.restore()

def _panel_ocean(c, x, y, w, h, t, a):
    c.save(); c.clipRect(skia.Rect(x, y, x + w, y + h))
    c.drawRect(skia.Rect(x, y, x + w, y + h), P(shader=lin((x, y), (x, y + h), [hexc('#1b2a50', a), hexc('#0c3a5a', a)])))
    for j in range(4):
        pa = skia.Path(); yy = y + h * (.62 + j * .09)
        pa.moveTo(x, yy)
        for i in range(0, int(w) + 20, 20):
            pa.lineTo(x + i, yy + 8 * math.sin(i * .03 + t * 2.4 + j))
        pa.lineTo(x + w, y + h); pa.lineTo(x, y + h); pa.close()
        c.drawPath(pa, P(hexc(['#2f6fa3', '#28608f', '#1f4f7a', '#173f63'][j], a)))
    c.restore()

def _panel_center(c, x, y, w, h, t, a):
    c.save(); c.clipRect(skia.Rect(x, y, x + w, y + h))
    c.drawRect(skia.Rect(x, y, x + w, y + h), P(hexc('#0b0612', a)))
    cx, cy = x + w / 2, y + h * .58
    for i in range(5):
        c.drawCircle(cx, cy, 160 - i * 30, P(hexc(['#3a1a12', '#5a2a18', '#7a3b1f', '#a8582a', '#e8a860'][i], a)))
    glow(c, cx, cy, 90, hexc('#ffd28a'), a * (.6 + .2 * math.sin(t * 3)))
    c.restore()

def s07(c, t):
    bg(c, '#0b1230', '#05070f')
    particles(c, t, .4, n=60, vy=-30, color='#9FB6FF', size=(1, 2.5))
    items = [(T_SOLID, 'SOMETHING SOLID?', _panel_solid), (T_OCEAN, 'AN OCEAN?', _panel_ocean), (T_CENTER, 'THE CENTER?', _panel_center)]
    w, h, gap = 500, 560, 60
    x0 = (W - (3 * w + 2 * gap)) / 2
    push = e_io(prog(t, T_LARGEST - .4, T_FINDOUT + .1))
    c.save()
    if push > 0:
        cx3 = x0 + 2 * (w + gap) + w / 2
        z = lerp(1, 1.35, push)
        c.translate(lerp(960, 960, push), 540); c.scale(z, z); c.translate(-lerp(960, cx3, push), -540)
    for i, (tt, label, fn) in enumerate(items):
        k = prog(t, tt + .1, tt + .55)
        if k <= 0:
            continue
        a = e_out(k)
        x = x0 + i * (w + gap); y = 190 + (1 - a) * 60
        dim = 1 - .55 * (i < 2) * push
        card(c, x - 8, y - 8, w + 16, h + 16, a * dim, color='#0b1330', border='#3D5A9E')
        fn(c, x, y, w, h * .78, t, a * dim)
        draw_text(c, label, x + w / 2, y + h * .78 + 78, font(40, 'black'), hexc('#FFF1D6'), 'center', alpha=a * dim)
        # falling capsule silhouette into each panel
        fy = y + 40 + ((t - tt) * 60) % (h * .4)
        draw_capsule(c, x + w / 2, fy, .18, 0, a * dim * .9, t, lamp=False)
        draw_text(c, '?', x + w - 50, y + 80, font(80, 'black'), hexc('#6FD3FF'), 'center', alpha=a * dim, glow=.4)
    c.restore()

# ------------------------------------------------------------------ S08 route: real vs imagined
def s08(c, t):
    bg(c, '#0b1230', '#05070f')
    # vertical depth column
    x = 760
    top, bot = 170, 980
    col_w = 180
    c.drawRect(skia.Rect(x - col_w / 2, top, x + col_w / 2, bot), P(shader=lin((0, top), (0, bot), [hexc('#E3B47A'), hexc('#8a3b1f'), hexc('#2d2a7a'), hexc('#1a1030')], [0, .3, .65, 1])))
    c.drawRect(skia.Rect(x - col_w / 2, top, x + col_w / 2, bot), P(hexc('#FFF1D6', .4), stroke=2))
    draw_text(c, 'CLOUD TOPS', x - col_w / 2 - 20, top + 8, mono(20, 'semi'), hexc('#FFF1D6'), 'right')
    draw_text(c, 'CENTER', x - col_w / 2 - 20, bot, mono(20, 'semi'), hexc('#FFF1D6'), 'right')
    draw_text(c, 'NOT TO SCALE', x - col_w / 2 - 20, top + 40, mono(16, 'medium'), hexc(HUDC), 'right', alpha=.7)
    k1 = e_io(prog(t, T_REAL, T_REAL + 1.6))
    real_end = top + 60
    if k1 > 0:
        c.drawLine(x, top, x, lerp(top, real_end, k1), P(hexc('#FFB347'), stroke=10, cap='round'))
        draw_galileo_descent(c, x, lerp(top, real_end, k1) - 5, .25, chute=1, t=t)
        label_line(c, x + 20, real_end, x + 220, real_end - 40, 'REAL SPACECRAFT', hexc('#FFB347'), k=prog(t, T_REAL + .8, T_REAL + 1.6), size=32, sub='GALILEO PROBE · 1995 · MEASURED DATA')
    k2 = e_io(prog(t, T_NOSPACE, T_NOSPACE + 2.4))
    if k2 > 0:
        dashed(c, [(x, real_end + 14), (x, bot - 20)], hexc('#6FD3FF'), 8, on=20, off=14, phase=-t * 50, k=k2)
        yy = lerp(real_end + 14, bot - 60, k2)
        draw_capsule(c, x, yy, .2, 0, 1, t)
        label_line(c, x + 20, (real_end + bot) / 2 + 80, x + 220, (real_end + bot) / 2 + 40, 'WHERE NO SPACECRAFT HAS GONE', hexc('#6FD3FF'), k=prog(t, T_NOSPACE + 1.0, T_NOSPACE + 1.8), size=32, sub='FICTIONAL JOURNEY · GUIDED BY SCIENTIFIC MODELS')

# ------------------------------------------------------------------ S09 Earth vs Jupiter falling
def s09(c, t):
    lt = t - T_BUTFIRST
    # left half: Earth sky + ground
    c.save(); c.clipRect(skia.Rect(0, 0, W / 2 - 3, H))
    bg(c, '#5fa3e8', '#cfe6ff')
    c.drawRect(skia.Rect(0, 760, W / 2, H), P(shader=lin((0, 760), (0, H), [hexc('#5f9a45'), hexc('#3c6b2c')])))
    c.drawLine(0, 760, W / 2, 760, P(hexc('#ffffff', .6), stroke=2))
    p = e_in(prog(t, T_BUTFIRST + .3, T_EARTHFALL + .5))
    yy = lerp(150, 700, p)
    draw_capsule(c, 480, yy, .38, 0, 1, t, lamp=False, ambient='#9fd0ff')
    if p >= 1:
        k = prog(t, T_EARTHFALL + .5, T_EARTHFALL + 1.3)
        for i in range(10):
            ang = math.pi + i / 9 * math.pi
            c.drawCircle(480 + math.cos(ang) * 120 * e_out(k), 760 + math.sin(ang) * 40 * e_out(k), 16 * (1 - k), P(hexc('#d8c8a8', .7 * (1 - k))))
        draw_text(c, 'LANDED', 480, 870, font(46, 'black'), hexc('#FFFFFF'), 'center', alpha=e_out(prog(t, T_EARTHFALL + .5, T_EARTHFALL + .9)), shadow=1)
    draw_text(c, 'EARTH', 480, 120, font(44, 'black'), hexc('#0b1230'), 'center')
    c.restore()
    # right half: Jupiter endless clouds
    c.save(); c.clipRect(skia.Rect(W / 2 + 3, 0, W, H)); c.translate(W / 2, 0)
    c.save(); c.scale(.5, 1)
    cloud_world(c, t, fall=lerp(60, 260, prog(t, T_BUTFIRST, T_EARTHFALL + 1)), tint=(1, .74, .5), bg_top='#E3B47A', bg_bot='#3a1a10', depth_dark=.5)
    c.restore()
    draw_capsule(c, 480, 470 + math.sin(t * 1.5) * 10, .38, 0, 1, t, lamp=False)
    dashed(c, [(60, 760), (900, 760)], hexc('#FFF1D6'), 3, alpha=.5 * (.6 + .4 * math.sin(t * 4)))
    draw_text(c, 'GROUND?', 480, 805, mono(30, 'bold'), hexc('#FFF1D6'), 'center', alpha=.8)
    draw_x(c, 480, 870, 46, prog(t, T_DIFFERENT, T_DIFFERENT + .5))
    draw_text(c, 'JUPITER', 480, 120, font(44, 'black'), hexc('#FFF1D6'), 'center', shadow=1)
    c.restore()
    c.drawRect(skia.Rect(W / 2 - 3, 0, W / 2 + 3, H), P(hexc('#070B1A')))

# ------------------------------------------------------------------ S10 nowhere to land / peaceful
def s10(c, t):
    lt = t - T_NOWHERE
    z = tw(t, T_PEACEFUL, T_REDOVAL, 1.0, 1.12, e_sine)
    space(c, t, zoom=z * .9 + .1)
    R = 400 * z
    a_pl = e_out(prog(t, T_NOWHERE + .8, T_PEACEFUL + .6))
    draw_jupiter(c, 960, 560, R, rot=2.6 + t * .03, alpha=a_pl)
    # wrap-around band tracers
    k = prog(t, T_WRAP - .6, T_WRAP + 1.2)
    if k > 0 and k < 1:
        for lat in (12, -14, 30, -32):
            yy = 560 - R * math.sin(math.radians(lat))
            rx = R * math.cos(math.radians(lat))
            arc = skia.Path(); arc.addArc(skia.Rect(960 - rx, yy - rx * .08, 960 + rx, yy + rx * .08), 180, -180 * e_io(k))
            c.drawPath(arc, P(hexc('#FFF1D6', .8 * math.sin(math.pi * k)), stroke=3))
    # title text
    a = fade_window(t, T_NOWHERE - .05, T_PEACEFUL + .2, .3, .5)
    draw_text(c, "THERE'S NOWHERE TO LAND.", 960, 560, font(96, 'black'), hexc('#FFF1D6'), 'center', alpha=a, glow=.3, shadow=1)
    chapter_card(c, 1, 'NOWHERE TO LAND', t, T_PEACEFUL + .4, T_STRIPES + 1.6)

# ------------------------------------------------------------------ S11 Great Red Spot zoom
def s11(c, t):
    lt = t - T_REDOVAL
    zk = e_io(prog(t, T_REDOVAL, T_CENTURIES))
    R = lerp(450, 1900, zk)
    lat = math.radians(-22)
    cy0 = 560
    gy = math.sin(-lat)  # ny of GRS
    cx = 960
    cy = lerp(cy0, 540 - gy * R, zk)
    pull = e_io(prog(t, T_NOTGROUND, T_CLOUDS + .3))
    R = lerp(R, 1450, pull)
    cy = lerp(cy, 540 - gy * R + 120, pull)
    space(c, t, zoom=1 + zk * .3)
    draw_jupiter(c, cx, cy, R, rot=math.pi + .35 - .35 * zk + t * .004)
    gx_s, gy_s = cx + R * math.sin(.35 * (1 - zk) - t * .004) * 0, cy + gy * R
    k = prog(t, T_GRS, T_GRS + .6)
    if k > 0:
        ga = 1 - pull
        rx, ry = R * .118, R * .082
        c.drawOval(skia.Rect(960 - rx * 1.3, gy_s - ry * 1.3, 960 + rx * 1.3, gy_s + ry * 1.3), P(hexc('#FFF1D6', .8 * e_out(k) * ga), stroke=3))
        label_line(c, 960 + rx * 1.2, gy_s - ry * 1.0, 1450, 260, 'GREAT RED SPOT', hexc('#FFF1D6'), alpha=ga, k=k, size=40, sub='A GIANT STORM · WIDER THAN EARTH')
        k2 = prog(t, T_CENTURIES - .3, T_CENTURIES + .3)
        if k2 > 0:
            er = 6371 / 71492 * R
            ex, ey = 420, gy_s
            draw_earth(c, ex, ey, er * e_back(min(1, k2), 1.3) if k2 < 1 else er, rot=1.0, alpha=ga, max_grid=500)
            draw_text(c, 'EARTH · TO SCALE', ex, ey + er + 40, mono(22, 'semi'), hexc('#FFF1D6'), 'center', alpha=ga * e_out(k2))
            draw_text(c, 'OBSERVED FOR CENTURIES', 1450 + 14, 260 + 100, mono(24, 'semi'), hexc('#E3B47A'), 'left', alpha=ga * e_out(k2))
    k3 = prog(t, T_NOTGROUND + .3, T_NOTGROUND + .9)
    if k3 > 0:
        for i, lat_ in enumerate((8, -9, -20)):
            yy = cy - R * math.sin(math.radians(lat_))
            c.drawLine(200, yy, 1720, yy, P(hexc('#FFF1D6', .6 * e_out(k3)), stroke=2))
        hud_panel(c, 1240, 160, 520, 100, None, e_out(k3))
        draw_text(c, 'STRIPES ≠ GROUND', 1500, 228, font(46, 'black'), hexc('#FFF1D6'), 'center', alpha=e_out(k3))

# ------------------------------------------------------------------ S12 clouds moving / winds
def s12(c, t):
    lt = t - T_CLOUDS
    strip = tex_strip_img(34, -34)
    sw, sh = strip.width(), strip.height()
    scale = H / sh * 1.25
    nb = 14
    for i in range(nb):
        y0 = sh * i / nb; y1 = sh * (i + 1) / nb
        lat = 34 - 68 * (i + .5) / nb
        v = 60 * math.sin(math.radians(lat) * 7.5) * (1.0 + .5 * (abs(lat) < 8)) + 25
        off = (t * v * 1.2) % sw
        dy = (y0 * scale) - (sh * scale - H) / 2
        for k in (-1, 0, 1):
            src = skia.Rect(0, y0, sw, y1)
            dst = skia.Rect(-off * scale + k * sw * scale, dy, -off * scale + (k + 1) * sw * scale, dy + (y1 - y0) * scale + 1)
            c.drawImageRect(strip, src, dst, LIN, P())
    letter_dim(c, .15)
    k = prog(t, T_MOVING, T_MOVING + .8)
    for i in range(6):
        lat = 34 - 68 * (i * 2 + 1.5) / nb
        v = math.sin(math.radians(lat) * 7.5)
        y = (H / 2) - lat / 34 * H * .62
        if 120 < y < 900:
            d = 1 if v > 0 else -1
            xs = 960 - d * 260
            arrow(c, xs, y, xs + d * 520 * e_out(k), y, hexc('#FFF1D6'), 6, 26, .85 * k)
    k2 = prog(t, T_WINDRACE, T_WINDRACE + .6)
    if k2 > 0:
        hud_readout(c, 1290, 140, 480, 'JET STREAM SPEED', 'HUNDREDS', 'km/h', e_out(k2), sub='ALTERNATING EAST ↔ WEST', size=46)
    draw_tag(c, 'CLOUD-TOP VIEW · ILLUSTRATIVE', 40, 36, 'concept', alpha=1)

# ------------------------------------------------------------------ S13 1,300 Earths
def s13(c, t):
    lt = t - T_ENORMOUS
    space(c, t)
    R = 380; cx, cy = 820, 560
    draw_jupiter(c, cx, cy, R, rot=2.9 + t * .02)
    er = 6371 / 71492 * R
    k0 = e_out(prog(t, T_ENORMOUS + .2, T_ENORMOUS + .8))
    draw_earth(c, 1420, 300, er * 1.0, rot=1.0, alpha=k0, max_grid=300)
    draw_text(c, 'EARTH · TO SCALE', 1420, 300 + er + 38, mono(20, 'semi'), hexc('#FFF1D6'), 'center', alpha=k0)
    k = prog(t, T_1300 - .4, T_YET - .2)
    if k > 0:
        # fill disc with earth icons (2D illustration of a volume comparison)
        n_show = int(e_io(k) * 600)
        rng = np.random.default_rng(2)
        r_ic = 9.5
        pts = []
        row = 0
        yy = cy - R + r_ic
        while yy < cy + R:
            half = math.sqrt(max(0, R * R - (yy - cy) ** 2)) - r_ic
            xx = cx - half + (row % 2) * r_ic
            while xx <= cx + half:
                pts.append((xx, yy)); xx += r_ic * 2.05
            yy += r_ic * 1.78; row += 1
        pts.sort(key=lambda p: -p[1])
        c.save(); c.clipPath(skia.Path().addCircle(cx, cy, R), doAntiAlias=True)
        for i, (px, py) in enumerate(pts[:n_show * len(pts) // 600]):
            draw_earth_icon(c, px, py, r_ic * .92, .95)
        c.restore()
        num = int(1300 * e_io(prog(t, T_1300 - .3, T_1300 + 1.4)))
        hud_panel(c, 1240, 560, 540, 210, None, e_out(prog(t, T_1300 - .4, T_1300)))
        draw_text(c, f'{num:,}+', 1510, 680, font(110, 'black'), hexc('#FFF1D6'), 'center', alpha=e_out(prog(t, T_1300 - .4, T_1300)), glow=.3)
        draw_text(c, 'EARTHS COULD FIT INSIDE (BY VOLUME)', 1510, 735, mono(19, 'semi'), hexc(HUDC), 'center', alpha=e_out(prog(t, T_1300 - .4, T_1300)))
    draw_tag(c, 'ILLUSTRATION · VOLUME SHOWN IN 2D', 40, 36, 'concept')

# ------------------------------------------------------------------ S14 rotation < 10 h, jet streams
def s14(c, t):
    lt = t - T_YET
    space(c, t)
    R = 380; cx, cy = 960, 560
    spin = lerp(.02, .9, e_io(prog(t, T_YET + .3, T_TENH))) if t < T_JET else lerp(.9, .15, e_io(prog(t, T_JET - .5, T_JET + .8)))
    # integrate spin roughly: use quadratic approx
    ang = 2.0 + (t - T_YET) * spin
    draw_jupiter(c, cx, cy, R, rot=ang)
    k = prog(t, T_YET + .3, T_TENH + 1.2)
    rect = skia.Rect(cx - R - 40, cy - R - 40, cx + R + 40, cy + R + 40)
    c.drawArc(rect, -90, 360 * e_io(k), False, P(hexc('#FFB347', .9), stroke=6, cap='round'))
    c.drawArc(rect, -90, 360, False, P(hexc('#FFB347', .2), stroke=6))
    hrs = 9 + 56 / 60
    hh = hrs * e_io(k)
    kk = prog(t, T_TENH - .2, T_TENH + .3)
    hud_panel(c, 1390, 220, 420, 200, 'ONE JUPITER DAY', e_out(kk))
    draw_text(c, f'{int(hh)} h {int((hh % 1) * 60):02d} min', 1410, 330, mono(52, 'bold'), hexc('#FFFFFF'), alpha=e_out(kk))
    draw_text(c, 'EARTH DAY: 24 h', 1410, 385, mono(22, 'semi'), hexc(HUDC), alpha=e_out(kk))
    k2 = prog(t, T_JET, T_JET + 1.0)
    if k2 > 0:
        c.save(); c.clipPath(skia.Path().addCircle(cx, cy, R), doAntiAlias=True)
        for i, lat in enumerate((26, 18, 7, -2, -12, -20, -30, -40)):
            yy = cy - R * math.sin(math.radians(lat))
            rx = R * math.cos(math.radians(lat)) * .8
            d = 1 if i % 2 == 0 else -1
            ph = (t * .6 * d) % 1.0
            x0 = cx - rx + ph * rx * .5
            arrow(c, cx - d * rx * .6, yy, cx + d * rx * .6, yy, hexc('#FFF1D6'), 4, 18, .8 * e_out(k2), k=e_out(k2))
        c.restore()
        label_line(c, cx + R * .7, cy - R * .5, 1500, 620, 'JET STREAMS', hexc('#FFF1D6'), k=k2, size=36, sub='SHAPE THE STRIPES')

# ------------------------------------------------------------------ S15 Juno: winds extend ~3,000 km deep
def s15(c, t):
    lt = t - T_UNSETTLE
    dark = e_io(prog(t, T_UNSETTLE, T_UNSETTLE + 2.0))
    split = e_io(prog(t, T_EXTEND - .6, T_3000))
    space(c, t, alpha=1)
    # slab view: zoomed section of the planet edge
    Rb = lerp(500, 2600, split)
    cx, cy = 960, lerp(560, 440 + 2600, split)
    if split < .999:
        draw_jupiter(c, cx, cy, Rb, rot=2.2 + t * .02, alpha=1)
    if split > 0:
        c.save()
        c.drawCircle(cx, cy, Rb, P(shader=rad(cx, cy, Rb, [hexc('#3a1408', split), hexc('#6b2a14', split), hexc('#b8693a', split), hexc('#E3B47A', split)], [0, .9, .985, 1])))
        # wind layer band ~3000 km thick
        th = 3000 / 69911 * Rb
        band = skia.Path(); band.addCircle(cx, cy, Rb); band.addCircle(cx, cy, Rb - th); band.setFillType(skia.PathFillType.kEvenOdd)
        c.drawPath(band, P(hexc('#FFB347', .28 * split)))
        # flowing arrows within band
        c.save(); c.clipPath(band, doAntiAlias=True)
        for j in range(3):
            rr = Rb - th * (.2 + .3 * j)
            for i in range(9):
                ang = -90 + (i - 4) * 9 + ((t * (4 - j) * (1 if j % 2 == 0 else -1)) % 9)
                a = math.radians(ang)
                x = cx + math.cos(a) * rr; y = cy + math.sin(a) * rr
                d = 1 if j % 2 == 0 else -1
                a2 = a + d * .02
                arrow(c, x, y, cx + math.cos(a2) * rr, cy + math.sin(a2) * rr, hexc('#FFF1D6'), 4, 16, .8 * split)
        c.restore()
        c.restore()
        kb = prog(t, T_3000 - .2, T_3000 + .5)
        if kb > 0:
            xb = 1500
            ytop = cy - math.sqrt(max(0, Rb ** 2 - (xb - cx) ** 2))
            ybot = cy - math.sqrt(max(0, (Rb - th) ** 2 - (xb - cx) ** 2))
            c.drawLine(xb + 30, ytop, xb + 30, lerp(ytop, ybot, e_out(kb)), P(hexc('#FFFFFF'), stroke=4))
            c.drawLine(xb + 18, ytop, xb + 42, ytop, P(hexc('#FFFFFF'), stroke=4))
            if kb >= 1:
                c.drawLine(xb + 18, ybot, xb + 42, ybot, P(hexc('#FFFFFF'), stroke=4))
            draw_text(c, '≈ 3,000 km', xb + 60, (ytop + ybot) / 2 + 14, mono(40, 'bold'), hexc('#FFFFFF'), alpha=e_out(kb), shadow=1)
            draw_text(c, 'VISIBLE CLOUD TOPS', 330, cy - Rb - 24 + (Rb - math.sqrt(max(0, Rb ** 2 - (330 - cx) ** 2))) , mono(22, 'semi'), hexc('#FFF1D6'), alpha=e_out(kb))
    letter_dim(c, .3 * dark * (1 - split))
    # Juno flyby
    kj = prog(t, T_JUNO - .4, T_EXTEND + 1.5)
    if 0 < kj < 1:
        jx = lerp(-300, 2200, e_sine(kj)); jy = lerp(300, 200, kj)
        draw_juno(c, jx, jy, .75, 15 + kj * 40, t=t)
        if kj > .15:
            draw_tag(c, 'NASA JUNO · AT JUPITER SINCE 2016', 960, 860 - 30, 'concept', align='center', alpha=fade_window(kj, .15, .95, .1, .1))
    if split > .5:
        draw_tag(c, 'CUTAWAY · JUNO GRAVITY RESULTS (2018)', 40, 36, 'model', alpha=e_out(prog(split, .5, 1)))

# ------------------------------------------------------------------ S16 3000 km, storm system, about to fall in
def s16(c, t):
    lt = t - T_3000B
    plunge = e_in(prog(t, T_ABOUT, T_OBSTACLE))
    Rb = 2600
    cx, cy = 960, 440 + 2600
    c.save()
    z = lerp(1, 4.5, plunge)
    c.translate(960, 600); c.scale(z, z); c.translate(-960, -600 + plunge * 40)
    space(c, t)
    c.drawCircle(cx, cy, Rb, P(shader=rad(cx, cy, Rb, [hexc('#3a1408'), hexc('#6b2a14'), hexc('#b8693a'), hexc('#E3B47A')], [0, .9, .985, 1])))
    th = 3000 / 69911 * Rb
    band = skia.Path(); band.addCircle(cx, cy, Rb); band.addCircle(cx, cy, Rb - th); band.setFillType(skia.PathFillType.kEvenOdd)
    c.drawPath(band, P(hexc('#FFB347', .28)))
    # storm column
    ks = e_io(prog(t, T_STORMSYS, T_STORMSYS + 2.0))
    if ks > 0:
        sx = 960
        top = 440
        for i in range(10):
            y = top + i * th / 9 * ks
            rw = 70 - i * 3
            c.drawOval(skia.Rect(sx - rw, y - 8, sx + rw, y + 8), P(hexc('#FFF1D6', .55 * ks), stroke=3))
            ph = t * 4 + i * .6
            c.drawCircle(sx + math.cos(ph) * rw, y + math.sin(ph) * 8, 5, P(hexc('#FFFFFF', .9 * ks)))
        glow(c, sx, top + th * .5 * ks, 120, hexc('#FFB347'), .4 * ks)
    c.restore()
    k = prog(t, T_3000B, T_3000B + .45)
    big_number(c, '3,000 km', 960, 260, 150, hexc('#FFF1D6'), t, T_3000B, alpha=1 - plunge, glow_=.35)
    draw_text(c, 'DEEP', 960, 330, mono(28, 'semi'), hexc('#E3B47A'), 'center', alpha=e_out(k) * (1 - plunge), spacing=8)
    flash(c, e_in(prog(t, T_OBSTACLE - .25, T_OBSTACLE)) * .9, '#FFF1D6')

# ------------------------------------------------------------------ S17 speed 170,000 km/h
def s17(c, t):
    lt = t - T_OBSTACLE
    # star streaks
    space(c, t, ox=-lt * 120, star_alpha=.6)
    sp = e_in(prog(t, T_SPEED, T_170 + 1.5))
    speed_lines(c, t, .2 + .6 * sp, direction=(-.86, -.5), n=80, speed=1500 + 5000 * sp, length=120 + 400 * sp, color='#cfe0ff', width=2)
    draw_jupiter(c, 1750 + lt * 3, 1300, 1150 + lt * 12, rot=2.0 + t * .01)
    px = 760 + math.sin(t * 7) * 2 * sp; py = 520 + math.cos(t * 9) * 2 * sp
    draw_galileo_entry(c, px, py, .9, 30, heat=0)
    kv = prog(t, T_170 - .2, T_170 + 2.2)
    v = int(170000 * e_out(kv)) // 100 * 100
    hud_readout(c, 1260, 150, 560, 'APPROACH SPEED', f'{v:,}', 'km/h', e_out(prog(t, T_SPEED, T_SPEED + .5)), sub='≈ 47 km EVERY SECOND' if kv > .9 else ' ', size=64)
    ks = prog(t, T_SIMILAR, T_SIMILAR + .5)
    if ks > 0:
        draw_tag(c, 'SAME AS GALILEO ENTRY SPEED · 1995', 1260, 360, 'hist', alpha=e_out(ks))
    draw_tag(c, 'ILLUSTRATION · YOUR APPROACH', 40, 36, 'concept')

SHOTS1 = [
    (0.0, s01, ('cut', 0)),
    (T_DROPPED, s02, ('fade', .35)),
    (T_WINDS, s03, ('flash', .25)),
    (T_KEPT, s04, ('fade', .4)),
    (T_THEN58, s05, ('fade', .4)),
    (T_BUTHERE, s06, ('black', .5)),
    (T_SOLID - .2, s07, ('fade', .4)),
    (T_FINDOUT, s08, ('fade', .45)),
    (T_BUTFIRST, s09, ('whip', .35)),
    (T_NOWHERE, s10, ('black', .3)),
    (T_REDOVAL, s11, ('fade', .5)),
    (T_CLOUDS, s12, ('fade', .5)),
    (T_ENORMOUS, s13, ('whip', .35)),
    (T_YET, s14, ('fade', .4)),
    (T_UNSETTLE, s15, ('fade', .5)),
    (T_3000B, s16, ('cut', 0)),
    (T_OBSTACLE, s17, ('flash', .3)),
]
```

## A.11 `engine/example_jupiter/scenes2.py` — Jupiter shots 18–35 (585 lines)

```python
# Shots 18-35 : entry, deceleration, fictional capsule, clouds without horizon, instruments, Galileo's last signal.
from common import *
from scenes1 import HIST_TAG, T_HIT
A = at
T_CHANGES = A('And suddenly everything')
T_COMPRESSED = A('is compressed and')
T_SHIELD = A('Your heat shield')
T_DARKNESS = A('Outside the darkness')
T_DECEL = A('Then the deceleration hits')
T_GREAL = A("During Galileo's real")
T_228 = A('two hundred twenty eight times')
T_228B = A('two hundred and twenty eight')
T_HUMAN = A("A human couldn't")
T_ORDINARY = A('Not in an ordinary')
T_SUIT = A('Not with a normal')
T_HOLD = A('simply holding on')
T_ROBOT = A('But Galileo was')
T_WORST = A('It survived the worst')
T_CHUTE = A('deployed its parachute')
T_TRANSMIT = A('began transmitting')
T_FICT = A('Now imagine you have')
T_SHAKESTOP = A('The shaking stops')
T_GLOWFADE = A('The glow fades')
T_FIRST = A('And for the first time')
T_SURROUND = A("You're surrounded")
T_ABOVE = A('Above you')
T_BESIDE = A('Beside you')
T_BELOW = A('Below you')
T_MORE = A('More clouds')
T_MISSING = A('And something is missing')
T_HORIZON = A('A horizon')
T_ONEARTH = A('On earth you can')
T_GROUND = A('the ground begins')
T_INSIDE = A('But inside Jupiter there')
T_INSTR = A('You check your instruments')
T_1BAR = A('approximately one bar')
T_SEALEVEL = A("close to the atmospheric")
T_SAFE = A('sounds almost safe')
T_UNTIL = A('Until you see')
T_M108 = A('Minus one hundred eight')
T_ATMOS = A('And the atmosphere')
T_HYD = A('Mostly hydrogen')
T_NOO2 = A("There's no breathable")
T_FATAL = A('stepping outside would be fatal')
T_STRANGE = A('But something strange')
T_RISING = A('The temperature starts rising')
T_WARMER = A('becoming warmer')
T_WARMDAY = A('warm day on Earth')
T_IMPROVE = A('Sounds like an improvement')
T_CATCH = A("Except there's a catch")
T_PINC = A('The pressure is increasing')
T_DOESNT = A("pressure doesn't care")
T_DENSER = A('becomes denser')
T_FIVE = A('five bars')
T_TEN = A('ten bars')
T_FIFTEEN = A('fifteen')
T_LOOKOUT = A('Now imagine looking')
T_EXPECT = A('You might expect')
T_SURELY = A('Because surely')
T_DOESNTEND = A("But it doesn't end")
T_BEFORE = A('And before we reach')
T_GDISC = A('Galileo discovers')
T_MEASURE = A('its instruments measure')
T_SURPRISING = A('particularly surprising')
T_LESSWATER = A("There's less water")
T_MATTERS = A('That matters because')
T_FORMED = A('how Jupiter formed')
T_MISUNDER = A('So did scientists')
T_DRY = A('Galileo had entered')
T_LIKE = A('It was like trying')
T_DESERT = A('into one desert')
T_ONELOC = A('One location')
T_KEPTF2 = A('But Galileo kept falling')
T_CLIMBED = A('The temperature climbed')
T_20X = A('The pressure passed twenty')
T_CONT = A('And the probe continued')
T_LOST = A('the signal was lost', end=True) - .15
T_LASTED = A('Its scientific data')
T_FAILED = A('Its transmitter failed')
T_DESTROY = A('ultimately destroyed')
T_EXTRA = A("And here's what makes that")
T_LASTDEPTH = A('At the last measured')
T_FRACTION = A('tiny fraction')
T_HUMANITY = A('Humanity had sent')
T_BARELY = A('barely begun exploring')
T_CONTINUE = A("So let's continue")

FICT_TAG = 'FICTIONAL CAPSULE · NOT REAL TECHNOLOGY'

def explorer_look_default(t):
    """Blinks every few seconds."""
    ph = t % 3.7
    return clamp(1 - abs(ph - 0.08) / 0.08) if ph < 0.16 else 0.0

# ------------------------------------------------------------------ S18 atmospheric entry, compression
def s18(c, t):
    lt = t - T_HIT
    k = prog(t, T_HIT, T_DARKNESS)
    bg(c, '#140a14', '#7a3418', '#3a1810')
    speed_lines(c, t, .35 + .3 * k, direction=(.5, .86), n=70, speed=3000, length=200, color='#ffcf9a', width=2)
    heat = lerp(.15, .75, e_in(k))
    sx, sy = shake(t, T_HIT, 2.0, 10)
    x, y = 860 + sx + math.sin(t * 13) * 3 * k, 520 + sy
    # bow shock arcs ahead of the nose (nose points down-right at 55deg)
    ang = 55
    a = math.radians(ang)
    nx, ny = x + math.cos(a) * 120, y + math.sin(a) * 120
    kc = prog(t, T_COMPRESSED - .5, T_COMPRESSED + .8)
    for i in range(4):
        rr = 150 + i * 36
        c.save(); c.translate(nx, ny); c.rotate(ang)
        c.drawArc(skia.Rect(-rr * .5, -rr, rr * .5 + 20, rr), -80, 160, False, P(hexc('#ffd8a8', (.55 - i * .12) * (0.4 + .6 * kc)), stroke=4 - i * .6))
        c.restore()
    if kc > 0:
        for i in range(-3, 4):
            # gas parcels converging on the nose
            ph = (t * 1.6 + i * .17) % 1.0
            d = lerp(520, 170, ph)
            aa = a + i * .16
            px, py = nx + math.cos(aa) * d, ny + math.sin(aa) * d
            arrow(c, px, py, px - math.cos(aa) * 70, py - math.sin(aa) * 70, hexc('#FFF1D6'), 4, 16, kc * (1 - ph) * .9)
        label_line(c, nx + 170, ny + 120, 1420, 760, 'GAS COMPRESSED & HEATED', hexc('#FFF1D6'), k=kc, size=34, sub='A GLOWING SHOCK LAYER FORMS')
    draw_galileo_entry(c, x, y, 1.15, ang, heat=heat, t=t)
    ks = prog(t, T_SHIELD, T_SHIELD + .6)
    if ks > 0:
        label_line(c, x + 40, y + 60, 420, 820, 'HEAT SHIELD', hexc('#FFB347'), k=ks, size=34, sub='ABSORBING ENORMOUS ENERGY')
        hud_panel(c, 1300, 140, 470, 110, 'HEAT LOAD', e_out(ks))
        fill = e_in(prog(t, T_SHIELD, T_DARKNESS + 2))
        rrect(c, 1320, 190, 430 * fill, 34, 8, P(mixc('#FFB347', '#FF3B30', fill)))
    draw_tag(c, 'ILLUSTRATION BASED ON GALILEO ENTRY · 1995', 40, 36, 'hist')

# ------------------------------------------------------------------ S19 brilliant glow (visual peak)
def s19(c, t):
    k = e_in(prog(t, T_DARKNESS, T_DECEL - .2))
    bg(c, '#3a1408', '#a8461c')
    c.drawPaint(P(shader=rad(960, 600, 1300, [mixc('#ffb070', '#fff4dc', k), mixc('#c4541c', '#ffb070', k), hexc('#3a1408')], [0, .45, 1])))
    speed_lines(c, t, .5 + .4 * k, direction=(.5, .86), n=110, speed=5200, length=320, color='#fff1d6', width=3)
    sx, sy = shake(t, T_DARKNESS, 6, 6 + 10 * k, freq=18)
    draw_galileo_entry(c, 960 + sx, 520 + sy, 1.35, 55, heat=1.0, t=t)
    glow(c, 1040, 650, 700 * (0.6 + k), hexc('#fff1d6'), .45 + .4 * k)
    draw_tag(c, 'ILLUSTRATION BASED ON GALILEO ENTRY · 1995', 40, 36, 'hist')

# ------------------------------------------------------------------ S20 228 g
def s20(c, t):
    lt = t - T_DECEL
    bg(c, '#1a0806', '#4a140a')
    k = 1 - e_out(prog(t, T_DECEL, T_DECEL + 3.5))
    speed_lines(c, t, .2 + .5 * k, direction=(.5, .86), n=60, speed=600 + 3000 * k, length=80 + 200 * k, color='#ffb080', width=2)
    sx, sy = shake(t, T_DECEL, 2.2, 38, freq=16)
    sx2, sy2 = shake(t, T_228B, 1.0, 14, freq=20, seed=3)
    c.save(); c.translate(sx + sx2, sy + sy2)
    draw_galileo_entry(c, 520, 560, .9, 55, heat=.7 * k + .2, t=t)
    g = 228 * e_out(prog(t, T_228 - 1.2, T_228 + 1.6))
    draw_gauge(c, 1300, 470, 230, g / 260, 'DECELERATION', f'{int(g)} g', warn_from=.35,
               tick_labels=['0', '', '', '', '', '130', '', '', '', '', '260'])
    c.restore()
    kb = prog(t, T_228B, T_228B + .4)
    if t > T_228 + 1.2:
        pulse = 1 + .12 * math.exp(-max(0, t - T_228B) * 5) * (t > T_228B)
        c.save(); c.translate(1300, 900 - 30); c.scale(pulse, pulse)
        draw_text(c, "× EARTH'S GRAVITY", 0, 0, font(40, 'black'), hexc('#FFF1D6'), 'center', alpha=e_out(prog(t, T_228 + 1.2, T_228 + 1.8)), shadow=1)
        c.restore()
    flash(c, (1 - e_out(prog(t, T_DECEL, T_DECEL + .5))) * .6, '#ff6040')
    flash(c, (1 - e_out(prog(t, T_228B, T_228B + .4))) * .25 * (t > T_228B), '#ff3b30')
    draw_tag(c, 'GALILEO PROBE · MEASURED PEAK ≈ 228 g', 40, 36, 'hist')

# ------------------------------------------------------------------ S21 a human couldn't survive
def _ico_craft(c, x, y, s, t, a):
    rrect(c, x - 60 * s, y - 80 * s, 120 * s, 160 * s, 40 * s, P(hexc('#a9b0bb', a)))
    c.drawCircle(x, y - 20 * s, 26 * s, P(hexc('#2b4a66', a)))
    c.drawRect(skia.Rect(x - 60 * s, y + 30 * s, x + 60 * s, y + 42 * s), P(hexc('#6FD3FF', a)))
def _ico_suit(c, x, y, s, t, a):
    draw_explorer_bust(c, x, y - 30 * s, 60 * s, alpha=a, brow=-1, mouth='grit', look=(0, 0))
def _ico_hold(c, x, y, s, t, a):
    c.drawRect(skia.Rect(x - 120 * s, y - 70 * s, x + 120 * s, y - 56 * s), P(hexc('#a9b0bb', a)))
    for side in (-1, 1):
        c.drawLine(x + side * 30 * s, y - 60 * s, x + side * 40 * s, y + 10 * s, P(hexc(SUIT, a), stroke=22 * s, cap='round'))
        c.drawCircle(x + side * 30 * s, y - 62 * s, 16 * s, P(hexc(SUIT, a)))
    c.drawCircle(x, y + 40 * s, 48 * s, P(hexc(SUIT, a)))
    c.drawCircle(x, y + 40 * s, 48 * s, P(hexc('#6a655a', a), stroke=3))

def s21(c, t):
    bg(c, '#14080a', '#05070f')
    draw_text(c, "A HUMAN COULDN'T SURVIVE 228 g", 960, 190, font(56, 'black'), hexc('#FFF1D6'), 'center', alpha=e_out(prog(t, T_HUMAN, T_HUMAN + .5)), shadow=1)
    items = [(T_ORDINARY, 'ORDINARY SPACECRAFT', _ico_craft), (T_SUIT, 'NORMAL SPACE SUIT', _ico_suit), (T_HOLD, 'HOLDING ON', _ico_hold)]
    for i, (tt, lab, fn) in enumerate(items):
        k = prog(t, tt, tt + .45)
        if k <= 0:
            continue
        x = 360 + i * 600; y = 560
        card(c, x - 230, y - 230, 460, 470, e_out(k))
        fn(c, x, y - 20, 1.0, t, e_out(k))
        draw_text(c, lab, x, y + 200, font(32, 'black'), hexc('#FFF1D6'), 'center', alpha=e_out(k))
        draw_x(c, x, y - 20, 220, prog(t, tt + .35, tt + .8), alpha=.92)

# ------------------------------------------------------------------ S22 Galileo robotic probe: chute, transmitting
def s22(c, t):
    lt = t - T_ROBOT
    cloud_world(c, t, fall=40, drift=-20, tint=(1, .8, .56), bg_top='#2a1830', bg_bot='#c27a44', bg_mid='#6b3a30')
    sep = e_in(prog(t, T_WORST + .6, T_CHUTE + .3))
    chute = prog(t, T_CHUTE, T_CHUTE + 1.0)
    x, y = 900, 560
    if chute <= 0:
        draw_galileo_entry(c, x, y, 1.0, 90, heat=.25 * (1 - sep), t=t)
        if sep > 0:
            pass
    else:
        # heat shield falling away
        draw_galileo_entry(c, x + 30 * chute, y + 600 * e_in(prog(t, T_CHUTE, T_CHUTE + 2.5)), 1.0, 90 + 40 * chute, heat=0, t=t, alpha=1 - prog(t, T_CHUTE + 1.5, T_CHUTE + 2.5))
        sway = math.sin(t * 1.8) * 6 * chute
        draw_galileo_descent(c, x, y - 40 * e_out(chute), 1.15, chute=chute, sway=sway, t=t, transmit=prog(t, T_TRANSMIT, T_TRANSMIT + .6))
    kr = prog(t, T_ROBOT + .2, T_ROBOT + .8)
    if kr > 0:
        draw_tag(c, 'ROBOTIC PROBE · BUILT TO SURVIVE ENTRY', 1300, 160, 'hist', alpha=e_out(kr))
    ko = prog(t, T_TRANSMIT, T_TRANSMIT + .8)
    if ko > 0:
        draw_text(c, 'DATA → GALILEO ORBITER (RELAY TO EARTH)', 960, 120, mono(24, 'semi'), hexc('#9FE3FF'), 'center', alpha=e_out(ko))
    draw_tag(c, HIST_TAG, 40, 36, 'hist')

# ------------------------------------------------------------------ S23 fictional capsule reveal
def s23(c, t):
    lt = t - T_FICT
    calm = e_out(prog(t, T_SHAKESTOP, T_SHAKESTOP + 1.0))
    gf = e_io(prog(t, T_GLOWFADE, T_FIRST + .3))
    bg(c, '#3a1408', '#8a4a26')
    c.drawPaint(P(hexc('#ffb070', .55 * (1 - gf))))
    cloud_world(c, t, fall=lerp(700, 60, calm), drift=0, tint=(1, .78, .52), bg_draw=False, alpha=.85)
    amp = 14 * (1 - calm)
    sx, sy = math.sin(t * 41) * amp, math.cos(t * 37) * amp * .6
    draw_capsule(c, 960 + sx, 540 + sy, 1.35, 0, 1, t, heat=.9 * (1 - gf),
                 face=dict(blink=1.0 if t < T_SHAKESTOP + .4 else explorer_look_default(t), brow=-1 + calm, mouth='grit' if calm < .5 else 'neutral', look=(0, 0)))
    k = prog(t, T_FICT + .4, T_FICT + 1.0)
    draw_tag(c, FICT_TAG, 40, 36, 'fict', alpha=e_out(k))
    if k > 0:
        label_line(c, 1080, 400, 1400, 260, 'YOUR FICTIONAL CAPSULE', hexc('#6FD3FF'), k=k, size=36, sub='IMAGINARY PROTECTION FROM THOSE FORCES')

# ------------------------------------------------------------------ S24 surrounded by clouds, no horizon
def s24(c, t):
    lt = t - T_FIRST
    look_y = keys(t, [(T_ABOVE - .3, 0), (T_ABOVE + .2, -1), (T_BESIDE - .2, -1), (T_BESIDE + .3, 0), (T_BELOW - .2, 0), (T_BELOW + .3, 1), (T_MISSING, 1), (T_MISSING + .6, 0)])
    look_x = keys(t, [(T_BESIDE - .2, 0), (T_BESIDE + .3, 1), (T_BELOW - .2, 1), (T_BELOW + .3, 0)])
    pull = e_io(prog(t, T_MISSING, T_HORIZON + .6))
    cam_y = look_y * 260 * (1 - pull)
    cam_x = look_x * 260 * (1 - pull)
    cloud_world(c, t, fall=55, drift=-12, ox=-cam_x, oy=-cam_y, tint=(1, .8, .56), bg_top='#efc58f', bg_bot='#a0582e', bg_mid='#d89a5c', depth_dark=.2)
    s = lerp(1.25, .32, pull)
    cx = 960 + cam_x * .3; cy = 560 + cam_y * .3
    draw_capsule(c, cx, cy, s, 0, 1, t, face=dict(look=(look_x, look_y), blink=explorer_look_default(t), brow=.6 if pull < .5 else .3, mouth='o' if T_SURROUND < t < T_BELOW + 1.5 else 'neutral'))
    for tt, txt, (lx, ly) in ((T_ABOVE, 'ABOVE: CLOUDS', (960, 150)), (T_BESIDE, 'BESIDE: CLOUDS', (1560, 540)), (T_BELOW, 'BELOW: MORE CLOUDS', (960, 880))):
        a = fade_window(t, tt, T_MISSING + .2, .3, .4)
        draw_text(c, txt, lx, ly, mono(32, 'bold'), hexc('#FFF1D6'), 'center', alpha=a, shadow=1)
    kh = prog(t, T_HORIZON - .1, T_HORIZON + .4)
    if kh > 0:
        dashed(c, [(80, 540), (1840, 540)], hexc('#FFF1D6'), 3, alpha=.6 * e_out(kh) * (.5 + .5 * math.sin(t * 5)), phase=t * 30)
        hud_panel(c, 1260, 150, 520, 120, 'HORIZON', e_out(kh), warn=True)
        draw_text(c, 'NOT FOUND', 1290, 240, mono(52, 'bold'), hexc(PAL['danger']), alpha=e_out(kh))
    draw_tag(c, FICT_TAG, 40, 36, 'fict')

# ------------------------------------------------------------------ S25 Earth horizon vs Jupiter
def s25(c, t):
    k = e_out(prog(t, T_ONEARTH, T_ONEARTH + .8))
    split = W / 2
    c.save(); c.clipRect(skia.Rect(0, 0, split - 3, H))
    bg(c, '#4f8fd8', '#cfe6ff')
    c.drawRect(skia.Rect(0, 620, split, H), P(shader=lin((0, 620), (0, H), [hexc('#6aa04a'), hexc('#2f5a22')])))
    for i in range(6):
        c.drawCircle(80 + i * 170, 625, 70 + (i % 3) * 25, P(hexc('#4a7d38')))
    c.drawLine(0, 620, split, 620, P(hexc('#FFFFFF', .9), stroke=3))
    label_line(c, 700, 620, 760, 470, 'HORIZON', hexc('#0b1230'), k=prog(t, T_ONEARTH + .8, T_GROUND + .5), size=36)
    draw_text(c, 'SKY', 200, 320, font(44, 'black'), hexc('#ffffff'), 'center', alpha=e_out(prog(t, T_ONEARTH + 1, T_ONEARTH + 1.5)))
    draw_text(c, 'GROUND', 200, 820, font(44, 'black'), hexc('#ffffff'), 'center', alpha=e_out(prog(t, T_GROUND, T_GROUND + .5)))
    draw_text(c, 'EARTH', 480, 110, font(44, 'black'), hexc('#0b1230'), 'center')
    c.restore()
    c.save(); c.clipRect(skia.Rect(split + 3, 0, W, H)); c.translate(split, 0)
    c.save(); c.scale(.5, 1)
    cloud_world(c, t, fall=40, tint=(1, .78, .52), bg_top='#E3B47A', bg_mid='#a8582a', bg_bot='#3a1408', depth_dark=.5)
    c.restore()
    ki = prog(t, T_INSIDE, T_INSIDE + .6)
    draw_text(c, 'NO HORIZON', 480, 560, font(52, 'black'), hexc('#FFF1D6'), 'center', alpha=e_out(ki), shadow=1)
    draw_text(c, 'NO LANDSCAPE BELOW', 480, 620, mono(24, 'semi'), hexc('#FFF1D6'), 'center', alpha=e_out(ki), shadow=1)
    draw_text(c, 'JUPITER', 480, 110, font(44, 'black'), hexc('#FFF1D6'), 'center', shadow=1)
    c.restore()
    c.drawRect(skia.Rect(split - 3, 0, split + 3, H), P(hexc('#070B1A')))

# ------------------------------------------------------------------ S26 instruments: 1 bar, -108 C, H/He, fatal
def s26(c, t):
    lt = t - T_INSTR
    cold = e_io(prog(t, T_M108 - .3, T_M108 + 1.2))
    cloud_world(c, t, fall=40, drift=-10, tint=(lerp(1, .8, cold), lerp(.78, .8, cold), lerp(.52, .75, cold)), bg_top='#d9a066', bg_bot='#6b3a20', alpha=1)
    c.drawPaint(P(hexc('#06101f', .55)))
    # cockpit: explorer bust left, lit by instruments
    mood = keys(t, [(T_SAFE, 0), (T_SAFE + .3, 1), (T_UNTIL, 1), (T_UNTIL + .3, -1)])
    mouth = 'smile' if T_SAFE < t < T_UNTIL else 'frown' if t > T_UNTIL else 'neutral'
    if t > T_FATAL: mouth = 'grit'
    lookx = .7 if t > T_INSTR + .3 else 0
    draw_explorer_bust(c, 430, 470, 170, look=(lookx, .1), blink=explorer_look_default(t), brow=mood if mood > 0 else mood, mouth=mouth, light='#9FE3FF', light_amt=.7, sweat=prog(t, T_FATAL, T_FATAL + .5))
    # instrument column right
    x = 960
    k1 = prog(t, T_1BAR - .3, T_1BAR + .3)
    if k1 > 0:
        draw_gauge(c, x + 170, 330, 150, .1 * e_out(k1), 'PRESSURE', f'{1.0 * e_out(k1):.1f} bar', alpha=e_out(k1), tick_labels=['0', '', '', '', '', '5', '', '', '', '', '10'],
                   sub='≈ EARTH SEA LEVEL' if t > T_SEALEVEL else None)
    k2 = prog(t, T_M108 - .4, T_M108 + .2)
    if k2 > 0:
        temp = -108 * e_out(prog(t, T_M108 - .4, T_M108 + 1.0))
        draw_thermo(c, x + 520, 220, 280, .08, f'{temp:.0f}°C', alpha=e_out(k2), marks=[(.08, '-108'), (.5, '0'), (.9, '+50')])
    k3 = prog(t, T_HYD - .2, T_HYD + .5)
    if k3 > 0:
        hud_panel(c, x, 560, 760, 220, 'ATMOSPHERE (GALILEO, BY VOLUME)', e_out(k3))
        rows = [('H₂  HYDROGEN', .86, '#FFF1D6', '~86%'), ('He  HELIUM', .136, '#E3B47A', '~14%')]
        for i, (lab, v, col, txt) in enumerate(rows):
            yy = 630 + i * 50
            draw_text(c, lab, x + 24, yy + 8, mono(22, 'semi'), hexc('#FFFFFF'), alpha=e_out(k3))
            rrect(c, x + 270, yy - 14, 380 * v * e_out(k3), 26, 6, P(hexc(col, e_out(k3))))
            draw_text(c, txt, x + 280 + 380 * v * e_out(k3), yy + 8, mono(22, 'bold'), hexc('#FFFFFF'), alpha=e_out(k3))
        ko = prog(t, T_NOO2, T_NOO2 + .4)
        if ko > 0:
            draw_text(c, 'O₂  BREATHABLE OXYGEN', x + 24, 738, mono(22, 'semi'), hexc(PAL['danger']), alpha=e_out(ko))
            draw_text(c, 'NONE', x + 380, 738, mono(26, 'bold'), hexc(PAL['danger']), alpha=e_out(ko))
    kf = prog(t, T_FATAL + .2, T_FATAL + .6)
    if kf > 0:
        hud_panel(c, 300, 790, 640, 90, None, e_out(kf), warn=True)
        draw_text(c, '⚠ OUTSIDE: LETHAL', 620, 852, font(44, 'black'), hexc(PAL['danger']), 'center', alpha=e_out(kf) * (.8 + .2 * math.sin(t * 8)))
    # frost on screen edges when cold
    if cold > 0:
        draw_img(c, vignette_img(.9), 0, 0, W, H, cold * .6, cf=tint_cf(0, 0, 0))
        c.drawPaint(P(shader=rad(960, 540, 1150, [hexc('#9FE3FF', 0), hexc('#9FE3FF', 0), hexc('#cfefff', .28 * cold)], [0, .7, 1])))
    draw_tag(c, FICT_TAG, 40, 36, 'fict')

# ------------------------------------------------------------------ S27 temperature rises, pressure increases
def hud_values(t):
    """Approx. Galileo-like profile: (pressure bar, temp C, depth km below 1-bar level). Values approximate."""
    kf = [(T_STRANGE, (1.0, -108, 0)), (T_WARMDAY + .5, (6.0, 25, 70)), (T_FIVE, (5.0, 10, 60)),
          (T_TEN, (10.0, 70, 95)), (T_FIFTEEN, (15.0, 110, 125)), (T_FIFTEEN + 1.5, (15.0, 110, 125))]
    if t < T_FIVE:
        p = keys(t, [(T_STRANGE, 1.0), (T_PINC, 4.0), (T_DENSER + .5, 4.8)])
        tc = keys(t, [(T_RISING, -108), (T_WARMDAY + .3, 25), (T_DENSER, 40)])
        d = keys(t, [(T_STRANGE, 0), (T_DENSER + .5, 58)])
        return p, tc, d
    p = keys(t, [(T_FIVE, 5.0), (T_TEN, 10.0), (T_FIFTEEN, 15.0)], e_out)
    tc = keys(t, [(T_FIVE, 45), (T_TEN, 80), (T_FIFTEEN, 115)], e_out)
    d = keys(t, [(T_FIVE, 60), (T_TEN, 100), (T_FIFTEEN, 125)], e_out)
    return p, tc, d

def hud_stack(c, t, alpha=1.0):
    p, tc, d = hud_values(t)
    hud_readout(c, 1440, 120, 380, 'PRESSURE', f'{p:.1f}', 'bar', alpha, warn=p > 9, size=40)
    hud_readout(c, 1440, 250, 380, 'TEMPERATURE', f'{tc:+.0f}', '°C', alpha, size=40)
    hud_readout(c, 1440, 380, 380, 'DEPTH (≈, BELOW 1-BAR)', f'{d:.0f}', 'km', alpha, size=40)

def s27(c, t):
    lt = t - T_STRANGE
    p, tc, d = hud_values(t)
    dk = clamp((p - 1) / 15)
    cloud_world(c, t, fall=160, drift=-10, tint=(1, .74 - .1 * dk, .5 - .12 * dk), bg_top=PAL['jlight'], bg_mid='#a8582a', bg_bot='#3a1408', depth_dark=.3 + .4 * dk, haze=.15 + .35 * dk)
    mouth = 'smile' if T_IMPROVE - .2 < t < T_CATCH + .2 else ('frown' if t > T_CATCH + .2 else 'neutral')
    brow = 1 if T_IMPROVE - .2 < t < T_CATCH else (-1 if t > T_CATCH else 0)
    sq = e_out(prog(t, T_DOESNT, T_DOESNT + 1.0))
    draw_capsule(c, 800, 540, 1.25, 0, 1, t, face=dict(look=(.5, 0), blink=explorer_look_default(t), brow=brow, mouth=mouth))
    if sq > 0:
        for i in range(10):
            a = i / 10 * math.tau + t * .2
            r0 = 420 - 40 * ((t * 1.3 + i * .13) % 1.0)
            arrow(c, 800 + math.cos(a) * r0, 540 + math.sin(a) * r0 * .9, 800 + math.cos(a) * (r0 - 110), 540 + math.sin(a) * (r0 - 110) * .9, hexc('#FFF1D6'), 5, 20, .75 * sq)
        draw_text(c, 'PRESSURE PUSHES FROM EVERY SIDE', 800, 980 - 70, mono(26, 'bold'), hexc('#FFF1D6'), 'center', alpha=sq, shadow=1)
    hud_stack(c, t)
    kw = fade_window(t, T_WARMDAY - .1, T_CATCH + .3, .3, .4)
    if kw > 0:
        draw_tag(c, '≈ A WARM DAY ON EARTH', 1440, 530, 'concept', alpha=kw)
    draw_tag(c, FICT_TAG, 40, 36, 'fict')

# ------------------------------------------------------------------ S28 five, ten, fifteen bars
def s28(c, t):
    p, tc, d = hud_values(t)
    cloud_world(c, t, fall=300, tint=(.9, .6, .4), bg_top='#a8582a', bg_bot='#2a0e06', depth_dark=.7, haze=.45)
    sx, sy = 0, 0
    for tt in (T_FIVE, T_TEN, T_FIFTEEN):
        a, b = shake(t, tt, .45, 12)
        sx += a; sy += b
    c.save(); c.translate(sx, sy)
    draw_capsule(c, 960, 600, 1.0, 0, 1, t, face=dict(look=(0, -.4), brow=-1, mouth='grit', blink=0))
    c.restore()
    for tt, txt, xx in ((T_FIVE, '5 BAR', 420), (T_TEN, '10 BAR', 960), (T_FIFTEEN, '15 BAR', 1500)):
        big_number(c, txt, xx, 250, 110, hexc('#FFF1D6') if txt != '15 BAR' else hexc(PAL['danger']), t, tt, glow_=.4)
    hud_stack(c, t, .0)
    draw_tag(c, FICT_TAG, 40, 36, 'fict')

# ------------------------------------------------------------------ S29 expecting an ocean
def s29(c, t):
    lt = t - T_LOOKOUT
    cloud_world(c, t, fall=120, tint=(.9, .62, .42), bg_top='#a8582a', bg_bot='#2a0e06', depth_dark=.6, haze=.35)
    # explorer looks down through window
    draw_explorer_bust(c, 960, 360, 150, look=(0, 1), blink=explorer_look_default(t), brow=.4, mouth='neutral', light='#ffb070', light_amt=.5)
    k = prog(t, T_EXPECT + .3, T_EXPECT + 1.5)
    gone = e_io(prog(t, T_DOESNTEND, T_DOESNTEND + 1.6))
    if k > 0:
        a = e_out(k) * (1 - gone)
        for j in range(4):
            pa = skia.Path(); yy = 800 + j * 40
            pa.moveTo(0, yy)
            for i in range(0, W + 40, 40):
                pa.lineTo(i, yy + 10 * math.sin(i * .01 + t * 2 + j))
            p_ = P(hexc('#6FD3FF', a * (.8 - j * .15)), stroke=3)
            p_.setPathEffect(skia.DashPathEffect.Make([20, 14], 0))
            c.drawPath(pa, p_)
        draw_tag(c, 'WHAT YOU MIGHT EXPECT: AN OCEAN SURFACE', 960, 720, 'concept', align='center', alpha=a)
    if gone > 0:
        draw_text(c, "BUT IT DOESN'T END THE WAY YOU EXPECT", 960, 860, font(46, 'black'), hexc('#FFF1D6'), 'center', alpha=fade_window(t, T_DOESNTEND + .3, T_BEFORE + 1.2, .4, .4), shadow=1)
    draw_tag(c, FICT_TAG, 40, 36, 'fict')

# ------------------------------------------------------------------ S30 Galileo measures
def s30(c, t):
    lt = t - T_GDISC
    cloud_world(c, t, fall=60, drift=-15, tint=(1, .78, .52), bg_top='#d9a066', bg_bot='#6b3a20', depth_dark=.3)
    # sepia archival treatment
    sway = math.sin(t * 1.6) * 5
    draw_galileo_descent(c, 760, 580, 1.2, chute=1, sway=sway, t=t, transmit=1)
    km = prog(t, T_MEASURE, T_MEASURE + .6)
    if km > 0:
        for i in range(16):
            ph = (t * .8 + i / 16) % 1.0
            a = i / 16 * math.tau
            r = lerp(300, 60, ph)
            c.drawCircle(760 + math.cos(a) * r, 600 + math.sin(a) * r * .7, 5, P(hexc('#9FE3FF', km * (1 - ph))))
        hud_panel(c, 1240, 300, 540, 300, 'PROBE INSTRUMENTS', e_out(km), color='#FFB347')
        for i, lab in enumerate(['TEMPERATURE', 'PRESSURE', 'COMPOSITION', 'CLOUDS', 'WINDS']):
            draw_text(c, '▸ ' + lab, 1270, 380 + i * 42, mono(24, 'semi'), hexc('#FFF1D6'), alpha=e_out(prog(t, T_MEASURE + i * .25, T_MEASURE + .3 + i * .25)))
    ks = prog(t, T_SURPRISING, T_SURPRISING + .4)
    if ks > 0:
        draw_text(c, '!', 1700, 380, font(140, 'black'), hexc('#FFB347'), 'center', alpha=e_out(ks), glow=.5)
    c.drawPaint(P(hexc('#704214', .12)))
    draw_tag(c, HIST_TAG, 40, 36, 'hist')

# ------------------------------------------------------------------ S31 less water, dry region (hot spot)
def s31(c, t):
    lt = t - T_LESSWATER
    bg(c, '#140d08', '#05070f')
    mapk = e_io(prog(t, T_DRY - .5, T_DRY + .8))
    if mapk < 1:
        a = 1 - mapk
        x0, y0 = 520, 820
        card(c, 300, 180, 1320, 720, a)
        draw_text(c, 'WATER VAPOR AT THE PROBE SITE', 960, 260, font(40, 'black'), hexc('#FFF1D6'), 'center', alpha=a)
        ke = e_out(prog(t, T_LESSWATER + .2, T_LESSWATER + 1.0)); km = e_out(prog(t, T_LESSWATER + 1.2, T_LESSWATER + 2.0))
        rrect(c, 560, 780 - 440 * ke, 240, 440 * ke, 10, P(hexc('#6FD3FF', .35 * a)))
        rrect(c, 560, 780 - 440 * ke, 240, 440 * ke, 10, P(hexc('#6FD3FF', a), stroke=3))
        draw_text(c, 'EXPECTED', 680, 830, mono(26, 'bold'), hexc('#6FD3FF'), 'center', alpha=a * ke)
        rrect(c, 1120, 780 - 120 * km, 240, 120 * km, 10, P(hexc('#FFB347', a)))
        draw_text(c, 'MEASURED', 1240, 830, mono(26, 'bold'), hexc('#FFB347'), 'center', alpha=a * km)
        draw_text(c, 'MUCH LESS', 1240, 780 - 120 * km - 24, font(34, 'black'), hexc('#FFFFFF'), 'center', alpha=a * km)
        draw_text(c, 'SCHEMATIC · NOT EXACT VALUES', 1580, 870, mono(16, 'medium'), hexc(HUDC), 'right', alpha=a * .8)
        kf = fade_window(t, T_FORMED - .3, T_DRY - .3, .4, .3)
        if kf > 0:
            draw_tag(c, 'WATER ABUNDANCE → CLUES TO HOW JUPITER FORMED', 960, 120, 'concept', align='center', alpha=kf)
        kq = fade_window(t, T_MISUNDER, T_DRY, .3, .3)
        draw_text(c, '?', 1240, 470, font(160, 'black'), hexc('#FFB347'), 'center', alpha=kq, glow=.4)
    if mapk > 0:
        a = mapk
        space(c, t, alpha=a)
        R = 420
        draw_jupiter(c, 960, 560, R, rot=1.0 + t * .01, alpha=a)
        hx, hy = 960 - 60, 560 - R * math.sin(math.radians(6.5))
        c.drawOval(skia.Rect(hx - 50, hy - 16, hx + 50, hy + 16), P(hexc('#2a1208', .75 * a), blur=6))
        kk = prog(t, T_DRY + .5, T_DRY + 1.2)
        label_line(c, hx, hy, 1500, 300, 'PROBE ENTRY SITE', hexc('#FFB347'), alpha=a, k=kk, size=36, sub='A RARE, UNUSUALLY DRY "HOT SPOT"')
    draw_tag(c, HIST_TAG, 40, 36, 'hist')

# ------------------------------------------------------------------ S32 weather station in a desert
def s32(c, t):
    lt = t - T_LIKE
    z = e_io(prog(t, T_LIKE + .5, T_DESERT + .2))
    space(c, t)
    R = lerp(330, 900, z)
    cx, cy = 960, lerp(560, 560 + 900 * .2, z)
    draw_earth(c, cx, cy, R, rot=0.6, max_grid=900)
    if z > .8:
        a = prog(z, .8, 1)
        c.drawOval(skia.Rect(760, 360, 1160, 520), P(hexc('#d8b07a', .85 * a), blur=20))
        # weather station
        sx, sy = 960, 430
        c.drawLine(sx, sy, sx, sy - 120, P(hexc('#e8e8e8', a), stroke=5))
        c.drawRect(skia.Rect(sx - 26, sy - 90, sx + 26, sy - 50), P(hexc('#ffffff', a)))
        for i in range(3):
            ang = t * 6 + i * 2.09
            c.drawLine(sx, sy - 120, sx + math.cos(ang) * 40, sy - 120 + math.sin(ang) * 10, P(hexc('#cccccc', a), stroke=3))
        label_line(c, sx + 30, sy - 70, 1400, 260, 'ONE WEATHER STATION', hexc('#FFF1D6'), alpha=a, k=prog(t, T_DESERT, T_DESERT + .6), size=36, sub='IN ONE DESERT')
    ko = prog(t, T_ONELOC, T_ONELOC + .5)
    if ko > 0:
        card(c, 560, 760, 800, 110, e_out(ko))
        draw_text(c, '1 LOCATION ≠ THE WHOLE PLANET', 960, 830, font(44, 'black'), hexc('#FFF1D6'), 'center', alpha=e_out(ko))
    draw_tag(c, 'ANALOGY', 40, 36, 'concept')

# ------------------------------------------------------------------ S33 Galileo keeps falling, signal lost
def s33(c, t):
    lt = t - T_KEPTF2
    k = prog(t, T_KEPTF2, T_LOST)
    cloud_world(c, t, fall=200, tint=(.9, .62, .42), bg_top='#a8582a', bg_bot='#2a0e06', depth_dark=.4 + .4 * k, haze=.2 + .4 * k)
    draw_galileo_descent(c, 820, 560, 1.0, chute=1, sway=math.sin(t * 2) * 4, t=t, transmit=1 if t < T_LOST - .3 else 0, heat=k * .6)
    p = keys(t, [(T_KEPTF2, 15), (T_20X, 20), (T_CONT, 22)])
    tc = keys(t, [(T_KEPTF2, 110), (T_CLIMBED + 1.0, 140), (T_CONT, 152)])
    d = keys(t, [(T_KEPTF2, 125), (T_CONT + 1, 150)])
    hud_readout(c, 1440, 120, 380, 'PRESSURE', f'{p:.0f}', 'bar', 1, warn=p >= 20, size=40, color='#FFB347')
    hud_readout(c, 1440, 250, 380, 'TEMPERATURE', f'{tc:+.0f}', '°C', 1, size=40, color='#FFB347')
    hud_readout(c, 1440, 380, 380, 'DEPTH (≈, BELOW 1-BAR)', f'{d:.0f}', 'km', 1, size=40, color='#FFB347')
    k20 = prog(t, T_20X, T_20X + .5)
    if k20 > 0:
        draw_tag(c, '> 20× EARTH SEA-LEVEL PRESSURE', 1440, 520, 'hist', alpha=e_out(k20))
    lost = t >= T_LOST - .3
    signal_bars(c, 1460, 640, 0 if lost else 1, lost=lost)
    draw_text(c, 'SIGNAL LOST' if lost else 'TRANSMITTING', 1560, 636, mono(22, 'bold'), hexc(PAL['danger']) if lost else hexc(PAL['ok']), alpha=1)
    if lost:
        # static burst
        rng = np.random.default_rng(int(t * 60))
        a = 1 - prog(t, T_LOST - .3, T_LOST)
        for i in range(160):
            y = rng.random() * H
            c.drawRect(skia.Rect(0, y, W, y + rng.random() * 6), P(rgba(255, 255, 255, a * .35 * rng.random())))
    draw_tag(c, HIST_TAG, 40, 36, 'hist')

# ------------------------------------------------------------------ S34 58 minutes, destroyed
def s34(c, t):
    lt = t - T_LOST
    bg(c, '#0a0506', '#000000')
    kd = e_io(prog(t, T_DESTROY - .5, T_EXTRA))
    glow(c, 960, 700, 500, hexc('#7a2a10'), .5)
    draw_galileo_descent(c, 960, lerp(420, 640, kd), .8, chute=1, alpha=(1 - kd) * .8, t=t)
    k = prog(t, T_LASTED, T_LASTED + 2.5)
    if k > 0:
        x0, x1, y = 460, 1460, 200
        c.drawLine(x0, y, x1, y, P(hexc('#ffffff', .2), stroke=6, cap='round'))
        c.drawLine(x0, y, lerp(x0, x1, e_io(k)), y, P(hexc('#FFB347'), stroke=6, cap='round'))
        draw_text(c, '0 MIN', x0, y + 44, mono(22, 'semi'), hexc('#FFF1D6'), 'center')
        draw_text(c, '≈ 58 MIN OF SCIENCE DATA', x1, y + 44, mono(22, 'semi'), hexc('#FFB347'), 'center', alpha=e_out(prog(k, .8, 1)))
    kf = prog(t, T_FAILED, T_FAILED + .5)
    if kf > 0:
        draw_text(c, 'TRANSMITTER FAILED · PROBE LATER DESTROYED BY HEAT AND PRESSURE', 960, 900 - 40, mono(22, 'semi'), hexc('#FFF1D6'), 'center', alpha=e_out(kf) * .9)
    draw_tag(c, HIST_TAG, 40, 36, 'hist')

# ------------------------------------------------------------------ S35 tiny fraction
def s35(c, t):
    lt = t - T_EXTRA
    space(c, t)
    z = keys(t, [(T_EXTRA, 1.0), (T_FRACTION + .2, 1.0), (T_HUMANITY, 1.15)])
    R = 400 * z
    cx, cy = 960, 560
    unknown = e_io(prog(t, T_BARELY - .5, T_BARELY + 1))
    draw_cross_section(c, cx, cy, R, wedge=(-90, 0), rot=2.0, dark_unknown=.85, core_alpha=0, show_metal=0, metal_glow=0, t=t)
    dep = 150 / 69911 * R
    c.drawLine(cx + 3, cy - R, cx + 3, cy - R + 3, P(hexc(PAL['danger']), stroke=4))
    glow(c, cx + 3, cy - R + 2, 30, hexc(PAL['danger']), .9)
    k = prog(t, T_LASTDEPTH, T_LASTDEPTH + .6)
    label_line(c, cx + 3, cy - R + 2, cx + 380, cy - R - 20 if cy - R > 120 else 140, 'GALILEO STOPPED HERE', hexc('#FF8A7A'), k=k, size=34, sub='≈ 150 km DOWN')
    kf = prog(t, T_FRACTION, T_FRACTION + .5)
    if kf > 0:
        # depth bar comparison
        x0, y0, L = 300, 930 - 60, 1320
        c.drawRect(skia.Rect(x0, y0, x0 + L, y0 + 22), P(hexc('#3D5A9E', .5 * e_out(kf))))
        c.drawRect(skia.Rect(x0, y0, x0 + max(3, L * 150 / 69911), y0 + 22), P(hexc(PAL['danger'], e_out(kf))))
        draw_text(c, 'CLOUD TOPS', x0, y0 - 14, mono(18, 'semi'), hexc('#FFF1D6'), alpha=e_out(kf))
        draw_text(c, 'CENTER ≈ 70,000 km', x0 + L, y0 - 14, mono(18, 'semi'), hexc('#FFF1D6'), 'right', alpha=e_out(kf))
        draw_text(c, 'GALILEO: ≈ 0.2%', x0, y0 + 56, mono(22, 'bold'), hexc('#FF8A7A'), alpha=e_out(kf))
    if unknown > 0:
        draw_text(c, '?', cx + R * .4, cy - R * .25, font(170, 'black'), hexc('#6FD3FF'), 'center', alpha=unknown, glow=.5)
        draw_text(c, 'UNEXPLORED', cx + R * .4, cy - R * .25 + 60, mono(24, 'bold'), hexc('#6FD3FF'), 'center', alpha=unknown)

SHOTS2 = [
    (T_HIT, s18, ('flash', .35)),
    (T_DARKNESS, s19, ('fade', .6)),
    (T_DECEL, s20, ('cut', 0)),
    (T_HUMAN, s21, ('black', .4)),
    (T_ROBOT, s22, ('fade', .5)),
    (T_FICT, s23, ('black', .6)),
    (T_FIRST, s24, ('fade', .6)),
    (T_ONEARTH, s25, ('fade', .4)),
    (T_INSTR, s26, ('fade', .5)),
    (T_STRANGE, s27, ('fade', .6)),
    (T_FIVE - .15, s28, ('cut', 0)),
    (T_LOOKOUT, s29, ('fade', .5)),
    (T_GDISC, s30, ('fade', .7)),
    (T_LESSWATER, s31, ('fade', .4)),
    (T_LIKE, s32, ('whip', .35)),
    (T_KEPTF2, s33, ('fade', .5)),
    (T_LOST, s34, ('cut', 0)),
    (T_EXTRA, s35, ('black', .8)),
]
```

## A.12 `engine/example_jupiter/scenes3.py` — Jupiter shots 36–54 (610 lines)

```python
# Shots 36-54 : imaginary probe, dense fluid, metallic hydrogen, magnetic field, fuzzy core, answer, ending.
from common import *
from scenes2 import T_CONTINUE, explorer_look_default
A = at
T_NOTREAL = A('Not with real technology')
T_IMAGINARY = A('but with an imaginary')
T_MODELS = A('scientific models predict')
T_HCOMP = A('As you descend the hydrogen')
T_DENSITY = A('The density rises')
T_PENORM = A('The pressure becomes enormous')
T_GRAD = A('And gradually')
T_DFLUID = A('more like a dense fluid')
T_WEIRD = A("But here's the weird part")
T_SPLASH = A('You never splash')
T_WAVE = A('enormous wave')
T_WLINE = A('No clear water line')
T_SUDDEN = A('No sudden moment')
T_INSTEAD = A('Instead the hydrogen')
T_DEEPF = A('deep fluid interior')
T_STRANGER = A('And now we reach')
T_FARTHER = A('much farther down')
T_SCIFI = A('sounds like science fiction')
T_METAL = A('Metallic hydrogen')
T_ROCKS = A("Now don't imagine")
T_MERCURY = A('Or a shiny metal')
T_NOTMEAN = A("That's not what scientists")
T_UNDER = A('Under extreme pressure')
T_ELECTRONS = A('Its electrons can move')
T_CURRENTS = A('electric currents to flow')
T_BELIEVE = A('And scientists believe')
T_WHYMATTER = A('But why does that matter')
T_REMEMBER = A("Remember Jupiter's powerful")
T_TRAP = A('trapping dangerous radiation')
T_DEEPMOVE = A('Deep inside Jupiter the movement')
T_GENERATE = A('helps generate that magnetic')
T_THINK = A('Think about that')
T_INVISIBLE = A('The invisible danger')
T_COULDNT = A("Something you couldn't see")
T_CENTER = A("But we still haven't")
T_SURPRISE = A('biggest surprise')
T_FORYEARS = A('For years')
T_COMPACT = A('relatively compact core')
T_BALL = A('something like a giant ball')
T_JUNO2 = A('But NASA Juno spacecraft complicated')
T_GRAV = A('By measuring tiny variations')
T_EVIDENCE = A('scientists found evidence')
T_FUZZY = A('A fuzzy core')
T_INSTEAD2 = A('Instead of all the heavier')
T_SPREAD = A('they may be spread')
T_DONTKNOW = A("And scientists still don't know")
T_FORMATION = A('Some models involve')
T_COLLISION = A('Others explore whether')
T_NOSC = A('But no spacecraft has ever reached')
T_NOCAM = A('No camera has photographed')
T_NOBODY = A('And nobody can tell')
T_BACK = A('Which brings us back')
T_IFYOU = A('If you actually fell', after=640)
T_NO = A('No', after=649)
T_WOULDNT = A("You wouldn't reach")
T_REALTECH = A('With real technology')
T_EVENIMAG = A('And even with our imaginary')
T_ROCKY = A('simple rocky landscape')
T_TRAVEL = A('Instead you would travel')
T_DENSEF = A('incredibly dense fluid')
T_LIKEMETAL = A('behaves like a metal')
T_CENTRAL = A('toward a central structure')
T_MOST = A("And here's the most surprising")
T_FROMEARTH = A('From Earth Jupiter looks')
T_ONLYCLOUDS = A('are only its visible clouds')
T_ALMOST = A('Almost everything')
T_PHOTO = A('We can photograph')
T_MEASGRAV = A('measure its gravity')
T_STUDYMAG = A('study its magnetic field')
T_PREDICT = A('and predict the exotic')
T_NEVER = A("But we've never directly")
T_NEXTTIME = A('So the next time')
T_NIGHT = A('in the night sky')
T_NOTLOOK = A("You're not looking at")
T_WORLD = A("You're looking at a world")
T_SENDING = A('sending spacecraft across')
T_BARELY2 = A("we've barely begun")
T_VO_END = 739.7
END_T = T_VO_END + 8.5

MODEL_TAG = 'MODEL-BASED ILLUSTRATION · IMAGINARY PROBE'

def deep_env(c, t, depth, fall=120):
    """depth 0..1: amber clouds -> dense dark-red fluid -> metallic blue-violet."""
    if depth < .5:
        k = depth / .5
        top = mixc('#8a3b1f', '#4a140a', k); bot = mixc('#2a0e06', '#14040a', k)
    else:
        k = (depth - .5) / .5
        top = mixc('#4a140a', '#1b1550', k); bot = mixc('#14040a', '#05031a', k)
    c.drawPaint(P(shader=lin((0, 0), (0, H), [top, bot])))
    hz = haze_sprites()
    for i in range(7):
        d = .4 + (i % 3) * .3
        y = ((i * 197 - t * fall * d) % (H + 300)) - 150
        x = ((i * 331 + t * 10 * d) % (W + 600)) - 600
        col = (1, .55, .35) if depth < .6 else (.55, .6, 1)
        draw_img(c, hz[i % len(hz)], x, y, 1600, 260, .25 * (1 - abs(depth - .5)) + .1, cf=tint_cf(*col))

def molecules(c, t, density, alpha=1.0, fall=100, metal=0.0):
    """H2 molecule field; density 0..1 controls spacing."""
    rng = np.random.default_rng(12)
    n = int(lerp(26, 220, density))
    pts = rng.random((220, 4))
    for i in range(n):
        x = (pts[i, 0] * (W + 100)) - 50 + math.sin(t * 2 + i) * 6
        y = (pts[i, 1] * (H + 100) - t * fall * (.5 + pts[i, 2])) % (H + 100) - 50
        r = lerp(16, 10, density)
        if metal > 0:
            c.drawCircle(x, y, r * .55, P(hexc('#ff9a7a', alpha * (1 - metal * .3))))
        else:
            h2_molecule(c, x, y, r, pts[i, 3] * 6.28 + t * .5, alpha * .85, '#FFE0C0')
    if metal > 0:
        for i in range(160):
            ph = (t * .35 + pts[i % 220, 3]) % 1.0
            x = ph * (W + 200) - 100
            y = pts[i % 220, 1] * H + math.sin(t * 3 + i) * 12
            c.drawCircle(x, y, 4, P(hexc('#8fe8ff', alpha * metal)))
            glow(c, x, y, 14, hexc('#6FD3FF'), alpha * metal * .5)

# ------------------------------------------------------------------ S36 imaginary indestructible probe
def s36(c, t):
    deep_env(c, t, .1)
    cloud_world(c, t, fall=80, tint=(.9, .6, .42), bg_draw=False, alpha=.6, depth_dark=.6)
    kr = prog(t, T_NOTREAL, T_NOTREAL + .5)
    if t < T_IMAGINARY:
        draw_galileo_descent(c, 960, 560, .9, chute=1, alpha=e_out(kr) * (1 - prog(t, T_IMAGINARY - .5, T_IMAGINARY)), t=t)
        draw_x(c, 960, 500, 260, prog(t, T_NOTREAL + .6, T_NOTREAL + 1.2))
        draw_text(c, 'NO REAL SPACECRAFT COULD SURVIVE THIS', 960, 880, font(40, 'black'), hexc('#FFF1D6'), 'center', alpha=e_out(prog(t, T_NOTREAL + 1, T_NOTREAL + 1.5)), shadow=1)
    else:
        k = e_out(prog(t, T_IMAGINARY, T_IMAGINARY + .8))
        draw_capsule(c, 960, 540, lerp(.8, 1.2, k), 0, k, t, shield=k, face=dict(look=(0, .4), brow=.6, mouth='neutral', blink=explorer_look_default(t)))
        draw_text(c, 'IMAGINARY · INDESTRUCTIBLE', 960, 900 - 20, font(44, 'black'), hexc('#8fd8ff'), 'center', alpha=k, glow=.3)
        km = prog(t, T_MODELS - .3, T_MODELS + .3)
        draw_tag(c, 'FROM HERE ON: WHAT SCIENTIFIC MODELS PREDICT', 960, 140, 'model', align='center', alpha=e_out(km))
    draw_tag(c, MODEL_TAG, 40, 36, 'model', alpha=e_out(prog(t, T_IMAGINARY, T_IMAGINARY + .5)))

# ------------------------------------------------------------------ S37 hydrogen compressed -> dense fluid
def s37(c, t):
    dens = e_io(prog(t, T_HCOMP, T_DFLUID + 1.0))
    deep_env(c, t, .15 + .25 * dens)
    molecules(c, t, dens, 1, fall=lerp(140, 40, dens))
    draw_capsule(c, 760, 540, .85, 0, 1, t, shield=.6, ambient='#c4541c', face=dict(look=(.6, .2), brow=.3, blink=explorer_look_default(t)))
    kd = prog(t, T_DENSITY - .2, T_DENSITY + .4)
    if kd > 0:
        draw_gauge(c, 1450, 330, 150, .15 + .7 * dens, 'DENSITY', 'RISING', alpha=e_out(kd), warn_from=.8)
    kp = prog(t, T_PENORM - .2, T_PENORM + .4)
    if kp > 0:
        hud_readout(c, 1260, 540, 380, 'PRESSURE (MODEL)', 'THOUSANDS', 'bar', e_out(kp), size=36)
    kg = prog(t, T_GRAD, T_GRAD + .8)
    if kg > 0:
        x0, y0, L = 1180, 760, 560
        c.drawRect(skia.Rect(x0, y0, x0 + L, y0 + 40), P(shader=lin((x0, 0), (x0 + L, 0), [hexc('#E3B47A'), hexc('#8a3b1f'), hexc('#3a0e08')])))
        draw_text(c, 'GAS', x0, y0 + 76, mono(24, 'bold'), hexc('#FFF1D6'), alpha=e_out(kg))
        draw_text(c, 'DENSE FLUID', x0 + L, y0 + 76, mono(24, 'bold'), hexc('#FFF1D6'), 'right', alpha=e_out(kg))
        mk = x0 + L * e_io(prog(t, T_GRAD, T_DFLUID + .8))
        c.drawCircle(mk, y0 + 20, 14, P(hexc('#6FD3FF')))
    draw_tag(c, MODEL_TAG, 40, 36, 'model')

# ------------------------------------------------------------------ S38 no splash
def s38(c, t):
    deep_env(c, t, .42)
    molecules(c, t, .85, .6, fall=60)
    sway = math.sin(t * 1.2) * 3
    brace = 1 if t > T_SPLASH else 0
    draw_capsule(c, 620, 520, .95, sway, 1, t, shield=.5, ambient='#c4541c', face=dict(look=(0, 1), brow=-1 if brace else .5, mouth='grit' if T_SPLASH < t < T_WAVE else 'o', blink=0))
    items = [(T_SPLASH, 'NO SPLASH'), (T_WAVE, 'NO WAVE'), (T_WLINE, 'NO WATER LINE'), (T_SUDDEN, 'NO SEPARATE SEA')]
    for i, (tt, txt) in enumerate(items):
        k = prog(t, tt, tt + .35)
        if k <= 0:
            continue
        y = 260 + i * 140
        card(c, 1100, y - 60, 640, 105, e_out(k))
        draw_x(c, 1160, y - 8, 46, prog(t, tt + .15, tt + .5))
        draw_text(c, txt, 1220, y + 8, font(44, 'black'), hexc('#FFF1D6'), alpha=e_out(k))
    draw_tag(c, MODEL_TAG, 40, 36, 'model')

# ------------------------------------------------------------------ S39 gradual change
def s39(c, t):
    bg(c, '#140608', '#05030a')
    x, top, bot, w = 960, 120, 960, 300
    c.drawRect(skia.Rect(x - w / 2, top, x + w / 2, bot), P(shader=lin((0, top), (0, bot), [hexc('#E3B47A'), hexc('#b8693a'), hexc('#6b2a14'), hexc('#3a0e08'), hexc('#1b1550')], [0, .2, .5, .8, 1])))
    c.drawRect(skia.Rect(x - w / 2, top, x + w / 2, bot), P(hexc('#FFF1D6', .4), stroke=2))
    yy = lerp(top + 40, bot - 140, e_io(prog(t, T_INSTEAD, T_DEEPF + 1.2)))
    draw_capsule(c, x, yy, .32, 0, 1, t, shield=.5)
    k = prog(t, T_INSTEAD + .4, T_INSTEAD + 1.0)
    draw_text(c, 'GAS', x - w / 2 - 30, top + 40, mono(26, 'bold'), hexc('#FFF1D6'), 'right', alpha=e_out(k))
    draw_text(c, 'DENSE FLUID', x - w / 2 - 30, bot - 160, mono(26, 'bold'), hexc('#FFF1D6'), 'right', alpha=e_out(k))
    kk = prog(t, T_INSTEAD + 1.4, T_INSTEAD + 2.0)
    label_line(c, x + w / 2, (top + bot) / 2, x + w / 2 + 160, (top + bot) / 2 - 60, 'NO SURFACE · NO BOUNDARY', hexc('#FFF1D6'), k=kk, size=36, sub='PROPERTIES CHANGE GRADUALLY WITH PRESSURE & TEMPERATURE')
    kd = prog(t, T_DEEPF - .2, T_DEEPF + .4)
    if kd > 0:
        draw_text(c, 'THE DEEP FLUID INTERIOR', x - w / 2 - 30, bot - 110, font(34, 'black'), hexc('#ff9a6a'), 'right', alpha=e_out(kd))
    draw_text(c, 'SCHEMATIC · NOT TO SCALE', x + w / 2 + 30, bot, mono(16, 'medium'), hexc(HUDC), alpha=.7)
    draw_tag(c, MODEL_TAG, 40, 36, 'model')

# ------------------------------------------------------------------ S40 metallic hydrogen reveal (visual peak)
def s40(c, t):
    k = e_io(prog(t, T_STRANGER, T_METAL))
    deep_env(c, t, .45 + .55 * k, fall=60)
    molecules(c, t, .9, 1 - .5 * k, fall=40, metal=k * .9)
    km = prog(t, T_METAL - .1, T_METAL + .4)
    flash(c, (1 - e_out(prog(t, T_METAL - .1, T_METAL + .5))) * .45 * (t > T_METAL - .1), '#9fb0ff')
    draw_capsule(c, 960, 520, .7, 0, 1, t, shield=.6, ambient='#6a6aff', hull_light='#bfc8ff', face=dict(look=(-.5, 0), brow=1, mouth='o', blink=0))
    if km > 0:
        draw_text(c, 'METALLIC HYDROGEN', 960, 900, font(96, 'black'), hexc('#cfd6ff'), 'center', alpha=e_out(km), glow=.6, glow_color=hexc('#6FD3FF'))
        draw_text(c, 'PREDICTED BY HIGH-PRESSURE PHYSICS', 960, 960 - 4, mono(22, 'semi'), hexc('#9FE3FF'), 'center', alpha=e_out(km) * .9)
    kf = fade_window(t, T_FARTHER, T_METAL - .1, .3, .2)
    draw_text(c, 'MUCH FARTHER DOWN…', 960, 200, font(52, 'black'), hexc('#FFF1D6'), 'center', alpha=kf, shadow=1)
    draw_tag(c, MODEL_TAG, 40, 36, 'model')

# ------------------------------------------------------------------ S41 not silver rocks, not mercury
def s41(c, t):
    bg(c, '#0d0a24', '#05031a')
    for i, (tt, txt) in enumerate(((T_ROCKS, 'SILVER ROCKS'), (T_MERCURY, 'A MERCURY-LIKE OCEAN'))):
        k = prog(t, tt, tt + .4)
        if k <= 0:
            continue
        x = 520 + i * 880; y = 480
        card(c, x - 340, y - 260, 680, 520, e_out(k))
        c.save(); c.clipRect(skia.Rect(x - 330, y - 250, x + 330, y + 170))
        if i == 0:
            for j in range(6):
                rx = x - 240 + j * 95; ry = y + 60 - (j % 2) * 40
                pa = path_from([(rx - 50, ry + 50), (rx - 30, ry - 40), (rx + 20, ry - 60), (rx + 55, ry + 10), (rx + 40, ry + 50)], True)
                c.drawPath(pa, P(shader=lin((rx - 50, ry - 60), (rx + 50, ry + 50), [hexc('#f4f6fb', e_out(k)), hexc('#7d8494', e_out(k))])))
        else:
            c.drawRect(skia.Rect(x - 330, y - 250, x + 330, y + 170), P(shader=lin((0, y - 250), (0, y + 170), [hexc('#2a2e3a', e_out(k)), hexc('#0e1018', e_out(k))])))
            for j in range(5):
                pa = skia.Path(); yy = y - 20 + j * 40
                pa.moveTo(x - 330, yy)
                for q in range(0, 680, 20):
                    pa.lineTo(x - 330 + q, yy + 8 * math.sin(q * .03 + t * 2 + j))
                pa.lineTo(x + 330, y + 170); pa.lineTo(x - 330, y + 170); pa.close()
                c.drawPath(pa, P(shader=lin((0, yy - 10), (0, yy + 40), [hexc('#f0f3f8', e_out(k) * .9), hexc('#5a6070', e_out(k))])))
        c.restore()
        draw_text(c, txt, x, y + 225, font(38, 'black'), hexc('#FFF1D6'), 'center', alpha=e_out(k))
        draw_x(c, x, y - 40, 300, prog(t, tt + .4, tt + .9), alpha=.9)
    kn = prog(t, T_NOTMEAN, T_NOTMEAN + .4)
    draw_text(c, "NOT WHAT SCIENTISTS MEAN", 960, 140, font(52, 'black'), hexc('#cfd6ff'), 'center', alpha=e_out(kn), shadow=1)

# ------------------------------------------------------------------ S42 conductivity
def s42(c, t):
    show_cs = e_io(prog(t, T_BELIEVE - .3, T_BELIEVE + .8))
    bg(c, '#120c34', '#05031a')
    if show_cs < 1:
        a = 1 - show_cs
        x0, y0, w, h = 260, 220, 1400, 560
        card(c, x0, y0, w, h, a, color='#0a0a26', border='#8A5CFF')
        rng = np.random.default_rng(3)
        for i in range(10):
            for j in range(4):
                px = x0 + 100 + i * 135 + math.sin(t * 3 + i + j) * 4
                py = y0 + 110 + j * 115 + math.cos(t * 2.5 + i * j) * 4
                c.drawCircle(px, py, 18, P(shader=rad(px - 5, py - 5, 22, [hexc('#ffc4b0', a), hexc('#ff6a4a', a)])))
                draw_text(c, '+', px, py + 8, font(24, 'black'), hexc('#5a1a10'), 'center', alpha=a)
        ke = prog(t, T_ELECTRONS - .3, T_ELECTRONS + .5)
        for i in range(70):
            r = rng.random(3)
            ph = (t * (.12 + .1 * r[2]) * (1 + 2 * prog(t, T_CURRENTS - .5, T_CURRENTS + .5)) + r[0]) % 1.0
            ex = x0 + 40 + ph * (w - 80); ey = y0 + 60 + r[1] * (h - 120) + math.sin(t * 4 + i) * 10
            c.drawCircle(ex, ey, 6, P(hexc('#8fe8ff', a * e_out(ke))))
            glow(c, ex, ey, 18, hexc('#6FD3FF'), a * e_out(ke) * .6)
        draw_text(c, '+  HYDROGEN NUCLEI (PROTONS)', x0 + 30, y0 + h + 50, mono(24, 'semi'), hexc('#ff9a7a'), alpha=a)
        draw_text(c, '●  FREE-MOVING ELECTRONS', x0 + 600, y0 + h + 50, mono(24, 'semi'), hexc('#8fe8ff'), alpha=a * e_out(ke))
        kc = prog(t, T_CURRENTS - .3, T_CURRENTS + .5)
        arrow(c, x0 + 300, y0 - 50, x0 + w - 300, y0 - 50, hexc('#8fe8ff'), 8, 30, a, k=e_out(kc), glow_=1)
        draw_text(c, 'ELECTRIC CURRENT', 960, y0 - 80, mono(26, 'bold'), hexc('#8fe8ff'), 'center', alpha=a * e_out(kc))
        draw_text(c, 'UNDER EXTREME PRESSURE: HYDROGEN CONDUCTS ELECTRICITY', 960, 150, font(38, 'black'), hexc('#cfd6ff'), 'center', alpha=a * e_out(prog(t, T_UNDER, T_UNDER + .5)))
        draw_tag(c, 'CONCEPTUAL DIAGRAM', 40, 36, 'concept', alpha=a)
    if show_cs > 0:
        space(c, t, alpha=show_cs)
        R = 420
        draw_cross_section(c, 960, 560, R, alpha=show_cs, wedge=(-90, 90), t=t, core_alpha=0, metal_glow=.9, highlight=(0.0, 0.8, '#8fe8ff'))
        label_line(c, 960 + R * .5, 560 - R * .1, 1560, 300, 'LIQUID METALLIC HYDROGEN', hexc('#cfd6ff'), alpha=show_cs, k=prog(t, T_BELIEVE + .5, T_BELIEVE + 1.2), size=36, sub='ENORMOUS REGIONS OF THE INTERIOR (MODEL)')
        draw_tag(c, 'MODEL-BASED CUTAWAY · NOT TO SCALE', 40, 36, 'model', alpha=show_cs)

# ------------------------------------------------------------------ S43 magnetic field + radiation (callback)
def belts(c, cx, cy, R, t, alpha):
    if alpha <= 0:
        return
    c.drawOval(skia.Rect(cx - R * 3.4, cy - R * .8, cx + R * 3.4, cy + R * .8), P(hexc('#6FD3FF', .12 * alpha), stroke=R * .5, blur=30))
    rng = np.random.default_rng(8)
    for i in range(140):
        r = rng.random(3)
        L = lerp(1.6, 3.4, r[0])
        ph = t * (.2 + .3 * r[1]) + r[2] * 6.28
        x = cx + math.cos(ph) * R * L; y = cy + math.sin(ph) * R * L * .22 + math.sin(t * 6 + i) * R * .05
        if math.sin(ph) < 0 and abs(x - cx) < R:
            continue
        c.drawCircle(x, y, 3, P(hexc('#cfefff', alpha * .8)))

def s43(c, t):
    space(c, t)
    R = 260
    cx, cy = 960, 560
    kf = e_io(prog(t, T_REMEMBER, T_REMEMBER + 2.5))
    dipole_lines(c, cx, cy, R, alpha=kf, k=kf, t=t)
    draw_jupiter(c, cx, cy, R, rot=2.2 + t * .03)
    kb = prog(t, T_TRAP - .3, T_TRAP + 1.0)
    belts(c, cx, cy, R, t, e_out(kb))
    if kf > 0:
        label_line(c, cx + R * 2.2, cy - R * 1.2, 1560, 180, 'MAGNETIC FIELD', hexc('#6FD3FF'), k=prog(t, T_REMEMBER + .8, T_REMEMBER + 1.6), size=38, sub='THE STRONGEST OF ANY PLANET')
    if kb > 0:
        label_line(c, cx - R * 2.4, cy + 20, 300, 840, 'TRAPPED RADIATION', hexc('#FF8A7A'), k=kb, size=36, sub='DANGEROUS TO SPACECRAFT')
    kq = fade_window(t, T_WHYMATTER, T_REMEMBER, .3, .3)
    draw_text(c, 'WHY DOES IT MATTER?', 960, 150, font(56, 'black'), hexc('#FFF1D6'), 'center', alpha=kq, shadow=1)
    draw_tag(c, 'ILLUSTRATION · FIELD LINES SIMPLIFIED', 40, 36, 'concept')

# ------------------------------------------------------------------ S44 dynamo: interior generates field
def s44(c, t):
    pull = e_io(prog(t, T_COULDNT - .3, T_CENTER))
    R = lerp(400, 230, pull)
    cx, cy = 960, 560
    space(c, t)
    dipole_lines(c, cx, cy, R, alpha=.4 + .6 * prog(t, T_GENERATE, T_GENERATE + 1), k=e_io(prog(t, T_DEEPMOVE, T_GENERATE + 1.5)), t=t)
    draw_cross_section(c, cx, cy, R, wedge=(-90, 90), t=t, core_alpha=0, metal_glow=1)
    # convection swirls in metallic region
    kd = prog(t, T_DEEPMOVE, T_DEEPMOVE + 1)
    for i in range(4):
        rr = R * (.35 + .1 * i)
        start = -60 + ((t * 40 + i * 50) % 120)
        c.drawArc(skia.Rect(cx - rr, cy - rr, cx + rr, cy + rr), start, 40, False, P(hexc('#8fe8ff', .8 * e_out(kd)), stroke=5, cap='round'))
    belts(c, cx, cy, R, t, pull)
    ki = prog(t, T_INVISIBLE, T_INVISIBLE + 1.0)
    if ki > 0:
        dashed(c, [(cx + R * .5, cy - R * .2), (cx + R * 2.0, cy - R * 1.3)], hexc('#FFF1D6'), 4, phase=-t * 40, k=e_out(ki))
        draw_text(c, 'MOVING CONDUCTIVE FLUID  →  MAGNETIC FIELD', 960, 150, font(40, 'black'), hexc('#FFF1D6'), 'center', alpha=e_out(ki), shadow=1)
    kt = fade_window(t, T_THINK, T_INVISIBLE, .3, .3)
    draw_text(c, 'THINK ABOUT THAT.', 960, 150, font(52, 'black'), hexc('#FFF1D6'), 'center', alpha=kt, shadow=1)
    draw_tag(c, 'MODEL-BASED CUTAWAY · NOT TO SCALE', 40, 36, 'model')

# ------------------------------------------------------------------ S45 the center: older compact-core model
def s45(c, t):
    space(c, t)
    z = e_io(prog(t, T_CENTER, T_FORYEARS))
    R = lerp(300, 430, z)
    draw_cross_section(c, 960, 560, R, wedge=(-90, 90), t=t, core_fuzz=0, core_alpha=e_out(prog(t, T_COMPACT - .3, T_COMPACT + .5)), show_metal=1, metal_glow=.3)
    chapter_card(c, 2, 'THE CENTER', t, T_CENTER + .2, T_FORYEARS + .5)
    kc = prog(t, T_COMPACT, T_COMPACT + .6)
    label_line(c, 960 + R * .12, 560, 1500, 700, 'COMPACT CORE', hexc('#FFF1D6'), k=kc, size=38, sub='HEAVY ELEMENTS IN A SHARP, SMALL BALL')
    ko = prog(t, T_FORYEARS, T_FORYEARS + .5)
    draw_tag(c, 'OLDER, SIMPLER MODEL', 1500, 160, 'model', alpha=e_out(ko))

# ------------------------------------------------------------------ S46 Juno gravity -> fuzzy core (visual peak)
def s46(c, t):
    space(c, t)
    R = 380; cx, cy = 820, 560
    fz = e_io(prog(t, T_EVIDENCE, T_FUZZY + .6))
    draw_cross_section(c, cx, cy, R, wedge=(-90, 90), t=t, core_fuzz=fz, core_alpha=1, metal_glow=.3)
    # Juno polar orbit
    kj = prog(t, T_JUNO2, T_JUNO2 + .6)
    if kj > 0:
        orb = skia.Rect(cx - R * .55, cy - R * 1.35, cx + R * .55, cy + R * 1.35)
        c.drawOval(orb, P(hexc('#9FE3FF', .45 * e_out(kj)), stroke=2))
        ph = t * .9
        jx = cx + math.cos(ph) * R * .55; jy = cy + math.sin(ph) * R * 1.35
        draw_juno(c, jx, jy, .16, ph * 50, alpha=e_out(kj))
        draw_tag(c, 'NASA JUNO', jx + 30, jy - 50, 'concept', alpha=e_out(kj))
    kg = prog(t, T_GRAV, T_GRAV + .8)
    if kg > 0:
        # gravity measurement: wavy contours
        for i in range(4):
            rr = R * (1.08 + i * .07)
            pa = skia.Path()
            for j in range(0, 361, 4):
                a = math.radians(j)
                r2 = rr + math.sin(a * 6 + t * 2 + i) * 4 * e_out(kg)
                x, y = cx + math.cos(a) * r2, cy + math.sin(a) * r2
                pa.moveTo(x, y) if j == 0 else pa.lineTo(x, y)
            c.drawPath(pa, P(hexc('#58E08A', .35 * e_out(kg) * (1 - fz * .6)), stroke=2))
        draw_text(c, 'MEASURING TINY GRAVITY VARIATIONS', 1440, 200, mono(24, 'bold'), hexc('#58E08A'), 'center', alpha=e_out(kg) * (1 - fz))
    if fz > 0:
        kk = prog(t, T_FUZZY - .2, T_FUZZY + .5)
        label_line(c, cx + R * .35, cy - R * .2, 1420, 330, 'A "FUZZY" CORE', hexc('#FFE2B0'), k=kk, size=52, sub='HEAVY ELEMENTS SPREAD OUT · DILUTE')
        draw_tag(c, 'EVIDENCE FROM JUNO GRAVITY DATA', 1300, 470, 'model', alpha=e_out(kk))

# ------------------------------------------------------------------ S47 spread through broad region
def s47(c, t):
    space(c, t)
    z = e_io(prog(t, T_INSTEAD2, T_SPREAD + 1))
    R = lerp(380, 900, z)
    cx, cy = lerp(820, 600, z), 560
    draw_cross_section(c, cx, cy, R, wedge=(-90, 90), t=t, core_fuzz=1, core_alpha=1, metal_glow=.3)
    ks = prog(t, T_SPREAD, T_SPREAD + 1.5)
    if ks > 0:
        rr = R * .52
        c.drawArc(skia.Rect(cx - rr, cy - rr, cx + rr, cy + rr), -90, 180, False, P(hexc('#FFE2B0', .8 * e_out(ks)), stroke=3))
        draw_text(c, 'A BROAD CENTRAL REGION', cx + rr + 30, cy + 10, font(40, 'black'), hexc('#FFE2B0'), alpha=e_out(ks), shadow=1)
    kd = prog(t, T_DONTKNOW, T_DONTKNOW + .5)
    if kd > 0:
        draw_text(c, 'HOW DID IT FORM?', 1500, 200, font(52, 'black'), hexc('#FFF1D6'), 'center', alpha=e_out(kd), shadow=1)
        draw_text(c, '?', 1500, 400, font(170, 'black'), hexc('#6FD3FF'), 'center', alpha=e_out(kd), glow=.4)
    draw_tag(c, 'MODEL-BASED CUTAWAY · NOT TO SCALE', 40, 36, 'model')

# ------------------------------------------------------------------ S48 formation vs giant collision
def s48(c, t):
    bg(c, '#0b1230', '#05070f')
    k1 = prog(t, T_FORMATION, T_FORMATION + .5)
    k2 = prog(t, T_COLLISION, T_COLLISION + .5)
    for i, (k, title) in enumerate(((k1, 'SLOW FORMATION PROCESSES'), (k2, 'A GIANT EARLY COLLISION?'))):
        if k <= 0:
            continue
        a = e_out(k)
        x = 500 + i * 920; y = 520
        card(c, x - 400, y - 330, 800, 640, a)
        c.save(); c.clipRect(skia.Rect(x - 390, y - 320, x + 390, y + 220))
        if i == 0:
            for j in range(6):
                rx = 340 - j * 45
                c.drawOval(skia.Rect(x - rx, y - rx * .22, x + rx, y + rx * .22), P(hexc('#E3B47A', a * (.15 + j * .05)), stroke=8))
            for j in range(40):
                ang = t * (.6 + j % 5 * .1) + j
                rr = 60 + (j * 37 % 280)
                c.drawCircle(x + math.cos(ang) * rr, y + math.sin(ang) * rr * .22, 3 + j % 3, P(hexc('#FFF1D6', a * .8)))
            c.drawCircle(x, y, 70, P(shader=rad(x - 20, y - 20, 90, [hexc('#f0c890', a), hexc('#8a4e2b', a)])))
        else:
            hit = (t - T_COLLISION) % 4.0
            draw_jupiter(c, x + 60, y, 150, rot=t * .2, alpha=a)
            ix = x + 60 - 150 - 300 * max(0, 1 - hit / 1.2); iy = y - 120 - 250 * max(0, 1 - hit / 1.2)
            if hit < 1.2:
                c.drawCircle(ix, iy, 50, P(shader=rad(ix - 15, iy - 15, 60, [hexc('#c8b8a8', a), hexc('#5a4a40', a)])))
            else:
                kb = (hit - 1.2) / 2.8
                glow(c, x - 60, y - 100, 260 * (0.3 + kb), hexc('#ffb070'), a * (1 - kb))
        c.restore()
        draw_text(c, title, x, y + 270, font(34, 'black'), hexc('#FFF1D6'), 'center', alpha=a)
        draw_tag(c, 'HYPOTHESIS', x, y - 300, 'model', align='center', alpha=a)

# ------------------------------------------------------------------ S49 no spacecraft, no camera
def s49(c, t):
    bg(c, '#05030a', '#000000')
    glow(c, 960, 560, 330, hexc('#ffb070'), .25 + .05 * math.sin(t * 2))
    glow(c, 960, 560, 160, hexc('#fff1d6'), .12)
    draw_text(c, '?', 960, 640, font(260, 'black'), hexc('#FFF1D6'), 'center', alpha=.8, glow=.4)
    k1 = prog(t, T_NOSC, T_NOSC + .5)
    draw_text(c, 'NO SPACECRAFT HAS BEEN THERE', 960, 170, font(44, 'black'), hexc('#FFF1D6'), 'center', alpha=e_out(k1), shadow=1)
    k2 = prog(t, T_NOCAM, T_NOCAM + .5)
    if k2 > 0:
        x, y = 1550, 560
        rrect(c, x - 90, y - 55, 180, 120, 18, P(hexc('#cfd6e0', e_out(k2))))
        c.drawCircle(x, y + 5, 40, P(hexc('#1d2027', e_out(k2))))
        c.drawCircle(x, y + 5, 26, P(hexc('#3d5a9e', e_out(k2))))
        rrect(c, x - 50, y - 80, 60, 30, 6, P(hexc('#cfd6e0', e_out(k2))))
        draw_x(c, x, y, 200, prog(t, T_NOCAM + .4, T_NOCAM + .9))
        draw_text(c, 'NEVER PHOTOGRAPHED', x, y + 170, mono(24, 'bold'), hexc('#FFF1D6'), 'center', alpha=e_out(k2))
    k3 = prog(t, T_NOBODY + .5, T_NOBODY + 1.2)
    draw_text(c, "NOBODY KNOWS EXACTLY WHAT JUPITER'S CENTER LOOKS LIKE", 960, 900 - 20, mono(26, 'bold'), hexc('#9FE3FF'), 'center', alpha=e_out(k3))

# ------------------------------------------------------------------ S50 back to the question: NO.
def s50(c, t):
    space(c, t)
    no = t >= T_NO
    draw_jupiter(c, 1430, 610, 720, rot=2.4 + t * .012, alpha=.55 if no else 1)
    px, py = 520, 400
    draw_capsule(c, px, py + math.sin(t * 1.4) * 8, .45, 25, 1, t, face=dict(look=(.6, .3), brow=.3, blink=explorer_look_default(t)))
    k = prog(t, T_IFYOU, T_IFYOU + .6)
    draw_text(c, 'WOULD YOU EVENTUALLY', 110, 700, font(64, 'black'), hexc('#FFF1D6'), alpha=e_out(k) * (1 - .6 * no), shadow=1)
    draw_text(c, 'LAND?', 110, 780, font(64, 'black'), hexc('#E3B47A'), alpha=e_out(k) * (1 - .6 * no), shadow=1)
    if no:
        kn = prog(t, T_NO, T_NO + .3)
        c.save(); c.translate(960, 560); s = lerp(1.6, 1.0, e_out(kn)); c.scale(s, s)
        draw_text(c, 'NO.', 0, 80, font(300, 'black'), hexc('#FFFFFF'), 'center', alpha=e_out(kn), glow=.5, shadow=1)
        c.restore()
    draw_tag(c, 'BACK TO THE QUESTION', 40, 36, 'concept', alpha=e_out(prog(t, T_BACK, T_BACK + .5)))

# ------------------------------------------------------------------ S51 recap journey
def s51(c, t):
    bg(c, '#0b1230', '#05070f')
    x, top, bot, w = 520, 110, 980, 220
    c.drawRect(skia.Rect(x - w / 2, top, x + w / 2, bot), P(shader=lin((0, top), (0, bot), [hexc('#E3B47A'), hexc('#8a3b1f'), hexc('#3a0e08'), hexc('#2d2a7a'), hexc('#c98a4a')], [0, .25, .5, .72, 1])))
    c.drawRect(skia.Rect(x - w / 2, top, x + w / 2, bot), P(hexc('#FFF1D6', .4), stroke=2))
    draw_text(c, 'SCHEMATIC · NOT TO SCALE', x, bot + 40, mono(16, 'medium'), hexc(HUDC), 'center', alpha=.7)
    kg = prog(t, T_WOULDNT, T_WOULDNT + .5)
    if kg > 0:
        draw_text(c, 'NO SOLID SURFACE LIKE EARTH', 1300, 880, font(44, 'black'), hexc('#FFF1D6'), 'center', alpha=e_out(kg), shadow=1)
    kr = prog(t, T_REALTECH, T_REALTECH + .5)
    if kr > 0:
        draw_galileo_descent(c, x - 160, top + 70, .25, chute=1, t=t, alpha=e_out(kr))
        draw_x(c, x - 160, top + 60, 80, prog(t, T_REALTECH + .5, T_REALTECH + 1.0))
        draw_text(c, 'REAL SPACECRAFT: DESTROYED EARLY', x - 240, top + 150, mono(18, 'bold'), hexc('#FF8A7A'), 'right' if False else 'left', alpha=0)
    stations = [(T_TRAVEL, .12, 'ATMOSPHERE', '#FFF1D6'), (T_DENSEF, .42, 'INCREDIBLY DENSE FLUID', '#ff9a6a'), (T_LIKEMETAL, .68, 'HYDROGEN BEHAVES LIKE A METAL', '#9fb0ff'), (T_CENTRAL, .92, 'A CENTRAL STRUCTURE STILL BEING STUDIED', '#FFE2B0')]
    prog_y = top
    for tt, f, lab, col in stations:
        k = prog(t, tt, tt + .6)
        if k > 0:
            yy = top + (bot - top) * f
            label_line(c, x + w / 2, yy, x + w / 2 + 140, yy, lab, hexc(col), k=k, size=36)
            prog_y = max(prog_y, lerp(prog_y, yy, 1))
    if t > T_TRAVEL:
        yy = keys(t, [(T_TRAVEL, top + 30)] + [(tt + .8, top + (bot - top) * f) for tt, f, _, _ in stations[1:]])
        draw_capsule(c, x, yy, .22, 0, 1, t, shield=.6)
    kk = prog(t, T_ROCKY - .3, T_ROCKY + .3)
    a = fade_window(t, T_ROCKY - .3, T_TRAVEL + .2, .3, .3)
    if a > 0:
        card(c, 1000, 380, 620, 120, a)
        draw_text(c, 'SIMPLE ROCKY LANDSCAPE', 1330, 455, font(36, 'black'), hexc('#FFF1D6'), 'center', alpha=a)
        draw_x(c, 1060, 440, 50, prog(t, T_ROCKY, T_ROCKY + .5), alpha=a)
    draw_tag(c, 'RECAP · MODEL-BASED', 40, 36, 'model')

# ------------------------------------------------------------------ S52 stripes are only the visible clouds
def s52(c, t):
    space(c, t)
    z = e_io(prog(t, T_MOST, T_FROMEARTH + 1.5))
    R = lerp(40, 380, z)
    op = e_io(prog(t, T_ONLYCLOUDS, T_ALMOST + 1.0))
    draw_cross_section(c, 960, 560, R, wedge=(-90, -90 + 150 * op), t=t, core_fuzz=1, metal_glow=.6)
    kc = prog(t, T_ONLYCLOUDS, T_ONLYCLOUDS + .6)
    if kc > 0 and R > 300:
        label_line(c, 960 - R * .7, 560 - R * .7, 420, 200, 'VISIBLE CLOUDS: A THIN SKIN', hexc('#FFF1D6'), k=kc, size=34)
    ka = prog(t, T_ALMOST + .5, T_ALMOST + 1.2)
    if ka > 0:
        draw_text(c, 'ALMOST EVERYTHING IS HIDDEN BENEATH', 960, 1000 - 70, font(44, 'black'), hexc('#FFF1D6'), 'center', alpha=e_out(ka), shadow=1)

# ------------------------------------------------------------------ S53 what we can do vs never explored
def s53(c, t):
    bg(c, '#0b1230', '#05070f')
    items = [(T_PHOTO, 'PHOTOGRAPH ITS STORMS'), (T_MEASGRAV, 'MEASURE ITS GRAVITY'), (T_STUDYMAG, 'STUDY ITS MAGNETIC FIELD'), (T_PREDICT, 'PREDICT WHAT LIES INSIDE')]
    dim = e_io(prog(t, T_NEVER, T_NEVER + 1.0))
    for i, (tt, lab) in enumerate(items):
        k = prog(t, tt, tt + .4)
        if k <= 0:
            continue
        a = e_out(k) * (1 - .6 * dim)
        x = 250 + (i % 2) * 720; y = 130 + (i // 2) * 370
        card(c, x, y, 680, 330, a)
        cx_, cy_ = x + 170, y + 165
        c.save(); c.clipRect(skia.Rect(x + 10, y + 10, x + 670, y + 320))
        if i == 0:
            draw_jupiter(c, cx_, cy_ - 520 * 0 , 130, rot=math.pi, alpha=a, max_grid=300)
            if t - tt < .3:
                flash(c, (1 - (t - tt) / .3) * .5 * a)
        elif i == 1:
            draw_jupiter(c, cx_, cy_, 100, rot=2.0, alpha=a, max_grid=300)
            draw_juno(c, cx_ + 120, cy_ - 80, .18, t * 30, alpha=a)
        elif i == 2:
            dipole_lines(c, cx_, cy_, 50, alpha=a, k=1, t=t, Ls=(1.6, 2.4, 3.2), width=2)
            draw_jupiter(c, cx_, cy_, 50, rot=2.0, alpha=a, max_grid=200)
        else:
            draw_cross_section(c, cx_, cy_, 120, alpha=a, wedge=(-60, 60), t=t, core_fuzz=1, metal_glow=.8)
        c.restore()
        draw_text(c, lab, x + 340, y + 175, font(30, 'black'), hexc('#FFF1D6'), 'left', alpha=a)
        draw_check(c, x + 620, y + 60, 40, prog(t, tt + .2, tt + .6), alpha=a)
    if dim > 0:
        card(c, 360, 380, 1200, 220, dim, color='#140608', border='#FF3B30')
        draw_text(c, 'DIRECTLY EXPLORED:', 960, 470, mono(30, 'bold'), hexc('#FF8A7A'), 'center', alpha=dim)
        draw_text(c, 'ONLY THE TOP SLIVER', 960, 550, font(64, 'black'), hexc('#FFFFFF'), 'center', alpha=dim, glow=.3)

# ------------------------------------------------------------------ S54 night sky ending
def s54(c, t):
    zoom = e_io(prog(t, T_WORLD, T_VO_END + 1.5))
    bg(c, '#070B1A', '#1C2A55')
    draw_stars(c, t, 1.0, zoom=1 + zoom * 2, cx=1240, cy=300)
    # Jupiter: a bright point, growing to the planet as we "look closer"
    jx, jy = 1240, 300
    R = lerp(5, 330, e_in(zoom))
    glow(c, jx, jy, lerp(60, 520, zoom), hexc('#ffe2b0'), lerp(.7, .25, zoom))
    if R > 8:
        draw_jupiter(c, lerp(jx, 960, zoom), lerp(jy, 470, zoom), R, rot=2.6 + t * .02, alpha=prog(R, 8, 40))
    else:
        c.drawCircle(jx, jy, 5, P(hexc('#fff6e0')))
    # landscape silhouette and a person looking up
    ga = 1 - prog(zoom, .2, .7)
    if ga > 0:
        pa = skia.Path(); pa.moveTo(0, 860)
        for i in range(0, W + 60, 60):
            pa.lineTo(i, 850 + 30 * math.sin(i * .004) + 14 * math.sin(i * .013))
        pa.lineTo(W, H); pa.lineTo(0, H); pa.close()
        c.drawPath(pa, P(hexc('#03050c', ga)))
        px, py = 600, 840
        c.drawCircle(px, py - 120, 22, P(hexc('#03050c', ga)))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(px - 30, py - 98, px + 30, py + 10), 18, 18), P(hexc('#03050c', ga)))
        kl = prog(t, T_NIGHT, T_NIGHT + .6)
        label_line(c, jx, jy, jx + 200, jy + 110, 'JUPITER', hexc('#FFE2B0'), alpha=ga, k=kl, size=34)
    kn = fade_window(t, T_NOTLOOK, T_WORLD, .3, .3)
    draw_text(c, 'NOT A BALL OF GAS WITH A SECRET LANDING SPOT', 960, 120, font(40, 'black'), hexc('#FFF1D6'), 'center', alpha=kn, shadow=1)
    kb = fade_window(t, T_BARELY2 - .3, T_VO_END + 1.0, .5, .6)
    draw_text(c, "WE'VE BARELY BEGUN TO DISCOVER WHAT'S INSIDE", 960, 940 - 40, font(44, 'black'), hexc('#FFF1D6'), 'center', alpha=kb, shadow=1)
    ke = fade_window(t, T_VO_END + 1.2, END_T, .8, 1.0)
    if ke > 0:
        c.drawPaint(P(rgba(3, 4, 10, .45 * ke)))
        draw_text(c, 'WHAT IF YOU ACTUALLY', 960, 810, font(64, 'black'), hexc('#FFF1D6'), 'center', alpha=ke, shadow=1)
        draw_text(c, 'FELL INTO JUPITER?', 960, 890, font(64, 'black'), hexc('#E3B47A'), 'center', alpha=ke, shadow=1, glow=.25)
        draw_text(c, 'Illustrations combine historical data, scientific models and clearly labeled fiction.', 960, 960, font(22, 'medium'), hexc('#9FE3FF'), 'center', alpha=ke * .9)

SHOTS3 = [
    (T_CONTINUE, s36, ('black', .6)),
    (T_HCOMP, s37, ('fade', .6)),
    (T_WEIRD, s38, ('fade', .5)),
    (T_INSTEAD, s39, ('fade', .5)),
    (T_STRANGER, s40, ('fade', .7)),
    (T_ROCKS, s41, ('whip', .35)),
    (T_UNDER, s42, ('fade', .5)),
    (T_WHYMATTER, s43, ('fade', .6)),
    (T_DEEPMOVE, s44, ('fade', .6)),
    (T_CENTER, s45, ('black', .6)),
    (T_JUNO2, s46, ('fade', .4)),
    (T_INSTEAD2, s47, ('cut', 0)),
    (T_FORMATION, s48, ('fade', .5)),
    (T_NOSC, s49, ('black', .5)),
    (T_BACK, s50, ('fade', .6)),
    (T_WOULDNT, s51, ('fade', .5)),
    (T_MOST, s52, ('black', .5)),
    (T_PHOTO, s53, ('fade', .4)),
    (T_NEXTTIME, s54, ('black', .7)),
]
```

## A.13 `engine/example_jupiter/mix.py` — Jupiter music + SFX cue sheet (136 lines)

```python
"""Jupiter cue sheet (worked example). Run from the engine folder:
   JV_PROJECT=example_jupiter python3 example_jupiter/mix.py <voiceover> <drama.mp3> <suspense.mp3> <inspiring.mp3> <out_dir>
Every SFX time comes from the narration (phrase lookups in scenes*.py), never from guessed seconds."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from sfxlib import *
import scenes1 as S1, scenes2 as S2, scenes3 as S3
VO, M_DRAMA, M_SUSP, M_INSP, OUT = sys.argv[1:6]
END = S3.END_T
N = int(END * SR) + SR

# ------------------------------------------------------------------ build SFX bus
sfx = np.zeros((N, 2), np.float32)
amb = np.zeros((N, 2), np.float32)
A = S1
# opening
place(sfx, boom(4, 55, 30, .45, .2), 0.0)
place(amb, drone(9, .10, (41.2, 61.7, 82.4)), 0.0)
place(sfx, whoosh(.9, 200, 3000, .25), S1.T_DROPPED - .3)
place(sfx, rumble(2.5, .25) * fade_env(int(2.5 * SR), 1.2, .8)[:, None], S1.T_SURV_ENTRY - 1.5)
place(sfx, ui_pop(.2), S1.T_SURV_ENTRY + .6)
place(amb, wind(5.0, .16, 2500), S1.T_WINDS - .3)
place(sfx, ui_pop(.15), S1.T_WINDS + .5); place(sfx, ui_pop(.15), S1.T_WINDS + 1.6)
place(amb, wind(4.0, .12, 1500), S1.T_KEPT)
place(sfx, alarm(.8, .1), S1.T_NOGROUND)
for i in range(8):
    place(sfx, blip(1000, .08, .12), S1.T_THEN58 + .4 + i * .45)
place(sfx, tone(1000, 1.8, .12, .005, 1.2), S1.T_ENDED + .25)
place(sfx, static(.35, .2), S1.T_ENDED + .1)
# scale pull-out
place(sfx, whoosh(2.5, 100, 1500, .2, .3), S1.T_SCRATCH + .2)
place(amb, drone(10, .08, (49, 73.4, 98)), S1.T_BUTHERE)
for tt in (S1.T_SOLID, S1.T_OCEAN, S1.T_CENTER):
    place(sfx, thud(.18), tt + .1)
place(sfx, whoosh(.5, 400, 5000, .3), S1.T_BUTFIRST - .2)
place(sfx, thud(.25), S1.T_EARTHFALL + .5)
place(sfx, boom(4, 60, 30, .35, .3), S1.T_NOWHERE)
place(sfx, whoosh(2.0, 150, 2000, .15, .6), S1.T_REDOVAL)
place(amb, wind(8, .07, 1800), S1.T_CLOUDS)
place(sfx, whoosh(.5, 400, 5000, .3), S1.T_ENORMOUS - .2)
for i in range(12):
    place(sfx, blip(900 + i * 60, .05, .06), S1.T_1300 - .3 + i * .14)
place(sfx, whoosh(3.0, 200, 3000, .3, .5), S1.T_JUNO - .2)
place(sfx, boom(3, 50, 28, .3, .2), S1.T_3000B)
place(sfx, riser(2.8, .25), S1.T_ABOUT)
place(sfx, boom(3, 70, 30, .5, .6), S1.T_OBSTACLE)
place(amb, rumble(15, .10, 30, 400, .3) * fade_env(int(15 * SR), 3, 1)[:, None], S1.T_OBSTACLE)
for i in range(10):
    place(sfx, blip(1500, .03, .05), S1.T_170 + i * .18)
# entry
entry_dur = S2.T_SHAKESTOP + .5 - S2.T_HIT
er = rumble(entry_dur, 1.0, 25, 900, .2)
t = tvec(entry_dur)
env = np.interp(t, [0, S2.T_DARKNESS - S2.T_HIT, S2.T_DECEL - S2.T_HIT, S2.T_DECEL - S2.T_HIT + 3, S2.T_HUMAN - S2.T_HIT, entry_dur - .5, entry_dur], [.15, .45, .7, .5, .12, .1, 0])
place(sfx, er * env[:, None] * .7, S2.T_HIT)
place(sfx, boom(2, 80, 40, .3, .7, 2500), S2.T_HIT)
place(sfx, riser(S2.T_DECEL - S2.T_DARKNESS, .3), S2.T_DARKNESS)
place(sfx, boom(5, 90, 25, 1.0, .9, 3000), S2.T_DECEL)
place(sfx, boom(3, 70, 30, .55, .5), S2.T_228B)
for tt in (S2.T_ORDINARY, S2.T_SUIT, S2.T_HOLD):
    place(sfx, thud(.2), tt + .4)
place(sfx, creak(1.0, .15, 120), S2.T_WORST + .6)
place(sfx, chute_snap(.35), S2.T_CHUTE - .2)
for i in range(6):
    place(sfx, blip(1400, .07, .05), S2.T_TRANSMIT + i * .5)
place(sfx, whoosh(1.2, 100, 1200, .2, .3), S2.T_FICT)
place(amb, wind(S2.T_ONEARTH - S2.T_FIRST, .10, 1400), S2.T_FIRST)
place(sfx, shimmer(2.0, .05), S2.T_HORIZON - .2)
place(sfx, alarm(.5, .06), S2.T_HORIZON)
for tt in (S2.T_1BAR, S2.T_M108, S2.T_HYD):
    place(sfx, ui_pop(.16), tt - .2)
place(sfx, alarm(1.6, .12), S2.T_FATAL + .2)
place(amb, wind(S2.T_GDISC - S2.T_STRANGE, .09, 1000), S2.T_STRANGE)
place(sfx, creak(1.6, .22, 80), S2.T_DOESNT + .2)
for i, tt in enumerate((S2.T_FIVE, S2.T_TEN, S2.T_FIFTEEN)):
    place(sfx, boom(1.6, 80, 40, .35 + .1 * i, .6), tt)
    place(sfx, creak(1.2, .18 + .05 * i, 70 - 8 * i), tt + .1)
place(sfx, ui_pop(.12), S2.T_WARMDAY)
place(amb, wind(S2.T_LESSWATER - S2.T_GDISC, .08, 1600), S2.T_GDISC)
place(sfx, ui_pop(.15), S2.T_SURPRISING)
place(sfx, whoosh(.5, 400, 5000, .3), S2.T_LIKE - .2)
place(amb, wind(S2.T_LOST - S2.T_KEPTF2, .12, 900), S2.T_KEPTF2)
for i in range(int((S2.T_LOST - S2.T_CONT) / .5)):
    place(sfx, blip(1000, .08, .08), S2.T_CONT + i * .5)
place(sfx, static(.6, .35), S2.T_LOST - .35)
place(sfx, tone(1000, 2.5, .09, .005, 2.0), S2.T_LOST + .2)
place(amb, drone(S2.T_CONTINUE - S2.T_LOST + 2, .09, (36.7, 55, 73.4)), S2.T_LOST + 1.0)
place(sfx, boom(4, 45, 25, .3, .1), S2.T_EXTRA)
# interior
place(sfx, thud(.25), S3.T_NOTREAL + .6)
place(sfx, shimmer(2.5, .07), S3.T_IMAGINARY)
place(amb, rumble(S3.T_STRANGER - S3.T_HCOMP, .08, 25, 200, .4) * fade_env(int((S3.T_STRANGER - S3.T_HCOMP) * SR), 2, 2)[:, None], S3.T_HCOMP)
for tt in (S3.T_SPLASH, S3.T_WAVE, S3.T_WLINE, S3.T_SUDDEN):
    place(sfx, thud(.18), tt + .15)
place(sfx, riser(S3.T_METAL - S3.T_STRANGER - .1, .22), S3.T_STRANGER)
place(sfx, boom(4, 60, 30, .45, .4), S3.T_METAL)
place(sfx, shimmer(4, .09), S3.T_METAL)
place(amb, crackle(S3.T_WHYMATTER - S3.T_METAL, .08, 6), S3.T_METAL)
place(sfx, whoosh(.5, 400, 5000, .3), S3.T_ROCKS - .2)
place(sfx, thud(.2), S3.T_ROCKS + .4); place(sfx, thud(.2), S3.T_MERCURY + .4)
place(amb, hum(S3.T_CENTER - S3.T_REMEMBER, .07, 55), S3.T_REMEMBER)
place(amb, crackle(S3.T_CENTER - S3.T_TRAP, .05, 4), S3.T_TRAP)
place(sfx, boom(3, 50, 28, .3, .2), S3.T_CENTER)
place(sfx, riser(S3.T_FUZZY - S3.T_EVIDENCE, .2), S3.T_EVIDENCE)
place(sfx, shimmer(3, .08), S3.T_FUZZY)
place(sfx, boom(3, 55, 30, .3, .3), S3.T_FUZZY)
place(sfx, boom(3, 80, 30, .35, .7), S3.T_COLLISION + 1.2)
place(sfx, thud(.25), S3.T_NOCAM + .4)
place(sfx, riser(S3.T_NO - S3.T_IFYOU, .18), S3.T_IFYOU)
place(sfx, boom(4.5, 70, 28, .7, .6), S3.T_NO)
for tt in (S3.T_TRAVEL, S3.T_DENSEF, S3.T_LIKEMETAL, S3.T_CENTRAL):
    place(sfx, ui_pop(.12), tt)
for tt in (S3.T_PHOTO, S3.T_MEASGRAV, S3.T_STUDYMAG, S3.T_PREDICT):
    place(sfx, ui_pop(.13), tt)
place(sfx, shimmer(4, .06), S3.T_NIGHT - .5)
place(sfx, boom(5, 50, 28, .4, .2), S3.T_VO_END + 1.2)

# ------------------------------------------------------------------ music bus
mus = np.zeros((N, 2), np.float32)
drama = load(M_DRAMA); susp = load(M_SUSP); insp = load(M_INSP)
cue(mus, drama, 0.0, 0.0, S2.T_HIT + 1.0, .05, 3.0, -3)
cue(mus, susp, S2.T_FIRST - 1.0, 0.0, S2.T_LOST - S2.T_FIRST + 1.0, 4.0, .25, -6)
cue(mus, drama, S2.T_CONTINUE - .3, 28.0, S3.T_CENTER - S2.T_CONTINUE + 2.5, 3.0, 3.0, -4)
cue(mus, susp, S3.T_CENTER + .5, 40.0, S3.T_BACK - S3.T_CENTER + 1.0, 4.0, 2.5, -9)
ti = S3.T_BACK - 1.0
cue(mus, insp, ti, 14.0, END - ti, 3.0, 4.0, -2)


# ------------------------------------------------------------------ voice + mix + finish
vo = load(VO, VO_CHAIN)
voice = np.zeros((N, 2), np.float32); place(voice, vo, 0.0)
os.makedirs(OUT, exist_ok=True)
raw = mixdown(voice, mus, sfx, amb, os.path.join(OUT, 'mix_raw.wav'))
print('final (LUFS, true peak dBFS):', finish(raw, os.path.join(OUT, 'mix_final.wav')))
```


---

# APPENDIX B — ENVIRONMENT SETUP (Claude Code cloud session)

```bash
# 1. Python packages
pip install skia-python numpy pillow sherpa-onnx
# 2. Skia needs EGL/GL system libraries
apt-get update && apt-get install -y libegl1 libgl1
python3 -c "import skia; print(skia.__version__)"
# 3. Speech model (GitHub release; Hugging Face may be blocked)
mkdir -p models && cd models
curl -sSL -o p.tar.bz2 https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8.tar.bz2
tar xjf p.tar.bz2 && cd ..
# 4. Tools present in the base image: ffmpeg/ffprobe (libx264), fonts Inter, Inter Display, JetBrains Mono
fc-list : family | grep -E "Inter|JetBrains"
nproc   # cores -> parallel render jobs
```

# APPENDIX C — COMMAND REFERENCE (one project, end to end)

```bash
ENGINE=prompt_book/engine ; PROJ=projects/<slug> ; OUT=$PROJ/out ; mkdir -p $PROJ
python3 $ENGINE/transcribe.py <voiceover.mp3> models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8 $PROJ
python3 -c "import sys;sys.path.insert(0,'$ENGINE');import sfxlib;print(sfxlib.music_energy('<track.mp3>'))"
cp $ENGINE/scenes_TEMPLATE.py $PROJ/scenes1.py          # write shots; add scenes2.py ...
cd $ENGINE
JV_PROJECT=../../$PROJ python3 render.py contact 0 60 1.5 /tmp/sheet.png 5   # QA loop
JV_PROJECT=../../$PROJ python3 render.py bench 5 60 200
./render_all.sh ../../$PROJ ../../$OUT 8 $(nproc) 60          # run in the background + monitor
JV_PROJECT=../../$PROJ python3 ../../$PROJ/mix.py <vo> <music1> <music2> <music3> ../../$OUT
ffmpeg -i $OUT/video_only.mp4 -i $OUT/mix_final.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k \
       -shortest -movflags +faststart $OUT/<Title>.mp4
ffprobe -v error -show_entries format=duration:stream=width,height,r_frame_rate,nb_frames -of compact $OUT/<Title>.mp4
```

**SRT generation (from words.json):** group words into captions of ≤ 38 characters, break after sentence punctuation (when the text is > 18 characters) or at pauses > 0.9 s, end each caption at the next caption's start (or +0.9 s after sentence ends), minimum 0.6 s.

# APPENDIX D — GLOSSARY

- **Micro-beat:** one animated development within a shot (label pop, counter, glance, reframe).
- **Visual peak:** a planned standout moment with extra production effort (3–5 per film).
- **Honesty tag:** the top-left pill that classifies a shot as historical / fictional / model / concept.
- **Contact sheet:** a grid of downscaled frames at regular times, used for QA before rendering.
- **Ducking:** automatic lowering of music and ambience under the voice.
- **LUFS / dBTP:** integrated loudness (EBU R128) / true-peak level.
- **Multiplane:** separating layers by depth so that parallax produces depth.
- **Cutaway:** a cross-section showing interior layers through a removed wedge.
- **END_T:** the program end time (voiceover end + end card), defined in the last scenes file.
