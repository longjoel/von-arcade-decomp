#!/usr/bin/env python3
"""Contract tests for annotate_bout stabilization + state math (synthetic)."""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from annotate_bout import (annotate_cpu_demo, destab, estimate_yaw_track,
                           fill_short_gaps, mobile_centroid,
                           oba_first_appearances, survey_families)


def rot_y(phi, p):
    c, s = math.cos(phi), math.sin(phi)
    x, y, z = p
    return [x * c + z * s, y, -x * s + z * c]


def rig(phimax_deg=66.0, drift=(1.5, -0.5, 0.8), n=12, decoy=False):
    pts = {
        "star": [40.0, 0.0, 5.0],
        "arm1": [10.0, 2.0, 30.0],
        "arm2": [-15.0, -3.0, 20.0],
        "arm3": [5.0, 8.0, -25.0],
        "arm4": [-30.0, 1.0, -10.0],
    }
    frames, truth = [], []
    for i in range(n):
        phi = math.radians(phimax_deg * i / (n - 1))
        d = [drift[k] * i for k in range(3)]
        truth.append(phi)
        lst = [(o, [rot_y(phi, p)[k] + d[k] for k in range(3)])
               for o, p in pts.items()]
        if decoy:
            # Persistent but non-rigid interloper (mech limb / projectile).
            lst.append(("decoy", [30.0 * math.sin(i), 5.0 * i, -20.0 + i]))
        frames.append(lst)
    return frames, truth


