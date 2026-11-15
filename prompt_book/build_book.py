"""Builds PROMPT_BOOK.md, MASTER_PROMPT.md and PROMPT_BOOK.pdf from chapters/ + engine/ + the principles PDF."""
import os, re, sys, subprocess, glob, html
HERE = os.path.dirname(os.path.abspath(__file__))
CH = os.path.join(HERE, 'chapters'); ENG = os.path.join(HERE, 'engine'); BUILD = os.path.join(HERE, 'build')
os.makedirs(BUILD, exist_ok=True)
PRINCIPLES_PDF = sys.argv[1] if len(sys.argv) > 1 else None

# ---------------------------------------------------------------- Part VI: 300 principles
APPLIED = {
 1: "Every effect in the cue sheet is tied to a narrated event; the opening boom + drone establish the sonic world in the first frame.",
 2: "Hook boom on frame 1; contrast resets at chapter turns (music drop at entry, hard cut at signal loss); risers only before real payoffs.",
 3: "VO chain (HPF 70 Hz, +1.5 dB @ 3 kHz, 2.5:1 compression) + automatic ducking keeps every key sentence clear.",
 4: "Delivered voiceover is used as-is; if re-recording, follow these when requesting takes.",
 5: "Effects are placed per cue, never per cut; fades on every clip (`fade_env`) prevent clicks; the narration is never edited.",
 6: "All sounds are synthesized to fit their object: weight and pitch scaled to scale (a probe vs. a planetary event).",
 7: "Impacts = sub pitch-drop (body) + noise burst (attack) + decay (tail); test each layer's contribution.",
 8: "VO high-passed; music ducked under speech; low end reserved for the biggest hits; midrange presence for phones.",
 9: "Ducking with 30 ms attack / 450 ms release; static gain + limiter instead of heavy compression; quiet moments preserved.",
 10: "Final: −14 LUFS integrated, ≤ −1.5 dBTP, measured on the delivered file; settings documented in sfxlib.finish().",
 11: "Tracks chosen per chapter mood by measured energy curve; music absent during entry; licensed tracks only.",
 12: "Cues enter at story turns with phrase-shaped fades; hard cut only for the signal loss; auto-ducking replaces manual rides.",
 13: "Fast sound events in danger, sparse in explanation; three escalating, varied hits for 5/10/15 bar.",
 14: "Near-silence after the signal loss (flatline + low drone), a deliberate design choice, protected from the loudness pass.",
 15: "Whooshes only on whip transitions and real movement; dips to black get bass hits only at chapter changes.",
 16: "Biggest boom on the deceleration; smaller repeat on the repeated number; no giant hits on trivial actions.",
 17: "Whoosh length matches the transition (0.5 s whip, 3 s flyby); peak timed to the fastest motion.",
 18: "Risers used only before the deceleration, metallic hydrogen, the fuzzy core and 'NO.', each ending cleanly at its event.",
 19: "Wind beds inside clouds (darker as depth increases), crackle for conductive fluid, hum for the magnetic field.",
 20: "The parachute snap, hull creaks and small thuds make objects tangible without overdoing mundane motion.",
 21: "Narration kept dry; space suggested by drone stereo offsets rather than reverb.",
 22: "Bass centered; subtle pan drift on whooshes; stereo offset on beds; critical sound mono-safe.",
 23: "Dread built with low drones and creaks before revealing the cause; aftermath silence after the loss.",
 24: "Used sparingly; the 'improvement, right?' beat is carried by the explorer's smile, not a comic sound.",
 25: "Designed sounds never presented as real recordings; historical moments treated with restraint (the probe's loss is solemn).",
 26: "Consistent fictional sonic logic: the capsule's shield = shimmer; instruments = clean sine blips.",
 27: "First second legible (boom + title); quick silences emphasize twists.",
 28: "Audio arc across 12 minutes: documentary → raw physical sound → suspense → silence → documentary → mystery → uplift.",
 29: "Measured QA: LUFS, true peak, window levels at peaks and silences; owner told to listen before publishing.",
 30: "Buses separated (voice, music, sfx, ambience); reusable library (sfxlib) + per-project cue sheet.",
}
def principles_md():
    if not PRINCIPLES_PDF:
        return "# PART VI — THE 300 PRINCIPLES OF SOUND DESIGN\n\n(Principles PDF not supplied at build time.)\n"
    txt = subprocess.run(['pdftotext', PRINCIPLES_PDF, '-'], capture_output=True, text=True).stdout
    lines = [l.strip() for l in txt.splitlines() if l.strip() and 'PRACTICAL FIELD GUIDE' not in l and not re.fullmatch(r'\d+', l.strip())]
    out = ["# PART VI — THE 300 PRINCIPLES OF SOUND DESIGN",
           "",
           "*A practical field guide for YouTube Shorts, long-form videos, animation, documentaries and cinematic storytelling. Use these principles as a decision-making checklist, not as inflexible rules. Effective sound design serves the story, maintains clarity and creates deliberate contrast.*",
           "",
           "Each chapter ends with **How this channel applies it**, showing exactly how the principle set was implemented in the engine and cue sheet.", ""]
    chap = 0
    for l in lines:
        m = re.match(r'^(\d{2}) ([A-Z][A-Z &\-]+)$', l)
        if m:
            if chap:
                out += ["", f"> **How this channel applies it:** {APPLIED[chap]}", ""]
            chap = int(m.group(1))
            out += ["", f"## 6.{chap} {m.group(2).title()}", ""]
            continue
        m = re.match(r'^(\d{3})\. (.*)$', l)
        if m and chap:
            out.append(f"{int(m.group(1))}. {m.group(2)}")
    out += ["", f"> **How this channel applies it:** {APPLIED[chap]}", ""]
    n = sum(1 for l in out if re.match(r'^\d+\. ', l))
    assert n == 300, n
    return "\n".join(out) + "\n"

