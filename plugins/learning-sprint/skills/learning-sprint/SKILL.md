---
name: learning-sprint
description: "Run a structured, resumable learning session that takes any topic from zero to retained understanding using chained techniques: a 20-hour 80/20 plan, a one-page cheat sheet, progressive quizzing, a 5-level difficulty ladder, web-validated resources, the Feynman re-teach loop, and spaced-repetition export (Anki deck, printable study guide, practice exam). Always grounds the material in fresh multi-source web research BEFORE presenting anything — never teaches from memory or guesswork. Progress persists across sessions, so sprints can be resumed. Strong fit for certification study (AWS/Azure/GCP, CompTIA, CISSP, PMP, CKA, etc.). MANDATORY TRIGGERS: 'learning sprint', 'run a sprint on', 'teach me', 'I need to learn X fast', 'help me master X', 'tutor me on X', 'I want to learn X', 'study for my <cert> exam', 'help me pass <cert>', 'make me flashcards / an Anki deck for X', 'build a study guide for X', 'make a practice exam for X', 'resume my sprint'. STRONG TRIGGERS (use when paired with a real topic and intent to actually learn, not a one-off lookup): 'how do I get good at X', 'where do I start with X', 'quiz me on X', 'explain X then test me', 'build me a study plan for X', 'I'm trying to ramp up on X'. Do NOT trigger on simple factual lookups ('what is X'), single definition requests, or when the user just wants one answer rather than to build durable understanding."
---

# Learning Sprint

Takes any topic from zero to retained, testable understanding using chained
techniques. Each stage feeds the next: plan → compress → test → sequence →
resource → re-teach → retain. The whole thing runs interactively — the user does
real cognitive work, not passive reading — and **persists across sessions** so a
sprint can be paused and resumed days later.

The stages are modular. Run the full sprint, or jump to any single stage on
request (e.g. "just quiz me on X" → Stage 3 only).

## Bundled resources

Read these as needed; they hold the load-bearing detail so this file stays lean:
- `references/research-gate.md` — **mandatory** research-before-teaching gate (no guessing).
- `references/your-materials.md` — prefer the user's own exam guide / course / notes.
- `references/progress-file.md` — the cross-session state file + **resume protocol**.
- `references/certification-mode.md` — exam blueprints, weighting, realistic exams.
- `references/spaced-repetition.md` — SM-2 rule for in-app re-quizzing + Anki split.
- `references/anki-and-exports.md` — how to drive the two generator scripts.
- `scripts/anki_export.py` — cards JSON → Anki `.tsv` (+ `.apkg` if genanki present).
- `scripts/build_docs.py` — content JSON → print-ready `.html` (+ `.pdf` if a tool exists).

---

## On Activation — Resume First, Then Orient

**Before anything else, check for an existing sprint** (see `references/progress-file.md`):
slugify the topic and look for `~/learning-sprints/<slug>/progress.md`.

- **If it exists**, load it and show the short **resume card** (last session, days to
  exam, weakest domains, count of due re-quiz cards), then offer: continue / re-quiz
  due cards / jump to a stage / start fresh. **Skip the cold-start orientation.**
- **If it doesn't exist**, run the first-run orientation below. It fires **once per
  conversation**; once the sprint is underway, never show it again.

### First-run orientation (cold start only)

**1. Show the compact orientation card** (roughly one mobile screen):

> **Learning Sprint** — I'll take **[topic]** from zero to retained understanding using chained techniques, and save your progress so you can resume anytime. You do the thinking; I drive the structure and grade you honestly.
>
> 1. **Plan** — 20-hour roadmap, the 20% that drives 80%
> 2. **Cheat Sheet** — one page, 5-minute review
> 3. **Quiz** — 10 questions, hardest at the end, graded live
> 4. **Ladder** — 5 levels, a checkable milestone each
> 5. **Resources** — top 5, current, justified
> 6. **Feynman Loop** — you teach it back until it's clean
> 7. **Retain** — Anki deck, study guide & practice exam, spaced re-quizzes
>
> Two ways to run: the **full sprint** or a **single stage** ("just quiz me," "build the plan," "make me an Anki deck").

Substitute the actual topic into **[topic]**. If they didn't name one, ask here.

**2. Offer the run-mode choice as tappable buttons** via `ask_user_input_v0`:
- *Full sprint — all seven stages*
- *Just one stage — I'll pick*
- *Jump straight in*

**3. After they choose**, begin with the scoping question: *what do you want to be
able to DO at the end?* — every stage is bounded by that goal. Then **run the research
gate** (below) before producing any material. If it's a **certification**, also read
`references/certification-mode.md` and capture the exam date and blueprint now.

Skip orientation entirely if the trigger already names both a stage and a topic with
no ambiguity (e.g. "just quiz me on TLS handshakes" → go straight to Stage 3) — but the
research gate still applies before you produce content.

---

