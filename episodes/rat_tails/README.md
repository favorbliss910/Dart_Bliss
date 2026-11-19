# Rat Tails (Hanoi, 1902): episode notes

Built with the 2D engine following `library/PROMPT_BOOK_blank_library.md` (Part 1 one-paste prompt).

- **Voiceover:** `vo.mp3` (supplied, mastered, untouched), 147.7 s, 545 words, about 221 wpm. `vo_transcript.srt` is the supplied word-level transcript; the alignment agrees with it to 30 ms (median).
- **Script:** `script.txt`. Numbers use the new `shown{said}` form, e.g. `20,000{twenty thousand}`, so captions show digits while the aligner hears words (added to `drongo/sound/align.py`, backward compatible).
- **Words:** `words.json` (all 545 aligned, +1.0 s tail = 148.33 s).
- **Shots:** 87 shots, one per phrase, 0.68–3.42 s (mean 1.70 s), each starting 0.06 s before its first word (`scenes.py`).
- **Cast** (`people.py`, extended from `library/people.py`): the rat catcher (lead: teal tunic, conical non la hat, scissors), French officials (white suits, pith helmets, moustaches), the night inspector (navy, kepi), two rival catchers, townspeople, and the rats (side view, front bust, dangling, dead, tailless with a red plaster). Model sheet: `model_sheet.py`.
- **Worlds:** Old Quarter street, French Quarter street (day/dusk/night), sewer tunnel, underground cutaway, health office and bounty counter, market, rice fields and the shed (day/dusk/night), shed interior with cages, explainer paper, chalkboard, garden, bank vault.
- **Post looks:** sepia silent-film for the backstory (shots 5–10) and "In real life" (84); red isolation on "no tail" (66); a dark, cold re-hook on "Now here's the weird part" (42). The reveal (70) reuses the shed framing from 47; the second snip (29) reuses the first (2); the release (80) reuses 30.
- **Sound** (`sound.py`): F# minor pentatonic at 96 BPM, away from the VO pitch (median 154 Hz, A2–G3). New zither (dan tranh-style bend), squeak, snip, coin, register, crackle, crickets and other recipes; the rest is reused from `library/sound.py`. Verified mix: −14.0 LUFS, bed 25.0 dB under the voice during speech, 22.8 dB in 1–4 kHz, limiter never touches the voice.

## Commands (from this folder)
```
python3 ../../drongo/sound/align.py vo.mp3 script.txt --out words.json   # then add the 1.0 s tail
python3 model_sheet.py
python3 scenes.py /tmp/st --times 0.5,1.8 --size 320x568
python3 sound.py
python3 render_video.py --ss 0.5 --size 320x568 --fps 15 --out out/preview_small.mp4
python3 render_video.py --ss 2.25 --size 1440x2560 --fps 30 --jobs 4
ffmpeg -i out/rat_tails_2k_master.mp4 -c:v libx264 -preset slow -b:v 16M -maxrate 22M -bufsize 32M -tune animation -c:a copy out/rat_tails_2k.mp4
```
