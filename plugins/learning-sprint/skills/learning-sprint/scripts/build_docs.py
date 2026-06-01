#!/usr/bin/env python3
"""Render a printable study guide or practice exam to self-contained HTML
(and a PDF too, if pandoc / wkhtmltopdf / weasyprint happen to be installed).

Usage:
    python3 build_docs.py spec.json [out_basename]

The HTML is fully self-contained (inline CSS, no external assets) and tuned for
print: open it in any browser and choose Print > Save as PDF. That path needs
NOTHING installed. If an HTML-to-PDF tool is on PATH, a .pdf is also produced
automatically; otherwise the script just tells you to print the HTML.

Study-guide spec:
{
  "type": "study_guide",
  "title": "AWS SAA-C03 Study Guide",
  "subtitle": "Generated 2026-06-02",
  "sections": [
    {"heading": "Domain 1: Secure Architectures",
     "body_html": "<p>...</p><ul><li>...</li></ul>",
     "keypoints": ["IAM is global", "Security groups are stateful"]}
  ]
}

Practice-exam spec:
{
  "type": "practice_exam",
  "title": "AWS SAA-C03 Practice Exam",
  "subtitle": "65 questions · 130 minutes",
  "questions": [
    {"stem": "A company needs ...", "type": "mc",
     "choices": ["...", "...", "...", "..."], "answer": "C",
     "explanation": "C is correct because ...; A/B/D fail because ..."},
    {"stem": "Explain the trade-off ...", "type": "free",
     "answer": "Model answer ...", "explanation": "Rubric / key points ..."}
  ]
}
"""
import html
import json
import os
import shutil
import string
import subprocess
import sys

PAGE = string.Template(
    """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>$title</title>
<style>
@page { size: letter; margin: 0.85in; }
:root { --ink:#1a1a1a; --muted:#555; --rule:#bbb; --accent:#2453a6; }
* { box-sizing: border-box; }
html { font-size: 11pt; }
body { color: var(--ink); line-height: 1.5; max-width: 7.2in; margin: 0 auto; padding: .5in 0;
       font-family: Georgia, "Times New Roman", serif; }
h1 { font-size: 2em; border-bottom: 3px solid var(--accent); padding-bottom:.2em; }
h2 { font-size: 1.4em; color: var(--accent); margin-top: 1.4em; }
h3 { font-size: 1.15em; }
h1,h2,h3 { font-family:"Helvetica Neue",Arial,sans-serif; break-after:avoid; page-break-after:avoid; }
p,li { orphans:3; widows:3; }
code,pre { font-family:"SF Mono",Consolas,monospace; background:#f4f4f4; }
pre { padding:.8em; border-radius:4px; break-inside:avoid; page-break-inside:avoid; }
table { width:100%; border-collapse:collapse; break-inside:avoid; page-break-inside:avoid; }
th,td { border:1px solid var(--rule); padding:.4em .6em; text-align:left; } th { background:#eef2fb; }
.section { break-before:page; page-break-before:page; }
.section:first-of-type { break-before:auto; page-break-before:auto; }
.keypoints { border:1px solid var(--accent); background:#f0f5ff; border-radius:6px;
             padding:.6em 1em; margin:1em 0; break-inside:avoid; page-break-inside:avoid; }
.q { break-inside:avoid; page-break-inside:avoid; margin:0 0 1.1em; padding-bottom:.6em;
     border-bottom:1px dotted var(--rule); }
.q .stem { font-weight:600; margin-bottom:.5em; } .q .num { color:var(--accent); margin-right:.4em; }
ol.choices { list-style:none; margin:.2em 0 0; padding:0; counter-reset:choice; }
ol.choices li { counter-increment:choice; margin:.25em 0 .25em 1.6em; position:relative; }
ol.choices li::before { content: counter(choice, upper-alpha) ")"; position:absolute; left:-1.6em; font-weight:600; }
.answer-space { border:1px solid var(--rule); border-radius:4px; height:1.1in; margin-top:.5em;
                break-inside:avoid; page-break-inside:avoid; }
.answer-blank { margin-top:.4em; } .answer-blank .box { display:inline-block; width:1.4in;
                border-bottom:1.5px solid #333; height:1.1em; }
.answer-key { break-before:page; page-break-before:page; }
.answer-key .a { break-inside:avoid; page-break-inside:avoid; margin-bottom:.9em; }
.answer-key .num { font-weight:700; color:var(--accent); } .answer-key .correct { font-weight:700; }
.answer-key .explain { color:#444; margin-top:.15em; }
.meta { color:var(--muted); margin-bottom:1.4em; }
@media print { .no-print { display:none; } body { max-width:none; padding:0; }
  a { color:inherit; text-decoration:none; } * { -webkit-print-color-adjust:exact; print-color-adjust:exact; } }
</style></head>
<body>
<p class="no-print"><em>Tip: Print this page (Ctrl/Cmd-P) and choose "Save as PDF".</em></p>
<h1>$title</h1>
<div class="meta">$subtitle</div>
$body
</body></html>
"""
)


