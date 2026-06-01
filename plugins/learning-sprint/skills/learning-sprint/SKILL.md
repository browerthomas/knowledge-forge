---
name: learning-sprint
description: "Run a structured learning session that takes any topic from zero to retained understanding using six chained techniques: a 20-hour 80/20 plan, a one-page cheat sheet, progressive quizzing, a 5-level difficulty ladder, curated resources, and the Feynman re-teach loop. MANDATORY TRIGGERS: 'learning sprint', 'run a sprint on', 'teach me', 'I need to learn X fast', 'help me master X', 'tutor me on X', 'I want to learn X'. STRONG TRIGGERS (use when paired with a real topic and intent to actually learn, not a one-off lookup): 'how do I get good at X', 'where do I start with X', 'quiz me on X', 'explain X then test me', 'build me a study plan for X', 'I'm trying to ramp up on X'. Do NOT trigger on simple factual lookups ('what is X'), single definition requests, or when the user just wants one answer rather than to build durable understanding."
---

# Learning Sprint

Takes any topic from zero to retained, testable understanding using six chained techniques. Each stage feeds the next: plan → compress → test → sequence → resource → re-teach. The whole thing runs interactively — the user does real cognitive work, not passive reading.

The six stages are modular. Run the full sprint, or jump to any single stage on request (e.g. "just quiz me on X" → Stage 3 only).

---

## On First Activation (Orientation)

**The first time this skill activates in a conversation, before running any stage**, orient the user. This fires once per conversation only — once the sprint is underway, never show it again; subsequent stage transitions and re-runs go straight to the work.

Do three things, in order:

**1. Show the compact orientation card** (keep it to roughly one mobile screen):

> **Learning Sprint** — I'll take **[topic]** from zero to retained understanding using six chained techniques. You do the thinking; I drive the structure and grade you honestly.
>
> 1. **Plan** — 20-hour roadmap, the 20% that drives 80%
> 2. **Cheat Sheet** — one page, 5-minute review
> 3. **Quiz** — 10 questions, hardest at the end, graded live
> 4. **Ladder** — 5 levels, a checkable milestone each
> 5. **Resources** — top 5, current, justified
> 6. **Feynman Loop** — you teach it back until it's clean
>
> Two ways to run: the **full sprint** (all six, optimal order) or a **single stage** ("just quiz me," "build the plan").

Substitute the actual topic into **[topic]** if the user named one (they usually do). If they didn't, ask for it here.

**2. Offer the run-mode choice as tappable buttons.** Use `ask_user_input_v0` (tappable options are easier on mobile and degrade fine to text). Present:
- *Full sprint — all six stages*
- *Just one stage — I'll pick*
- *Jump straight in* (skip the menu; you proceed with the cold-start order)

**3. After they choose**, begin. If they picked the full sprint or "jump in," the first real action is Stage 1's scoping question: *what do you want to be able to DO at the end?* — because every stage is bounded by that goal.

Skip the orientation entirely if the user's trigger already specifies both a stage and a topic with no ambiguity (e.g. "just quiz me on TLS handshakes" → go straight to Stage 3). Orientation is for cold starts, not for users who've already told you exactly what they want.

---

## When to Run

**Good sprint topics:** anything the user wants to actually *retain* and *use* — a new framework, a certification domain, a language feature, a body of theory, a tool, a discipline.
- "Teach me Kubernetes networking"
- "I need to learn options trading fast"
- "Help me master RAG architectures before my interview"

**Not a sprint:** one-off factual questions, single definitions, quick lookups. Just answer those directly.

---

## The Six Stages

| # | Stage | What it produces |
|---|---|---|
| 1 | **20-Hour Plan** | A 10-session 80/20 roadmap targeting the vital 20% |
| 2 | **One-Page Cheat Sheet** | A single-page compression — bullets, diagrams, examples |
| 3 | **Quiz Until You Break** | 10 progressively harder questions, graded, with gap analysis |
| 4 | **Learning Ladder** | 5 difficulty levels with a milestone at each rung |
| 5 | **Best Resources** | Top 5 books/videos/courses/people, each justified |
| 6 | **Feynman Loop** | User re-explains; Claude finds gaps, re-teaches, repeats |

**Recommended order for a cold start:** 1 → 5 → 4 → 2 → 3 → 6 (plan the time, point at resources, sequence the climb, compress, test, then cement by teaching back). But honor whatever the user asks for.

