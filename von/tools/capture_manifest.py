#!/usr/bin/env python3
"""Create and validate deterministic sidecar manifests for bounded captures."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


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


def rooted(root: Path, path_text: Any) -> Path | None:
    """Resolve a manifest path only when it remains inside the capture root."""
    if not safe_path(path_text):
        return None
    candidate = root / path_text
    try:
        candidate.resolve().relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def validate(manifest: dict[str, Any], root: Path) -> list[str]:
    errors: list[str] = []
    if not isinstance(manifest, dict):
        return ["capture manifest must be an object"]
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
    checkpoints = manifest.get("checkpoints")
    if (not isinstance(checkpoints, list) or not checkpoints
            or not all(isinstance(item, str) and item for item in checkpoints)
            or len(set(checkpoints)) != len(checkpoints)):
        errors.append("capture checkpoints must be a non-empty unique string array")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        errors.append("capture requires at least one artifact")
    if stimulus.get("kind") == "input-free-attract" and not manifest.get("coverage_report"):
        errors.append("input-free-attract capture requires coverage_report")
    configuration = manifest.get("configuration", {})
    if not isinstance(configuration, dict):
        errors.append("configuration must be an object")
        configuration = {}
    for field in ("set", "mame_revision", "patch_profile", "execution_engine"):
        if not configuration.get(field):
            errors.append(f"missing configuration.{field}")
    command = manifest.get("command")
    if not isinstance(command, list) or not command or not all(isinstance(item, str) and item for item in command):
        errors.append("command must be a non-empty string array")
    def command_argument(flag: str) -> str | None:
        if not isinstance(command, list):
            return None
        try:
            index = command.index(flag)
        except ValueError:
            return None
        return command[index + 1] if index + 1 < len(command) else None
    report_path_text = manifest.get("coverage_report")
    if report_path_text:
        report_path = rooted(root, report_path_text)
        if report_path is None or not report_path.is_file():
            errors.append(f"missing coverage report {report_path_text}")
        elif not isinstance(artifacts, list) or not any(
                isinstance(item, dict) and item.get("path") == report_path_text
                for item in artifacts):
            errors.append("coverage report must be a declared capture artifact")
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
                if report.get("edge_semantics") != "possible_static_edges":
                    errors.append("coverage report must use possible_static_edges semantics")
                expected_phase = stimulus.get("phase")
                if report.get("phase") is not None and report.get("phase") != expected_phase:
                    errors.append("coverage report phase does not match sidecar stimulus phase")
    isolation = manifest.get("isolation", {})
    if not isinstance(isolation, dict):
        errors.append("isolation must be an object")
        isolation = {}
    isolation_resolved: dict[str, Path] = {}
    for field in ("cfg_directory", "nvram_directory", "state_directory"):
        path = isolation.get(field)
        if not safe_path(path) or not path:
            errors.append(f"missing isolation.{field}")
        elif rooted(root, path) is None or not rooted(root, path).is_dir():
            errors.append(f"missing isolation directory {path}")
        elif isolation.get(f"{field}_sha256") != directory_sha256(rooted(root, path)):
            errors.append(f"hash mismatch for isolation.{field}")
        else:
            isolation_resolved[field] = rooted(root, path).resolve()
    if len(set(isolation_resolved.values())) != len(isolation_resolved):
        errors.append("isolation directories must be distinct")
    for flag, field in (("-cfg_directory", "cfg_directory"),
                        ("-nvram_directory", "nvram_directory"),
                        ("-state_directory", "state_directory")):
        if isinstance(command, list) and command.count(flag) > 1:
            errors.append(f"command must contain {flag} only once")
        argument = command_argument(flag)
        expected = isolation_resolved.get(field)
        if argument is None:
            errors.append(f"command must declare {flag}")
        elif expected is not None:
            try:
                if Path(argument).resolve() != expected:
                    errors.append(f"command {flag} does not match isolation.{field}")
            except (OSError, RuntimeError):
                errors.append(f"command {flag} has an invalid path")
    seconds_argument = command_argument("-seconds_to_run")
    if seconds_argument is None:
        errors.append("command must declare -seconds_to_run")
    elif isinstance(command, list) and command.count("-seconds_to_run") > 1:
        errors.append("command must contain -seconds_to_run only once")
    else:
        try:
            if float(seconds_argument) != float(stimulus.get("seconds")):
                errors.append("command -seconds_to_run does not match stimulus seconds")
        except (TypeError, ValueError):
            errors.append("command -seconds_to_run must be numeric")
    for section in ("inputs", "artifacts"):
        items = manifest.get(section, [])
        if not isinstance(items, list):
            errors.append(f"{section} must be an array")
            continue
        paths: set[Path] = set()
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                errors.append(f"{section}[{index}] must be an object")
                continue
            path_text = item.get("path")
            path = rooted(root, path_text)
            if path is None or not path.is_file():
                errors.append(f"{section}[{index}]: missing file {path_text}")
                continue
            resolved_path = path.resolve()
            if resolved_path in paths:
                errors.append(f"{section}[{index}]: duplicate file {path_text}")
                continue
            paths.add(resolved_path)
            if not isinstance(item.get("sha256"), str) or not SHA256_RE.fullmatch(item["sha256"]):
                errors.append(f"{section}[{index}]: sha256 must be a SHA-256 digest")
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
    parser.add_argument("--stimulus-kind", choices=("input-free-attract", "bounded-trace", "causal-trace"),
                        default="input-free-attract")
    parser.add_argument("--phase", default="stable-attract")
    parser.add_argument("--checkpoint", action="append", required=True,
                        help="ordered checkpoint name; may be repeated")
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
        "stimulus": {"kind": args.stimulus_kind, "seconds": args.seconds, "phase": args.phase},
        "checkpoints": args.checkpoint,
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
