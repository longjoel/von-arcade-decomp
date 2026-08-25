#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MAME_BIN="$ROOT_DIR/third_party/mame-master/von"
TOOLBOX_NAME="${VON_TOOLBOX:-von-mame}"
ROM_PATH="$ROOT_DIR/von/build/disasm/rompath"
OUT_DIR="$ROOT_DIR/von/build/disasm"
SCRIPT="$ROOT_DIR/von/tools/trace_texture_buffers.lua"

[[ -x "$MAME_BIN" ]] || { printf 'error: MAME binary is not built\n' >&2; exit 1; }
[[ -d "$ROM_PATH/vonj" ]] || { printf 'error: staged ROM path is missing\n' >&2; exit 1; }

rm -f "$OUT_DIR"/texture-11000000.*.hex "$OUT_DIR"/texture-11200000.*.hex
toolbox run --container "$TOOLBOX_NAME" env \
    VON_TEXTURE_LOG="$OUT_DIR/vonj-texture-buffers.log" \
    VON_TEXTURE_DUMP_DIR="$OUT_DIR" \
    "$MAME_BIN" vonj \
    -rompath "$ROM_PATH" \
    -video none -sound none -oslog \
    -autoboot_script "$SCRIPT" \
    -seconds_to_run 10 -skip_gameinfo -nothrottle \
    > "$OUT_DIR/vonj-texture-buffers.trace" 2>&1

printf 'Wrote %s\n' "$OUT_DIR/vonj-texture-buffers.log"
