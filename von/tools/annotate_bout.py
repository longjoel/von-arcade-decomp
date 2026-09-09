#!/usr/bin/env python3
"""Annotate one bout start-to-finish from a twin-capture geometry trace.

Reads vonj_geometry_matrix / vonj_geometry_object events, groups them
into frames, splits Temjin / foe / stage / projectile parts, and emits a
timestamped annotation: round bounds, dashes, jumps, weapon-fire events
(projectile OBAs appearing with trajectories), knockdowns, and freezes.

Detection constants come from the recovered player physics
(gravity 0.030/frame^2, jump vy 1.755, walk cap 3.50 u/f, dash cruise
4.20 u/f): jump apex ~~51 units, dash band ~~4 u/f sustained.
"""
from __future__ import annotations
import argparse
import json
import math
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_geometry_frame_gltf import MATRIX, OBJECT

TEMJIN = {'009e410d', '009e3f80', '009e43a8', '009e3c34', '009e3aa7',
          '009e3ecf', '009e2a84', '009e35b7', '009e2ea2', '009e30ab',
          '009e343a', '009e3588', '008964ba', '009e2f5d', '009e3300',
          '008ad656', '009e332f', '009e2cb1', '009e36c2'}
ROOT = '009e332f'
WALK_CAP = 3.50
DASH_BAND = (3.6, 6.0)
JUMP_APEX = 51.0
JUMP_MIN = 12.0


def load_frames(trace: Path):
    cur = None
    frames: dict[float, list] = {}
    with trace.open(errors="replace") as fh:
        for raw in fh:
            line = raw.rstrip()
            m = MATRIX.search(line)
            if m:
                cur = (tuple(float(x) for x in m.group(2).split(","))
                       + tuple(float(x) for x in m.group(3).split(",")))
                continue
            m = OBJECT.search(line)
            if m and int(m.group(6)) == 3 and m.group(7) == "polygon-rom":
                frames.setdefault(float(m.group(1)), []).append(
                    (m.group(4), cur))
    return frames


def load_frames_json(path: Path):
    raw = json.loads(path.read_text())
    return {float(t): v for t, v in raw.items()}


def chain_positions(snaps: list[list[list[float]]], gate: float = 8.0):
    """Greedy nearest-neighbour chains over per-frame position snapshots.

    Seeds from the fullest frame; steps forward then backward. Returns a
    list of chains, each a per-frame list of positions or None.
    """
    med_n = statistics.median(len(s) for s in snaps)
    si = min(range(len(snaps)), key=lambda i: abs(len(snaps[i]) - med_n))
    chains = [[p] for p in snaps[si]]

    def step(fi: int, forward: bool):
        cur = snaps[fi]
        used: set[int] = set()
        for c in chains:
            ref = c[-1] if forward else c[0]
            if ref is None:
                seq = reversed(c) if forward else iter(c)
                ref = next((p for p in seq if p is not None), None)
            best = None
            bd = gate
            if ref is not None:
                for j, p in enumerate(cur):
                    if j in used:
                        continue
                    d = math.sqrt(sum((ref[k] - p[k]) ** 2 for k in range(3)))
                    if d < bd:
                        bd = d
                        best = (j, p)
            if best is not None:
                if forward:
                    c.append(best[1])
                else:
                    c.insert(0, best[1])
                used.add(best[0])
            else:
                if forward:
                    c.append(None)
                else:
                    c.insert(0, None)

    for fi in range(si + 1, len(snaps)):
        step(fi, True)
    for fi in range(si - 1, -1, -1):
        step(fi, False)
    return chains


def survey_families(frames, width: int = 4, top: int = 10):
    """Top OBA-family prefixes by row count: which mechs are in this bout.

    Mech families vary by matchup (twin-run bouts used 00845/00851,
    Temjin bouts use 009e vs a foe family), so cpu mode cannot guess them.
    Returns [(prefix, rows)] sorted by rows desc.
    """
    counts: dict[str, int] = {}
    for objs in frames.values():
        for o in objs:
            fam = o[0][:width]
            counts[fam] = counts.get(fam, 0) + 1
    return sorted(counts.items(), key=lambda kv: -kv[1])[:top]


