#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$ROOT_DIR/von/build/disasm"
MAINCPU_IMAGE="$OUT_DIR/vonj-maincpu.bin"
SHARC_IMAGE="$OUT_DIR/vonj-sharc-bootstrap.bin"
SHARC_LISTING="$OUT_DIR/vonj-sharc-bootstrap.lst"
UNIDASM="${VON_UNIDASM:-$ROOT_DIR/third_party/mame-master/unidasm}"

command -v python3 >/dev/null 2>&1 || {
    printf 'error: python3 is required\n' >&2
    exit 1
}
[[ -x "$UNIDASM" ]] || {
    printf 'error: unidasm is not built; set VON_UNIDASM or build MAME tools\n' >&2
    exit 1
}

python3 "$ROOT_DIR/von/tools/extract_maincpu.py" --output "$MAINCPU_IMAGE"
python3 "$ROOT_DIR/von/tools/extract_sharc_bootstrap.py" \
    --input "$MAINCPU_IMAGE" --output "$SHARC_IMAGE"

"$UNIDASM" "$SHARC_IMAGE" -arch sharc -basepc 0 -count 2760 > "$SHARC_LISTING"
printf 'Wrote %s\n' "$SHARC_LISTING"
