#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_DIR="$ROOT_DIR/config"
source "$CONFIG_DIR/remote-build.env.example"
[[ -f "$CONFIG_DIR/remote-build.local.env" ]] && source "$CONFIG_DIR/remote-build.local.env"

REMOTE_HOST="${VON_REMOTE_HOST:-drone0}"
REMOTE_CHECKOUT="${VON_REMOTE_CHECKOUT:-/home/drone/von-arcade-decomp}"
IMAGE="ghcr.io/nkito/i960_sbc@sha256:c4baf40df8c6db1774e2bb87020824ca0d99201b11fb1944ef3a6d2922bd4b6c"

command -v ssh >/dev/null 2>&1 || { printf 'error: ssh is required\n' >&2; exit 1; }
command -v rsync >/dev/null 2>&1 || { printf 'error: rsync is required\n' >&2; exit 1; }

printf 'Synchronizing i960 C sources to %s...\n' "$REMOTE_HOST"
mkdir -p "$ROOT_DIR/von/build/i960"
python3 "$ROOT_DIR/von/tools/extract_maincpu.py" \
    --output "$ROOT_DIR/von/build/i960/vonj-original-maincpu.bin"
rsync -a --delete "$ROOT_DIR/von/i960/" "$REMOTE_HOST:$REMOTE_CHECKOUT/von/i960/"
rsync -a "$ROOT_DIR/scripts/i960-build-inner.sh" "$REMOTE_HOST:$REMOTE_CHECKOUT/scripts/i960-build-inner.sh"
rsync -a "$ROOT_DIR/von/tools/build_clean_i960_image.py" \
    "$REMOTE_HOST:$REMOTE_CHECKOUT/von/tools/build_clean_i960_image.py"
rsync -a "$ROOT_DIR/von/build/i960/vonj-original-maincpu.bin" \
    "$REMOTE_HOST:$REMOTE_CHECKOUT/von/build/i960/vonj-original-maincpu.bin"

printf 'Building i960 C images remotely in Docker...\n'
ssh "$REMOTE_HOST" "docker run --rm -v '$REMOTE_CHECKOUT:/src' -w /src/von/i960 --entrypoint /bin/bash '$IMAGE' /src/scripts/i960-build-inner.sh"

mkdir -p "$ROOT_DIR/von/build/i960" "$ROOT_DIR/von/build/rompath/reconstructed/vonjdev"
scp "$REMOTE_HOST:$REMOTE_CHECKOUT/von/build/i960/"'prototype.elf' "$ROOT_DIR/von/build/i960/prototype.elf"
scp "$REMOTE_HOST:$REMOTE_CHECKOUT/von/build/i960/"'prototype.bin' "$ROOT_DIR/von/build/i960/prototype.bin"
scp "$REMOTE_HOST:$REMOTE_CHECKOUT/von/build/i960/"'prototype-maincpu.bin' "$ROOT_DIR/von/build/i960/prototype-maincpu.bin"
scp "$REMOTE_HOST:$REMOTE_CHECKOUT/von/build/i960/"'prototype.lst' "$ROOT_DIR/von/build/i960/prototype.lst"
scp "$REMOTE_HOST:$REMOTE_CHECKOUT/von/build/i960/"'reconstructed.elf' "$ROOT_DIR/von/build/i960/reconstructed.elf"
scp "$REMOTE_HOST:$REMOTE_CHECKOUT/von/build/i960/"'reconstructed.bin' "$ROOT_DIR/von/build/i960/reconstructed.bin"
scp "$REMOTE_HOST:$REMOTE_CHECKOUT/von/build/i960/"'reconstructed.lst' "$ROOT_DIR/von/build/i960/reconstructed.lst"
scp "$REMOTE_HOST:$REMOTE_CHECKOUT/von/build/i960/"'reconstructed-maincpu.bin' "$ROOT_DIR/von/build/i960/reconstructed-maincpu.bin"
scp "$REMOTE_HOST:$REMOTE_CHECKOUT/von/build/i960/"'reconstructed_reset.elf' "$ROOT_DIR/von/build/i960/reconstructed_reset.elf"
scp "$REMOTE_HOST:$REMOTE_CHECKOUT/von/build/i960/"'reconstructed_reset.bin' "$ROOT_DIR/von/build/i960/reconstructed_reset.bin"
scp "$REMOTE_HOST:$REMOTE_CHECKOUT/von/build/i960/"'reconstructed_reset.lst' "$ROOT_DIR/von/build/i960/reconstructed_reset.lst"
rsync -a --delete "$REMOTE_HOST:$REMOTE_CHECKOUT/von/build/rompath/reconstructed/" "$ROOT_DIR/von/build/rompath/reconstructed/"
"$ROOT_DIR/scripts/package-i960-clean.sh"
printf 'Synchronized reconstructed i960 image\n'
