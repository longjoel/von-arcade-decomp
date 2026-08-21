#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MAME_DIR="$ROOT_DIR/third_party/mame-master"
MAME_BIN="${VON_MAME_BIN:-$MAME_DIR/von}"
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
    if compgen -G "$ROM_DIR/*.zip" >/dev/null; then
        printf '%s' "$ROM_DIR"
        return
    fi

    [[ -d "$ROM_DIR" ]] || die "ROM directory does not exist: $ROM_DIR"
    local staging="$ROOT_DIR/von/build/rompath"
    rm -rf "$staging"
    mkdir -p "$staging/vonj"
    cp -as "$ROM_DIR"/* "$staging/vonj/"
    printf '%s' "$staging"
}
