# Prompt Book: THE BLANK LIBRARY (library/)

This book holds everything that produced this Short, so that anyone can make the next one at the same quality from a new voiceover:

- Part 1 is the single prompt that rebuilds an episode.
- Parts 2 to 9 are the rules and the decisions behind it: story, cast, art style, editing, camera, sound, finish and publish.
- Part 10 is a blank template for the next episode.

Nothing here is invented after the fact. Everything is copied from the files that drove the render: `library/scenes.py`, `library/people.py`, `library/sound.py`, `library/render_video.py`, `drongo/render.py` (the shared engine), `drongo/sound/*` and `library/publish/*`.

> **How it was really made:** the voiceover came first, recorded with no script. The words were recovered from the audio by offline forced alignment. The picture was then cut to the voice: every shot starts on a word. The sound was designed around the voice, which is never processed.

---

## 1. The one-paste prompt (reproduces this quality)

Open Claude Code in the `Dart_Bliss` repository, put the new voiceover file in a new episode folder (for example `episodes/<name>/vo.mp3`), and paste:

```
NEW SHORT (2D v1)
Voiceover: episodes/<name>/vo.mp3 (already mastered; do NOT process it)
Script: <paste the exact words read, or write "transcribe it">
Format: YouTube Short, 9:16, final 2K = 1440x2560, 30 fps, H.264 16 Mbit/s, AAC 256k 48 kHz, -14 LUFS

Make the complete Short with the 2D engine in this repo, copying the library/ episode
structure (scenes.py + people.py + sound.py + render_video.py) and following
library/PROMPT_BOOK_blank_library.md, drongo/sound/PRINCIPLES_1000.md,
drongo/sound/SPEC.md and thumbnails/Thumbnail_Retention_Rules_200.md,
without stopping to ask me unless something fails twice.

1. ALIGN: confirm the VO tells the story I described (transcribe it and check), write
   script.txt, run drongo/sound/align.py -> words.json (every word must align).
   Add 1.0 s of tail after the last word for the button and the loop.
2. SHOTS: one shot per phrase, 0.6-3.5 s each (average about 1.8 s), every shot
   starts 0.06 s before its first word. Each shot gets a visual gag that SHOWS its
   key noun (part 5). The camera never stops. Faces stay in the upper 60% of
   the frame (captions sit at 70.5% height).
3. CAST: reference-style stick figures (part 4). Rotate the lead. Render a model sheet first.
4. WORLDS: one place per act; post looks for flashbacks / CCTV / colour isolation.
5. STILLS: render one still per shot at 320x568, review, fix framing, then a
   low-res full preview (render_video.py --ss 0.5 --size 320x568 --fps 15).
6. SOUND: voice-first mix (part 7): music in a key that avoids the VO's pitch,
   SFX on action words and in gaps, silence before the reveal, a button
   >= 300 ms after the last word. Verify: everything else >= 18 dB under the voice
   during speech, >= 20 dB under it in 1-4 kHz, and the limiter never touches the voice.
7. RENDER: render_video.py --ss 2.25 --size 1440x2560 --fps 30 --jobs 4,
   then re-encode the delivery file at 16 Mbit/s.
8. PUBLISH: Gemini thumbnail prompt + 3 reference frames, title, description,
   tags, pinned comment (part 8).
```

### Pipeline commands (run from the episode folder)

| Step | Command | Time |
|---|---|---|
| Word timings | `python3 ../drongo/sound/align.py vo.mp3 script.txt --out words.json` | seconds |
| Model sheet | a short script calling `person()` / props onto one canvas | seconds |
| Stills | `python3 scenes.py /tmp/st --times 0.5,1.8,... --size 320x568` | seconds |
| Low-res preview | `python3 render_video.py --ss 0.5 --size 320x568 --fps 15 --out out/preview_small.mp4` | about 15 s |
| Sound and mix | `python3 sound.py` → `out/library_mix.wav` + `out/stems/` | about 7 s |
| 2K master | `python3 render_video.py --ss 2.25 --size 1440x2560 --fps 30 --jobs 4` | about 7 min |
| Delivery file | `ffmpeg -i master.mp4 -c:v libx264 -preset slow -b:v 16M -maxrate 22M -bufsize 32M -tune animation -c:a copy out.mp4` | about 1 min |

