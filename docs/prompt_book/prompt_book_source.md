# 3D Short Prompt Book
## Script + voiceover in, "Last Stop" quality out
Version 1.1 · 2026-11-15 · Built from the verified P01 "Last Stop" production in this repository

# 0. How to use this book

Every time you make a video, you supply only two things:

- **SCRIPT**: what happens, shot by shot (use the input form in Section 2).
- **VOICEOVER**: either the narration *text* (Claude synthesizes it with Kokoro) or a finished *audio file* (Claude measures and uses it).

Claude Code does everything else at the quality locked in Section 3: characters, sets, lighting, animation, camera, weather, sound, captions, assembly and QC.

**Every video gets a brand-new cast and a brand-new world.** The *quality* stays fixed; the *designs* never repeat. Section 3A (the Variety Engine) generates a unique ensemble of characters and a unique 3D environment for each project. A registry of past designs stops a character or world from coming back. Pip and the rainy street in P01 are only a quality reference and are never reused.

The workflow is three steps:

1. Open a Claude Code session on this repository (`favorbliss910/Dart_Bliss`).
2. Paste the **MASTER PROMPT** (Section 1) as your message.
3. Directly underneath it, paste your filled-in **INPUT FORM** (Section 2) and attach the voiceover file if you have one.

Claude works through Stages 0–10 (Section 4), including the Variety Engine in Stage 1B. It stops at the gates and shows you stills before any long render. Section 5 has copy-ready fix prompts for the problems most likely to come up. Section 6 is the quick reference.

What "this quality" means, in one sentence: a new original, stylized 3D world for every video rendered in Blender Cycles. It has real camera movement through near/mid/far depth layers, wet reflective surfaces and motivated warm/cool practical lighting. Each video has its own ensemble of distinct, appealing characters with planted feet, eyes that lead the head, overlap and squash. Narration is Kokoro `am_michael`, with procedural sound timed to the animation. Everything is assembled in Remotion with measured captions.

Honest limits: only one shot (P01, a rainy night street) has been fully produced and verified. Every new location, weather or character must pass its own look-development gate (Stage 5) before a full render. On the current cloud container (4 CPUs, no GPU), each 540×960 frame takes about 31 s, which is about 1 hour per 5 seconds of video.

# 1. Master prompt (paste this every time)

```
You are Claude Code working in my repository favorbliss910/Dart_Bliss. Produce a
stylized 3D short at the locked "Last Stop" quality defined in
docs/prompt_book/ (this prompt book) and proven by tools/build_proof_scene.py,
tools/make_audio.py, tools/qc_p01.py and remotion/.

MY INPUTS are the INPUT FORM below (script, voiceover text or attached
voiceover audio, format, characters). Treat them as the creative brief. Do not
change my words. If something in the form is ambiguous, pick the option that
best serves the story, write the choice in docs/decisions_<PROJECT>.md, and
continue. Only stop to ask me if the script is impossible to stage.

NON-NEGOTIABLE QUALITY LOCK (do not lower without asking me):
- Blender (bpy 5.3) + Cycles. All depth, perspective and camera movement are real
  3D in Blender. Remotion only sequences, captions, mixes and encodes; never 2D
  zoom/pan to fake movement.
- Every shot: a near layer that crosses frame (pole, sign, bollard, rain,
  foliage...), a mid layer (characters + main set), a far layer (distant
  buildings/landscape + atmosphere). Measure parallax: near/far screen shift ratio > 3.
- AgX view transform, look "AgX - Medium High Contrast", exposure about +0.35,
  denoised, adaptive sampling, 24 fps, portrait 9:16 unless the form says otherwise.
- Motivated lighting: a warm key from a practical source, a cool rim, a low fill
  about 3 stops under the key, practicals visible in frame; area lights hidden from
  camera (and from glossy rays where they would wash out glass).
- Characters: original, subdivided, believable materials (clear-coat plastic,
  felt, knit, ceramic, metal, fur - varied per character); big readable
  eyes with pupils on pivots; brows; arc mouth with shape changes; feet planted
  with 0 mm sliding; eyes lead head by about 4 frames; hat/hair/ears lag by about 3
  frames; bob lowest on contact; squash about 3.5% on contact; anticipation before
  big moves; overshoot and settle on stops; blink at least once per shot over 3 s.
- Voice: if I attached audio, use it unchanged except resampling and level.
  If I gave text, synthesize with Kokoro voice am_michael (speed 1.0, en-us)
  unless the form names another voice. Never claim the voice is a real person.
- Sound: original procedural ambience, Foley and FX generated in code, timed
  from the exported animation events (contact frames, prop events). Duck
  ambience -6 dB under dialogue. Final mix -16 LUFS integrated, true peak <= -1 dBTP.
- Captions: phrase-level, timed from the MEASURED voice audio (energy envelope),
  placed where they never cover a face or key action.
- Original work only. Do not copy any existing film, show, game or brand.

UNIQUENESS RULES (as important as quality):
- EVERY video gets a NEW cast and a NEW environment. Never reuse a character
  design, set, layout or palette from an earlier project. Pip and the P01
  rainy street are only a QUALITY reference; never put them in a new video.
- Run the Variety Engine (prompt book section 3A, Stage 1B): roll a project
  seed, generate the cast and the world from the design dice, and check both against
  registry/characters.json and registry/environments.json. Re-roll any axis
  that repeats a past project's combination. Log the new designs in the
  registry when the video ships.
- Cast as MANY distinct characters as the story can hold: named leads, plus
  supporting characters, plus background extras with their own simple
  idle/walk cycles. Every character must differ from every other in
  silhouette, proportions, palette and signature feature (squint test: tell
  them apart as black silhouettes at 360 px wide).
- Vary the world on every axis: setting, era, time of day, weather, palette,
  architecture, set dressing, lighting recipe, camera language and sound bed.

PROCESS: follow Stages 0-10 of the prompt book in order. Stages and gates:
  0 environment check -> 1 script breakdown + shot manifest -> 1B VARIETY
  ENGINE (unique cast + unique world, registry check) -> 2 voice first
  (timing comes from audio) -> 3 character build -> 4 set build -> 5 LOOKDEV
  GATE (show me 5 stills per shot at 360x640 and wait for my OK unless I wrote
  AUTO-APPROVE in the form) -> 6 benchmark -> 7 full render (restart-safe) ->
  8 sound -> 9 Remotion assembly -> 10 QC + scorecard.
  After each stage, commit and push to your working branch.

REPORTING: give me the final MP4, a contact sheet, a cast sheet (every
character in a line-up) and a world sheet (3 establishing stills), plus exact commands,
measured timings, QC metrics and a 1-5 scorecard. Mark anything you did not
measure or could not check (e.g. "audio not auditioned by a human"). Never claim
success without the files. If any scorecard category is below 4, list the fixes
and ask whether to do them.

BUDGET: before Stage 7, tell me the estimated render hours (seconds/frame x
frames). If it is more than 3 hours, ask me first, and offer lower resolution,
fewer samples, shorter shots or GPU compute.

INPUT FORM:
<paste Section 2 form here>
```

