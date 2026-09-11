#!/usr/bin/env bash
# Human-instrumented capture: a human joins and plays (gamepad) while the
# patched binary traces geometry and record_human_session.lua records RAM.
# Realtime flags (video/sound on, throttled) -- the human is in the loop.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MAME_BIN="$ROOT_DIR/third_party/mame-master/von"
ROM_PATH="$ROOT_DIR/von/build/disasm/rompath"
RECORDER="$ROOT_DIR/von/tools/record_human_session.lua"

OUT_DIR="${VON_HUMAN_OUT:-$ROOT_DIR/von/captures/human-$(date -u +%Y%m%dT%H%M%SZ)}"
SECONDS_TO_RUN="${VON_HUMAN_SECONDS:-600}"
TRACE_T0="${VON_TRACE_T0:-0}"
TRACE_T1="${VON_TRACE_T1:-600}"
SNAP_EVERY_S="${VON_HUMAN_SNAP_EVERY_S:-10}"
# Preload a known-good input mapping so the gamepad/marker work from boot.
# Unset VON_HUMAN_CFG: default to the mapped session's cfg. Set it to a
# cfg dir to use that; set it empty to start unmapped. Only *.cfg copied.
CFG_SRC="${VON_HUMAN_CFG-$ROOT_DIR/von/input-preload/cfg}"

[[ -x "$MAME_BIN" ]] || { printf 'error: MAME binary is not built\n' >&2; exit 1; }
[[ -d "$ROM_PATH/vonj" ]] || { printf 'error: staged ROM path is missing\n' >&2; exit 1; }

mkdir -p "$OUT_DIR"/{snaps,cfg,nvram,inp}
if [[ -n "$CFG_SRC" && -d "$CFG_SRC" ]]; then
    cp -f "$CFG_SRC"/*.cfg "$OUT_DIR/cfg"/ 2>/dev/null || true
    echo "cfg: preloaded from $CFG_SRC"
elif [[ -n "$CFG_SRC" ]]; then
    echo "cfg: WARNING source missing ($CFG_SRC), starting unmapped" >&2
else
    echo "cfg: starting unmapped (VON_HUMAN_CFG empty)"
fi
echo "out: $OUT_DIR  budget: ${SECONDS_TO_RUN}s  trace window: [$TRACE_T0, $TRACE_T1]"

# -log routes the C++ traces (logerror AND osd_printf_verbose) to ./error.log;
# run from OUT_DIR so it lands with the capture instead of the repo root. All
# other paths below are absolute, so only the working directory changes.
# Both -log and -oslog are required: geometry uses verbose, palette uses
# logerror, and -log sends both to error.log.
pushd "$OUT_DIR" >/dev/null
VON_TRACE_T0="$TRACE_T0" VON_TRACE_T1="$TRACE_T1" \
VON_RECORD_LOG="$OUT_DIR/record.log" \
VON_WATCH_WRITES="${VON_WATCH_WRITES:-}" \
VON_RECORD_SNAP_DIR="$OUT_DIR/snaps" \
VON_RECORD_SNAP_EVERY_S="$SNAP_EVERY_S" \
    "$MAME_BIN" vonj \
    -rompath "$ROM_PATH" \
    -sound auto -skip_gameinfo \
    -log -oslog \
    -cfg_directory "$OUT_DIR/cfg" -nvram_directory "$OUT_DIR/nvram" \
    -input_directory "$OUT_DIR/inp" -snapshot_directory "$OUT_DIR/snaps" \
    -autoboot_script "$RECORDER" \
    -seconds_to_run "$SECONDS_TO_RUN" \
    > "$OUT_DIR/mame.log" 2>&1
popd >/dev/null

printf 'done: %s\n' "$OUT_DIR"
