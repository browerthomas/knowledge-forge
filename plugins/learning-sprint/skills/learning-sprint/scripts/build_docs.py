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

Interactive mock-exam spec (timed, self-scoring HTML — open in a browser):
{
  "type": "mock_exam",
  "title": "AWS MLA-C01 Mock Exam",
  "subtitle": "65 questions · 130 minutes",
  "time_limit_min": 130,
  "pass_pct": 72,
  "domains": {"d1": "Data Engineering", "d2": "EDA", "d3": "Modeling", "d4": "Ops"},
  "questions": [
    {"stem": "...", "type": "single", "choices": ["...", "...", "...", "..."],
     "answer": "C", "explanation": "...", "domain": "d3"},
    {"stem": "... (choose TWO)", "type": "multi", "choices": ["...", "...", "...", "..."],
     "answer": ["B", "D"], "explanation": "...", "domain": "d1"}
  ]
}
Renders a self-contained page with a countdown timer, auto-submit on timeout, a
PASS / NOT YET verdict against pass_pct, a per-domain score breakdown, and inline
answer review with explanations. No dependencies; nothing to install.

Static printable practice-exam spec:
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
.example { border-left:4px solid var(--accent); background:#fafcff; padding:.5em .9em; margin:1em 0;
           border-radius:0 6px 6px 0; break-inside:avoid; page-break-inside:avoid; }
.example .lbl { font-weight:700; color:var(--accent); font-size:.8em; text-transform:uppercase; letter-spacing:.05em; }
.check { margin-top:1.6em; } .check details { border:1px solid var(--rule); border-radius:6px; padding:.5em .8em; margin:.5em 0; }
.check summary { font-weight:600; cursor:pointer; }
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


def render_chapter(spec):
    """A digestible lesson: concept -> worked example -> check-yourself."""
    parts = []
    for sec in spec.get("sections", []):
        block = ['<div class="section">', f"<h2>{esc(sec.get('heading',''))}</h2>"]
        if sec.get("body_html"):
            block.append(sec["body_html"])
        ex = sec.get("example")
        if ex:
            block.append(f'<div class="example"><div class="lbl">Example</div>{ex.get("body_html", "")}</div>')
        if sec.get("keypoints"):
            items = "".join(f"<li>{esc(k)}</li>" for k in sec["keypoints"])
            block.append(f'<div class="keypoints"><strong>Key points</strong><ul>{items}</ul></div>')
        block.append("</div>")
        parts.append("\n".join(block))
    check = spec.get("check", [])
    if check:
        c = ['<div class="check"><h2>Check yourself</h2>']
        for i, q in enumerate(check, 1):
            c.append(
                f"<details><summary>{i}. {esc(q.get('q', ''))}</summary>"
                f"<div>{esc(q.get('a', ''))}</div></details>"
            )
        c.append("</div>")
        parts.append("\n".join(c))
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


def _norm_answer(ans):
    if isinstance(ans, list):
        return [str(a).strip().upper() for a in ans]
    return [str(ans).strip().upper()]


MOCK_PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>%%TITLE%%</title>
<style>
:root{--ink:#1a1a1a;--accent:#1f6f43;--bad:#b4232c;--rule:#ccc;}
*{box-sizing:border-box;}
body{font-family:"Helvetica Neue",Arial,sans-serif;color:var(--ink);line-height:1.45;
     max-width:46rem;margin:0 auto;padding:4.4rem 1rem 3rem;}
#bar{position:fixed;top:0;left:0;right:0;background:#fff;border-bottom:2px solid var(--accent);
     display:flex;align-items:center;gap:1rem;padding:.6rem 1rem;z-index:9;}
#bar #title{font-weight:700;flex:1;}
#timer{font-variant-numeric:tabular-nums;font-weight:700;color:var(--accent);}
button{font:inherit;font-weight:600;background:var(--accent);color:#fff;border:0;border-radius:6px;
       padding:.5rem .9rem;cursor:pointer;}
