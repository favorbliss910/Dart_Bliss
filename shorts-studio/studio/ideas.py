"""Generate ideas and production specs with Claude (optional; the prompts also work pasted into claude.ai).

    export ANTHROPIC_API_KEY=...        # or `ant auth login`
    python -m studio.ideas ideas --n 10 --themes "ancient engineering, ocean mysteries"
    python -m studio.ideas script --idea-file ideas/2026-11-11.json --pick 3
    python -m studio.ideas script --idea "A town where the clocks all run backwards..."
    python -m studio.ideas review specs/my_story.json
    python -m studio.ideas ideas --print-prompt        # just print the filled prompt

Ideas land in ideas/, specs in specs/. Past ideas are fed back in automatically
so the generator never repeats itself.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

from . import config

MODEL = "claude-opus-5-5"
PROMPTS = config.ROOT / "prompts"
IDEAS_DIR = config.ROOT / "ideas"
SPECS_DIR = config.ROOT / "specs"


def _fill(template: str, values: dict) -> str:
    def rep(m):
        key = m.group(1).strip().split("|")[0].strip()
        default = m.group(1).split("default", 1)[1].strip(" :") if "default" in m.group(1) else ""
        return str(values.get(key) or default)
    return re.sub(r"\{\{([^}]+)\}\}", rep, template)


def _prompt(name: str, values: dict) -> str:
    text = (PROMPTS / name).read_text()
    body = text.split("\n---\n", 1)[1] if "\n---\n" in text else text
    return _fill(body, values)


def _extract_json(text: str) -> dict:
    m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.S)
    raw = m.group(1) if m else text[text.find("{"): text.rfind("}") + 1]
    return json.loads(raw)


def ask_claude(prompt: str, effort: str = "high") -> str:
    import anthropic
    client = anthropic.Anthropic()
    with client.beta.messages.stream(
        model=MODEL,
        max_tokens=64000,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",          # re-run on a fallback model if a request is declined
        output_config={"effort": effort},
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        msg = stream.get_final_message()
    if msg.stop_reason == "refusal":
        raise RuntimeError(f"Request declined: {getattr(msg, 'stop_details', None)}")
    return "".join(b.text for b in msg.content if b.type == "text")


def _past_ideas() -> str:
    titles = []
    for f in sorted(IDEAS_DIR.glob("*.json")):
        try:
            titles += [f"{i['title']}: {i['hook_line']}" for i in json.loads(f.read_text())["ideas"]]
        except Exception:
            pass
    for f in sorted(SPECS_DIR.glob("*.json")):
        try:
            titles.append(json.loads(f.read_text()).get("title", f.stem))
        except Exception:
            pass
    return "\n".join(f"- {t}" for t in titles[-200:]) or "none"


def cmd_ideas(a):
    prompt = _prompt("01_idea_generator.md", {
        "N": a.n, "THEMES": a.themes, "FORMATS": a.formats, "LENGTHS": a.lengths,
        "PAST_IDEAS": _past_ideas(), "AUDIENCE": a.audience})
    if a.print_prompt:
        print(prompt)
        return
    data = _extract_json(ask_claude(prompt))
    IDEAS_DIR.mkdir(exist_ok=True)
    out = IDEAS_DIR / f"{dt.datetime.now():%Y-%m-%d_%H%M}.json"
    out.write_text(json.dumps(data, indent=2))
    for i, idea in enumerate(data["ideas"], 1):
        s = idea.get("scores", {})
        print(f"{i:2d}. [{idea['format']}] {idea['title']}  (avg {sum(s.values()) / max(len(s), 1):.1f})")
        print(f"    {idea['hook_line']}")
    print(f"\nSaved {out}. Next: python -m studio.ideas script --idea-file {out} --pick <n>")


def cmd_script(a):
    if a.idea_file:
        ideas = json.loads(Path(a.idea_file).read_text())["ideas"]
        idea = json.dumps(ideas[a.pick - 1], indent=2)
    else:
        idea = a.idea
    prompt = _prompt("02_script_writer.md", {"IDEA": idea})
    if a.print_prompt:
        print(prompt)
        return
    spec = _extract_json(ask_claude(prompt))
    if a.review:
        spec = _extract_json(ask_claude(_prompt("03_retention_review.md", {"SPEC_JSON": json.dumps(spec, indent=2)})))
    SPECS_DIR.mkdir(exist_ok=True)
    out = SPECS_DIR / f"{spec.get('slug') or 'story'}.json"
    out.write_text(json.dumps(spec, indent=2))
    words = sum(len(b["vo"].split()) for b in spec["beats"])
    print(f"Saved {out}: {len(spec['beats'])} beats, {words} words (~{words / 3.0:.0f}s)")
    print(f"Next: python -m studio.make_short {out} --preview")


def cmd_review(a):
    prompt = _prompt("03_retention_review.md", {"SPEC_JSON": Path(a.spec).read_text()})
    if a.print_prompt:
        print(prompt)
        return
    text = ask_claude(prompt)
    print(text.split("```")[0])
    spec = _extract_json(text)
    out = Path(a.spec).with_name(Path(a.spec).stem + "_reviewed.json")
    out.write_text(json.dumps(spec, indent=2))
    print(f"Saved revised spec -> {out}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("ideas")
    p.add_argument("--n", type=int, default=10)
    p.add_argument("--themes", default="")
    p.add_argument("--formats", default="")
    p.add_argument("--lengths", default="")
    p.add_argument("--audience", default="")
    p.add_argument("--print-prompt", action="store_true")
    p.set_defaults(fn=cmd_ideas)
    p = sub.add_parser("script")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--idea")
    g.add_argument("--idea-file")
    p.add_argument("--pick", type=int, default=1)
    p.add_argument("--review", action="store_true", help="also run the retention review pass")
    p.add_argument("--print-prompt", action="store_true")
    p.set_defaults(fn=cmd_script)
    p = sub.add_parser("review")
    p.add_argument("spec")
    p.add_argument("--print-prompt", action="store_true")
    p.set_defaults(fn=cmd_review)
    a = ap.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
