# Reference analysis: 9 story Shorts

How these were analyzed: every video was transcribed with word-level timestamps (Whisper small). Each one was cut into timestamped contact sheets at 1 fps, or 2 fps for the 15-second clips, and every sheet was inspected frame by frame. Shot changes were detected with ffmpeg scene scoring. Loudness was measured with EBU R128. Speech rate and the level of the music bed between words were computed from the word timings. Spectrograms were read for music, SFX and stereo content.

File names below are the ones you uploaded. "V1…V9" are used throughout the docs.

---

## The measurements at a glance

| # | Video | Length | Words | WPM while talking | Speech covers | First word | LUFS | Bed vs voice* | Caption style |
|---|---|---|---|---|---|---|---|---|---|
| V1 | 720p (zombies) | 30.1s | 34 | 142 | 50% | 2.0s | -15.3 | -6 dB (SFX-heavy) | none |
| V2 | 720p1 (chickens) | 73.3s | 254 | 263 | 87% | 0.0s | -14.0 | -13 dB | 1-2 words, centre |
| V3 | RicksClips animation (button town) | 60.1s | 226 | 254 | 95% | 0.0s | -14.3 | -11 dB | 1-2 words, centre |
| V4 | Grandma's Secret Recipe | 58.8s | 124 | 207 | 69% | 0.0s | -13.3 | -10 dB | ALL CAPS, lower third, yellow and cyan keywords, emoji |
| V5 | How a Mirror Rigged a Horse Race | 15.1s | 58 | 235 | 100% | 0.0s | -17.2 | no bed (voice only) | 1-2 words + "Subscribe" badge |
| V6 | The Well That Held Back a River | 61.8s | 174 | 205 | 88% | 0.0s | -9.4 | -15 dB | 1-2 words + yellow number overlays |
| V7 | This Shape Saved Roller Coasters | 15.1s | 55 | 247 | 94% | 0.0s | -17.3 | -11 dB | 1-2 words |
| V8 | Why Perfect Railroads Don't Work | 15.1s | 53 | 227 | 97% | 0.0s | -16.2 | -13 dB | 1-2 words |
| V9 | Never lose against your own greed | 35.2s | 116 | 232 | 90% | 0.0s | -14.1 | -2 dB (loud score) | 1-2 words |

\*How loud the audio sits between words, relative to the voice. Lower means a quieter bed.

**What the numbers say:**
1. **8 of 9 start talking at 0.00s.** There is no intro, no logo and no silence. The first frame is already the story.
2. **The narrators run fast: 205–263 wpm while talking.** That is about 1.5× normal conversation. Pauses between sentences are short (median 0.14–0.36s).
3. **Something is spoken almost all the time (87–100% coverage)** in narrated formats. Silence is used on purpose, only before a reveal.
4. **There is always a soft bed under the voice**, sitting 10–15 dB lower. A constant tonal pad is visible in nearly every spectrogram. V9 runs its score much louder for emotion. V5 has none, and it sounds the cheapest of the set.
5. **Loudness is all over the place (-9.4 to -17.3 LUFS)** and three of the uploads are mono. This is where they are beatable. We master every video to exactly -14 LUFS / -1 dBTP in full stereo.
6. **Visual change every ~1–3s.** In the narrated ones, every sentence gets a new shot or a new camera move, and no frame is ever completely still.

---

## Video by video

### V1: "What if zombies could run?" (30s, no captions)
- **Format:** *What-if scenario → escalation → false safety → twist → "To be continued..."*
- **Hook:** the question is spoken at 2.0s over a calm walk-in. The visuals (a horde appearing behind him) carry the first 2 seconds.
- **Beats:** calm walk (0–3s) → zombies appear (3–5s) → shock close-up (5s) → chase montage with varied angles: side, front, POV, over-the-shoulder, fence jump (6–19s) → glass door, "Okay, I'm safe now, right?" (20–23s) → zombies press on the glass (24s) → wide shot, horde breaks in (26s) → dark close-up, trembling (27–29s) → black "To be continued...".
- **Visual style:** AI-generated 2D cartoon. A stickman with a round white head, red cap and blue hoodie stays consistent in every shot. Clean flat city backgrounds, image-to-video motion.
- **Audio:** the most SFX-heavy video of the nine. Whooshes, footsteps, zombie groans and sub-bass hits sit nearly as loud as the voice. The narrator mostly voices the character's thoughts.
- **What to learn:** a single consistent character design builds a recognisable "series" look. The cliffhanger ending invites a Part 2.

