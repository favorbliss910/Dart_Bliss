"""Build the prompt book (PDF + TXT) from docs/prompt_book/prompt_book_source.md.

Supports the markdown subset used by the source: '#'/'##' headings, paragraphs,
'- ' bullets, '- [ ]' checkboxes, '1. ' lists, '|' tables, ``` code blocks,
and inline **bold**, *italic* and `code`.

Usage: python3 tools/build_prompt_book.py
"""
import os
import re
import textwrap

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (KeepTogether, PageBreak, Paragraph, Preformatted, SimpleDocTemplate, Spacer,
                                Table, TableStyle)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "docs", "prompt_book", "prompt_book_source.md")
OUT_DIR = os.path.join(ROOT, "docs", "prompt_book")
BASENAME = "3D_Short_Prompt_Book"


# ------------------------------------------------------------------ parse
def parse(text):
    blocks, lines, i = [], text.splitlines(), 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("```"):
            j = i + 1
            while not lines[j].startswith("```"):
                j += 1
            blocks.append(("code", "\n".join(lines[i + 1 : j])))
            i = j + 1
        elif ln.startswith("## "):
            blocks.append(("h2", ln[3:].strip()))
            i += 1
        elif ln.startswith("# "):
            blocks.append(("h1", ln[2:].strip()))
            i += 1
        elif ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            blocks.append(("table", rows))
        elif re.match(r"^(- |\d+\. )", ln):
            items = []
            while i < len(lines) and re.match(r"^(- |\d+\. )", lines[i]):
                items.append(lines[i])
                i += 1
            blocks.append(("list", items))
        elif ln.strip() == "":
            i += 1
        else:
            para = [ln]
            i += 1
            while i < len(lines) and lines[i].strip() and not re.match(r"^(#|```|\||- |\d+\. )", lines[i]):
                para.append(lines[i])
                i += 1
            blocks.append(("p", " ".join(para)))
    return blocks


def strip_inline(s):
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"\1", s)
    return s.replace("`", "")


# ------------------------------------------------------------------ TXT
def to_txt(blocks):
    out, W = [], 92
    wrap = lambda s, ind="", sub=None: textwrap.fill(s, W, initial_indent=ind, subsequent_indent=sub if sub is not None else ind,
                                                     break_long_words=False, break_on_hyphens=False)
    first_h1 = True
    for kind, val in blocks:
        if kind == "h1":
            if first_h1:  # title
                out += ["=" * W, val.upper().center(W), "=" * W]
                first_h1 = False
            else:
                out += ["", "", "=" * W, val.upper(), "=" * W, ""]
        elif kind == "h2":
            if len(out) <= 3:  # subtitle
                out += [val.center(W)]
            else:
                out += ["", val, "-" * len(val)]
        elif kind == "p":
            out += [wrap(strip_inline(val)), ""]
        elif kind == "list":
            for it in val:
                m = re.match(r"^(- \[ \] |- |\d+\. )(.*)", it)
                bullet = "[ ] " if m.group(1).startswith("- [") else ("* " if m.group(1) == "- " else m.group(1))
                out.append(wrap(strip_inline(m.group(2)), "  " + bullet, " " * (2 + len(bullet))))
            out.append("")
        elif kind == "table":
            hdr, rows = val[0], val[1:]
            if len(hdr) == 2:
                for r in rows:
                    out.append(wrap(f"{strip_inline(r[0])}: {strip_inline(r[1])}", "  * ", "      "))
            else:
                for r in rows:
                    out.append(wrap(strip_inline(r[0]), "  * ", "      "))
                    for h, c in zip(hdr[1:], r[1:]):
                        out.append(wrap(f"{strip_inline(h)}: {strip_inline(c)}", "      ", "        "))
            out.append("")
        elif kind == "code":
            out += ["    ----------------------------- COPY FROM HERE -----------------------------",
                    val,
                    "    ---------------------------------- END ----------------------------------", ""]
    return "\n".join(out).rstrip() + "\n"


