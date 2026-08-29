#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
require_mame

SET_NAME="${VON_SET:-vonj}"
P1_PORT="${VON_P1_PORT:-12340}"
P2_PORT="${VON_P2_PORT:-12341}"
ROM_PATH="$(prepare_rom_path)"
trap 'cleanup_rom_path "$ROM_PATH"' EXIT
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
TWIN_DIR="$CAPTURE_DIR/twin-$SET_NAME-$STAMP"

if command -v ss >/dev/null 2>&1; then
    ACTIVE_SOCKETS="$(ss -ltn 2>/dev/null || true)"
    [[ "$ACTIVE_SOCKETS" =~ :$P1_PORT[[:space:]] ]] && die "communication port already in use: $P1_PORT"
    [[ "$ACTIVE_SOCKETS" =~ :$P2_PORT[[:space:]] ]] && die "communication port already in use: $P2_PORT"
fi

mkdir -p "$TWIN_DIR/p1/cfg" "$TWIN_DIR/p1/nvram" "$TWIN_DIR/p1/inp" "$TWIN_DIR/p1/snap" \
    "$TWIN_DIR/p2/cfg" "$TWIN_DIR/p2/nvram" "$TWIN_DIR/p2/inp" "$TWIN_DIR/p2/snap"

MAME_ARGS=(-window -skip_gameinfo -verbose "$@")
COMM_DIAGNOSTIC_ARGS=()
[[ "${VON_COMM_DIAGNOSTICS:-0}" == 1 ]] && COMM_DIAGNOSTIC_ARGS=(-comm_diagnostics)
P1_LOG="$TWIN_DIR/p1/mame.log"
P2_LOG="$TWIN_DIR/p2/mame.log"
P1_PID=""
P2_PID=""

relay_log() {
    local label="$1"
    local logfile="$2"
    local line

    while IFS= read -r line; do
        printf '%s\n' "$line" >>"$logfile"
        case "$line" in
            M2COMM:*) printf '%s %s\n' "$label" "$line" ;;
        esac
    done
}

cleanup() {
    trap - EXIT INT TERM
    [[ -z "$P1_PID" ]] || kill "$P1_PID" 2>/dev/null || true
    [[ -z "$P2_PID" ]] || kill "$P2_PID" 2>/dev/null || true
    [[ -z "$P1_PID" ]] || wait "$P1_PID" 2>/dev/null || true
    [[ -z "$P2_PID" ]] || wait "$P2_PID" 2>/dev/null || true
    rm -f "socket.127.0.0.1:$P1_PORT" "socket.127.0.0.1:$P2_PORT"
    cleanup_rom_path "$ROM_PATH"
}
trap cleanup EXIT INT TERM

printf 'Starting cabinet P1 on comm port %s\n' "$P1_PORT"
printf 'Starting cabinet P2 on comm port %s\n' "$P2_PORT"
printf 'Twin capture directory: %s\n' "$TWIN_DIR"

env $(runtime_env) \
    stdbuf -oL -eL "$MAME_BIN" "$SET_NAME" \
        -rompath "$ROM_PATH" \
        -cfg_directory "$TWIN_DIR/p1/cfg" \
        -nvram_directory "$TWIN_DIR/p1/nvram" \
        -input_directory "$TWIN_DIR/p1/inp" \
        -snapshot_directory "$TWIN_DIR/p1/snap" \
        -comm_localhost 127.0.0.1 -comm_localport "$P1_PORT" \
        -comm_remotehost 127.0.0.1 -comm_remoteport "$P2_PORT" \
        -comm_framesync -comm_master "${COMM_DIAGNOSTIC_ARGS[@]}" "${MAME_ARGS[@]}" > >(relay_log P1 "$P1_LOG") 2>&1 &
P1_PID=$!

env $(runtime_env) \
    stdbuf -oL -eL "$MAME_BIN" "$SET_NAME" \
        -rompath "$ROM_PATH" \
        -cfg_directory "$TWIN_DIR/p2/cfg" \
        -nvram_directory "$TWIN_DIR/p2/nvram" \
        -input_directory "$TWIN_DIR/p2/inp" \
        -snapshot_directory "$TWIN_DIR/p2/snap" \
        -comm_localhost 127.0.0.1 -comm_localport "$P2_PORT" \
        -comm_remotehost 127.0.0.1 -comm_remoteport "$P1_PORT" \
        -comm_framesync "${COMM_DIAGNOSTIC_ARGS[@]}" "${MAME_ARGS[@]}" -sound none > >(relay_log P2 "$P2_LOG") 2>&1 &
P2_PID=$!

wait -n "$P1_PID" "$P2_PID"
