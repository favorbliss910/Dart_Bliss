## Part 3 — Sound Effects, Foley & Cartoon Sound Construction (401–600)

### Layering anatomy

401. **Four-layer anatomy** — Build every hero SFX from transient (0–15 ms), body (15–150 ms), tail (150 ms+) and optional sweetener, synthesizing and enveloping each layer separately before summing.
402. **One job per layer** — Give each layer its own band and time window: transient owns 2–8 kHz clicks, body owns 150–800 Hz weight, tail owns decay texture.
403. **Transient sells the hit** — Design the transient as a 2–10 ms burst of high-passed noise or a single-cycle click; listeners judge timing and impact almost entirely from it.
404. **Body carries identity** — Let the body define what the object is (sand, flesh, wood, chitin) through resonant filter frequencies and modal partials, not through the transient.
405. **Tail places it in space** — Author tails as filtered decaying noise or modal ring-out of 80–400 ms rather than generic reverb, so each sound's length is designed.
406. **Sweetener for character** — Add a small tonal sweetener (a 1–2 semitone chirp, a tiny boing, a bell partial) 6–12 dB below the body to give cartoon personality without clutter.
407. **Harmonics imply weight on phones** — Phone speakers roll off below ~250 Hz, so add a harmonic layer at 2–4× any sub fundamental so weight is implied through upper partials.
408. **Sub layer is removable** — Keep content below 80 Hz on its own layer so earbud versions get thump while phone-speaker renders stay clean and headroom-efficient.
409. **Align onsets deliberately** — Start layers sample-aligned for maximum punch, or delay the body 3–8 ms after the transient for a two-stage "crack-then-thud" read.
410. **Control phase in summed lows** — When stacking sines or low-passed thumps near the same frequency, set start phases explicitly (usually 0 or 90°) to avoid cancellation that kills low end.
411. **Three audible layers max** — Cap most SFX at three audible layers; beyond that, small-speaker playback smears them into mush that competes with narration.
412. **Keep sustain out of the speech band** — Let sustained SFX layers live below 800 Hz or above 5 kHz, allowing only brief transients to touch the 1–4 kHz intelligibility band.
413. **Internal layer balance** — Start with transient 0 to +3 dB relative to body peak, tail −6 to −12 dB, and sweetener −9 to −15 dB, then adjust by ear.
414. **Bake stacks into one asset** — Render each layered stack to a single normalized mono file per variation so timeline placement is simple and layers can never drift apart.
415. **Build a layer library** — Keep a reusable bank of transients, bodies and tails so new SFX are recombinations, giving the whole film a consistent sonic family.

### Envelope shaping

416. **Attack defines hardness** — Use 0–2 ms attacks for hard contacts, 5–20 ms for soft or padded ones, and 30 ms+ for swells; attack time is the fastest material cue.
417. **Exponential decays sound natural** — Shape decays as amplitude × e^(−t/τ) rather than linear ramps, which sound artificial and appear to stop abruptly.
418. **Decay time encodes size** — Scale decay τ with object size: roughly 15–20 ms for a beetle tick, 60–80 ms for a meerkat paw, 200–250 ms for a hawk landing.
419. **Click-free edges** — Apply at least a 1–3 ms fade-in and 5–10 ms fade-out to every synthesized buffer unless a click is the intended transient.
420. **Two-stage decay** — Use a fast initial drop (about −12 dB in 30 ms) followed by a slower tail for resonant objects that "hit, then ring."
421. **Pair pitch and amplitude envelopes** — Give every amplitude envelope a matching pitch envelope; even a 1–3 semitone downward drift during decay makes synthetic tones feel physical.
422. **Filter envelopes add life** — Sweep a low-pass cutoff down with the decay (e.g., 8 kHz to 800 Hz over 100 ms) so sounds darken naturally as energy dissipates.
423. **Hold stage for emphasis** — Insert a 10–40 ms hold at peak before decay for cartoon freeze-frame moments where the hit should feel momentarily suspended.
424. **Reverse swells for anticipation** — Use reversed exponential swells of 200–600 ms leading into an event, cutting off sharply on the sync frame.
425. **Tremolo for flutter and nerves** — Amplitude-modulate at 15–40 Hz for buzzing and fluttering, and at 4–8 Hz for wobbling, trembling or nervousness.
426. **Envelopes follow frames** — Derive envelope stage times from animation frame counts (one frame is 33.3 ms at 30 fps, 41.7 ms at 24 fps) so the sound's shape mirrors the motion.
427. **Gate and trim tails** — Truncate tails once they fall below −60 dBFS and trim trailing silence so short assets don't carry noise floors that build up when stacked.
428. **ADSR for sustained calls** — Give sustained calls (hawk scream, drongo whistle) a 10–30 ms attack, slight decay to ~70% sustain, and a 50–150 ms release.
429. **Accent rhythmic repeats** — In rapid sequences (scurrying, pecking), make every third or fourth peak 2–3 dB louder so the motion implies intent and rhythm.
430. **Equal-power crossfades** — Use equal-power or logarithmic curves when crossfading synthesized segments to avoid the ~3 dB mid-fade dip of linear fades.