# 2. Input form (fill this in each time)

Copy the form, fill in the brackets and delete what you don't need. Only TITLE, at least one SHOT and VOICEOVER are required. Claude decides everything else in the house style.

```
TITLE: [working title]
PROJECT_ID: [short code, e.g. EP02]           (used for folder names)
FORMAT: [9:16 portrait | 16:9 | 1:1]  FPS: [24]  DELIVERY: [1080x1920]
PROOF_RES: [540x960]                           (render size before upscale/rerender)
VOICEOVER: [TEXT (synthesize) | FILE: <attached file name>]
VOICE: [am_michael]                            (any installed Kokoro voice)
VOICE_SPEED: [1.0]
CAPTIONS: [ON | OFF]   CAPTION_POSITION: [AUTO | TOP | BOTTOM]
APPROVAL: [WAIT-FOR-ME at lookdev | AUTO-APPROVE]
MAX_RENDER_HOURS: [3]

CAST: [AUTO | describe below]     CAST_SIZE: [MAX | number, e.g. 6]
  (AUTO = Claude invents a brand-new ensemble that fits the story. MAX = as
  many distinct characters as the shots can stage well: leads + supporting +
  background extras.)
CHARACTERS (optional; anything you leave out is generated fresh):
  - NAME: [name]   ROLE: [lead | supporting | extra]
    LOOK: [species/type, shape, outfit, colours, signature feature, prop]
    PERSONALITY / ACTING NOTES: [how they move]
WORLD: [AUTO | describe: setting, era, culture/style, time of day, weather]
VARIETY_SEED: [AUTO | any number]   (same seed = same designs, for reruns)

SHOTS:
  SHOT 1
    LOCATION / TIME / WEATHER: [e.g. rooftop garden, dawn, light mist | AUTO]
    WHO IS IN SHOT: [names + extras, e.g. "Mo, Tali, 4 market extras" | AUTO]
    ACTION: [what the character physically does, in order]
    VO: "[exact narration for this shot, or the timecode range in the file]"
    VISUAL PAYOFF: [the image that answers or lands the line]
    CAMERA (optional): [e.g. low push-in past a railing | lateral truck | crane up]
    MOOD / PALETTE (optional): [e.g. cold blue with one warm window]
    SOUND NOTES (optional): [e.g. pigeons, distant traffic, kettle click]
  SHOT 2
    ...

STORY RULE (optional): [e.g. "the line asks, the picture answers"]
DO NOT: [anything to avoid]
```

Tips that keep the quality high:

- Write one clear physical action and one visual payoff per shot. Shots of 4–7 s work best at this quality.
- Put the payoff *after* the line ends. In P01 the line ended at 3.10 s and the sign flickered on at 3.29 s.
- Name a near-camera object in the location so the camera has something to move past (railings, lamps, plants, signs).
- Leave CAST and WORLD on AUTO if you want maximum variety. Claude will still keep any detail you do give.
- Crowded shots cost more render time. Claude simplifies extras that are far from camera (lower subdivision, simpler cycles) so the budget stays reasonable.
- If you attach a voiceover file, use WAV or high-bitrate MP3. Claude cuts it into lines by measuring silences.

# 3. The quality lock (exact settings that define this look)

These values come from the shipped P01 shot. New shots start from these values and may change them only with a written reason in `docs/decisions_<PROJECT>.md`.

## 3.1 Render

| Setting | Value |
|---|---|
| Engine / device | Cycles, CPU (GPU if available: OptiX/CUDA) |
| Samples | 24, adaptive threshold 0.03, OIDN denoise on |
| Light paths | max bounces 6, transparent 8, volume bounces 0, caustics off, filter glossy 1.0 |
| Performance | persistent data on; frames written one PNG at a time; existing frames skipped (restart-safe) |
| Colour | view AgX, look "AgX - Medium High Contrast", exposure +0.35, 8-bit sRGB PNG |
| Motion blur | off (rain streak length implies motion) |
| Frame rate / size | 24 fps; proof 540×960; delivery 1080×1920 |

## 3.2 Camera grammar

| Rule | Value |
|---|---|
| Sensor | 36 mm, fit VERTICAL for portrait |
| Lenses | 26–35 mm (wide lenses make small characters feel present; P01 went 30 → 26 mm) |
| Depth of field | f/2.2, focus object = character head / neck pivot |
| Aim | Track To constraint on an empty that follows the head, damped (lerp 0.25 per frame); it eases toward the payoff object (P01: 56 % toward the sign, frames 80–110) |
| Height | at or just below character eye level (0.78–1.05 m for a 1.3 m character) |
| Path | 3 location keys (start / middle / end), Bezier; it must pass within about 0.5 m of a near-layer object |
| End frame | 3/4 front view of the character's face with the payoff object in frame. Never end on the back of a head |
| Measured target | near:far projected screen-shift ratio > 3 (P01 = 16.8) |

## 3.3 Lighting recipe (night exterior; adapt the colours for other times of day)