# ------------------------------------------------------------------ PDF
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
pdfmetrics.registerFont(TTFont("DV", os.path.join(FONT_DIR, "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DV-B", os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("DVM", os.path.join(FONT_DIR, "DejaVuSansMono.ttf")))
from reportlab.pdfbase.pdfmetrics import registerFontFamily  # noqa: E402

registerFontFamily("DV", normal="DV", bold="DV-B", italic="DV", boldItalic="DV-B")  # no oblique sans installed

INK = colors.HexColor("#1d2330")
ACCENT = colors.HexColor("#0b6e74")
WARM = colors.HexColor("#c4572a")
CODE_BG = colors.HexColor("#f3f1ec")
RULE = colors.HexColor("#d9d4c7")

ST = {
    "title": ParagraphStyle("title", fontName="DV-B", fontSize=30, leading=36, textColor=INK, spaceAfter=10),
    "subtitle": ParagraphStyle("subtitle", fontName="DV", fontSize=14, leading=19, textColor=ACCENT, spaceAfter=24),
    "h1": ParagraphStyle("h1", fontName="DV-B", fontSize=17, leading=22, textColor=ACCENT, spaceBefore=4, spaceAfter=10),
    "h2": ParagraphStyle("h2", fontName="DV-B", fontSize=12, leading=16, textColor=INK, spaceBefore=12, spaceAfter=6),
    "p": ParagraphStyle("p", fontName="DV", fontSize=9.6, leading=14, textColor=INK, spaceAfter=7, alignment=TA_LEFT),
    "li": ParagraphStyle("li", fontName="DV", fontSize=9.6, leading=13.5, textColor=INK, leftIndent=16, bulletIndent=4, spaceAfter=3),
    "cell": ParagraphStyle("cell", fontName="DV", fontSize=7.9, leading=10.2, textColor=INK),
    "cellh": ParagraphStyle("cellh", fontName="DV-B", fontSize=8, leading=10.2, textColor=colors.white),
    "code": ParagraphStyle("code", fontName="DVM", fontSize=7.6, leading=9.8, textColor=INK),
    "toc": ParagraphStyle("toc", fontName="DV", fontSize=10.5, leading=17, textColor=INK),
}


def inline(s):
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    parts = re.split(r"(`[^`]+`)", s)
    out = []
    for p in parts:
        if p.startswith("`") and p.endswith("`") and len(p) > 1:
            out.append(f'<font name="DVM" color="#0b6e74">{p[1:-1]}</font>')
        else:
            p = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", p)
            p = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", p)
            out.append(p)
    return "".join(out)


def code_block(text, max_lines=52):
    """Shaded copy-ready block; long blocks become several page-sized boxes."""
    lines = text.split("\n")
    chunks = [lines[i : i + max_lines] for i in range(0, len(lines), max_lines)]
    return [_code_box("\n".join(c)) for c in chunks]


def _code_box(text):
    pre = Preformatted(text, ST["code"], maxLineLength=96, newLineChars="  ")
    t = Table([[pre]], colWidths=[6.9 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CODE_BG),
        ("LINEBEFORE", (0, 0), (0, -1), 2.5, WARM),
        ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return t


def table_block(rows):
    ncol = len(rows[0])
    total = 6.9 * inch
    # width by content length, clamped
    lens = [max(len(strip_inline(r[c])) for r in rows) for c in range(ncol)]
    raw = [min(max(L, 11), 70) for L in lens]
    widths = [total * w / sum(raw) for w in raw]
    # never let a column be narrower than its header word(s)
    mins = [max(pdfmetrics.stringWidth(w, "DV-B", 8) for w in strip_inline(h).split()) + 12 for h in rows[0]]
    for _ in range(3):
        short = [i for i in range(ncol) if widths[i] < mins[i]]
        if not short:
            break
        deficit = sum(mins[i] - widths[i] for i in short)
        for i in short:
            widths[i] = mins[i]
        rest = [i for i in range(ncol) if i not in short]
        pool = sum(widths[i] for i in rest)
        for i in rest:
            widths[i] -= deficit * widths[i] / pool
    data = [[Paragraph(inline(c), ST["cellh"]) for c in rows[0]]]
    data += [[Paragraph(inline(c), ST["cell"]) for c in r] for r in rows[1:]]
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f6f2")]),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]))
    return t


def to_pdf(blocks, path):
    story, title_done, sub_done = [], False, False
    h1s = [v for k, v in blocks if k == "h1"][1:]
    for kind, val in blocks:
        if kind == "h1" and not title_done:
            story += [Spacer(1, 1.6 * inch), Paragraph(inline(val), ST["title"])]
            title_done = True
            continue
        if kind == "h2" and not sub_done:
            story.append(Paragraph(inline(val), ST["subtitle"]))
            sub_done = True
            continue
        if kind == "p" and val.startswith("Version") and len(story) < 4:
            story.append(Paragraph(inline(val), ST["p"]))
            story += [Spacer(1, 0.5 * inch), Paragraph("<b>Contents</b>", ST["h2"])]
            story += [Paragraph(inline(h), ST["toc"]) for h in h1s]
            story.append(PageBreak())
            continue
        if kind == "h1":
            story.append(PageBreak())
            story.append(Paragraph(inline(val), ST["h1"]))
        elif kind == "h2":
            story.append(Paragraph(inline(val), ST["h2"]))
        elif kind == "p":
            story.append(Paragraph(inline(val), ST["p"]))
        elif kind == "list":
            for it in val:
                m = re.match(r"^(- \[ \] |- |\d+\. )(.*)", it)
                b = "☐" if m.group(1).startswith("- [") else ("•" if m.group(1) == "- " else m.group(1).strip())
                story.append(Paragraph(inline(m.group(2)), ST["li"], bulletText=b))
            story.append(Spacer(1, 4))
        elif kind == "table":
            story += [table_block(val), Spacer(1, 8)]
        elif kind == "code":
            boxes = code_block(val)
            # keep a short block together with the heading right above it
            if len(boxes) == 1 and story and isinstance(story[-1], Paragraph) and story[-1].style.name == "h2":
                h = story.pop()
                story.append(KeepTogether([h, boxes[0]]))
            else:
                story += boxes
            story.append(Spacer(1, 9))

    def deco(canvas, doc):
        canvas.saveState()
        if doc.page > 1:
            canvas.setFont("DV", 7.5)
            canvas.setFillColor(colors.HexColor("#7a7f8a"))
            canvas.drawString(0.8 * inch, 0.55 * inch, "3D Short Prompt Book · script + voiceover in, 'Last Stop' quality out")
            canvas.drawRightString(7.7 * inch, 0.55 * inch, f"{doc.page}")
            canvas.setStrokeColor(RULE)
            canvas.line(0.8 * inch, 0.72 * inch, 7.7 * inch, 0.72 * inch)
        else:
            canvas.setFillColor(ACCENT)
            canvas.rect(0, 10.2 * inch, 8.5 * inch, 0.8 * inch, fill=1, stroke=0)
            canvas.setFillColor(WARM)
            canvas.rect(0, 10.12 * inch, 8.5 * inch, 0.08 * inch, fill=1, stroke=0)
        canvas.restoreState()

    doc = SimpleDocTemplate(path, pagesize=letter, leftMargin=0.8 * inch, rightMargin=0.8 * inch,
                            topMargin=0.75 * inch, bottomMargin=0.95 * inch,
                            title="3D Short Prompt Book", author="Dart_Bliss production pipeline",
                            subject="Script + voiceover in, Last Stop quality out")
    doc.build(story, onFirstPage=deco, onLaterPages=deco)


if __name__ == "__main__":
    blocks = parse(open(SRC, encoding="utf-8").read())
    txt_path = os.path.join(OUT_DIR, BASENAME + ".txt")
    pdf_path = os.path.join(OUT_DIR, BASENAME + ".pdf")
    open(txt_path, "w", encoding="utf-8").write(to_txt(blocks))
    to_pdf(blocks, pdf_path)
    print(txt_path)
    print(pdf_path)
