# Spaced repetition

The sprint promises *retained* understanding — and retention comes from **spaced
retrieval over days**, not one session. Two complementary mechanisms:

1. **In-app re-quiz (this skill owns it).** Lightweight SM-2 state in the progress
   file drives "re-quiz me on what I'm weak on" sessions. Schedule them with
   `/schedule` so they fire on the due date.
2. **Anki (owns the long-term daily loop).** Export cards one-way to Anki (see
   `anki-and-exports.md`); its FSRS scheduler handles serious long-horizon review.

**Do not two-way sync** the two — SM-2 and FSRS are different models and will fight.
Export is one-way (skill → Anki). The skill's SM-2 state only decides which cards to
surface in-app; Anki schedules its own copies independently.

## SM-2 update rule (apply when grading a re-quiz card)

Per card track `ease` (start **2.5**), `interval_days`, `repetitions` (consecutive
correct), `lapses`, `due`. Grade `q` is 0–5; **q ≥ 3 passes**.

```
if q >= 3:                       # correct
    if   repetitions == 0: interval_days = 1
    elif repetitions == 1: interval_days = 6
    else:                  interval_days = round(interval_days * ease)
    repetitions += 1
else:                            # failed — relearn from scratch
    repetitions = 0
    interval_days = 1
    lapses += 1

ease = ease + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
if ease < 1.3: ease = 1.3        # floor

due = today + interval_days
```

If you only show **Again / Hard / Good / Easy** buttons, map them to `q = 2 / 3 / 4 / 5`.

The natural interval progression with "Good" answers is roughly
**1d → 6d → 15d → 38d → 94d …**. That's the v1 default; it's fine to use it as-is.

## Driving re-quiz sessions

- "Due" = any card whose `due <= today`. On resume, count and surface them first.
- Prioritise the user's actual weak spots: sort due cards by high `lapses`, low
  `ease`, or a recent failing `last_grade`.
- To automate it, offer `/schedule`: e.g. re-quiz the due set in 2 days, then on each
  card's next `due`. Only offer a concrete date you can derive from the card state —
  never invent one. `/schedule` works in both Claude Code and Claude Cowork (in Cowork,
  scheduled tasks run only while the machine is awake and the Desktop app is open, so a
  due re-quiz may fire late — the SR state in the progress file makes manual resume
  work regardless).
