#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MAME_DIR="$ROOT_DIR/third_party/mame-master"
MAME_URL="https://github.com/mamedev/mame.git"
MAME_REF="569c5e9d4534cb244ff67ebbdb5f9fe69a465318"
PATCH_FILE="$ROOT_DIR/third_party/patches/0001-von-mame-support.patch"
TRACE_PATCH_FILE="$ROOT_DIR/third_party/patches/0002-von-sharc-tracing.patch"
VON_SUBTARGET="$ROOT_DIR/scripts/mame-von.lua"

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

for patch in "$PATCH_FILE" "$TRACE_PATCH_FILE"; do
    if git -C "$MAME_DIR" apply --reverse --check "$patch" >/dev/null 2>&1; then
        printf 'MAME patch already applied: %s\n' "$(basename "$patch")"
    elif git -C "$MAME_DIR" apply --check "$patch" >/dev/null 2>&1; then
        git -C "$MAME_DIR" apply "$patch"
        printf 'Applied MAME patch: %s\n' "$(basename "$patch")"
    else
        printf 'error: MAME patch does not apply cleanly: %s\n' "$patch" >&2
        exit 1
    fi
done

install -m 0644 "$VON_SUBTARGET" "$MAME_DIR/scripts/target/mame/von.lua"
printf 'Installed Virtual-On MAME subtarget.\n'
