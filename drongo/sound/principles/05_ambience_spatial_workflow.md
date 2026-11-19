## Part 5 — Ambience, Space, Perspective, Workflow & Delivery (801–1000)

801. **Never true silence** — Keep at least a −60 dBFS room-tone bed under every scene so narration pauses never drop into digital zero, which reads as a dropout on phones.
802. **Ambience is a floor, not a feature** — Sit ambience beds 18–24 dB below narration peaks so they are felt in pauses and vanish under speech.
803. **Generate long, loop-free beds** — Synthesize each ambience as a 60–90 s non-repeating render with randomized event timing so no loop seam is audible across the 3-minute runtime.
804. **Crossfade any unavoidable loop** — If a bed must loop, use an equal-power crossfade of at least 2 s at a low-energy point to hide the seam.
805. **Desert wind from shaped noise** — Build wind from pink noise through a 200–1200 Hz band-pass whose centre and gain drift with a 0.05–0.2 Hz random LFO.
806. **Layer wind in three bands** — Combine a low rumble (<150 Hz), a mid body (300–900 Hz) and a high whistle/sand-hiss (3–8 kHz), each with independent movement.
807. **Gust envelopes are asymmetric** — Shape gusts with a 1–3 s rise and a 3–6 s decay so wind breathes naturally instead of pulsing.
808. **Sand hiss rides the gusts** — Couple a faint 5–10 kHz granular sand-grain layer to gust intensity so stronger wind audibly carries grit.
809. **High-pass wind for phones** — Cut wind rumble below 80–100 Hz since phone speakers cannot reproduce it and it only eats headroom.
810. **Dawn is cool and sparse** — Make the dawn bed quiet (−30 dBFS RMS), low wind, isolated bird calls and long gaps that suggest cold, still air.
811. **Midday is dense and static** — Use a steady insect drone, minimal wind and almost no birds at midday to convey oppressive heat.
812. **Heat as a sustained shimmer** — Suggest heat with a very quiet 4–8 kHz filtered-noise shimmer with slow 0.3 Hz amplitude wobble rather than any literal sound.
813. **Cicada-style insect drones** — Synthesize insects as 4–7 kHz carriers amplitude-modulated at 20–60 Hz, with several detuned voices for a chorus.
814. **Insects swell with temperature** — Raise insect density and level gradually from dawn to midday, by roughly 6–9 dB over the time-of-day arc.
815. **Crickets for cool hours** — Use 3–5 kHz pulsed chirps at 2–4 Hz repetition for dawn or burrow-mouth night tones, stopping as the sun climbs.
816. **Distant birds as punctuation** — Place one distant call every 4–12 s at random, never on a fixed grid, so the world feels alive without competing.
817. **Distant birds are thin and wet** — Treat far calls with a 3–4 kHz low-pass, −20 dB level and a higher reverb ratio than near sounds.
818. **Avoid ambience in the narration band clutter** — Notch or dip ambience by 3–4 dB in 1–4 kHz whenever narration is active to keep consonants clear.
819. **Duck ambience gently** — Sidechain beds to narration with 3–6 dB of reduction, 50 ms attack and 400–800 ms release so ducking is never heard pumping.
820. **Ambience swells in narration gaps** — Let the bed rise 2–3 dB over 1 s in pauses longer than 2 s to remind viewers where they are.
821. **One signature sound per location** — Give each location a recognizable motif, such as a specific insect pitch at the waterhole, so viewers identify places by ear.
822. **Worldbuilding by off-screen life** — Add occasional off-screen events like a distant jackal yip or rustling grass to imply a wider ecosystem beyond the frame.
823. **Keep the world consistent** — Reuse the same seeded ambience generator for a location across scenes so returning there sounds identical.
824. **Seed every random generator** — Fix numpy random seeds per ambience layer so renders are reproducible and revisions do not shift texture.
825. **Time-of-day as a slow crossfade** — Transition dawn to midday beds over 8–15 s of story time rather than hard cuts, unless the edit itself jumps in time.
826. **Time jumps get hard ambience cuts** — When the picture jumps forward in time, cut the bed on the picture cut to sell the elapsed time.
827. **Dawn chorus builds** — Start dawn with one or two birds and add a voice every few seconds so the soundscape visibly wakes up with the light.
828. **Temperature through spectrum** — Tilt cool scenes slightly darker (−2 dB above 6 kHz) and hot scenes slightly brighter and hazier to reinforce the colour grade.
829. **Sky scenes need air** — Build open-sky beds from high, thin wind (2–6 kHz) with almost no low end to convey altitude.
830. **Hawk-filled sky has distant cries** — Scatter far hawk calls panned wide and low-passed at 5 kHz to establish many predators without cluttering the centre.
831. **Underground tone is low and close** — Make burrow room tone a dark 60–300 Hz rumble with almost no high frequencies and no wind.
832. **Burrows muffle the outside** — Feed the surface bed into burrow scenes through a 400–600 Hz low-pass at −15 to −20 dB so the world above is still present.
833. **Earth absorbs high frequencies** — Treat any sound passing through soil with a steep 24 dB/oct low-pass around 500 Hz.
834. **Ambience level tracks shot size** — Raise ambience 3–4 dB on wide shots and lower it on close-ups to match the camera's implied distance.
835. **Distance equals high-cut** — Apply a low-pass that falls from 16 kHz at close range to around 3–5 kHz at far distance to mimic air absorption.
836. **Distance equals level** — Drop level roughly 6 dB per doubling of distance as a starting point, then adjust by ear.
837. **Distance equals wet/dry ratio** — Increase reverb-to-direct ratio as sources recede, keeping close sources nearly dry.
838. **Distance softens transients** — Smooth attacks of far sounds with a 5–15 ms attack slope since distance blurs sharp onsets.
839. **Pre-delay reveals proximity** — Use longer reverb pre-delay (20–40 ms) for close sources in a space and shorter pre-delay for distant ones.
840. **Approach with automation, not steps** — Animate filter, level and wetness together on approaching or receding sources so all three cues move in lockstep.
841. **Doppler only when it reads** — Add a subtle pitch shift of 2–5% only for fast flybys like a diving hawk; skip it for slow movement.
842. **Close-ups get presence** — Boost 2–4 kHz by 1–2 dB and remove reverb on extreme close-ups to place the source right at the viewer's ear.
843. **Close-up detail layers** — On close-ups, reveal micro-sounds such as whisker brushes or breath that are muted on wider shots.
844. **Pan to screen position** — Map a sound's horizontal position on the 1080-wide frame to pan, but keep the range narrow because vertical video is a slim window.
845. **Limit pan width in vertical video** — Restrict on-screen sources to about ±30% pan, since full hard pans feel detached from a narrow 9:16 image.
846. **Use equal-power panning** — Pan with a −3 dB centre law (sin/cos) so sources do not dip or bulge in level as they move.
847. **Off-screen sounds go wider** — Place off-screen sources at ±60–80% pan to signal they sit beyond the frame edges.
848. **Narration stays dead centre** — Keep narration mono and centred at all times; never pan, widen or reverb it with scene spaces.
849. **Low end stays centred** — Keep everything below 150 Hz mono so earbuds and single phone speakers reproduce bass consistently.
850. **Movement panning is slow** — Animate pans over at least 300 ms with smoothed curves to avoid zipper noise and jumpy imaging.
851. **Decorrelate ambience for width** — Build stereo beds from independently generated left and right noise sources rather than duplicating one channel.
852. **Cap stereo width** — Keep ambience inter-channel correlation above roughly +0.3 so the image stays wide but folds down safely.
853. **Check mono fold-down every scene** — Sum L+R and listen; any element that thins out or disappears needs its width reduced.
854. **Avoid Haas widening on key sounds** — Do not use 10–30 ms inter-channel delays on story-critical sounds since they comb-filter in mono.
855. **Mono speaker reality** — Assume many phones play one speaker or a summed mix, so every story-critical cue must be audible in mono.
856. **Mid/side for safe width** — Widen ambience by raising side gain at most 3 dB in M/S rather than with phase tricks.
857. **No phase-inverted layers** — Never polarity-flip a channel for effect; it cancels completely on mono playback.
858. **Correlation meter in the render script** — Compute per-section L/R correlation in Python and flag any window below 0 for review.
859. **Reverb defines the space** — Choose one reverb profile per location and apply it consistently to every sound in that location.
860. **Open desert is nearly dry** — Use almost no reverb outdoors, maybe a faint 1–2 s very low-level slapback from distant dunes, because open sand has few reflections.
861. **Distant echo over open plains** — For a shout or call across the desert, add a single delayed repeat at 150–400 ms, −12 to −18 dB, low-passed at 3 kHz.
862. **Burrows are small, dark and short** — Give burrow reverb a 0.2–0.5 s decay, dense early reflections and a high-frequency roll-off above 3 kHz.
863. **Burrow tunnels add resonance** — Add a gentle 150–400 Hz resonant peak to burrow reverb to convey a narrow earthen tube.
864. **Deeper burrow, darker sound** — Lower the low-pass and raise wetness progressively as characters move deeper underground.
865. **Convolution from synthetic IRs** — Generate impulse responses as exponentially decaying filtered noise in numpy and apply with scipy.signal.fftconvolve.
866. **Shape IR decay per band** — Make high frequencies in synthetic IRs decay 2–3× faster than lows to mimic natural absorption.
867. **Early reflections sell size** — Add 3–6 discrete early reflections within 5–30 ms for small spaces and 30–80 ms for larger ones.
868. **Reverb returns get EQ** — High-pass reverb returns at 200–300 Hz to keep low-end mud out of phone speakers.
869. **Avoid reverb tails over narration** — Tame or duck reverb returns by 4–6 dB under narration so tails never smear words.
870. **Sky has no reverb** — Keep mid-air sky scenes dry with only distance filtering, because there are no reflective surfaces in open air.
871. **Underground POV shift** — When the camera drops underground, low-pass the surface world to ~500 Hz and reveal burrow tone within 200–400 ms.
872. **Surfacing reveals the world** — When emerging from a burrow, open the low-pass from 500 Hz to full range over 0.5–1 s for a satisfying reveal.
873. **Sky POV is wide and thin** — When the camera rises to a hawk's view, widen ambience, drop low end and pull ground sounds down by 10–15 dB.
874. **Predator POV narrows** — In a hawk's hunting POV, narrow the stereo image and focus on the target sound to suggest locked attention.
875. **Close-up POV isolates** — On subjective close-ups, cut ambience by 6–10 dB to put the viewer inside the character's focus.
876. **Fear narrows perception** — In tense moments, low-pass ambience progressively toward 2 kHz to simulate tunnel hearing, then release when tension breaks.
877. **POV changes are cut-synced** — Make perspective changes land within one frame (about 33 ms at 30 fps) of the picture cut.
878. **Pre-lap the next space** — Start the next location's ambience 6–12 frames before the cut to pull viewers forward smoothly.
879. **Post-lap a departing space** — Let a previous space's tail ring 0.3–1 s past the cut for gentle exits in calm moments.
880. **Hard cuts for shocks** — Use instant ambience cuts with no crossfade when the edit is meant to jolt the viewer.
881. **Crossfade spaces with equal power** — Use equal-power curves for ambience crossfades longer than 200 ms to avoid a mid-fade level dip.
882. **Short fades on every edit** — Apply at least 5–10 ms fades on every clip boundary to prevent clicks.
883. **Transition through a filter sweep** — Bridge surface-to-burrow transitions with a 0.5 s low-pass sweep rather than a simple crossfade.
884. **Whoosh-free transitions by default** — Prefer ambience-driven transitions over whooshes so spatial changes feel organic and narration is not covered.
885. **Match ambience across shots** — Keep beds continuous across cuts within the same location so edits are invisible.
886. **Never restart the bed on a cut** — Continue the same ambience timeline across shots in one location instead of retriggering from the beginning.
887. **Ambience ends with the story** — Fade the final bed over 1.5–3 s rather than truncating it with the last frame.
888. **Start with ambience before the hook** — Bring in the ambience at frame 0 at full level so the opening second already places the viewer in the Kalahari.
889. **Ambience moves with camera moves** — On a pan or tilt, shift ambience balance or pan slightly in the camera's direction to anchor the move.
890. **Vertical camera moves change spectrum** — Tilting up toward the sky can lighten low end; tilting down toward sand can add grit and warmth.
891. **Elevation cues are spectral** — Suggest sounds above with a slight 7–9 kHz lift and sounds below with a dull, low-passed tone.
892. **Ambience detail for earbuds** — Include subtle stereo micro-detail that earbud listeners notice, while ensuring phone-speaker listeners lose nothing essential.
893. **Masking checks for beds** — Solo narration plus ambience and confirm every syllable is intelligible before adding any other layers.
894. **Avoid tonal ambience clashes** — Keep insect drones and resonances away from the narrator's fundamental (about 90–250 Hz) and from the music key's tonic if audible.
895. **Ambience is per-scene stem** — Render ambience for each location as its own stem so space and perspective can be rebalanced without re-rendering.
896. **Document each space's recipe** — Store each location's ambience and reverb parameters in a Python dict or JSON preset for reuse.
897. **Spatial consistency pass** — Watch the full piece once listening only to ambience and reverb, checking each space stays coherent.
898. **Less space on small speakers** — Reduce reverb wetness by about 20% in the final mix since phone speakers exaggerate reverb muddiness relative to studio monitors.
899. **Silence as a spatial event** — Drop ambience abruptly by 10–15 dB for one beat before a hawk strike to make the sky feel suddenly empty.
900. **Space serves the voice** — When any spatial effect competes with narration intelligibility, reduce the effect, never the narration.
901. **Spot against the script first** — Hold a spotting session with the locked script and animatic, marking every sound need before generating any audio.
902. **Spot in three passes** — Spot narration-critical cues first, then ambience and spaces, then detail sounds, so priorities stay clear.
903. **Timecode every cue** — Log each cue with start time in HH:MM:SS:FF at the project frame rate and an end time or duration.
904. **Cue sheet as data** — Keep the cue sheet as a CSV or JSON with columns for ID, time in, time out, layer, description, location and status.
905. **Cue sheet drives the render** — Have the Python build script read the cue sheet directly so placement is data-driven, not hard-coded.
906. **Stable cue IDs** — Give cues permanent IDs such as SFX_031 or AMB_DAWN_01 that never get renumbered when cues are inserted.
907. **Mark narration-critical cues** — Flag cues that land on or near narration lines so the mixer checks them for masking.
908. **Note intent, not just sound** — Include a short purpose field per cue, such as "sell distance" or "reveal burrow", to guide revisions.
909. **Lock picture before final placement** — Do final sync placement only after the edit is locked, and record the picture version the cues match.
910. **Track picture changes** — When the edit changes, diff the edit decision list and shift affected cues by the exact frame offset.
911. **Consistent file naming** — Name files as project_scene_layer_description_v###.wav, lowercase with underscores and no spaces.
912. **Zero-pad numbers** — Use zero-padded versions and indices like v003 and sc07 so files sort correctly.
913. **No "final" in filenames** — Use version numbers instead of words like final or final2, which become meaningless after revisions.
914. **Fixed folder structure** — Separate folders for src (scripts), presets, renders/stems, renders/mix, refs and deliverables.
915. **Generated audio is disposable** — Treat rendered WAVs as build artefacts reproducible from code and presets, and keep them out of git.
916. **Version code with git** — Commit generator scripts, presets and cue sheets with a message describing each audible change.
917. **Tag delivered versions** — Tag the git commit that produced each uploaded mix, for example mix-v004-published.
918. **Changelog per version** — Keep a short changelog noting what changed in each mix version and why.
919. **Standard stem set** — Render separate stems for narration, dialogue/vocal FX, SFX, ambience and music.
920. **Stems sum to the mix** — Verify stems summed together null against the full mix to within −90 dBFS residual.
921. **Stems share length and start** — Render every stem from time zero to the same sample length so they align without offsets.
922. **Print a narration-free mix** — Export an M&E (music and effects) mix without narration for re-voicing or translation.
923. **Render the deterministic way** — One command should rebuild every stem and the mix from source, so any version can be reproduced exactly.
924. **Log render parameters** — Write a JSON sidecar with each render recording git hash, seeds, sample rate and key settings.
925. **Pick reference tracks** — Choose two or three successful narrated nature shorts as references for balance, ambience density and narration presence.
926. **Level-match references** — Compare against references only after matching integrated loudness to within 0.5 LU, since louder always sounds better.
927. **Compare spectra objectively** — Plot long-term average spectra of your mix and references in Python and investigate differences larger than 3 dB.
928. **Reference the same playback chain** — Listen to references through the same phone and earbuds you use for checking your mix.
929. **Blind A/B where possible** — Randomize which version plays in A/B tests so preference is not biased by knowing which is new.
930. **A/B checklist: narration** — Check that every narration word is intelligible on the first listen without captions.
931. **A/B checklist: balance** — Check that no SFX or music hit masks a word and no layer jumps out unexpectedly.
932. **A/B checklist: space** — Check that each location sounds distinct and consistent and that perspective matches shot size.
933. **A/B checklist: transitions** — Check that every cut is free of clicks, gaps, dips or abrupt bed changes not intended by the story.
934. **A/B checklist: tonal balance** — Check for harshness at 2–5 kHz, boominess at 100–250 Hz and sibilance at 5–8 kHz.
935. **A/B one change at a time** — Change a single variable between versions so you know what caused any improvement.
936. **Rest your ears** — Take a 10-minute break every hour and do critical judgments early in a session before fatigue sets in.
937. **Monitor at moderate level** — Mix at a consistent moderate listening level, around 75–80 dB SPL, and check briefly at low volume.
938. **Listen on phone speakers** — Play the exported file on at least two phone models' built-in speakers, because that is the primary audience.
939. **Listen on cheap earbuds** — Check on inexpensive wired or Bluetooth earbuds for exaggerated stereo, harsh highs or missing ambience.
940. **Listen on good headphones** — Use accurate headphones to catch clicks, noise, distortion and edits that small speakers hide.
941. **Listen on a laptop** — Check on laptop speakers as a mid-range device that exposes low-mid build-up.
942. **Listen in a noisy room** — Play the mix with background noise such as a kitchen or street to confirm narration survives real conditions.
943. **Listen at low volume** — Play at very low volume and confirm narration remains understandable while effects fade gracefully.
944. **Test in-app playback** — Upload a private or draft post and listen inside the TikTok and YouTube apps, since their transcoding changes the sound.
945. **Note device findings** — Record each device's problems in a QC log with timecode before making fixes.
946. **Work at 48 kHz** — Generate and mix at 48 kHz, the video standard, to avoid resampling against picture.
947. **One sample rate everywhere** — Keep every generated layer at the same sample rate; resample any outlier once with scipy.signal.resample_poly.
948. **Process in float** — Do all synthesis and mixing in float32 or float64 numpy arrays to keep headroom and avoid intermediate clipping.
949. **Store masters as 24-bit or 32-bit float** — Write intermediate stems and masters as 24-bit PCM or 32-bit float WAV, never 16-bit.
950. **Oversample nonlinear processes** — Run saturation or clipping-based processing at 2–4× oversampling to avoid aliasing.
951. **Dither only on bit reduction** — Apply TPDF dither only when converting to 16-bit or lower, and only once, as the final step.
952. **TPDF dither recipe** — Add the sum of two independent uniform random arrays of ±0.5 LSB each before rounding to 16-bit integers.
953. **No dither before lossy encode from float** — When feeding AAC directly from a 24-bit or float master, skip dither since the encoder requantizes anyway.
954. **Never clip in float masters** — Check that no master sample exceeds ±1.0 before writing; normalize or limit instead of letting the writer clamp.
955. **Leave true-peak headroom** — Keep master true peak at or below −1 dBTP, measured with 4× oversampling, so AAC encoding does not create overs.
956. **Count clipped samples** — Fail the build if more than zero samples reach ±0.999 full scale in any deliverable.
957. **Detect intersample peaks** — Upsample the master 4× with resample_poly and measure the peak to catch overs that sample peak misses.
958. **Remove DC offset** — High-pass every generated layer at 10–20 Hz or subtract its mean so DC does not waste headroom.
959. **Measure DC on the master** — Fail QC if the mean of either channel exceeds ±0.001 (about −60 dBFS).
960. **Start and end at zero** — Fade every rendered file in and out over at least 5 ms so the first and last samples are zero.
961. **Scan for clicks** — Flag sample-to-sample jumps above a threshold, such as 0.2 in a quiet passage, for manual inspection.
962. **Check for NaN and Inf** — Assert np.isfinite over every rendered array before writing, since a single NaN can silence or corrupt a file.
963. **Check for silent channels** — Verify both channels carry signal and are not accidentally identical when stereo is intended, or opposite in polarity.
964. **Sync to the frame** — Convert all cue times with samples = round(seconds × 48000) and confirm against frame boundaries at the project fps.
965. **Verify sync with a slate** — During development, render a test with a one-frame white flash and a 1 kHz beep at the same timecode and check alignment.
966. **Sync tolerance** — Keep audio within ±1 frame of picture; viewers notice when audio leads by more than about 45 ms or lags beyond 125 ms.
967. **Check sync after encode** — Inspect the final MP4 in a frame-accurate player, since encoding can introduce priming offsets.
968. **Match durations exactly** — Make the audio master the exact length of the video, padding or trimming to the sample, before muxing.
969. **Check stream start times** — Use ffprobe to confirm audio and video streams both start at 0 with no start_time offset.
970. **Use AAC-LC** — Encode delivery audio as AAC-LC, which TikTok and YouTube Shorts both accept and transcode reliably.
971. **Encode at high bitrate** — Use at least 256 kbps stereo AAC (320 kbps if file size allows) to survive platform re-encoding.
972. **Prefer a quality encoder** — Use libfdk_aac if your ffmpeg build has it; otherwise use the native aac encoder at 320 kbps.
973. **Keep 48 kHz stereo on delivery** — Pass -ar 48000 -ac 2 explicitly so ffmpeg does not silently resample or downmix.
974. **Mux without re-encoding video** — When only audio changes, mux with -c:v copy -c:a aac -b:a 320k to avoid an extra video generation loss.
975. **Map streams explicitly** — Use -map 0:v:0 -map 1:a:0 so the right audio track is muxed and stray streams are excluded.
976. **Use -shortest carefully** — Prefer exact-length masters over -shortest, which can trim the final frames or audio tail unexpectedly.
977. **Faststart for uploads** — Add -movflags +faststart so the MP4 index sits at the start and uploads process quickly.
978. **One audio track only** — Deliver a single stereo audio stream since platforms ignore or mishandle additional tracks.
979. **Strip unnecessary metadata** — Use -map_metadata -1 if needed so leftover tags or chapter data do not confuse platform ingest.
980. **Decode the delivery back** — Decode the final MP4 audio to WAV with ffmpeg and re-run peak, DC, NaN and duration checks on it.
981. **Null-test the encode** — Subtract the decoded delivery from the master after alignment and listen to the residual to hear codec artefacts.
982. **Watch for AAC pre-echo** — Listen for smearing before sharp transients like hawk strikes and soften the attack slightly if pre-echo is audible.
983. **Avoid extreme highs into AAC** — Gently low-pass above 18–19 kHz before encoding, since codecs waste bits on content phones cannot play.
984. **Re-check after platform transcode** — Download or screen-record the processed post and compare it to your master for dulling, pumping or lost ambience.
985. **Automate QC in one script** — Run all checks (peaks, true peak, DC, NaN, clipping, length, correlation, sample rate) in a single qc.py that exits non-zero on failure.
986. **QC report per version** — Save the QC output as a text or JSON report alongside each delivered version.
987. **ffprobe the deliverable** — Confirm codec aac, sample_rate 48000, channels 2, bit_rate near target and duration equal to video.
988. **Mind the 9:16 container** — Confirm the final file is 1080×1920 with audio attached, since some pipelines drop audio when re-scaling video.
989. **Check the first second** — Confirm audio starts on frame 0 with no silent lead-in, because platforms autoplay and viewers swipe within a second.
990. **Check the loop point** — Since Shorts and TikTok autoloop, confirm the end-to-start transition has no click and no jarring level jump.
991. **Check caption alignment** — Verify burned-in or auto captions match narration timing, since mismatches look like sync errors.
992. **Mute-safe check** — Watch once muted to confirm the story still reads, then once with eyes closed to confirm the sound tells it too.
993. **Archive the delivery set** — Keep the master WAV, stems, M&E, final MP4, cue sheet, QC report and git hash together per published version.
994. **Pre-publish: narration** — Confirm every line is intelligible on a phone speaker at medium volume in a moderately noisy room.
995. **Pre-publish: technical** — Confirm zero clipped samples, true peak ≤ −1 dBTP, DC within tolerance and no NaN in the decoded deliverable.
996. **Pre-publish: sync** — Confirm audio is within one frame of picture at start, middle and end of the decoded MP4.
997. **Pre-publish: format** — Confirm AAC-LC, 48 kHz, stereo, 256–320 kbps, faststart and exact matching duration.
998. **Pre-publish: mono** — Confirm the mono fold-down keeps every story-critical sound and loses no more than about 3 dB of perceived level.
999. **Pre-publish: devices** — Confirm the final file has been heard on phone speaker, earbuds and headphones with no unresolved QC notes.
1000. **Pre-publish: sign-off** — Publish only when the checklist passes and the version is tagged, so any future fix starts from the exact published source.
