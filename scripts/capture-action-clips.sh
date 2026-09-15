#!/usr/bin/env bash
# Capture labelled fighter animation: a deterministic action schedule plus the
# geometry trace, so per-state clips can be segmented and baked.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MAME_BIN="${VON_MAME_BIN:-$ROOT_DIR/bin/von}"
SECONDS_TO_RUN="${VON_ACTION_SECONDS:-88}"
START_FRAME="${VON_ACTION_START_FRAME:-2120}"
CYCLES="${VON_ACTION_CYCLES:-2}"
ROM_PATH="$ROOT_DIR/von/build/disasm/rompath"
OUT_DIR="${VON_ACTION_OUT:-$ROOT_DIR/von/build/action-clips}"
SCRIPT="$ROOT_DIR/von/tools/action_schedule.lua"
TRACE_LOG="$OUT_DIR/action-twin-${SECONDS_TO_RUN}s.trace"
ACTION_LOG="$OUT_DIR/action-twin-${SECONDS_TO_RUN}s.actions.log"

[[ -x "$MAME_BIN" ]] || { printf 'error: MAME binary missing: %s\n' "$MAME_BIN" >&2; exit 1; }
[[ -d "$ROM_PATH/vonj" ]] || { printf 'error: ROM staging missing: %s\n' "$ROM_PATH/vonj" >&2; exit 1; }

mkdir -p "$OUT_DIR"
SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-dummy}" \
VON_ACTION_LOG="$ACTION_LOG" \
VON_ACTION_SECONDS="$SECONDS_TO_RUN" \
VON_ACTION_START_FRAME="$START_FRAME" \
VON_ACTION_CYCLES="$CYCLES" \
VON_FIFO_MAX="${VON_FIFO_MAX:-1}" \
VON_GEOMETRY_OBJECT_MAX="${VON_GEOMETRY_OBJECT_MAX:-2000000}" \
    "$MAME_BIN" vonj \
    -rompath "$ROM_PATH" \
    -video none -sound none -oslog \
    -autoboot_script "$SCRIPT" \
    -seconds_to_run "$SECONDS_TO_RUN" -skip_gameinfo -nothrottle \
    >"$TRACE_LOG" 2>&1 || true

objects=$(rg -c 'vonj_geometry_object:' "$TRACE_LOG" || echo 0)
matrices=$(rg -c 'vonj_geometry_matrix:' "$TRACE_LOG" || echo 0)
printf 'wrote %s\n' "$TRACE_LOG"
printf 'wrote %s\n' "$ACTION_LOG"
printf 'geometry: objects=%s matrices=%s\n' "$objects" "$matrices"
