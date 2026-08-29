#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if command -v brew >/dev/null 2>&1; then
    brew install mesa alsa-lib sdl2 sdl2_ttf pipewire
    printf 'Homebrew dependencies installed.\n'
else
    printf '%s\n' 'Homebrew not found; use your Linux distribution packages for MAME build/runtime dependencies.'
fi
printf 'Build remotely with %s/scripts/remote-build.sh, or locally with %s/scripts/build.sh.\n' "$ROOT_DIR" "$ROOT_DIR"
