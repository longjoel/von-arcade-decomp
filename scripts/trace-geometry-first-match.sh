#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SECONDS_TO_RUN="${VON_GEOMETRY_FIRST_MATCH_SECONDS:-35}"
ROM="${VON_GEOMETRY_ROM:-$ROOT_DIR/von/build/disasm/geometry-rom.bin}"
OUTPUT_ROOT="${VON_GEOMETRY_FIRST_MATCH_OUTPUT:-$ROOT_DIR/von/build/disasm/first-match-twin}"
SCRIPT="$ROOT_DIR/von/tools/gameplay_progress.lua"

[[ "$SECONDS_TO_RUN" =~ ^[1-9][0-9]*$ ]] || {
    printf 'error: VON_GEOMETRY_FIRST_MATCH_SECONDS must be a positive integer\n' >&2
    exit 1
}

mkdir -p "$ROOT_DIR/von/build/disasm"
if [[ ! -f "$ROM" ]]; then
    python3 "$ROOT_DIR/von/tools/extract_geometry_rom.py" --output "$ROM"
fi

RUN_LOG="$(mktemp "$ROOT_DIR/von/build/disasm/geometry-first-match-run.XXXXXX.log")"
trap 'rm -f -- "$RUN_LOG"' EXIT

SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-dummy}" \
VON_TWIN_SECONDS="$SECONDS_TO_RUN" \
VON_PROGRESS_SECONDS="$SECONDS_TO_RUN" \
VON_PROGRESS_COMBAT=0 \
    "$ROOT_DIR/scripts/run-twin.sh" \
    -video none -sound none -oslog -nothrottle \
    -autoboot_script "$SCRIPT" >"$RUN_LOG" 2>&1

TWIN_DIR="$(awk -F': ' '/^Twin capture directory:/ {value=$2} END {print value}' "$RUN_LOG")"
[[ -n "$TWIN_DIR" && -f "$TWIN_DIR/p1/mame.log" && -f "$TWIN_DIR/p2/mame.log" ]] || {
    printf 'error: twin runner did not report a usable capture directory\n' >&2
    cat "$RUN_LOG" >&2
    exit 1
}

STAMP="$(basename "$TWIN_DIR")"
OUTPUT_DIR="$OUTPUT_ROOT/$STAMP"
mkdir -p "$OUTPUT_DIR/p1" "$OUTPUT_DIR/p2"

for cabinet in p1 p2; do
    trace="$TWIN_DIR/$cabinet/mame.log"
    objects="$OUTPUT_DIR/$cabinet/objects"
    VON_GEOMETRY_OUTPUT="$objects" \
        "$ROOT_DIR/scripts/export-player-select-models.sh" "$trace"
    python3 "$ROOT_DIR/von/tools/export_geometry_frame_gltf.py" \
        --trace "$trace" --rom "$ROM" \
        --output "$OUTPUT_DIR/$cabinet/first-match-frame.gltf" \
        --max-time 32.8 --min-objects 100
done

printf 'First-match geometry capture: %s\n' "$TWIN_DIR"
printf 'Extracted scene and models: %s\n' "$OUTPUT_DIR"
