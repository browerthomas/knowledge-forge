# Certification mode

When the topic is a named professional certification (AWS/Azure/GCP, CompTIA,
CISSP, PMP, CKA, etc.), specialise the sprint around the real exam.

## 1. Anchor on the official exam blueprint

- **Web-search the current exam guide** (e.g. "AWS SAA-C03 exam guide domains
  weights"). Vendors publish the domains and their percentage weights, and they
  change between exam versions — do not list from memory.
- Record the domains and weights in the progress file's `domains:` list. These
  weights drive everything:
  - **Stage 1 (plan):** allocate the 20 hours proportionally to domain weight ×
    (1 − mastery). Spend time where it pays off most on the scored exam.
  - **Stage 3 (quiz) / practice exam:** sample questions per domain in proportion
    to weight, so practice mirrors the real score distribution.
  - **Readiness:** `readiness = Σ(weight_i × mastery_i) / Σ(weight_i)`.

## 2. Capture the exam logistics

Ask for and store: exam date (→ `exam_date`, enables countdown + spacing),
question count, time limit, passing score, and question format (single-answer,
multiple-response, etc.). Use them to make the practice exam realistic.

## 3. Make the practice exam mirror the real thing

Build the practice exam (via `build_docs.py`, see `anki-and-exports.md`) to match
the real format:

- Same **question count** and **time limit** as the real exam where practical
  (offer a shorter "domain drill" too).
- **Scenario-based** stems, not definition recall — most associate/professional
  exams test application, not vocabulary.
- **Multiple-response** questions ("choose TWO") when the real exam has them.
- Plausible distractors — wrong answers that are wrong for an instructive reason,
  explained in the answer key.
- Weight questions per domain to match the blueprint.

## 4. Readiness gate

Before telling the user they're ready, check: weighted `readiness` ≥ the passing
score with margin, AND no single high-weight domain left weak. Report honestly —
"Domain 2 is 25% and it's 26% of the exam; you're not ready yet" beats false
comfort. The whole skill depends on honest grading.
