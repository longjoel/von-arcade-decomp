#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="ghcr.io/nkito/i960_sbc@sha256:c4baf40df8c6db1774e2bb87020824ca0d99201b11fb1944ef3a6d2922bd4b6c"
OUT_DIR="$ROOT_DIR/von/build/disasm"
ROM_IMAGE="$OUT_DIR/vonj-maincpu.bin"

command -v docker >/dev/null 2>&1 || {
    printf 'error: docker is required\n' >&2
    exit 1
}

python3 "$ROOT_DIR/von/tools/extract_maincpu.py" \
    --output "$ROM_IMAGE"

docker run --rm \
    -v "$ROOT_DIR:/src" \
    -w /src/von/build/disasm \
    --entrypoint /bin/bash \
    "$IMAGE" \
    -lc 'i960-elf-objdump -m i960 -b binary --adjust-vma=0 -D vonj-maincpu.bin > vonj-maincpu.lst'

printf 'Wrote %s\n' "$OUT_DIR/vonj-maincpu.lst"