**Requirements:** Python 3 with `pycairo`, `numpy`, `scipy`, `Pillow`, `soundfile`, `pyloudnorm`, `librosa` and `pocketsphinx`, plus `ffmpeg`. Install the fonts Poppins ExtraBold and DejaVu Sans Mono.

---

## 2. Story

**Title:** Don't Read This Book Alone (A/B: The Librarian Who Never Speaks / Who Was Standing Behind Him?)

**Twist:** the blank books never wrote anything. The silent librarian stood behind every reader and whispered their own story to them.

**Voiceover:** 127 words, 35.6 s, about 214 words per minute. It's a dense, punchy read with almost no gaps longer than 0.4 s.

**Story shape:** hook (impossible place) → rules of the place (no windows, no signs, a silent librarian) → what you do there (pick, sit, read nothing) → re-hook ("But here's the strange part") → proof (people walk out with stories) → one emotional case (a crying man, his father, the colour of the car) → investigation (scientists hide a camera) → evidence (three hours, empty pages) → reveal (the librarian behind every reader, whispering) → question to the viewer ("Would you open the book?"), which loops back into the hook.

| # | Shot | Time (s) | Line | Visual gag (shows the key noun) |
|---|---|---|---|---|
| 1 | exterior | 0.00–1.09 | There's a library in Norway | aurora, snowy fjords, a windowless stone monolith, a tiny queue |
| 2 | blank_book | 1.09–2.54 | where every book is blank, | top-down open book; a blank page turns over by itself |
| 3 | queue | 2.54–4.47 | and people wait years to get inside. | long queue in the snow; snow piles on heads, one beard grows; calendar pages fly away |
| 4 | facade | 4.47–6.61 | The building has no windows, no signs, | ghost window outlines flash and get crossed out in red; an empty plaque with "?" |
| 5 | librarian | 6.61–8.63 | and only one librarian who never speaks. | the librarian at her desk; an empty speech bubble "..." pops up and away |
| 6 | shelves | 8.63–9.25 | You pick a shelf, | the reader looks up between tall shelves |
| 7 | pick_book | 9.25–9.91 | you pick a book, | close-up: a hand slides one purple book out |
| 8 | read_nothing | 9.91–11.60 | and you sit down to read nothing. | the reader flips blank pages, confused; a "?" pops up |
| 9 | strange | 11.60–13.35 | But here's the strange part. | dark re-hook: the librarian in the shadows slowly turns toward camera |
| 10 | walk_out | 13.35–16.70 | Everyone who walks out swears the pages told them a story. | amazed readers walk out of the glowing door hugging books; glowing words float up |
| 11 | their_story | 16.70–19.79 | Their story, with names and places nobody else could know. | handwriting writes itself across the pages; a house sketch appears |
| 12 | crying | 19.79–20.82 | One man left crying | a crying man walks out into the snow clutching his book |
| 13 | flashback | 20.82–23.39 | because the book described the night his father disappeared, | blue-night duotone, rain, a streetlamp; the father walks to the car and fades |
| 14 | car_colour | 23.39–24.89 | down to the color of the car. | everything grey except the car, which bleeds back to RED |
| 15 | hide_camera | 24.89–26.69 | So scientists hid a camera. | two scientists ("shh"); a CCTV camera slides onto the shelf, REC blinks |
| 16 | cctv_hours | 26.69–29.34 | For three hours, the pages stayed completely empty. | CCTV look; the timestamp races 00:00:00 → 03:00:00 |
| 17 | monitor | 29.34–30.85 | When they played the footage back, | dark room, scientists' backs, a screen with rewind streaks |
| 18 | reveal | 30.85–33.79 | the librarian was standing behind every reader, whispering. | PLAYBACK CCTV: a librarian ghost behind every reader, leaning to whisper; glitches |
| 19 | be_honest | 33.79–34.37 | So, be honest. | the librarian, eye contact, finger to her lips |
| 20 | open_book | 34.37–36.60 | Would you open the book? | a closed book opens toward camera, light pours out (1 s tail for the button) |

---

## 3. Cast (`library/people.py`)

Each character has one dominant hue, a signature hair or hat, and a prop.

