#!/usr/bin/env python3
"""Ensure MAME failures cannot suppress the clean-image PC audit."""

from pathlib import Path


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
    print("PASS: clean runtime always audits PCs before propagating MAME failure")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
