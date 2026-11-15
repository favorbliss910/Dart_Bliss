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