| Who | Role | Look |
|---|---|---|
| **Reader** (hero) | the visitor; carries the audience's point of view | orange sweater, brown bowl-cut hair |
| **Librarian** (threat) | silent, calm, never speaks | 1.35× taller, pale grey-white head, grey hair bun, round glasses, small half-lidded eyes, long charcoal coat to the shins, cool blue rim light |
| **Crying man** | the emotional case | slate-blue sweater, side-parted hair, tear streams, wobbly mouth, hugs his book |
| **Father** | flashback | grey sweater, short beard; fades out like a ghost |
| **Scientists ×2** | the investigation | white lab coats with pocket pens, glasses, one side-part and one messy hair |
| **Queue / walkers** | crowd | spine colours, red beanies, yellow scarves, one grows a grey beard |

**Expression set:** flat, smile, frown, o, wobble, grin, whisper and scream; for brows: worried, angry, raised and shock; for eyes: normal, wide, small and huge; plus blink, lid (heavy lids), tears, sweat drops and underlight (a face lit from below).

**Arm poses:** down, read, hug, reach, shh, whisper, face, sneak, up and cheeks.

**Legs:** stand, walking (`step` phase) and sit.

**Props:** open book (blank or writing itself, with glow and a page flip), closed book (hinged lid that opens, light pours out), car, CCTV camera (REC light), banker's lamp, bookshelf (procedural spines, a book that can be pulled out), table, desk, streetlamp, calendar pages and speech bubble.

---

## 4. Art style (matches the reference Shorts)

- **Heads:** big rounded-oval white heads (100 units wide, about 115 tall), with a 5.2-unit black ink outline.
- **Eyes:** two large white discs touching each other, a black outline and a dot pupil with one highlight. Huge eyes are 22 units with a 3-unit pupil.
- **Bodies and limbs:** pill-shaped coloured bodies; thin black stick arms and legs with round ends; small black oval feet.
- **Shading:** painterly, 2–3 value steps.
  - A gradient fill lit from the upper-left, with a soft core shadow on the lower-right.
  - Bounce light on the shadow edge, and ambient occlusion where shapes meet.
  - A lit rim (a shifted outline clipped inside the shape).
  - A soft contact shadow under the feet. Eye whites carry a small spherical shade.
- **Backgrounds:** softer, with thinner outlines and colour depth (gradients, haze), plus depth-of-field blur on the far layers. Characters always pop.
- **Worlds:** a night exterior (an aurora sky, stars, layered fjords with snow caps, snow ground with drifts, falling snow), a warm library interior (dark wood panelling, procedural shelves, lamp-light pools, dust motes), a rainy night street, and a dark monitor room.
- **Post looks:**
  - **CCTV:** a green mono tint, scanlines, noise, a lens vignette, corner brackets, a REC dot, a timestamp, and optional glitch tears.
  - **Flashback:** a blue-night duotone with an edge vignette.
  - **Colour isolation:** keep only saturated reds.
- **Grade for every shot:** a radial vignette (0.45–0.75), an optional tint, a warm glow, plus film grain added to every frame.

---

## 5. Editing style and camera

### The editing rules

1. **Cut on the word.** Every shot starts 0.06 s before its first word, so the picture leads the voice.
2. **One phrase = one shot.** Shots run 0.6–3.5 s, averaging 1.8 s. The quick shots ("You pick a shelf," / "you pick a book,") are 0.6 s each.
3. **Show the noun.** Every key noun gets a visual gag that pops in on that exact word: years → calendar pages, windows → crossed-out outlines, never speaks → an empty bubble, nothing → "?", three hours → a racing timestamp, color → red bleeding back.
4. **The camera never stops.** Every shot has a push, tilt, truck, crash-zoom or slow rotate.
5. **The re-hook goes dark.** "But here's the strange part" drops the light (vignette 0.65 plus a cold tint) and the threat slowly turns.
6. **The reveal reuses the evidence shot.** The same CCTV framing returns, now with the librarian behind every reader. The viewer compares the two shots without being told to.
7. **End on a question to the viewer, and leave a 1 s tail** so the button lands and the loop restarts cleanly.
8. **Keep faces clear of the captions.** Captions sit at 70.5% of the frame height, so faces stay in the upper 30–60%.

### Camera grammar used

