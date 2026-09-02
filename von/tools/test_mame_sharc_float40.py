#!/usr/bin/env python3
"""Compile the MAME SHARC 40-bit seam against the shared precision vectors."""

import json
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
HEADER = ROOT / "third_party/mame-master/src/devices/cpu/sharc/sharcfloat40.h"
CORE_HEADER = ROOT / "third_party/mame-master/src/devices/cpu/sharc/sharc.h"
SHARC_CPP = ROOT / "third_party/mame-master/src/devices/cpu/sharc/sharc.cpp"
SHARC_DRC_CPP = ROOT / "third_party/mame-master/src/devices/cpu/sharc/sharcdrc.cpp"
FIXTURE = ROOT / "von/i960/sharc_precision_fixtures.json"


HARNESS = r"""
#include "sharcfloat40.h"
#include <cstdint>
#include <iostream>
#include <string>

int main(int argc, char **argv)
{
    if (argc == 3 && std::string(argv[1]) == "VIEW")
    {
        sharc_float40::register_value value;
        value.set_extended(std::stoull(argv[2], nullptr, 0));
        std::cout << std::hex << value.storage_low_word() << ' '
                  << value.ieee32_word() << '\n';
        return 0;
    }
    if (argc == 2 && std::string(argv[1]) == "FLOAT")
    {
        std::cout << std::hex << sharc_float40::integer_to_float(3) << '\n';
        return 0;
    }
    if (argc == 3 && std::string(argv[1]) == "REJECT")
    {
        try
        {
            sharc_float40::decode(std::stoull(argv[2], nullptr, 0));
        }
        catch (const std::domain_error &)
        {
            return 0;
        }
        return 1;
    }
    const auto x = std::stoull(argv[2], nullptr, 0);
    const auto y = std::stoull(argv[3], nullptr, 0);
    const bool rnd32 = std::stoi(argv[4]) != 0;
    const bool truncate = std::stoi(argv[5]) != 0;
    const auto result = argv[1][2] == 'D'
        ? sharc_float40::add(x, y, rnd32, truncate)
        : sharc_float40::multiply(x, y, rnd32, truncate);
    std::cout << std::hex << result << '\n';
}
"""


def main():
    core_header = CORE_HEADER.read_text()
    if '#include "sharcfloat40.h"' not in core_header:
        raise SystemExit("MAME SHARC core header does not expose the 40-bit seam")
    if "using SHARC_REG_EXTENDED = sharc_float40::register_value;" not in core_header:
        raise SystemExit("MAME SHARC core header lacks the named extended register type")

    sharc_cpp = SHARC_CPP.read_text()
    if "m_drcuml->symbol_add(&m_core->r[i].r, sizeof(m_core->r[i].r), buf);" not in sharc_cpp:
        raise SystemExit("MAME DRC symbols do not expose the explicit low register word")
    if "m_regmap[i] = uml::mem(&m_core->r[i].r);" not in sharc_cpp:
        raise SystemExit("MAME DRC register map does not expose the explicit low register word")
    if "save_pointer(NAME(&m_core->r[0].r)" in sharc_cpp or "save_pointer(NAME(&m_core->reg_alt[0].r)" in sharc_cpp:
        raise SystemExit("MAME SHARC save-state registration still assumes contiguous register objects")
    if "for (int i = 0; i < std::size(m_core->r); ++i)" not in sharc_cpp or "save_item(NAME(m_core->r[i].r), i);" not in sharc_cpp:
        raise SystemExit("MAME SHARC primary registers lack per-register save-state entries")
    if "for (int i = 0; i < std::size(m_core->reg_alt); ++i)" not in sharc_cpp or "save_item(NAME(m_core->reg_alt[i].r), i);" not in sharc_cpp:
        raise SystemExit("MAME SHARC alternate registers lack per-register save-state entries")
    sharc_drc = SHARC_DRC_CPP.read_text()
    if sharc_drc.count("mem(&m_core->r[regnum].r)") != 2:
        raise SystemExit("MAME DRC synchronization does not use explicit low register words")
    if "UML_SWAPDQ(block, mem(&m_core->r[" in sharc_drc or "UML_SWAPDQ(block, mem(&m_core->reg_alt[" in sharc_drc:
        raise SystemExit("MAME DRC alternate-register swap still assumes contiguous register objects")

    vectors = json.loads(FIXTURE.read_text())["vectors"]
    with tempfile.TemporaryDirectory(prefix="mame-sharc-float40-") as directory:
        directory = pathlib.Path(directory)
        source = directory / "harness.cpp"
        binary = directory / "harness"
        source.write_text(HARNESS)
        subprocess.check_call([
            "g++", "-std=c++17", "-Wall", "-Wextra", "-Werror",
            "-I", str(HEADER.parent), str(source), "-o", str(binary),
        ])
        for vector in vectors:
            if vector["operation"] == "FLOAT":
                command = [str(binary), "FLOAT"]
            else:
                mode = vector["mode1"]
                command = [
                    str(binary), vector["operation"], vector["x"], vector["y"],
                    str(int(mode["rnd32"])), str(int(mode["trunc"])),
                ]
            actual = subprocess.check_output(command, text=True).strip()
            assert actual.lower() == vector["expected"][2:].lower(), (vector["name"], actual)
        for raw in ("0x0000000001", "0x7f80000000", "0x7fc0000000"):
            assert subprocess.call([str(binary), "REJECT", raw]) == 0, raw
        view = subprocess.check_output([
            str(binary), "VIEW", "0x3f80000001"], text=True).strip()
        assert view == "80000001 3f800000", view
    print("PASS: MAME SHARC 40-bit arithmetic seam")


if __name__ == "__main__":
    main()
