#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_DIR="$ROOT_DIR/config"
CONFIG_EXAMPLE="$CONFIG_DIR/remote-build.env.example"
CONFIG_LOCAL="$CONFIG_DIR/remote-build.local.env"

[[ -f "$CONFIG_EXAMPLE" ]] || { printf 'error: missing remote build example config: %s\n' "$CONFIG_EXAMPLE" >&2; exit 1; }
# shellcheck disable=SC1090
source "$CONFIG_EXAMPLE"
if [[ -f "$CONFIG_LOCAL" ]]; then
    # shellcheck disable=SC1090
    source "$CONFIG_LOCAL"
fi

REMOTE_HOST="${VON_REMOTE_HOST:-drone0}"
REMOTE_CHECKOUT="${VON_REMOTE_CHECKOUT:-/home/drone/von-arcade-decomp}"
BUILD_IMAGE="${VON_MAME_BUILD_IMAGE:-von-mame-build:ubuntu26.04}"
REMOTE_JOBS="${VON_REMOTE_JOBS:-$(nproc)}"

command -v ssh >/dev/null 2>&1 || { printf 'error: ssh is required\n' >&2; exit 1; }
command -v rsync >/dev/null 2>&1 || { printf 'error: rsync is required\n' >&2; exit 1; }
command -v scp >/dev/null 2>&1 || { printf 'error: scp is required\n' >&2; exit 1; }

printf 'Checking remote build host %s...\n' "$REMOTE_HOST"
ssh "$REMOTE_HOST" true || {
    printf 'error: SSH connection failed for %s\n' "$REMOTE_HOST" >&2
    exit 1
}
ssh "$REMOTE_HOST" "test -d '$REMOTE_CHECKOUT'" || {
    printf 'error: remote checkout does not exist: %s:%s\n' "$REMOTE_HOST" "$REMOTE_CHECKOUT" >&2
    exit 1
}
ssh "$REMOTE_HOST" 'command -v docker >/dev/null 2>&1' || {
    printf 'error: Docker is not available on %s\n' "$REMOTE_HOST" >&2
    exit 1
}
ssh "$REMOTE_HOST" "docker image inspect '$BUILD_IMAGE' >/dev/null 2>&1" || {
    printf 'error: Docker image not found on %s: %s\n' "$REMOTE_HOST" "$BUILD_IMAGE" >&2
    exit 1
}

printf 'Synchronizing build inputs (ROMs are not copied)...\n'
rsync -a "$ROOT_DIR/scripts/" "$REMOTE_HOST:$REMOTE_CHECKOUT/scripts/" || {
    printf 'error: failed to synchronize scripts\n' >&2; exit 1;
}
rsync -a --delete "$ROOT_DIR/third_party/patches/" "$REMOTE_HOST:$REMOTE_CHECKOUT/third_party/patches/" || {
    printf 'error: failed to synchronize patch inputs\n' >&2; exit 1
}
rsync -a "$ROOT_DIR/third_party/mame-master/src/mame/sega/m2comm.cpp" \
    "$REMOTE_HOST:$REMOTE_CHECKOUT/third_party/mame-master/src/mame/sega/m2comm.cpp" || {
    printf 'error: failed to synchronize communication diagnostics source\n' >&2; exit 1
}

printf 'Building MAME remotely in Docker...\n'
ssh "$REMOTE_HOST" "cd '$REMOTE_CHECKOUT' && VON_MAME_BUILD_IMAGE='$BUILD_IMAGE' JOBS='$REMOTE_JOBS' VON_MAME_PATCH_SET='${VON_MAME_PATCH_SET:-core}' ./scripts/build-mame-docker.sh" || {
    printf 'error: remote MAME build failed\n' >&2; exit 1
}

mkdir -p "$ROOT_DIR/bin"
TEMP_BINARY="$ROOT_DIR/bin/.von.remote.tmp"
rm -f "$TEMP_BINARY"
scp "$REMOTE_HOST:$REMOTE_CHECKOUT/third_party/mame-master/von" "$TEMP_BINARY" || {
    rm -f "$TEMP_BINARY"
    printf 'error: failed to copy the remote MAME binary\n' >&2
    exit 1
}
chmod +x "$TEMP_BINARY"
mv -f "$TEMP_BINARY" "$ROOT_DIR/bin/von"
printf 'Synchronized %s (remote host: %s)\n' "$ROOT_DIR/bin/von" "$REMOTE_HOST"
