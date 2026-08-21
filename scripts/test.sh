#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
require_command python3
require_mame

cd "$ROOT_DIR"
python3 von/tools/rom_audit.py

SYSTEM_LIST="$(LD_LIBRARY_PATH="$(brew_runtime_path)${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" \
    "$MAME_BIN" -listfull)"
[[ "$SYSTEM_LIST" =~ (^|$'\n')vonj[[:space:]] ]] || die "vonj driver is not present in the built target"

LD_LIBRARY_PATH="$(brew_runtime_path)${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" \
    "$MAME_BIN" vonj -rompath "$ROM_DIR" -validate

if [[ -f "$ROOT_DIR/von/build/i960/prototype-maincpu.bin" ]]; then
    LD_LIBRARY_PATH="$(brew_runtime_path)${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" \
        "$MAME_BIN" vonjdev -rompath "$ROOT_DIR/von/build/rompath" -validate
fi

printf 'Tests passed.\n'
