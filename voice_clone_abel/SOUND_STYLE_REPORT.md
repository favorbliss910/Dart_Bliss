# Sound style report: what the reference shorts do, measured

**Sources:** "The Scientists Insane" (40 s), "What If Humans" (54 s), "The Town Built" (66 s).
The two "Scientists" uploads are the same file. The three MP3s (rec_wav, rec_234, rrc) are these videos' soundtracks.

**Method:** each soundtrack was split into voice, drums/SFX, bass and other with Demucs. The voice was transcribed with word timings by Whisper, then everything was measured: loudness, pitch, pacing, spectrum, events and cuts.
I can't hear audio. Every point below is a measurement or something visible in the frames, not a listening impression.
Measurements of separated stems carry some error from the separation. Treat small dB differences as approximate.

There are about 150 distinct, real observations here, not 1,000. Past this point, more items would be invented or repeated. Each observation that can be automated is built into `sound_engine/style_profile.json` as a range, so every new video follows it.

Format for numbers: Scientists / What If / Town.

---

## A. Format and delivery
1. Vertical 1080×1920 (9:16), 30 fps, H.264 video. These are YouTube Shorts / TikTok / Reels sized.
2. Audio is AAC, 44.1 kHz, stereo, 128 kb/s. That's the platform default, so nothing special is needed.
3. Lengths are 40 s, 54 s and 66 s. All are under 70 s, and the story always fits one short.
4. The audio runs the full length of the video, with no silent intro or outro card.
5. The video ends 0.21–0.59 s after the last word. The cut comes almost instantly after the final line.

## B. Overall mix and loudness
6. Integrated loudness is −15.2 / −14.2 / −14.1 LUFS, so the channel masters to about −14 LUFS (the YouTube/TikTok norm).
7. Peaks are −3.9 / −2.8 / −2.2 dBFS. The mix leaves headroom and is never slammed to 0 dB.
8. Left/right correlation is 0.997–0.999, so the mix is effectively mono. There's no wide stereo music or panned effects.
9. The voice is mono and centred (correlation 0.993–0.996).
10. The voice carries the loudness. The voice stem alone is within 0.1–0.3 LU of the full mix.
11. The music + SFX bed sits at −30.7 / −25.5 / −33.9 LUFS, i.e. very quiet.
12. The voice is 14.5 / 8.7 / 19.8 dB above the bed. Typical is about 15 dB, and "What If" runs its bed hotter.
13. **The music isn't ducked.** The bed is −33.4 vs −33.7 dB (speaking vs gaps) in Scientists, −26.6 vs −25.7 in What If, and −37.4 vs −36.9 in Town. It stays at one level throughout.
14. The bed is steady across the video: per-5-second levels stay within about ±2 dB. There are no big builds or drops.
15. Exceptions: "What If" swells about 2–3 dB in the last 10 s, under the closing question. "Town" bumps about 4 dB at 40–45 s, under "presses it, but nothing happens".
16. Scientists' bed is loudest in the first 5 s (−30.7 vs about −33). The opening is slightly more energetic.
17. Voice level per 5 s stays within about 1.5 dB from start to finish, so it's heavily levelled/compressed.
18. The final sentence is 2–4 dB quieter than the rest (−19.8 / −20.3 vs about −17), giving a softer, intimate last line.
19. The hook (first sentence) is **not** louder than the body (−0.1 to −0.6 dB). The hook works through words and pitch, not volume.

## C. Voice: tone and timbre
20. Median pitch is 195 / 191 / 187 Hz, the same narrator in all three. That's high and bright for a male voice: an animated "storyteller" register.
21. Typical pitch range (10th–90th percentile) is 133–299 / 123–280 / 131–274 Hz.
22. That's 14.1 / 14.3 / 12.7 semitones of movement, a **very** expressive delivery (a flat read is about 5–7).
23. 46–56% of the voice energy is in 150–300 Hz: a full, chesty fundamental.
24. 23–29% is in 300–800 Hz, a solid lower-mid body.
25. Under 1% is below 80 Hz, so the voice is high-passed with no rumble or plosive thumps.
26. 3–5% is above 5 kHz: air and crispness are kept, so it's a bright recording.
27. Spectral centroid is 2.6–2.8 kHz, a bright, forward voice.
28. The content extends to about 14 kHz, so it's a full-band, high-quality recording (not phone or room-mic quality).
29. Sibilance (5–9 kHz vs 1–4 kHz) is −1.7 / −3.6 / −2.7 dB: "s" sounds are present and crisp, only lightly de-essed.
30. The noise floor in gaps is −53 to −58 dB, a clean, silent background (studio or AI-clean).
31. The voice falls 7.5–8 dB in the first 100 ms after a word. It's dry, with no audible reverb or room.
32. Crest factor is about 14 dB, so it's compressed but not squashed flat.
33. Level spread while speaking (10th–90th percentile) is 14–15.6 dB, so natural word-to-word dynamics remain.
34. Breath-like sounds in pauses: 16 / 33 / 14. **Breaths are left in**, and they make it sound human and urgent.
35. All three reads sound like the same narrator. Voice-identity similarity between them is 0.96–0.98.

