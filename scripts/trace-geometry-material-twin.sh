#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SECONDS_TO_RUN="${VON_GEOMETRY_MATERIAL_SECONDS:-35}"
ROM="${VON_GEOMETRY_ROM:-$ROOT_DIR/von/build/disasm/geometry-rom.bin}"
TEXTURE_ROM="${VON_GEOMETRY_TEXTURE_ROM:-$ROOT_DIR/von/build/disasm/texture-pipeline/texture-rom.bin}"
TEXTURE_BANK="${VON_GEOMETRY_TEXTURE_BANK:-$ROOT_DIR/von/build/disasm/texture-pipeline/bank0-primary.bin}"
TEXTURE_BANK_SECONDARY="${VON_GEOMETRY_TEXTURE_BANK_SECONDARY:-$ROOT_DIR/von/build/disasm/texture-pipeline/bank0-secondary.bin}"
OUTPUT_ROOT="${VON_GEOMETRY_MATERIAL_OUTPUT:-$ROOT_DIR/von/build/disasm/first-match-material-twin}"
SCRIPT="$ROOT_DIR/von/tools/gameplay_progress.lua"

[[ "$SECONDS_TO_RUN" =~ ^[1-9][0-9]*$ ]] || {
    printf 'error: VON_GEOMETRY_MATERIAL_SECONDS must be a positive integer\n' >&2
    exit 1
}

mkdir -p "$ROOT_DIR/von/build/disasm"
if [[ ! -f "$ROM" ]]; then
    python3 "$ROOT_DIR/von/tools/extract_geometry_rom.py" --output "$ROM"
fi
if [[ ! -f "$TEXTURE_ROM" || ! -f "$TEXTURE_BANK" || ! -f "$TEXTURE_BANK_SECONDARY" ]]; then
    python3 "$ROOT_DIR/von/tools/extract_texture_pipeline.py" --output-dir "$(dirname "$TEXTURE_BANK")"
fi

RUN_LOG="$(mktemp "$ROOT_DIR/von/build/disasm/geometry-material-run.XXXXXX.log")"
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
    frame_output="$OUTPUT_DIR/$cabinet/first-match-frame-textured.gltf"
    python3 "$ROOT_DIR/von/tools/export_geometry_frame_textured_gltf.py" \
        --trace "$trace" --rom "$ROM" --texture-rom "$TEXTURE_ROM" \
        --bank-primary "$TEXTURE_BANK" --bank-secondary "$TEXTURE_BANK_SECONDARY" \
        --palette-trace "$trace" --output "$frame_output" \
        --max-time 32.8 --min-objects 100
    frame_time="$(python3 - "$frame_output" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as stream:
    print(json.load(stream)["extras"]["trace_time"])
PY
)"
    objects="$OUTPUT_DIR/$cabinet/objects"
    VON_GEOMETRY_OUTPUT="$objects" \
        "$ROOT_DIR/scripts/export-player-select-models.sh" "$trace"
    textured_objects="$OUTPUT_DIR/$cabinet/textured-objects"
    mkdir -p "$textured_objects"
    while IFS=$'\t' read -r _ oba tpa tha _ _ _; do
        [[ "$oba" == "oba" || -z "$oba" ]] && continue
        python3 "$ROOT_DIR/von/tools/export_geometry_textured_gltf.py" \
            --rom "$ROM" --texture-rom "$TEXTURE_ROM" \
            --bank-primary "$TEXTURE_BANK" --bank-secondary "$TEXTURE_BANK_SECONDARY" \
            --palette-trace "$trace" --palette-time "$frame_time" \
            --oba "$oba" --tpa "$tpa" --tha "$tha" \
            --output "$textured_objects/oba-${oba#0x}.gltf"
    done < "$objects/index.tsv"
    python3 "$ROOT_DIR/von/tools/export_geometry_frame_gltf.py" \
        --trace "$trace" --rom "$ROM" \
        --output "$OUTPUT_DIR/$cabinet/first-match-frame.gltf" \
        --max-time 32.8 --min-objects 100
    python3 "$ROOT_DIR/von/tools/extract_texture_tiles.py" \
        --trace "$trace" --bank "$TEXTURE_BANK" \
        --output-dir "$OUTPUT_DIR/$cabinet/texture-tiles" --limit 2048
done

printf 'First-match material capture: %s\n' "$TWIN_DIR"
printf 'Extracted geometry and texture materials: %s\n' "$OUTPUT_DIR"
