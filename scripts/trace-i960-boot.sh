#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"
require_mame

OUT_DIR="$ROOT_DIR/von/build/disasm"
TRACE_LOG="$OUT_DIR/vonj-boot.trace"
ERROR_LOG="$OUT_DIR/error.log"
ROM_PATH="$OUT_DIR/rompath"
mkdir -p "$OUT_DIR"
mkdir -p "$ROM_PATH/vonj"
for rom in "$ROM_DIR"/*; do
    ln -sfn "$rom" "$ROM_PATH/vonj/$(basename "$rom")"
done
RUNTIME_PATH="$(brew_runtime_path)${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

pushd "$OUT_DIR" >/dev/null
LD_LIBRARY_PATH="$RUNTIME_PATH" \
    "$MAME_BIN" vonj \
        -rompath "$ROM_PATH" \
        -video none \
        -sound none \
        -oslog \
        -seconds_to_run "${VON_TRACE_SECONDS:-1}" \
        -skip_gameinfo \
        > "$TRACE_LOG" 2>&1
popd >/dev/null

if [[ -f "$ERROR_LOG" ]]; then
    cp "$ERROR_LOG" "$TRACE_LOG"
fi

printf 'Wrote %s\n' "$TRACE_LOG"
