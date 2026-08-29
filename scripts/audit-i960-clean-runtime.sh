#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"
require_mame

SECONDS_TO_RUN="${VON_CLEAN_AUDIT_SECONDS:-8}"
OUT_DIR="$ROOT_DIR/von/build/i960/clean-audit"
PC_LOG="$OUT_DIR/clean-${SECONDS_TO_RUN}s.pcs"
ROM_PATH="$ROOT_DIR/von/build/rompath/reconstructed-clean"
MANIFEST="$ROOT_DIR/von/build/i960/reconstructed-clean-maincpu.manifest.json"

[[ -e "$ROM_PATH/vonjdev/prototype-maincpu.bin" ]] || "$ROOT_DIR/scripts/i960-build.sh"
[[ -f "$MANIFEST" ]] || die "clean image manifest is missing: $MANIFEST"
mkdir -p "$OUT_DIR"

VON_ATTRACT_SECONDS="$SECONDS_TO_RUN" \
VON_ATTRACT_PC_LOG="$PC_LOG" \
SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-dummy}" \
"$MAME_BIN" vonjdev -rompath "$ROM_PATH" \
    -debug -debugger none -video none -sound none -skip_gameinfo -nothrottle \
    -autoboot_script "$ROOT_DIR/von/tools/trace_i960_attract_coverage.lua" \
    -seconds_to_run "$SECONDS_TO_RUN"

python3 "$ROOT_DIR/von/tools/audit_clean_i960_coverage.py" \
    --pcs "$PC_LOG" --manifest "$MANIFEST"
