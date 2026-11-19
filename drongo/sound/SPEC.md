# Sound design spec: "The Drongo" short

This spec turns `principles/` (1–1000) into the concrete decisions for this video.
Numbers in [brackets] cite the principle each decision comes from.

## 0. Targets measured from the reference videos

| Measure | Reference shorts | Our target |
|---|---|---|
| Integrated loudness | −14.1 to −15.1 LUFS | **−14 LUFS** |
| Loudness range | 1.6–2.5 LU | **≤ 3 LU** (dense and compressed) |
| True peak | −2.2 to −3.6 dBFS | **≤ −1.5 dBTP** |
| Stereo (side vs mid) | −28 to −31 dB, effectively mono | **near mono**: centred core, only small stereo touches |
| Spectral weight | 80–2000 Hz holds about 85% of the energy | voice owns 150 Hz–4 kHz; music and SFX work around it |
| Bed under voice | gaps only about 8 dB below speech | music/ambience never drops out by accident; about 8–12 dB under VO |
| Delivery format | 44.1 kHz stereo AAC at 128 kbps | 48 kHz stereo AAC at 192 kbps |

## 1. Hierarchy

1. **Narration is king** [601, 900]. Anything that competes with intelligibility goes down, never the voice.
2. **One hero sound per beat** [600, 706]. On each gag, either the SFX or a music stinger leads, not both.
3. Ambience is a floor, not a feature: 18–24 dB under VO peaks, never true silence (> −60 dBFS) [801, 802].

## 2. Character sound identities (pitch homes [465, 628])

| Character | Signature | Recipe |
|---|---|---|
| **Drongo** | Bright, metallic FM chirps at 1.5–6 kHz [538]; harsh "scream" alarm made of noisy FM syllables [557] | FM at ratio 1:2, index envelope, 4–7 Hz vibrato [447] |
| **Drongo mimicry** | Uses the exact recipe of the copied call plus a faint metallic FM edge and +1 semitone [539]; at the reveal it crossfades into the drongo's own timbre over 300 ms [540] | |
| **Meerkats** | Soft contact chirps at 1–3 kHz [544]; alarm bark is a noisy burst at 1–2 kHz over a harmonic buzz with an abrupt onset [541]; group voices offset 1–3 semitones [556] | Formant yelps for startle reactions [560] |
| **Hawk** | Descending cry 3.2 → 2.2 kHz with rasp [546, 547]; every instance different [549]; kept more realistic than the gags [599] | Slow wing whumps at 200–1500 Hz [480, 568] |
| **Beetle / scorpion / lizard** | Beetle: 1–3 ms clicks at 3–7 kHz [517]. Scorpion: chitin click-scrape [518, 551]. Lizard: near-silent patter and a freeze click [519, 552] | |

## 3. Music

- **Palette** [613, 620, 616]: marimba (modal 1:4:10) [788], pizzicato (Karplus–Strong) [787], comic reedy bass [791], whistle lead for the drongo [624, 793], woodblock and shaker [792], low brass and toms for the hawk only [623, 797]. No kick on every beat [621]. At most 4–5 voices playing at once [617].
- **Keys and tempo**: F major home at 104 BPM [631, 637]. Dawn opening in F Lydian [644]. Drongo in F Mixolydian with 58% swing [632, 641]. Sneaking in D Dorian at 88 BPM [633, 638]. Hawk danger in E Phrygian [634]. Scrambles at 138 BPM [639]. Step up to G as the con escalates [642]. Reveal chord is **A major on "thief"** [646, 745].
- **Motifs** [647–668]:
  - Drongo: C–F–E · D♯–E zigzag, taught twice in the first 15 seconds [668].
  - Meerkats: repeated staccato sixteenths ending in a step up [650].
  - Sentinel: a rising fourth C→F, sharing the drongo's fourth to plant the twist [652, 657, 743].
  - Hawk: a slow falling minor second in the low register [651].
  - A single alarm figure (fast repeated high minor third) for both the real and the fake alarms [653].
- **Density ladder** [677]: 0 silence · 1 pulse · 2 +bass · 3 +harmony · 4 +melody. Use levels 1–2 under speech [669, 670] and bloom to 3–4 in gaps of 1 s or more. Motifs only go in gaps of 0.4 s or more [604].
- **Frequency slots** [685–696]: under speech, music is low-passed near 2 kHz and has nothing sustained at the voice's fundamental. Music is high-passed at 38 Hz [690]. The bass gets saturation for 200–600 Hz harmonics [689].
- **Ducking** [767–774]: 8–12 dB, pre-ducked 150 ms before each line, 80 ms attack, 450 ms release, held through gaps under 400 ms. Stingers and the final button are exempt from ducking [773].
- **Dropouts** [714, 741, 744]: silence one beat before each hawk strike, before the punchline "Nice try, feather duster", and before the twist line. Three to five dropouts in total [722].
- **Ending** [753–766]: a staccato button built from the drongo motif ending, placed at least 300 ms after the last syllable [759], with a ring-out under 1 s. Total music length is whole bars in F at 104 BPM so the loop seam works [761–766].

## 4. SFX rules applied

- **Anatomy**: transient / body / tail / sweetener, with at most three audible layers [401, 411]. Sustained SFX stay out of 1–4 kHz while the narrator speaks [412].
- **Whooshes**: band-passed pink noise swept 300 → 3 k → 600 Hz, with the peak at about 70% of the length, on the cut [471, 472]. They go **only on motion or emphasis cuts**, not on every cut [481]. Zoom-ins sweep up and zoom-outs sweep down [483]. Feathered movers get flutter [478].
- **Pops and dives**: burrow emergence is an up-pop plus a sand spill plus a comb-filtered hollow tone [527]. Retreat is a down-swish into a muffled comb-filtered thump [528]. Pops in a sequence step up a whole tone each time [470].
- **Sand**: granular grains with density matched to the action [438, 439]. Digging strokes at 4–8 per second [521]. A dust puff after each landing [524].
- **Variation**: 4–8 seeded round-robin variants of everything that repeats [451, 586–591]. Signature calls stay consistent [594].
- **Graphics**: the name-card FM ding uses ratio 1:3.5 [581], is purer than the world sounds [577], and is tuned to the score's key [468].

## 5. Space

- The open desert is dry, with only short, sparse early reflections [ambience, part 5]. The burrow is comb-filtered with the high end cut. The sky uses a wide, airy bed with distant hawk cries low-passed at 3–5 kHz [548].
- Pan small things to their on-screen position at most ±30%. Keep the core mono-safe [477].

## 6. Delivery and QC (from 901–1000)

Render seeded and reproducible. Export stems (VO, MUSIC, SFX, AMB) plus the mix. Normalise to −14 LUFS with true peak ≤ −1.5 dBTP. Check mono compatibility and that there's no DC offset or clipping. Verify sync of the shot cuts against the words. Encode AAC at 192 kbps and 48 kHz. Listen through on a phone speaker and on earbuds before publishing.

## 7. Spotting (cue sheet)

The cue sheet lives in `cues.py`. Every cue is anchored to a **script phrase**, not a timestamp, so it re-times automatically to any voiceover once `align.py` has produced `words.json`.
