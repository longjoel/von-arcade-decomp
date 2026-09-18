#!/usr/bin/env bash
# Explicit, instrumented original-ROM locomotion capture for Godot calibration.
# This never affects normal MAME play; it runs seven short headless sessions.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
out="${VON_LOCOMOTION_OUT:-$root/von/sandbox/locomotion-$stamp}"

exec env VON_SWEEP_OUT="$out" \
	VON_SWEEP_FRAMES="${VON_LOCOMOTION_FRAMES:-120}" \
	VON_SWEEP_JOBS="${VON_LOCOMOTION_JOBS:-1}" \
	"$root/bin/vonctl" sweep locomotion "$@"
