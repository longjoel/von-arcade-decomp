#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MAME_DIR="$ROOT_DIR/third_party/mame-master"
MAME_URL="https://github.com/mamedev/mame.git"
MAME_REF="569c5e9d4534cb244ff67ebbdb5f9fe69a465318"
PATCH_FILE="$ROOT_DIR/third_party/patches/0001-von-mame-support.patch"
COMM_DIAGNOSTICS_PATCH_FILE="$ROOT_DIR/third_party/patches/0010-von-communication-diagnostics.patch"
PATCHSET_MANIFEST="$ROOT_DIR/third_party/patches/patchsets.json"
VON_SUBTARGET="$ROOT_DIR/scripts/mame-von.lua"
PATCH_SET="${VON_MAME_PATCH_SET:-core}"

contains_text() {
    if command -v rg >/dev/null 2>&1; then
        rg -Fq "$1" "$2"
    else
        grep -Fq "$1" "$2"
    fi
}

patch_already_applied() {
    local patch_name
    patch_name="$(basename "$1")"
    case "$patch_name" in
        0002-von-sharc-tracing.patch)
            contains_text 'vonj_copro_fifo_trace_count' "$MAME_DIR/src/mame/sega/model2.cpp" ;;
        0014-von-geometry-response-tracing.patch)
            contains_text 'vonj_geometry_projection_response_trace_count' "$MAME_DIR/src/mame/sega/model2.cpp" ;;
        0015-von-sharc-20de1-tracing.patch)
            contains_text 'vonj_sharc_boot_trace_count' "$MAME_DIR/src/devices/cpu/sharc/sharc.cpp" ;;
        0016-von-sharc-interpreter-tracing.patch)
            contains_text 'VON_SHARC_DRC' "$MAME_DIR/src/mame/sega/model2.cpp" ;;
        0017-von-sharc-opcode-1f-state-tracing.patch)
            contains_text 'vonj_sharc_1f_state' "$MAME_DIR/src/devices/cpu/sharc/sharc.cpp" ;;
        0018-von-sharc-output-tracing.patch)
            contains_text 'vonj_sharc_output_trace_count' "$MAME_DIR/src/devices/cpu/sharc/sharcinternal.ipp" ;;
        0019-von-sharc-state-upload-tracing.patch)
            contains_text 'vonj_sharc_0d_state' "$MAME_DIR/src/devices/cpu/sharc/sharc.cpp" ;;
        0020-von-sharc-opcode-0c-output-tracing.patch)
            contains_text 'vonj_sharc_opcode0c_output_trace_count' "$MAME_DIR/src/devices/cpu/sharc/sharcinternal.ipp" ;;
        0021-von-sharc-opcode-22-compare-tracing.patch)
            contains_text 'vonj_sharc_22_compare_trace_count' "$MAME_DIR/src/devices/cpu/sharc/sharc.cpp" ;;
        0022-von-opcode-09-caller-tracing.patch)
            contains_text 'vonj_opcode_09_caller_trace_count' "$MAME_DIR/src/devices/cpu/i960/i960.cpp" ;;
        0023-von-sharc-reduction-tracing.patch)
            contains_text 'vonj_sharc_reduction_trace_count' "$MAME_DIR/src/devices/cpu/sharc/sharc.cpp" ;;
        0024-von-sharc-20d68-tracing.patch)
            contains_text 'vonj_sharc_20d68_trace_count' "$MAME_DIR/src/devices/cpu/sharc/sharc.cpp" ;;
        0025-von-sharc-scalar-tracing.patch)
            contains_text 'vonj_sharc_scalar_trace_count' "$MAME_DIR/src/devices/cpu/sharc/sharc.cpp" ;;
        0026-von-sharc-reciprocal-tracing.patch)
            contains_text 'vonj_sharc_reciprocal_trace_count' "$MAME_DIR/src/devices/cpu/sharc/sharc.cpp" ;;
        0027-von-sharc-drc-angle-tracing.patch)
            contains_text 'vonj_sharc_drc_angle' "$MAME_DIR/src/devices/cpu/sharc/sharcdrc.cpp" ;;
        0028-von-sharc-drc-float-special-cases.patch)
            contains_text 'canonical NaN writeback policy' "$MAME_DIR/src/devices/cpu/sharc/sharcdrc.cpp" ;;
        0029-von-sharc-expose-stky-state.patch)
            contains_text 'SHARC_STKY' "$MAME_DIR/src/devices/cpu/sharc/sharc.cpp" ;;
        0030-von-sharc-interpreter-angle-boundary-tracing.patch)
            contains_text 'vonj_sharc_interpreter_angle_trace_count' "$MAME_DIR/src/devices/cpu/sharc/sharc.cpp" ;;
        0031-von-sharc-40bit-header.patch)
            contains_text 'using wide_t = unsigned __int128;' "$MAME_DIR/src/devices/cpu/sharc/sharcfloat40.h" ;;
        0032-von-sharc-40bit-register-seam.patch)
            contains_text 'using SHARC_REG_EXTENDED = sharc_float40::register_value;' "$MAME_DIR/src/devices/cpu/sharc/sharc.h" ;;
        0033-von-sharc-drc-compound-abs-special-cases.patch)
            contains_text 'FABS(NaN) returns the canonical NaN' "$MAME_DIR/src/devices/cpu/sharc/sharcdrc.cpp" ;;
        0034-von-sharc-runtime-diagnostics.patch)
            contains_text 'VON_SHARC_TRACE_START' "$MAME_DIR/src/devices/cpu/sharc/sharc.cpp" ;;
        0006-von-texture-command-tracing.patch)
            contains_text 'vonj_texture_command' "$MAME_DIR/src/mame/sega/model2_v.cpp" ;;
        0007-von-geometry-object-tracing.patch)
            contains_text 'vonj_geometry_object_trace_count' "$MAME_DIR/src/mame/sega/model2_v.cpp" ;;
        0008-von-geometry-matrix-tracing.patch)
            contains_text 'vonj_geometry_matrix_trace_count' "$MAME_DIR/src/mame/sega/model2_v.cpp" ;;
        0009-von-geometry-polygon-tracing.patch)
            contains_text 'vonj_geometry_polygon_trace_count' "$MAME_DIR/src/mame/sega/model2_v.cpp" ;;
        0012-von-renderer-boundary-tracing.patch)
            contains_text 'vonj_video_frame_trace_count' "$MAME_DIR/src/mame/sega/model2_v.cpp" ;;
        0037-von-reconstructed-geometry-parser-tracing.patch)
            contains_text 'vonj_geometry_parse_trace_count < 4096' "$MAME_DIR/src/mame/sega/model2_v.cpp" ;;
        0038-von-reconstructed-geometry-opcode-tracing.patch)
            contains_text 'machine().time().as_double() > 30.0' "$MAME_DIR/src/mame/sega/model2_v.cpp" ;;
        *)
            return 1 ;;
    esac
}

