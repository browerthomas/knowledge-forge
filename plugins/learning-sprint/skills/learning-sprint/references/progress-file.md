# Progress file — cross-session memory

Every sprint persists to one human-readable file so it can be **resumed** in a
later conversation. This is the single source of truth all exports read from.

## The lane index (cross-lane memory)

A student may have **several lanes** going at once (e.g. two certs). The teacher keeps
a roster so it remembers the whole picture and where each lane was left off:

```
~/learning-sprints/index.md
```

One line per lane — goal, readiness, last session, and the next action:

```markdown
# Learning lanes
- [AWS MLA-C01](aws-mla-c01/progress.md) — ML Engineer Associate · readiness 26% · last 2026-06-02 · next: teach Chapter 1 (Data Prep)
- [CKA](cka/progress.md) — Certified Kubernetes Admin · readiness 0% · last 2026-05-30 · next: research gate + plan
```

**On activation, read the index first.** If the student names a topic, open that lane.
If they don't, show the roster — *"You've got two lanes going: MLA-C01 (next: Chapter 1)
and CKA (not started). Which today?"* — and let them pick. Create a new lane (and add a
line) when they start a new topic. **Update the lane's line after every session.**

## Machine state vs. human narrative

Each lane keeps two things:
- **`state.json`** — the **machine source of truth**, owned by `scripts/progress.py`
  (domains/mastery, SR cards, mock history, question bank, readiness inputs). **Always
  read and update it through `progress.py`** — never hand-edit the SR math, mock
  history, or readiness; that's what kept drifting. The dashboard and mock exams are
  generated *from* it, not hand-computed.
- **`progress.md`** — the human-readable narrative you maintain: the research brief,
  cheat sheet, session log, weak-spot notes. This is for the student to read.

Typical commands (see `progress.py -h`): `init`, `set-domains`, `add-card`, `review`,
`due`, `add-questions`, `sample-mock`, `record-mock`, `set-mastery`, `readiness`,
`dashboard`, `reindex`. Pass `--today YYYY-MM-DD` for deterministic dates.

## Per-lane files

```
~/learning-sprints/<slug>/state.json        # machine state — managed by progress.py
~/learning-sprints/<slug>/progress.md       # human narrative (brief, cheat sheet, log)
~/learning-sprints/<slug>/cards.json        # card spec for anki_export.py
~/learning-sprints/<slug>/cards.tsv|.apkg   # generated Anki deck
~/learning-sprints/<slug>/study-guide.html  # generated study guide
~/learning-sprints/<slug>/practice-exam.html
```

`<slug>` is the topic kebab-cased (e.g. `aws-saa-c03`, `kubernetes-networking`).
Create the directory if it doesn't exist. Keep everything for one topic together.

## Format

YAML frontmatter holds the machine-readable state; the markdown body holds
human-readable notes and the cheat sheet.

```markdown
---
sprint: aws-saa-c03
topic: "AWS Certified Solutions Architect – Associate (SAA-C03)"
type: certification            # certification | skill | theory | tool
goal: "Pass SAA-C03"
background: "Knows ML generally; new to AWS services"  # where the student started — tailor to this
exam_date: 2026-07-15          # omit if not a dated exam
created: 2026-06-02
last_session: 2026-06-02
sessions: 1
# Certification only — official exam blueprint, weights, and current mastery (0-100):
domains:
  - {id: domain1-design-secure,    name: "Design Secure Architectures",     weight: 30, mastery: 40}
  - {id: domain2-resilient,        name: "Design Resilient Architectures",  weight: 26, mastery: 25}
  - {id: domain3-high-performing,  name: "Design High-Performing",          weight: 24, mastery: 30}
  - {id: domain4-cost-optimized,   name: "Design Cost-Optimized",           weight: 20, mastery: 20}
# Spaced-repetition state (SM-2). One entry per card. See spaced-repetition.md.
cards:
  - {id: saa-0001, concept: "Shared Responsibility Model", domain: domain1-design-secure,
     ease: 2.5, interval_days: 1, repetitions: 1, due: 2026-06-03, lapses: 0, last_grade: 4}
weak_spots: ["VPC peering vs Transit Gateway", "S3 storage-class trade-offs"]
# Mock-exam history — drives the readiness verdict (>=80% on >=3 mocks, no weak domain):
mocks:
  - {date: 2026-06-08, pct: 62, per_domain: {d1: 70, d2: 55}}
  - {date: 2026-06-12, pct: 81, per_domain: {d1: 80, d2: 75}}
readiness: 38                  # rough overall % (weighted mean of domain mastery)
researched: 2026-06-02         # when the research gate last ran (refresh if stale)
sources:                       # cited knowledge base from the research gate
  - {title: "AWS SAA-C03 Exam Guide", url: "https://...", checked: 2026-06-02}
  - {title: "Official AWS Well-Architected Framework", url: "https://...", checked: 2026-06-02}
---

# AWS SAA-C03 — Sprint Notes

## Research brief
<what's actually current, the real 20%, the recommended path, key pitfalls —
all grounded in `sources:` above. This is the substrate every stage draws from.>

## Session log
- 2026-06-02 — Research gate run (4 sources); Stage 1 plan built; quizzed domain 1 (6/10).

## Cheat sheet
<the one-page cheat sheet, kept current; cite sources, flag anything unverified>
```

## Resume protocol (run on every activation)

1. Slugify the topic and look for `~/learning-sprints/<slug>/progress.md`.
2. **If it exists**, load it and **skip the cold-start orientation card**. Instead show a
   short resume card:
   > **Resuming AWS SAA-C03** — last session 3 days ago. Exam in 43 days. Weakest:
   > Domain 2 (25%), Domain 4 (20%). **5 cards due** for re-quiz.
   > Continue where we left off, re-quiz the due cards, or jump to a stage?
3. **If it doesn't exist**, run the normal first-run orientation, then create the file
   after the first stage produces real state.
4. **After every stage**, update the frontmatter (mastery, cards, weak_spots,
   last_session, sessions) and append a one-line session-log entry. Recompute
   `readiness` as the weight-weighted mean of domain mastery.

## Why a single MD-with-frontmatter file

- Human-openable and editable; the user owns it and can read their own progress.
- Machine-parseable header drives resume, due-card queues, and every export.
- One source of truth → the cheat sheet, Anki deck, study guide, and practice exam
  are all generated from the same state, never drift apart.
- No database, no extra dependency, git-friendly, portable.
