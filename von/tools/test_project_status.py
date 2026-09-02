#!/usr/bin/env python3
"""Check that generated project status agrees with authoritative inputs."""

from pathlib import Path

from project_status import collect


def main() -> int:
    status = collect(Path.cwd())
    assert status["ledger"]["valid"]
    attract = status["attract"]
    assert attract["discovered_units"] == (
        attract["modeled_units"] + attract["integrated_units"] + attract["untriaged_units"]
    )
    assert attract["integrated_units"] >= 0
    assert not status["tests"]["fast_requires_mame"]
    configured = status["tests"]["configured"]
    assert all(configured[name] > 0 for name in ("unit", "contract", "trace", "smoke", "attract"))
    assert status["evidence"]["healthy"]
    print("PASS: generated status agrees with ledger, worklist, tests, and evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