def mobile_centroid(chains, min_disp: float = 8.0, min_fill: int = 10):
    """Centroid track over chains that actually relocate (mech limbs).

    Static chains (stage architecture) are excluded by end-to-end
    displacement. Returns (track, n_chains) where track is a list of
    (frame_index, centroid, size). Empty input yields an empty track
    (a mech family absent from the bout is legal input, not a crash).
    """
    if not chains:
        return [], 0, []
    keep = []
    for c in chains:
        pts = [p for p in c if p is not None]
        if len(pts) >= min_fill and math.dist(pts[0], pts[-1]) > min_disp:
            keep.append(c)
    track = []
    for fi in range(len(chains[0])):
        pts = [c[fi] for c in keep if c[fi] is not None]
        if len(pts) > 5:
            med = [statistics.median(p[k] for p in pts) for k in range(3)]
            # Spatial outlier rejection: stage chunks that slipped past
            # the displacement filter sit tens of units from the mech.
            core = [p for p in pts if math.dist(p, med) < 20.0]
            if len(core) > 5:
                pts = core
            track.append((fi, [statistics.median(p[k] for p in pts)
                              for k in range(3)], len(pts)))
    return track, len(keep), keep


def small_family_chains(frames, ts, prefix4: str, t_max: float,
                        gate: float = 6.0, min_len: int = 8):
    """Tight chains for rare families (weapons, shots, impact flashes).

    Returns chains of (t, oba, pos) with per-frame single assignment.
    """
    perframe: dict[float, list] = {}
    for t in ts:
        if t > t_max:
            continue
        for o in frames[t]:
            if o[0].startswith(prefix4):
                perframe.setdefault(t, []).append((t, o[0], o[10:13]))
    chains: list[list] = []
    for t in sorted(perframe):
        used: set[int] = set()
        for r in perframe[t]:
            best = None
            bd = gate
            bi = -1
            for i, c in enumerate(chains):
                if c[-1][0] >= t or t - c[-1][0] > 0.5:
                    continue
                d = math.dist(c[-1][2], r[2])
                if d < bd:
                    bd = d
                    best = c
                    bi = i
            if best is not None and bi not in used:
                best.append(r)
                used.add(bi)
            else:
                chains.append([r])
    return [c for c in chains if len(c) >= min_len]


