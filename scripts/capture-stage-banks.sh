#!/usr/bin/env bash
# Capture the two texture RAMs for each stage ordinal while that stage is live.
#
# The arena exporter must texture from the RAM state the hardware showed; bank1
# holds the current stage's tiles and is scene-dependent. This reuses
# probe_stage_binding.lua's forcing path without the heavy geometry trace.
#
# Env: VON_MAME_BIN, VON_CAPTURE_DIR, VON_ORDINALS, VON_STAGE_SECONDS
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MAME_BIN="${VON_MAME_BIN:-$ROOT_DIR/bin/von}"
ROM_PATH="$ROOT_DIR/von/build/disasm/rompath"
OUT_DIR="${VON_CAPTURE_DIR:-$ROOT_DIR/von/build/disasm/stage-captures}"
ORDINALS="${VON_ORDINALS:-0 1 2 3 4 5 6 7 8 9}"
# 50s reaches the live match/arena (a shorter run can capture the pre-match
# loading screen, whose RAM state is not the stage's).
RUN_SECONDS="${VON_STAGE_SECONDS:-50}"

[[ -x "$MAME_BIN" ]] || { printf 'error: no MAME binary: %s\n' "$MAME_BIN" >&2; exit 1; }
[[ -d "$ROM_PATH/vonj" ]] || { printf 'error: no rompath: %s\n' "$ROM_PATH" >&2; exit 1; }
mkdir -p "$OUT_DIR"

for ord in $ORDINALS; do
    bank_dir="$OUT_DIR/ord$ord-banks"
    if [[ -s "$bank_dir/texture-11000000.hex" && -s "$bank_dir/texture-11200000.hex" \
          && -s "$bank_dir/palette.trace" ]]; then
        printf 'ord %s: banks already captured (%s)\n' "$ord" "$bank_dir"
        continue
    fi
    VON_STAGE_LOG="$OUT_DIR/ord$ord.banks.log" \
    VON_STAGE_ORDINAL="$ord" \
    VON_STAGE_SECONDS="$RUN_SECONDS" \
    VON_STAGE_TEXTURE_DUMP="$bank_dir" \
    VON_STAGE_TEXTURE_FRAME="$((RUN_SECONDS * 60 - 120))" \
    VON_STAGE_PALETTE_DUMP="$bank_dir/palette.trace" \
    VON_STAGE_SNAPSHOT="$OUT_DIR/ord$ord-reference.png" \
        env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        "$MAME_BIN" vonj \
        -rompath "$ROM_PATH" \
        -video none -sound none \
        -autoboot_script "$ROOT_DIR/von/tools/probe_stage_binding.lua" \
        -seconds_to_run "$((RUN_SECONDS + 10))" -skip_gameinfo -nothrottle \
        >"$OUT_DIR/ord$ord.banks.mame.log" 2>&1 || true
    printf 'ord %s: banks -> %s\n' "$ord" "$bank_dir"
done