### Designing sounds from synthesis

431. **Start from noise, sculpt with filters** — Build most foley and texture by band-passing white or pink noise; the center frequency sets material and Q sets resonance.
432. **Choose the waveform for the mood** — Use sines for cute and clean, triangles for soft toy-like tones, and band-limited saws or squares for buzzy, harsh or villainous sounds.
433. **Band-limit oscillators** — Generate saws and squares additively or with PolyBLEP; aliasing reads as cheap digital fizz on bright phone tweeters.
434. **Modal synthesis for objects** — Model struck objects as 3–8 damped sinusoids with inharmonic ratios (e.g., 1, 2.76, 5.40, 8.93) for convincing pebbles, sticks and shells.
435. **Inharmonic = solid, harmonic = alive** — Use inharmonic partials for stone, wood and chitin, and harmonic series for voices, whistles and anything that should feel like a creature.
436. **FM for bells and chirps** — Use non-integer modulator ratios (1:1.4, 1:3.5) for metallic pings and integer ratios (1:1, 1:2) for rounder, friendlier tones.
437. **FM index is brightness** — Envelope the modulation index (e.g., 5 → 0 over the decay) instead of a filter to get cheap, natural decaying brightness.
438. **Granular for sand and texture** — Scatter 1–5 ms grains of filtered noise or clicks at 200–2000 grains/s with random amplitudes to synthesize sand, scratching and crumbling.
439. **Grain density equals intensity** — Map action intensity to grain density: about 50 grains/s for a trickle up to 3000 grains/s for a sand avalanche.
440. **Resonators as virtual bodies** — Pass clicks or noise bursts through 2–4 parallel band-pass resonators (Q 10–40) to imply a hollow body such as a beetle shell or burrow.
441. **Comb filters for tunnels** — Apply a comb filter with 2–10 ms delay and 0.6–0.85 feedback to give tube or tunnel coloration to sounds inside burrows.
442. **Karplus-Strong for twangs** — Use Karplus-Strong for twangs, plucks and snapping twigs, lowering loop feedback below 0.99 to shorten and dull the decay.
443. **Soft-clip for audible weight** — Drive low thumps through tanh with gain 2–6 to generate upper harmonics that make weight audible on phone speakers without raising peak level.
444. **Ring modulation for menace** — Ring-modulate tones with 30–200 Hz carriers for alien, unsettling textures suited to scorpion stings and villain reveals.
445. **Master the swept sine** — A sine swept between two frequencies is the backbone of slide whistles, boings, zips, pops and drops; build one flexible sweep function and reuse it.
446. **Sweep exponentially** — Sweep frequency in constant semitones per second rather than linear Hz so glides sound even across their whole range.
447. **Vibrato adds life** — Add 4–7 Hz vibrato of ±20–50 cents to sustained tones; static pitch reads as electronic, gently modulated pitch reads as a living voice.
448. **Jitter and shimmer** — Add per-cycle pitch jitter of 0.5–2% and amplitude shimmer of 1–3 dB to synthetic voices to defeat the robotic feel.
449. **Formants make vowels** — Shape buzzy sources with 2–3 band-pass formants (about 700/1200 Hz for "ah", 300/2300 Hz for "ee", 300/800 Hz for "oo") for expressive wordless voices.
450. **Formant glides convey intent** — Glide formants "oo"→"ah" for surprise or opening up, and "ah"→"ee" for whining or pleading.
451. **Seed every random generator** — Seed numpy's RNG per asset and per variation so approved sounds are reproducible and can be tweaked without losing the take.
452. **Oversample nonlinear stages** — Run waveshaping, high-index FM and ring modulation at 2–4× sample rate, then filter and decimate, to keep aliasing out.
453. **Parameterize every recipe** — Write each SFX as a function of size, intensity and mood so one recipe scales consistently from beetle to hawk.
454. **DC-block after synthesis** — High-pass at 20–30 Hz after asymmetric waveshaping or filtered noise to remove DC offset that wastes headroom and causes edit clicks.
455. **Micro-convolution for material** — Convolve dry hits with a synthesized 10–50 ms decaying, filtered noise impulse to add material texture without a reverb tail.

