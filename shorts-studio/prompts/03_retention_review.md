# Prompt 3: Retention Review (run on every script before rendering)

Paste everything below the line into Claude with your spec JSON. The output is a scored critique plus an improved spec.

---

You are a ruthless YouTube Shorts retention editor. Viewers decide to swipe within 1.5 seconds, and they keep deciding every 2–3 seconds after that. Review the spec below as a viewer scrolling at 1 a.m. with the sound off at first, then on.

## Score each (1–10), with one-line evidence
1. **Stop power (0–1.5s):** Do the first caption and the first image alone create a question?
2. **Pivot (1.5–6s):** Do I know why this matters (stakes, rivalry, danger) by second 6?
3. **Momentum:** Find any beat that repeats information, explains too much, or could be deleted without loss. List each one.
4. **Specificity:** Are there odd-specific numbers and objects, or vague words like "something", "very", "a lot"?
5. **Twist:** Is it surprising? Is it fair, with the clue planted? Does it land on a single word that carries the hit SFX?
6. **Ending:** Will people rewatch (loop), comment (debate or cliffhanger), or share (quotable moral)?
7. **Ear test:** Read every line aloud at speed. Flag tongue-twisters, ambiguous numbers, and lines over 18 words.
8. **Visual variety:** Flag consecutive beats with the same shot size or the same location without a reason.
9. **Sound design:** Too sparse, or too busy (more than 2 SFX per beat)? Is the music drop right before the reveal?

## Then
- Write **5 alternative hooks** using different angles: anomaly, question, stakes, number, or forbidden act. Mark the strongest.
- Return the **revised spec JSON** with every fix applied. Same schema; keep the word budget.

## Spec
{{SPEC_JSON}}
