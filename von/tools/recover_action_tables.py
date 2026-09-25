#!/usr/bin/env python3
"""Emit the real runtime action motion tables as a `dump_motion_tables`-shaped JSON.

`dump_motion_tables.py`'s `ACTION_HEADERS` are hardcoded and point at 8-part
skeleton + 17-part body tables that the running game does not use. The headers
the game actually publishes for each labelled action were recovered from an
`action_schedule.lua` capture's lock log (`0x0051ab08`/`0x0051ab0c`); this
resolves them to their skeleton and body tables (8-part and 15-part) and emits
the same JSON shape so `actions_to_sharc_header.py` can consume it.

  python3 tools/sharc/recover_action_tables.py --out /tmp/temjin-actions.json
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
from decode_model_part_table import load_main_data  # noqa: E402
from dump_motion_tables import load_maincpu, motion_header  # noqa: E402

_DECOMP = _HERE.parent.parent

MAIN_DATA_BASE = 0x02000000

# action -> (skeleton header, body header), from the lock log of a labelled
# action-schedule capture (idle/forward/... windows). strafe_left/right resolve
# to the forward header for this input schedule.
ACTION_HEADERS = {
    "idle": (0x021A09D8, 0x020E4668),
    "forward": (0x021AADC8, 0x020F7968),
    "back": (0x021AA1C0, 0x020F62E0),
    "turn_l": (0x021B5658, 0x0210B4F8),
    "turn_r": (0x021B5C68, 0x0210C048),
    "dash": (0x02139C00, 0x020238C0),
    "guard": (0x02141C28, 0x02032878),
    "jump": (0x02170540, 0x0208A080),
    "shot_l": (0x02171158, 0x0208B718),
    "shot_r": (0x021996A8, 0x020D6ED0),
}


def records(md: bytes, data: int, frames: int, parts: int) -> str:
    blob = md[data - MAIN_DATA_BASE:data - MAIN_DATA_BASE + frames * parts * 12]
    return base64.b64encode(blob).decode("ascii")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom-dir", type=Path, default=_DECOMP / "von" / "artifacts")
    parser.add_argument("--fighter", default="temjin")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    maincpu = load_maincpu(args.rom_dir)
    main_data = load_main_data(args.rom_dir)

    actions = []
    for name, (skeleton, body) in ACTION_HEADERS.items():
        sk = motion_header(maincpu, main_data, skeleton)
        bd = motion_header(maincpu, main_data, body)
        if not sk or not bd:
            raise SystemExit(f"{name}: header did not resolve ({sk}, {bd})")
        sk_data, sk_frames, sk_parts = sk
        bd_data, bd_frames, bd_parts = bd
        actions.append({
            "name": name,
            "header": skeleton, "data": sk_data,
            "frames": sk_frames, "parts": sk_parts,
            "body_header": body, "body_data": bd_data,
            "body_frames": bd_frames, "body_parts": bd_parts,
            "records_b64": records(main_data, sk_data, sk_frames, sk_parts),
            "body_records_b64": records(main_data, bd_data, bd_frames, bd_parts),
        })
        print(f"{name:8} skeleton={skeleton:#010x} {sk_frames}f/{sk_parts}p "
              f"body={body:#010x} {bd_frames}f/{bd_parts}p")

    document = {"fighter": args.fighter, "source": "recovered-runtime-headers",
                "actions": actions}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(document) + "\n")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