| Move | How | Used on |
|---|---|---|
| Tilt-down reveal | camera height eases from the sky to the subject | exterior (aurora → building) |
| Slow push | zoom +10–25% over the shot, ease in-out | librarian, reading, crying, CCTV |
| Truck along a line | x moves linearly | queue |
| Tilt up a wall | y eases up | facade |
| Slow rotate | rotation −0.06 → +0.02 rad | blank book |
| Dolly toward the threat | x and zoom ease toward the librarian | strange (re-hook) |
| Push into the screen | ease-in zoom 1.4 → 2.1 | monitor |
| Three-key push | wide → threat → close-up | reveal |
| Parallax | far layers move and zoom less (sky 0, mountains 0.2, shelves 0.4–0.7) | every exterior and interior |
| Depth of field | per-layer Gaussian blur (background 3–8 units) | interiors, close-ups |

---

## 6. Captions

- **Font:** Poppins ExtraBold, 50 px on the 640-wide logical canvas (112 px at 2K).
- **Fill and outline:** white fill with a 9 px black stroke, plus a soft drop shadow (12 px at 35% black, offset 2 px right and 4 px down).
- **Timing:** one word at a time, from the word's start to the next word (at most 0.9 s on screen). Punctuation is kept.
- **Animation:** a back-out pop from 82% to 100% scale over 90 ms.
- **Position:** centred horizontally, at 70.5% of the frame height.

---

## 7. Sound (`library/sound.py`, `drongo/sound/*`)

### The voice comes first. These rules never change.

- **Voice:** a supplied mastered VO (−14.2 LUFS, −2.7 dBFS peak) is NOT processed: no EQ, compression or de-essing. It's only resampled to 48 kHz with the soxr resampler and given one static gain in the final normalisation (−2.7 dB).
- **Music under speech:** low-passed at 1.8 kHz and ducked 13 dB. Ducking starts 150 ms before the line, with 80 ms attack and 450 ms release, and holds through gaps under 400 ms.
- **SFX under speech:** low-passed at 3.5 kHz and ducked 8 dB. Gap hits (booms, stings, whispers) duck 10 dB as soon as words return, so their tails never sit on the voice.
- **Ambience:** 28 dB down, high-passed at 80 Hz, a further 8 dB under speech. It is never true silence.

### Verified mix

| Measure | Result |
|---|---|
| Integrated loudness | −14.0 LUFS |
| Peak | −2.3 dBFS after AAC |
| Everything else vs the voice, during speech | 20.7 dB below |
| Same, in the 1–4 kHz consonant band | 22.8 dB below |
| Worst one-second window | 12.5 dB below |
| Bed in gaps | about 10 dB under speech level |
| Limiter | never touches the voice |

### Music by act

The key is D minor at 76 BPM. It sits away from the voice's ~117 Hz fundamental, and there's no sustained A2/A3.

