#!/usr/bin/env bash
# Environment readiness report for agent sessions.
# Read-only: inspects, never installs or mutates. Exits 1 when a required
# tool is missing; advisory gaps are reported but do not fail.
set -uo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
failures=0
advisories=0

need() {
    if command -v "$1" >/dev/null 2>&1; then
        printf 'READY     %s\n' "$1"
    else
        printf 'MISSING   %s (required)\n' "$1"
        failures=$((failures + 1))
    fi
}

want() {
    if eval "$2" >/dev/null 2>&1; then
        printf 'READY     %s\n' "$1"
    else
        printf 'GAP       %s -- %s\n' "$1" "$3"
        advisories=$((advisories + 1))
    fi
}

need cc
need python3
need git

want "gh auth" "gh auth status" "push/fetch need a valid GitHub token"
want "docker" "docker info" "i960 image build needs the daemon"
want "sudo docker" "sudo -n docker info" "image build here needs sudo"
want "ssh drone0" "ssh -o BatchMode=yes -o ConnectTimeout=5 drone0 true" \
    "remote builds need drone0 reachability"
want "MAME binary" "test -x $ROOT_DIR/bin/von" "traces and smoke need bin/von"
want "staged ROMs" "test -d $ROOT_DIR/von/build/disasm/rompath/vonj" \
    "traces need staged ROMs"
want "attract coverage" "test -f $ROOT_DIR/von/build/attract-coverage/vonj-attract-60s.json" \
    "worklist regen needs the coverage report"
want "i960 toolchain" "command -v i960-elf-gcc" "only via docker/drone0 here"

printf 'required failures: %d, advisory gaps: %d\n' "$failures" "$advisories"
exit "$([ "$failures" -eq 0 ] && echo 0 || echo 1)"
