#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 "$ROOT_DIR/von/tools/build_clean_i960_image.py" \
    --generated "$ROOT_DIR/von/build/i960/reconstructed.bin" \
    --original "$ROOT_DIR/von/build/i960/vonj-original-maincpu.bin" \
    --ranges "$ROOT_DIR/von/i960/approved_data_ranges.json" \
    --output "$ROOT_DIR/von/build/i960/reconstructed-clean-maincpu.bin" \
    --build-manifest "$ROOT_DIR/von/build/i960/reconstructed-clean-maincpu.manifest.json"
rm -rf "$ROOT_DIR/von/build/rompath/reconstructed-clean"
cp -a "$ROOT_DIR/von/build/rompath/reconstructed" \
    "$ROOT_DIR/von/build/rompath/reconstructed-clean"
ln -sfn ../../../i960/reconstructed-clean-maincpu.bin \
    "$ROOT_DIR/von/build/rompath/reconstructed-clean/vonjdev/prototype-maincpu.bin"
