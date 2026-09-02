#!/usr/bin/env python3
"""Run manifest-defined test tiers in parallel with deterministic output."""

from __future__ import annotations

import argparse
import concurrent.futures
from datetime import datetime, timezone
import glob
import fnmatch
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path


def commands_for(root: Path, manifest: dict, suite_name: str) -> tuple[list[list[str]], dict[str, str]]:
    suites = manifest.get("suites", {})
    if suite_name not in suites:
        raise ValueError(f"unknown suite {suite_name!r}; expected {', '.join(suites)}")
    suite = suites[suite_name]
    commands = [list(command) for command in suite.get("commands", [])]
    for pattern in suite.get("discover", []):
        commands.extend([["python3", path] for path in sorted(glob.glob(str(root / pattern)))])
    prefix = str(root) + os.sep
    for command in commands:
        for index, value in enumerate(command):
            if value.startswith(prefix):
                command[index] = value[len(prefix):]
    excluded = suite.get("exclude", [])
    commands = [
        command for command in commands
        if not (len(command) >= 2 and any(fnmatch.fnmatch(command[1], pattern) for pattern in excluded))
    ]
    unique: list[list[str]] = []
    seen: set[tuple[str, ...]] = set()
    for command in commands:
        key = tuple(command)
        if key not in seen:
            seen.add(key)
            unique.append(command)
    return unique, {str(key): str(value) for key, value in suite.get("environment", {}).items()}


def run_one(index: int, command: list[str], root: Path, environment: dict[str, str]) -> tuple[int, list[str], int, str, float]:
    started = time.monotonic()
    completed = subprocess.run(command, cwd=root, env={**os.environ, **environment}, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return index, command, completed.returncode, completed.stdout, time.monotonic() - started


def record_result(root: Path, suite_name: str, manifest_sha256: str, results: list[tuple]) -> None:
    failures = [" ".join(command) for _, command, returncode, _, _ in results if returncode]
    document = {
        "schema_version": 1,
        "suite": suite_name,
        "manifest_sha256": manifest_sha256,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "passed": not failures,
        "tests": len(results),
        "commands": [command for _, command, _, _, _ in results],
        "failures": failures,
        "elapsed_seconds": round(sum(result[4] for result in results), 3),
    }
    output = root / "von/build/test-results" / f"{suite_name}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("suites", nargs="+", choices=("unit", "contract", "trace", "smoke", "attract"))
    parser.add_argument("--manifest", type=Path, default=Path("von/tests/manifest.json"))
    parser.add_argument("--jobs", type=int, default=min(8, os.cpu_count() or 1))
    args = parser.parse_args()
    root = Path.cwd()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    manifest_sha256 = hashlib.sha256(manifest_bytes).hexdigest()
    overall_started = time.monotonic()
    total = 0
    for suite_name in args.suites:
        commands, environment = commands_for(root, manifest, suite_name)
        total += len(commands)
        print(f"[{suite_name}] {len(commands)} test(s), jobs={args.jobs}")
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as executor:
            results = list(executor.map(lambda item: run_one(item[0], item[1], root, environment), enumerate(commands)))
        failures = 0
        for _, command, returncode, output, elapsed in sorted(results):
            label = "PASS" if returncode == 0 else "FAIL"
            print(f"[{suite_name}] {label} {elapsed:6.2f}s {' '.join(command)}")
            if returncode:
                failures += 1
                print(output.rstrip())
        record_result(root, suite_name, manifest_sha256, results)
        if failures:
            print(f"[{suite_name}] {failures} failure(s)")
            return 1
    elapsed = time.monotonic() - overall_started
    print(f"PASS: {total} test(s) across {len(args.suites)} suite(s) in {elapsed:.2f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
