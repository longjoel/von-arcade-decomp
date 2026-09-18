#!/usr/bin/env bash
# Launch the untouched original-ROM Virtual-On set for local play.
#
# No autoboot Lua, trace/capture hook, debugger, or headless-video is enabled.
# The only repository configuration is the keyboard-encoder twin-stick profile:
# W/A/S/D + Q/E on the left, I/J/K/L + U/O on the right.
#
# Extra MAME options pass through unchanged, for example:
#   scripts/play-original-clean.sh -fullscreen

set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# `vonctl run` only stages the private ROM files and gives MAME isolated
# cfg/nvram/input/snapshot directories. It does not attach instrumentation.
# Use the dedicated keyboard-encoder profile rather than the default x360 pad
# mapping. MAME's Tab menu can still override any binding for this run.
exec env VON_SET=vonj VON_CTRLR=keyboard_twinstick \
    "$root/bin/vonctl" run -window -skip_gameinfo "$@"
