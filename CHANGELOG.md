# Changelog

All notable changes to **learning-sprint** (the `knowledge-forge` marketplace).

## 2.4.0
- New `course` output: bundle the whole syllabus into ONE self-contained HTML with
  left-side chapter tabs, prev/next nav, and deep-link hashes (dark theme; print shows
  all chapters). Lets the teacher deliver the entire curriculum as a single document.

## 2.3.0
- The chapter set is now a self-sufficient curriculum: a student should pass on the
  chapters alone. progress.py adds a syllabus + coverage tracking; readiness requires
  FULL coverage (every chapter delivered) AND >=3 mocks >=80% with no weak domain.
  Dashboard shows curriculum coverage.

## 2.2.1
- Chapters are now robust and self-contained by default: teach the underlying concept
  first, then the platform/tool specifics; don't assume fundamentals unless shown.

## 2.2.0
- Deterministic state: `scripts/progress.py` owns per-lane `state.json` (SM-2 review,
  due list, deduped question bank, weighted mock sampling, mastery, readiness verdict,
  dashboard spec, lane-index rebuild). Tracking no longer drifts.
- CI (`tests/smoke.sh` + GitHub Actions) and a secret/personal-data leak-check.
- README rewritten simple, with separate Claude Code and Cowork install paths.

## 2.1.0
- Dark "ember/steel" SaaS theme across all generated HTML; printable docs flip to
  clean light when printing. Cross-lane memory (`~/learning-sprints/index.md`).

## 2.0.0
- Reframed from a fixed pipeline into an adaptive **teacher with a toolkit**
  (`references/teaching.md`). New artifacts: chapters, the board (Mermaid visuals),
  readiness dashboard. Readiness threshold: ≥80% on ≥3 practice exams, no weak domain.

## 1.2.x
- Mandatory research gate (never teach from memory); effort scaled to stakes;
  credential goals trigger a deep build-out.

## 1.1.0
- Cross-session persistence + resume, SM-2 spaced repetition, Anki export, study
  guide + scored interactive mock exam, certification mode, ingest-your-own-materials.

## 1.0.0
- Initial release: six-stage learning sprint (plan, cheat sheet, quiz, ladder,
  resources, Feynman loop), published as a Claude Code plugin marketplace.
