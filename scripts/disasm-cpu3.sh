#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$ROOT_DIR/von/build/disasm"
IMAGE="$OUT_DIR/vonj-cpu3.bin"
LISTING="$OUT_DIR/vonj-cpu3.lst"
UNIDASM="${VON_UNIDASM:-$ROOT_DIR/third_party/mame-master/unidasm}"

command -v python3 >/dev/null 2>&1 || {
    printf 'error: python3 is required\n' >&2
    exit 1
}
[[ -x "$UNIDASM" ]] || {
    printf 'error: unidasm is not built; set VON_UNIDASM or build MAME tools\n' >&2
    exit 1
}

python3 "$ROOT_DIR/von/tools/extract_cpu3.py" --output "$IMAGE"
"$UNIDASM" "$IMAGE" -arch z80 -basepc 0 > "$LISTING"
printf 'Wrote %s\n' "$LISTING"
