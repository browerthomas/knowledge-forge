# Ground in the user's own materials

The research gate validates against the open web. But the user often already has the
**authoritative** source — the official exam guide PDF, a course they bought, lecture
slides, a textbook, their own notes, or an existing flashcard deck. Prefer that
material: it's what they'll actually be tested on, and using it extends "no guessing"
to "use the source of truth they already have."

## Ask early

At the start of a sprint (right after scoping, alongside the research gate), ask:

> Do you have any source material for this — the official exam guide, a course
> syllabus, slides, a textbook, notes, or an existing deck? Point me at the files (or
> paste a link) and I'll build from those, not just the web.

If they share files, **read them** (the Read tool handles PDFs, notebooks, and text).
If they give a URL, fetch it. If they have nothing, fall back to the research gate's
web sources alone.

### When a PDF won't parse (have a fallback — don't dead-end)

PDF extraction can fail: PDF page-rendering may be unavailable (needs poppler /
`pdftotext`), a web-fetched PDF may arrive as un-parsable compressed streams, and
small-model fetchers choke on binary. If you can't reliably read a PDF, **do not
guess its contents** — fall back, in order:
1. Try `pdftotext <file> -` if it's installed (best plain-text extraction).
2. Find the same content as **HTML** — the official guide and reputable summaries
   usually exist as web pages you *can* parse; cross-check several.
3. Ask the user to paste the relevant section (e.g. the domain list) as text.

Whatever you use, record it and its limitation honestly in the progress file (e.g.
"official PDF unparsed here; blueprint taken from the HTML guide + 2 corroborating
sources").

## How to use ingested material

- **Extract the real structure.** Pull the actual objectives / domains / weights / table
  of contents from the material and use it to drive Stage 1 (plan) and Stage 4 (ladder).
  For a cert, the official guide's domain list overrides any guessed structure.
- **Build content from it.** Cheat sheet, quiz questions, mock-exam items, and Anki
  cards should be grounded in the user's material first, the web second.
- **Cross-check, don't blindly trust.** User notes can be wrong or outdated. Where the
  material and current web sources disagree on something load-bearing, flag it and say
  which you trust and why. Course material can also lag the current exam version —
  check it against the official guide's date/version.
- **Cite the material** the same way you cite web sources (file name + section), and
  record it in the progress file's `sources:` list (e.g. `{title: "Official MLA-C01
  Exam Guide", file: "~/Downloads/mla-c01-guide.pdf", checked: <date>}`).
- **Respect privacy.** The material is the user's. Don't send its contents to external
  services beyond what's needed to verify facts; never publish it.

## Precedence

For *what to learn* (scope, structure, weights): **the user's official material wins**,
then the open web. For *whether a fact is current and correct*: cross-check both, and
flag conflicts rather than silently picking one.