| Light | Type | Power | Colour | Role |
|---|---|---|---|---|
| Key | Area 2.0×1.4 m at the practical source | 45 W | warm (1.0, 0.65, 0.35) | motivated by the window/lamp; hidden from camera, glossy and transmission rays |
| Interior / practical | Area 1.5 m | 18 W | warm (1.0, 0.7, 0.4) | gives interiors depth behind glass |
| Rim | Area 3 m, high, behind subject | 220 W | cool (0.45, 0.6, 1.0) | silhouette separation |
| Fill | Area 4 m, camera side | 35 W | cool (0.6, 0.7, 0.95) | about 3 stops under key; keeps eye whites readable |
| Street / scene practicals | Spot 95°, blend 0.6, radius 0.15 | 70–80 W | warm (1.0, 0.72, 0.42) | pools of light receding into depth |
| Story practical | Point light keyed with the emissive prop | 0 → 32 W | accent (pink 1.0, 0.25, 0.4 in P01) | the payoff light, animated |
| World | Gradient sky | — | (0.035, 0.05, 0.09) → (0.006, 0.008, 0.016) | dark at the top |
| Atmosphere | Volume Scatter, far region only | density 0.035 | (0.6, 0.7, 0.9) | depth haze without slowing near objects |

Day or interior variants: keep the ratios (key 1 : rim about 0.7 : fill about 0.15) and the warm/cool split. Replace the sky gradient with a brighter one or an HDRI-free sun plus sky gradient. Benchmark again, because sun and sky change render times.

## 3.4 Materials (Principled BSDF)

| Surface | Base colour | Roughness | Extras |
|---|---|---|---|
| Wet asphalt / ground | (0.025, 0.026, 0.03) | 0.03–0.42 from Noise (scale 0.6) → ColorRamp (0.45 / 0.6) | grain bump: Noise scale 90, strength 0.15 |
| Curb / concrete | (0.32, 0.31, 0.30) | 0.55 | 2-segment bevel 0.02 |
| Glass | (0.9, 0.95, 1.0) | 0.03 | transmission 1.0 (shows interior and reflects the character) |
| Painted wood / shopfront | e.g. (0.02, 0.16, 0.12) | 0.35 | coat 0.6 |
| Brick / plaster | (0.20, 0.085, 0.06) / (0.08, 0.11, 0.15) | 0.75–0.8 | |
| Metal | (0.05, 0.06, 0.07) | 0.3 | metallic 1.0 |
| Lit window (far) | black | 0.5 | emission (1.0, 0.55, 0.25) strength 0.9 |
| Cool window | black | 0.5 | emission (0.55, 0.75, 1.0) strength 1.6 |
| Lamp bulb | black | — | emission (1.0, 0.75, 0.45) strength 25 |
| Striped fabric | Wave texture BANDS scale 3.5 → constant ramp | 0.6 | e.g. red (0.55, 0.04, 0.05) / cream (0.85, 0.78, 0.62) |
| Character plastics | saturated colour | 0.25–0.32 | coat weight 0.6–0.8 (wet toy sheen) |
| Character skin | warm tan (0.80, 0.50, 0.33) | 0.55 | matte |
| Eye white / pupil | (0.92, 0.92, 0.9) / near black | 0.15 / 0.1 | |
| Rain | (0.7, 0.8, 1.0) | 0.1 | emission (0.6, 0.72, 0.95) 1.5, alpha 0.45, casts no shadow |

Edge softness: every character part has Subdivision Surface level 1–2 and smooth shading. Hard props get a bevel of 0.01–0.02 m with 2 segments. No razor edges.

## 3.5 Character construction standard (applies to every new design; Pip shows the build quality only)

- **Hierarchy:** root empty (position + yaw) → body empty (hip 0.42 m; bob, lean, squash) → neck empty (+0.42; head rotation) → head, nose, mouth, brows, eye lid-scale empties → eye pivot → pupil; hat pivot (overlap). Shoulder empties (±0.24, +0.30 from hip) → arm + mitten (+ held prop).
- **Parenting rule:** set each child's location relative to its parent. If you parent while keeping the world transform, call `view_layer.update()` first, because fresh objects have stale matrices.
- **Proportions:** head about 40 % of body height; head ellipsoid (0.25, 0.235, 0.23); eyes (0.062, 0.05, 0.072) at ±0.085 m, sitting 0.025 m proud of the face; wide signature silhouette item (P01: hat brim r 0.33 m).
- **Readability test:** the silhouette must read at 360 px frame width.
- **Legs:** posed in world space every frame from hip to planted foot (cylinder stretched along the hip→ankle vector); boots placed on plants. Upgrade for better quality: a 2-bone IK armature for knee bend (the P01 scorecard asks for this).
- **New characters:** every project's characters are new designs from the Variety Engine (Section 3A). What stays constant is the build quality: subdivided forms, believable materials, readable faces with eye pivots, brows and a mouth, the pivot hierarchy, planted feet and the acting rules. Shapes, species, materials, palettes and gaits change every time.
- **Non-humanoids:** four-legged characters use 4 plant lists with diagonal gait pairs. Hovering characters get bob and drift with no plants, plus a soft contact shadow. Living objects get squash-and-stretch on their whole body and a face on their main surface.
- **Character modules:** build each character as tools/p3d/characters/<project>_<name>.py. It exposes build(seed, variant) and a pose API (root, body, neck, eyes, mouth, brows, arms, plants), so the same animation code drives every design.

## 3.6 Animation standard (procedural, every frame keyed)

