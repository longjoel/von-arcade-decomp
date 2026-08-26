#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MAME_BIN="$ROOT_DIR/third_party/mame-master/von"
TOOLBOX_NAME="${VON_TOOLBOX:-von-mame}"
SECONDS_TO_RUN="${VON_TRACE_SECONDS:-5}"
ROM_PATH="$ROOT_DIR/von/build/disasm/rompath"
OUT_DIR="$ROOT_DIR/von/build/disasm"
TRACE_LOG="$OUT_DIR/vonj-toolbox-${SECONDS_TO_RUN}s.trace"

[[ -x "$MAME_BIN" ]] || {
    printf 'error: MAME binary is not built: %s\n' "$MAME_BIN" >&2
    exit 1
}
[[ -d "$ROM_PATH/vonj" ]] || {
    printf 'error: staged ROM path is missing: %s\n' "$ROM_PATH/vonj" >&2
    exit 1
}

mkdir -p "$OUT_DIR"
toolbox run --container "$TOOLBOX_NAME" "$MAME_BIN" vonj \
    -rompath "$ROM_PATH" \
    -video none -sound none -oslog \
    -seconds_to_run "$SECONDS_TO_RUN" -skip_gameinfo -nothrottle \
    >"$TRACE_LOG" 2>&1

printf 'Wrote %s\n' "$TRACE_LOG"
