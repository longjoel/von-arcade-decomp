#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MAME_DIR="$ROOT_DIR/third_party/mame-master"
MAME_BIN="${VON_MAME_BIN:-$ROOT_DIR/bin/von}"
ROM_DIR="${VON_ROM_DIR:-$ROOT_DIR/von/artifacts}"
CAPTURE_DIR="${VON_CAPTURE_DIR:-$ROOT_DIR/von/captures}"

die() {
    printf 'error: %s\n' "$*" >&2
    exit 1
}

require_command() {
    command -v "$1" >/dev/null 2>&1 || die "required command not found: $1"
}

brew_prefix() {
    require_command brew
    brew --prefix "$1"
}

brew_runtime_path() {
    command -v brew >/dev/null 2>&1 || return 0
    local paths
    paths="$(brew --prefix)/lib"
    for formula in sdl2_ttf sdl2-compat mesa alsa-lib pipewire; do
        if brew list --formula "$formula" >/dev/null 2>&1; then
            paths="$(brew --prefix "$formula")/lib:$paths"
        fi
    done
    printf '%s' "$paths"
}

require_mame() {
    [[ -x "$MAME_BIN" ]] || die "MAME is not built; run scripts/build.sh first"
}

prepare_rom_path() {
    [[ -d "$ROM_DIR" ]] || die "ROM directory does not exist: $ROM_DIR"
    local staging
    staging="$(mktemp -d "$ROOT_DIR/von/build/rompath.XXXXXX")"
    mkdir -p "$staging/vonj"
    find "$ROM_DIR" -maxdepth 1 -type f -print0 |
        while IFS= read -r -d '' rom; do
            ln -s "$rom" "$staging/vonj/$(basename "$rom")"
        done
    printf '%s' "$staging"
}

cleanup_rom_path() {
    [[ -n "${1:-}" && -d "$1" ]] && rm -rf -- "$1"
}

runtime_env() {
    local runtime
    runtime="$(brew_runtime_path)"
    if [[ -n "$runtime" ]]; then
        printf 'LD_LIBRARY_PATH=%s' "$runtime${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
    elif [[ -n "${LD_LIBRARY_PATH:-}" ]]; then
        printf 'LD_LIBRARY_PATH=%s' "$LD_LIBRARY_PATH"
    fi
}
