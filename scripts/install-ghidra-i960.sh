#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GHIDRA_HOME="${GHIDRA_HOME:-$ROOT_DIR/../voff/ghidra/ghidra_11.3.1_PUBLIC}"
TARGET="$GHIDRA_HOME/Ghidra/Processors/i960"
REF="727ef7872c5b1cd6ceb5a81f5e474d1ced92945c"
WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT

[[ -d "$GHIDRA_HOME/Ghidra/Processors" ]] || {
    printf 'error: invalid Ghidra installation: %s\n' "$GHIDRA_HOME" >&2
    exit 1
}

git clone --quiet https://github.com/mumbel/ghidra_i960.git "$WORK_DIR/i960"
git -C "$WORK_DIR/i960" checkout --quiet "$REF"
mkdir -p "$TARGET"
cp -a "$WORK_DIR/i960/data" "$TARGET/"
patch -d "$TARGET" -p1 < "$ROOT_DIR/von/ghidra/i960-bal-call.patch" >/dev/null

printf 'Installed i960 Ghidra module at %s\n' "$TARGET"
printf 'Source revision: %s\n' "$REF"
