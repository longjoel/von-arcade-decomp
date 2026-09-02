#!/usr/bin/env python3
"""Compile and exercise the standalone C++ SHARC 40-bit execution oracle."""

import json
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools/sharc_40bit_reference.cpp"
FIXTURE = ROOT / "i960/sharc_precision_fixtures.json"


def run(binary, vector):
    if vector["operation"] == "FLOAT":
        command = [str(binary), "FLOAT"]
    else:
        mode = vector["mode1"]
        command = [
            str(binary),
            vector["operation"],
            vector["x"],
            vector["y"],
            str(int(mode["rnd32"])),
            str(int(mode["trunc"])),
        ]
    actual = subprocess.check_output(command, text=True).strip()
    assert actual.lower() == vector["expected"][2:].lower(), (vector["name"], actual)


def main():
    document = json.loads(FIXTURE.read_text())
    with tempfile.TemporaryDirectory(prefix="von-sharc-40bit-") as directory:
        binary = pathlib.Path(directory) / "reference"
        subprocess.check_call([
            "g++", "-std=c++17", "-O2", str(SOURCE), "-o", str(binary),
        ])
        for vector in document["vectors"]:
            run(binary, vector)
    print("PASS: standalone SHARC 40-bit C++ execution oracle")


if __name__ == "__main__":
    main()
