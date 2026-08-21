#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MAME_DIR="$ROOT_DIR/third_party/mame-master"
MAME_URL="https://github.com/mamedev/mame.git"
MAME_REF="569c5e9d4534cb244ff67ebbdb5f9fe69a465318"
PATCH_FILE="$ROOT_DIR/third_party/patches/0001-von-mame-support.patch"

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

if git -C "$MAME_DIR" apply --reverse --check "$PATCH_FILE" >/dev/null 2>&1; then
    printf 'MAME patch already applied.\n'
elif git -C "$MAME_DIR" apply --check "$PATCH_FILE" >/dev/null 2>&1; then
    git -C "$MAME_DIR" apply "$PATCH_FILE"
    printf 'Applied project MAME patch.\n'
else
    printf 'error: MAME patch does not apply cleanly to %s\n' "$MAME_REF" >&2
    exit 1
fi
