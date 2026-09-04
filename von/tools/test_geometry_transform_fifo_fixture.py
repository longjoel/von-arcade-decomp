#!/usr/bin/env python3
"""Validate the original-ROM 0x76240 geometry FIFO evidence fixture."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "i960/geometry_transform_fifo_fixture.json"


def main():
    document = json.loads(FIXTURE.read_text())
    provenance = document["provenance"]
    assert provenance["rom"] == "original vonj"
    assert provenance["authoritative"] is True
    assert len(document["transactions"]) == 6
    commands = [item["command"] for item in document["transactions"]]
    assert commands == [29, 30, 29, 30, 29, 30]
    values = [int(item["value"], 16) for item in document["transactions"]]
    assert values == [0xe000, 0xe000, 0x2000, 0x2000, 0x8000, 0x8000]
    for item in document["transactions"]:
        assert len(item["responses"]) == 2
        assert int(item["responses"][0][1], 16) == 0
        assert int(item["command_pc"], 16) < int(item["responses"][0][0], 16)
    assert document["transactions"][0]["responses"][1][1] == "0xc129b5af"
    assert document["transactions"][-1]["responses"][1][1] == "0xc4bb7fff"
    print("PASS: original-ROM 0x76240 geometry FIFO fixture contract")


if __name__ == "__main__":
    main()
