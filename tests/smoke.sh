#!/usr/bin/env bash
# Smoke test: manifests valid, scripts compile + run, generators produce output,
# mock JS parses, progress.py state round-trips. Runs in CI and locally.
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$(pwd)"
SK="$ROOT/plugins/learning-sprint/skills/learning-sprint"
SCRIPTS="$SK/scripts"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
fail() { echo "FAIL: $*" >&2; exit 1; }

echo "1. JSON manifests valid"
python3 -c "import json; json.load(open('.claude-plugin/marketplace.json')); json.load(open('plugins/learning-sprint/.claude-plugin/plugin.json'))" \
  || fail "manifest JSON invalid"

echo "2. version fields match across manifests"
python3 - <<'PY' || fail "version mismatch between manifests"
import json
m = json.load(open('.claude-plugin/marketplace.json'))['plugins'][0]['version']
p = json.load(open('plugins/learning-sprint/.claude-plugin/plugin.json'))['version']
assert m == p, f"{m} != {p}"
PY

echo "3. SKILL.md frontmatter has name + description"
python3 - <<'PY' || fail "SKILL.md frontmatter problem"
import re
t = open('plugins/learning-sprint/skills/learning-sprint/SKILL.md').read()
fm = re.match(r'^---\n(.*?)\n---', t, re.S)
assert fm, "no frontmatter"
body = fm.group(1)
assert re.search(r'^name:\s*learning-sprint', body, re.M), "name missing/wrong"
assert re.search(r'^description:\s*\S', body, re.M), "description missing"
PY

echo "4. python scripts compile"
python3 -m py_compile "$SCRIPTS"/*.py || fail "py_compile failed"

echo "5. build_docs.py renders every type"
for kind in study_guide practice_exam chapter board dashboard mock_exam; do
  case $kind in
    study_guide)   echo '{"type":"study_guide","title":"T","sections":[{"heading":"H","body_html":"<p>x</p>","keypoints":["k"]}]}' > "$TMP/s.json"; spec="$TMP/s.json";;
    practice_exam) echo '{"type":"practice_exam","title":"T","questions":[{"stem":"q","type":"mc","choices":["a","b"],"answer":"A","explanation":"e"}]}' > "$TMP/s.json"; spec="$TMP/s.json";;
    chapter)       echo '{"type":"chapter","title":"T","sections":[{"heading":"H","body_html":"<p>x</p>","example":{"body_html":"<p>e</p>"},"keypoints":["k"]}],"check":[{"q":"q","a":"a"}]}' > "$TMP/s.json"; spec="$TMP/s.json";;
    board)         echo '{"type":"board","title":"T","mermaid":"graph LR; A-->B","caption":"c"}' > "$TMP/s.json"; spec="$TMP/s.json";;
    dashboard)     echo '{"type":"dashboard","title":"T","domains":[{"name":"D","weight":50,"mastery":40}],"mocks":[{"date":"x","pct":81}]}' > "$TMP/s.json"; spec="$TMP/s.json";;
    mock_exam)     echo '{"type":"mock_exam","title":"T","time_limit_min":5,"pass_pct":72,"domains":{"d1":"D"},"questions":[{"stem":"q","type":"single","choices":["a","b"],"answer":"A","explanation":"e","domain":"d1"}]}' > "$TMP/s.json"; spec="$TMP/s.json";;
  esac
  python3 "$SCRIPTS/build_docs.py" "$spec" "$TMP/out_$kind" >/dev/null
  test -f "$TMP/out_$kind.html" || fail "build_docs $kind produced no html"
done

echo "6. mock JS parses (if node available)"
if command -v node >/dev/null; then
  python3 -c "import re,sys; sys.stdout.write(re.search(r'<script>(.*)</script>', open('$TMP/out_mock_exam.html').read(), re.S).group(1))" > "$TMP/mock.js"
  node --check "$TMP/mock.js" || fail "mock JS syntax error"
else
  echo "   (node not found — skipped)"
fi

echo "7. anki_export.py writes a TSV"
echo '{"deck":"D","cert_slug":"t","cards":[{"id":"c1","type":"basic","front":"f","back":"b","domain":"d1"}]}' > "$TMP/cards.json"
python3 "$SCRIPTS/anki_export.py" "$TMP/cards.json" "$TMP/cards" >/dev/null
test -f "$TMP/cards.tsv" || fail "anki_export produced no tsv"
head -1 "$TMP/cards.tsv" | grep -q '#separator:Tab' || fail "tsv missing directive"

echo "8. progress.py state round-trips (init -> card -> review -> mock -> readiness -> dashboard -> reindex)"
mkdir -p "$TMP/lanes/demo"
P() { python3 "$SCRIPTS/progress.py" "$@"; }
P init "$TMP/lanes/demo" --today 2026-06-02 --topic "Demo" --pass-pct 80 --streak 3 --min-domain 65 >/dev/null
P set-domains "$TMP/lanes/demo" '[{"id":"d1","name":"D1","weight":100,"mastery":90}]' >/dev/null
P add-card "$TMP/lanes/demo" --today 2026-06-02 --id c1 --concept "x" --domain d1 >/dev/null
P review "$TMP/lanes/demo" c1 4 --today 2026-06-03 | grep -q 'due 2026-06-04' || fail "SM-2 first-success interval wrong"
P record-mock "$TMP/lanes/demo" --pct 85 --today 2026-06-05 >/dev/null
P record-mock "$TMP/lanes/demo" --pct 88 --today 2026-06-07 >/dev/null
P record-mock "$TMP/lanes/demo" --pct 90 --today 2026-06-09 >/dev/null
P readiness "$TMP/lanes/demo" | grep -q '"verdict": "GO"' || fail "readiness should be GO (3 mocks >=80, domain 90)"
P dashboard "$TMP/lanes/demo" --today 2026-06-09 | python3 -c "import json,sys; json.load(sys.stdin)" || fail "dashboard spec not valid JSON"
P reindex "$TMP/lanes" --today 2026-06-09 >/dev/null
grep -q 'GO' "$TMP/lanes/index.md" || fail "index missing GO lane"

echo "ALL SMOKE TESTS PASSED"