### Pitch as size and emotion

456. **Smaller body, higher contact pitch** — Pitch impacts and steps inversely to size: beetle ticks near 4–6 kHz, meerkat pats near 300–800 Hz, hawk landings with body near 100–200 Hz.
457. **Resize with pitch and time together** — To scale an object, shift pitch and stretch decay together (e.g., −12 semitones with 2× decay for double size) so it stays believable.
458. **Up is energy, down is loss** — Use upward pitch motion for hope, curiosity, lift-off and questions, and downward motion for defeat, falling and deflation.
459. **Semitone beating for danger** — Stack two tones a semitone apart (e.g., 880 and 932 Hz) in threat cues; the audible beating reads as tension instantly.
460. **Consonance for success** — Build positive pops and chimes on fifths and octaves (3:2, 2:1), adding a major third (5:4) for extra sweetness on cute moments.
461. **The deflation glide** — Signal failure with a 3–12 semitone downward glide over 300–800 ms, slower and wider for sadder beats.
462. **Glide speed sets emotion** — Fast glides (50–150 ms) read as playful or startled; slow glides (500 ms+) read as sad, sleepy or ominous.
463. **Low register for menace, with harmonics** — Give hawk shadows and scorpion approaches sub-200 Hz content plus harmonics at 200–600 Hz so phones still convey the dread.
464. **High and pure for cute** — Pitch pup chirps and comic accents at 2–5 kHz with sine-like timbres; brightness plus purity reads as small and endearing.
465. **Character pitch homes** — Assign each recurring character a home pitch range and keep their SFX inside it so viewers know who acted without looking.
466. **Faster means higher** — Raise pitch 1–4 semitones on faster versions of a movement sound; perceived velocity and pitch are linked.
467. **Doppler on fly-bys** — Add a 1–3 semitone pitch drop at the closest point of any fly-by to sell motion past the camera, even in flat 2D.
468. **Tune tonal SFX to the score** — Tune pops, chimes and boings to the music's key or root, detuning only on purpose for comic sourness or tension.
469. **Wobble for uncertainty** — Add slow pitch wobble (2–4 Hz, ±30–80 cents) on dizzy, confused or unsteady moments.
470. **Stepped pitch for building sequences** — Raise each successive repeated pop by a semitone or whole tone so a series of appearances feels like it is building.

### Whooshes and swishes