def esc(text):
    return html.escape(str(text))


def render_study_guide(spec):
    parts = []
    for sec in spec.get("sections", []):
        block = ['<div class="section">', f"<h2>{esc(sec.get('heading',''))}</h2>"]
        if sec.get("body_html"):
            block.append(sec["body_html"])  # trusted rich content from the skill
        if sec.get("keypoints"):
            items = "".join(f"<li>{esc(k)}</li>" for k in sec["keypoints"])
            block.append(f'<div class="keypoints"><strong>Key points</strong><ul>{items}</ul></div>')
        block.append("</div>")
        parts.append("\n".join(block))
    return "\n".join(parts)


def render_practice_exam(spec):
    questions = spec.get("questions", [])
    body, key = [], ['<section class="answer-key">', "<h2>Answer Key</h2>"]
    for i, q in enumerate(questions, 1):
        stem = f'<div class="stem"><span class="num">{i}.</span>{esc(q.get("stem",""))}</div>'
        if q.get("type") == "mc" and q.get("choices"):
            choices = "".join(f"<li>{esc(c)}</li>" for c in q["choices"])
            answer_area = (
                f'<ol class="choices">{choices}</ol>'
                '<div class="answer-blank">Your answer: <span class="box"></span></div>'
            )
        else:
            answer_area = '<div class="answer-space"></div>'
        body.append(f'<div class="q">{stem}{answer_area}</div>')
        key.append(
            f'<div class="a"><span class="num">{i}.</span> '
            f'<span class="correct">{esc(q.get("answer",""))}</span>'
            f'<div class="explain">{esc(q.get("explanation",""))}</div></div>'
        )
    key.append("</section>")
    return "\n".join(body) + "\n" + "\n".join(key)


def try_pdf(html_path, pdf_path):
    """Best-effort HTML->PDF using whatever is installed. Returns path or None."""
    candidates = [
        ("wkhtmltopdf", ["wkhtmltopdf", "-q", html_path, pdf_path]),
        ("weasyprint", ["weasyprint", html_path, pdf_path]),
        ("pandoc", ["pandoc", html_path, "-o", pdf_path]),  # needs a PDF engine
    ]
    for tool, cmd in candidates:
        if not shutil.which(tool):
            continue
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=120)
            return pdf_path
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            continue
    return None


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    spec_path = sys.argv[1]
    with open(spec_path, encoding="utf-8") as fh:
        spec = json.load(fh)
    base = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(spec_path)[0]

    kind = spec.get("type", "study_guide")
    body = render_practice_exam(spec) if kind == "practice_exam" else render_study_guide(spec)
    page = PAGE.safe_substitute(
        title=esc(spec.get("title", "Document")),
        subtitle=esc(spec.get("subtitle", "")),
        body=body,
    )
    html_path = base + ".html"
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(page)
    print(f"Wrote {html_path}")

    pdf = try_pdf(html_path, base + ".pdf")
    if pdf:
        print(f"Wrote {pdf}  (HTML-to-PDF tool detected)")
    else:
        print("No HTML-to-PDF tool found — open the .html in a browser and Print > Save as PDF.")


if __name__ == "__main__":
    main()
