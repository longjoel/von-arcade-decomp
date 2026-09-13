#!/usr/bin/env bash
# Regenerate every stage_<NN>_arena.gltf with recovered UVs and texture tiles.
#
# Consumes the per-ordinal geometry traces from capture-stage-arenas.sh and
# writes textured glTFs straight into the Godot project's (ignored) generated
# arena directory. Textured statics keep their UVs/materials; any static whose
# texture addresses were not traced stays as a position-only gray mesh.
#
# Env: VON_GODOT, VON_CAPTURE_DIR
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GODOT_DIR="${VON_GODOT:-$ROOT_DIR/../von-godot}"
CAP_DIR="${VON_CAPTURE_DIR:-$ROOT_DIR/von/build/disasm/stage-captures}"
OUT_DIR="$GODOT_DIR/assets/generated/arena"

[[ -d "$GODOT_DIR" ]] || { printf 'error: no Godot project: %s\n' "$GODOT_DIR" >&2; exit 1; }
mkdir -p "$OUT_DIR"

for ord in ${VON_ORDINALS:-0 1 2 3 4 5 6 7 8 9}; do
    trace="$CAP_DIR/ord$ord.trace"
    if [[ ! -s "$trace" ]]; then
        printf 'ord %s: no capture trace, skipped\n' "$ord"
        continue
    fi
    python3 "$ROOT_DIR/von/tools/extract_stage_textured_gltf.py" \
        --stage "$ord" \
        --trace "$trace" \
        --palette-trace "$trace" \
        --output "$OUT_DIR/stage_$(printf '%02d' "$ord")_arena.gltf"
done