def main() -> int:
    frames, truth = rig()
    yaw_s, centers, c0, info = estimate_yaw_track(frames)
    assert info["yaw_trusted"], info
    assert info["n_arms"] == 4, info
    assert info["spread_deg"] < 1.0, info
    assert info["span_deg"] == 54.0, info  # +-2 median edge bias on a ramp
    mid = len(frames) // 2
    err = abs((yaw_s[mid] - (truth[mid] - truth[0]) + math.pi)
              % (2 * math.pi) - math.pi)
    assert err < 1e-9, (yaw_s[mid], truth[mid])
    p0 = {o: p for o, p in frames[0]}
    # Exact collapse mid-window; edge frames carry +-2 median smooth bias.
    for lst, yw, c in list(zip(frames, yaw_s, centers))[2:-2]:
        for o, p in lst:
            assert math.dist(destab(p, yw, c, c0), p0[o]) < 1e-6, o
    # Rigid shape preserved on every frame.
    d0 = {(a, b): math.dist(p0[a], p0[b]) for a in p0 for b in p0}
    for lst, yw, c in zip(frames, yaw_s, centers):
        q = {o: destab(p, yw, c, c0) for o, p in lst}
        for a in q:
            for b in q:
                assert abs(math.dist(q[a], q[b]) - d0[(a, b)]) < 1e-9, (a, b)

    # A persistent moving decoy must not become star or arm, and yaw stays
    # accurate mid-window.
    frames, truth = rig(decoy=True)
    yaw_s, centers, c0, info = estimate_yaw_track(frames)
    assert info["yaw_trusted"], info
    assert info["star"] != "decoy", info
    err = abs((yaw_s[mid] - (truth[mid] - truth[0]) + math.pi)
              % (2 * math.pi) - math.pi)
    assert err < 1e-9, (yaw_s[mid], truth[mid])

    # Nothing rigid: explicit translation-only fallback, never a fake de-yaw.
    import random
    rng = random.Random(7)
    soup = [[(f"p{k}", [rng.uniform(-50, 50) for _ in range(3)])
             for k in range(6)] for _ in range(10)]
    yaw_s, centers, c0, info = estimate_yaw_track(soup)
    assert not info["yaw_trusted"], info
    assert all(y == 0.0 for y in yaw_s), yaw_s
    assert all(c is not None for c in centers), centers

    # Screen-fixed cluster plus a moving scene: the blind rig is refused even
    # though its arms agree perfectly.
    hud = [(f"hud{k}", [float(k * 10), 0.0, 0.0]) for k in range(5)]
    blind = []
    for i in range(12):
        lst = list(hud)
        for k in range(5):
            lst.append((f"mob{k}",
                        [100.0 + 8.0 * i + k, 0.0, 50.0 + k * 7.0]))
        blind.append(lst)
    yaw_s, centers, c0, info = estimate_yaw_track(blind)
    assert not info["yaw_trusted"], info
    assert all(y == 0.0 for y in yaw_s), yaw_s
    assert all(v["verdict"] != "accepted" for v in info["tried"]), info

    # Gap filling: <=2 interpolated, longer/edge gaps kept.
    chains = [[[0.0, 0.0, 0.0], None, None, [3.0, 0.0, 0.0], None, None,
               None, [7.0, 0.0, 0.0]],
              [[0.0, 0.0, 0.0], None, [2.0, 0.0, 0.0]]]
    fill_short_gaps(chains)
    assert chains[0][1] == [1.0, 0.0, 0.0], chains[0]
    assert chains[0][2] == [2.0, 0.0, 0.0], chains[0]
    assert chains[0][4] is None and chains[0][6] is None, chains[0]
    assert chains[1][1] == [1.0, 0.0, 0.0], chains[1]

    # First appearances: cull flicker ignored, inventory is cumulative.
    fr = {0.0: [("a",), ("b",)], 1.0: [("a",)], 2.0: [("a",), ("c",)],
          3.0: [("b",), ("c",)]}
    ts = sorted(fr)
    tr, segs = oba_first_appearances(fr, ts, lambda o: True)
    assert [o for _, o in tr] == ["a", "b", "c"], tr
    assert tr[2][0] == 2.0, tr
    assert segs[-1]["obas"] == ["a", "b", "c"], segs
    assert segs[0] == {"t0": 0.0, "t1": 0.0, "obas": ["a", "b"]}, segs[0]
    # Registry consistency: every TEMJIN-set OBA is registered, families
    # referenced by the annotator exist in the registry.
    import json
    from annotate_bout import ROOT, TEMJIN
    reg = json.loads((Path(__file__).resolve().parent.parent
                      / "oba_registry.json").read_text())
    assert set(TEMJIN) <= set(reg["parts"]), "TEMJIN set drifts from registry"
    assert reg["parts"][ROOT]["role"] == "root", ROOT
    for fam in ("009e", "00a6", "0084", "0085", "0091", "0093"):
        assert fam in reg["families"], fam
        assert reg["families"][fam]["role"], fam

    # Empty chains are legal input (absent mech family), never a crash.
    assert mobile_centroid([]) == ([], 0, []), mobile_centroid([])

    # Synthetic two-mech frames: entries need oba + 12 numbers so [10:13]
    # is the position.
    def entry(oba, x, y, z):
        return [oba] + [0.0] * 9 + [x, y, z] + [0.0] * 2

    cpu_frames = {float(i): [entry("00845a", 2.0 * i, 0.0, 0.0),
                             entry("009e01", 100.0 - 1.5 * i, 0.0, 0.0),
                             entry("0091aa", 500.0, 0.0, 0.0)]
                  for i in range(12)}
    fams = survey_families(cpu_frames)
    assert fams[0][0] == "0084" and fams[1][0] == "009e", fams
    summary, events = annotate_cpu_demo(cpu_frames, "0084", "009e", [])
    assert "pose_segments" in summary, summary.keys()
    assert isinstance(events, list), events

    # An absent family raises naming the prefix (matchup-specific mechs),
    # instead of IndexError deep in the centroid code.
    try:
        annotate_cpu_demo(cpu_frames, "0084", "00851", [])
    except ValueError as e:
        assert "'00851'" in str(e) and "009e" in str(e), str(e)
    else:
        raise AssertionError("absent mech-b family did not raise")

    print("annotate_bout stabilization/state tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
