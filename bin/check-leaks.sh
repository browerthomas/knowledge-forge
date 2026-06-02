#!/usr/bin/env bash
# Fail if tracked files contain secrets or personal data. Patterns in
# .github/leak-patterns.txt (one extended-regex per line, '#' comments ignored).
set -euo pipefail
cd "$(dirname "$0")/.."
PATTERNS=".github/leak-patterns.txt"
[ -f "$PATTERNS" ] || { echo "no $PATTERNS"; exit 0; }

hits=0
# Scan git-tracked files only (skip the patterns file itself).
files="$(git ls-files | grep -v "^${PATTERNS}$" || true)"
while IFS= read -r pat; do
  [ -z "$pat" ] && continue
  case "$pat" in \#*) continue;; esac
  while IFS= read -r f; do
    [ -z "$f" ] && continue
    if grep -nIE "$pat" "$f" >/dev/null 2>&1; then
      echo "LEAK: pattern /$pat/ in $f"
      grep -nIE "$pat" "$f" | sed 's/^/   /'
      hits=$((hits+1))
    fi
  done <<< "$files"
done < "$PATTERNS"

if [ "$hits" -gt 0 ]; then
  echo "FAILED: $hits leak pattern hit(s)."
  exit 1
fi
echo "No leaks found."
