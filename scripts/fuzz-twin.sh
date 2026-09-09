#!/usr/bin/env bash
# Twin input-fuzz run: P1 drives per-input holds with RAM snapshots;
# P2 joins versus then idles (enemy AI off: human-controlled dummy).
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MAME_BIN="${VON_MAME_BIN:-$ROOT_DIR/third_party/mame-master/von}"
ROM_PATH="$ROOT_DIR/von/build/disasm/rompath"
SCRIPT="$ROOT_DIR/von/tools/fuzz_battle_ram.lua"
OUT="${VON_FUZZ_TWIN_OUT:-/tmp/fuzztwin}"
P1_PORT="${VON_P1_PORT:-12340}"
P2_PORT="${VON_P2_PORT:-12341}"
SECONDS_TO_RUN="${VON_FUZZ_SECONDS:-110}"
mkdir -p "$OUT/p1snaps" "$OUT/p2snaps"
[[ -x "$MAME_BIN" ]] || { echo "no MAME binary"; exit 1; }

launch() {
    local role="$1" port="$2" rport="$3" idle="$4" log="$5" snaps="$6" master="$7" coin="$8" start="$9" extra="${10:-}"
    # shellcheck disable=SC2086
    env SDL_VIDEODRIVER=dummy \
    VON_FUZZ_LOG="$log" VON_FUZZ_SNAP_DIR="$snaps" \
    VON_FUZZ_IDLE="$idle" VON_FUZZ_SECONDS="$SECONDS_TO_RUN" \
    VON_FUZZ_COIN="$coin" VON_FUZZ_START="$start" \
    VON_FUZZ_BATTLE="${VON_FUZZ_BATTLE:-2400}" \
    VON_FUZZ_ONLY="${VON_FUZZ_ONLY:-}" VON_FUZZ_HOLD="${VON_FUZZ_HOLD:-45}" \
    VON_FUZZ_SETTLE="${VON_FUZZ_SETTLE:-45}" VON_FUZZ_TAPS="${VON_FUZZ_TAPS:-}" \
    VON_FUZZ_TELEMETRY="${VON_FUZZ_TELEMETRY:-}" $extra \
    "$MAME_BIN" vonj -rompath "$ROM_PATH" -verbose \
        -video soft -sound none -skip_gameinfo \
        -cfg_directory "$OUT/$role-cfg" -nvram_directory "$OUT/$role-nvram" \
        -input_directory "$OUT/$role-inp" -snapshot_directory "$OUT/$role-snap" \
        -comm_localhost 127.0.0.1 -comm_localport "$port" \
        -comm_remotehost 127.0.0.1 -comm_remoteport "$rport" \
        -comm_framesync $master \
        -autoboot_script "$SCRIPT" -seconds_to_run "$SECONDS_TO_RUN" \
        -nothrottle -oslog >"$OUT/$role-mame.log" 2>&1
}
launch p1 "$P1_PORT" "$P2_PORT" 0 "$OUT/p1-fuzz.log" "$OUT/p1snaps" -comm_master "${VON_P1_COIN:-900}" "${VON_P1_START:-1500}" "${VON_P1_EXTRA:-} VON_FUZZ_COMM_ROLE=1" &
P1_PID=$!
launch p2 "$P2_PORT" "$P1_PORT" 1 "$OUT/p2-fuzz.log" "$OUT/p2snaps" "" "${VON_P2_COIN:-900}" "${VON_P2_START:-1500}" "${VON_P2_EXTRA:-} VON_FUZZ_COMM_ROLE=2" &
P2_PID=$!
wait "$P1_PID"; A=$?
wait "$P2_PID"; B=$?
echo "exit p1=$A p2=$B"