---

## Stage 1 — 20-Hour Plan

Build a 20-hour plan focused on the 20% that drives 80% of results. Break it into **10 two-hour sessions**, each with:
- A specific, outcome-based objective (not "learn X" but "be able to do Y")
- The single best resource for that session
- A **15-minute review** block at the end of each session

Be ruthless about scope. Cut anything that isn't load-bearing for the user's stated goal. If they gave no goal, ask one question: *what do you want to be able to DO at the end?*

---

## Stage 2 — One-Page Cheat Sheet

Summarize the key concepts on a **single page** the user can review in 5 minutes. Use bullet points, simple ASCII/text diagrams where they clarify, and one concrete example per concept. Optimize for recall, not completeness — this is a memory anchor, not documentation.

Offer to save this as a standalone file (markdown or, if they want something printable/polished, a PDF or .docx via the relevant skill).

---

## Stage 3 — Quiz Until You Break

Generate **10 progressively harder questions** — Q1 trivial, Q10 expert-edge. Deliver them **one at a time**. After each answer:
1. **Grade it** (correct / partial / wrong)
2. **Explain what was missed** — the actual gap, not just the right answer
3. Only then reveal the next question

Stop early if the user breaks (two wrong in a row) and re-teach the failing concept before continuing. Track which concepts they miss — that list feeds Stage 6.

Do not dump all 10 questions at once. The value is in the loop.

---

## Stage 4 — Learning Ladder

Break the topic into **5 levels of difficulty**, Level 1 (beginner) → Level 5 (advanced). For each level give:
- What you can do at this level
- A **clear, checkable milestone** that proves you've reached it
- The bridge to the next level — the specific thing to learn to climb one rung

The milestones must be objective ("can deploy a 3-node cluster from scratch"), never vague ("understand clusters better").

---

## Stage 5 — Best Resources

List the **top 5 resources** (books, videos, courses, or people) for learning the topic fast. For each, explain **why it's worth the time** — what it uniquely gives that the others don't.

**ALWAYS web-search to validate current resources.** Do not list from memory — books go out of print, courses get deprecated, creators stop publishing, better material ships constantly. Search, then cite. Flag anything you couldn't verify is current.

---

## Stage 6 — Feynman Loop

The retention engine. Run it as a real loop:
1. Claude explains the topic (or sub-topic) in the **simplest possible terms**
2. User re-explains it back in their own words
3. Claude **points out gaps** — what was vague, wrong, or missing
4. Claude **re-teaches only the gap**
5. Repeat until the user can explain it cleanly and unprompted

Be honest in step 3. False "great job!" defeats the entire technique. If an explanation has a hole, name it precisely. Feed in the missed concepts from Stage 3 as priority targets.

The loop ends when the user — not Claude — produces a clean explanation with no prompting.

---

## Execution Notes

### Orient once, then get out of the way
On the first activation in a conversation, run the orientation (see *On First Activation*) — but only once. After the user picks a mode, drop the scaffolding and run the actual stages. Don't re-explain the six stages at every transition.

### Interactive by default
Stages 3 and 6 are loops, not lectures. Wait for the user's actual response before advancing. Never simulate the user's side of a quiz or re-teach.

### One topic, threaded through
Carry the same topic and the same identified weak spots across all six stages. The sprint is more than the sum of the prompts — Stage 3's missed concepts should drive Stage 6's loop; Stage 1's scope should bound Stage 4's ladder.

### Validate resources, always
Stage 5 (and any resource mention elsewhere) requires a live web search. Training data has a cutoff; the internet is current.

### Honest grading
Stages 3 and 6 only work if feedback is truthful. Calibrate difficulty up when the user is cruising, and stop to re-teach the moment they stall.

### Save what's worth keeping
Offer to save the cheat sheet (Stage 2), the plan (Stage 1), and a session summary of weak spots so the user can resume a sprint later.

---

## Quick Reference

```
0. ORIENT   → first activation only: show card + tappable mode choice
1. PLAN     → 20hr, 10 sessions, 80/20, 15-min reviews
2. COMPRESS → one page, bullets + diagrams + examples
3. TEST     → 10 questions, one at a time, graded, gaps named
4. SEQUENCE → 5 levels, checkable milestone each
5. RESOURCE → top 5, justified, WEB-VALIDATED
6. RE-TEACH → Feynman loop until clean unprompted explanation
```