| Element | Value |
|---|---|
| Walk cadence | step every 8 frames (3 steps/s) |
| Foot plants | list of (contact frame, foot, world position, yaw). A foot lifts at next_contact − min(8, gap); swing is smoothstep with lift 0.075 m (0.04 for shuffles) and toe pitch 18° |
| Speed | integrate a speed profile so the body lands exactly on its mark; ease out over about 16 frames |
| Lead | foot lands 0.15 × speed ahead of the body |
| Bob | −0.022 m × cos(phase) × speed; lowest on contact |
| Squash | 3.5 % on contact, volume preserved |
| Lean | 7° forward × speed; on stopping, overshoot then settle (decaying sine, τ = 5 frames) |
| Anticipation | 0.035 m dip over 6 frames before a big head or body move |
| Turn | body yaw eased over about 14 frames; 2–3 small re-plant steps (no sliding pivot) |
| Eyes | lead the head by about 4 frames; up to 22° pitch |
| Head | counter the body lean (−0.6 × lean) so the gaze stays level |
| Overlap | hat (or hair, ears) = 0.6 × (head rotation 3 frames ago − now) |
| Arms | free arm swings ±28° opposite the same-side leg; the arm holding a prop is near-static |
| Blink | 4 frames: lid scale 0.15, 0.05, 0.4, 0.9 |
| Expressions | mouth scale neutral (0.7, 1, 0.25) → smile (1.15, 1, 1.0) over 8 frames; brows +0.035 m for hope or surprise |
| Event export | write every contact frame, prop event and light flicker to manifests/<shot>_animation_events.json, because sound is timed from this file |

## 3.7 Environment standard

- **A new world every project** comes from the Section 3A environment dice; never rebuild a past set.
- **Three depth layers per shot**, kept in named collections: ENV_near, ENV_mid, ENV_far, CHAR_*, FX_*, LIGHTS, CAMERA.
- **Real interiors** behind any window the camera sees (a back wall, shelves and props about 1.5 m deep), so the window shows parallax.
- **Repetition with variation:** facades with randomized window states (lit warm, cool, dark) from a fixed random seed.
- **Weather systems:** rain sheets (below), snow (slower, 0.03–0.06 m/frame, with sideways drift and round flakes), leaves and petals (spinning instanced cards), dust motes, fireflies (small emissive points with noise paths), and bubbles for underwater. Same looping technique.
- **Rain (when it fits the weather):** two stacked sheets of 900 thin streaks (0.0045 m × 0.16–0.30 m) over a 12 m loop, falling 0.33 m per frame (about 8 m/s), keyed every frame.
- **Ground** stays wet and reflective at night or in rain; for dry scenes use roughness 0.5–0.7 with the same grain bump.
- **Fixed seeds:** `random.seed(7)` for set dressing and numpy seed 11 for audio, so reruns give identical results.

## 3.8 Voice, sound and mix standard

| Element | Value |
|---|---|
| TTS | kokoro-onnx 0.6.1, Kokoro-82M v1.0 int8 ONNX, voice am_michael, speed 1.0, lang en-us, 24 kHz → resampled to 48 kHz with ffmpeg |
| Supplied VO file | convert to 48 kHz mono WAV and keep the performance; only trim silence and set level |
| Line placement | first line starts at about 0.45 s; a line must END before its visual payoff |
| Phrase timing | energy envelope, 10 ms hop, gate −38 dBFS, a gap of 120 ms or more splits phrases; segments under 50 ms are dropped |
| Rain bed | stereo noise, 250–9000 Hz, −2.5 dB/oct tilt, −14 dB; 220 droplet ticks at −34 to −22 dB, random pan |
| Room tone | 60 + 120 Hz hum at −38 dB, rising as the camera approaches the source |
| Footsteps | thud (95 Hz) + slap (0.9–6 kHz) + splash (2.5–11 kHz) at each contact frame; gain by distance (−14 dB far → −4 dB near); shuffles −5 dB |
| Cloth | band-passed noise (1.2–8 kHz) at −30 dB over turns |
| Prop / light FX | buzz from 120 Hz harmonics gated by the light's keyed intensity; a click on each turn-on |
| Music sting | additive synth arpeggio (e.g. C–E–G–C) at −24 dB on the payoff frame; original |
| Mix | dialogue −3 dB after peak-normalising the line to −1 dBFS; ambience ducked −6 dB under dialogue; 0.15 s fade in, 0.2 s fade out |
| Loudness | measured with ffmpeg ebur128; gain to −16 LUFS integrated; true peak ≤ −1 dBTP |
| Stems | dialogue, ambience, foley, fx, music, mix as 24-bit WAV; rights logged in assets/audio_licenses.csv |

## 3.9 Captions and assembly

- Remotion 4.0.543 with React 19.1.1. The composition's fps, width, height and duration are read from the shot manifest.
- Frames come in as an `<Img>` PNG sequence via `staticFile` (frame + frame_in offset). Audio is `<Audio>` of mix.wav.
- Captions: phrase-level, cream #fff8ec, 700 weight, 30 px at 540 px width (scale with width), 1 px dark stroke, shadow 0 2px 0 / 0 0 12px. They fade in over 0.08 s, and their position is chosen per shot so they never cover a face. P01 used 18 % from the top.
- Encode: h264 CRF 18 + AAC, using the browser at `/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell`.
- The validator copies the media and fails on missing frames, wrong size, near-empty PNGs, or audio/video drift of more than 1 frame.

# 3A. The Variety Engine (a new cast and world every video)

The quality lock (Section 3) fixes *how well* things are made. The Variety Engine decides *what* gets made, and makes it different every time. It runs in Stage 1B, before any modelling.

## 3A.1 Project seed and registry

- Every project gets a `VARIETY_SEED`. If the form says AUTO, Claude derives it from the project ID and date. All design dice below are rolled from this seed, so a rerun of the same project gives the same designs, and a new project gives new ones.
- The registry lives in `registry/characters.json` and `registry/environments.json`. Each entry stores the project ID, the rolled axes, the palette hex codes and a thumbnail path.
- **No-repeat rule:** a new character may not match a past character on 3 or more of: archetype, body shape, head shape, primary colour family, signature feature. A new environment may not match a past one on 3 or more of: setting, era, time of day, weather, palette family, architecture style. Re-roll the matching axes until the design is clear of the registry.
- **Within a video:** no two characters may share both body shape and primary colour family, and every character needs a different signature feature.
- **Never reused:** Pip and the P01 street set are reference only.

## 3A.2 Character dice (roll each axis per character)