## Ground First — Research Gate (MANDATORY)

**Never teach from memory. Research the topic against current sources before producing
any plan, cheat sheet, quiz, ladder, or explanation. No guessing, ever.** This fires
once per sprint, before Stage 1, on a cold start (a resumed sprint already has its
researched base — refresh only if stale).

**First ask if the user has their own material** (official exam guide, course, slides,
notes, an existing deck) and build from it — see `references/your-materials.md`. Their
authoritative source beats the open web for *what* to learn.

Then read and follow `references/research-gate.md`. In short: do genuine multi-source
web research, read the authoritative/primary sources, cross-check every non-trivial
claim against ≥2 current sources, and record a cited knowledge base in the progress
file.
Scale depth to the stakes — go deep for certifications, interviews, and broad fields,
using a deep-research capability if one is available. Then show a short **research
brief** ("here's what's actually current, the real 20%, the sources") before Stage 1.

Hard rules that bind every stage below: everything traces to the researched base;
cite substantive claims; flag anything you couldn't verify as "⚠️ unverified"; if
research can't confirm something important, say so rather than guess.

---

## When to Run

**Good sprint topics:** anything the user wants to actually *retain* and *use* — a
framework, a certification domain, a language feature, a body of theory, a tool.
- "Teach me Kubernetes networking" · "Study for my AWS SAA-C03 exam" · "Help me master RAG before my interview"

**A stated credential / exam / role-readiness goal is the strongest signal** — e.g.
"I'm trying to get the AWS Certified Machine Learning – Associate." Go deep on the
research gate and **proactively offer to build the whole thing out** (plan → ladder →
cheat sheet → quiz → Feynman → Anki deck + study guide + practice exam), persisted for
resume. See `references/research-gate.md` (depth scaling).

**Not a sprint:** one-off factual questions, single definitions, quick lookups —
answer those directly, after a quick validation of the facts. No guessing, but no
need for the full apparatus either.

---

## The Seven Stages

| # | Stage | What it produces |
|---|---|---|
| 0 | **Research Gate** | A cited, current knowledge base — runs first, mandatory, no guessing |
| 1 | **20-Hour Plan** | A 10-session 80/20 roadmap targeting the vital 20% |
| 2 | **One-Page Cheat Sheet** | A single-page compression — bullets, diagrams, examples |
| 3 | **Quiz Until You Break** | 10 progressively harder questions, graded, with gap analysis |
| 4 | **Learning Ladder** | 5 difficulty levels with a milestone at each rung |
| 5 | **Best Resources** | Top 5 books/videos/courses/people, each justified |
| 6 | **Feynman Loop** | User re-explains; Claude finds gaps, re-teaches, repeats |
| 7 | **Retain & Export** | Anki deck, study guide, practice exam, spaced re-quizzes |

**Recommended order for a cold start:** 0 (gate) → 1 → 5 → 4 → 2 → 3 → 6 → 7. The
gate is not optional — every other stage draws from its researched base. Honor
whatever order the user asks for, but never skip the gate before producing content.

---

## Stage 1 — 20-Hour Plan

Build a 20-hour plan focused on the 20% that drives 80% of results. Break it into
**10 two-hour sessions**, each with:
- A specific, outcome-based objective (not "learn X" but "be able to do Y")
- The single best resource for that session
- A **15-minute review** block at the end of each session

Be ruthless about scope. Cut anything not load-bearing for the stated goal. **Base the
80/20 on what the research gate found experts actually recommend — not on a guess.** If
no goal was given, ask: *what do you want to be able to DO at the end?* For a
certification, allocate time by **domain weight × (1 − mastery)** — see
`references/certification-mode.md`. If the user has less than 20 hours, scale the plan
to their actual budget.

---

## Stage 2 — One-Page Cheat Sheet

Summarize the key concepts on a **single page** reviewable in 5 minutes. Bullets,
simple ASCII/text diagrams where they clarify, one concrete example per concept.
Optimize for recall, not completeness — a memory anchor, not documentation. **Every
fact comes from the researched base; flag anything unverified rather than guessing.**

Save it into the progress file's body, and offer to render it as a polished study
guide in Stage 7. The cheat sheet is also the main source for Anki cards.

---

## Stage 3 — Quiz Until You Break

Generate **10 progressively harder questions** — Q1 trivial, Q10 expert-edge.
Deliver them **one at a time**. After each answer:
1. **Grade it** (correct / partial / wrong) — favor free-recall and application
   questions over recognition; don't give the answer away in the stem.
2. **Explain what was missed** — the actual gap, not just the right answer.
3. Only then reveal the next question.

Questions and their correct answers come from the researched base, not memory — if you
can't ground an answer in a current source, don't ask that question. Stop early if the
user breaks (two wrong in a row) and re-teach the failing concept before continuing.
**Record every miss** in the progress file's `weak_spots` and turn each into an Anki
card — these feed Stage 6 and Stage 7. Do not dump all 10 at once.

