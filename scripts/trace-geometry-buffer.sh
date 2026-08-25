#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MAME_BIN="$ROOT_DIR/third_party/mame-master/von"
TOOLBOX_NAME="${VON_TOOLBOX:-von-mame}"
ROM_PATH="$ROOT_DIR/von/build/disasm/rompath"
OUT_DIR="$ROOT_DIR/von/build/disasm"
SCRIPT="$ROOT_DIR/von/tools/trace_geometry_buffer.lua"
SECONDS_TO_RUN="${VON_GEOMETRY_SECONDS:-10}"
LOG_PATH="$OUT_DIR/vonj-geometry-buffer.log"
DUMP_PATH="$OUT_DIR/vonj-geometry-buffer.hex"
TRACE_PATH="$OUT_DIR/vonj-geometry-buffer.trace"

[[ -x "$MAME_BIN" ]] || { printf 'error: MAME binary is not built\n' >&2; exit 1; }
[[ -d "$ROM_PATH/vonj" ]] || { printf 'error: staged ROM path is missing\n' >&2; exit 1; }

rm -f "$LOG_PATH" "$DUMP_PATH".*
toolbox run --container "$TOOLBOX_NAME" env \
    VON_GEOMETRY_BUFFER_LOG="$LOG_PATH" \
    VON_GEOMETRY_BUFFER_DUMP="$DUMP_PATH" \
    "$MAME_BIN" vonj \
    -rompath "$ROM_PATH" \
    -video none -sound none -oslog \
    -autoboot_script "$SCRIPT" \
    -seconds_to_run "$SECONDS_TO_RUN" -skip_gameinfo -nothrottle \
    > "$TRACE_PATH" 2>&1

printf 'Wrote %s\n' "$LOG_PATH"
printf 'Wrote %s.N dumps\n' "$DUMP_PATH"
