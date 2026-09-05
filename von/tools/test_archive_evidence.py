#!/usr/bin/env python3
"""Contract tests for content-addressed evidence archive metadata."""

from __future__ import annotations

import gzip
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from archive_evidence import validate_metadata


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "von/tools/archive_evidence.py"


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source = root / "events.ndjson"
        archive = root / "archive"
        metadata = root / "metadata.json"
        payload = b'{"seq":1}\n'
        source.write_bytes(payload)
        result = subprocess.run(
            [sys.executable, str(TOOL), str(source), "--archive", str(archive), "--metadata", str(metadata)],
            cwd=ROOT, capture_output=True, text=True, check=True,
        )
        digest = hashlib.sha256(payload).hexdigest()
        target = archive / f"{digest}.gz"
        record = json.loads(metadata.read_text(encoding="utf-8"))
        assert f"sha256:{digest}" in result.stdout
        assert record["source"]["sha256"] == digest
        assert record["archive"]["sha256"] == hashlib.sha256(target.read_bytes()).hexdigest()
        assert not validate_metadata(record)
        record["archive"]["sha256"] = "0" * 64
        assert any("archive hash mismatch" in error for error in validate_metadata(record))
        record["archive"]["sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
        with gzip.open(target, "wb") as stream:
            stream.write(b'{"wrong":true}\n')
        record["archive"]["sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
        assert any("decompressed payload mismatch" in error for error in validate_metadata(record))
        with gzip.open(target, "rb") as stream:
            assert stream.read() == b'{"wrong":true}\n'
        poisoned = subprocess.run(
            [sys.executable, str(TOOL), str(source), "--archive", str(archive)],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        assert poisoned.returncode != 0
        assert "payload mismatch" in poisoned.stderr
        linked_archive = root / "linked-archive"
        linked_archive.mkdir()
        linked_target = linked_archive / f"{digest}.gz"
        linked_target.symlink_to(target)
        linked = subprocess.run(
            [sys.executable, str(TOOL), str(source), "--archive", str(linked_archive)],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        assert linked.returncode != 0
        assert "symlink components" in linked.stderr
        linked_archive_parent = root / "linked-archive-parent"
        linked_archive_parent.symlink_to(archive, target_is_directory=True)
        linked_archive_parent_run = subprocess.run(
            [sys.executable, str(TOOL), str(source), "--archive", str(linked_archive_parent / "nested")],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        assert linked_archive_parent_run.returncode != 0
        assert "archive directory path" in linked_archive_parent_run.stderr
        linked_source_archive = root / "source-link.ndjson"
        linked_source_archive.symlink_to(source)
        linked_source_run = subprocess.run(
            [sys.executable, str(TOOL), str(linked_source_archive),
             "--archive", str(root / "source-link-archive")],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        assert linked_source_run.returncode != 0
        assert "capture source path" in linked_source_run.stderr
        linked_source_parent = root / "linked-source-parent"
        linked_source_parent.symlink_to(root, target_is_directory=True)
        linked_source_parent_run = subprocess.run(
            [sys.executable, str(TOOL), str(linked_source_parent / source.name),
             "--archive", str(root / "source-parent-archive")],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        assert linked_source_parent_run.returncode != 0
        assert "capture source path" in linked_source_parent_run.stderr
        missing_source_run = subprocess.run(
            [sys.executable, str(TOOL), str(root / "missing-events.ndjson"),
             "--archive", str(root / "missing-source-archive")],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        assert missing_source_run.returncode != 0
        assert "missing capture source" in missing_source_run.stderr
        archive_directory_link = root / "archive-directory-link"
        archive_directory_link.symlink_to(archive, target_is_directory=True)
        linked_directory_run = subprocess.run(
            [sys.executable, str(TOOL), str(source), "--archive", str(archive_directory_link)],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        assert linked_directory_run.returncode != 0
        assert "archive directory path" in linked_directory_run.stderr
        wrong_target = archive / "not-content-addressed.gz"
        wrong_target.write_bytes(target.read_bytes())
        wrong_name = json.loads(json.dumps(record))
        wrong_name["archive"] = {
            "path": str(wrong_target), "bytes": wrong_target.stat().st_size,
            "sha256": hashlib.sha256(wrong_target.read_bytes()).hexdigest(),
        }
        assert any("archive filename" in error for error in validate_metadata(wrong_name))
        malformed = {"schema_version": 1, "source": [], "archive": {}}
        assert any("source metadata must be an object" in error
                   for error in validate_metadata(malformed))
        linked_source = root / "linked-source.ndjson"
        linked_source.symlink_to(source)
        linked_metadata = json.loads(json.dumps(record))
        linked_metadata["source"]["path"] = str(linked_source)
        assert any("source path must not contain symlink components" in error
                   for error in validate_metadata(linked_metadata))
        linked_metadata_path = root / "linked-metadata.json"
        linked_metadata_path.symlink_to(metadata)
        linked_metadata_run = subprocess.run(
            [sys.executable, str(TOOL), str(source), "--archive", str(archive),
             "--metadata", str(linked_metadata_path)],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        assert linked_metadata_run.returncode != 0
        assert "metadata path" in linked_metadata_run.stderr
        linked_metadata_parent = root / "linked-metadata-parent"
        linked_metadata_parent.symlink_to(root, target_is_directory=True)
        linked_metadata_parent_run = subprocess.run(
            [sys.executable, str(TOOL), str(source), "--archive", str(archive),
             "--metadata", str(linked_metadata_parent / "nested.json")],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        assert linked_metadata_parent_run.returncode != 0
        assert "metadata path" in linked_metadata_parent_run.stderr
        quarantine_root = root / "quarantine-collision-cwd"
        collision_source = quarantine_root / "collision.ndjson"
        collision_archive = quarantine_root / "archive"
        collision_source.parent.mkdir(parents=True)
        collision_source.write_bytes(b"new capture\n")
        collision_target = quarantine_root / "von/build/evidence/quarantine/collision.ndjson"
        collision_target.parent.mkdir(parents=True)
        collision_target.write_bytes(b"old capture\n")
        collision_run = subprocess.run(
            [sys.executable, str(TOOL), str(collision_source), "--archive", str(collision_archive),
             "--quarantine"],
            cwd=quarantine_root, capture_output=True, text=True, check=False,
        )
        assert collision_run.returncode != 0
        assert "quarantine target payload mismatch" in collision_run.stderr
        quarantine_parent_cwd = root / "quarantine-parent-cwd"
        (quarantine_parent_cwd / "von/build").mkdir(parents=True)
        quarantine_real = root / "quarantine-real-evidence"
        quarantine_real.mkdir()
        (quarantine_parent_cwd / "von/build/evidence").symlink_to(
            quarantine_real, target_is_directory=True
        )
        quarantine_parent_run = subprocess.run(
            [sys.executable, str(TOOL), str(source), "--archive", str(root / "quarantine-parent-archive"),
             "--quarantine"],
            cwd=quarantine_parent_cwd, capture_output=True, text=True, check=False,
        )
        assert quarantine_parent_run.returncode != 0
        assert "quarantine directory path" in quarantine_parent_run.stderr
    print("PASS: evidence archive emits reproducible source and blob metadata")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
