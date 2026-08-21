#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -z "${VON_MAME_BIN:-}" && -x "$SCRIPT_DIR/../bin/von" ]]; then
    VON_MAME_BIN="$SCRIPT_DIR/../bin/von"
else
    VON_MAME_BIN="${VON_MAME_BIN:-$SCRIPT_DIR/../third_party/mame-master/von}"
fi
source "$SCRIPT_DIR/common.sh"
require_command python3
require_mame

SET_NAME="${VON_SET:-vonj}"
MAME_ARGS=("$@")
if [[ ${#MAME_ARGS[@]} -eq 0 ]]; then
    MAME_ARGS=(-window -skip_gameinfo)
fi
ROM_PATH="$(prepare_rom_path)"
LD_LIBRARY_PATH="$(brew_runtime_path)${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" \
    python3 "$ROOT_DIR/von/tools/mame_runner.py" \
        --mame "$MAME_BIN" \
        --set "$SET_NAME" \
        --rom-dir "$ROM_PATH" \
        --capture-dir "$CAPTURE_DIR" \
        -- "${MAME_ARGS[@]}"