471. **Whoosh = swept band-passed noise** — Build whooshes from pink noise through a band-pass whose center sweeps roughly 300 Hz → 3 kHz → 600 Hz under a rise-peak-fall envelope.
472. **Peak on the motion peak** — Put the whoosh's loudest point on the cut or the frame of fastest motion, with about 70% of its duration before the peak.
473. **Length matches the move** — Use 150–250 ms whooshes for snap cuts, 400–800 ms for pans, and up to 1.5 s for slow push-ins.
474. **Swish versus whoosh** — Keep swishes (tails, arms, quick turns) short and bright at 80–200 ms and 2–6 kHz; keep whooshes (camera, bodies) longer and broader.
475. **Tonal core for direction** — Add a faint swept sine or saw about 12 dB under the noise to give whooshes pitch direction and a designed, non-windy character.
476. **Land the whip-pan** — End whip pans with a soft 5–10 ms tick or thud on the landing frame so the camera arrives instead of just fading out.
477. **Mono-safe whooshes** — Avoid wide decorrelated stereo noise in whooshes; it partially cancels when summed to mono on phone speakers, so keep the core mono.
478. **Flutter in feathered motion** — Amplitude-modulate whooshes at 20–60 Hz for feathered or flapping movers, raising the rate as speed increases.
479. **Frequency mirrors direction** — Sweep the whoosh filter downward for dives and drops and upward for launches and reveals.
480. **Mover size in the band** — Center large-mover whooshes low and wide (hawk: 200–1500 Hz) and small darts high and narrow (drongo: 1.5–6 kHz).
481. **Not every cut gets a whoosh** — Reserve whooshes for cuts with motion or emphasis; whooshing every cut in a 60-second short turns them into noise wallpaper.
482. **Reverse-tail suck-ins** — Create suck-in transitions by reversing a 300–600 ms decaying noise burst so energy rushes into the next shot's first frame.
483. **Zoom pitch direction** — Sweep zoom-in whooshes up (+5 to +12 semitones) and zoom-outs down to match perceived approach and retreat.
484. **Q sets material** — Use broad, low-Q (~0.7) noise for airy camera moves and narrower Q (3–6) for whippy objects like tails and sticks.
485. **Hand off whoosh to impact** — End or duck the whoosh tail by ~10 dB within 0–20 ms of an impact transient so the hit lands clean.
486. **Spectral tilt sets weight** — Use brown-leaning noise for heavy, slow moves and white-to-blue-leaning noise for small, quick flicks.
487. **Spins as chained swishes** — For spins and tumbles, chain 3–6 short swishes with rising rate and pitch, or amplitude-modulate a whoosh at the spin frequency.
488. **Smear frames get streaks** — When animation shows speed lines or smear frames, add a brief noise streak high-passed above 2 kHz lasting exactly the smear.
489. **Render whoosh sets, don't stretch** — Generate each whoosh type in short, medium and long versions from one parameterized function so editing never needs time-stretching.
490. **Wind-up then release** — Precede a dash with a 150–300 ms low swell, then a sharp high whoosh, mirroring animation's anticipation-then-action poses.

### Impacts, pops and squash-and-stretch

