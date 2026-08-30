#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MAME_DIR="$ROOT_DIR/third_party/mame-master"
MAME_URL="https://github.com/mamedev/mame.git"
MAME_REF="569c5e9d4534cb244ff67ebbdb5f9fe69a465318"
PATCH_FILE="$ROOT_DIR/third_party/patches/0001-von-mame-support.patch"
COMM_DIAGNOSTICS_PATCH_FILE="$ROOT_DIR/third_party/patches/0010-von-communication-diagnostics.patch"
TRACE_PATCH_FILE="$ROOT_DIR/third_party/patches/0002-von-sharc-tracing.patch"
TEXTURE_TRACE_PATCH_FILE="$ROOT_DIR/third_party/patches/0003-von-texture-write-tracing.patch"
TEXTURE_SOURCE_TRACE_PATCH_FILE="$ROOT_DIR/third_party/patches/0004-von-texture-source-tracing.patch"
PALETTE_TRACE_PATCH_FILE="$ROOT_DIR/third_party/patches/0005-von-palette-tracing.patch"
TEXTURE_COMMAND_TRACE_PATCH_FILE="$ROOT_DIR/third_party/patches/0006-von-texture-command-tracing.patch"
FIRST_MATCH_TEXTURE_TRACE_PATCH_FILE="$ROOT_DIR/third_party/patches/0013-von-first-match-texture-command-tracing.patch"
GEOMETRY_OBJECT_TRACE_PATCH_FILE="$ROOT_DIR/third_party/patches/0007-von-geometry-object-tracing.patch"
GEOMETRY_MATRIX_TRACE_PATCH_FILE="$ROOT_DIR/third_party/patches/0008-von-geometry-matrix-tracing.patch"
GEOMETRY_POLYGON_TRACE_PATCH_FILE="$ROOT_DIR/third_party/patches/0009-von-geometry-polygon-tracing.patch"
RENDERER_TRACE_PATCH_FILE="$ROOT_DIR/third_party/patches/0012-von-renderer-boundary-tracing.patch"
PC_COVERAGE_PATCH_FILE="$ROOT_DIR/third_party/patches/0011-mame-lua-pc-coverage.patch"
VON_SUBTARGET="$ROOT_DIR/scripts/mame-von.lua"
PATCH_SET="${VON_MAME_PATCH_SET:-core}"

contains_text() {
    if command -v rg >/dev/null 2>&1; then
        rg -Fq "$1" "$2"
    else
        grep -Fq "$1" "$2"
    fi
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

case "$PATCH_SET" in
    core)
        PATCHES=("$PATCH_FILE" "$COMM_DIAGNOSTICS_PATCH_FILE" "$PC_COVERAGE_PATCH_FILE")
        ;;
    debug|all)
        PATCHES=("$PATCH_FILE" "$COMM_DIAGNOSTICS_PATCH_FILE" "$PC_COVERAGE_PATCH_FILE" "$TRACE_PATCH_FILE" "$TEXTURE_TRACE_PATCH_FILE" "$TEXTURE_SOURCE_TRACE_PATCH_FILE" "$PALETTE_TRACE_PATCH_FILE" "$TEXTURE_COMMAND_TRACE_PATCH_FILE" "$GEOMETRY_OBJECT_TRACE_PATCH_FILE" "$GEOMETRY_MATRIX_TRACE_PATCH_FILE" "$GEOMETRY_POLYGON_TRACE_PATCH_FILE" "$RENDERER_TRACE_PATCH_FILE")
        ;;
    texture-trace)
        PATCHES=("$PATCH_FILE" "$COMM_DIAGNOSTICS_PATCH_FILE" "$PC_COVERAGE_PATCH_FILE" "$TEXTURE_TRACE_PATCH_FILE" "$TEXTURE_SOURCE_TRACE_PATCH_FILE")
        ;;
    geometry-trace)
        PATCHES=("$PATCH_FILE" "$COMM_DIAGNOSTICS_PATCH_FILE" "$PC_COVERAGE_PATCH_FILE" "$GEOMETRY_OBJECT_TRACE_PATCH_FILE" "$GEOMETRY_MATRIX_TRACE_PATCH_FILE" "$RENDERER_TRACE_PATCH_FILE")
        ;;
    geometry-material)
        PATCHES=("$PATCH_FILE" "$COMM_DIAGNOSTICS_PATCH_FILE" "$PC_COVERAGE_PATCH_FILE" "$FIRST_MATCH_TEXTURE_TRACE_PATCH_FILE" "$GEOMETRY_OBJECT_TRACE_PATCH_FILE" "$GEOMETRY_MATRIX_TRACE_PATCH_FILE" "$RENDERER_TRACE_PATCH_FILE")
        ;;
    *)
        printf 'error: unknown VON_MAME_PATCH_SET=%s (expected core, texture-trace, geometry-trace, geometry-material, debug, or all)\n' "$PATCH_SET" >&2
        exit 1
        ;;
esac

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
