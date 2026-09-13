#!/usr/bin/env bash
# Capture a geometry trace while driving a turn/move pattern, so the recovered
# view matrix can be sampled against known player motion.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MAME_BIN="${VON_MAME_BIN:-$ROOT_DIR/bin/von}"
ROM_PATH="$ROOT_DIR/von/build/disasm/rompath"
OUT_DIR="${VON_CAMERA_DIR:-$ROOT_DIR/von/build/disasm}"
SECONDS="${VON_CAMERA_SECONDS:-70}"
ORDINAL="${VON_CAMERA_ORDINAL:-1}"
TRACE="$OUT_DIR/vonj-camera-${ORDINAL}-${SECONDS}s.trace"
LUA_LOG="$OUT_DIR/vonj-camera-${ORDINAL}-${SECONDS}s.lua.log"

[[ -x "$MAME_BIN" ]] || { printf 'error: no MAME binary: %s\n' "$MAME_BIN" >&2; exit 1; }
[[ -d "$ROM_PATH/vonj" ]] || { printf 'error: no rompath: %s\n' "$ROM_PATH" >&2; exit 1; }
mkdir -p "$OUT_DIR"

SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-dummy}" \
VON_CAMERA_LOG="$LUA_LOG" \
VON_CAMERA_ORDINAL="$ORDINAL" \
VON_CAMERA_SECONDS="$SECONDS" \
    "$MAME_BIN" vonj \
    -rompath "$ROM_PATH" \
    -video none -sound none -oslog \
    -autoboot_script "$ROOT_DIR/von/tools/probe_camera.lua" \
    -seconds_to_run "$((SECONDS + 10))" -skip_gameinfo -nothrottle \
    >"$TRACE" 2>&1 || true

objects=$(grep -c 'vonj_geometry_object:' "$TRACE" || true)
matrices=$(grep -c 'vonj_geometry_matrix:' "$TRACE" || true)
printf 'wrote %s (objects=%s matrices=%s)\n' "$TRACE" "$objects" "$matrices"