### V2: "Why do the rich keep getting richer…? One chicken explains it." (73s)
- **Format:** *big system explained through a simple parable*. A question hook, then a toy model (one chicken each), then three groups making three choices, then a payoff line that names the system ("The poor, the middle class, and the rich").
- **Hook (0–4.7s):** a question with built-in tension ("rich get richer while the poor get poorer") plus a promise ("One chicken explains it").
- **Devices:** rhythmic triplets ("Every coin. Every house. Every field. Gone."), punchy two-word callbacks ("Best dinner in three days. Last dinner too."), a chalkboard-explainer cutaway (a chicken teaching at a blackboard with "2 = egg, 3 = chickens"), time jumps ("Three weeks later…").
- **Visual style:** 2.5D. Flat-shaded cartoon characters in barrels inside a soft 3D-rendered village, with tilt-shift depth of field and warm lighting. Whip-pan motion-blur transitions. A day-to-night lighting shift marks time.
- **Ending:** a quiet sunset wide shot over the final line, with no CTA.

### V3: The button in the middle of town (60s)
- **Format:** *mystery loop*. A strange rule or place, then two weird details, then the protagonist breaks the rule, then the world changes, then the opening detail returns with a twist (47 scratches become 48).
- **Hook (0–3.5s):** "There's a button in the middle of town and nobody's allowed to press it." The anomaly and the forbidden act arrive in one line.
- **Devices:** specific numbers (47 scratches, 30 seconds, 3 a.m., five bucks), a named everyman ("Gary"), a peer-pressure trigger (a bet), a ticking clock (the guard swap), and a twist that turns the opening detail into the answer.
- **Visual style:** the most cinematic of the nine. A 3D world (a circular town inside a giant wall) with 2D stickman characters, dramatic night lighting with a glow, macro inserts (tally scratches, a counter reading 0047 → 0048), and a top-down reveal of the empty field.
- **Audio:** dense narration (254 wpm) with a mysterious bed. A tiny scratching sound is the key SFX.
- **What to learn:** **loop endings.** The last line re-frames the first, so viewers rewatch.

### V4: "Grandma's Secret Recipe Went WRONG" (59s)
- **Format:** *chaos-escalation comedy*. A mission, then a small mistake, then a bigger mistake, then the problem spreads (kitchen → street → bakery → gym → whole block → fire alarm), then rock bottom, then a magical warm resolution, then a deadpan button line ("Mission accomplished… sort of").
- **Writing:** a list rhythm with "Step one / Step two", "Oops", "Wait, which spice? Just all of them."
- **Visual style:** flat 2D AI images (a stickman in a red shirt and apron), lots of cartoon smoke, and a ghost grandma in golden sparkle light.
- **Captions:** ALL CAPS, bold, in the lower third with a dark outline. Keywords are highlighted in yellow or cyan, small emoji appear above the text, and an "SMFF" brand watermark sits bottom-right.
- **Audio:** a lower, warmer narrator voice (f0 ≈ 106 Hz). Comedic SFX: chop chops, bubbling, an alarm, a sparkle chime.

### V5: How a mirror rigged a horse race (15s)
- **Format:** *cold-open genius trick → "because…" → setup → ends mid-sentence*. A teaser that cuts off ("…the racetrack is right over the hill from—").
- **Hook:** "He bet his life savings on the slowest horse in the race." An absurd action and the stakes arrive in 3 seconds.
- **Devices:** the room laughing at him (social stakes), a contradiction ("bet his life savings" / "hasn't bet a single dollar"), the skeptic's line "Wait, what's a mirror going to do?", which voices the viewer's question.
- **Visual style:** a 2.5D old-west town, stickmen in bowler hats, a betting board, a piggy bank smashed with a hammer.
- **Audio:** voice only, mono, -17 LUFS. The weakest mix of the set.
- **Overlay:** a persistent white "Subscribe" pill at the top.

### V6: The well that held back a river (62s)
- **Format:** *legend or fable with a hidden-science reveal*. A warning, then the warning ignored, then an eerie anomaly (no splash), then escalating tests (a rope "208 FT… 604 FT"), then it is sealed, then "YEARS LATER" a drought, then it is reopened, then a flood, then a cross-section diagram explains the truth (a pressurized underground reservoir), then the moral sting ("…had just broken its seal").
- **Devices:** a forbidden rule in quotes ("Never throw a stone into this water"), an arrogant authority (the king), sensory absence ("No sound. No splash. Not even an echo."), animated number overlays in yellow, and a cutaway diagram with a pressure gauge.
- **Visual style:** low-poly 3D medieval village with stickman characters (a king with a crown, soldiers with helmets).
- **Audio:** the loudest master (-9.4 LUFS, slightly clipping), with mono sub-booms on the drop and the flood.

