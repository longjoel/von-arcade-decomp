#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"
require_mame

SECONDS_TO_RUN="${VON_CLEAN_AUDIT_SECONDS:-8}"
OUT_DIR="$ROOT_DIR/von/build/i960/clean-audit"
PC_LOG="$OUT_DIR/clean-${SECONDS_TO_RUN}s.pcs"
RUN_LOG="$OUT_DIR/clean-${SECONDS_TO_RUN}s.log"
ROM_PATH="$ROOT_DIR/von/build/rompath/reconstructed-clean"
MANIFEST="$ROOT_DIR/von/build/i960/reconstructed-clean-maincpu.manifest.json"

[[ -e "$ROM_PATH/vonjdev/prototype-maincpu.bin" ]] || "$ROOT_DIR/scripts/i960-build.sh"
[[ -f "$MANIFEST" ]] || die "clean image manifest is missing: $MANIFEST"
mkdir -p "$OUT_DIR"

set +e
VON_ATTRACT_SECONDS="$SECONDS_TO_RUN" \
VON_ATTRACT_PC_LOG="$PC_LOG" \
SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-dummy}" \
"$MAME_BIN" vonjdev -rompath "$ROM_PATH" \
    -debug -debugger none -video none -sound none -skip_gameinfo -nothrottle \
    -autoboot_script "$ROOT_DIR/von/tools/trace_i960_attract_coverage.lua" \
    -seconds_to_run "$SECONDS_TO_RUN" 2>&1 | tee "$RUN_LOG"
MAME_STATUS=$?
set -e

AUDIT_STATUS=0
if [[ -s "$PC_LOG" ]]; then
    python3 "$ROOT_DIR/von/tools/audit_clean_i960_coverage.py" \
        --pcs "$PC_LOG" --manifest "$MANIFEST" || AUDIT_STATUS=$?
else
    printf 'error: MAME produced no i960 PC coverage: %s\n' "$PC_LOG" >&2
    AUDIT_STATUS=1
fi

if [[ "$MAME_STATUS" -ne 0 ]]; then
    printf 'error: MAME clean runtime exited with status %d\n' "$MAME_STATUS" >&2
    exit "$MAME_STATUS"
fi
if rg -q 'Unhandled 00|Unhandled exception|\[LUA ERROR\]' "$RUN_LOG"; then
    printf 'error: MAME reported an i960 or instrumentation failure; see %s\n' "$RUN_LOG" >&2
    exit 1
fi
exit "$AUDIT_STATUS"
