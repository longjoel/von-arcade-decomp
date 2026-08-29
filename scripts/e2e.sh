#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

"$ROOT_DIR/scripts/test.sh"

printf 'Booting %s headlessly for one second...\n' "${VON_SET:-vonj}"
SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-dummy}" "$ROOT_DIR/scripts/run-twin.sh" \
    -window -video none -sound none -skip_gameinfo -seconds_to_run 1

printf 'End-to-end boot test passed.\n'