### V7: This shape saved roller coasters (15s)
- **Format:** *genius-trick teaser*. "He bent the roller coaster's loop out of shape. You see, …". Stakes ("cost him everything"), a rival copy ("bolt for bolt"), a disaster ("test dummy comes back crushed like a soda can"), cut.
- **Visual style:** 3D theme park with stickman characters. A rival in a suit at a blueprint easel, an "OPENING TOMORROW" banner.
- **Cut rhythm:** the fastest of the set, about 0.4s per visual change in the action moments.

### V8: Why perfect railroads don't work (15s)
- **Format:** the same teaser template as V7. "He sawed gaps into a railroad every 39 feet. You see, two companies are racing…" Stakes ("whoever finishes first gets the whole country's business"), the youngest engineer, the boss sees the gap, cut.
- **Visual style:** stylized 3D canyon with saturated red rock strata, drone moves along the track, and a "FIRST LINE IN GETS IT ALL!" banner.
- **Pattern for V5, V7 and V8:** *[He did something that looks stupid] → "You see," → [the competitive context] → [a problem] → cut before the answer.* It sells the full video, or a Part 2.

### V9: Alexander pours out the water (35s)
- **Format:** *historical anecdote → life lesson*. An aphorism hook in parallel structure ("Give a man his last drink of water… and he'll save himself. But give a great leader… he'll pour it onto the ground."), then the date and setting ("Around 325 BC…"), then the story, then the moral as a two-line chiasmus ("people don't follow leaders because they put themselves first. They follow leaders because they put everyone else first").
- **Visual style:** warm desert palette with purple shadows, stylized 3D sand and rock, stickman soldiers with spears, a helmet with water, a map cutaway, motion-blur whips.
- **Audio:** a big emotional score almost as loud as the voice. A shimmering riser at the climax (23.5s).

---

## The formula behind all nine

### 1. The first sentence is the whole pitch
- It is spoken at 0.0s and is 8–14 words.
- It contains an **anomaly** (an impossible fact, a forbidden act, or an action that looks stupid) or a **big question**.
- Examples: *"There's a button in the middle of town and nobody's allowed to press it."* · *"He bet his life savings on the slowest horse in the race."* · *"He sawed gaps into a railroad every 39 feet."*

### 2. "You see," is the pivot
Straight after the hook, the narrator gives just enough context to make the anomaly matter. That context is a rivalry, a deadline, money, a king, or a crowd laughing.

### 3. Concrete, odd-specific numbers
47 scratches, 39 feet, 325 BC, 208 ft → 604 ft, 3 a.m., 30 seconds, five bucks. Numbers make a story feel true and make good on-screen overlays.

### 4. Escalation in steps of three
Every coin / every house / every field. Kitchen → bakery → gym → whole block. Three groups. Each step raises the stakes. Nothing repeats.

### 5. Silence or a hit before the reveal
Narration and music pull back for half a second, then the reveal line lands with a hit or a boom.

### 6. Endings that create a second view
- **Loop** (V3): the last line answers the first.
- **Cliffhanger or cut-off** (V1, V5, V7, V8): the viewer replays or goes looking for Part 2.
- **Moral sting** (V2, V6, V9): one quotable line.

### 7. The visual grammar
- The same character style across the channel: stickmen with round white heads, readable eyes, one signature accessory or colour per character.
- Environments are richer than the characters: soft 3D or 2.5D with depth of field and cinematic light. That contrast is the look.
- A new shot every sentence. Inserts for details (scratches, a counter, a helmet of water). Wide establishing shots for scale. Cutaway diagrams for "how it works".
- Motion on every frame: push-ins, pans, whip-pans with motion blur.
- Big yellow overlay text for numbers and time jumps ("208 FT", "YEARS LATER").

### 8. Captions
1–2 words at a time, switching on the spoken word. Heavy rounded white sans with a dark outline and soft shadow, centred about two-thirds down the frame. Yellow for key words and numbers.

---

## Where we beat them

| Weakness in the references | Our fix (built into the studio) |
|---|---|
| Loudness from -9.4 to -17.3 LUFS; some clipping | Two-pass loudnorm to **-14 LUFS, -1 dBTP**, every time |
| 3 of 9 are mono; V5 has no music at all | Stereo SFX, panned whooshes, wide reverb; a music bed always on |
| SFX are sparse or generic in most of them | Cue-level sound design on every transition, reveal and number |
| Pacing sometimes rushed (263 wpm) and swallows punchlines | 215–230 wpm default, plus a deliberate *music drop* and pause before each reveal |
| Inconsistent caption styles across channels | One house caption style with word-synced pops and keyword colour |
| Teasers that cut off can feel like clickbait | Cliffhangers that still deliver a full-story payoff, or a true loop |