| From line | Music |
|---|---|
| hook | low D drone + a 4-note music-box motif on frame one (D5 F5 A5 G5) |
| facade → reading | clock-tick pulse + a low pizzicato ostinato; music-box notes only in gaps of 0.25 s or more |
| strange | drop-out → reverse swell → low boom in the gap; D + G# tritone pad |
| walk out / their story | lift to B♭ major: a celesta arpeggio + sparkles |
| crying / flashback | G minor, a slow falling music box (D C B♭ A G) |
| scientists | tiptoe pizzicato |
| three hours | ticks accelerating (×0.9 each), tape-forward whir |
| playback | tape rewind, then **silence** (0.5 s fade) before the reveal |
| reveal | glitch + boom + a dissonant cluster (D, D#, G#, A) |
| be honest | the music-box motif alone |
| button | low boom + shimmer + a D-minor celesta chord, 0.32 s after "book?" |

### SFX on action words

| Line | Sounds |
|---|---|
| exterior | wind howl bed |
| blank book | downward whoosh into the shot; a page flip as the page turns |
| queue | snow crunch steps; paper flutter for each calendar page |
| facade | long whoosh up the wall; a muffled thud on the crossed windows; a hollow pop for the plaque |
| librarian | heavy door thud (outside → inside); bubble pop up / pop down |
| shelves / book / sit | wood footsteps, book-slide creak, chair creak, page flip, a "?" pop |
| strange | low heartbeat; a creak as the librarian turns |
| walk out / story | door, snow steps, sparkles |
| flashback | rain bed, low car idle, wet steps; reverse swell + shimmer on "color" |
| hide camera | servo + click + beep from the CCTV |
| CCTV / monitor | 60 Hz hum, tape whir |
| reveal | glitch, boom, a second glitch at 1 s, whisper texture after "whispering" (high-passed above 2.5 kHz so it never masks the voice) |
| ending | low book-cover creak (below 1.2 kHz), button |

**Ambience per space:** wind outside, room tone inside, rain in the flashback, electrical hum on CCTV and in the monitor room.

---

## 8. Publish kit (`library/publish/`)

- **Title:** Don't Read This Book Alone
- **Description:** "Every book in this library is blank… until you're alone with it. 📖 / Would you open the book? / A short animated mystery (fiction). / #shorts #mystery #animation #creepy #storytime"
- **Tags:** mystery shorts, creepy story, animated story, scary library, blank book, short horror story, storytime animation, mystery animation
- **Pinned comment:** "Be honest: would you open the book? 👀"
- **Thumbnail:** the Gemini prompt is in `gemini_thumbnail_prompt.md`, with reference frames `ref1_reader.png`, `ref2_librarian.png` and `ref3_reveal_style.png`. Concept:
  - The hero's shocked face in extreme close-up: huge white eyes, pinprick pupils, a dark gasp mouth, hands on cheeks, sweat drops, eye contact.
  - Lit from below by the glowing blank book, which writes itself.
  - The calm librarian half-hidden in the dark just behind his ear, with cold teal light and one red glint in her glasses.
  - Gold against teal, inside the 9:16 safe box (x 60–940, y 200–1500), with no text.
  - Use the same image as frame 1 for about 0.3 s.

---

## 9. Lessons this episode added

- **Check the VO before anything else.** The first file sent was a different story. Transcribe it and confirm it before building.
- **Score ambiguous words against the audio.** Without the script, test candidate wordings by alignment score (`cand.py` approach). The closest call here was "the pages told them" vs "the book told them". Always ask for the script when you can.
- **Faces collide with captions.** In seven shots the first framing put faces at the 70% caption line. Always check stills for face vs caption position.
- **Booms placed in gaps still ruin the voice** when their tails run 2–3 s. Keep booms ≤ 1.3 s and duck gap hits by 10 dB when speech returns. Measure the bed vs voice for every one-second window.
- **CCTV looks crush the payoff.** Lift the luminance (×1.55 + 28) so the reveal reads.
- **Light rays drawn over a face** wash out the eyes. Rays always go behind the subject.
- **Render time:** 2K takes about 1.5 s per frame on 4 cores, roughly 7 minutes for 36 s. Pipe raw frames to ffmpeg in parallel chunks; don't save 2K PNGs.
- **Size:** the master is 43 Mbit/s (198 MB); the delivery file is 16 Mbit/s (75 MB). Only the delivery file fits on GitHub.

---

## 10. Template for the next episode

```
NEW SHORT (2D v1)
Voiceover: episodes/<name>/vo.mp3      Script: <exact words, or "transcribe it">
Format: YouTube Short 9:16, 2K 1440x2560, 30 fps, -14 LUFS, voice untouched

Follow library/PROMPT_BOOK_blank_library.md, drongo/sound/PRINCIPLES_1000.md and
thumbnails/Thumbnail_Retention_Rules_200.md, without stopping to ask me unless
something fails twice.

1. ALIGN: confirm the VO matches the story; words.json; +1.0 s tail.
2. SHOT LIST: one phrase = one shot (0.6-3.5 s); a visual gag for every key noun;
   re-hook goes dark; the reveal reuses an earlier framing; end on a question.
3. CAST: new cast, rotate the lead (skin, age, body, hue differ from the last 3 heroes);
   one hue + signature hair/hat + a prop each; the threat is taller, calm, cool-lit.
4. WORLDS: one place per act + one post look (flashback / CCTV / colour isolation).
5. CAMERA: never static; push / tilt / truck / rotate / crash-zoom; parallax + DOF;
   faces in the upper 60%; captions at 70.5%.
6. SOUND: key away from the VO pitch; music per act; SFX on action words; hits in gaps;
   silence before the reveal; button >= 300 ms after the last word; verify
   bed >= 18 dB under the voice during speech, >= 20 dB under it in 1-4 kHz.
7. RENDER: stills -> low-res preview -> 2K master -> 16 Mbit/s delivery file.
8. PUBLISH: Gemini thumbnail prompt (9:16, safe zones, no text) + 3 ref frames,
   title < 40 chars that adds the missing half (never describes the image),
   a 3-line description with a fiction note, 8 tags, a pinned question.
```
