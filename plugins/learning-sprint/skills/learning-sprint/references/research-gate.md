# Research Gate — ground before you teach (HARD GATE)

**The single most important rule in this skill: never teach from memory.** Model
training is stale and lossy. Before producing *any* learning material — the plan, the
cheat sheet, quiz questions or their answers, the ladder, explanations — research the
topic against current sources. No guessing, ever. If you can't verify it, you flag it
or you don't say it.

This gate runs **once per sprint, before Stage 1**, on a true cold start (a resumed
sprint already has its researched base in the progress file — refresh only if stale or
the user asks).

## What the gate does

1. **Map the topic with multi-source web research.** Run several searches, don't stop
   at the first hit. Establish, from current sources:
   - What the topic actually *is today* (versions, current consensus, what changed).
   - Genuine prerequisites and the real high-leverage **20%** — what experts say
     drives most of the results, not what you assume.
   - The canonical learning path(s) practitioners actually recommend.
   - Common pitfalls, misconceptions, and gotchas.
   - The current best resources (this also seeds Stage 5).
2. **Read primary/authoritative sources.** Fetch and actually read the load-bearing
   ones — official docs, specs, well-regarded syllabi, expert write-ups. For a
   **certification**, fetch the *current official exam guide* (domains, weights,
   format, version) — see `certification-mode.md`.
3. **Cross-check and date-check.** Verify any non-trivial claim against **≥2
   independent current sources**. Distrust single-source claims and anything that
   smells outdated; check publication dates. Adversarially ask "what would make this
   wrong or stale?"
4. **Record a cited knowledge base** in the progress file: the key findings plus a
   `sources:` list (title, URL, date checked). Everything downstream cites it.

## Depth scaling

Effort is a spectrum, matched to the stakes — no guessing applies at every level, but
the *weight* of the response differs enormously:

- **Easy / one-off question** ("what are the OSI layers?") → this usually isn't a
  sprint at all. Just answer it, after a **quick validation** of the facts against a
  current source. Don't spin up the full apparatus.
- **Quick / well-bounded topic** → a focused pass: several searches + fetch the few
  authoritative sources, cross-checked.
- **Stated credential / exam / role-readiness goal** ("I'm trying to get the AWS
  Certified Machine Learning – Associate," "ramp me for a staff SRE interview") → the
  signal to **go deep AND build it all out**. Deep multi-source research (broad
  fan-out, primary sources, adversarial verification — fetch the current official exam
  guide), then proactively offer the full sprint: plan → ladder → cheat sheet → quiz →
  Feynman → Anki deck + study guide + practice exam, all persisted for resume. **If a
  deep-research capability/skill is available in the environment, use it** for the
  gate; otherwise perform the deep research directly following this protocol.

## Hard rules (apply to every stage that follows)

- **Never** generate the plan, cheat sheet, quiz, ladder, milestones, or explanations
  from model memory alone. Everything traces to the researched base.
- **Cite** sources for substantive claims (cheat sheet facts, the 80/20 selection,
  quiz answers, resource picks).
- **Flag the unverified.** If you could not confirm something against a current
  source, label it "⚠️ unverified — confirm before relying on this," or leave it out.
  Do not fill gaps with plausible-sounding guesses.
- If research can't establish something important, **say so plainly** and tell the
  user what you'd need to confirm it.

## If web tools aren't available (e.g. Cowork with web search off)

Some surfaces gate web access (in Claude Cowork an Owner must enable Web Search, then
the user toggles it on per chat). If you have no working web search/fetch:
1. **Lean entirely on the user's own materials** (`your-materials.md`) — the official
   exam guide, course, notes. This is the best ground truth anyway.
2. **Say so explicitly:** "Web search isn't available here, so I'm building from your
   materials only — enable Web Search (or paste a source) and I'll validate against
   the current web." Record the limitation in the progress file.
3. **Still never guess.** Better to mark something "⚠️ unverified" than to invent it.

## Present before proceeding

After the gate, show a short **research brief** — "here's what's actually current,
here's the real 20%, here are the sources, here's how we'll attack it" — then start
Stage 1. The user should see the sprint is grounded, not guessed.
