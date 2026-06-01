# Progress file — cross-session memory

Every sprint persists to one human-readable file so it can be **resumed** in a
later conversation. This is the single source of truth all exports read from.

## Location

```
~/learning-sprints/<slug>/progress.md      # the state file
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
readiness: 38                  # rough overall % (weighted mean of domain mastery)
---

# AWS SAA-C03 — Sprint Notes

## Session log
- 2026-06-02 — Stage 1 plan built; quizzed domain 1 (6/10). Weak: VPC peering, S3 classes.

## Cheat sheet
<the one-page cheat sheet, kept current>
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