---

## Stage 4 — Learning Ladder

Break the topic into **5 levels**, Level 1 (beginner) → Level 5 (advanced). For each:
- What you can do at this level
- A **clear, checkable milestone** that proves you've reached it (objective — "can
  deploy a 3-node cluster from scratch," never "understand clusters better")
- The bridge to the next level

For technical topics in Claude Code, offer to **actually do** a milestone with the
user (run the code, build the thing) and verify it — not just describe it.

---

## Stage 5 — Best Resources

List the **top 5 resources** (books, videos, courses, people). For each, explain
**why it's worth the time** — what it uniquely gives.

**ALWAYS web-search to validate current resources.** Don't list from memory — books
go out of print, courses get deprecated, better material ships constantly. Search,
then cite. Flag anything you couldn't verify is current.

---

## Stage 6 — Feynman Loop

The retention engine. Run it as a real loop:
1. Claude explains the topic in the **simplest possible terms**.
2. User re-explains it back in their own words.
3. Claude **points out gaps** — what was vague, wrong, or missing. Be honest; false
   "great job!" defeats the technique. Name the hole precisely.
4. Claude **re-teaches only the gap**.
5. Repeat until the user produces a clean explanation **unprompted**.

Feed in the Stage-3 misses as priority targets. If a concept won't come clean after a
few rounds, offer an off-ramp: "let's park this one and move on" — don't grind the
user into discouragement.

---

## Stage 7 — Retain & Export

Turn the session into durable, portable artifacts. Offer these (read
`references/anki-and-exports.md` and `references/spaced-repetition.md`):

- **Anki deck** — generate cards from the cheat sheet + every Stage-3 miss, write
  `cards.json`, run `scripts/anki_export.py`. Tag by exam domain. Default to TSV;
  `.apkg` if genanki is installed.
- **Study guide** — a polished, printable HTML (→ Save as PDF) via `build_docs.py`.
- **Scored mock exam** — for certifications, an interactive, timed, self-scoring mock
  (`type: mock_exam` via `build_docs.py`): countdown timer, auto-submit, a PASS / NOT
  YET verdict against the real passing percentage, a **per-domain score breakdown**,
  and inline answer review. This *is* the readiness gate — feed every missed question
  back into `weak_spots` and the SR deck. Build it blueprint-weighted; see
  `references/certification-mode.md`.
- **Printable practice exam** — a static `type: practice_exam` PDF/HTML with a
  page-broken answer key, for offline work.
- **Spaced re-quizzes** — keep SM-2 state in the progress file and offer to
  `/schedule` re-quiz sessions on the due dates, so retention actually compounds.

Always update the progress file before ending so the sprint can be resumed.

---

## Execution Notes

### Resume first, orient once, then get out of the way
On activation, always check for an existing sprint and resume it. On a true cold
start, run orientation once, then drop the scaffolding and run the stages. Don't
re-explain the stages at every transition.

### Persist everything
Maintain `~/learning-sprints/<slug>/progress.md` (see `references/progress-file.md`).
After every stage, update mastery, weak spots, card SR state, and the session log.

### Interactive by default
Stages 3 and 6 are loops, not lectures. Wait for the user's actual response before
advancing. Never simulate the user's side of a quiz or re-teach.

### One topic, threaded through
Carry the same topic and weak spots across all stages. Stage 3's misses drive Stage
6's loop and Stage 7's cards; Stage 1's scope bounds Stage 4's ladder; for a cert,
the blueprint weights bound the plan, quiz, and practice exam.

### Research first, never guess
The research gate (Stage 0) is mandatory and binds every other stage: all content
traces to current, cross-checked sources; substantive claims are cited; anything
unverifiable is flagged "⚠️ unverified" rather than asserted. Stage 5 and any resource
mention require a live web search. When research can't confirm something, say so — do
not fill the gap with a plausible guess.

### Grade honestly
Stages 3, 6, and the readiness call only work if feedback is truthful — calibrate
difficulty up when the user is cruising, stop to re-teach the moment they stall, and
never give false "you're ready."

---

## Quick Reference

```
0. RESUME   → check ~/learning-sprints/<slug>/; resume if found, else orient once
   RESEARCH → MANDATORY gate: multi-source web research, cited base, NO guessing
1. PLAN     → 20hr, 10 sessions, 80/20, 15-min reviews (cert: weight time by blueprint)
2. COMPRESS → one page, bullets + diagrams + examples
3. TEST     → 10 questions, one at a time, graded, gaps named + recorded
4. SEQUENCE → 5 levels, checkable milestone each
5. RESOURCE → top 5, justified, WEB-VALIDATED
6. RE-TEACH → Feynman loop until clean unprompted explanation
7. RETAIN   → Anki deck + study guide + scored timed mock exam + scheduled re-quizzes
```