| Axis | Options (examples; Claude may invent more in the same spirit) |
|---|---|
| Archetype | human kid, adult, elder; animal-person (fox, frog, owl, bear, axolotl, pangolin, crab...); creature (blob, moth-folk, mushroom-folk, cloud sprite); robot or automaton; living object (teapot, lamp, cactus, sneaker, mailbox); plant or mineral being |
| Body shape | egg, pear, bean, tall noodle, square block, triangle (broad shoulders), round ball, long-torso-short-legs, tiny-body-giant-head |
| Height | 0.4–2.2 m (vary it inside a cast: mix tiny, mid and tall) |
| Head shape | sphere, wide oval, tall capsule, flat-top, heart, pointed, boxy, droplet |
| Eyes | big round, sleepy half-lid, button dots, wide-set, single cyclops, visor/LED, goggles, lashes |
| Mouth | arc, wide smile, small o, beak, snout, grille, none (expressive brows instead) |
| Signature feature | hat style, hair silhouette (bun, mohawk, curls, braids), ears, antenna, tail, horns, scarf, backpack, glasses, cape, apron, oversized boots, glowing core |
| Palette | pick from a harmony (complementary, split-complementary, triadic, analogous plus one accent). Each character's primary hue must be at least 40° from every other cast member's on the colour wheel |
| Surface | clear-coat plastic, soft felt or velvet (sheen), knitted, ceramic glaze, brushed metal, rubber, fuzzy (fur with a short hair system or noise bump) |
| Gait and acting | bouncy, shuffling, stomping, gliding/hovering, tiptoe, waddle, march, slinky. This sets step length, cadence (6–12 frames), bob height and squash |
| Props | job- or story-based (umbrella, toolbox, basket, kite, instrument, lantern, phone, skateboard...) |

How many characters: by default use **CAST_SIZE = MAX**. That means every speaking role, at least 2 supporting characters wherever the story allows, and background extras in any public setting (streets, markets, parks, schools). The working ceiling is about 3 hero-detail characters plus up to 12 extras per shot.

Extras are real 3D characters made from the same dice but cheaper. They use subdivision level 1, no blink or mouth shapes, and simple looping walk or idle cycles with offset phases. They sit in the mid and far layers to fill the world and add parallax.

## 3A.3 Environment dice (roll per project; vary per shot within it)

| Axis | Options (examples) |
|---|---|
| Setting | rooftop garden, floating market, desert outpost, harbour pier, mountain train, snowy village, underwater dome, greenhouse, night bazaar, school corridor, subway car, laundromat, lighthouse, treehouse town, space-station galley, canyon diner, rice terraces, carnival, library tower, swamp boardwalk |
| Era / style | contemporary, retro 1950s, art deco, futuristic, solarpunk, medieval-fantasy, steampunk-light, folk-tale, mid-century modern, brutalist, coastal cottage |
| Time of day | dawn, golden morning, noon, overcast afternoon, golden hour, blue hour, night, midnight |
| Weather / atmosphere | clear, rain, drizzle and mist, fog, snow, wind with leaves, dust haze, heat shimmer, underwater caustics, falling petals, fireflies |
| Palette family | warm earth, pastel candy, teal-and-orange, monochrome plus one accent, jewel tones, desaturated cool plus neon, sun-bleached, forest greens |
| Architecture / shapes | round and soft, tall and narrow, wide and low, stacked and crooked, geometric, organic grown, nautical |
| Set dressing density | sparse (minimal and graphic) to dense (cluttered, lived-in). Always include story props |
| Signature set piece | one unforgettable element per world: a giant clock, a whale-shaped bus, a lantern tree, a waterfall stair, a neon koi sign |
| Camera language | per shot, vary among lateral truck, push-in past a near object, crane up/down, orbit, low tracking follow, over-the-shoulder reveal, high-angle drift. Never use the same move twice in a row |
| Sound bed | matched procedurally: rain, wind, surf, birds, insects, crowd murmur, traffic, machine hum, room tone, water drips, fire crackle |

Within a multi-shot video, the world stays coherent (same seed and palette family) but every shot changes at least two of: location within the world, camera move, lighting angle, weather intensity, and which characters are present.

## 3A.4 Lighting recipe library (the quality ratios stay; the look changes)

Every recipe keeps the locked ratio of key 1 : rim about 0.7 : fill about 0.15, plus visible practicals.

| Recipe | Key | Rim | Fill / world | Atmosphere |
|---|---|---|---|---|
| Night rain (P01) | warm window area | cool blue | dark blue gradient | far volume, rain sheets |
| Golden hour | low Sun 3–5 strength, warm (1.0, 0.7, 0.45) | sky bounce, cool | peach-to-blue gradient | light dust haze |
| Overcast | large soft area overhead | faint | grey-blue gradient, strength 0.8 | mist |
| Noon | Sun 5–7, near white | strong top light | bright blue sky | none or heat shimmer |
| Blue hour | practicals only, warm | deep blue sky | blue gradient | low fog |
| Interior tungsten | warm practical lamps | cool window light | dark | dust motes |
| Neon night | coloured emissive signs as keys | contrasting neon | near black | wet ground and haze |
| Snow day | cool soft sun | bright bounce off snow | pale sky | falling snow particles |
| Underwater | sun shafts through a volume | caustic projector | teal gradient | dense volume, bubbles |
| Forest dappled | sun through leaf gobo | green bounce | sky through the canopy | god rays |

Every new recipe goes through the Stage 5 lookdev gate and Stage 6 benchmark, because render times change with sun, volume and particles.

# 4. Stage prompts (Claude follows these; you can also paste any one on its own)

## Stage 0: Environment check

```
Stage 0. Verify the toolchain before building anything: python3 (3.13), a venv
with tools/requirements.txt (bpy 5.3.0, kokoro-onnx 0.6.1, onnxruntime, soundfile,
numpy), Kokoro model files (kokoro-v1.0.int8.onnx + voices-v1.0.bin from the
GitHub release thewh1teagle/kokoro-onnx model-files-v1.0, since HuggingFace may be
blocked), ffmpeg, node, remotion/ npm ci, and the Chromium headless shell. Run
python tools/check_blender.py renders/smoke and report the version, engines, GPU
devices and seconds/frame. Confirm the requested voice is in
Kokoro.get_voices(). Update docs/environment_audit.md only if something changed.
```

