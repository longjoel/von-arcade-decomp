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
        malformed = {"schema_version": 1, "source": [], "archive": {}}
        assert any("source metadata must be an object" in error
                   for error in validate_metadata(malformed))
    print("PASS: evidence archive emits reproducible source and blob metadata")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
