#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"
require_mame

I960_ROMPATH="$ROOT_DIR/von/build/rompath/reconstructed"
if [[ ! -e "$I960_ROMPATH/vonjdev/prototype-maincpu.bin" ]]; then
    "$ROOT_DIR/scripts/i960-build.sh"
fi

[[ -e "$I960_ROMPATH/vonjdev/prototype-maincpu.bin" ]] ||
    die "reconstructed i960 ROM staging is missing"

ROM_IMAGE="$(readlink -f "$I960_ROMPATH/vonjdev/prototype-maincpu.bin")"
[[ -f "$ROM_IMAGE" ]] || die "reconstructed i960 ROM target is missing: $ROM_IMAGE"
printf 'Using reconstructed i960 ROM: %s (%s bytes)\n' \
    "$ROM_IMAGE" "$(stat -c '%s' "$ROM_IMAGE")"
sha256sum "$ROM_IMAGE"

MAME_ARGS=("$@")
if [[ ${#MAME_ARGS[@]} -eq 0 ]]; then
    MAME_ARGS=(-window -skip_gameinfo)
fi

env $(runtime_env) \
    "$MAME_BIN" vonjdev -rompath "$I960_ROMPATH" "${MAME_ARGS[@]}"