## Stage 1: Script breakdown and shot manifest

```
Stage 1. Turn my INPUT FORM into manifests/<PROJECT>_shots.json: one entry per
shot that validates against manifests/shot_schema.json. For each shot, write: id
(S01...), location, the character action broken into beats with frame ranges,
the VO line, the visual payoff and the frame it lands on, the camera plan (start /
mid / end positions, lenses, the near-layer object it passes, the end framing),
near/mid/far layer lists, the lighting recipe variant, audio cues, and caption
placement. Use placeholder frame counts for now; Stage 2 sets the real
durations from the audio. Write docs/decisions_<PROJECT>.md listing every
creative choice you made that I did not specify.
```

## Stage 1B: Variety Engine (new cast and new world)

```
Stage 1B. Run the Variety Engine (prompt book section 3A). Set VARIETY_SEED
(from the form, or derive it from PROJECT_ID + date). Roll the environment dice for the
project and the character dice for every role. Make CAST_SIZE as large as the
story can stage well (leads + supporting + extras), unless the form gives a
number. Keep every detail I wrote in the form and roll only what I left open. Check
registry/characters.json and registry/environments.json: re-roll any design
matching a past entry on 3+ axes, and make sure that within this video no two
characters share body shape + colour family and every hue is 40+ degrees apart.
Write docs/cast_<PROJECT>.md (per character: name, role, archetype, shape,
height, palette hex codes, materials, signature feature, gait, acting notes) and
docs/world_<PROJECT>.md (setting, era, time, weather, palette, architecture,
signature set piece, lighting recipe from section 3A.4, sound bed, and the
camera move per shot). Add the entries to the registry, marked "pending" until delivery.
```

## Stage 2: Voice first (timing comes from audio)

```
Stage 2. Build the dialogue before the animation. If VOICEOVER is TEXT,
synthesize each shot's line with Kokoro (voice and speed from the form). If it is
a FILE, convert it to 48 kHz mono WAV and split it into per-shot lines by measured
silences (gate -38 dBFS, gap >= 120 ms), matching my script text in order.
Save assets/audio/<PROJECT>/<shot>_line.wav. Measure each duration and its
phrase boundaries. Set each shot's length to: 0.45 s pre-roll + line duration +
at least 1.0 s for the visual payoff and hold, rounded up to whole frames at
24 fps. Shots should be 4-7 s. Update the manifest with the real frame ranges
and write manifests/<PROJECT>_audio_timing.json.
```

## Stage 3: Characters

```
Stage 3. Build every character from docs/cast_<PROJECT>.md as a NEW module
(tools/p3d/characters/<PROJECT>_<name>.py) following the quality lock section 3.5: rounded subdivided primitives, a
clear-coat material palette, empties hierarchy (root -> body -> neck -> head
parts, eye lid-scale -> eye pivot -> pupil, hat/hair pivot for overlap,
shoulders -> arms -> hands -> props), and legs/feet solved in world space from
foot plants (or the 4-leg / hover variants). Build extras as cheaper variants
(subdivision 1, loop cycles, offset phases). Never import Pip or any past
project's character. Render a CAST LINE-UP still (all characters side by side,
front and 3/4) plus a black-silhouette version at 360 px wide. Every character
must be distinguishable in silhouette alone, and eyes, mouth and brows must sit on
the face surface. Re-roll or redesign any character that fails.
```

## Stage 4: Sets, lighting and camera

```
Stage 4. Build the NEW world from docs/world_<PROJECT>.md in
tools/p3d/sets/<PROJECT>_<location>.py using quality lock sections 3.3, 3.4,
3.7 and the 3A.4 lighting recipe. Include the signature set piece, set dressing
at the rolled density, extras placed in the mid/far layers, and the weather system: named depth-layer collections, at least one
near object on the camera path, a real interior behind any visible window,
motivated warm key + cool rim + low fill, practicals, a world gradient, and a
far-only volume for haze. Animate the performance procedurally per section 3.6,
and export manifests/<shot>_animation_events.json (contacts, prop events, light
keys, beats, camera keys). Camera per section 3.2: a 3-key Bezier path past the
near object, Track To a damped target, DOF on the head, ending on a 3/4 front
view with the payoff in frame. Save renders/<PROJECT>/<shot>/scene.blend.
```

## Stage 5: Lookdev gate (stills before any long render)

```
Stage 5. For each shot, render 5 stills at 360x640, 16 samples: first frame,
mid-action, just before the payoff, the payoff, and the last frame. Combine
them into one contact sheet and look at it yourself first. Fix any of these
before showing me: missing or floating face parts; a face turned away at the
payoff; a payoff object cropped or hidden behind set pieces (check the line of
sight through window frames and pillars); blown-out windows (hide area lights
from camera, glossy and transmission rays); a near object covering the face for
more than about 12 frames; and a flat composition with no near layer. Then
run tools/qc_<shot>.py: parallax ratio > 3, foot slide < 2 mm, boot contact
between -5 and +8 mm. Also check variety: the cast line-up and world stills must not resemble any
registry thumbnail. Show me the contact sheets, cast line-up and metrics, and wait
for my OK unless the form says AUTO-APPROVE.
```

## Stage 6: Benchmark and budget

```
Stage 6. Render 2 frames per shot at PROOF_RES with 24 samples and record
seconds/frame. Use the most crowded frame of each shot, since extras and weather add cost. Estimate total hours = sum(frames x s/frame). Write
docs/render_budget_<PROJECT>.md. If the total exceeds MAX_RENDER_HOURS, stop
and offer options: fewer samples (no lower than 16), smaller proof resolution,
shorter shots, splitting into batches, or GPU compute.
```

## Stage 7: Full render

```
Stage 7. Render every shot's frames to renders/<PROJECT>/<shot>/frames/####.png
in the background with the restart-safe builder (it skips existing frames).
Log seconds per frame to render_timings.json. Do not stop for routine
progress; check every 30 frames for errors. If a shot fails visually, delete
only the affected frames, fix the scene, and render those frames again.
```