## D. Voice: pacing and rhythm
36. Speaking rate is 217 / 220 / 225 words per minute, fast (normal conversation is about 150).
37. The voice is talking 88 / 85 / 94% of the time, so there's almost no dead air.
38. The first word starts at **0.00 s** in all three. No intro, no music lead-in, no title sting.
39. The median pause after a sentence is **0.24 s** in all three, an extremely consistent rhythm.
40. The median pause after a comma is 0.28 / 0.20 s.
41. The longest pause in any video is 0.36 s. Nothing is ever held for drama longer than that.
42. Pauses over 0.25 s occur only 10 / 13 / 4 times per video.
43. The longest pauses sit before a turn: "Apparently, | when", "died. | And", "scratches. | Then", "anyone. | It".
44. Pace varies by sentence, from 2.9 to 5.3 words per second.
45. **Slowest lines are reveals and hooks:** "Under the glass there are 47 tiny scratches…" (2.9 w/s), "But Gary's always noticed two weird things." (3.1), "When humans invent teleportation…" (3.1), "But nobody ever asks…" (3.1).
46. **Fastest lines are action and lists:** "So when his friends bet him five bucks…" (5.3), "people teleport to work, to see family, even to grab lunch…" (4.7), "than it really did. But when he asked…" (4.6).
47. Sentences are long: about 16 / 15 / 14 words on average, read in one breath.
48. Sentence counts are 9 / 13 / 18, roughly one sentence per 3.5–4.5 s.

## E. Voice: melody (intonation)
49. Most statements **end on a strong downward fall**: −4.7, −8.7, −7.8 (Scientists); −7.7, −6.2, −7.8 (What If); −8.9, −9.7, −12.8, −9.5 semitones (Town). The narrator "lands" each fact.
50. The biggest fall (−12.8 st) is on "Just a tiny scratching sound under the glass." Creepy details are delivered falling and low.
51. Lists and build-ups **rise**: "with your face, your memories, and the feeling…" (+7.0 st). It keeps you waiting for the end.
52. Questions rise: "then where did you go every other morning?" (+5.6 st).
53. The final question to the viewer **falls** (−4.4 st, "would you still step inside?"). It's a rhetorical, confident ending, not an uncertain one.
54. Hooks start high (205–206 Hz) and fall, a "headline" contour.
55. Twist lines starting with "But" jump **up**. "But Gary's always noticed two weird things" is the highest line in Town (248 Hz).
56. Ominous lines drop **down**: "But nobody ever asks what actually happens inside that pod" is among the lowest in What If (160 Hz). The pitch tells you whether a twist is exciting or dark.
57. Pitch alternates high and low from sentence to sentence (e.g. 222 → 160 → 248 → 203 Hz in Town), so no two neighbouring lines sit at the same pitch.
58. Emphasis comes from pitch and pace, not volume: sentence loudness only varies about 3 dB.

## F. Music
59. Music plays from the first frame. It never starts after the voice.
60. Town fades the bed in over about 0.3 s. Scientists and What If start at full level.
61. Keys are minor: D minor (Scientists), G minor (What If), D minor (Town). The tone is mysterious, dark-curious.
62. Tempo is about 120 BPM (Scientists), about 117.5 BPM (Town), and What If detects at 172 BPM, likely an 86 BPM half-time feel. These are mid-tempo, walking-pace beds.
63. Scientists loops every 8 s (4 bars at 120 BPM), a short, simple loop.
64. What If and Town don't show a short repeat, so the music is longer or through-composed.
65. The music is **heavily low-passed**: only 0.01–0.8% of its energy is above 2 kHz. It leaves the whole voice-presence range (2–5 kHz) empty.
66. What If's bed is 89% sub-bass (<80 Hz): a deep drone or sub pulse you feel more than hear.
67. Town's bed is 44% in 300–800 Hz: warm mid-range plucks/mallets.
68. Scientists' bed is split between sub (37% <80 Hz) and mids (30% at 300–800 Hz).
69. Music spectral centroid is 700–1550 Hz, darker than the voice (2.6–2.8 kHz), so they never fight.
70. A light percussive pulse is present in all three (the drums stem is active), but it's quiet: −34 to −39 LUFS.
71. The music ends with a quick fade (about 0.3–0.6 s) right as the video cuts.
72. The music never changes key or style mid-video. It's one bed per video.
73. The music sits under the voice all the way through. It's never featured on its own.