491. **Core impact recipe** — Build impacts from a noise-click transient, a pitch-dropping sine thump (e.g., 120→50 Hz over 60 ms) and a filtered noise tail, varying each for material.
492. **The pitch-drop thump** — Sweep the body sine exponentially from 2–3× down to its final pitch in 20–80 ms; this is the core of every punchy thud.
493. **Soft versus hard contact** — For soft impacts, low-pass the transient near 2 kHz with a ~5 ms attack; for hard impacts, keep a full-band 0 ms transient.
494. **Cartoon pop recipe** — Make pops from a 10–40 ms sine swept upward (e.g., 400→1200 Hz) with fast decay plus a 2 ms click, scaling sweep range with size.
495. **Bloop pop** — Create mouth or bubble "bloops" by sweeping a sine up quickly while amplitude falls exponentially, imitating a shrinking resonant cavity.
496. **Squash sound** — Sell squash frames with a 60–120 ms downward-pitched soft body of low-passed noise (200–800 Hz) and a slight "oomph" formant.
497. **Stretch sound** — Sell stretch with a rising, slightly creaky tone (saw 200→600 Hz through a narrow band-pass, 100–300 ms), like rubber pulling.
498. **Boing for rebound** — Synthesize boings as a 150–400 Hz sine with 6–10 Hz vibrato whose depth decays over 300–600 ms.
499. **Bounces decay geometrically** — Drop each successive bounce 3–5 dB, shorten the interval by ×0.6–0.7, and raise pitch slightly as energy is lost.
500. **Honor hit-stop frames** — During animation hit-stop, hold the impact's ring for 50–100 ms, then release the tail, so audio respects the visual pause.
501. **Body-fall versus object-drop** — Give bodies landing a soft, broad thump with rustle; give objects a sharper, pitched hit with a modal ring.
502. **Material by modal tuning** — Tune modal partials per material: chitin around 2–5 kHz with very short ring, pebbles 1.5–4 kHz with brief ring, twigs 600 Hz–2 kHz heavily damped.
503. **Impact size ladder** — Define small, medium and large impacts with fixed steps (about −7 semitones and 1.6× decay per step) so size reads consistently across the film.
504. **Pre-impact vacuum** — Precede big cartoon impacts with a 30–80 ms dip to silence or a reversed micro-swell; contrast makes the hit feel harder.
505. **Saturation, not gore** — Get punch from gentle saturation rather than realistic crunch so predator-prey hits stay comic and family-friendly.
506. **Head bonk** — Build bonks from a hollow wood-block tone (click through a 700–1200 Hz band-pass, Q ~15) plus a short downward pitch tail.
507. **Seeing stars** — Follow dazed impacts with a soft triangle or FM bell trill at 2–4 kHz alternating two notes at 8–12 Hz.
508. **Splat** — Build splats from a broadband noise burst through a low-pass closing fast (6 kHz → 400 Hz in 80 ms) plus a few scattered droplet grains.
509. **Debris settle** — After big impacts, scatter 3–10 tiny pebble ticks over 200–500 ms with random timing and decreasing level.
510. **Pop-in and pop-out** — Give characters appearing an upward-swept pop with a 30 ms air puff, and disappearing a downward-swept version.

### Cartoon physics: falling, scurrying, diving, digging, sand

511. **Falling whistle** — Synthesize falls as a sine gliding exponentially from about 2 kHz down to 400 Hz over the fall, with subtle 5 Hz vibrato.
512. **Whistle ends before landing** — Compute the glide length from the fall's frame count and end it 1–2 frames before landing to leave room for the impact.
513. **Distance in the fall** — Progressively low-pass and attenuate a whistle as the faller recedes, or brighten and raise it as it approaches camera.
514. **Drop = release + gap + land** — Treat drops as a tiny release tick or swish, silence scaled to height, then a landing impact.
515. **Meerkat scurry rhythm** — Build scurries from soft pats at 8–14 per second with ±15% timing jitter and alternating 1–2 dB level differences for left and right feet.
516. **Glue scurries with a sand bed** — Layer scurry pats over a quiet continuous granular sand hiss so fast runs feel connected rather than machine-gunned.
517. **Beetle skitter** — Make beetle skitters from 1–3 ms clicks at 20–40 per second, band-passed at 3–7 kHz, in irregular bursts.
518. **Scorpion gait** — Give scorpions slower, deliberate chitin click-scrapes: tight clicks plus a narrow noise scrape at 2–4 kHz, fewer and heavier than beetle steps.
519. **Lizard dash and freeze** — Give lizards a light, fast patter (16–20 steps/s, high-passed above 1 kHz) ending in a sharp stop click when they freeze.
520. **Hawk dive** — Build a dive from a falling-band whoosh whose amplitude and flutter rate accelerate over 300–700 ms, cutting hard into the strike or the miss.
521. **Digging strokes** — Synthesize digging as 80–150 ms granular sand bursts at 4–8 per second, each with a low-passed thump onset and a scatter of thrown grains.
522. **Depth changes the dig** — As a hole deepens, lower the low-pass cutoff and add slight comb-filter coloration to imply the enclosed space.
523. **Sand pour** — Synthesize pouring sand as dense granular noise (1000–3000 grains/s) high-passed at ~1.5 kHz, with density tracking the visible flow.
524. **Dust puff on landing** — Add a 100–200 ms high-passed noise puff after landings in sand to sell the dust cloud.
525. **Sand is soft** — Keep sand impact transients rounded (low-pass at 3–4 kHz, 3–5 ms attack) and rely on grainy tails to separate sand from rock.
526. **Dune slide** — Make slides from continuous band-passed noise with slow random filter wander at 0.5–2 Hz and level tied to slide speed.
527. **Burrow emergence** — Pair a meerkat popping out with an upward pop, a granular sand-spill tail and a faint comb-filtered hollow tone for the tunnel.
528. **Burrow retreat** — Use a fast downward swish into a muffled thump low-passed near 800 Hz and comb-colored to place it underground.
529. **Mid-air hang** — When a character hangs before falling, drop all motion sound to silence or a thin high sine, then start the fall whistle on release.
530. **Skid stop** — Build skids from rising-then-falling band-passed noise at 1–3 kHz over 200–500 ms, ending in a scatter of sand grains.
531. **Tumble roll** — Make tumbles from irregular soft thumps at 4–8 per second with alternating pitch over a steady sand hiss, intervals randomized ±25%.
532. **Jiggle after contact** — After a bump, add a decaying 4–8 Hz amplitude wobble on a low tone for the struck object's jiggle.
533. **Gravity in the glide** — Make the fall glide steepen toward the end so pitch acceleration matches the visible acceleration under gravity.
534. **Scrabbling claws** — Make frantic scrabbling from irregular high clicks (3–6 kHz, 15–30 per second) mixed with short noise scrapes.
535. **Kicked sand** — Model kicked sand as a short broadband burst followed by a grain spray whose density decays over 300–600 ms.

