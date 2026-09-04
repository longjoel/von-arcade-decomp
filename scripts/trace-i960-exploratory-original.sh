#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"
require_mame

SECONDS_TO_RUN="${VON_EXPLORATORY_SECONDS:-60}"
OUT_DIR="$ROOT_DIR/von/build/attract-coverage"
PC_LOG="$OUT_DIR/exploratory-accelerated-vonj-${SECONDS_TO_RUN}s.pcs"
EVENT_LOG="$OUT_DIR/exploratory-accelerated-vonj-${SECONDS_TO_RUN}s.events"
ROM_PATH="$ROOT_DIR/von/build/disasm/rompath"

[[ -d "$ROM_PATH/vonj" ]] || die "original vonj ROM staging is missing: $ROM_PATH/vonj"
mkdir -p "$OUT_DIR"

VON_EXPLORATORY_SECONDS="$SECONDS_TO_RUN" \
VON_EXPLORATORY_PC_LOG="$PC_LOG" \
VON_EXPLORATORY_EVENTS_LOG="$EVENT_LOG" \
SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-dummy}" \
"$MAME_BIN" vonj -rompath "$ROM_PATH" -bench "$SECONDS_TO_RUN" \
    -skip_gameinfo -autoboot_script \
    "$ROOT_DIR/von/tools/trace_i960_exploratory_accelerated.lua"

printf 'Exploratory PCS (not strict evidence): %s\n' "$PC_LOG"
printf 'Exploratory events (not strict evidence): %s\n' "$EVENT_LOG"
