#!/usr/bin/env python3
"""Check that generated project status agrees with authoritative inputs."""

from pathlib import Path

from project_status import collect


def main() -> int:
    status = collect(Path.cwd())
    assert status["ledger"]["valid"]
    assert status["attract"]["discovered_units"] == 262
    assert status["attract"]["modeled_units"] == 94
    assert status["attract"]["untriaged_units"] == 168
    assert not status["tests"]["fast_requires_mame"]
    assert sum(status["tests"]["configured"].values()) >= 360
    assert status["evidence"]["healthy"]
    print("PASS: generated status agrees with ledger, worklist, tests, and evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
