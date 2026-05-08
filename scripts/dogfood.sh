#!/usr/bin/env bash
# Exercises pydoc_fork against itself and checks the output is sane.
set -euo pipefail

PASS=0
FAIL=0
OUT_DIR="$(mktemp -d)"
trap 'rm -rf "$OUT_DIR"' EXIT

check() {
    local desc="$1"; shift
    if "$@" > /dev/null 2>&1; then
        echo "  PASS: $desc"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $desc  (cmd: $*)"
        FAIL=$((FAIL + 1))
    fi
}

check_file() {
    local desc="$1"
    local path="$2"
    if [ -f "$path" ]; then
        echo "  PASS: $desc"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $desc  (missing: $path)"
        FAIL=$((FAIL + 1))
    fi
}

check_not_file() {
    local desc="$1"
    local path="$2"
    if [ ! -f "$path" ]; then
        echo "  PASS: $desc"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $desc  (should not exist: $path)"
        FAIL=$((FAIL + 1))
    fi
}

check_nonempty() {
    local desc="$1"
    local path="$2"
    if [ -s "$path" ]; then
        echo "  PASS: $desc"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $desc  (empty or missing: $path)"
        FAIL=$((FAIL + 1))
    fi
}

check_contains() {
    local desc="$1"
    local path="$2"
    local needle="$3"
    if grep -q "$needle" "$path" 2>/dev/null; then
        echo "  PASS: $desc"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $desc  (needle '$needle' not found in $path)"
        FAIL=$((FAIL + 1))
    fi
}

echo "=== pydoc_fork dogfood tests ==="
echo "Output dir: $OUT_DIR"
echo ""

# --- Run against the package itself ---
echo "--- generate: pydoc_fork (classic theme) ---"
check "pydoc_fork exits 0 on pydoc_fork package" \
    python -m pydoc_fork pydoc_fork --output "$OUT_DIR/classic" --theme classic --project_name "Dogfood Test"

check_file  "index.html written"              "$OUT_DIR/classic/index.html"
check_file  "style.css written"               "$OUT_DIR/classic/style.css"
check_file  "pydoc_fork.html written"         "$OUT_DIR/classic/pydoc_fork.html"
check_nonempty "index.html is non-empty"      "$OUT_DIR/classic/index.html"
check_nonempty "pydoc_fork.html is non-empty" "$OUT_DIR/classic/pydoc_fork.html"
check_contains "index.html contains pydoc_fork link" "$OUT_DIR/classic/index.html" "pydoc_fork"
check_not_file "no degenerate ..html produced" "$OUT_DIR/classic/..html"

echo ""
echo "--- generate: dot shorthand (.) ---"
check "pydoc_fork exits 0 on dot shorthand" \
    python -m pydoc_fork . --output "$OUT_DIR/dot" --theme classic --project_name "Dot Test"

check_file "index.html written for dot run"   "$OUT_DIR/dot/index.html"
check_not_file "no ..html for dot run"        "$OUT_DIR/dot/..html"

echo ""
echo "--- generate: dark theme ---"
check "pydoc_fork exits 0 on dark theme" \
    python -m pydoc_fork pydoc_fork --output "$OUT_DIR/dark" --theme dark

check_file "index.html written (dark)"        "$OUT_DIR/dark/index.html"

echo ""
echo "--- generate: --no_index flag ---"
check "pydoc_fork exits 0 with --no_index" \
    python -m pydoc_fork pydoc_fork --output "$OUT_DIR/noindex" --no_index

check_not_file "no index.html with --no_index" "$OUT_DIR/noindex/index.html"

echo ""
if [ "$FAIL" -eq 0 ]; then
    echo "All $PASS checks passed."
else
    echo "$PASS passed, $FAIL failed."
    exit 1
fi
