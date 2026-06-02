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
:root { --bg:#0a0a0d; --surface:#16161b; --surface-2:#1c1c22; --border:#2a2a32; --border-2:#3a3a44;
        --text:#f0f0f3; --text-2:#a8a8b3; --text-3:#6b6b78; --ember:#ff7530; --ember-2:#ffac4a;
        --ember-3:#fff0c8; --steel:#8c95a2; --green:#5fbf7a; --red:#ff5a4a;
        --font:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
        --mono:'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,monospace; }
* { box-sizing: border-box; }
body { background:var(--bg); color:var(--text); font-family:var(--font); line-height:1.65; margin:0; padding:3rem 1rem;
       background-image:radial-gradient(ellipse at top,rgba(255,117,48,.06) 0%,transparent 55%); -webkit-font-smoothing:antialiased; }
.wrap { max-width:46rem; margin:0 auto; background:var(--surface); border:1px solid var(--border); border-radius:14px; padding:2.4rem 2.6rem; }
h1 { font-size:1.95rem; font-weight:800; letter-spacing:-.02em; margin:0 0 .3rem;
     background:linear-gradient(135deg,var(--ember),var(--ember-2) 60%,var(--ember-3)); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }
h2 { font-size:1.3rem; font-weight:700; color:var(--ember-2); margin:2rem 0 .6rem; letter-spacing:-.01em; }
h3 { font-size:1.08rem; font-weight:700; color:var(--text); }
h1,h2,h3 { break-after:avoid; page-break-after:avoid; }
p,li { color:var(--text-2); orphans:3; widows:3; } strong { color:var(--text); }
a { color:var(--ember-2); text-decoration:none; }
code,pre { font-family:var(--mono); background:var(--bg); border:1px solid var(--border); border-radius:6px; }
code { padding:.05em .35em; font-size:.9em; } pre { padding:.9em; overflow:auto; break-inside:avoid; page-break-inside:avoid; }
table { width:100%; border-collapse:collapse; margin:1rem 0; break-inside:avoid; page-break-inside:avoid; }
th,td { border:1px solid var(--border); padding:.5em .7em; text-align:left; color:var(--text-2); }
th { background:var(--surface-2); color:var(--text); }
.section { break-before:page; page-break-before:page; }
.section:first-of-type { break-before:auto; page-break-before:auto; }
.keypoints { background:var(--surface-2); border:1px solid var(--border-2); border-left:3px solid var(--ember);
             border-radius:8px; padding:.7em 1.1em; margin:1.2em 0; break-inside:avoid; page-break-inside:avoid; }
.keypoints strong { color:var(--ember-2); }
.q { break-inside:avoid; page-break-inside:avoid; margin:0 0 1.1em; padding:1em 0; border-bottom:1px solid var(--border); }
.q .stem { font-weight:600; color:var(--text); margin-bottom:.5em; } .q .num { color:var(--ember); margin-right:.4em; }
ol.choices { list-style:none; margin:.2em 0 0; padding:0; counter-reset:choice; }
ol.choices li { counter-increment:choice; margin:.3em 0 .3em 1.7em; position:relative; color:var(--text-2); }
ol.choices li::before { content: counter(choice, upper-alpha) ")"; position:absolute; left:-1.7em; font-weight:700; color:var(--ember-2); }
.answer-space { border:1px solid var(--border-2); border-radius:6px; height:1.1in; margin-top:.5em; break-inside:avoid; page-break-inside:avoid; }
.answer-blank { margin-top:.4em; color:var(--text-2); } .answer-blank .box { display:inline-block; width:1.4in;
                border-bottom:1.5px solid var(--border-2); height:1.1em; }
.answer-key { break-before:page; page-break-before:page; }
.answer-key .a { break-inside:avoid; page-break-inside:avoid; margin-bottom:.9em; }
.answer-key .num { font-weight:700; color:var(--ember); } .answer-key .correct { font-weight:700; color:var(--green); }
.answer-key .explain { color:var(--text-2); margin-top:.15em; }
.meta { color:var(--text-3); margin-bottom:1.6rem; font-size:.95rem; }
.example { background:var(--surface-2); border:1px solid var(--border); border-left:3px solid var(--steel); border-radius:8px;
           padding:.6em 1em; margin:1.1em 0; break-inside:avoid; page-break-inside:avoid; }
.example .lbl { font-weight:700; color:var(--text-3); font-size:.72rem; text-transform:uppercase; letter-spacing:.08em; }
.check { margin-top:1.8em; } .check details { background:var(--surface-2); border:1px solid var(--border); border-radius:8px; padding:.6em .9em; margin:.5em 0; }
.check summary { font-weight:600; color:var(--text); cursor:pointer; } .check details>div { color:var(--text-2); margin-top:.4em; }
.tip { color:var(--text-3); font-size:.85rem; margin-bottom:1rem; }
@media print {
  body { background:#fff !important; color:#111 !important; background-image:none !important; padding:0; }
  .wrap { max-width:none; background:#fff !important; border:0; border-radius:0; padding:0; }
  h1 { background:none !important; -webkit-text-fill-color:#111 !important; color:#111 !important; border-bottom:3px solid #2453a6; padding-bottom:.2em; }
  h2 { color:#2453a6 !important; } h3 { color:#111 !important; }
  p,li,td,.answer-blank,.example .lbl,.meta { color:#222 !important; } strong { color:#000 !important; } a { color:#111 !important; }
  code,pre { background:#f4f4f4 !important; border-color:#ccc !important; color:#111 !important; }
  th { background:#eef2fb !important; color:#111 !important; } th,td { border-color:#bbb !important; }
  .keypoints,.example,.check details { background:#f7f9fc !important; border-color:#ccd !important; color:#111 !important; }
  .keypoints strong { color:#2453a6 !important; }
  .no-print { display:none; }
  * { -webkit-print-color-adjust:exact; print-color-adjust:exact; }
}
</style></head>
<body><div class="wrap">
<p class="tip no-print">Tip: Print (Ctrl/Cmd-P) → Save as PDF. (Screen is dark; print comes out clean.)</p>
<h1>$title</h1>
<div class="meta">$subtitle</div>
$body
</div></body></html>
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
:root{--bg:#0a0a0d;--surface:#16161b;--surface-2:#1c1c22;--border:#2a2a32;--text:#f0f0f3;--text-2:#a8a8b3;--text-3:#6b6b78;
      --ember:#ff7530;--ember-2:#ffac4a;--green:#5fbf7a;--bad:#ff5a4a;
      --font:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;}
*{box-sizing:border-box;}
body{font-family:var(--font);background:var(--bg);color:var(--text);line-height:1.5;
     max-width:46rem;margin:0 auto;padding:4.6rem 1rem 3rem;-webkit-font-smoothing:antialiased;
     background-image:radial-gradient(ellipse at top,rgba(255,117,48,.06) 0%,transparent 55%);}
#bar{position:fixed;top:0;left:0;right:0;background:rgba(10,10,13,.9);backdrop-filter:blur(8px);border-bottom:1px solid var(--border);
     display:flex;align-items:center;gap:1rem;padding:.7rem 1rem;z-index:9;}
#bar #title{font-weight:700;flex:1;}
#timer{font-variant-numeric:tabular-nums;font-weight:700;color:var(--ember-2);}
button{font:inherit;font-weight:600;background:var(--ember);color:#1a1206;border:0;border-radius:7px;
       padding:.5rem 1rem;cursor:pointer;}
button:hover{background:var(--ember-2);} button[disabled]{opacity:.5;cursor:default;}
.meta{color:var(--text-3);margin:.4rem 0 1.4rem;}
.q{border-bottom:1px solid var(--border);padding:1.1rem 0;}
.q .stem{font-weight:600;margin-bottom:.5rem;} .q .num{color:var(--ember);margin-right:.4rem;}
.choices label{display:block;margin:.3rem 0;padding:.45rem .6rem;border:1px solid transparent;border-radius:7px;cursor:pointer;color:var(--text-2);}
.choices label:hover{background:var(--surface-2);border-color:var(--border);} .choices input{margin-right:.5rem;accent-color:var(--ember);}
.q-ok{background:rgba(95,191,122,.08);border-radius:8px;} .q-bad{background:rgba(255,90,74,.07);border-radius:8px;}
.review{margin-top:.5rem;font-size:.92em;padding:.5rem .7rem;border-radius:7px;color:var(--text-2);}
.review.ok{background:rgba(95,191,122,.12);} .review.bad{background:rgba(255,90,74,.12);} .review .ex{color:var(--text-3);margin-top:.25rem;}
#results{margin:1.4rem 0;padding:1.1rem 1.3rem;border:1px solid var(--green);border-radius:10px;background:var(--surface);}
#results.fail{border-color:var(--bad);} .verdict{font-size:1.3em;font-weight:800;}
.pass{color:var(--green);} .fail{color:var(--bad);}
table{width:100%;border-collapse:collapse;margin-top:.6rem;}
th,td{border:1px solid var(--border);padding:.4rem .6rem;text-align:left;color:var(--text-2);} th{background:var(--surface-2);color:var(--text);}
.dbar{height:.7em;background:var(--ember);border-radius:3px;display:inline-block;vertical-align:middle;}
textarea{background:var(--bg);color:var(--text-2);border:1px solid var(--border);border-radius:8px;}
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
:root{--bg:#0a0a0d;--surface:#16161b;--surface-2:#1c1c22;--border:#2a2a32;--text:#f0f0f3;--text-2:#a8a8b3;--text-3:#6b6b78;
      --ember:#ff7530;--ember-2:#ffac4a;--ember-3:#fff0c8;
      --font:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;}
*{box-sizing:border-box;}
body{font-family:var(--font);background:var(--bg);color:var(--text);line-height:1.6;
     max-width:52rem;margin:0 auto;padding:2.5rem 1.2rem;-webkit-font-smoothing:antialiased;
     background-image:radial-gradient(ellipse at top,rgba(255,117,48,.06) 0%,transparent 55%);}
h1{font-size:1.55rem;font-weight:800;letter-spacing:-.02em;
   background:linear-gradient(135deg,var(--ember),var(--ember-2) 60%,var(--ember-3));-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;}
.caption{color:var(--text-2);margin-top:1rem;}
.mermaid{margin:1.5rem 0;text-align:center;background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:1.2rem;}
table{border-collapse:collapse;margin:1rem 0;width:100%;}
th,td{border:1px solid var(--border);padding:.5em .75em;text-align:left;color:var(--text-2);} th{background:var(--surface-2);color:var(--text);}
.note{color:var(--text-3);font-size:.85em;margin-top:2rem;}
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
    "mermaid.initialize({startOnLoad:true,theme:'dark'});"
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
:root{--bg:#0a0a0d;--surface:#16161b;--surface-2:#1c1c22;--border:#2a2a32;--text:#f0f0f3;--text-2:#a8a8b3;--text-3:#6b6b78;
      --ember:#ff7530;--ember-2:#ffac4a;--ember-3:#fff0c8;--green:#5fbf7a;--red:#ff5a4a;
      --font:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;}
*{box-sizing:border-box;}
body{font-family:var(--font);background:var(--bg);color:var(--text);max-width:44rem;margin:0 auto;padding:2.5rem 1.2rem;
     -webkit-font-smoothing:antialiased;background-image:radial-gradient(ellipse at top,rgba(255,117,48,.06) 0%,transparent 55%);}
h1{font-size:1.7rem;font-weight:800;letter-spacing:-.02em;
   background:linear-gradient(135deg,var(--ember),var(--ember-2) 60%,var(--ember-3));-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;}
h2{font-size:1.1rem;font-weight:700;color:var(--ember-2);margin-top:1.8rem;}
.verdict{font-size:1.5em;font-weight:800;padding:.7rem 1.1rem;border-radius:10px;margin:1rem 0;}
.go{background:rgba(95,191,122,.12);color:var(--green);border:1px solid var(--green);}
.notyet{background:rgba(255,90,74,.1);color:var(--red);border:1px solid var(--red);}
.row{display:flex;align-items:center;gap:.6rem;margin:.5rem 0;}
.row .lab{width:14rem;font-size:.92em;color:var(--text-2);} .row .num{width:3rem;text-align:right;font-variant-numeric:tabular-nums;}
.track{flex:1;background:var(--surface-2);border:1px solid var(--border);border-radius:6px;height:.85rem;overflow:hidden;}
.fill{height:100%;border-radius:6px;}
.mock{display:inline-block;width:2.6rem;text-align:center;padding:.35rem 0;margin:.15rem;border-radius:6px;font-weight:700;font-size:.85em;}
.big{font-size:2em;font-weight:800;color:var(--ember-2);} .muted{color:var(--text-3);}
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
