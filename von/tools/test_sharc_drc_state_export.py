#!/usr/bin/env python3
"""Check the SHARC DRC architectural-state export contract."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SHARC = ROOT / "third_party/mame-master/src/devices/cpu/sharc/sharc.cpp"
DISTATE = ROOT / "third_party/mame-master/src/emu/distate.cpp"


def main() -> int:
    sharc = SHARC.read_text()
    distate = DISTATE.read_text()

    assert "case SHARC_ASTAT:" in sharc
    export = sharc[sharc.index("void adsp21062_device::state_export") : sharc.index("void adsp21062_device::enable_recompiler")]
    assert "m_core->astat_drc.pack()" in export
    assert "m_core->astat = (m_core->astat & flags_mask)" in export
    assert 'state_add(SHARC_ASTAT,  "ASTAT", m_core->astat).formatstr("%08X").callimport().callexport();' in sharc
    assert "// call the exporter before we do anything" in distate
    assert "m_device_state->state_export(*this);" in distate

    print("PASS: SHARC DRC ASTAT state-export contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
