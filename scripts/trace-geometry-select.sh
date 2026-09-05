#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MAME_BIN="${VON_MAME_BIN:-$ROOT_DIR/bin/von}"
SECONDS_TO_RUN="${VON_GEOMETRY_SELECT_SECONDS:-40}"
CAPTURE_START_FRAME="${VON_PROGRESS_CAPTURE_START_FRAME:-0}"
COIN_FRAME="${VON_PROGRESS_COIN_FRAME:-900}"
START_FRAME="${VON_PROGRESS_START_FRAME:-1500}"
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
mame_status=0
SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-dummy}" \
VON_PROGRESS_SECONDS="$SECONDS_TO_RUN" \
VON_PROGRESS_LOG="$LUA_LOG" \
VON_PROGRESS_CAPTURE_START_FRAME="$CAPTURE_START_FRAME" \
VON_PROGRESS_COIN_FRAME="$COIN_FRAME" \
VON_PROGRESS_START_FRAME="$START_FRAME" \
    "$MAME_BIN" vonj \
    -rompath "$ROM_PATH" \
    -video none -sound none -oslog \
    -autoboot_script "$SCRIPT" \
    -seconds_to_run "$SECONDS_TO_RUN" -skip_gameinfo -nothrottle \
    >"$TRACE_LOG" 2>&1 || mame_status=$?

python3 "$ROOT_DIR/von/tools/summarize_mame_trace.py" "$TRACE_LOG"

objects=$(rg -c 'vonj_geometry_object:' "$TRACE_LOG" || echo 0)
matrices=$(rg -c 'vonj_geometry_matrix:' "$TRACE_LOG" || echo 0)
polygons=$(rg -c 'vonj_geometry_polygon:' "$TRACE_LOG" || echo 0)
printf 'Wrote %s\n' "$TRACE_LOG"
printf 'Wrote %s\n' "$LUA_LOG"
printf 'Geometry events: objects=%s matrices=%s polygons=%s\n' "$objects" "$matrices" "$polygons"

# Failure bundle: a nonzero emulator exit or an event-free trace gets a
# self-describing directory so the next failure needs no digging.
if [[ "$mame_status" -ne 0 || "$objects$matrices$polygons" == "000" ]]; then
    bundle="$OUT_DIR/bundle-geometry-select-${SECONDS_TO_RUN}s-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$bundle"
    {
        printf 'script: trace-geometry-select.sh\n'
        printf 'mame_exit: %s\n' "$mame_status"
        printf 'seconds_to_run: %s\n' "$SECONDS_TO_RUN"
        printf 'objects: %s\n' "$objects"
        printf 'matrices: %s\n' "$matrices"
        printf 'polygons: %s\n' "$polygons"
        printf 'trace_log: %s\n' "$TRACE_LOG"
        printf 'lua_log: %s\n' "$LUA_LOG"
    } >"$bundle/manifest.txt"
    tail -n 200 "$TRACE_LOG" >"$bundle/trace-tail.log" 2>/dev/null || true
    tail -n 100 "$LUA_LOG" >"$bundle/lua-tail.log" 2>/dev/null || true
    printf 'Failure bundle: %s\n' "$bundle"
    exit "$mame_status"
fi
