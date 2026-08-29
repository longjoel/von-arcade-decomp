#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
require_mame

# The diagnostic runner must use the rebuilt diagnostic binary. A normal
# Virtual-On binary can still establish the socket, which otherwise makes a
# stale build look like a protocol failure.
MAME_STRINGS="$(strings "$MAME_BIN" 2>/dev/null || true)"
if [[ "$MAME_STRINGS" != *comm_diagnostics* ]]; then
    die "MAME binary lacks -comm_diagnostics; rebuild the diagnostic MAME binary first"
fi

SET_NAME="${VON_SET:-vonj}"
SECONDS_TO_RUN="${VON_TWIN_SECONDS:-60}"
MATRIX="${VON_TWIN_MATRIX:-default}"
PREFLIGHT="${VON_TWIN_PREFLIGHT:-1}"
ROM_PATH="$(prepare_rom_path)"
trap 'cleanup_rom_path "$ROM_PATH"' EXIT
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_DIR="$CAPTURE_DIR/twin-diagnostic-$SET_NAME-$STAMP"
SCRIPT="$ROOT_DIR/von/tools/twin_diagnostic.lua"
mkdir -p "$OUT_DIR"

matches() {
    if command -v rg >/dev/null 2>&1; then
        rg -q "$1" "${@:2}"
    else
        grep -q -E "$1" "${@:2}"
    fi
}

case "$MATRIX" in
    default) CASES=("ff:ff") ;;
    targeted)
        CASES=("ff:ff")
        for bit in 0 1 2 3 4 5 6 7; do
            value=$(printf '%02x' $((0xff ^ (1 << bit))))
            CASES+=("$value:ff" "$value:$value")
        done
        ;;
    full)
        CASES=()
        for value in $(seq 0 255); do
            hex=$(printf '%02x' "$value")
            CASES+=("$hex:ff")
        done
        ;;
    *) die "VON_TWIN_MATRIX must be default, targeted, or full" ;;
esac

printf 'case,p1_sw3,p2_sw3,p1_link,p2_link,p1_stable,p2_stable,p1_battle_candidate,p2_battle_candidate,result,earliest_failure\n' > "$OUT_DIR/results.csv"
run_case() {
    local case_name="$1" p1_sw3="$2" p2_sw3="$3"
    local case_dir="$OUT_DIR/$case_name"
    local p1="$case_dir/p1" p2="$case_dir/p2"
    mkdir -p "$p1/cfg" "$p1/nvram" "$p1/inp" "$p1/snap" "$p2/cfg" "$p2/nvram" "$p2/inp" "$p2/snap"
    for cabinet in p1 p2; do
        local value="$p1_sw3"
        [[ "$cabinet" == p2 ]] && value="$p2_sw3"
        # MAME stores DIP state as a port value. The fields remain UNKNOWN in
        # the driver; this file only supplies a reproducible candidate value.
        cat > "$case_dir/$cabinet/cfg/$SET_NAME.cfg" <<EOF
<mameconfig version="10">
 <system name="default">
  <input>
   <port tag=":SW" type="DIPSWITCH" mask="ff" value="$value" />
  </input>
 </system>
</mameconfig>
EOF
    done
    local p1_log="$p1/mame.log" p2_log="$p2/mame.log"
    SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-dummy}" VON_TWIN_LOG="$p1/twin_diagnostic.lua.log" VON_TWIN_PREFLIGHT="$PREFLIGHT" VON_TWIN_ROLE=master env $(runtime_env) stdbuf -oL -eL "$MAME_BIN" "$SET_NAME" -rompath "$ROM_PATH" \
        -cfg_directory "$p1/cfg" -nvram_directory "$p1/nvram" -input_directory "$p1/inp" -snapshot_directory "$p1/snap" \
        -comm_localhost 127.0.0.1 -comm_localport 12340 -comm_remotehost 127.0.0.1 -comm_remoteport 12341 \
        -comm_framesync -comm_master -comm_diagnostics -autoboot_script "$SCRIPT" \
        -video none -sound none -skip_gameinfo -nothrottle -verbose -oslog > "$p1_log" 2>&1 & local p1_pid=$!
    SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-dummy}" VON_TWIN_LOG="$p2/twin_diagnostic.lua.log" VON_TWIN_PREFLIGHT="$PREFLIGHT" VON_TWIN_ROLE=slave env $(runtime_env) stdbuf -oL -eL "$MAME_BIN" "$SET_NAME" -rompath "$ROM_PATH" \
        -cfg_directory "$p2/cfg" -nvram_directory "$p2/nvram" -input_directory "$p2/inp" -snapshot_directory "$p2/snap" \
        -comm_localhost 127.0.0.1 -comm_localport 12341 -comm_remotehost 127.0.0.1 -comm_remoteport 12340 \
        -comm_framesync -comm_diagnostics -autoboot_script "$SCRIPT" \
        -video none -sound none -skip_gameinfo -nothrottle -verbose -oslog > "$p2_log" 2>&1 & local p2_pid=$!
    wait "$p1_pid" || true
    wait "$p2_pid" || true
    local p1_link=0 p2_link=0 p1_stable=0 p2_stable=0 p1_battle=0 p2_battle=0
    matches 'diag link-state=established' "$p1_log" && p1_link=1 || true
    matches 'diag link-state=established' "$p2_log" && p2_link=1 || true
    ((p1_link)) && ! matches 'diag link-state=failed' "$p1_log" && p1_stable=1 || true
    ((p2_link)) && ! matches 'diag link-state=failed' "$p2_log" && p2_stable=1 || true
    matches 'battle-screen-change' "$p1/twin_diagnostic.lua.log" 2>/dev/null && p1_battle=1 || true
    matches 'battle-screen-change' "$p2/twin_diagnostic.lua.log" 2>/dev/null && p2_battle=1 || true
    local result=fail stage=socket-setup
    if ((p1_link || p2_link)) && ! ((p1_stable && p2_stable)); then
        stage=link-stability
    elif ((p1_stable && p2_stable)); then
        stage=menu-synchronization
        if ((p1_battle && p2_battle)); then
            result=pass
            stage=none
        fi
    elif matches 'listen on socket|connect to socket|diag packet id=ff|diag packet id=fe' "$p1_log" "$p2_log"; then
        stage=handshake
    fi
    printf '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' "$case_name" "$p1_sw3" "$p2_sw3" "$p1_link" "$p2_link" "$p1_stable" "$p2_stable" "$p1_battle" "$p2_battle" "$result" "$stage" >> "$OUT_DIR/results.csv"
}

case_number=0
for pair in "${CASES[@]}"; do
    IFS=: read -r p1_sw3 p2_sw3 <<< "$pair"
    case_number=$((case_number + 1))
    run_case "case-$case_number" "$p1_sw3" "$p2_sw3"
done
printf 'Twin diagnostic results: %s\n' "$OUT_DIR/results.csv"
