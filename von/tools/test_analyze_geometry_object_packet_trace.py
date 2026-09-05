#!/usr/bin/env python3
import tempfile
from pathlib import Path

from analyze_geometry_object_packet_trace import find_prefix


def test_prefix_is_detected():
    lines = [
        "[:] vonj_geometry_object_fifo: pc=00034048 data=0000002f",
        "[:] vonj_geometry_object_fifo: pc=00034068 data=0000b6d0",
        "[:] vonj_geometry_object_fifo: pc=00034070 data=00004c4c",
        "[:] vonj_geometry_object_fifo: pc=00034078 data=0000bb8b",
        "[:] vonj_geometry_object_fifo: pc=0003408c data=00000016",
        "[:] vonj_geometry_object_fifo: pc=0003409c data=0000006c",
        "[:] vonj_geometry_object_fifo: pc=000340b0 data=00000015",
        "[:] vonj_geometry_object_fifo: pc=000340c0 data=00000017",
        "[:] vonj_geometry_object_fifo: pc=000340d4 data=00000014",
        "[:] vonj_geometry_object_fifo: pc=000340e4 data=ffffff80",
    ]
    with tempfile.TemporaryDirectory() as directory:
        trace = Path(directory) / "trace.log"
        trace.write_text("\n".join(lines) + "\n")
        count, prefix = find_prefix(trace)
    assert count == 10
    assert prefix is not None
    assert prefix[0] == (0x34048, 0x2F)


if __name__ == "__main__":
    test_prefix_is_detected()
