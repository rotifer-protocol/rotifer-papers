#!/usr/bin/env bash
# verify-spec-refs.sh
#
# Publication gate for rotifer-papers — refuse to push when a paper's
# §X.Y reference targets a section not present in the public Rotifer
# Protocol Specification.
#
# Spec: ADR-270 (rotifer-papers tiering & publication gate).
# Source of truth for PUBLIC_SECTIONS:
#   rotifer-spec/rotifer-protocol-specification.md
# Whenever the public spec adds or renumbers sections, update the
# whitelist below in the same commit (see ADR-270 §D4).
#
# Usage:
#   ./scripts/verify-spec-refs.sh                   # check all *.md in repo root
#   ./scripts/verify-spec-refs.sh paper-a.md ...    # check explicit files
#
# Escape hatch (per-line):
#   <!-- spec-ref-allow: REASON -->   on the same line as the §X.Y
#
# Escape hatch (whole run, emergency only):
#   ROTIFER_SKIP_SPEC_REFS=1 git push
#
# Exit codes:
#   0 — all references valid (or no §X.Y references found)
#   1 — at least one invalid reference

set -uo pipefail

if [ "${ROTIFER_SKIP_SPEC_REFS:-0}" = "1" ]; then
  echo "⚠️  spec-refs check skipped via ROTIFER_SKIP_SPEC_REFS=1"
  exit 0
fi

# Whitelist must mirror rotifer-spec/rotifer-protocol-specification.md
# Format: space-separated tokens, each prefixed with §
PUBLIC_SECTIONS="§1 §1.1 §1.2 §1.3 §1.4 §2 §3 §4 §5 §6"

# Resolve scope: explicit args, or all *.md in invocation dir.
if [ "$#" -gt 0 ]; then
  FILES=("$@")
else
  REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
  cd "$REPO_ROOT" || exit 0
  FILES=()
  for f in *.md; do
    [ -f "$f" ] || continue
    case "$f" in
      README.md|LICENSE*) continue ;;
    esac
    FILES+=("$f")
  done
fi

if [ "${#FILES[@]}" -eq 0 ]; then
  echo "✅ no .md files in scope; nothing to verify"
  exit 0
fi

errors=0
checked=0

# Token check helper — returns 0 if token is in PUBLIC_SECTIONS.
in_whitelist() {
  case " $PUBLIC_SECTIONS " in
    *" $1 "*) return 0 ;;
    *)        return 1 ;;
  esac
}

for f in "${FILES[@]}"; do
  if [ ! -f "$f" ]; then
    echo "  (skipping non-file: $f)"
    continue
  fi
  checked=$((checked + 1))

  # Step 1: lines that mention [Ss]pecification AND a §-reference
  # are candidates for spec-ref verification. Lines without this
  # combination are treated as paper self-references.
  while IFS= read -r raw; do
    line_num="${raw%%:*}"
    line_body="${raw#*:}"

    # Step 2: per-line escape hatch — skip whole line.
    if printf '%s' "$line_body" | grep -qE '<!--[[:space:]]*spec-ref-allow[[:space:]]*:'; then
      continue
    fi

    # Step 3: extract every §-reference on this line and check.
    while IFS= read -r ref; do
      [ -z "$ref" ] && continue
      if ! in_whitelist "$ref"; then
        printf "  ❌ %s:%s — \"%s\" is not in the public spec\n" \
               "$f" "$line_num" "$ref"
        errors=$((errors + 1))
      fi
    done < <(printf '%s' "$line_body" | grep -oE '§[0-9]+(\.[0-9]+)?')

  done < <(grep -nE '[Ss]pecification.*§[0-9]+|§[0-9]+.*[Ss]pecification' "$f" 2>/dev/null)
done

echo ""
if [ "$errors" -gt 0 ]; then
  echo "╔══════════════════════════════════════════════════════════════╗"
  echo "║  ⛔ PUSH BLOCKED — invalid spec §X.Y reference(s)           ║"
  echo "║  ADR-270: public papers must cite only sections that exist ║"
  echo "║  in the published rotifer-spec executive summary.          ║"
  echo "╚══════════════════════════════════════════════════════════════╝"
  echo ""
  echo "Public spec sections currently published:"
  echo "  $PUBLIC_SECTIONS"
  echo ""
  echo "Fixes:"
  echo "  1. Change the reference to a published section, or"
  echo "  2. Remove it (the surviving sentence may not need a number), or"
  echo "  3. Add an inline escape on the same line:"
  echo "       <!-- spec-ref-allow: REASON -->"
  echo "     (only for true edge cases — be specific in REASON;"
  echo "      git blame can audit the choice later)"
  echo ""
  echo "If the reference IS valid because the public spec was just"
  echo "extended, update PUBLIC_SECTIONS in this script in the same"
  echo "commit that updates rotifer-spec — see ADR-270 §D4."
  exit 1
fi

echo "✅ spec-refs check passed ($checked file(s) inspected, 0 errors)"
exit 0
