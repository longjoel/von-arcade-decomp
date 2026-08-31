#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
require_command python3
require_mame

cd "$ROOT_DIR"
python3 von/tools/test_recovered_runtime_math.py
python3 von/tools/test_recovered_audio_queue.py
python3 von/tools/test_recovered_audio_helpers.py
python3 von/tools/test_recovered_audio_queue_consumer.py
python3 von/tools/test_recovered_host_control.py
python3 von/tools/test_recovered_memory.py
python3 von/tools/test_recovered_geometry_service.py
python3 von/tools/test_recovered_text_control.py
python3 von/tools/test_recovered_text_video.py
python3 von/tools/test_summarize_mame_trace.py
python3 von/tools/test_export_geometry_triangle_build_gltf.py
python3 von/tools/test_export_geometry_frame_gltf.py
python3 von/tools/test_texture_palette.py
python3 von/tools/rom_audit.py
ROM_PATH="$(prepare_rom_path)"
trap 'cleanup_rom_path "$ROM_PATH"' EXIT

SYSTEM_LIST="$(env $(runtime_env) "$MAME_BIN" -listfull)"
for set_name in vonj vonu vonjdev; do
    [[ "$SYSTEM_LIST" =~ (^|$'\n')$set_name[[:space:]] ]] || die "$set_name driver is not present in the built target"
done

env $(runtime_env) "$MAME_BIN" vonj -rompath "$ROM_PATH" -validate

if [[ -f "$ROOT_DIR/von/build/i960/prototype-maincpu.bin" ]]; then
    env $(runtime_env) "$MAME_BIN" vonjdev -rompath "$ROM_PATH" -validate
fi

printf 'Tests passed.\n'