# ---------------------------------------------------------------- Part IX: worked example
SHOTDESC = {
 's01': ("Hook", "Giant Jupiter + tiny probe with glowing trail; title; 'DEC 7, 1995' callout", "Sub-boom + low drone on frame 1"),
 's02': ("Dropped into Jupiter", "Probe streaks to the limb; entry glow; 'ENTRY SURVIVED' check", "Whoosh, rumble swell, UI pop"),
 's03': ("Winds", "Probe under parachute in shearing clouds; hurricane vs. Galileo wind bars", "Wind bed, pops on the bars"),
 's04': ("No ground", "Vertical descent, rising clouds, scrolling ruler; 'SOLID GROUND: NONE DETECTED'", "Wind, soft alarm"),
 's05': ("58 minutes", "Telemetry monitor: timer to 58:00, waveform flatlines; SIGNAL LOST", "Beeps → static → flatline"),
 's06': ("Barely scratched", "Scale pull-out from ×9 to the full cutaway; deepest-point mark; '≈0.2%'; dashed '?' plunge", "Long whoosh, mystery drone"),
 's07': ("Three questions", "Cards: something solid? / an ocean? / the center? with falling capsule; push into the center card", "Three thuds"),
 's08': ("The plan", "Depth column: solid amber 'real spacecraft' vs. dashed blue 'where no spacecraft has gone'", "Music build"),
 's09': ("Earth vs. Jupiter", "Split screen: capsule lands on Earth; on Jupiter 'GROUND?' gets an X", "Whip whoosh, landing thud"),
 's10': ("Nowhere to land", "Big statement → full rotating Jupiter; band tracers; CHAPTER 01", "Chapter boom"),
 's11': ("Great Red Spot", "Zoom to the GRS; label; Earth to scale; 'STRIPES ≠ GROUND'", "Slow whoosh"),
 's12': ("Clouds move", "Texture strips shear in alternating jets; arrows; 'HUNDREDS km/h'", "Wind"),
 's13': ("1,300 Earths", "Earth to scale; Earth icons fill the disk; counter to 1,300+", "Rising blips with the counter"),
 's14': ("<10 h day", "Fast spin with day ring to 9 h 56 min; jet-stream arrows", "—"),
 's15': ("Juno, 3,000 km", "Planet darkens; Juno flyby; slab cutaway with a wind band and '≈3,000 km' bracket", "Flyby whoosh"),
 's16': ("Storm deep inside", "'3,000 km' number; storm column; plunge zoom + flash", "Boom, riser, flash boom"),
 's17': ("Speed", "Star streaks; counter to 170,000 km/h; '≈47 km every second'", "Counter ticks, approach rumble"),
 's18': ("Entry heating", "Bow-shock arcs, gas arrows converging, heat-shield callout, heat-load bar", "Entry roar builds (music out)"),
 's19': ("Brilliant glow — PEAK", "Screen floods orange-white; plasma streaks; shake", "Roar + riser"),
 's20': ("228 g — PEAK", "Hard shake; gauge slams to 228 g; '× EARTH'S GRAVITY' pulse", "Biggest impact; second hit on the repeat"),
 's21': ("Not survivable", "Three cards crossed out: spacecraft / space suit / holding on", "Thuds"),
 's22': ("Robotic probe", "Heat shield falls away; parachute blooms; radio arcs to the orbiter", "Separation creak, chute snap, beeps"),
 's23': ("Fictional capsule", "Capsule reveal; glow fades; explorer opens eyes", "Downward whoosh"),
 's24': ("No horizon — PEAK", "Explorer looks up / beside / below; pull back; 'HORIZON: NOT FOUND'", "Suspense music in; shimmer + alarm"),
 's25': ("Earth horizon", "Split: Earth sky/ground/horizon vs. Jupiter 'NO HORIZON'", "Cloud wind"),
 's26': ("Instruments", "Bust lit by the instruments: 1.0 bar, −108 °C with frost, H₂/He bars, O₂ NONE, 'OUTSIDE: LETHAL'", "Pops, lethal alarm"),
 's27': ("Warmer, denser", "Readouts climb; '≈ warm day on Earth'; smile → frown; pressure arrows", "Creak"),
 's28': ("5 / 10 / 15 bar", "Numbers slam in on each word; capsule shakes", "Three escalating hits + creaks"),
 's29': ("Expecting an ocean", "Explorer looks down; dashed 'expected ocean' dissolves", "—"),
 's30': ("Galileo measures", "Historical descent module sampling; instruments list; '!'", "Pop"),
 's31': ("Less water / dry spot", "Expected vs. measured bars (schematic) → the entry site in a dry 'hot spot'", "—"),
 's32': ("Desert analogy", "Earth zoom; a weather station in one desert; '1 location ≠ whole planet'", "Whip whoosh"),
 's33': ("Signal lost", "Probe sinks into red; readouts to 22 bar / 152 °C; static burst", "Beeps → static; music hard-cut"),
 's34': ("58 minutes, destroyed", "Solemn timeline bar; probe fades into the dark", "Flatline + dark drone (near-silence)"),
 's35': ("Tiny fraction", "Cutaway with a red mark; depth bar 150 km vs 70,000 km; 'UNEXPLORED ?'", "Soft boom"),
 's36': ("Imaginary probe", "Galileo crossed out → shielded capsule 'IMAGINARY · INDESTRUCTIBLE'", "Thud, shimmer; drama returns"),
 's37': ("Compression", "H₂ molecules crowd; density gauge; 'THOUSANDS bar'; gas → dense-fluid bar", "Low rumble bed"),
 's38': ("No splash", "NO SPLASH / NO WAVE / NO WATER LINE / NO SEPARATE SEA cards", "Four thuds"),
 's39': ("Gradual change", "Gradient column; 'NO SURFACE · NO BOUNDARY'; deep fluid interior", "—"),
 's40': ("Metallic hydrogen — PEAK", "Palette flips to electric blue-violet; electrons stream; title", "Riser → boom + shimmer; crackle bed"),
 's41': ("Misconceptions", "Silver rocks ✕, mercury ocean ✕; 'NOT WHAT SCIENTISTS MEAN'", "Whip whoosh, thuds"),
 's42': ("Conductivity", "Protons + free electrons + current arrow → cutaway with the metallic region highlighted", "Crackle"),
 's43': ("Magnetic field (callback)", "Field lines bloom; radiation belts; labels", "Magnetic hum"),
 's44': ("Dynamo", "Swirls in the conducting layer; field connected to the interior; pull-out", "Hum + crackle"),
 's45': ("The center", "CHAPTER 02; older compact-core model", "Boom; suspense returns"),
 's46': ("Fuzzy core — PEAK", "Juno polar orbit + gravity contours; compact core dissolves into the dilute core", "Riser → shimmer + boom"),
 's47': ("Spread out", "Zoom into the broad core; 'HOW DID IT FORM?'", "—"),
 's48': ("Hypotheses", "Formation disk vs. giant-collision cards, both tagged HYPOTHESIS", "Collision boom"),
 's49': ("Never photographed", "A glowing '?' in darkness; camera ✕", "Thud"),
 's50': ("NO. (callback)", "Opening composition returns; 'WOULD YOU EVENTUALLY LAND?' → giant 'NO.'", "Inspiring music; riser → big boom"),
 's51': ("Recap", "Journey column: real probe ✕ → atmosphere → dense fluid → metal → central structure", "Pops on each station"),
 's52': ("Only clouds", "Jupiter grows; the cutaway opens; 'ALMOST EVERYTHING IS HIDDEN BENEATH'", "—"),
 's53': ("What we can do", "Four cards (storms, gravity, field, predictions) → 'DIRECTLY EXPLORED: ONLY THE TOP SLIVER'", "Pops"),
 's54': ("Night sky ending", "Person on a hill under the stars; Jupiter dot zooms to the planet; final line; end card", "Shimmer; end-card boom; music outro"),
}
def example_md():
    sys.path.insert(0, ENG); sys.path.insert(0, os.path.join(ENG, 'example_jupiter'))
    os.environ['JV_PROJECT'] = os.path.join(ENG, 'example_jupiter')
    import importlib
    shots = []
    for m in ('scenes1', 'scenes2', 'scenes3'):
        mod = importlib.import_module(m)
        for k, v in vars(mod).items():
            if k.startswith('SHOTS'): shots += v
    end_t = importlib.import_module('scenes3').END_T
    shots.sort(key=lambda s: s[0])
    rows = ["| # | Time | In | Shot | Visual | Sound |", "|---|---|---|---|---|---|"]
    for i, (t0, fn, (tt, td)) in enumerate(shots):
        name = fn.__name__; title, vis, snd = SHOTDESC[name]
        rows.append(f"| {i+1:02d} | {int(t0//60)}:{t0%60:04.1f} | {tt} | **{title}** | {vis} | {snd} |")
    return f"""# PART IX — WORKED EXAMPLE: "WHAT IF YOU ACTUALLY FELL INTO JUPITER?"

**Specs:** {int(end_t//60)}:{end_t%60:04.1f} runtime · 54 shots · 44,892 frames · 1920×1080 · 60 fps · H.264 CRF 18 · 186 MB · −14.2 LUFS / −1.4 dBTP · ~120 SFX cues · 3 music tracks · 308 caption lines.

**Inputs:** voiceover (12:20, male documentary voice, 1,535 words); music: *dramatic cinematic documentary*, *suspense cinematic*, *inspiring cinematic*; the Master Prompt V2.0; the 300 Sound Design Principles.

**Chapters and palettes:** Hook & plan (deep space navy + amber) → Nowhere to land (Jupiter amber/cream) → Entry (black → orange-white → red) → Inside the clouds (amber → red-brown, cyan instruments) → Galileo's measurements & loss (sepia amber → black) → Deep interior (dark red → electric violet) → The center (violet + warm cream core) → Answer & ending (navy night sky + warm Jupiter).

## 9.1 Complete shot map (start times from the narration)

{chr(10).join(rows)}

## 9.2 Visual peaks and callbacks

Peaks: s01 tiny probe · s19–s20 glow + 228 g · s24 no horizon · s40 metallic hydrogen · s46 fuzzy core. Callbacks: s50 restages s01 for the answer; s43–s44 connect the interior to the magnetic field and radiation from the opening chapters; s54 returns to the viewer's own sky.

## 9.3 Honesty decisions made

- Great Red Spot texture sized to about 17,000 km so the to-scale Earth is truthful; "observed for centuries".
- Winds labeled "Galileo-measured up to ~650 km/h" against "strong Earth hurricane ~250+ km/h".
- Depth, pressure and temperature readouts marked "≈, below 1-bar"; the Galileo probe's last values ≈22 bar, ≈152 °C, ≈150 km.
- Water chart labeled "schematic · not exact values"; entry site described as a rare, unusually dry "hot spot".
- Interior always `MODEL-BASED · NOT TO SCALE`; hypotheses tagged `HYPOTHESIS`; the center shown as an unphotographed "?".
- Fictional capsule tagged "FICTIONAL CAPSULE · NOT REAL TECHNOLOGY", later "IMAGINARY · INDESTRUCTIBLE".
"""

