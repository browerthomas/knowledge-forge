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
(A=first choice); set `domain` per question so the breakdown is meaningful. Pull
`pass_pct`, `time_limit_min`, and the `domains` map from the official exam guide. See
`certification-mode.md` for making it mirror the real test, and feed every miss back
into `weak_spots` + the Anki deck.
