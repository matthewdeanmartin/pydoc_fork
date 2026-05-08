#!/usr/bin/env bash
set -euo pipefail

PASS=0
FAIL=0

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

check_fails() {
    local desc="$1"; shift
    if ! "$@" > /dev/null 2>&1; then
        echo "  PASS (expected failure): $desc"
        PASS=$((PASS + 1))
    else
        echo "  FAIL (expected failure but succeeded): $desc  (cmd: $*)"
        FAIL=$((FAIL + 1))
    fi
}

echo "=== pydoc_fork smoke tests ==="
check "--help exits 0"   pydoc_fork --help
check "--version exits 0" pydoc_fork --version

echo ""
if [ "$FAIL" -eq 0 ]; then
    echo "All $PASS checks passed."
else
    echo "$PASS passed, $FAIL failed."
    exit 1
fi