def estimate_yaw_track(frame_obas: list[list[tuple[str, list]]]):
    """Common-mode yaw + translation per frame from one rigid part cluster.

    Persistence alone does not imply rigidity: mech limbs easily clear an
    80%-presence bar while articulating 25u+, and the farthest-from-centroid
    "star" may be a projectile. So the rig is selected by rigidity, not
    persistence: candidate OBAs (present in >20% of frames, cap 160) are
    scored by pairwise-distance stability over sampled frames and grouped
    into rigidity-graph components (link <1.0u distance std). Components are
    tried largest-diameter-first (the stage spans ~100u, a torso block ~10u);
    the star is the most-rigid high-presence member and arms are members
    rigid to it (>=3u away for angular SNR, farthest-first, cap 24).

    A component is accepted only if its arms agree (median within-frame
    spread <=5 deg) and it is not blind (span >=2 deg whenever the scene's
    median part travel >=5u -- a screen-fixed HUD cluster reports zero yaw
    while the scene moves). Per-frame yaw is the median wrapped angle-delta
    versus the fullest-rig base frame, smoothed with a +-2-frame median.
    Returns (yaw_s, centers, c0, info) where info carries span_deg, n_refs,
    n_arms, spread_deg, yaw_trusted, star, global_travel, and per-component
    tried[] diagnostics. Refused rigs yield a translation-only track (yaw_s
    all zero, centers from the largest component) with yaw_trusted False --
    never a silent de-yaw.
    """
    n = len(frame_obas)
    fill: dict[str, int] = {}
    first_pos: dict[str, list] = {}
    for lst in frame_obas:
        for oba, pos in lst:
            fill[oba] = fill.get(oba, 0) + 1
            if oba not in first_pos:
                first_pos[oba] = list(pos)
    cand = sorted((o for o, k in fill.items() if k > 0.2 * n),
                  key=lambda o: -fill[o])[:160]
    info = {"span_deg": 0.0, "n_refs": 0, "n_arms": 0, "spread_deg": 0.0,
            "yaw_trusted": False, "star": None}
    if len(cand) < 3 or n < 2:
        return [0.0] * n, [None] * n, [0.0, 0.0, 0.0], info
    info["n_refs"] = len(cand)
    stride = max(1, n // 100)
    sample = range(0, n, stride)
    tracks: dict[str, list] = {o: [] for o in cand}
    for i in sample:
        pos = {oba: p for oba, p in frame_obas[i]}
        for o in cand:
            tracks[o].append(pos.get(o))

    def dist_std(a: str, b: str) -> float:
        ds = [math.dist(pa, pb) for pa, pb in zip(tracks[a], tracks[b])
              if pa is not None and pb is not None]
        return statistics.pstdev(ds) if len(ds) >= 3 else float("inf")

    pair: dict[tuple[str, str], float] = {}
    for i, a in enumerate(cand):
        for b in cand[i + 1:]:
            pair[tuple(sorted((a, b)))] = dist_std(a, b)

    def linked(a: str, b: str) -> bool:
        key = (a, b) if a < b else (b, a)
        return pair[key] < 1.0

    # Rigidity-graph components: a pitching torso block is 3D-rigid but
    # useless as a yaw rig, so prefer the largest-diameter component (the
    # stage spans ~100u, a torso block ~10u).
    base = {o: first_pos[o] for o in cand}
    rc = [sum(base[o][i] for o in cand) / len(cand) for i in range(3)]
    seen_c: set[str] = set()
    comps = []
    for o in cand:
        if o in seen_c:
            continue
        comp = [o]
        seen_c.add(o)
        queue = [o]
        while queue:
            cur = queue.pop()
            for p in cand:
                if p not in seen_c and linked(cur, p):
                    seen_c.add(p)
                    comp.append(p)
                    queue.append(p)
        comps.append(comp)

    def diameter(comp) -> float:
        best = 0.0
        for i, a in enumerate(comp):
            for b in comp[i + 1:]:
                best = max(best, math.dist(base[a], base[b]))
        return best

    def ang(dx: float, dz: float) -> float:
        return math.atan2(dx, dz)

    tr_all: dict[str, list] = {}
    for lst in frame_obas:
        for o, p in lst:
            tr_all.setdefault(o, []).append(p)
    trav = {o: max((math.dist(p, ps[0]) for p in ps), default=0.0)
            for o, ps in tr_all.items() if o in cand}
    glob_travel = statistics.median(trav.values())
    info["tried"] = []
    info["global_travel"] = round(glob_travel, 1)

    def try_comp(comp):
        """Rig tuple or None if the component cannot see camera yaw."""
        with_comp = {o: statistics.median(pair[tuple(sorted((o, p)))]
                                          for p in comp if p != o)
                     for o in comp}
        star = min(comp, key=lambda o: (with_comp[o], -fill[o]))
        arms = sorted((o for o in comp if o != star
                       and linked(star, o)
                       and math.dist(base[o], base[star]) >= 3.0),
                      key=lambda o: math.dist(base[o], base[star]),
                      reverse=True)[:24]
        diag = {"size": len(comp), "diameter": round(diameter(comp), 1),
                "star": star, "fam": star[:4],
                "travel": round(trav.get(star, 0.0), 1),
                "n_arms": len(arms)}
        if len(arms) < 3:
            diag["verdict"] = "few-arms"
            info["tried"].append(diag)
            return None
        sb = {oba: pos for oba, pos in frame_obas[bi_of([star] + arms)]}
        if star not in sb:
            diag["verdict"] = "no-base-frame"
            info["tried"].append(diag)
            return None
        base_angles = [(a, ang(sb[a][0] - sb[star][0], sb[a][2] - sb[star][2]))
                       for a in arms if a in sb]
        raw: list[float] = []
        spreads = []
        for lst in frame_obas:
            pos = {oba: p for oba, p in lst}
            ds = []
            if star in pos:
                for arm, ba in base_angles:
                    if arm in pos:
                        p, q = pos[star], pos[arm]
                        x = ang(q[0] - p[0], q[2] - p[2]) - ba
                        ds.append((x + math.pi) % (2 * math.pi) - math.pi)
            raw.append(statistics.median(ds) if ds else 0.0)
            if len(ds) >= 2:
                spreads.append(statistics.pstdev(ds))
        spread = math.degrees(statistics.median(spreads)) if spreads else 0.0
        yaw = [statistics.median(raw[max(0, i - 2):min(n, i + 3)])
               for i in range(n)]
        span = round(math.degrees(max(yaw) - min(yaw)), 1)
        diag["spread"] = round(spread, 1)
        diag["span"] = span
        if spread > 5.0:
            diag["verdict"] = "articulated"
            info["tried"].append(diag)
            return None  # 3D articulation (pitching torso), not common yaw
        if span < 2.0 and glob_travel >= 5.0:
            diag["verdict"] = "blind"
            info["tried"].append(diag)
            return None  # rig sees no rotation while the scene moves
        diag["verdict"] = "accepted"
        info["tried"].append(diag)
        return star, arms, base_angles, round(spread, 1), raw

    def bi_of(rig) -> int:
        # The base frame must contain the star; otherwise base angles are
        # undefined and the component is unusable.
        star0 = rig[0]
        return max(range(n),
                   key=lambda i: (any(o == star0 for o, _ in frame_obas[i]),
                                  sum(1 for o, _ in frame_obas[i]
                                      if o in rig)))

    big = sorted((c for c in comps if len(c) >= 4),
                 key=lambda c: (diameter(c), len(c)), reverse=True)
    pick = next((t for t in (try_comp(c) for c in big) if t), None)
    if pick is None:
        # No yaw rig: still track translation from the largest component so
        # callers get usable centers with yaw_trusted False.
        seed = max(comps, key=len) if comps else cand
        rig = list(seed)
        raw_yaw = [0.0] * n
    else:
        star, arms, base_angles, spread, raw_yaw = pick
        info.update({"star": star, "n_arms": len(arms),
                     "spread_deg": spread})
        rig = [star] + arms
        info["yaw_trusted"] = True
    bi = bi_of(rig)
    sb = {oba: pos for oba, pos in frame_obas[bi]}
    in_base = [o for o in rig if o in sb]
    c0 = ([sum(sb[o][i] for o in in_base) / len(in_base) for i in range(3)]
          if in_base else list(rc))
    centers: list = []
    for lst in frame_obas:
        pos = {oba: p for oba, p in lst}
        present = [pos[o] for o in rig if o in pos]
        c = ([sum(p[i] for p in present) / len(present) for i in range(3)]
             if present else None)
        centers.append(c)
    # Fill center gaps from neighbours so translation cannot snap to c0.
    last = None
    for i, c in enumerate(centers):
        if c is None:
            centers[i] = last
        else:
            last = c
    nxt = None
    for i in range(n - 1, -1, -1):
        if centers[i] is None:
            centers[i] = nxt
        else:
            nxt = centers[i]
    if any(c is None for c in centers):
        centers = [list(c0)] * n
    yaw_s = []
    for i in range(n):
        lo, hi = max(0, i - 2), min(n, i + 3)
        yaw_s.append(statistics.median(raw_yaw[lo:hi]))
    info["span_deg"] = round(math.degrees(max(yaw_s) - min(yaw_s)), 1)
    return yaw_s, centers, c0, info


def destab(pos, yaw: float, c, c0):
    """Inverse-stabilize one position: subtract frame centroid, de-yaw, rebase."""
    rx, ry, rz = pos[0] - c[0], pos[1] - c[1], pos[2] - c[2]
    cy, sy = math.cos(-yaw), math.sin(-yaw)
    return [rx * cy + rz * sy + c0[0], ry + c0[1],
            -rx * sy + rz * cy + c0[2]]


def fill_short_gaps(chains, max_gap: int = 2):
    """Linearly interpolate None gaps of <= max_gap frames in place.

    Static-hold through cull gaps: short dropouts keep the chain (and any
    centroid/speed derived from it) instead of breaking it.
    """
    for c in chains:
        i = 0
        while i < len(c):
            if c[i] is not None:
                i += 1
                continue
            j = i
            while j < len(c) and c[j] is None:
                j += 1
            gap = j - i
            if 0 < gap <= max_gap and i > 0 and j < len(c):
                a, b = c[i - 1], c[j]
                for k in range(gap):
                    f = (k + 1) / (gap + 1)
                    c[i + k] = [a[d] + (b[d] - a[d]) * f for d in range(3)]
            i = j
    return chains


def oba_first_appearances(frames, ts, pred):
    """Geometry half of a per-unit state table.

    A newly loaded part overlay (an OBA never seen before in this bout) is
    a new animation state; presence flicker of known OBAs is just culling
    and is ignored. Returns (transitions, segments) where transitions are
    (t, new_oba) first sightings and segments carry the cumulative OBA
    inventory between consecutive first appearances.
    """
    seen: set[str] = set()
    transitions = []
    for t in ts:
        for o in frames[t]:
            oba = o[0]
            if pred(oba) and oba not in seen:
                seen.add(oba)
                transitions.append((t, oba))
    segments = []
    bounds = [t for t, _ in transitions] + ([ts[-1]] if ts else [])
    inv: set[str] = set()
    ti = 0
    for si in range(len(bounds) - 1):
        while ti < len(transitions) and transitions[ti][0] <= bounds[si]:
            inv.add(transitions[ti][1])
            ti += 1
        segments.append({"t0": bounds[si], "t1": bounds[si + 1],
                         "obas": sorted(inv)})
    return transitions, segments


def stabilize_json_frames(frames, ts):
    """De-yaw/de-translate a frames-JSON dict in place-format. Returns info."""
    fob = [[(e[0], list(e[10:13])) for e in frames[t]] for t in ts]
    yaw_s, centers, c0, info = estimate_yaw_track(fob)
    for t, yw, c in zip(ts, yaw_s, centers):
        frames[t] = [e[:10] + destab(list(e[10:13]), yw, c, c0)
                     for e in frames[t]]
    return info


def annotate_cpu_demo(frames, a_prefix: str, b_prefix: str,
                      small_fams: list[str]):
    """Annotate a CPU-vs-CPU demo window. Returns (summary, events).

    Raises ValueError naming any mech prefix that matches no OBAs: mech
    families are matchup-specific, so a silent empty track would only
    produce a nonsense annotation.
    """
    ts = sorted(frames)
    for side, prefix in (("mech-a", a_prefix), ("mech-b", b_prefix)):
        if not any(o[0].startswith(prefix)
                   for objs in frames.values() for o in objs):
            present = ", ".join(f"{fam}:{n}" for fam, n
                                in survey_families(frames))
            raise ValueError(
                f"{side} prefix {prefix!r} matches no OBAs in this trace. "
                f"Present families: {present}. Pass --mech-a/--mech-b for "
                f"this matchup.")
    stab_info = stabilize_json_frames(frames, ts)
    snaps_a = [[o[10:13] for o in frames[t]
                if o[0].startswith(a_prefix)] for t in ts]
    snaps_b = [[o[10:13] for o in frames[t]
                if o[0].startswith(b_prefix)] for t in ts]
    chains_a = fill_short_gaps(chain_positions(snaps_a))
    chains_b = fill_short_gaps(chain_positions(snaps_b))
    track_a, n_a, keep_a = mobile_centroid(chains_a)
    track_b, n_b, _ = mobile_centroid(chains_b, min_disp=4.0)
    pos_a = {ts[fi]: p for fi, p, _ in track_a}
    pos_b = {ts[fi]: p for fi, p, _ in track_b}
    all_t = sorted(set(pos_a) | set(pos_b))

    def near(pos, t):
        return pos[min(pos, key=lambda k: abs(k - t))]

    events = []
    if track_a:
        t0 = ts[track_a[0][0]]
        events.append({"t": t0, "event": "combat_window_start",
                       "detail": f"mech {a_prefix} mobile "
                       f"({n_a} chains), mech {b_prefix} ({n_b} chains)"})
    # Dash candidates: sustained runs where the FASTEST member chain
    # exceeds 2x its median (limbs dash; the centroid lags and would hide
    # them). Runs >= 6 frames; single-frame spikes are membership noise.
    if keep_a and len(ts) > 4:
        spd = []
        for fi in range(len(ts) - 1):
            dt = ts[fi + 1] - ts[fi]
            best = 0.0
            for c in keep_a:
                if c[fi] is not None and c[fi + 1] is not None and dt > 0:
                    best = max(best, math.dist(c[fi], c[fi + 1]) / dt)
            spd.append((ts[fi + 1], best))
        med = statistics.median(s for _, s in spd)
        run = []

        def flush():
            if len(run) >= 6:
                events.append({"t": run[0][0], "event": "dash_candidate",
                               "detail": f"{len(run)} frames, "
                               f"peak={max(x[1] for x in run):.1f} u/s"})

        for t, s in spd:
            if s > max(2.0 * med, 8.0):
                run.append((t, s))
            else:
                flush()
                run = []
        flush()
    # Small-family bursts: classify by own motion signature plus distance
    # to the nearer mech (centroids carry chain-membership noise, so the
    # label keys off hover-vs-travel, not exact spawn distance).
    for fam in small_fams:
        for c in small_family_chains(frames, ts, fam, all_t[-1] if all_t else 0):
            p0, p1 = c[0][2], c[-1][2]
            travel = math.dist(p0, p1)
            span = c[-1][0] - c[0][0]
            d0 = min(math.dist(p0, near(pos_a, c[0][0])) if pos_a else 1e9,
                     math.dist(p0, near(pos_b, c[0][0])) if pos_b else 1e9)
            if travel > 15:
                kind = "projectile_burst"
            elif d0 < 12 and span > 1.0:
                kind = "ordnance_linger"
            else:
                kind = "ambient_burst"
            events.append({"t": c[0][0], "event": kind,
                           "detail": f"fam={fam} len={len(c)} "
                           f"travel={travel:.1f}u span={span:.1f}s "
                           f"near_mech={d0:.1f}u"})
    # Bout end: mech-A family unloads (scene cut to next bout), not a count
    # spike -- wreckage shares the family prefix, so counts stay flat.
    counts = [(t, sum(1 for o in frames[t]
                     if o[0].startswith(a_prefix))) for t in ts]
    med_c = statistics.median(n for _, n in counts)
    for t, n in counts:
        if n < 0.5 * med_c:
            events.append({"t": t, "event": "bout_end_cut",
                           "detail": f"mech {a_prefix} count {n} "
                           f"(median {med_c:.0f}): scene cut"})
            break
    # Geometry half of the per-unit state tables: newly loaded part
    # overlays per mech, with cumulative-inventory segments.
    pose_segments = {}
    for tag, prefix in (("a", a_prefix), ("b", b_prefix)):
        tr, segs = oba_first_appearances(frames, ts,
                                         lambda o, p=prefix: o.startswith(p))
        pose_segments[tag] = segs
        for t, oba in tr:
            events.append({"t": t, "event": "state_change",
                           "detail": f"mech {prefix} new overlay oba={oba}"})
    events.sort(key=lambda e: e["t"])
    summary = {"window": [ts[0], ts[-1]], "frames": len(ts),
               "mech_a_chains": n_a, "mech_b_chains": n_b,
               "a_points": len(track_a), "b_points": len(track_b),
               "stabilization": stab_info, "pose_segments": pose_segments}
    return summary, events


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--trace", type=Path, required=False, default=None)
    p.add_argument("--frames-json", type=Path, required=False, default=None)
    p.add_argument("--mode", choices=["temjin", "cpu"], default="temjin")
    p.add_argument("--mech-a", default="00845")
    p.add_argument("--mech-b", default="00851")
    p.add_argument("--small-fams", nargs="*", default=["0089", "008a"])
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    if a.mode == "cpu":
        if a.frames_json is None:
            p.error("--mode cpu needs --frames-json")
        frames = load_frames_json(a.frames_json)
        ts = sorted(frames)
        print(f"frames: {len(ts)} span: {ts[0]:.2f}-{ts[-1]:.2f}")
        try:
            summary, events = annotate_cpu_demo(frames, a.mech_a, a.mech_b,
                                                a.small_fams)
        except ValueError as e:
            p.error(str(e))
        out = {"summary": summary, "events": events}
        a.output.write_text(json.dumps(out, indent=1) + "\n")
        for e in events:
            print(f"{e['t']:8.3f}  {e['event']:15s} {e['detail']}")
        print(f"wrote {a.output} ({len(events)} events)")
        return 0
    if a.trace is None:
        p.error("--mode temjin needs --trace")
    frames = load_frames(a.trace)
    ts = sorted(frames)
    print(f"frames: {len(ts)} span: {ts[0]:.2f}-{ts[-1]:.2f}")
    fob = [[(o, list(m[9:12])) for o, m in frames[t] if m is not None]
           for t in ts]
    yaw_s, centers, c0, stab_info = estimate_yaw_track(fob)
    for t, yw, c in zip(ts, yaw_s, centers):
        frames[t] = [(o, m if m is None else
                      tuple(m[:9]) + tuple(destab(list(m[9:12]), yw, c, c0)))
                     for o, m in frames[t]]
    print(f"stabilization: trusted={stab_info['yaw_trusted']} "
          f"span={stab_info['span_deg']}deg arms={stab_info['n_arms']} "
          f"spread={stab_info['spread_deg']}deg star={stab_info['star']}")

    rows = []
    for t in ts:
        objs = [(o, m) for o, m in frames[t] if m is not None]
        by_oba = {}
        for o, m in objs:
            by_oba.setdefault(o, m)
        root = by_oba.get(ROOT)
        foe = [m[9:12] for o, m in objs if o.startswith("00a6")]
        proj = sorted({o for o, m in objs
                       if o not in TEMJIN and not o.startswith("00a6")
                       and not o.startswith("0091") and o != "0084553f"})
        rows.append({"t": t, "root": root[9:12] if root else None,
                     "foe": ([sum(p[i] for p in foe) / len(foe)
                              for i in range(3)] if foe else None),
                     "proj": proj})

    have = [r for r in rows if r["root"]]
    print(f"frames with temjin root: {len(have)}/{len(rows)}")
    # Speed via finite differences on root translation.
    for prev, cur_ in zip(have, have[1:]):
        dt = cur_["t"] - prev["t"]
        d = math.sqrt(sum((cur_["root"][i] - prev["root"][i]) ** 2
                          for i in range(3)))
        cur_["speed"] = d / dt if dt > 0 else 0.0
    have[0]["speed"] = 0.0
    base_y = min(r["root"][1] for r in have)
    for r in have:
        r["height"] = r["root"][1] - base_y

    events = []
    events.append({"t": have[0]["t"], "event": "round_window_start",
                   "detail": f"temjin root present, {len(have)} rooted frames"})
    # Dash runs: speed in dash band, >= 8 consecutive rooted frames.
    run = []
    for r in have:
        if DASH_BAND[0] <= r["speed"] <= DASH_BAND[1]:
            run.append(r)
        else:
            if len(run) >= 8:
                events.append({"t": run[0]["t"], "event": "dash",
                               "detail": f"{len(run)} frames, "
                               f"peak={max(x['speed'] for x in run):.2f} u/f"})
            run = []
    if len(run) >= 8:
        events.append({"t": run[0]["t"], "event": "dash",
                       "detail": f"{len(run)} frames"})
    # Jumps: height excursions above JUMP_MIN.
    air = []
    for r in have:
        if r["height"] >= JUMP_MIN:
            air.append(r)
        else:
            if air:
                apex = max(x["height"] for x in air)
                events.append({"t": air[0]["t"], "event": "jump",
                               "detail": f"{len(air)} frames, apex={apex:.1f}u "
                               f"(physics predicts ~{JUMP_APEX:.0f}u)"})
                air = []
    if air:
        events.append({"t": air[0]["t"], "event": "jump",
                       "detail": f"{len(air)} frames (window ends airborne)"})
    # Weapon fire: projectile OBA sets appearing per frame.
    prev_set: set = set()
    for r in rows:
        cur_set = set(r["proj"])
        for oba in sorted(cur_set - prev_set):
            events.append({"t": r["t"], "event": "projectile_on",
                           "detail": f"oba={oba}"})
        for oba in sorted(prev_set - cur_set):
            events.append({"t": r["t"], "event": "projectile_off",
                           "detail": f"oba={oba}"})
        prev_set = cur_set
    # Knockdown heuristic: root height collapses while speed is low after
    # having been airborne or fast (a fall, not a landing: landing keeps
    # height ~0 with control; knockdown pins it with a preceding spike).
    # Reported as candidates with peak prior speed for review.
    # Freeze: consecutive rooted frames with ~zero root displacement.
    still = 0
    for prev, cur_ in zip(have, have[1:]):
        d = math.sqrt(sum((cur_["root"][i] - prev["root"][i]) ** 2
                          for i in range(3)))
        if d < 0.05:
            still += 1
        else:
            if still >= 30:
                events.append({"t": prev["t"], "event": "freeze_end",
                               "detail": f"held {still} frames"})
            still = 0
    events.append({"t": have[-1]["t"], "event": "round_window_end",
                   "detail": "temjin root last present"})
    events.sort(key=lambda e: e["t"])
    speeds = [r["speed"] for r in have]
    tframes = {t: [(o, None) for o, m in frames[t]] for t in ts}
    _, temjin_segs = oba_first_appearances(tframes, ts, lambda o: o in TEMJIN)
    summary = {"trace": str(a.trace), "frames": len(ts),
               "span": [ts[0], ts[-1]],
               "rooted_frames": len(have),
               "peak_speed": round(max(speeds), 2),
               "mean_speed": round(statistics.mean(speeds), 3),
               "peak_height": round(max(r["height"] for r in have), 1),
               "foe_frames": sum(1 for r in rows if r["foe"]),
               "stabilization": stab_info,
               "pose_segments": {"temjin": temjin_segs}}
    out = {"summary": summary, "events": events}
    a.output.write_text(json.dumps(out, indent=1) + "\n")
    for e in events:
        print(f"{e['t']:8.3f}  {e['event']:15s} {e['detail']}")
    print(f"wrote {a.output} ({len(events)} events)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
