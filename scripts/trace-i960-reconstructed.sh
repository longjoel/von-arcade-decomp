#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
OUT_DIR="$ROOT_DIR/von/build/disasm"
TRACE_LOG="$OUT_DIR/vonj-reconstructed-boot.trace"
mkdir -p "$OUT_DIR"

SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-dummy}" \
    "$SCRIPT_DIR/run-i960-reconstructed.sh" \
    -video none -sound none -oslog \
    -seconds_to_run "${VON_TRACE_SECONDS:-1}" -skip_gameinfo \
    > "$TRACE_LOG" 2>&1

printf 'Wrote %s\n' "$TRACE_LOG"
