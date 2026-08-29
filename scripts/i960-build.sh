#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="ghcr.io/nkito/i960_sbc@sha256:c4baf40df8c6db1774e2bb87020824ca0d99201b11fb1944ef3a6d2922bd4b6c"

command -v docker >/dev/null 2>&1 || {
    printf 'error: docker is required\n' >&2
    exit 1
}

mkdir -p "$ROOT_DIR/von/build/i960"
python3 "$ROOT_DIR/von/tools/extract_maincpu.py" \
    --output "$ROOT_DIR/von/build/i960/vonj-original-maincpu.bin"

docker run --rm \
    -v "$ROOT_DIR:/src" \
    -w /src/von/i960 \
    --entrypoint /bin/bash \
    "$IMAGE" \
    /src/scripts/i960-build-inner.sh
