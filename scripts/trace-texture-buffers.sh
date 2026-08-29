#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"
require_mame

ROM_PATH="$ROOT_DIR/von/build/disasm/rompath"
OUT_DIR="$ROOT_DIR/von/build/disasm"
SCRIPT="$ROOT_DIR/von/tools/trace_texture_buffers.lua"
FRAMES_TO_RUN="${VON_TEXTURE_FRAMES:-600}"
SECONDS_TO_RUN="${VON_TEXTURE_SECONDS:-10}"

[[ -d "$ROM_PATH/vonj" ]] || { printf 'error: staged ROM path is missing\n' >&2; exit 1; }

mkdir -p "$OUT_DIR"
rm -f "$OUT_DIR"/texture-11000000.*.hex "$OUT_DIR"/texture-11200000.*.hex
SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-dummy}" env $(runtime_env) \
    VON_TEXTURE_LOG="$OUT_DIR/vonj-texture-buffers.log" \
    VON_TEXTURE_DUMP_DIR="$OUT_DIR" \
    VON_TEXTURE_FRAMES="$FRAMES_TO_RUN" \
    "$MAME_BIN" vonj \
    -rompath "$ROM_PATH" \
    -video none -sound none -oslog \
    -autoboot_script "$SCRIPT" \
    -seconds_to_run "$SECONDS_TO_RUN" -skip_gameinfo -nothrottle \
    > "$OUT_DIR/vonj-texture-buffers.trace" 2>&1

for bank in 11000000 11200000; do
    latest="$(find "$OUT_DIR" -maxdepth 1 -type f -name "texture-$bank.*.hex" -printf '%T@ %p\n' | sort -n | tail -n 1 | cut -d' ' -f2-)"
    [[ -n "$latest" ]] || { printf 'error: no texture dump was captured for %s\n' "$bank" >&2; exit 1; }
    ln -sfn "$(basename "$latest")" "$OUT_DIR/texture-$bank.hex"
done

printf 'Wrote %s\n' "$OUT_DIR/vonj-texture-buffers.log"
printf 'Published %s and %s\n' "$OUT_DIR/texture-11000000.hex" "$OUT_DIR/texture-11200000.hex"
