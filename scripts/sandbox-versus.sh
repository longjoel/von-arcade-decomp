#!/usr/bin/env bash
# Movement sandbox: single-cabinet 2P versus (P2 idle dummy), frozen round
# timer, scripted P1 program. Headless-fast: -video none, no sound,
# unthrottled. The Lua drives everything; this only sets up dirs/env.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MAME_BIN="$ROOT_DIR/third_party/mame-master/von"
ROM_PATH="$ROOT_DIR/von/build/disasm/rompath"
SANDBOX="$ROOT_DIR/von/tools/sandbox_versus.lua"

OUT_DIR="${VON_SANDBOX_OUT:-$ROOT_DIR/von/sandbox/sandbox-$(date -u +%Y%m%dT%H%M%SZ)}"
SECONDS_TO_RUN="${VON_SANDBOX_SECONDS:-1200}"

[[ -x "$MAME_BIN" ]] || { printf 'error: MAME binary is not built\n' >&2; exit 1; }
[[ -d "$ROM_PATH/vonj" ]] || { printf 'error: staged ROM path is missing\n' >&2; exit 1; }

mkdir -p "$OUT_DIR"/{cfg,nvram,inp}
echo "out: $OUT_DIR  budget: ${SECONDS_TO_RUN}s"

pushd "$OUT_DIR" >/dev/null
VON_SANDBOX_LOG="$OUT_DIR/sandbox.log" \
VON_SANDBOX_FREEZE="${VON_SANDBOX_FREEZE:-1}" \
VON_SANDBOX_RECON="${VON_SANDBOX_RECON:-8}" \
VON_SANDBOX_WEAPON_CASE="${VON_SANDBOX_WEAPON_CASE:-left}" \
VON_SANDBOX_SHOT_INTERVAL="${VON_SANDBOX_SHOT_INTERVAL:-6}" \
VON_SANDBOX_WEAPON_LOG="${VON_SANDBOX_WEAPON_LOG:-0}" \
VON_SANDBOX_WEAPON_WRITES="${VON_SANDBOX_WEAPON_WRITES:-0}" \
VON_SANDBOX_SINGLE_PLAYER="${VON_SANDBOX_SINGLE_PLAYER:-0}" \
VON_SANDBOX_ACTIVE_LEVELS="${VON_SANDBOX_ACTIVE_LEVELS:-0}" \
    "$MAME_BIN" vonj \
    -rompath "$ROM_PATH" \
    -video none -sound none -nothrottle -skip_gameinfo \
    -cfg_directory "$OUT_DIR/cfg" -nvram_directory "$OUT_DIR/nvram" \
    -input_directory "$OUT_DIR/inp" \
    -autoboot_script "$SANDBOX" \
    -seconds_to_run "$SECONDS_TO_RUN" \
    > "$OUT_DIR/mame.log" 2>&1
popd >/dev/null

printf 'done: %s\n' "$OUT_DIR"
