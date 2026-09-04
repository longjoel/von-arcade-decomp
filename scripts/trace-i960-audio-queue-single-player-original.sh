#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"
require_mame

OUT_ROOT="${VON_CAPTURE_OUTPUT_ROOT:-$ROOT_DIR/von/captures/audio-queue-single-player}"
MAX_SAMPLES="${VON_CAPTURE_QUEUE_MAX_SAMPLES:-4096}"
SELECTOR_STEPS="${VON_CAPTURE_SELECTOR_STEPS:-0}"
[[ "$SELECTOR_STEPS" =~ ^[0-9]+$ ]] || die "VON_CAPTURE_SELECTOR_STEPS must be nonnegative"
mkdir -p "$OUT_ROOT"

VON_CAPTURE_SELECTOR_COUNT=1 \
VON_CAPTURE_SELECTOR_START="$SELECTOR_STEPS" \
VON_CAPTURE_ENABLE_PC_TRACE=0 \
VON_CAPTURE_QUEUE_TRACE=1 \
VON_CAPTURE_QUEUE_MAX_SAMPLES="$MAX_SAMPLES" \
VON_CAPTURE_QUEUE_SAMPLE_INTERVAL="${VON_CAPTURE_QUEUE_SAMPLE_INTERVAL:-4}" \
VON_CAPTURE_OUTPUT_ROOT="$OUT_ROOT" \
"$SCRIPT_DIR/capture-single-player-original.sh"

printf 'Original-vonj selector-%s audio queue capture: %s\n' "$SELECTOR_STEPS" "$OUT_ROOT"
