#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GHIDRA_HOME="${GHIDRA_HOME:-$ROOT_DIR/../voff/ghidra/ghidra_11.3.1_PUBLIC}"
GHIDRA_HEADLESS="$GHIDRA_HOME/support/analyzeHeadless"
PROCESSOR_DIR="$GHIDRA_HOME/Ghidra/Processors/i960"
ROM_IMAGE="$ROOT_DIR/von/build/disasm/vonj-maincpu.bin"
PROJECT_DIR="$ROOT_DIR/von/build/ghidra"
PROJECT_NAME="vonj-i960"
ANNOTATION_SCRIPT="$ROOT_DIR/von/ghidra/AnnotateVonI960.py"
REPORT_SCRIPT="$ROOT_DIR/von/ghidra/ReportVonI960.py"

[[ -x "$GHIDRA_HEADLESS" ]] || {
    printf 'error: Ghidra headless analyzer not found: %s\n' "$GHIDRA_HEADLESS" >&2
    exit 1
}
[[ -f "$PROCESSOR_DIR/data/languages/i960.ldefs" ]] || {
    printf 'error: i960 Ghidra processor module is not installed: %s\n' "$PROCESSOR_DIR" >&2
    printf 'Install mumbel/ghidra_i960 into Ghidra/Processors/i960 first.\n' >&2
    exit 1
}

python3 "$ROOT_DIR/von/tools/extract_maincpu.py" --output "$ROM_IMAGE"
mkdir -p "$PROJECT_DIR"

"$GHIDRA_HEADLESS" "$PROJECT_DIR" "$PROJECT_NAME" \
    -import "$ROM_IMAGE" \
    -processor "i960:LE:32:default" \
    -cspec default \
    -scriptPath "$ROOT_DIR/von/ghidra" \
    -postscript "$(basename "$ANNOTATION_SCRIPT")" \
    -overwrite \
    -log "$PROJECT_DIR/analyze.log"

"$GHIDRA_HEADLESS" "$PROJECT_DIR" "$PROJECT_NAME" \
    -process "$(basename "$ROM_IMAGE")" \
    -scriptPath "$ROOT_DIR/von/ghidra" \
    -postscript "$(basename "$REPORT_SCRIPT")" \
    -log "$PROJECT_DIR/report.log" \
    > "$PROJECT_DIR/report.txt" 2>&1

printf 'Ghidra project: %s/%s\n' "$PROJECT_DIR" "$PROJECT_NAME"
printf 'Ghidra report: %s/report.txt\n' "$PROJECT_DIR"
