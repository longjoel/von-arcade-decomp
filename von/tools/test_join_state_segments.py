#!/usr/bin/env python3
"""Contract tests for the RAM/geometry state join (synthetic data only)."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent


def run_join(log_text: str, annot: dict, base: str = "0x1000"):
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        (td / "fuzz.log").write_text(log_text)
        (td / "annot.json").write_text(json.dumps(annot))
        out = td / "out.json"
        r = subprocess.run(
            [sys.executable, str(TOOLS / "join_state_segments.py"),
             "--fuzz-log", str(td / "fuzz.log"),
             "--annotation", str(td / "annot.json"),
             "--statelog-base", base, "--output", str(out)],
            capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        return json.loads(out.read_text())


def state_row(frame: int, words: list[str]) -> str:
    return f"fuzz: state f{frame} {' '.join(words)}\n"


def main() -> int:
    # Two segments (60 frames @60Hz = 1s each): word 1 flips exactly at the
    # boundary, word 2 churns always, word 0 is constant.
    log = ""
    for f in range(0, 60, 5):
        log += state_row(f, ["aaaaaaaa", "11111111", f"{f:08x}"])
    for f in range(60, 120, 5):
        log += state_row(f, ["aaaaaaaa", "22222222", f"{f:08x}"])
    log += "fuzz: frame 10 hold left_dash\n"
    annot = {"summary": {"pose_segments": {
        "a": [{"t0": 0.0, "t1": 1.0, "obas": ["x"]},
              {"t0": 1.0, "t1": 2.0, "obas": ["x", "y"]}]}}}
    out = run_join(log, annot)
    segs = out["mechs"]["a"]["segments"]
    assert len(segs) == 2, segs
    assert segs[0]["signature"] == ["aaaaaaaa", "11111111", segs[0]["signature"][2]], segs[0]
    assert segs[1]["signature"][1] == "22222222", segs[1]
    cands = out["mechs"]["a"]["state_bytes"]
    assert len(cands) == 1, cands
    assert cands[0]["word"] == 1, cands
    assert cands[0]["addr"] == "0x1004", cands
    assert cands[0]["values"] == ["11111111", "22222222"], cands
    assert out["holds"][0]["input"] == "left_dash", out["holds"]

    # No state rows: hard error naming the missing instrument.
    try:
        run_join("fuzz: frame 1 hold up\n", annot)
    except AssertionError as e:
        assert "VON_FUZZ_STATELOG" in str(e), e
    else:
        raise AssertionError("expected failure on stateless log")

    # Human-session marks pass through with frame-derived timestamps.
    log = state_row(0, ["aaaaaaaa"] * 2) + "mark f90 #3\n"
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        (td / "fuzz.log").write_text(log)
        (td / "annot.json").write_text(json.dumps(annot))
        out = td / "out.json"
        r = subprocess.run(
            [sys.executable, str(TOOLS / "join_state_segments.py"),
             "--fuzz-log", str(td / "fuzz.log"),
             "--annotation", str(td / "annot.json"),
             "--statelog-base", "0x1000", "--output", str(out)],
            capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        res = json.loads(out.read_text())
        assert res["marks"] == [{"frame": 90, "mark": 3, "t": 1.5}], \
            res["marks"]

    print("state-segment join tests passed")
    return 0


def main_snap() -> int:
    # Snapshot ingestion over 10 segments: word 1 flips once (kept), word 0
    # is constant (no candidate), word 3 takes 10 distinct modals (the
    # distinct cap rejects churn).
    log = ""
    for i in range(10):
        log += f"fuzz: frame {60 * i + 10} snapshot s{i}-pre\n"
    log += state_row(60, ["aaaaaaaa"] * 4)
    annot = {"summary": {"pose_segments": {
        "a": [{"t0": float(i), "t1": float(i + 1), "obas": ["x"]}
              for i in range(10)]}}}
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        (td / "fuzz.log").write_text(log)
        (td / "annot.json").write_text(json.dumps(annot))
        snapd = td / "snaps"
        snapd.mkdir()
        for i in range(10):
            words = ["11111111",
                     "22222222" if i < 5 else "33333333",
                     "00000001",
                     f"{i:08x}"]
            lines = "".join(f"{0x5000 + 4 * k:08x} {w}\n"
                            for k, w in enumerate(words))
            (snapd / f"snap-s{i}-pre-5000.txt").write_text(lines)
        out = td / "out.json"
        r = subprocess.run(
            [sys.executable, str(TOOLS / "join_state_segments.py"),
             "--fuzz-log", str(td / "fuzz.log"),
             "--annotation", str(td / "annot.json"),
             "--statelog-base", "0x5000",
             "--snap-dir", str(snapd), "--output", str(out)],
            capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        res = json.loads(out.read_text())
        regs = res["snap_regions"]
        assert "0x5000" in regs, regs.keys()
        cands = regs["0x5000"]["a"]["state_bytes"]
        words = {c["word"]: c["values"] for c in cands}
        assert words.get(1) == ["22222222", "33333333"], words
        assert 0 not in words, words
        assert 3 not in words, words
    print("snapshot join tests passed")
    return 0


main_snap()


if __name__ == "__main__":
    raise SystemExit(main())
