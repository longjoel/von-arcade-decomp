#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"
require_mame

SECONDS_TO_RUN="${VON_AUDIO_QUEUE_SECONDS:-5}"
MAX_SAMPLES="${VON_AUDIO_QUEUE_MAX_SAMPLES:-4096}"
OUT_PATH="${VON_AUDIO_QUEUE_LOG:-$ROOT_DIR/von/build/attract-coverage/vonj-audio-queue.log}"
ROM_PATH="$ROOT_DIR/von/build/disasm/rompath"

[[ -d "$ROM_PATH/vonj" ]] || die "original vonj ROM staging is missing: $ROM_PATH/vonj"
mkdir -p "$(dirname "$OUT_PATH")"

VON_AUDIO_QUEUE_SECONDS="$SECONDS_TO_RUN" \
VON_AUDIO_QUEUE_MAX_SAMPLES="$MAX_SAMPLES" \
VON_AUDIO_QUEUE_LOG="$OUT_PATH" \
SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-dummy}" \
"$MAME_BIN" vonj -rompath "$ROM_PATH" -bench "$SECONDS_TO_RUN" \
    -skip_gameinfo -autoboot_script \
    "$ROOT_DIR/von/tools/trace_i960_audio_queue_original.lua"

printf 'Original-vonj audio queue trace: %s\n' "$OUT_PATH"
