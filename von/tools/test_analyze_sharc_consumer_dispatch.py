#!/usr/bin/env python3
from analyze_sharc_consumer_dispatch import analyze


def test_unique_slot_dispatch():
    result = analyze([
        {"kind": "marker_slot_consume", "pc": 0x34050, "slot": 1},
        {"kind": "marker_slot_consume", "pc": 0x34050, "slot": 1},
        {"kind": "marker_slot_consume", "pc": 0x33ed0, "slot": 0},
    ])
    assert result["validation"]["ambiguous_dispatch_pcs"] == 0
    assert result["validation"]["slot_0_pcs"] == 1
    assert result["validation"]["slot_1_pcs"] == 1


def test_mixed_pc_is_rejected_by_check_contract():
    result = analyze([
        {"kind": "marker_slot_consume", "pc": 0x1234, "slot": 0},
        {"kind": "marker_slot_consume", "pc": 0x1234, "slot": 1},
    ])
    assert result["validation"]["ambiguous_dispatch_pcs"] == 1
    assert result["ambiguous"][0]["slots"] == [0, 1]


if __name__ == "__main__":
    test_unique_slot_dispatch()
    test_mixed_pc_is_rejected_by_check_contract()
    print("PASS: marker consumer PC dispatch")
