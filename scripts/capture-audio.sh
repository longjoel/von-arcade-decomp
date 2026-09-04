#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"
require_mame
require_command date

SECONDS_TO_RUN="${VON_AUDIO_SECONDS:-30}"
OUTPUT="${1:-$ROOT_DIR/von/captures/vonj-audio-$(date -u +%Y%m%dT%H%M%SZ).wav}"
ROM_PATH="$(prepare_rom_path)"
trap 'cleanup_rom_path "$ROM_PATH"' EXIT

mkdir -p "$(dirname "$OUTPUT")"
echo "Capturing $SECONDS_TO_RUN emulated seconds to $OUTPUT"
MAME_AUDIO_ARGS=()
if [[ -n "${VON_AUDIO_SCRIPT:-}" ]]; then
    MAME_AUDIO_ARGS=(-autoboot_script "$VON_AUDIO_SCRIPT")
fi
MAME_LOG_ARGS=()
if [[ "${VON_MAME_LOG:-0}" == "1" ]]; then
    MAME_LOG_ARGS=(-log -oslog)
fi
SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-dummy}" \
SDL_AUDIODRIVER="${SDL_AUDIODRIVER:-dummy}" \
env $(runtime_env) "$MAME_BIN" vonj -rompath "$ROM_PATH" \
    -video none -sound sdl -samplerate "${VON_AUDIO_RATE:-44100}" \
    -wavwrite "$OUTPUT" -skip_gameinfo -nothrottle \
    -seconds_to_run "$SECONDS_TO_RUN" "${MAME_LOG_ARGS[@]}" "${MAME_AUDIO_ARGS[@]}"

echo "Wrote $OUTPUT"