### Creature vocalizations

536. **Birdsong from swept sines** — Build bird calls from sines with fast frequency sweeps of 1–3 kHz over 20–100 ms, each syllable with its own amplitude envelope.
537. **Syllable rhythm identifies** — Structure calls as 30–200 ms syllables separated by 20–80 ms gaps; the rhythm pattern identifies a species as much as pitch does.
538. **Drongo signature voice** — Give the drongo a bright, metallic signature from FM chirps (ratio ~1:2) with nasal harmonics at 2–4 kHz, distinct from anything it mimics.
539. **Mimicry reuses the original recipe** — When the drongo mimics, run the exact recipe of the copied call, adding only a subtle tell such as a faint metallic FM edge or +1 semitone.
540. **Reveal the trick sonically** — When the deception is revealed, replay the mimicked call and crossfade it into the drongo's own timbre over 200–400 ms.
541. **Meerkat alarm bark** — Synthesize alarm barks as 80–150 ms noisy bursts band-passed around 1–2 kHz over a harmonic buzz, with an abrupt onset.
542. **Urgency through call rate** — Encode urgency with bark rate: 2–3 per second for watchful, 5–8 per second for imminent danger.
543. **Two alarm codes** — Make aerial-predator alarms harsher, higher and noisier, and ground-predator alarms lower, more tonal and rhythmic, so viewers learn both codes.
544. **Contact chirps** — Make calm foraging chirps as soft 30–60 ms sine blips at 1–3 kHz with small upward glides, scattered irregularly.
545. **Pup begging** — Give pups high, wavering squeaks at 3–5 kHz with strong vibrato, repeated 4–6 times per second, to sell hunger and vulnerability.
546. **Hawk cry recipe** — Synthesize hawk screams as a descending glide (e.g., 3.2 → 2.2 kHz over 400–800 ms) with a raspy noise component and a strong attack.
547. **Rasp by modulation** — Add rasp by amplitude-modulating the tone with band-passed noise or a 60–120 Hz square wave for a grainy, harsh edge.
548. **Distance in a call** — For distant calls, low-pass at 3–5 kHz, soften the attack and add a short diffuse tail; keep close calls full-band and dry.
549. **Predator cries vary hard** — Make every hawk cry instance noticeably different in contour and length; a repeated identical scream loses its menace at once.
550. **Beetle flight buzz** — Make beetle flight from a 100–200 Hz saw amplitude-modulated at wingbeat rate, band-passed at 400–1500 Hz, with slight Doppler on passes.
551. **Scorpion threat** — Build scorpion threat sounds from dense stridulation clicks repeating at 50–100 Hz, band-passed at 3–6 kHz, swelling in level.
552. **Lizards stay near-silent** — Keep lizard vocals minimal: tiny mouth clicks and a dry 2–6 kHz noise hiss reserved for rare expressive beats.
553. **Wordless reactions** — Give characters small gasps, hmms and yelps synthesized through formant filters so emotion reads without adding words that compete with narration.
554. **Contour tells mood** — Shape call contours deliberately: rising for questioning or alert, falling for content or defeat, rise-fall for excitement.
555. **Breaths before big calls** — Add a 100–250 ms filtered noise inhale (band-pass 1–3 kHz) before major vocalizations so synthesized creatures feel alive.
556. **Individuals in a chorus** — When several meerkats call, offset each one's fundamental by 1–3 semitones and vary timbre so the group sounds like individuals.
557. **Drongo scold chatter** — Build scolding chatters from harsh noisy-FM syllables at 8–15 per second with a descending overall pitch.
558. **Calls sync to mouth frames** — Start each syllable on the frame the beak or mouth opens and end on closure; a one-frame miss reads as bad dubbing.
559. **Anchor to real ranges, then exaggerate** — Start from approximate real ranges (meerkat calls ~0.5–4 kHz, drongo ~1–6 kHz, raptor screams ~2–4 kHz) before stylizing.
560. **Comic yelp** — For startled characters, use a fast upward glide of +12 semitones in 60–100 ms with a squeaky formant and abrupt cutoff.

