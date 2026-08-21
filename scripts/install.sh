#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
command -v brew >/dev/null 2>&1 || {
    printf '%s\n' 'error: Linuxbrew/Homebrew is required; install it before running this script' >&2
    exit 1
}

brew install mesa alsa-lib sdl2 sdl2_ttf pipewire
printf 'Dependencies installed. Build with %s/scripts/build.sh\n' "$ROOT_DIR"
