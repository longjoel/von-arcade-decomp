#!/usr/bin/env bash
# Hacking bout driver: run the instrumented MAME (VON_MAME_PATCH_SET=hacking)
# headless with soft video, join a bout, force cells, set write watchpoints,
# mirror the geometry matrix, and capture PNG+JSON sidecars.
#
# Build the binary first:
#   VON_MAME_PATCH_SET=hacking VON_MAME_BIN=$PWD/bin/von-hack scripts/build.sh
#
# Examples:
#   VON_FORCE="0x503a80=3" VON_WP="0x503ad8,4,w" VON_MIRROR=10 \
#     VON_HACK_SNAP_EVERY=120 VON_HACK_SECONDS=40 scripts/hack-bout.sh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MAME_BIN="${VON_MAME_BIN:-$ROOT_DIR/bin/von-hack}"
ROM_PATH="${VON_HACK_ROMPATH:-$ROOT_DIR/von/build/disasm/rompath}"
SCRIPT="$ROOT_DIR/von/tools/hack_bout.lua"
SECONDS_TO_RUN="${VON_HACK_SECONDS:-60}"
OUT="${VON_HACK_OUT:-$ROOT_DIR/von/captures/hack-$(date -u +%Y%m%dT%H%M%SZ)}"
mkdir -p "$OUT/snap" "$OUT/cfg" "$OUT/nvram"

[[ -x "$MAME_BIN" ]] || {
    printf 'error: hacking MAME binary missing: %s\n' "$MAME_BIN" >&2
    printf 'build: VON_MAME_PATCH_SET=hacking VON_MAME_BIN=%s scripts/build.sh\n' "$MAME_BIN" >&2
    exit 1
}
[[ -d "$ROM_PATH/vonj" ]] || {
    printf 'error: ROM path missing: %s/vonj\n' "$ROM_PATH" >&2
    exit 1
}

SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-dummy}" \
VON_HACK_LOG="$OUT/hack.log" \
VON_HACK_SNAP_DIR="$OUT/snap" \
VON_HACK_SECONDS="$SECONDS_TO_RUN" \
    "$MAME_BIN" vonj -rompath "$ROM_PATH" \
    -video soft -sound none -skip_gameinfo \
    -debug -debugger none \
    -cfg_directory "$OUT/cfg" -nvram_directory "$OUT/nvram" \
    -snapshot_directory "$OUT/snap" \
    -autoboot_script "$SCRIPT" \
    -seconds_to_run "$SECONDS_TO_RUN" -nothrottle -oslog -verbose \
    > "$OUT/mame.log" 2>&1

printf 'hack capture: %s\n' "$OUT"
