#!/usr/bin/env bash
# Single-cabinet 2P-versus input fuzz: one MAME, P2 idle (no P2 fields exist
# on this cabinet), timer runs free (bout ends by timeout) or freeze via taps.
# Flow: coin, coin2 (2 credits), 2P start, cursor walk on the versus select
# screen, auto-confirm, then the fuzz_battle_ram per-input hold program.
#
# Env:
#   VON_FUZZVERSUS_OUT        output dir (default von/fuzz-versus/<stamp>)
#   VON_FUZZVERSUS_SECONDS    seconds budget (default 240)
#   VON_FUZZ_T0               coin frame anchor (default 7200; 3600 fast path)
#   VON_FUZZVERSUS_OSLOG      set to -oslog to capture geometry logerror lines
#   VON_FUZZ_SELECT_STEPS     versus cursor right-presses (default 0)
#   VON_FUZZ_SELECT_DOWN      versus cursor down-presses first (default 0)
#   VON_FUZZ_ONLY             comma subset of fuzz combos (default all)
#   VON_FUZZ_HOLD/SETTLE      hold/settle frames (default 45/45)
#   VON_FUZZ_TELEMETRY        "0xaddr,..." per-frame words during holds
#   VON_FUZZ_STATELOG         "base,len,every[;...]" region time series
#   VON_FUZZ_TAPS             "0xaddr,..." reader-PC taps during holds
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MAME_BIN="$ROOT_DIR/third_party/mame-master/von"
ROM_PATH="$ROOT_DIR/von/build/disasm/rompath"
SCRIPT="$ROOT_DIR/von/tools/fuzz_battle_ram.lua"

OUT_DIR="${VON_FUZZVERSUS_OUT:-$ROOT_DIR/von/fuzz-versus/fuzz-$(date -u +%Y%m%dT%H%M%SZ)}"
SECONDS_TO_RUN="${VON_FUZZVERSUS_SECONDS:-240}"
# Flow anchor: coin frame; coin2=+60, start2=+200, select=+950/+2200 battle.
# Default 7200 waits out attract; 3600 attempts a fast path into the
# geometry-trace line budget (131072 logerror lines from boot).
T0="${VON_FUZZ_T0:-7200}"
OSLOG="${VON_FUZZVERSUS_OSLOG:-}"

[[ -x "$MAME_BIN" ]] || { printf 'error: MAME binary is not built\n' >&2; exit 1; }
[[ -d "$ROM_PATH/vonj" ]] || { printf 'error: staged ROM path is missing\n' >&2; exit 1; }

mkdir -p "$OUT_DIR"/{cfg,nvram,inp,snaps}
echo "out: $OUT_DIR  budget: ${SECONDS_TO_RUN}s  steps: ${VON_FUZZ_SELECT_STEPS:-0}  only: ${VON_FUZZ_ONLY:-all}"

pushd "$OUT_DIR" >/dev/null
VON_FUZZ_LOG="$OUT_DIR/fuzz.log" \
VON_FUZZ_SNAP_DIR="$OUT_DIR/snaps" \
VON_FUZZ_COIN="$T0" VON_FUZZ_COIN2=$((T0 + 60)) \
VON_FUZZ_NO_START=1 VON_FUZZ_START2=$((T0 + 200)) \
VON_FUZZ_SELECT_FRAME=$((T0 + 950)) \
VON_FUZZ_SELECT_STEPS="${VON_FUZZ_SELECT_STEPS:-0}" \
VON_FUZZ_SELECT_DOWN="${VON_FUZZ_SELECT_DOWN:-0}" \
VON_FUZZ_BATTLE=$((T0 + 2200)) \
VON_FUZZ_HOLD="${VON_FUZZ_HOLD:-45}" VON_FUZZ_SETTLE="${VON_FUZZ_SETTLE:-45}" \
VON_FUZZ_ONLY="${VON_FUZZ_ONLY:-}" \
VON_FUZZ_TELEMETRY="${VON_FUZZ_TELEMETRY:-}" \
VON_FUZZ_STATELOG="${VON_FUZZ_STATELOG:-}" \
VON_FUZZ_TAPS="${VON_FUZZ_TAPS:-}" \
VON_FUZZ_SECONDS="$SECONDS_TO_RUN" \
    "$MAME_BIN" vonj \
    -rompath "$ROM_PATH" \
    -video none -sound none -nothrottle -skip_gameinfo $OSLOG \
    -cfg_directory "$OUT_DIR/cfg" -nvram_directory "$OUT_DIR/nvram" \
    -input_directory "$OUT_DIR/inp" \
    -autoboot_script "$SCRIPT" \
    -seconds_to_run "$SECONDS_TO_RUN" \
    > "$OUT_DIR/mame.log" 2>&1
popd >/dev/null

printf 'done: %s\n' "$OUT_DIR"
