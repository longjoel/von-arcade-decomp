#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"
require_mame
require_command docker

I960_BIN="$ROOT_DIR/von/build/i960/prototype-maincpu.bin"
I960_ROMPATH="$ROOT_DIR/von/build/rompath"

if [[ ! -f "$I960_BIN" || ! -e "$I960_ROMPATH/vonjdev/prototype-maincpu.bin" ]]; then
    "$ROOT_DIR/scripts/i960-build.sh"
fi

[[ -f "$I960_BIN" ]] || die "i960 prototype was not generated"
[[ -e "$I960_ROMPATH/vonjdev/prototype-maincpu.bin" ]] || die "i960 ROM staging is missing"

MAME_ARGS=("$@")
if [[ ${#MAME_ARGS[@]} -eq 0 ]]; then
    MAME_ARGS=(-window -skip_gameinfo)
fi

LD_LIBRARY_PATH="$(brew_runtime_path)${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" \
    "$MAME_BIN" vonjdev \
        -rompath "$I960_ROMPATH" \
        "${MAME_ARGS[@]}"
