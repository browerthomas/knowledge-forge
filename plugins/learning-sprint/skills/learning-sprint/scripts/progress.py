#!/usr/bin/env python3
"""Deterministic state for a learning lane — so tracking never drifts.

Machine state lives in <lane_dir>/state.json (this script owns it); the human-
readable progress.md narrative is maintained separately by the teacher. Exports
(dashboard, mock exams) are fed from here, never hand-computed.

Commands (python3 progress.py <cmd> -h for each):
  init           create state.json for a lane and (re)build the index
  set-domains    set the exam domains/weights (JSON list)
  add-card       add a spaced-repetition card (seeded as just-missed: due tomorrow)
  review         grade a card 0-5; applies SM-2 and reschedules
  due            list cards due today or earlier
  add-questions  append questions to the lane's bank (deduped by stem)
  sample-mock    pick N questions weighted by domain -> mock_exam spec (stdout)
  record-mock    record a mock result (pct + optional per-domain); updates mastery
  set-mastery    set a domain's mastery %
  readiness      GO / NOT YET against the threshold (stdout JSON)
  dashboard      emit a dashboard spec (stdout) for build_docs.py
  reindex        rebuild ~/learning-sprints/index.md from every lane

Determinism: pass --today YYYY-MM-DD anywhere a date is needed (defaults to the
real date); selection is first-fit, not random, so runs are reproducible.
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import sys


def _path(d):
    return os.path.join(d, "state.json")


def _load(d):
    with open(_path(d), encoding="utf-8") as fh:
        return json.load(fh)


def _save(d, s):
    with open(_path(d), "w", encoding="utf-8") as fh:
        json.dump(s, fh, indent=1, ensure_ascii=False)


def _today(args):
    return getattr(args, "today", None) or datetime.date.today().isoformat()


def _date_plus(iso, days):
    y, m, d = map(int, iso.split("-"))
    return (datetime.date(y, m, d) + datetime.timedelta(days=int(days))).isoformat()


def _norm(text):
    return re.sub(r"[^a-z0-9]+", " ", str(text).lower()).strip()


def _is_ready(s):
    qual = [m for m in s.get("mocks", []) if m.get("pct", 0) >= s.get("pass_pct", 80)]
    weak = [d for d in s.get("domains", []) if d.get("mastery", 0) < s.get("min_domain", 65)]
    return len(qual) >= s.get("streak_target", 3) and not weak, qual, weak


# ---- commands -------------------------------------------------------------

def cmd_init(args):
    os.makedirs(args.dir, exist_ok=True)
    s = {
        "slug": os.path.basename(args.dir.rstrip("/")),
        "topic": args.topic,
        "goal": args.goal or "",
        "type": args.type,
        "background": args.background or "",
        "exam_date": args.exam_date,
        "pass_pct": args.pass_pct,
        "streak_target": args.streak,
        "min_domain": args.min_domain,
        "time_limit_min": args.time_limit,
        "domains": [],
        "cards": [],
        "mocks": [],
        "bank": [],
        "weak_spots": [],
        "created": _today(args),
        "last_session": _today(args),
    }
    _save(args.dir, s)
    _reindex(os.path.dirname(os.path.abspath(args.dir.rstrip("/"))))
    print(f"initialized {_path(args.dir)}")


def cmd_set_domains(args):
    s = _load(args.dir)
    s["domains"] = json.loads(args.json)
    _save(args.dir, s)
    print(f"set {len(s['domains'])} domains")


def cmd_add_card(args):
    s = _load(args.dir)
    if any(c["id"] == args.id for c in s["cards"]):
        sys.exit(f"card {args.id} already exists")
    s["cards"].append({
        "id": args.id, "concept": args.concept, "domain": args.domain,
        "ease": 2.5, "interval_days": 1, "repetitions": 0,
        "due": _date_plus(_today(args), 1), "lapses": 1, "last_grade": 2,
    })
    _save(args.dir, s)
    print(f"added card {args.id} (due {_date_plus(_today(args), 1)})")


def cmd_review(args):
    s = _load(args.dir)
    today, q = _today(args), int(args.grade)
    for c in s["cards"]:
        if c["id"] != args.card_id:
            continue
        if q >= 3:
            n = c.get("repetitions", 0)
            c["interval_days"] = 1 if n == 0 else (6 if n == 1 else round(c["interval_days"] * c.get("ease", 2.5)))
            c["repetitions"] = n + 1
        else:
            c["repetitions"], c["interval_days"] = 0, 1
            c["lapses"] = c.get("lapses", 0) + 1
        ef = c.get("ease", 2.5) + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        c["ease"] = max(1.3, round(ef, 3))
        c["due"] = _date_plus(today, c["interval_days"])
        c["last_grade"], c["last_reviewed"] = q, today
        _save(args.dir, s)
        print(f"{c['id']}: ease {c['ease']}, interval {c['interval_days']}d, due {c['due']}")
        return
    sys.exit(f"no card {args.card_id}")


def cmd_due(args):
    s, t = _load(args.dir), _today(args)
    due = [c for c in s["cards"] if c.get("due", "9999") <= t]
    for c in due:
        print(f"{c['id']}  {c.get('concept', '')}  (due {c['due']}, lapses {c.get('lapses', 0)})")
    if not due:
        print("nothing due")


def cmd_add_questions(args):
    s = _load(args.dir)
    bank = s.setdefault("bank", [])
    seen = {q.get("_h") for q in bank}
    payload = json.load(open(args.file, encoding="utf-8"))
    items = payload["questions"] if isinstance(payload, dict) else payload
    added = 0
    for q in items:
        h = hashlib.sha1(_norm(q.get("stem", "")).encode()).hexdigest()[:12]
        if h in seen:
            continue
        q["_h"] = h
        q.setdefault("id", f"q-{h}")
        bank.append(q)
        seen.add(h)
        added += 1
    _save(args.dir, s)
    print(f"added {added} questions (bank now {len(bank)}, {len(items) - added} dupes skipped)")


def cmd_sample_mock(args):
    s = _load(args.dir)
    bank, n, domains = s.get("bank", []), args.n, s.get("domains", [])
    chosen = []
    if domains:
        tw = sum(d.get("weight", 0) for d in domains) or 1
        for d in domains:
            k = max(1, round(n * d.get("weight", 0) / tw))
            chosen += [q for q in bank if q.get("domain") == d["id"]][:k]
    else:
        chosen = bank[:n]
    chosen = chosen[:n]
    spec = {
        "type": "mock_exam",
        "title": f"{s.get('topic', 'Mock')} — Mock Exam",
        "subtitle": f"{len(chosen)} questions",
        "time_limit_min": s.get("time_limit_min", 130),
        "pass_pct": s.get("pass_pct", 80),
        "domains": {d["id"]: d["name"] for d in domains},
        "questions": [
            {"id": q.get("id"), "stem": q.get("stem"), "type": q.get("type", "single"),
             "choices": q.get("choices", []), "answer": q.get("answer"),
             "explanation": q.get("explanation", ""), "domain": q.get("domain", "")}
            for q in chosen
        ],
    }
    print(json.dumps(spec, indent=1, ensure_ascii=False))


def cmd_record_mock(args):
    s = _load(args.dir)
    m = {"date": _today(args), "pct": args.pct}
    if args.per_domain:
        m["per_domain"] = json.loads(args.per_domain)
        for d in s.get("domains", []):
            if d["id"] in m["per_domain"]:
                d["mastery"] = m["per_domain"][d["id"]]
    s.setdefault("mocks", []).append(m)
    s["last_session"] = _today(args)
    _save(args.dir, s)
    ready, qual, _ = _is_ready(s)
    print(f"recorded {args.pct}% ({len(s['mocks'])} mocks; {len(qual)}/{s.get('streak_target', 3)} qualifying; "
          f"{'GO' if ready else 'NOT YET'})")


def cmd_set_mastery(args):
    s = _load(args.dir)
    for d in s["domains"]:
        if d["id"] == args.domain:
            d["mastery"] = args.pct
            _save(args.dir, s)
            print(f"{args.domain} mastery = {args.pct}%")
            return
    sys.exit(f"no domain {args.domain}")


def cmd_readiness(args):
    s = _load(args.dir)
    ready, qual, weak = _is_ready(s)
    print(json.dumps({
        "verdict": "GO" if ready else "NOT YET",
        "qualifying_mocks": len(qual),
        "streak_target": s.get("streak_target", 3),
        "pass_pct": s.get("pass_pct", 80),
        "weak_domains": [d["name"] for d in weak],
    }, indent=1, ensure_ascii=False))


def cmd_dashboard(args):
    s, t = _load(args.dir), _today(args)
    spec = {
        "type": "dashboard",
        "title": s.get("topic", "Readiness"),
        "subtitle": "as of " + t,
        "pass_pct": s.get("pass_pct", 80),
        "streak_target": s.get("streak_target", 3),
        "min_domain": s.get("min_domain", 65),
        "exam_date": s.get("exam_date"),
        "cards_due": len([c for c in s.get("cards", []) if c.get("due", "9999") <= t]),
        "domains": [{"name": d["name"], "weight": d.get("weight", "?"), "mastery": d.get("mastery", 0)}
                    for d in s.get("domains", [])],
        "mocks": [{"date": m.get("date", ""), "pct": m.get("pct", 0)} for m in s.get("mocks", [])],
    }
    print(json.dumps(spec, indent=1, ensure_ascii=False))


def _reindex(root):
    if not root or not os.path.isdir(root):
        return
    lines = ["# Learning lanes", ""]
    for name in sorted(os.listdir(root)):
        sp = os.path.join(root, name, "state.json")
        if not os.path.isfile(sp):
            continue
        s = json.load(open(sp, encoding="utf-8"))
        ready, qual, _ = _is_ready(s)
        lines.append(
            f"- [{s.get('topic', name)}]({name}/progress.md) — "
            f"{'GO' if ready else 'NOT YET'} · {len(qual)}/{s.get('streak_target', 3)} mocks "
            f"≥{s.get('pass_pct', 80)}% · last {s.get('last_session', '?')}"
        )
    with open(os.path.join(root, "index.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def cmd_reindex(args):
    _reindex(args.root)
    print(f"reindexed {os.path.join(args.root, 'index.md')}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    def lane(sp):
        sp.add_argument("dir", help="lane directory (contains state.json)")
        sp.add_argument("--today", help="override date (YYYY-MM-DD) for determinism")

    sp = sub.add_parser("init"); lane(sp)
    sp.add_argument("--topic", required=True); sp.add_argument("--goal")
    sp.add_argument("--type", default="certification"); sp.add_argument("--background")
    sp.add_argument("--exam-date", dest="exam_date"); sp.add_argument("--pass-pct", dest="pass_pct", type=int, default=80)
    sp.add_argument("--streak", type=int, default=3); sp.add_argument("--min-domain", dest="min_domain", type=int, default=65)
    sp.add_argument("--time-limit", dest="time_limit", type=int, default=130)
    sp.set_defaults(fn=cmd_init)

    sp = sub.add_parser("set-domains"); lane(sp); sp.add_argument("json"); sp.set_defaults(fn=cmd_set_domains)
    sp = sub.add_parser("add-card"); lane(sp)
    sp.add_argument("--id", required=True); sp.add_argument("--concept", required=True); sp.add_argument("--domain", required=True)
    sp.set_defaults(fn=cmd_add_card)
    sp = sub.add_parser("review"); lane(sp); sp.add_argument("card_id"); sp.add_argument("grade"); sp.set_defaults(fn=cmd_review)
    sp = sub.add_parser("due"); lane(sp); sp.set_defaults(fn=cmd_due)
    sp = sub.add_parser("add-questions"); lane(sp); sp.add_argument("file"); sp.set_defaults(fn=cmd_add_questions)
    sp = sub.add_parser("sample-mock"); lane(sp); sp.add_argument("--n", type=int, default=65); sp.set_defaults(fn=cmd_sample_mock)
    sp = sub.add_parser("record-mock"); lane(sp)
    sp.add_argument("--pct", type=int, required=True); sp.add_argument("--per-domain", dest="per_domain")
    sp.set_defaults(fn=cmd_record_mock)
    sp = sub.add_parser("set-mastery"); lane(sp); sp.add_argument("domain"); sp.add_argument("pct", type=int); sp.set_defaults(fn=cmd_set_mastery)
    sp = sub.add_parser("readiness"); lane(sp); sp.set_defaults(fn=cmd_readiness)
    sp = sub.add_parser("dashboard"); lane(sp); sp.set_defaults(fn=cmd_dashboard)
    sp = sub.add_parser("reindex"); sp.add_argument("root"); sp.add_argument("--today"); sp.set_defaults(fn=cmd_reindex)

    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