## G. Sound effects
74. SFX are present but **subtle**: 67 / 19 / 42 short events (some in Scientists are rhythmic music hits).
75. Most SFX are short: 0.04–0.5 s.
76. Most SFX are bright: centroid 1.2–7.9 kHz (pops, clicks, swishes, ticks).
77. SFX levels run −25 to −50 dBFS against voice peaks of −7 to −11 dBFS, roughly **15–40 dB under the voice**.
78. Only a few SFX get close to the voice: the −25 to −27 dB "hero" hits.
79. **SFX land on the word they illustrate**, matched to what's on screen.
80. Town: hit on "button" (0.4 s), "press" (2.9 s), "whole [town]" (3.6 s), "built" (4.3 s).
81. Town: hit on "tall" (13.8 s), the wall/ladder shot.
82. Town: the loudest hit is on "glow" (16.6 s, −26.5 dB), the glowing horizon shot.
83. Town: hits on "gets [dimmer]" and "dimmer" (19.5–20.3 s).
84. Town: a big hit on "two [weird things]" (21.9 s, −25 dB), emphasising the number.
85. Town: hits on "there are [47]" (24.1 s) and "explain" (26.5 s).
86. Town: a hit on "three [in the morning]" (34.6 s).
87. Town: a hit as he lifts the glass (38.5 s).
88. Town: a literal scratch SFX on "Just a tiny scratching sound" (42.1 s, 19 dB jump).
89. Town: low booms (about 500–900 Hz centroid, 0.2–0.6 s) on the "glow" line and on the reveal sequence "tiny… home… glow… over… wall… brighter… The houses are gone… field" (42–55 s). Low end is reserved for the creepy reveal.
90. Town: a hit on "nobody's [allowed]" (2.1 s) in the very first line.
91. Town: a closing sound on the final word "here" (65 s).
92. What If: a 1.8 s low boom (656 Hz centroid) on "billions [of people will die]" (1.7 s), **the shock line of the hook gets the biggest effect**.
93. What If: a hit on "teleportation" (1.1 s).
94. What If: hits on "[stepping] into" (5.3 s), "glass" (5.8 s), "every [single atom]" (8.1 s).
95. What If: hits on "work" (14.9 s) and "even [to grab lunch]" (16.0 s), list items get pops.
96. What If: a hit on "a [machine glitches]" (22.1 s) and on "glitches" (22.6 s).
97. What If: hits on "terrifying" (32.5 s), "morning?" (36.8 s), "[deletes] you," (39.5 s), "perfect" (41.0 s), "face," (43.0 s, very bright: 7.9 kHz), "trip," (46.6 s).
98. What If: soft musical accents at sentence starts: "Imagine" (4.6 s), "Within" (11.8 s), "But" (18.1 s), "Then" (21.1 s), "You" (23.2 s). Each new beat of the story gets a little "ding".
99. Scientists: hits on "off [a tower]" (1.3 s), "just" (2.0 s), "right [before you die]" (4.1 s).
100. Scientists: **a run of evenly spaced hits every 0.38 s** under "brain speeds up so much that the whole world" (7.8–9.2 s). The ticking illustrates the brain speeding up.
101. Scientists: a 1.2 s swell on "into slow motion" (13.4 s), a slow-motion whoosh.
102. Scientists: low hits on "scientist" (0.2 s) and "motion." (14.1 s).
103. SFX never cover a word. They stay quiet enough to sit under speech.
104. Picture moves get no big "whoosh" every time. SFX are selective, roughly 3–5 per 10 s.
105. SFX are mono and centred, like the rest of the mix.

