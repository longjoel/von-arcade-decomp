#!/usr/bin/env python3
"""Replay the recovered SHARC packet program in model space.

The i960 emits per-part transform packets (push, translate, Z/Y/X rotate,
commit) whose committed matrices are camera-relative: Model 2 has no view
command, so the camera is baked into the object base. Given a normalized
emitter/stack fixture (decomp `normalize_transform_trace.py`) and a per-frame
`camera.log`, this:

  1. re-evaluates each part's commit from its pushed base and packet body,
     proving the packet/lineage join, then
  2. factors the camera out, `model = inv(view) * commit`, so the pose is
     fighter/world space rather than view space.

The fixture already carries the OBA the emitter tagged each part with, so no
capture-fitted parent or nearest-neighbour choice is involved.

  python3 tools/sharc_replay.py --fixture tests/fixtures/sharc/temjin-match-1924.json \
      --camera-log tests/fixtures/sharc/temjin-match-1924.camera.log
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import camera  # noqa: E402
from sharc_transform import compose_motion_record  # noqa: E402


def f32(word: int) -> float:
    return struct.unpack("<f", struct.pack("<I", word & 0xFFFFFFFF))[0]


def portable(matrix_words: list[int]) -> list[float]:
    """Native m0..m8 + tail -> 3x4 row-major column-vector affine."""
    m = [f32(w) for w in matrix_words]
    return [m[0], m[3], m[6], m[9],
            m[1], m[4], m[7], m[10],
            m[2], m[5], m[8], m[11]]


def record_of(packet: dict) -> list[int]:
    """Packet body [tx, ty, tz, z, y, x] from the ordered word stream."""
    w = packet["words"]
    return [w[2], w[3], w[4], w[6], w[8], w[10]]


def replay(fixture_path: Path, camera_log: Path) -> dict:
    fixture = json.loads(fixture_path.read_text())
    views = camera.parse_camera_log(camera_log)
    packets = {p["event_id"]: p for p in fixture["packets"]}

    poses: dict[int, dict[str, list[float]]] = {}
    worst_eval = 0.0
    for program in fixture["part_programs"]:
        packet = packets.get(program["packet_event_id"])
        if packet is None:
            continue
        base = [f32(w) for w in program["push"]["base_words"]]
        matrix, tail = compose_motion_record(record_of(packet), base[:9])
        evaluated = matrix + [base[9 + i] + tail[i] for i in range(3)]

        commit = program["commit"]["matrix_words"]
        committed = [f32(w) for w in commit]
        error = max(max(abs(evaluated[i] - committed[i]) for i in range(9)),
                    max(abs(evaluated[9 + i] - committed[9 + i]) for i in range(3)))
        worst_eval = max(worst_eval, error)

        frame = program["commit"]["frame"]
        view_frame = camera.nearest_frame(views, frame)
        view = camera.view_matrix(view_frame["eye"], view_frame["target"])
        model = camera.model_space(portable(commit), view)
        poses.setdefault(frame, {})[program["commit"]["oba"]] = model
    return {"poses": poses, "max_eval_error": worst_eval,
            "validation": fixture.get("validation", {})}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--camera-log", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    result = replay(args.fixture, args.camera_log)
    validation = result["validation"]
    assert validation.get("unresolved_packet_obas", 1) == 0, validation
    assert validation.get("unmatched_commits", 1) == 0, validation
    assert result["max_eval_error"] < 1e-3, result["max_eval_error"]

    for frame in sorted(result["poses"]):
        parts = result["poses"][frame]
        print(f"frame {frame}: {len(parts)} parts, "
              f"root={parts.get('0x009e2a84', [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])[3:]} ")
    print(f"max packet replay error {result['max_eval_error']:.3g}; "
          f"obas unresolved {validation.get('unresolved_packet_obas')}")
    if args.out:
        args.out.write_text(json.dumps({"schema": "von-sharc-model-space/1",
                                        "poses": result["poses"]},
                                       sort_keys=True, separators=(",", ":")) + "\n")
        print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