## Stage 8: Sound

```
Stage 8. Generate the stems per quality lock section 3.8 from the animation events:
rain/ambience bed suited to the location (swap rain for wind, birds, traffic, room
tone as the setting demands, all procedural), footsteps on contact frames with a
surface-appropriate tone, cloth on turns, FX on prop events, an optional original
sting on the payoff. Duck ambience -6 dB under dialogue. Normalize the mix
to -16 LUFS integrated with true peak <= -1 dBTP, and verify both with ebur128.
Log every sound's source and rights in assets/audio_licenses.csv.
```

## Stage 9: Remotion assembly

```
Stage 9. Extend remotion/ into a multi-shot composition driven by
manifests/<PROJECT>_shots.json: a <Series> of shots, each an <Img> sequence,
with one continuous mix (or per-shot audio in <Sequence>). Hard cuts by
default; at most a 6-frame cross-dissolve where the script implies a time
jump. Phrase captions come from the measured timings, positioned per shot
so they avoid faces. Extend the validator to every shot and run it. Render
out/<PROJECT>.mp4 at h264 CRF 18. Also export a still contact sheet (every
12th frame).
```

## Stage 10: QC, scorecard and delivery

```
Stage 10. Verify the final file: ffprobe frame count, duration and fps; ebur128
LUFS and true peak; blackdetect for blank segments; A/V drift < 1 frame. Then score each shot
1-5 on character consistency, silhouette, motion mechanics, genuine parallax,
composition, lighting, materials, environment detail, sound sync,
storytelling clarity and variety (new vs. the registry, distinct cast), with a one-line reason for each. State that the
scores are your own review from stills. Name what was not checked
(real-time playback, human listening). Any score below 4 means listing the
concrete fixes and asking me whether to apply them. Change this project's
registry entries from "pending" to "shipped". Commit and push. Give me the MP4,
the contact sheet, and a short summary.
```

# 5. Fix-it prompts (problems already hit and solved)

Paste the matching prompt if any of these come up.

```
FIX - "No module named bmesh":
Import bpy before bmesh in every script (bpy registers bmesh). Keep
"import bpy" above "import bmesh".
```

```
FIX - character parts float or eyes disappear:
Parenting used stale matrix_world values. For each child, either set the
location in the parent's local space, or call bpy.context.view_layer.update()
before setting matrix_parent_inverse. Empties created with a parent must
use local offsets (e.g. neck (0,0,0.42) under the body, not world height). Re-
render one still to confirm.
```

```
FIX - a window or soft light shows as a white rectangle / washed glass:
Set visible_camera = False on all area lights. For lights in front of glass, also
set visible_glossy = False and visible_transmission = False. Lower the interior
light (P01: 18 W) and darken the interior wall so the shelves read.
```

```
FIX - the character faces away at the payoff:
Move the camera's end position onto the side the character turns toward
(P01 moved the camera onto the sidewalk next to the facade), widen the lens
(26 mm), and if needed reduce the body turn and let the head and eyes do the
rest. Target: the face at least 3/4 to camera on the payoff frame.
```

```
FIX - the payoff object (sign, door, prop) is cropped or occluded:
Ray-check the line of sight from the end camera position through window
openings, pillars and frames. Move the object toward the frame centre or
along the facade until it is fully visible, angle it about 30 degrees toward the
camera, and ease the camera target about 50% toward it during the payoff.
```

```
FIX - EEVEE renders nothing / no GPU:
Use Cycles CPU (the cloud container has no GPU or GL context). Keep the
24 spp + OIDN settings; budget about 31 s/frame at 540x960 on 4 vCPU.
```

```
FIX - HuggingFace / blender.org downloads blocked (403):
Install Blender with `pip install bpy==5.3.0`. Get the Kokoro files from the GitHub release
thewh1teagle/kokoro-onnx model-files-v1.0. Record this in the audit.
```

```
FIX - QC reports foot sliding during turn steps:
Check the QC stance window first. A foot's stance ends at its own lift-off
(next_own_contact - min(8, gap)), not when the other foot lands. Only change
the animation if the slide is still there after correcting the window.
```

```
FIX - foreground object covers the character too long:
Allow at most about 12 frames of face/body occlusion. Move the object 0.3 m off the
camera line, or adjust the camera's middle key in height or lateral position.
```

```
FIX - legs look stiff (motion mechanics below 4):
Replace the stretched-cylinder legs with a 2-bone armature per leg and an IK
constraint targeting the planted foot, pole target forward, with knee bend
increasing during swing. Re-run the foot-slide QC.
```

```
FIX - environment feels empty (environment detail below 4):
Add puddle ripple rings at random positions, timed to the rain (procedural
ring texture animated by frame), drips from the awning or brim edges, small litter
or leaves on the ground, signage or posters on the mid facades, and window
interiors with silhouetted props. Keep the extra cost under 20% per frame.
```

```
FIX - the new video looks too similar to a past one:
Compare the cast line-up and world stills against the registry thumbnails.
Re-roll at least 3 environment axes (setting, time of day, palette family
or architecture) and every character whose archetype, shape or colour family
repeats. Change the camera language and the lighting recipe too. Update the
registry and re-run the lookdev gate.
```

```
FIX - characters in the cast look alike:
Run the squint test: render the line-up as black silhouettes at 360 px. For any
pair that is hard to tell apart, change body shape (egg vs. noodle vs. block),
height class (tiny / mid / tall), and the signature feature, and push their hues
at least 40 degrees apart. Repeat until every silhouette is unique.
```

```
FIX - crowd shots render too slowly:
Lower subdivision to 0 on far extras, use instanced linked duplicates for
repeated props, hide extras outside the camera frustum per frame, and cap
hero-detail characters at 3. Re-run the benchmark.
```

```
FIX - voiceover runs over the payoff:
Lengthen the shot (preferred), start the line earlier (not before 0.25 s), or
re-synthesize at speed 1.05-1.1. Never cut words. Remeasure and update the manifest.
```

# 6. Quick reference

