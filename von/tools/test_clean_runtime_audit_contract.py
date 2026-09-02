#!/usr/bin/env python3
"""Ensure MAME failures cannot suppress the clean-image PC audit."""

from pathlib import Path
import json
import subprocess
import tempfile


def main() -> int:
    script = Path("scripts/audit-i960-clean-runtime.sh").read_text(encoding="utf-8")
    required = (
        "MAME_STATUS=$?",
        "AUDIT_STATUS=0",
        "audit_clean_i960_coverage.py",
        "MAME produced no i960 PC coverage",
        'if [[ "$MAME_STATUS" -ne 0 ]]',
        'exit "$AUDIT_STATUS"',
    )
    missing = [fragment for fragment in required if fragment not in script]
    if missing:
        raise SystemExit(f"clean runtime audit contract missing: {missing}")
    assert script.index("MAME_STATUS=$?") < script.index("audit_clean_i960_coverage.py")
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
    print("PASS: clean runtime always audits PCs before propagating MAME failure")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
