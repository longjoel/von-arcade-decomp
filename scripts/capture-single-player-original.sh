#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"
require_mame

ROM_PATH="$ROOT_DIR/von/build/disasm/rompath"
LUA_SCRIPT="$ROOT_DIR/von/tools/capture_single_player.lua"
FINALIZER="$ROOT_DIR/von/tools/finalize_single_player_capture.py"
SELECTOR_COUNT="${VON_CAPTURE_SELECTOR_COUNT:-8}"
SELECTOR_START="${VON_CAPTURE_SELECTOR_START:-0}"
OUT_ROOT="${VON_CAPTURE_OUTPUT_ROOT:-$ROOT_DIR/von/captures}"
ENABLE_PC_TRACE="${VON_CAPTURE_ENABLE_PC_TRACE:-0}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_ROOT="$OUT_ROOT/single-player-$STAMP"

[[ "$SELECTOR_COUNT" =~ ^[1-9][0-9]*$ ]] || die "VON_CAPTURE_SELECTOR_COUNT must be positive"
[[ "$SELECTOR_START" =~ ^[0-9]+$ ]] || die "VON_CAPTURE_SELECTOR_START must be nonnegative"
[[ "$ENABLE_PC_TRACE" == 0 || "$ENABLE_PC_TRACE" == 1 ]] || die "VON_CAPTURE_ENABLE_PC_TRACE must be 0 or 1"
[[ -d "$ROM_PATH/vonj" ]] || die "original-ROM staging is missing: $ROM_PATH/vonj"
mkdir -p "$RUN_ROOT"

for ((selector = SELECTOR_START; selector < SELECTOR_START + SELECTOR_COUNT; ++selector)); do
    RUN_DIR="$RUN_ROOT/mech-$(printf '%02d' "$selector")"
    mkdir -p "$RUN_DIR/snap"
    printf 'Capturing selector %d into %s\n' "$selector" "$RUN_DIR"
    MAME_DEBUG_ARGS=()
    if [[ "$ENABLE_PC_TRACE" == 1 ]]; then
        MAME_DEBUG_ARGS=(-debug -debugger none)
    fi
    SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-dummy}" env $(runtime_env) \
        VON_CAPTURE_DIR="$RUN_DIR" \
        VON_CAPTURE_SELECT_STEPS="$selector" \
        "$MAME_BIN" vonj -rompath "$ROM_PATH" \
        -cfg_directory "$RUN_DIR/cfg" -nvram_directory "$RUN_DIR/nvram" \
        -input_directory "$RUN_DIR/inp" -snapshot_directory "$RUN_DIR/snap" \
        -video none -sound none -oslog -nothrottle -skip_gameinfo "${MAME_DEBUG_ARGS[@]}" \
        -autoboot_script "$LUA_SCRIPT" >"$RUN_DIR/mame.log" 2>&1
    if [[ "${VON_CAPTURE_QUEUE_TRACE:-0}" != 1 ]]; then
        python3 "$FINALIZER" --capture-dir "$RUN_DIR" --selector-steps "$selector" \
            --mame "$MAME_BIN" --rom "$ROM_PATH/vonj/epr-18664b.15"
    fi
done

printf 'Single-player original-ROM capture matrix: %s\n' "$RUN_ROOT"