## H. Picture and sound together
106. Stick-figure cartoon characters in colourful 3D/2.5D sets: friendly visuals against a dark-mystery script.
107. A new shot comes roughly every 2–3 s (every 3-second sample shows a different image).
108. The scene detector found few hard cuts. Shots change with camera moves, zooms and morphs, and SFX often sit on those moves.
109. Captions show one or two words at a time, in bold white with a black outline, centred mid-screen.
110. The caption word changes exactly with the spoken word, which needs word-level timing.
111. Literal visuals follow the words: "brain" shows a brain, "47" shows the number 47, "glow" shows the glow. The SFX follow the same rule.
112. Numbers are shown on screen and get an SFX hit ("two", "47", "30", "three").

## I. Script and storytelling patterns that shape the sound
113. Line 1 is always a shock claim: "A scientist dropped people off a tower…", "billions of people will die…", "a button… nobody's allowed to press".
114. Line 1 is spoken from 0.0 s with no lead-in. The hook is the first sound you hear.
115. The second line explains or widens ("Apparently…", "Imagine…", "The whole town…").
116. "But" marks a twist: 2–3 "But" turns per video, each with a pitch jump and often a hit.
117. The script uses second person ("you", "your brain", "you step out in Tokyo") to pull the viewer in.
118. Numbers are very specific (47 scratches, 48 scratches, 30 seconds, five bucks, 3 a.m., one second, two of you).
119. Short punch sentences follow long ones ("Every trip, the real you died.").
120. Endings are a question to the viewer ("So be honest, would you still step inside?") or a twist line ("We'll build our town right here.").
121. The final line is softer and falling (see 18 and 53).
122. Plain spoken words and contractions ("nobody's", "there's", "he's got about 30 seconds").
123. Ellipses or cliffhangers are carried by pace, not pauses: the narrator rarely stops for more than 0.36 s.

## J. Implied production chain (what to copy)
124. High-pass on the voice at about 80–90 Hz.
125. A gentle 150–300 Hz warmth/body lift.
126. A little 3–4 kHz presence and 8–10 kHz air.
127. Light de-essing only. Keep the crisp "s".
128. Compression of about 3:1, with fast attack and medium release, plus a leveller (voice stays within ±1.5 dB per 5 s).
129. No reverb on the voice.
130. Keep the breaths.
131. Voice normalised to about −14.5 LUFS before the mix.
132. Music low-passed at about 2 kHz, sitting 12–18 dB under the voice, with no sidechain ducking.
133. SFX 15–30 dB under voice peaks, on keywords, 3–5 per 10 s.
134. Master to −14 LUFS integrated, −2 to −3 dBTP peak.
135. Mono-compatible (near-mono) final.
136. Cut the video about 0.2–0.6 s after the last word.

## K. What the Abel voice can and can't match yet
137. Pace: matched. The engine auto-tunes Abel to 215–225 wpm.
138. Pause rhythm: matched. Sentence gaps are 0.20–0.36 s, centred near 0.24 s.
139. Loudness, music level, music darkness and SFX density: matched (the test remake measured −14.0 LUFS, voice 13.3 dB over music, 0.03% music energy above 2 kHz).
140. Timbre: close but not the same. Voice-identity similarity is about 0.86 against the separated narrator (1.0 = same voice; the narrator vs themself is about 0.97).
141. **Pitch: lower.** Abel is about 147 Hz vs the narrator's about 190 Hz. Pitch-shifting Abel up made it sound *less* like the narrator, so it isn't done.
142. **Expressiveness: flatter.** Abel moves about 9 semitones vs the narrator's 13–14. Kokoro can't be directed line by line ("go up on this twist"), which is the biggest remaining gap.
143. Breaths: Kokoro doesn't generate breaths. Adding real breath samples would close this.

## L. Notes for using this
144. These shorts appear to be from another creator's channel (downloaded via SnapYT). Copying the *style* (pacing, mix, structure) is fine. Don't reuse their actual music or effects, and don't present Abel as that narrator.
145. The generated music bed and SFX in `sound_engine` are made from scratch (synthesised), so they're yours to use.
146. Want real instruments instead? Pass your own royalty-free track with `--music track.mp3`. The engine still low-passes it and sets its level and fades.
147. The `--seed` option changes key, tempo, EQ amounts, music level, SFX picks and pause lengths, all inside the measured ranges. Same channel sound, never an identical copy.
148. Word-by-word captions (`.srt`) come out of every run, timed to the voice, like the reference videos.
149. Each run also writes `_stems/voice.wav`, `music.wav` and `sfx.wav`, so you can adjust levels in an editor.
150. Edit `style_profile.json` to add your own keywords to SFX types (e.g. add "door" to "thud").
