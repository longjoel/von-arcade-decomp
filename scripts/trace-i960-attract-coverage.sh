#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"
require_mame

SECONDS_TO_RUN="${VON_ATTRACT_SECONDS:-60}"
CAPTURE_ID="vonj-attract-${SECONDS_TO_RUN}s"
OUT_DIR="$ROOT_DIR/von/build/attract-coverage"
RUN_DIR="$OUT_DIR/$CAPTURE_ID"
PC_LOG="$OUT_DIR/vonj-attract-${SECONDS_TO_RUN}s.pcs"
JSON_REPORT="$OUT_DIR/vonj-attract-${SECONDS_TO_RUN}s.json"
MARKDOWN_REPORT="$OUT_DIR/vonj-attract-${SECONDS_TO_RUN}s.md"
WORKLIST_JSON="$OUT_DIR/vonj-attract-${SECONDS_TO_RUN}s.worklist.json"
WORKLIST_MARKDOWN="$OUT_DIR/vonj-attract-${SECONDS_TO_RUN}s.worklist.md"
CAPTURE_MANIFEST="$OUT_DIR/vonj-attract-${SECONDS_TO_RUN}s.capture.json"
LISTING="$ROOT_DIR/von/build/disasm/vonj-maincpu.lst"
ROM_PATH="$ROOT_DIR/von/build/disasm/rompath"

[[ -f "$LISTING" ]] || die "i960 listing is missing; run scripts/remote-disasm-i960.sh"
[[ -d "$ROM_PATH/vonj" ]] || die "staged vonj ROM path is missing: $ROM_PATH/vonj"
mkdir -p "$OUT_DIR" "$RUN_DIR/cfg" "$RUN_DIR/nvram" "$RUN_DIR/state"

VON_ATTRACT_SECONDS="$SECONDS_TO_RUN" \
VON_ATTRACT_PC_LOG="$PC_LOG" \
SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-dummy}" \
"$MAME_BIN" vonj -rompath "$ROM_PATH" \
    -debug -debugger none -video none -sound none -skip_gameinfo -nothrottle \
    -cfg_directory "$RUN_DIR/cfg" -nvram_directory "$RUN_DIR/nvram" \
    -state_directory "$RUN_DIR/state" \
    -autoboot_script "$ROOT_DIR/von/tools/trace_i960_attract_coverage.lua" \
    -seconds_to_run "$SECONDS_TO_RUN"

python3 "$ROOT_DIR/von/tools/analyze_attract_coverage.py" \
    --pcs "$PC_LOG" --listing "$LISTING" \
    --json "$JSON_REPORT" --markdown "$MARKDOWN_REPORT" \
    --capture-id "$CAPTURE_ID" \
    --annotations "$ROOT_DIR/von/ghidra/AnnotateVonI960.py"
python3 "$ROOT_DIR/von/tools/capture_manifest.py" \
    --output "$CAPTURE_MANIFEST" --root "$ROOT_DIR" \
    --id "$CAPTURE_ID" --objective "c-only-i960-attract-60s" \
    --seconds "$SECONDS_TO_RUN" --phase stable-attract --set vonj \
    --checkpoint reset --checkpoint hardware-init --checkpoint scheduler \
    --checkpoint attract-entry --checkpoint duration-complete \
    --mame-revision "$(git -C "$ROOT_DIR/third_party/mame-master" rev-parse HEAD)" \
    --patch-profile "${VON_MAME_PATCH_SET:-default}" --execution-engine interpreter \
    --command "$MAME_BIN" --command vonj --command -rompath --command "$ROM_PATH" \
    --command -debug --command -debugger --command none --command -video --command none \
    --command -sound --command none --command -skip_gameinfo --command -nothrottle \
    --command -cfg_directory --command "$RUN_DIR/cfg" \
    --command -nvram_directory --command "$RUN_DIR/nvram" \
    --command -state_directory --command "$RUN_DIR/state" \
    --command -autoboot_script --command "$ROOT_DIR/von/tools/trace_i960_attract_coverage.lua" \
    --command -seconds_to_run --command "$SECONDS_TO_RUN" \
    --coverage-report "$JSON_REPORT" \
    --cfg-directory "$RUN_DIR/cfg" --nvram-directory "$RUN_DIR/nvram" \
    --state-directory "$RUN_DIR/state" \
    --input "$ROOT_DIR/von/rom_manifest.json" \
    --artifact "$PC_LOG" --artifact "$JSON_REPORT"
python3 "$ROOT_DIR/von/tools/build_attract_worklist.py" \
    --coverage "$JSON_REPORT" --ledger "$ROOT_DIR/von/reconstruction_ledger.json" \
    --json "$WORKLIST_JSON" --markdown "$WORKLIST_MARKDOWN"

printf 'PC coverage: %s\n' "$PC_LOG"
printf 'Coverage report: %s\n' "$MARKDOWN_REPORT"
printf 'Worklist: %s\n' "$WORKLIST_MARKDOWN"
printf 'Capture manifest: %s\n' "$CAPTURE_MANIFEST"
