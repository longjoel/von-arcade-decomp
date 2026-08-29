#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MAME_BIN="${VON_MAME_BIN:-$ROOT_DIR/bin/von}"
SECONDS_TO_RUN="${VON_GEOMETRY_SELECT_SECONDS:-40}"
ROM_PATH="$ROOT_DIR/von/build/disasm/rompath"
OUT_DIR="$ROOT_DIR/von/build/disasm"
SCRIPT="$ROOT_DIR/von/tools/gameplay_progress.lua"
TRACE_LOG="$OUT_DIR/vonj-geometry-select-${SECONDS_TO_RUN}s.trace"
LUA_LOG="$OUT_DIR/vonj-geometry-select-${SECONDS_TO_RUN}s.lua.log"

[[ -x "$MAME_BIN" ]] || {
    printf 'error: MAME binary is not built: %s\n' "$MAME_BIN" >&2
    exit 1
}
[[ -d "$ROM_PATH/vonj" ]] || {
    printf 'error: staged ROM path is missing: %s\n' "$ROM_PATH/vonj" >&2
    exit 1
}

mkdir -p "$OUT_DIR"
SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-dummy}" \
VON_PROGRESS_SECONDS="$SECONDS_TO_RUN" \
VON_PROGRESS_LOG="$LUA_LOG" \
    "$MAME_BIN" vonj \
    -rompath "$ROM_PATH" \
    -video none -sound none -oslog \
    -autoboot_script "$SCRIPT" \
    -seconds_to_run "$SECONDS_TO_RUN" -skip_gameinfo -nothrottle \
    >"$TRACE_LOG" 2>&1

objects=$(rg -c 'vonj_geometry_object:' "$TRACE_LOG" || echo 0)
matrices=$(rg -c 'vonj_geometry_matrix:' "$TRACE_LOG" || echo 0)
polygons=$(rg -c 'vonj_geometry_polygon:' "$TRACE_LOG" || echo 0)
printf 'Wrote %s\n' "$TRACE_LOG"
printf 'Wrote %s\n' "$LUA_LOG"
printf 'Geometry events: objects=%s matrices=%s polygons=%s\n' "$objects" "$matrices" "$polygons"
