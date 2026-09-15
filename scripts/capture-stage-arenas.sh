#!/usr/bin/env bash
# Capture one geometry trace per stage ordinal for arena texture-address recovery.
#
# Each run joins the deterministic first match, forces 0x503a80 to the ordinal,
# and logs the instrumented geometry stream (patch 0007) via -oslog. The
# per-OBA tpa/tha in that stream is what extract_stage_textured_gltf.py needs.
#
# Env: VON_MAME_BIN, VON_CAPTURE_DIR, VON_ORDINALS, VON_STAGE_SECONDS
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MAME_BIN="${VON_MAME_BIN:-$ROOT_DIR/bin/von}"
ROM_PATH="$ROOT_DIR/von/build/disasm/rompath"
OUT_DIR="${VON_CAPTURE_DIR:-$ROOT_DIR/von/build/disasm/stage-captures}"
ORDINALS="${VON_ORDINALS:-0 1 2 3 4 5 6 7 8 9}"
RUN_SECONDS="${VON_STAGE_SECONDS:-50}"

[[ -x "$MAME_BIN" ]] || { printf 'error: no MAME binary: %s\n' "$MAME_BIN" >&2; exit 1; }
[[ -d "$ROM_PATH/vonj" ]] || { printf 'error: no rompath: %s\n' "$ROM_PATH" >&2; exit 1; }
mkdir -p "$OUT_DIR"

for ord in $ORDINALS; do
    trace="$OUT_DIR/ord$ord.trace"
    if [[ -s "$trace" ]]; then
        printf 'ord %s: already captured (%s)\n' "$ord" "$trace"
        continue
    fi
    # Dump the two texture RAMs late in the run so the exporter textures from the
    # same scene state the geometry was submitted in (bank1 holds the stage).
    VON_STAGE_LOG="$OUT_DIR/ord$ord.lua.log" \
    VON_STAGE_ORDINAL="$ord" \
    VON_STAGE_SECONDS="$RUN_SECONDS" \
    VON_STAGE_TEXTURE_DUMP="$OUT_DIR/ord$ord-banks" \
    VON_STAGE_TEXTURE_FRAME="$((RUN_SECONDS * 60 - 120))" \
        "$MAME_BIN" vonj \
        -rompath "$ROM_PATH" \
        -video none -sound none -oslog \
        -autoboot_script "$ROOT_DIR/von/tools/probe_stage_binding.lua" \
        -seconds_to_run "$((RUN_SECONDS + 10))" -skip_gameinfo -nothrottle \
        >"$trace" 2>&1 || true
    objects=$(grep -c 'vonj_geometry_object:' "$trace" || true)
    printf 'ord %s: %s geometry objects -> %s\n' "$ord" "$objects" "$trace"
done