# ---------------------------------------------------------------- Appendix A: code
CODE_FILES = [('core.py', 'Timing, easing, colors, fonts, text, paints, images, noise'),
              ('assets.py', 'Procedural textures, sphere renderer, clouds, stars, overlays'),
              ('elements.py', 'Props, explorer rig, capsule, HUD, labels, cutaway, field lines'),
              ('common.py', 'Environments: space, multiplane clouds, speed lines, particles'),
              ('render.py', 'Timeline, transitions, post, still/contact/bench/segment encode'),
              ('render_all.sh', 'Parallel segment render + concat'),
              ('transcribe.py', 'Word-level transcription'),
              ('sfxlib.py', 'Sound engine: SFX synthesis, cues, ducking, mixdown, finishing'),
              ('scenes_TEMPLATE.py', 'Starter shot file'),
              ('example_jupiter/scenes1.py', 'Jupiter shots 01–17'),
              ('example_jupiter/scenes2.py', 'Jupiter shots 18–35'),
              ('example_jupiter/scenes3.py', 'Jupiter shots 36–54'),
              ('example_jupiter/mix.py', 'Jupiter music + SFX cue sheet')]
def code_md():
    out = ["# APPENDIX A — COMPLETE ENGINE SOURCE CODE", "",
           "The full, working engine that rendered the Jupiter film. It is also stored as files in `prompt_book/engine/` in the repository; prefer copying the files over retyping. File order follows the dependency order.", ""]
    for i, (f, d) in enumerate(CODE_FILES, 1):
        p = os.path.join(ENG, f)
        lang = 'bash' if f.endswith('.sh') else 'python'
        src = open(p).read().rstrip()
        out += [f"## A.{i} `engine/{f}` — {d} ({src.count(chr(10)) + 1} lines)", "", f"```{lang}", src, "```", ""]
    return "\n".join(out)

