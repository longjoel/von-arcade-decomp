#!/usr/bin/env python3
"""Ensure MAME failures cannot suppress the clean-image PC audit."""

from pathlib import Path
import json
import subprocess
import tempfile


def main() -> int:
    script = Path("scripts/audit-i960-clean-runtime.sh").read_text(encoding="utf-8")
    lua = Path("von/tools/trace_i960_attract_coverage.lua").read_text(encoding="utf-8")
    capture = Path("scripts/trace-i960-attract-coverage.sh").read_text(encoding="utf-8")
    required = (
        "MAME_STATUS=$?",
        "AUDIT_STATUS=0",
        "audit_clean_i960_coverage.py",
        "MAME produced no i960 PC coverage",
        'if [[ "$MAME_STATUS" -ne 0 ]]',
        'RUN_LOG=',
        "Unhandled 00|Unhandled exception|\\[LUA ERROR\\]",
        'exit "$AUDIT_STATUS"',
    )
    missing = [fragment for fragment in required if fragment not in script]
    if missing:
        raise SystemExit(f"clean runtime audit contract missing: {missing}")
    for fragment in ("capture_manifest.py", "-cfg_directory", "-nvram_directory", "-state_directory"):
        if fragment not in capture:
            raise SystemExit(f"attract capture provenance contract missing: {fragment}")
    assert script.index("MAME_STATUS=$?") < script.index("audit_clean_i960_coverage.py")
    assert "manager.machine:exit()" in lua
    assert "emu.exit()" not in lua
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        pcs = root / "pcs"
        manifest = root / "manifest.json"
        pcs.write_text("# fixture\n00000000\n00000004\n", encoding="ascii")
        manifest.write_text(json.dumps({"generated_code_bytes": 0x100}), encoding="utf-8")
        result = subprocess.run(
            ["python3", "von/tools/audit_clean_i960_coverage.py", "--pcs", str(pcs), "--manifest", str(manifest)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode != 0
        assert "PC zero was executed" in result.stderr
        cases = [
            ("# visited=0\n", None, "PC coverage is empty"),
            ("00000100\n", None, "escaped generated code"),
            ("00000005\n", None, "invalid or unaligned"),
            ("00000004\n", "60", "completion time"),
            ("00000004\n# completed_time=59.99\n", "60", "before 60.0s"),
            ("00000004\n# completed_time=60.0\n# completed_time=61.0\n", "60", "completion time"),
            ("00000004\n# completed_time=60.0\n", "nan", "finite and positive"),
            ("00000004\n# completed_time=60.0\n", "60", None),
        ]
        for content, duration, error in cases:
            pcs.write_text(content, encoding="ascii")
            command = ["python3", "von/tools/audit_clean_i960_coverage.py",
                       "--pcs", str(pcs), "--manifest", str(manifest)]
            if duration is not None:
                command += ["--expected-seconds", duration]
            result = subprocess.run(command, capture_output=True, text=True)
            assert (result.returncode == 0) == (error is None), result
            if error:
                assert error in result.stderr, result.stderr
    assert 'mktemp -d "$OUT_DIR/run-XXXXXXXX"' in script
    assert '--expected-seconds "$SECONDS_TO_RUN"' in script
    assert '# completed_time=%.9f' in lua
    print("PASS: clean runtime always audits PCs before propagating MAME failure")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
