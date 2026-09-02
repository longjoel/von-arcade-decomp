#!/usr/bin/env python3
"""Verify the 16-sample signed sine/cosine runtime sweep."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


SINE = (
    0x00000000, 0x3EC3F089, 0x3F350610, 0x3F6C8446,
    0x3F800000, 0x3F6C81DE, 0x3F35019C, 0x3EC3E4F0,
    0x38C92EEF, 0xBEC3E4F0, 0xBF35019C, 0xBF6C81DE,
    0xBF800000, 0xBF6C8446, 0xBF350610, 0xBEC3F089,
)
COSINE = (
    0x3F7FFFFF, 0x3F6C8310, 0x3F3503D8, 0x3EC3EAB8,
    0xB8492EEF, 0xBEC3F657, 0xBF35084A, 0xBF6C8578,
    0xBF7FFFFF, 0xBF6C8578, 0xBF35084A, 0xBEC3F657,
    0xB8492EEF, 0x3EC3EAB8, 0x3F3503D8, 0x3F6C8310,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("trace", type=Path)
    parser.add_argument("probe_log", type=Path)
    args = parser.parse_args()

    requests = []
    for line in args.probe_log.read_text(encoding="utf-8").splitlines():
        match = re.search(r"index=(\d+) opcode=([0-9a-f]+) input=([0-9a-f]+)", line)
        if match:
            requests.append((int(match.group(1)), int(match.group(2), 16), int(match.group(3), 16)))
    if len(requests) != 32:
        raise SystemExit(f"expected 32 probe requests, found {len(requests)}")

    outputs = []
    for line in args.trace.read_text(encoding="utf-8", errors="replace").splitlines():
        if "vonj_sharc_output:" not in line:
            continue
        match = re.search(r"pc=([0-9a-f]+).*data=([0-9a-f]+)", line)
        if match and int(match.group(1), 16) in (0x203C0, 0x203CC):
            outputs.append(int(match.group(2), 16))
    if len(outputs) != 32:
        raise SystemExit(f"expected 32 service outputs, found {len(outputs)}")

    for request, actual, wanted in zip(requests, outputs, SINE + COSINE):
        if actual != wanted:
            raise SystemExit(
                f"sample {request[0]} opcode={request[1]:02x} input={request[2]:08x} "
                f"was {actual:08x}, expected {wanted:08x}"
            )
    print("PASS: SHARC signed sine/cosine quadrant sweep")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
