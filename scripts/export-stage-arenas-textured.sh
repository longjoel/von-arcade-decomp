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
    # Prefer the texture RAMs captured with this ordinal's geometry trace: the
    # stage's textures live in bank1 and that RAM is scene-dependent. Without a
    # dump the tool falls back to the boot sheets, which render the title atlas.
    bank_args=()
    bank_dir="$CAP_DIR/ord$ord-banks"
    if [[ -f "$bank_dir/texture-11000000.hex" && -f "$bank_dir/texture-11200000.hex" ]]; then
        bank_args=(--bank0 "$bank_dir/texture-11000000.hex"
                   --bank1 "$bank_dir/texture-11200000.hex")
    else
        printf 'ord %s: no captured texture banks; using boot sheets\n' "$ord" >&2
    fi
    # The geometry trace's palette-write log caps out during boot, so prefer the
    # palette RAM captured live at match time with the banks.
    palette="$trace"
    if [[ -f "$bank_dir/palette.trace" ]]; then
        palette="$bank_dir/palette.trace"
    fi
    python3 "$ROOT_DIR/von/tools/extract_stage_textured_gltf.py" \
        --stage "$ord" \
        --trace "$trace" \
        --palette-trace "$palette" \
        "${bank_args[@]}" \
        --output "$OUT_DIR/stage_$(printf '%02d' "$ord")_arena.gltf"
done
