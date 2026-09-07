#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"
require_command python3
require_mame

SET_NAME="${VON_SET:-vonj}"
MAME_ARGS=("$@")
if [[ ${#MAME_ARGS[@]} -eq 0 ]]; then
    MAME_ARGS=(-window -skip_gameinfo)
fi
ROM_PATH="$(prepare_rom_path)"
trap 'cleanup_rom_path "$ROM_PATH"' EXIT
CTRLR_ARGS=()
if [[ -n "$VON_CTRLR" && -d "$VON_CTRLRPATH" ]]; then
    CTRLR_ARGS=(--ctrlr "$VON_CTRLR" --ctrlr-path "$VON_CTRLRPATH")
fi
env $(runtime_env) python3 "$ROOT_DIR/von/tools/mame_runner.py" \
        --mame "$MAME_BIN" \
        --set "$SET_NAME" \
        --rom-dir "$ROM_PATH" \
        --capture-dir "$CAPTURE_DIR" \
        "${CTRLR_ARGS[@]}" \
        -- "${MAME_ARGS[@]}"
