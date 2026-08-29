#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_DIR="$ROOT_DIR/config"
source "$CONFIG_DIR/remote-build.env.example"
[[ -f "$CONFIG_DIR/remote-build.local.env" ]] && source "$CONFIG_DIR/remote-build.local.env"

REMOTE_HOST="${VON_REMOTE_HOST:-drone0}"
REMOTE_CHECKOUT="${VON_REMOTE_CHECKOUT:-/home/drone/von-arcade-decomp}"
IMAGE="ghcr.io/nkito/i960_sbc@sha256:c4baf40df8c6db1774e2bb87020824ca0d99201b11fb1944ef3a6d2922bd4b6c"
OUT_DIR="$ROOT_DIR/von/build/disasm"

command -v ssh >/dev/null 2>&1 || { printf 'error: ssh is required\n' >&2; exit 1; }
command -v rsync >/dev/null 2>&1 || { printf 'error: rsync is required\n' >&2; exit 1; }

mkdir -p "$OUT_DIR"
python3 "$ROOT_DIR/von/tools/extract_maincpu.py" \
    --output "$OUT_DIR/vonj-maincpu.bin"
ssh "$REMOTE_HOST" "mkdir -p '$REMOTE_CHECKOUT/von/build/disasm'"
rsync -a "$OUT_DIR/vonj-maincpu.bin" \
    "$REMOTE_HOST:$REMOTE_CHECKOUT/von/build/disasm/vonj-maincpu.bin"

ssh "$REMOTE_HOST" "docker run --rm -v '$REMOTE_CHECKOUT:/src' -w /src/von/build/disasm --entrypoint /bin/bash '$IMAGE' -lc 'i960-elf-objdump -m i960 -b binary --adjust-vma=0 -D vonj-maincpu.bin > vonj-maincpu.lst'"
rsync -a "$REMOTE_HOST:$REMOTE_CHECKOUT/von/build/disasm/vonj-maincpu.lst" \
    "$OUT_DIR/vonj-maincpu.lst"
printf 'Wrote %s\n' "$OUT_DIR/vonj-maincpu.lst"
