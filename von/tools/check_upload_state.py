#!/usr/bin/env python3
"""Check M2 upload-state lines from a MAME trace log against the oracle.

Usage: check_upload_state.py <trace-log>

Parses `upload-state:` lines emitted by gameplay_progress.lua and verifies
the live cluster run: 768 stores, post-run counter 5, and the sampled
destination words equal to the scale form of the sampled source words
(fade 0x80 -> factor 0x180 over in & 0x00ff00ff). Exits nonzero with a
diagnostic on the first mismatch, or when no upload-state lines exist.
"""
import re
import sys

MASK = 0x00FF00FF
M32 = 0x100000000
LINE = re.compile(
    r"upload-state: frame (\d+) stores=([0-9a-f]+) counter=([0-9a-f]+) "
    r"dst_first=([0-9a-f]+) dst_last=([0-9a-f]+) "
    r"src_first=([0-9a-f]+) src_last=([0-9a-f]+) "
    r"live_first=([0-9a-f]+) live_last=([0-9a-f]+)")


def oracle_mul(pixel, factor):
    return (((factor * (pixel & MASK)) % M32) >> 8) % M32


def main(path):
    lines = []
    with open(path, errors="replace") as handle:
        for raw in handle:
            match = LINE.search(raw)
            if match:
                lines.append([match.group(1),
                              *[int(g, 16) for g in match.groups()[1:]]])
    if not lines:
        print("FAIL: no upload-state lines in log")
        return 1
    frame, stores, counter, dst_first, dst_last, src_first, src_last, \
        live_first, live_last = lines[0]
    errors = []
    if stores != 768:
        errors.append(f"stores {stores} != 768")
    if counter != 5:
        errors.append(f"counter {counter} != 5")
    if dst_first != live_first:
        errors.append("state dst_first disagrees with live window read")
    if dst_last != live_last:
        errors.append("state dst_last disagrees with live window read")
    if live_first != oracle_mul(src_first, 0x180):
        errors.append(f"live_first {live_first:#x} != "
                      f"scale({src_first:#x})")
    if live_last != oracle_mul(src_last, 0x180):
        errors.append(f"live_last {live_last:#x} != "
                      f"scale({src_last:#x})")
    if errors:
        print(f"FAIL: frame {frame}: " + "; ".join(errors))
        return 1
    print(f"PASS: frame {frame} stores=768 counter=5 "
          f"dst==scale(src) on both samples")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
