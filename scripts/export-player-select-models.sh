#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TRACE="${1:-$ROOT_DIR/von/build/disasm/vonj-geometry-select-40s.trace}"
ROM="${VON_GEOMETRY_ROM:-$ROOT_DIR/von/build/disasm/geometry-rom.bin}"
OUTPUT_DIR="${VON_GEOMETRY_OUTPUT:-$ROOT_DIR/von/build/disasm/geometry-objects}"
WINDOW="${VON_GEOMETRY_WINDOW:-16384}"

[[ -f "$TRACE" ]] || { printf 'error: geometry trace is missing: %s\n' "$TRACE" >&2; exit 1; }
[[ -f "$ROM" ]] || {
    printf 'Geometry ROM is missing; assembling it from private artifacts...\n'
    python3 "$ROOT_DIR/von/tools/extract_geometry_rom.py" --output "$ROM"
}

python3 "$ROOT_DIR/von/tools/dump_geometry_objects.py" \
    --trace "$TRACE" --rom "$ROM" --output-dir "$OUTPUT_DIR" \
    --window "$WINDOW"

index="$OUTPUT_DIR/index.tsv"
count=0
while IFS=$'\t' read -r file oba _; do
    [[ "$file" == "file" || -z "$file" ]] && continue
    stem="oba-${oba#0x}"
    obj="$OUTPUT_DIR/$stem.obj"
    gltf="$OUTPUT_DIR/$stem.gltf"
    python3 "$ROOT_DIR/von/tools/export_geometry_obj.py" \
        --rom "$ROM" --oba "$oba" --words "$WINDOW" --output "$obj"
    python3 "$ROOT_DIR/von/tools/export_geometry_gltf.py" "$obj" "$gltf"
    count=$((count + 1))
done < "$index"

printf 'Exported %s polygon-ROM objects to %s\n' "$count" "$OUTPUT_DIR"
