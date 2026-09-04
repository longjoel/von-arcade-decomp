#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"
require_mame

SECONDS_TO_RUN="${VON_ATTRACT_SECONDS:-60}"
OUT_DIR="$ROOT_DIR/von/build/attract-coverage"
PC_LOG="$OUT_DIR/vonj-attract-${SECONDS_TO_RUN}s.pcs"
JSON_REPORT="$OUT_DIR/vonj-attract-${SECONDS_TO_RUN}s.json"
MARKDOWN_REPORT="$OUT_DIR/vonj-attract-${SECONDS_TO_RUN}s.md"
WORKLIST_JSON="$OUT_DIR/vonj-attract-${SECONDS_TO_RUN}s.worklist.json"
WORKLIST_MARKDOWN="$OUT_DIR/vonj-attract-${SECONDS_TO_RUN}s.worklist.md"
LISTING="$ROOT_DIR/von/build/disasm/vonj-maincpu.lst"
ROM_PATH="$ROOT_DIR/von/build/disasm/rompath"

[[ -f "$LISTING" ]] || die "i960 listing is missing; run scripts/remote-disasm-i960.sh"
[[ -d "$ROM_PATH/vonj" ]] || die "staged vonj ROM path is missing: $ROM_PATH/vonj"
mkdir -p "$OUT_DIR"

VON_ATTRACT_SECONDS="$SECONDS_TO_RUN" \
VON_ATTRACT_PC_LOG="$PC_LOG" \
SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-dummy}" \
"$MAME_BIN" vonj -rompath "$ROM_PATH" \
    -debug -debugger none -video none -sound none -skip_gameinfo -nothrottle \
    -autoboot_script "$ROOT_DIR/von/tools/trace_i960_attract_coverage.lua" \
    -seconds_to_run "$SECONDS_TO_RUN"

python3 "$ROOT_DIR/von/tools/analyze_attract_coverage.py" \
    --pcs "$PC_LOG" --listing "$LISTING" \
    --json "$JSON_REPORT" --markdown "$MARKDOWN_REPORT" \
    --annotations "$ROOT_DIR/von/ghidra/AnnotateVonI960.py"
python3 "$ROOT_DIR/von/tools/build_attract_worklist.py" \
    --coverage "$JSON_REPORT" --ledger "$ROOT_DIR/von/reconstruction_ledger.json" \
    --json "$WORKLIST_JSON" --markdown "$WORKLIST_MARKDOWN"

printf 'PC coverage: %s\n' "$PC_LOG"
printf 'Coverage report: %s\n' "$MARKDOWN_REPORT"
printf 'Worklist: %s\n' "$WORKLIST_MARKDOWN"
