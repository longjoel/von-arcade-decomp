#!/usr/bin/env python3
"""Keep the focused MAME Virtual-On subtarget link closure explicit."""

import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]
SUBTARGET = ROOT.parent / "scripts/mame-von.lua"


def main():
    source = SUBTARGET.read_text()
    required = {
        'CPUS["ADSP2106X"] = true',
        'CPUS["I960"] = true',
        'CPUS["MB86233"] = true',
        'MACHINES["GEN_FIFO"] = true',
        'MACHINES["I8251"] = true',
        'MACHINES["MB3773"] = true',
        'MACHINES["Z80CTC"] = true',
        'MACHINES["Z80PIO"] = true',
        'MACHINES["Z80SIO"] = true',
        'BUSES["RS232"] = true',
        'VIDEOS["HD44780"] = true',
        'SOUNDS["MPEG_AUDIO"] = true',
    }
    missing = sorted(item for item in required if item not in source)
    if missing:
        raise SystemExit("missing focused MAME dependency declarations: " + ", ".join(missing))
    for filename in (
        'src/mame/sega/model2.cpp',
        'src/mame/sega/model2_v.cpp',
        'src/mame/sega/model1io2.cpp',
    ):
        if filename not in source:
            raise SystemExit(f"focused MAME subtarget does not include {filename}")
    print("PASS: focused MAME Virtual-On subtarget dependency contract")


if __name__ == "__main__":
    main()
