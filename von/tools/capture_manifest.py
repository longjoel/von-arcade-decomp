#!/usr/bin/env python3
"""Create and validate deterministic sidecar manifests for bounded captures."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def directory_sha256(path: Path) -> str:
    """Hash directory contents by sorted relative names and file bytes."""
    digest = hashlib.sha256()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(relative(child, path).encode("utf-8"))
        digest.update(b"\0")
        with child.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        digest.update(b"\0")
    return digest.hexdigest()


def relative(path: Path, root: Path) -> str:
    return str(path.resolve().relative_to(root.resolve()))


def safe_path(path_text: Any) -> bool:
    if not isinstance(path_text, str):
        return False
    path = Path(path_text)
    return not path.is_absolute() and ".." not in path.parts


def validate(manifest: dict[str, Any], root: Path) -> list[str]:
    errors: list[str] = []
    if manifest.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if not isinstance(manifest.get("id"), str) or not manifest.get("id"):
        errors.append("missing stable capture id")
    stimulus = manifest.get("stimulus", {})
    if not isinstance(stimulus, dict):
        stimulus = {}
    if not isinstance(stimulus, dict) or not isinstance(stimulus.get("kind"), str) \
            or not stimulus.get("kind") or not isinstance(stimulus.get("seconds"), (int, float)) \
            or isinstance(stimulus.get("seconds"), bool) or stimulus.get("seconds") < 0:
        errors.append("stimulus requires kind and numeric seconds")
    if not isinstance(manifest.get("objective"), str) or not manifest.get("objective"):
        errors.append("missing capture objective")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        errors.append("capture requires at least one artifact")
    if stimulus.get("kind") == "input-free-attract" and not manifest.get("coverage_report"):
        errors.append("input-free-attract capture requires coverage_report")
    configuration = manifest.get("configuration", {})
    for field in ("set", "mame_revision", "patch_profile", "execution_engine"):
        if not configuration.get(field):
            errors.append(f"missing configuration.{field}")
    command = manifest.get("command")
    if not isinstance(command, list) or not command or not all(isinstance(item, str) and item for item in command):
        errors.append("command must be a non-empty string array")
    report_path_text = manifest.get("coverage_report")
    if report_path_text:
        report_path = root / report_path_text if safe_path(report_path_text) else None
        if report_path is None or not report_path.is_file():
            errors.append(f"missing coverage report {report_path_text}")
        else:
            try:
                report = json.loads(report_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"unable to read coverage report: {exc}")
            else:
                if report.get("capture_id") != manifest.get("id"):
                    errors.append("coverage report capture_id does not match sidecar id")
                if report.get("tier") != "A":
                    errors.append("coverage report must be Tier A")
                expected_phase = stimulus.get("phase")
                if report.get("phase") is not None and report.get("phase") != expected_phase:
                    errors.append("coverage report phase does not match sidecar stimulus phase")
    isolation = manifest.get("isolation", {})
    for field in ("cfg_directory", "nvram_directory", "state_directory"):
        path = isolation.get(field)
        if not safe_path(path) or not path:
            errors.append(f"missing isolation.{field}")
        elif not (root / path).is_dir():
            errors.append(f"missing isolation directory {path}")
        elif isolation.get(f"{field}_sha256") != directory_sha256(root / path):
            errors.append(f"hash mismatch for isolation.{field}")
    for section in ("inputs", "artifacts"):
        items = manifest.get(section, [])
        if not isinstance(items, list):
            errors.append(f"{section} must be an array")
            continue
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                errors.append(f"{section}[{index}] must be an object")
                continue
            path_text = item.get("path")
            path = root / path_text if safe_path(path_text) else None
            if path is None or not path.is_file():
                errors.append(f"{section}[{index}]: missing file {path_text}")
                continue
            if item.get("sha256") != sha256(path):
                errors.append(f"{section}[{index}]: hash mismatch for {path_text}")
    return errors


def entry(path: Path, root: Path) -> dict[str, str]:
    return {"path": relative(path, root), "sha256": sha256(path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--id", required=True)
    parser.add_argument("--objective", required=True)
    parser.add_argument("--seconds", required=True, type=float)
    parser.add_argument("--phase", default="stable-attract")
    parser.add_argument("--set", required=True)
    parser.add_argument("--mame-revision", required=True)
    parser.add_argument("--patch-profile", required=True)
    parser.add_argument("--execution-engine", required=True)
    parser.add_argument("--command", action="append", required=True)
    parser.add_argument("--coverage-report", type=Path)
    parser.add_argument("--cfg-directory", required=True, type=Path)
    parser.add_argument("--nvram-directory", required=True, type=Path)
    parser.add_argument("--state-directory", required=True, type=Path)
    parser.add_argument("--input", action="append", default=[], type=Path)
    parser.add_argument("--artifact", action="append", default=[], type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    manifest = {
        "schema_version": 1,
        "id": args.id,
        "objective": args.objective,
        "stimulus": {"kind": "input-free-attract", "seconds": args.seconds, "phase": args.phase},
        "configuration": {
            "set": args.set, "mame_revision": args.mame_revision,
            "patch_profile": args.patch_profile, "execution_engine": args.execution_engine,
        },
        "command": args.command,
        "coverage_report": relative(args.coverage_report, root) if args.coverage_report else None,
        "isolation": {
            "cfg_directory": relative(args.cfg_directory, root),
            "nvram_directory": relative(args.nvram_directory, root),
            "state_directory": relative(args.state_directory, root),
        },
        "inputs": [entry(path, root) for path in args.input],
        "artifacts": [entry(path, root) for path in args.artifact],
    }
    for field in ("cfg_directory", "nvram_directory", "state_directory"):
        manifest["isolation"][f"{field}_sha256"] = directory_sha256(
            root / manifest["isolation"][field]
        )
    errors = validate(manifest, root)
    if errors:
        for error in errors:
            print(f"- {error}")
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
