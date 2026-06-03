# Anki deck, study guide & practice exam — how to generate them

Two bundled python scripts (stdlib-only; one optional dependency) do the
mechanical formatting so you never hand-format TSV or HTML. You produce the
*content* as JSON; the script produces a valid artifact.

Run them with `python3` from the skill's `scripts/` directory. Write outputs into
the sprint folder `~/learning-sprints/<slug>/`.

## Anki deck — `scripts/anki_export.py`

Write a `cards.json`, then:

```
python3 scripts/anki_export.py ~/learning-sprints/<slug>/cards.json
```

- Always writes `cards.tsv` (zero dependencies). Tell the user: **Anki →
  File → Import** — the directives auto-map every column.
- Also writes `cards.apkg` **iff** `genanki` is importable (`pip install genanki`);
  that's a one-click double-click import. Don't require it; TSV is the default.

`cards.json` shape (see the script header for the full spec):

```json
{
  "deck": "AWS SAA-C03",
  "cert_slug": "aws-saa-c03",
  "cards": [
    {"id": "saa-0001", "type": "basic", "front": "...", "back": "...",
     "domain": "domain1-design-secure", "topics": ["vpc"]},
    {"id": "saa-c-0001", "type": "cloze",
     "text": "An S3 bucket is {{c1::private}} by default.", "extra": "",
     "domain": "domain1-design-secure", "topics": ["s3"]}
  ]
}
```

Rules that matter:
- **`id` must be stable** across regenerations — it becomes the Anki GUID, so
  re-exporting + re-importing *updates* cards instead of duplicating them. Reuse the
  same ids as the progress file's `cards:` entries.
- **Cloze** cards use `{{c1::...}}`, `{{c2::...::hint}}` in `text`; leave `extra` "".
- `domain` becomes the hierarchical tag `<cert_slug>::<domain>`, so the user can
  study one domain at a time in Anki (search `tag:<cert_slug>::<domain>` or build a
  filtered deck). `topics` become extra flat tags.
- Good cert decks are mostly Basic recall + Cloze for facts/numbers. Generate cards
  from the cheat sheet and from every Stage-3 miss.

## Chapters, the board & the dashboard — `scripts/build_docs.py`

- **Chapter** (`type: chapter`) — a digestible lesson; always offer HTML or PDF.
  `{"type":"chapter","title":..,"subtitle":..,"sections":[{"heading":..,"body_html":"<p>..</p>","example":{"body_html":"<p>..</p>"},"keypoints":[..]}],"check":[{"q":..,"a":..}]}`.
  `example` renders a callout; `check` renders collapsible self-test questions.
- **The board** (`type: board`) — an on-demand visual. `{"type":"board","title":..,
  "mermaid":"graph LR; A-->B","html":"<table>..</table>","caption":..}`. Provide
  `mermaid` for a diagram/flow/tree (rendered via Mermaid; needs internet to draw,
  degrades to readable source) and/or `html` for styled tables/labeled boxes. Use on
  any "show me / put it on the board / visualize."
- **Dashboard** (`type: dashboard`) — readiness at a glance, computed by the script:
  `{"type":"dashboard","title":..,"pass_pct":80,"streak_target":3,"min_domain":65,
  "exam_date":..,"cards_due":N,"domains":[{"name":..,"weight":28,"mastery":70}],
  "mocks":[{"date":..,"pct":81}]}`. Verdict is **GO** only when `streak_target` mocks
  are ≥ `pass_pct` AND no domain mastery < `min_domain`; otherwise **NOT YET**. Feed it
  straight from the progress file's `domains` + `mocks`.

**Full course** (`type: course`) — bundle many chapters into ONE self-contained HTML
with a **left-side tab per chapter** the student works through (prev/next nav, deep-link
hashes, dark theme, print shows all chapters). Spec: `{"type":"course","title":..,
"chapters":[{"id":"c0","nav_title":"0 · Intro","title":..,"subtitle":..,"sections":[...],
"check":[...]}]}` — each chapter takes the same `sections`/`check` shape as `type: chapter`.
Use it to deliver the whole syllabus as one document.

## Study guide & practice exam — `scripts/build_docs.py`

```
python3 scripts/build_docs.py ~/learning-sprints/<slug>/guide.json
python3 scripts/build_docs.py ~/learning-sprints/<slug>/exam.json
```

- Always writes a **self-contained `.html`** (inline CSS, print-tuned). Tell the
  user: open it and **Print → Save as PDF** — needs nothing installed.
- Also writes a `.pdf` automatically **iff** `wkhtmltopdf`, `weasyprint`, or
  `pandoc` (with a PDF engine) is on PATH. Don't require it.

Study-guide JSON: `{"type":"study_guide","title":..,"subtitle":..,"sections":[{"heading":..,"body_html":"<p>..</p>","keypoints":[..]}]}`
— `body_html` is trusted rich HTML you write; keypoints render as a callout box.

Practice-exam JSON: `{"type":"practice_exam","title":..,"subtitle":..,"questions":[{"stem":..,"type":"mc","choices":[..],"answer":"C","explanation":..}]}`
— `type:"free"` gives a write-in box instead of choices. The answer key is forced
onto its own page so it can be printed and separated.

**Scored mock exam** (the cert readiness tool) — `{"type":"mock_exam","title":..,
"time_limit_min":130,"pass_pct":72,"domains":{"d1":"Data Engineering",..},
"questions":[{"stem":..,"type":"single|multi","choices":[..],"answer":"C" | ["B","D"],
"explanation":..,"domain":"d1"}]}`. Produces a self-contained interactive HTML: a
countdown timer that auto-submits, a PASS / NOT YET verdict against `pass_pct`, a
per-domain score breakdown, and inline answer review. `answer` is the choice letter(s)
(A=first choice); set `domain` per question so the breakdown is meaningful. Give each
question a stable **`id`** and a short **`concept`** so misses map back to cards and
re-teaching. Pull `pass_pct`, `time_limit_min`, and the `domains` map from the official
exam guide. See `certification-mode.md` for making it mirror the real test.

**Closing the loop:** the mock scores in the browser and ends with a "Copy results"
button emitting a JSON payload (`score`, `pct`, `pass`, `per_domain`, and `missed` with
each item's `id`/`domain`/`concept`/`your`/`correct`). When the user pastes it back,
update the progress file, mint Anki cards for the misses, run a targeted Feynman
re-teach on those concepts, and `/schedule` spaced re-quizzes — see SKILL.md Stage 7.
