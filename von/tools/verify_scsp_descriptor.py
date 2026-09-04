#!/usr/bin/env python3
"""Verify exact PCM/WAV output for runtime SCSP sample descriptors."""

from __future__ import annotations

import argparse
import hashlib
import json
import wave
from pathlib import Path
from typing import Any


def swap_words(data: bytes) -> bytes:
    if len(data) % 2:
        raise ValueError("sample ROMs must have even length")
    return b"".join(data[index + 1:index + 2] + data[index:index + 1]
                    for index in range(0, len(data), 2))


def pcm8_to_pcm16(data: bytes) -> bytes:
    return b"".join(((value - 256 if value >= 128 else value) << 8).to_bytes(
        2, "little", signed=True) for value in data)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def expected_pcm(sample: bytes, entry: dict[str, Any]) -> tuple[bytes, int]:
    start, length = entry.get("sa"), entry.get("lea")
    if not isinstance(start, int) or not isinstance(length, int) or start < 0 or length <= 0:
        raise ValueError("descriptor requires positive integer sa and lea")
    end = start + length
    if end > len(sample):
        raise ValueError("descriptor exceeds sample ROM")
    raw = sample[start:end]
    if entry.get("pcm8"):
        return pcm8_to_pcm16(raw), len(raw)
    if len(raw) % 2:
        raise ValueError("PCM16 descriptor has odd byte length")
    return b"".join(raw[index + 1:index + 2] + raw[index:index + 1]
                    for index in range(0, len(raw), 2)), len(raw) // 2


def validate(catalog: Any, sample: bytes, root: Path) -> list[dict[str, Any]]:
    if not isinstance(catalog, dict) or catalog.get("format") != "runtime-scsp":
        raise ValueError("catalog must be a runtime-scsp object")
    rate = catalog.get("rate")
    entries = catalog.get("entries")
    if not isinstance(rate, int) or isinstance(rate, bool) or rate <= 0:
        raise ValueError("catalog rate must be a positive integer")
    if not isinstance(entries, list) or not entries:
        raise ValueError("catalog entries must be a non-empty array")
    if catalog.get("sample_rom_bytes") is not None and catalog.get("sample_rom_bytes") != len(sample):
        raise ValueError("catalog sample_rom_bytes does not match supplied ROMs")
    results: list[dict[str, Any]] = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ValueError(f"entries[{index}] must be an object")
        if entry.get("status") != "extracted":
            raise ValueError(f"entries[{index}] is not an extracted descriptor")
        wav_name = entry.get("wav")
        if not isinstance(wav_name, str) or not wav_name or Path(wav_name).is_absolute() \
                or ".." in Path(wav_name).parts:
            raise ValueError(f"entries[{index}] wav must be a safe relative path")
        wav_path = root / wav_name
        if not wav_path.is_file():
            raise ValueError(f"entries[{index}] missing WAV {wav_name}")
        try:
            pcm, frames = expected_pcm(sample, entry)
        except ValueError as error:
            raise ValueError(f"entries[{index}]: {error}") from error
        with wave.open(str(wav_path), "rb") as wav:
            if wav.getnchannels() != 1 or wav.getsampwidth() != 2 or wav.getframerate() != rate:
                raise ValueError(f"entries[{index}] WAV metadata does not match catalog")
            if wav.getnframes() != frames:
                raise ValueError(f"entries[{index}] WAV frame count does not match descriptor")
            actual = wav.readframes(wav.getnframes())
        if actual != pcm:
            raise ValueError(f"entries[{index}] WAV PCM does not match sample ROM descriptor")
        lsa = entry.get("lsa")
        if not isinstance(lsa, int) or lsa < 0 or lsa > entry["lea"]:
            raise ValueError(f"entries[{index}] LSA must be within LEA")
        results.append({
            "index": index, "slot": entry.get("slot"), "wav": wav_name,
            "pcm_sha256": sha256(actual), "frames": frames,
            "claims": {"audio_descriptor": "validated", "source_bytes": "validated",
                        "identity": "candidate"},
        })
    return results


def validate_rom_inputs(catalog: dict[str, Any], paths: list[Path], data: list[bytes]) -> None:
    declared = catalog.get("sample_roms")
    if declared is None:
        return
    if not isinstance(declared, list) or len(declared) != len(paths):
        raise ValueError("catalog sample_roms does not match supplied ROM count")
    for index, (item, path, payload) in enumerate(zip(declared, paths, data)):
        if not isinstance(item, dict) or item.get("path") != path.name:
            raise ValueError(f"sample ROM {index} path does not match catalog")
        if item.get("bytes") != len(payload) or item.get("sha256") != sha256(payload):
            raise ValueError(f"sample ROM {index} hash or size does not match catalog")


def validate_trace_input(catalog: dict[str, Any], path: Path | None, data: bytes | None) -> None:
    declared_hash = catalog.get("trace_sha256")
    if declared_hash is None:
        return
    if path is None or data is None:
        raise ValueError("catalog declares trace provenance but no trace was supplied")
    if catalog.get("trace_bytes") != len(data) or declared_hash != sha256(data):
        raise ValueError("trace hash or size does not match catalog")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--trace", type=Path,
                        help="runtime trace whose hash is declared by the catalog")
    parser.add_argument("--sample-rom", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        catalog_bytes = args.catalog.read_bytes()
        catalog = json.loads(catalog_bytes)
        trace_data = args.trace.read_bytes() if args.trace else None
        validate_trace_input(catalog, args.trace, trace_data)
        physical_roms = [path.read_bytes() for path in args.sample_rom]
        validate_rom_inputs(catalog, args.sample_rom, physical_roms)
        sample = swap_words(b"".join(physical_roms))
        entries = validate(catalog, sample, args.catalog.parent)
        report = {"schema_version": 1, "status": "validated", "catalog_sha256": sha256(catalog_bytes),
                  "sample_rom_sha256": sha256(sample),
                  "trace_sha256": sha256(trace_data) if trace_data is not None else None,
                  "sample_roms": [{"path": path.name, "sha256": sha256(data), "bytes": len(data)}
                                  for path, data in zip(args.sample_rom, physical_roms)],
                  "entries": entries}
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    except (OSError, json.JSONDecodeError, ValueError, wave.Error) as error:
        print(f"SCSP descriptor verification: {error}")
        return 1
    print(f"SCSP descriptor verification: {len(entries)} descriptor(s) validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