## 6.1 Repository map

| Path | What it is |
|---|---|
| registry/characters.json, registry/environments.json | Every past design, so new videos never repeat (created on the first project) |
| docs/cast_<PROJECT>.md, docs/world_<PROJECT>.md | This video's unique cast and world sheets |
| tools/check_blender.py | Smoke test: version, engines, GPU, 12-frame render |
| tools/build_proof_scene.py | P01 reference implementation: materials, Pip, street set, animation, camera, render loop |
| tools/make_audio.py | Kokoro dialogue + procedural ambience/Foley/FX/sting + ducking + LUFS normalisation |
| tools/qc_p01.py | Parallax ratio, foot slide, ground contact from the .blend |
| manifests/shot_schema.json | JSON schema for every shot entry |
| manifests/p01_*.json | Example shot, animation events and audio timing |
| remotion/ | Assembly: P01.tsx, shot.ts, validate-media.mjs; npm run render |
| docs/style_bible.md | Full look spec for the "Last Stop" world |
| docs/render_budget.md / qc_scorecard_p01.md | Measured costs and the reference scorecard |

## 6.2 Commands

```
python3 -m venv .venv && . .venv/bin/activate && pip install -r tools/requirements.txt
python tools/check_blender.py renders/smoke
python tools/build_proof_scene.py --out renders/proof_v1 --res 360x640 --samples 16 --stills 1,45,75,95,120
python tools/build_proof_scene.py --out renders/proof_v1 --res 540x960 --samples 24
python tools/make_audio.py --kokoro-model .models/kokoro-v1.0.int8.onnx --kokoro-voices .models/voices-v1.0.bin
python tools/qc_p01.py renders/proof_v1/proof_scene.blend
cd remotion && npm ci && REMOTION_BROWSER=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell npm run render
```

## 6.3 Budgets measured in the cloud container (4 vCPU, no GPU)

| Job | Time |
|---|---|
| Lookdev still 360×640, 16 spp | 9–12 s |
| Final frame 540×960, 24 spp | 28–42 s (mean 31.2) |
| 5 s shot (120 frames) | about 62 min |
| 60 s of finished video | about 12.5 h (estimate) |
| 1080×1920 delivery | about 4× slower per frame (estimate) |
| Audio generation (5 s) | under 5 s |
| Remotion assemble + encode (5 s) | about 12 s |

## 6.4 Gate checklist

- [ ] Toolchain verified, voice present in Kokoro.get_voices()
- [ ] Manifest validates against shot_schema.json
- [ ] Variety Engine run: new cast + new world, registry clear, silhouettes distinct, CAST_SIZE as large as the story allows
- [ ] Shot lengths come from measured audio
- [ ] Lookdev contact sheet approved (or AUTO-APPROVE)
- [ ] Parallax > 3, foot slide < 2 mm, contact −5…+8 mm
- [ ] Render estimate within MAX_RENDER_HOURS
- [ ] All frames present, no blank segments, A/V drift < 1 frame
- [ ] −16 LUFS integrated, true peak ≤ −1 dBTP
- [ ] Captions avoid faces; timings measured
- [ ] Scorecard has every category ≥ 4, or the fixes are listed and you have been asked
- [ ] Committed and pushed; MP4 and contact sheet delivered

# 7. Worked example: the P01 input that produced "Last Stop"

This is the QUALITY reference only. Its character (Pip) and street set are in the registry and will never be reused. Your next video gets a different cast and world.

```
TITLE: Last Stop
PROJECT_ID: P01
FORMAT: 9:16 portrait  FPS: 24  DELIVERY: 1080x1920  PROOF_RES: 540x960
VOICEOVER: TEXT (synthesize)
VOICE: am_michael   VOICE_SPEED: 1.0
CAPTIONS: ON   CAPTION_POSITION: AUTO
APPROVAL: AUTO-APPROVE   MAX_RENDER_HOURS: 2

CHARACTERS:
  - NAME: Pip
    LOOK: small round night courier, teal clear-coat raincoat, mustard rain hat
          with wide brim and mittens, red boots, kraft parcel under the right arm
    PERSONALITY / ACTING NOTES: earnest, tired but hopeful; small careful steps

SHOTS:
  SHOT 1
    LOCATION / TIME / WEATHER: city side street, night, steady rain, wet asphalt
    ACTION: Pip walks toward camera along the sidewalk, slows, stops at a
            corner shop, turns toward the window, looks up
    VO: "Last stop tonight... please, still be open."
    VISUAL PAYOFF: the neon OPEN sign in the window flickers on; pink light
                   on Pip's face; Pip smiles
    CAMERA: low lateral truck from the street onto the sidewalk past a lamp
            post and bollard, ending 3/4 front on Pip with the sign in frame
    MOOD / PALETTE: cool blue night, warm shop window, pink neon accent
    SOUND NOTES: rain, wet footsteps, neon buzz, small hopeful chime

STORY RULE: the line asks, the picture answers
```

A next-project form can be as short as this. Everything left blank is generated fresh:

```
TITLE: The Kite Repair Shop
PROJECT_ID: EP02
VOICEOVER: FILE: ep02_vo.wav
CAST: AUTO   CAST_SIZE: MAX
WORLD: AUTO
APPROVAL: WAIT-FOR-ME at lookdev
SHOTS:
  SHOT 1
    ACTION: a customer brings in a torn kite; the shopkeeper studies it
    VO: (0:00-0:04 of the file)
    VISUAL PAYOFF: the shopkeeper grins and pulls out a strange tool
  SHOT 2
    ACTION: the repaired kite lifts off a hill with neighbours watching
    VO: (0:04-0:09 of the file)
    VISUAL PAYOFF: the kite catches the wind and everyone looks up
```

Measured result: 120 frames at 540×960 rendered in 62.4 min. Line spans 0.58–3.10 s, sign turns on at 3.29 s. Parallax ratio 16.8, foot slide 0.0 mm, −16.0 LUFS. Self-scorecard: motion, environment detail and sound at 3/5, with the fixes listed in docs/qc_scorecard_p01.md (also Section 5 above).