button[disabled]{opacity:.5;cursor:default;}
.meta{color:#555;margin:.4rem 0 1.4rem;}
.q{border-bottom:1px dotted var(--rule);padding:1rem 0;}
.q .stem{font-weight:600;margin-bottom:.5rem;} .q .num{color:var(--accent);margin-right:.4rem;}
.choices label{display:block;margin:.3rem 0;padding:.35rem .5rem;border-radius:6px;cursor:pointer;}
.choices label:hover{background:#f3f7f4;} .choices input{margin-right:.5rem;}
.q-ok{background:#f1f8f3;} .q-bad{background:#fdf2f2;}
.review{margin-top:.5rem;font-size:.92em;padding:.4rem .6rem;border-radius:6px;}
.review.ok{background:#e7f5ec;} .review.bad{background:#fbe7e7;} .review .ex{color:#444;margin-top:.25rem;}
#results{margin:1.4rem 0;padding:1rem 1.2rem;border:2px solid var(--accent);border-radius:8px;}
#results.fail{border-color:var(--bad);} .verdict{font-size:1.3em;font-weight:800;}
.pass{color:var(--accent);} .fail{color:var(--bad);}
table{width:100%;border-collapse:collapse;margin-top:.6rem;}
th,td{border:1px solid var(--rule);padding:.35rem .5rem;text-align:left;}
.dbar{height:.7em;background:var(--accent);border-radius:3px;display:inline-block;vertical-align:middle;}
</style></head><body>
<div id="bar"><span id="title">%%TITLE%%</span><span id="timer"></span>
<button id="submitBtn" onclick="submitExam()">Submit exam</button></div>
<div class="meta">%%META%%</div>
<div id="results" hidden></div>
<form id="exam">%%QUESTIONS%%</form>
<div style="text-align:center;margin-top:1rem;"><button onclick="submitExam()">Submit exam</button></div>
<script>
var DATA = %%DATA%%;
var done = false;
function fmt(s){var m=Math.floor(s/60),x=s%60;return m+":"+(x<10?"0":"")+x;}
var remain = DATA.time_limit_min*60, tEl = document.getElementById("timer");
function tick(){tEl.textContent="Time left "+fmt(remain); if(remain<=0){submitExam();return;} remain--;}
tick(); var timer = setInterval(tick,1000);
function picked(n){return Array.prototype.slice.call(document.querySelectorAll('[name="'+n+'"]:checked')).map(function(e){return e.value;});}
function eq(a,b){if(a.length!==b.length)return false;return a.slice().sort().join(",")===b.slice().sort().join(",");}
function esc(t){var d=document.createElement("div");d.textContent=(t==null?"":t);return d.innerHTML;}
function submitExam(){
  if(done)return; done=true; clearInterval(timer);
  document.getElementById("submitBtn").disabled=true;
  var correct=0, dom={}, missed=[];
  DATA.questions.forEach(function(q,i){
    var sel=picked("q"+i), ok=eq(sel,q.answer);
    if(ok)correct++;
    var d=q.domain||"general", dn=DATA.domains[d]||d;
    dom[d]=dom[d]||{n:dn,c:0,t:0}; dom[d].t++; if(ok)dom[d].c++;
    if(!ok)missed.push({id:q.id,domain:dn,concept:q.concept||"",
      your:(sel.length?sel.join(""):"(blank)"),correct:q.answer.join("")});
    var qe=document.getElementById("q"+i); qe.classList.add(ok?"q-ok":"q-bad");
    var rv=qe.querySelector(".review"); rv.hidden=false; rv.className="review "+(ok?"ok":"bad");
    rv.innerHTML="Correct: <b>"+q.answer.join(", ")+"</b> &middot; You: "+(sel.length?sel.join(", "):"(blank)")
      +"<div class=ex>"+esc(q.explanation)+"</div>";
  });
  var n=DATA.questions.length, pct=n?Math.round(correct/n*100):0, pass=pct>=DATA.pass_pct;
  var rows="", dlist=[];
  Object.keys(dom).forEach(function(k){var o=dom[k],p=Math.round(o.c/o.t*100);
    rows+="<tr><td>"+esc(o.n)+"</td><td>"+o.c+"/"+o.t+"</td><td><span class=dbar style='width:"+p+"%'></span> "+p+"%</td></tr>";
    dlist.push({domain:o.n,correct:o.c,total:o.t,pct:p});});
  var payload={topic:DATA.title,score:correct,total:n,pct:pct,pass:pass,per_domain:dlist,missed:missed};
  var pj=JSON.stringify(payload,null,2);
  var r=document.getElementById("results"); r.hidden=false; r.className=pass?"":"fail";
  r.innerHTML="<h2>Result</h2><p class=verdict><span class='"+(pass?"pass":"fail")+"'>"+(pass?"PASS":"NOT YET")
    +"</span> &mdash; "+correct+"/"+n+" ("+pct+"%), passing is "+DATA.pass_pct+"%</p>"
    +"<table><tr><th>Domain</th><th>Score</th><th></th></tr>"+rows+"</table>"
    +"<h3 style='margin-top:1rem'>Re-teach what you missed</h3>"
    +"<p style='color:#555'>Copy this and paste it back to your learning assistant — it'll re-teach the misses, add them to your Anki deck, and schedule spaced re-quizzes.</p>"
    +"<textarea id='payload' readonly style='width:100%;height:9em;font-family:monospace;font-size:.8rem'>"+esc(pj)+"</textarea>"
    +"<div style='margin-top:.4rem'><button type='button' onclick='copyResults()'>Copy results</button> <span id='copied' style='color:var(--accent);font-weight:600'></span></div>"
    +"<p style='color:#555;margin-top:.6rem'>Estimate vs the published passing percentage; the real exam uses a scaled score. Review each question above.</p>";
  r.scrollIntoView({behavior:"smooth"});
}
function copyResults(){
  var t=document.getElementById("payload"); t.select();
  function flag(){var c=document.getElementById("copied"); c.textContent="Copied!";}
  if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(t.value).then(flag,function(){});}
  try{if(document.execCommand("copy"))flag();}catch(e){}
}
</script></body></html>"""


def render_mock_exam(spec):
    questions = spec.get("questions", [])
    qhtml = []
    for i, q in enumerate(questions):
        ans = _norm_answer(q.get("answer", ""))
        multi = q.get("type") == "multi" or len(ans) > 1
        itype = "checkbox" if multi else "radio"
        note = f" <em>(choose {len(ans)})</em>" if multi else ""
        opts = []
        for j, choice in enumerate(q.get("choices", [])):
            letter = chr(65 + j)
            opts.append(
                f'<label><input type="{itype}" name="q{i}" value="{letter}">'
                f'<span>{letter}.</span> {esc(choice)}</label>'
            )
        qhtml.append(
            f'<div class="q" id="q{i}"><div class="stem"><span class="num">{i + 1}.</span>'
            f'{esc(q.get("stem", ""))}{note}</div>'
            f'<div class="choices">{"".join(opts)}</div>'
            '<div class="review" hidden></div></div>'
        )
    data = {
        "title": spec.get("title", "Mock Exam"),
        "time_limit_min": spec.get("time_limit_min", 90),
        "pass_pct": spec.get("pass_pct", 72),
        "domains": spec.get("domains", {}),
        "questions": [
            {
                "id": q.get("id") or f"q{i + 1}",
                "answer": _norm_answer(q.get("answer", "")),
                "explanation": q.get("explanation", ""),
                "domain": q.get("domain", "general"),
                "concept": q.get("concept", ""),
            }
            for i, q in enumerate(questions)
        ],
    }
    data_str = json.dumps(data).replace("</", "<\\/")
    meta = esc(spec.get("subtitle", f"{len(questions)} questions"))
    return (
        MOCK_PAGE.replace("%%TITLE%%", esc(spec.get("title", "Mock Exam")))
        .replace("%%META%%", meta)
        .replace("%%QUESTIONS%%", "\n".join(qhtml))
        .replace("%%DATA%%", data_str)
    )


BOARD_PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>%%TITLE%%</title>
<style>
body{font-family:"Helvetica Neue",Arial,sans-serif;color:#1a1a1a;line-height:1.5;
     max-width:52rem;margin:0 auto;padding:2rem 1rem;}
h1{font-size:1.5em;border-bottom:3px solid #2453a6;padding-bottom:.2em;}
.caption{color:#555;margin-top:1rem;}
.mermaid{margin:1.5rem 0;text-align:center;}
table{border-collapse:collapse;margin:1rem 0;width:100%;}
th,td{border:1px solid #bbb;padding:.45em .7em;text-align:left;} th{background:#eef2fb;}
.note{color:#777;font-size:.85em;margin-top:2rem;}
</style></head><body>
<h1>%%TITLE%%</h1>
%%BODY%%
%%MERMAID%%
<div class="caption">%%CAPTION%%</div>
<p class="note">If a diagram appears as code, this view needs internet to render it (Mermaid). The text is still accurate.</p>
%%SCRIPT%%
</body></html>"""

MERMAID_SCRIPT = (
    '<script type="module">'
    "import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';"
    "mermaid.initialize({startOnLoad:true,theme:'neutral'});"
    "</script>"
)


def render_board(spec):
    """A visual aid — Mermaid diagram and/or styled HTML, for when a picture beats prose."""
    mermaid = spec.get("mermaid", "")
    body = spec.get("html", "")  # trusted styled HTML (tables, labeled boxes)
    mblock = f'<pre class="mermaid">{esc(mermaid)}</pre>' if mermaid else ""
    return (
        BOARD_PAGE.replace("%%TITLE%%", esc(spec.get("title", "On the board")))
        .replace("%%BODY%%", body)
        .replace("%%MERMAID%%", mblock)
        .replace("%%CAPTION%%", esc(spec.get("caption", "")))
        .replace("%%SCRIPT%%", MERMAID_SCRIPT if mermaid else "")
    )


DASH_PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>%%TITLE%%</title>
<style>
body{font-family:"Helvetica Neue",Arial,sans-serif;color:#1a1a1a;max-width:44rem;margin:0 auto;padding:2rem 1rem;}
h1{font-size:1.6em;} h2{font-size:1.15em;color:#2453a6;margin-top:1.6rem;}
.verdict{font-size:1.5em;font-weight:800;padding:.6rem 1rem;border-radius:8px;margin:1rem 0;}
.go{background:#e7f5ec;color:#1f6f43;border:2px solid #1f6f43;}
.notyet{background:#fbe7e7;color:#b4232c;border:2px solid #b4232c;}
.row{display:flex;align-items:center;gap:.6rem;margin:.4rem 0;}
.row .lab{width:13rem;font-size:.92em;} .row .num{width:3rem;text-align:right;font-variant-numeric:tabular-nums;}
.track{flex:1;background:#eee;border-radius:5px;height:.8rem;overflow:hidden;}
.fill{height:100%;border-radius:5px;}
.mock{display:inline-block;width:2.4rem;text-align:center;padding:.3rem 0;margin:.15rem;border-radius:5px;font-weight:700;font-size:.85em;}
.big{font-size:2em;font-weight:800;} .muted{color:#666;}
</style></head><body>
<h1>%%TITLE%%</h1>
<div class="muted">%%SUBTITLE%%</div>
<div class="verdict %%VCLASS%%">%%VERDICT%%</div>
<p class="muted">%%RULE%%</p>
<h2>Mastery by domain</h2>%%DOMAINS%%
<h2>Practice-exam history</h2><div>%%MOCKS%%</div>
<h2>Where you stand</h2>%%STATS%%
</body></html>"""


def _bar_color(pct):
    return "#1f6f43" if pct >= 80 else ("#c9a227" if pct >= 60 else "#b4232c")


def render_dashboard(spec):
    """Readiness at a glance: domain mastery, mock-score history, GO / NOT YET."""
    pass_pct = spec.get("pass_pct", 80)
    streak_target = spec.get("streak_target", 3)
    min_domain = spec.get("min_domain", 65)
    domains = spec.get("domains", [])
    mocks = spec.get("mocks", [])

    drows = []
    for d in domains:
        m = d.get("mastery", 0)
        drows.append(
            f'<div class="row"><span class="lab">{esc(d.get("name", ""))} '
            f'<span class="muted">({d.get("weight", "?")}%)</span></span>'
            f'<span class="track"><span class="fill" style="width:{m}%;background:{_bar_color(m)}"></span></span>'
            f'<span class="num">{m}%</span></div>'
        )
    mhtml = "".join(
        f'<span class="mock" style="background:{_bar_color(mk.get("pct", 0))};color:#fff" '
        f'title="{esc(mk.get("date", ""))}">{mk.get("pct", 0)}%</span>'
        for mk in mocks
    ) or '<span class="muted">No practice exams taken yet.</span>'

    qualifying = [mk for mk in mocks if mk.get("pct", 0) >= pass_pct]
    weak = [d.get("name") for d in domains if d.get("mastery", 0) < min_domain]
    ready = len(qualifying) >= streak_target and not weak
    rule = (
        f"Ready = {streak_target} practice exams at or above {pass_pct}%, "
        f"and no domain below {min_domain}%."
    )
    stats = (
        f'<p><span class="big">{len(qualifying)}</span> / {streak_target} qualifying exams '
        f'(&ge;{pass_pct}%)</p>'
    )
    if spec.get("exam_date"):
        stats += f'<p>Exam date: <b>{esc(spec["exam_date"])}</b></p>'
    if spec.get("cards_due") is not None:
        stats += f'<p>Cards due for re-quiz: <b>{esc(spec["cards_due"])}</b></p>'
    if weak:
        stats += f'<p class="muted">Still weak (&lt;{min_domain}%): {esc(", ".join(weak))}</p>'

    return (
        DASH_PAGE.replace("%%TITLE%%", esc(spec.get("title", "Readiness")))
        .replace("%%SUBTITLE%%", esc(spec.get("subtitle", "")))
        .replace("%%VCLASS%%", "go" if ready else "notyet")
        .replace("%%VERDICT%%", "GO — you're ready" if ready else "NOT YET")
        .replace("%%RULE%%", rule)
        .replace("%%DOMAINS%%", "".join(drows))
        .replace("%%MOCKS%%", mhtml)
        .replace("%%STATS%%", stats)
    )


def try_pdf(html_path, pdf_path):
    """Best-effort HTML->PDF using whatever is installed. Returns path or None.

    LibreOffice (soffice) is included because Claude Cowork ships it; it writes
    <basename>.pdf into --outdir, which we then move to pdf_path if needed.
    """
    outdir = os.path.dirname(os.path.abspath(pdf_path)) or "."
    base = os.path.splitext(os.path.basename(html_path))[0]
    libre_out = os.path.join(outdir, base + ".pdf")
    candidates = [
        ("wkhtmltopdf", ["wkhtmltopdf", "-q", html_path, pdf_path], None),
        ("weasyprint", ["weasyprint", html_path, pdf_path], None),
        ("libreoffice", ["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", outdir, html_path], libre_out),
        ("soffice", ["soffice", "--headless", "--convert-to", "pdf", "--outdir", outdir, html_path], libre_out),
        ("pandoc", ["pandoc", html_path, "-o", pdf_path], None),  # needs a PDF engine
    ]
    for tool, cmd, produced in candidates:
        if not shutil.which(tool):
            continue
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=180)
            if produced and produced != pdf_path and os.path.exists(produced):
                os.replace(produced, pdf_path)
            if os.path.exists(pdf_path):
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
    if kind == "mock_exam":
        html_path = base + ".html"
        with open(html_path, "w", encoding="utf-8") as fh:
            fh.write(render_mock_exam(spec))
        print(f"Wrote {html_path}")
        print("Open it in a browser — it's a timed, self-scoring mock with a per-domain breakdown.")
        return
    if kind in ("board", "visual"):
        html_path = base + ".html"
        with open(html_path, "w", encoding="utf-8") as fh:
            fh.write(render_board(spec))
        print(f"Wrote {html_path}  (open in a browser)")
        return
    if kind == "dashboard":
        html_path = base + ".html"
        with open(html_path, "w", encoding="utf-8") as fh:
            fh.write(render_dashboard(spec))
        print(f"Wrote {html_path}  (open in a browser)")
        return
    if kind == "chapter":
        body = render_chapter(spec)
    elif kind == "practice_exam":
        body = render_practice_exam(spec)
    else:
        body = render_study_guide(spec)
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
