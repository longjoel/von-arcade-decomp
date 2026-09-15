#!/usr/bin/env bash
# Sweep the arcade twin-stick map: run the single-phase probe for a set of
# P1 action holds, then summarize each opponent's motion (travel, dyaw) so the
# true IN1/IN2 -> movement mapping can be read off. Runs captures in parallel.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_ROOT="${VON_SWEEP_OUT:-$ROOT_DIR/von/sandbox/sweep-$STAMP}"
JOBS="${VON_SWEEP_JOBS:-6}"
FRAMES="${VON_SWEEP_FRAMES:-180}"

# One entry per logical hold; commas separate actions held together.
PROBES=(
    "up" "down" "left" "right" "up2" "down2" "left2" "right2"
    "up,up2" "down,down2" "left,left2" "right,right2"
    "up,down2" "down,up2" "right,left2" "left,right2"
    "dash" "shot" "right_shot"
    "up,up2,dash" "up,up2,shot" "right,right2,dash"
)

mkdir -p "$OUT_ROOT"
printf 'sweep: %d probes -> %s (jobs=%d)\n' "${#PROBES[@]}" "$OUT_ROOT" "$JOBS"

run_one() {
    local probe="$1"
    local tag="${probe//,/+}"
    local out="$OUT_ROOT/$tag"
    VON_BOUT_OUT="$out" \
    VON_BOUT_PROGRAM=probe \
    VON_BOUT_PROBE="$probe" \
    VON_BOUT_PROBE_FRAMES="$FRAMES" \
    VON_BOUT_SECONDS=200 \
        "$ROOT_DIR/scripts/capture-bout.sh" > "$out.log" 2>&1 || echo "probe $probe failed" >&2
}

running=0
for probe in "${PROBES[@]}"; do
    run_one "$probe" &
    running=$((running + 1))
    if (( running >= JOBS )); then
        wait -n || true
        running=$((running - 1))
    fi
done
wait || true

python3 - "$OUT_ROOT" "$FRAMES" <<'PY'
import csv, math, os, sys
root = sys.argv[1]
frames = int(sys.argv[2])
base = 9600
print(f"{'probe':22s} {'travel':>8s} {'dx':>8s} {'dz':>8s} {'dyaw':>8s} {'n':>5s}")
for tag in sorted(os.listdir(root)):
    path = os.path.join(root, tag, "bout.csv")
    if not os.path.isfile(path):
        continue
    rows = {}
    for r in csv.DictReader(open(path)):
        rows[int(r["frame"])] = r
    fs = sorted(rows)
    if not fs:
        continue
    a = base - 1
    b = min(base + frames - 1, fs[-1])
    if a not in rows or b not in rows:
        continue
    x0, z0 = float(rows[a]["p1x"]), float(rows[a]["p1z"])
    x1, z1 = float(rows[b]["p1x"]), float(rows[b]["p1z"])
    dyaw = float(rows[b]["p1yaw"]) - float(rows[a]["p1yaw"])
    print(f"{tag:22s} {math.dist((x0,z0),(x1,z1)):8.2f} {x1-x0:8.2f} {z1-z0:8.2f} {dyaw:8.2f} {len(fs):5d}")
PY