### Foley: steps, feathers, wings, bodies

561. **Sand footstep recipe** — Build a sand step from a soft 100–250 Hz thump (~30 ms) plus a 40–120 ms granular crunch at 2–6 kHz with randomized grain timing.
562. **Compound steps for bigger feet** — Give larger creatures a two-part step (impact, then a grain roll-off 30–60 ms later); small creatures get one compact tick.
563. **Step weight by thump** — Scale step weight through thump pitch and level: meerkat light at ~250 Hz, hawk landing heavier at ~120 Hz, beetle with no thump.
564. **Steps on contact frames** — Sync steps to foot-contact frames; with ambiguous stick-figure walks, place each step on the lowest pose of the cycle.
565. **Surface variants** — Build separate recipes for loose sand, packed sand, rock and dry grass so terrain changes are audible within a scene.
566. **Feather rustle** — Synthesize rustles from 2–8 kHz band-passed noise with rapid irregular 10–30 ms micro-bursts mimicking overlapping feather friction.
567. **Wing flap recipe** — Make each flap a 60–150 ms "whump" of 200–1200 Hz band-passed noise with fast attack and soft decay, topped with a high feather flutter.
568. **Flap rate matches size** — Use roughly 2–4 flaps/s for hawks, 6–10 for drongos and a 50–100 Hz buzz for beetles; size and rate must agree.
569. **Takeoff loud, glide quiet** — Make takeoffs loud with accelerating flaps, and glides nearly silent with a faint air whisper; the contrast sells flight.
570. **Landing flutter** — End bird landings with 2–3 rapid decreasing flaps, a small talon tick and a brief feather-settle rustle.
571. **Body and fur movement** — Give meerkat gestures soft brushed noise at 1–4 kHz with gentle 20 ms attacks so movement is never fully silent.
572. **Scratching and grooming** — Build scratches from band-passed noise strokes at 6–10 per second alternating between ~2.5 kHz and ~4.5 kHz centers.
573. **Crunching prey** — Make beetle crunches from modal chitin clicks at 3–6 kHz followed by small irregular noise crumbles, kept comic rather than gross.
574. **Talon and claw ticks** — Model talons on rock or branches as tiny modal clicks (2–5 kHz, 10–30 ms decay) with slight random pitch per contact.
575. **Foley detail matches visual detail** — Stick-figure animation needs clean, iconic foley; dense realistic layers imply texture the picture doesn't show.