# ---------------------------------------------------------------- assemble markdown
def chapter(name): return open(os.path.join(CH, name)).read().rstrip() + "\n"
parts = [chapter('00_front.md'), chapter('01_master_prompt.md'), chapter('02_story.md'), chapter('03_visual.md'),
         chapter('04_animation.md'), chapter('05_sound.md'), principles_md(), chapter('07_qa.md'),
         chapter('08_templates.md'), example_md(), chapter('10_topics.md'), code_md(), chapter('11_appendix_bcd.md')]
book = "\n\n---\n\n".join(parts)
open(os.path.join(HERE, 'PROMPT_BOOK.md'), 'w').write(book)
mp = chapter('01_master_prompt.md')
open(os.path.join(HERE, 'MASTER_PROMPT.md'), 'w').write(
    "<!-- Paste-ready master prompt. The full reference (Parts II–X, code) is PROMPT_BOOK.md; paste both for best results. -->\n\n" + mp)
print('markdown chars', len(book), 'lines', book.count('\n'))

# ---------------------------------------------------------------- HTML + PDF
import markdown
body = markdown.markdown(book, extensions=['tables', 'fenced_code', 'codehilite', 'sane_lists', 'toc'],
                         extension_configs={'codehilite': {'guess_lang': False, 'noclasses': False}, 'toc': {'toc_depth': '1-2'}})