command -v git >/dev/null 2>&1 || {
    printf 'error: git is required\n' >&2
    exit 1
}

if [[ ! -d "$MAME_DIR/.git" ]]; then
    mkdir -p "$(dirname "$MAME_DIR")"
    git clone "$MAME_URL" "$MAME_DIR"
fi

if [[ "$(git -C "$MAME_DIR" rev-parse HEAD)" != "$MAME_REF" ]]; then
    git -C "$MAME_DIR" checkout "$MAME_REF"
fi

mapfile -t PATCHES < <(python3 "$ROOT_DIR/von/tools/patchset_manifest.py" \
    "$PATCH_SET" --manifest "$PATCHSET_MANIFEST" --paths)
[[ "${#PATCHES[@]}" -gt 0 ]] || {
    printf 'error: patch profile %s resolved to no patches\n' "$PATCH_SET" >&2
    exit 1
}

CORE_APPLIED=0
if contains_text 'OPTION_COMM_MASTER' "$MAME_DIR/src/emu/emuopts.h" &&
   contains_text 'vonjdev' "$MAME_DIR/src/mame/mame.lst" &&
   contains_text 'void model2b_state::von' "$MAME_DIR/src/mame/sega/model2.cpp"; then
    CORE_APPLIED=1
fi
DIAGNOSTICS_APPLIED=0
if contains_text 'OPTION_COMM_DIAGNOSTICS' "$MAME_DIR/src/emu/emuopts.h" &&
   contains_text 'diagnostic_state' "$MAME_DIR/src/mame/sega/m2comm.cpp"; then
    DIAGNOSTICS_APPLIED=1
fi

REMAINING_PATCHES=()
for patch in "${PATCHES[@]}"; do
    [[ "$patch" == "$PATCH_FILE" && "$CORE_APPLIED" == 1 ]] && continue
    [[ "$patch" == "$COMM_DIAGNOSTICS_PATCH_FILE" && "$DIAGNOSTICS_APPLIED" == 1 ]] && continue
    REMAINING_PATCHES+=("$patch")
done
PATCHES=("${REMAINING_PATCHES[@]}")
if [[ "$CORE_APPLIED" == 1 && "$DIAGNOSTICS_APPLIED" == 1 ]]; then
    printf 'MAME Virtual-On core and communication diagnostics are already applied.\n'
fi

for patch in "${PATCHES[@]}"; do
    if git -C "$MAME_DIR" apply --recount --reverse --check "$patch" >/dev/null 2>&1; then
        printf 'MAME patch already applied: %s\n' "$(basename "$patch")"
    elif patch_already_applied "$patch"; then
        printf 'MAME patch already applied (marker): %s\n' "$(basename "$patch")"
    elif git -C "$MAME_DIR" apply --recount --check "$patch" >/dev/null 2>&1; then
        git -C "$MAME_DIR" apply --recount "$patch"
        printf 'Applied MAME patch: %s\n' "$(basename "$patch")"
    else
        printf 'error: MAME patch does not apply cleanly: %s\n' "$patch" >&2
        exit 1
    fi
done

install -m 0644 "$VON_SUBTARGET" "$MAME_DIR/scripts/target/mame/von.lua"
printf 'Installed Virtual-On MAME subtarget.\n'