### UI, text, captions and stingers

576. **Caption pop recipe** — Make caption pops as 20–50 ms sine blips at 800–1500 Hz with a 1 ms click attack, soft enough not to fight the narrator.
577. **UI sounds are cleaner than the world** — Give graphics sounds purer, more synthetic timbres (sines, quantized pitches) than creatures and foley so viewers parse them as overlays.
578. **Pitch ladders for lists** — For items appearing in sequence, ascend a pentatonic scale (e.g., 880, 990, 1110, 1320 Hz), one note per item.
579. **Stinger anatomy** — Build graphic stingers from a transient hit, a fifth- or octave-based tonal swell and a 300–800 ms shimmer tail, totaling under 1.5 s.
580. **Weight by hierarchy** — Give title cards a full stinger with sub-thump and harmonic body, and minor labels only a small blip.
581. **Fact-card ding** — Use a short FM bell (carrier 1–2 kHz, ratio 1:3.5, index decaying over ~300 ms) for "did you know" reveals.
582. **Arrows and lines zip** — Give animated arrows and map lines a quick rising zip (+7 semitone sweep in 80–150 ms) ending on arrival.
583. **Highlight sparkle** — Give circles and highlights a soft granular sparkle (sine grains at 3–8 kHz, 20–40 grains/s) lasting the draw-on.
584. **Quiet type-on clicks** — For typed text, use very quiet 5–15 ms clicks with ±2 semitone random pitch, one per word or character group rather than per letter.
585. **Wrong-answer stinger** — Signal a failed trick or wrong guess with two descending buzzy square-wave notes a tritone or minor second apart, about 150 ms each.

### Variation and anti-repetition

586. **Round-robin pools** — Render 4–8 variations of every repeated SFX (steps, pats, clicks, chirps) and cycle through them.
587. **Pitch randomization ranges** — Randomize pitch ±0.5–2 semitones per instance for steps and clicks, up to ±3 for chaotic textures, and less for tonal UI.
588. **Timing jitter** — Offset repeated events ±5–15 ms from the grid to avoid machine-gunning, except where tight sync is the point.
589. **Level randomization** — Vary amplitude ±1–3 dB per instance; identical levels are a strong copy-paste giveaway.
590. **Vary the recipe, not just playback** — Randomize synthesis parameters per variation (filter center ±10%, decay ±20%, new grain seed) instead of pitch-shifting one master.
591. **Never repeat the last pick** — Use shuffle-without-replacement selection so the same variation never plays twice in a row.
592. **Vary transients most** — Listeners detect repetition mostly in transients, so prioritize click shape and noise-seed variation over tail variation.
593. **Re-render instead of stretching** — Regenerate procedural assets at the needed length rather than time-stretching, whose artifacts are obvious on bright content.
594. **Signatures stay consistent** — Keep signature sounds (drongo call, alarm bark) recognizably stable while varying incidental ones, so any repetition is clearly intentional.
595. **Audit for loops** — Watch the short on repeat at least three times and flag any sound that noticeably repeats; looping Shorts playback exposes repetition fast.

### Exaggeration versus realism

596. **Truth of feeling over physics** — Design sounds for how the moment should feel; a tiny meerkat may land like a sack of flour if the comedy demands it.
597. **Real anchor, one exaggerated dimension** — Start from a realistic recipe and exaggerate one dimension (pitch range, attack, decay) by 2–4×, keeping the rest grounded.
598. **Match the art's abstraction** — Stick-figure visuals pair best with simple, iconic, slightly synthetic sounds; ultra-realistic foley creates a stylistic mismatch.
599. **Danger stays real-ish** — Keep threat sounds (hawk, scorpion) more realistic and less comic than gags so stakes stay believable in the cartoon world.
600. **One exaggeration per beat** — Exaggerate only the hero sound in a moment; if everything is cartoonish at once, nothing reads as the joke.
