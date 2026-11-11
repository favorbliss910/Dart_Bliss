# Sound design: how the studio sounds better than the references

The studio's audio chain does the work a sound designer would do in a DAW, automatically on every render.

## Signal flow

```
Kokoro am_michael (24 kHz) ─► resample 48 kHz ─► trim ─► per-beat timing
        │
        ▼
VOICE CHAIN  highpass 70 Hz → -2 dB @220 Hz (de-mud) → +2.5 dB @3.2 kHz (presence)
             → +2 dB shelf @9.5 kHz (air) → de-esser → compressor 3:1 (-20 dB, 4/90 ms)
        │                                          ┌──────────── sidechain ─────────────┐
        ▼                                          ▼                                    │
      VOICE ───────────────────────────────►  MUSIC BED (mood preset or your track) ◄───┘
        │                                    level -13 dB vs voice, ducks 5 dB under speech,
        │                                    hard "drops" before reveals
        ▼
      SFX BUS (cue-synced to spoken words and transitions; stereo; reverb tails)
        │
        ▼
MASTER  two-pass EBU R128 loudnorm → -14 LUFS integrated, -1 dBTP, limiter → 48 kHz / 24-bit
```

## Measured targets (from the 9 references)

| | References | Studio |
|---|---|---|
| Integrated loudness | -9.4 to -17.3 LUFS (inconsistent) | **-14.0 LUFS** every time |
| True peak | up to +1.6 dBFS (clipping in V6) | **-1.0 dBTP** |
| Stereo | 3 of 9 are mono | stereo SFX pans, wide reverb, Haas-widened music |
| Bed under voice | absent (V5) to -2 dB (V9) | -13 dB, ducking under speech |
| Speech pace | 205–263 wpm | 215–230 wpm (`speed: 1.18`) |
| Dead air at start | 0.0s (except V1) | 0.0s |

## The SFX palette (25 synthesized effects, all original and royalty-free)

| Use it for | Effect(s) | Placement |
|---|---|---|
| Scene or location change | `whoosh` (auto on `whip`), `swish` | peak lands on the cut |
| Building to a reveal | `riser`, `reverse_swell` (auto on `music: drop`) | ends exactly on the cue |
| Reveal word | `impact` | on the word |
| THE twist (once per video) | `boom` | on the word |
| Ominous discovery | `braam` | on the word |
| Numbers / overlays / emojis | `pop` (auto on `overlay`), `click`, `typing` | on appearance |
| Time pressure | `tick`, `ticking` | under the beat |
| Realisation / correct answer | `ding` | on the word |
| Magic / wholesome | `sparkle` | on the word |
| Money | `coin` | on the word |
| Fear | `heartbeat` | beat start |
| Something unnatural | `glitch`, `tape_stop` | on the word |
| Comedy fail | `boing`, `slide_down` | after the punchline |
| Footsteps, doors, falls | `thud` | on the word (+offsets for steps) |
| Environment | `rumble`, `wind`, `splash`, `crowd_gasp` | beat start |

Audition them all with `python -m studio.sfx`. That writes `output/sfx_preview/_all_effects_reel.wav`.

**Rules the references follow (and we follow better):**
1. **Every visual cut gets a sound.** Whooshes on whips, pops on text, a thud on every hard cut-to-impact.
2. **Hit the word, not the sentence.** SFX are cued with `on_word`, so the impact lands on "today", not near it.
3. **Silence is an effect.** `music: drop` kills the bed for about 0.6s before the reveal. Contrast makes the hit feel twice as loud.
4. **At most 2 effects per beat.** More than that turns into noise that buries the narrator.
5. **One `boom` per video.** If everything is huge, nothing is.

## Music
Six generated mood beds: `mystery`, `curious`, `tension`, `comedy`, `reflective`, `epic`. Each is matched to a reference format (see `studio/music.py`). They are fine for daily output. For a channel signature sound, use a licensed track:

```json
"music_file": "music/my_track.mp3", "music_db": -13
```
The studio loops or trims it, ducks it under the voice, applies the drops, fades the end and masters it.

Good legal sources: YouTube Audio Library (free, in YouTube Studio), Pixabay Music (free), Epidemic Sound and Artlist (subscriptions, Content ID-safe for channels). Avoid uncleared "no copyright" uploads, which often trigger Content ID claims.

## Better recordings for the SFX
The synthesized palette is solid. Real recordings add texture. Drop WAVs into `sfx_library/` named after the effect (`whoosh_1.wav`, `whoosh_2.wav`, `impact.wav`…), and they replace the synthesized versions automatically, with random variants per cue. You can also add new names (`door_creak.wav`) and use them in specs. Sources: Sonniss GDC bundles (free, royalty-free), freesound.org (filter by CC0), Epidemic Sound or Artlist SFX.

## About "the best plugin"
For TTS narration you don't need restoration plugins like iZotope RX: Kokoro output is already noise-free. What matters is EQ, de-essing, compression, ducking and loudness, and the studio does all of that in code, the same way every time, so episodes match. If you also finish in a DAW (Audacity, Reaper, DaVinci Resolve Fairlight, Premiere), the equivalents are:
- **EQ:** FabFilter Pro-Q 3 (paid) / TDR Nova (free)
- **Compression:** FabFilter Pro-C 2 / TDR Kotelnikov (free)
- **De-esser:** FabFilter Pro-DS / TDR Nova (dynamic band)
- **Limiter:** FabFilter Pro-L 2 / LoudMax (free)
- **Loudness meter:** Youlean Loudness Meter 2 (free); aim for -14 LUFS integrated, -1 dBTP
- **Ducking:** a sidechain compressor on the music bus keyed from the voice, about 5 dB of gain reduction

The stems are exported (`output/<slug>/stems/voice.wav, music.wav, sfx.wav`) so you can remix in any of these.