from pygments.formatters import HtmlFormatter
pyg = HtmlFormatter(style='friendly').get_style_defs('.codehilite')
# table of contents from H1/H2
heads = re.findall(r'<h([12]) id="([^"]+)">(.*?)</h\1>', body)
toc = ['<nav class="toc"><h1 class="tochead">Contents</h1><ul>']
for lvl, hid, txt in heads[1:]:
    if lvl == '1': toc.append(f'<li class="l1"><a href="#{hid}">{txt}</a></li>')
    elif not hid.startswith('a') or True:
        if re.match(r'^(\d+\.\d+|6\.\d+)', re.sub('<[^>]+>', '', txt)) and not re.sub('<[^>]+>', '', txt).startswith('6.'):
            toc.append(f'<li class="l2"><a href="#{hid}">{txt}</a></li>')
toc.append('</ul></nav>')
first_h1_end = body.index('</h1>') + 5
# cover = everything before the first <hr>
hr = body.index('<hr')
cover_html = body[:hr]; rest = body[body.index('>', hr) + 1:]
css = open(os.path.join(HERE, 'book.css')).read()
cover = f"""<!doctype html><html><head><meta charset="utf-8"><style>{css}
@page {{ margin: 0; }} body {{ margin:0; }} .cover {{ margin:0; height:297mm; width:210mm; }}</style></head><body>
<section class="cover"><div class="planet"></div><div class="cover-inner">
<div class="kicker">PRODUCTION BIBLE · MASTER PROMPT · VERSION 1.0</div>
<div class="title">WHAT IF YOU…?</div>
<div class="subtitle">Cinematic 2D Science Documentary<br>Prompt Book</div>
<div class="specs">Build-from-code 2D/2.5D animation<br>Narration-synced sound design<br>1920×1080 · 60 fps · 16:9 · −14 LUFS<br><br>Master Prompt · Animation Engine<br>Sound Design Engine · 300 Principles<br>QA · Templates · Full Source Code</div>
</div></section></body></html>"""
open(os.path.join(BUILD, 'cover.html'), 'w').write(cover)
doc = f"""<!doctype html><html><head><meta charset="utf-8"><title>What If You…? Prompt Book</title>
<style>{css}\n{pyg}</style></head><body>
<section class="intro">{cover_html}</section>
{''.join(toc)}
<main>{rest}</main></body></html>"""
open(os.path.join(BUILD, 'book.html'), 'w').write(doc)
subprocess.run(['node', os.path.join(HERE, 'make_pdf.js'), BUILD], check=True)
from pypdf import PdfReader, PdfWriter
w = PdfWriter()
for f in ('cover.pdf', 'body.pdf'):
    for pg in PdfReader(os.path.join(BUILD, f)).pages: w.add_page(pg)
w.add_metadata({'/Title': 'What If You…? Cinematic 2D Science Documentary Prompt Book', '/Subject': 'Master prompt, animation engine, sound design engine, source code'})
w.write(os.path.join(HERE, 'PROMPT_BOOK.pdf'))
print('pdf ok')
