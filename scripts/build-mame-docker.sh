#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="${VON_MAME_BUILD_IMAGE:-von-mame-build:ubuntu26.04}"
PATCH_SET="${VON_MAME_PATCH_SET:-core}"

command -v docker >/dev/null 2>&1 || { printf 'error: docker is required\n' >&2; exit 1; }
docker image inspect "$IMAGE" >/dev/null 2>&1 || { printf 'error: Docker image not found: %s\n' "$IMAGE" >&2; exit 1; }

docker run --rm \
    --user "$(id -u):$(id -g)" \
    -e "VON_MAME_PATCH_SET=$PATCH_SET" \
    -e "JOBS=${JOBS:-}" \
    -v "$ROOT_DIR:/src" \
    -w /src \
    "$IMAGE" \
    bash -lc '
set -euo pipefail
./scripts/prepare-mame.sh
cd third_party/mame-master
make REGENIE=1 TARGET=mame SUBTARGET=von \
    SOURCES=src/mame/sega/model2.cpp \
    USE_QTDEBUG=0 NO_USE_MIDI=1 NO_USE_PORTAUDIO=1 \
    NO_USE_PIPEWIRE=1 NO_USE_PULSEAUDIO=1 \
    -j"${JOBS:-$(nproc)}"
'
