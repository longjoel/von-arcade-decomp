#!/usr/bin/env bash
# Deterministic versus-bout telemetry capture (gameplay parity oracle).
#
# Boots single-cabinet 2P versus, drives the scripted P1 program from
# sandbox_versus.lua with electrical-level inputs so shots/dashes register,
# and writes a per-frame work-RAM telemetry CSV (positions, heading, both
# working HP, weapon timers, round/state) that the Godot replay-diff consumes.
#
# Not a human capture: P1 is fully scripted, so runs are byte-reproducible.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${VON_BOUT_OUT:-$ROOT_DIR/von/captures/bout-$(date -u +%Y%m%dT%H%M%SZ)}"
SECONDS_TO_RUN="${VON_BOUT_SECONDS:-220}"

mkdir -p "$OUT_DIR"

VON_SANDBOX_OUT="$OUT_DIR" \
VON_SANDBOX_SECONDS="$SECONDS_TO_RUN" \
VON_SANDBOX_ACTIVE_LEVELS=1 \
VON_SANDBOX_FREEZE="${VON_BOUT_FREEZE:-1}" \
VON_SANDBOX_PROGRAM="${VON_BOUT_PROGRAM:-default}" \
VON_SANDBOX_WEAPON_CASE="${VON_BOUT_WEAPON_CASE:-both}" \
VON_SANDBOX_TELEMETRY="$OUT_DIR/bout.csv" \
    "$ROOT_DIR/scripts/sandbox-versus.sh"

printf 'bout telemetry: %s\n' "$OUT_DIR/bout.csv"
