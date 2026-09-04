#!/usr/bin/env python3
"""Extract exact SCSP clips from a runtime register-write trace."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import wave
from pathlib import Path


REG = re.compile(
    r"time=(?P<time>[0-9.]+) slot=(?P<slot>[0-9]+) reg=00 value=(?P<value>[0-9a-f]+) "
    r"keyonb=(?P<keyonb>[01]) keyonex=(?P<keyonex>[01]) sa=(?P<sa>[0-9a-f]+) "
    r"lsa=(?P<lsa>[0-9a-f]+) lea=(?P<lea>[0-9a-f]+) pcm8=(?P<pcm8>[01]) "
    r"oct=(?P<oct>[0-9a-f]+) fns=(?P<fns>[0-9a-f]+) tl=(?P<tl>[0-9a-f]+)"
)
GENERIC_REG = re.compile(
    r"time=(?P<time>[0-9.]+) slot=(?P<slot>[0-9]+) reg=(?P<reg>[0-9a-f]+) value=(?P<value>[0-9a-f]+)"
)


def swap_words(data: bytes) -> bytes:
    if len(data) % 2:
        raise ValueError("sample ROMs must have even length")
    return b"".join(data[i + 1:i + 2] + data[i:i + 1]
                    for i in range(0, len(data), 2))


def pcm8_to_wav_pcm(data: bytes) -> bytes:
    return b"".join(((value - 256 if value >= 128 else value) << 8).to_bytes(
        2, "little", signed=True) for value in data)


def write_wav(path: Path, pcm: bytes, rate: int) -> None:
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(rate)
        output.writeframes(pcm)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("trace", type=Path, help="filtered vonj_scsp_reg log")
    parser.add_argument("sample_roms", nargs=2, type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument("--rate", type=int, default=88200)
    parser.add_argument("--min-time", type=float, default=0.0,
                        help="ignore key-ons before this trace time")
    args = parser.parse_args()
    if args.rate <= 0:
        parser.error("--rate must be positive")

    trace_bytes = args.trace.read_bytes()
    physical_roms = [path.read_bytes() for path in args.sample_roms]
    sample = swap_words(b"".join(physical_roms))
    descriptors = []
    register_state: dict[int, dict[int, int]] = {}
    active_events: dict[int, dict] = {}
    # The MAME oslog path escapes newlines as the two characters ``\\n``
    # before writing them to the log.  Normalize those record separators first;
    # otherwise splitlines() sees only the first SCSP write in each batch.
    trace_text = args.trace.read_text(errors="replace").replace("\\n", "\n")
    for line_number, line in enumerate(trace_text.splitlines(), 1):
        generic = GENERIC_REG.search(line)
        if generic:
            slot = int(generic["slot"])
            reg = int(generic["reg"], 16)
            value = int(generic["value"], 16)
            register_state.setdefault(slot, {})[reg] = value
            if reg == 0x10 and slot in active_events:
                active_events[slot].setdefault("pitch_updates", []).append({
                    "time": float(generic["time"]),
                    "oct": (value >> 11) & 0x0f,
                    "fns": value & 0x03ff,
                })
            elif reg in (0x0c, 0x14, 0x16) and slot in active_events:
                active_events[slot].setdefault("state_updates", []).append({
                    "time": float(generic["time"]), "reg": reg, "value": value,
                })
        match = REG.search(line)
        # SCSP uses KEYONEX to commit a voice start. KEYONB-only writes also
        # occur later while a voice is active (for example when LEA changes),
        # and must not be mistaken for new notes.
        if (not match or match["keyonb"] != "1" or match["keyonex"] != "1"
                or float(match["time"]) < args.min_time):
            continue
        item = {key: int(value, 16) if key not in ("time",) else float(value)
                for key, value in match.groupdict().items()}
        item["trace_line"] = line_number
        item["pitch_updates"] = []
        item["state_updates"] = []
        item["loop"] = bool((item["value"] & 0x0060) == 0x0020)
        route_a = register_state.get(item["slot"], {}).get(0x14, 0)
        route_b = register_state.get(item["slot"], {}).get(0x16, 0)
        item["isel"] = (route_a >> 3) & 0x0f
        item["imxl"] = route_a & 0x07
        item["disdl"] = (route_b >> 13) & 0x07
        item["dipan"] = (route_b >> 8) & 0x1f
        # SCSP slot registers are logged by byte offset (the macros in MAME
        # index u16 data[]).  EG parameters therefore live at 08/0a, while
        # TL is at 0c and was already decoded by REG above.
        env_a = register_state.get(item["slot"], {}).get(0x08, 0)
        env_b = register_state.get(item["slot"], {}).get(0x0a, 0)
        item["ar"] = env_a & 0x1f
        item["d1r"] = (env_a >> 6) & 0x1f
        item["d2r"] = (env_a >> 11) & 0x1f
        item["eghold"] = bool(env_a & 0x20)
        item["dl"] = (env_b >> 5) & 0x1f
        item["rr"] = env_b & 0x1f
        item["sdir"] = bool(env_b & 0x100)
        item["stwinh"] = bool(env_b & 0x200)
        item["lpslnk"] = bool(env_b & 0x4000)
        item["krs"] = (env_b >> 10) & 0x0f
        item["start"] = item["sa"]
        item["end"] = item["sa"] + item["lea"]
        item["length_bytes"] = item["lea"]
        item["confidence"] = "authoritative-runtime"
        descriptors.append(item)
        active_events[item["slot"]] = item

    args.output.mkdir(parents=True, exist_ok=True)
    entries = []
    for index, item in enumerate(descriptors):
        start, end = item["start"], item["end"]
        if not (0 <= start < end <= len(sample)):
            item["status"] = "outside-sample-rom"
            entries.append(item)
            continue
        raw = sample[start:end]
        if item["pcm8"]:
            pcm = pcm8_to_wav_pcm(raw)
            frames = len(raw)
        else:
            if len(raw) % 2:
                item["status"] = "odd-pcm16-length"
                entries.append(item)
                continue
            pcm = b"".join(raw[i + 1:i + 2] + raw[i:i + 1]
                            for i in range(0, len(raw), 2))
            frames = len(raw) // 2
        wav = f"{index:04d}-slot-{item['slot']:02d}-sa-{start:06x}-lea-{item['lea']:04x}.wav"
        write_wav(args.output / wav, pcm, args.rate)
        item.update(status="extracted", frames=frames, wav=wav,
                    duration_seconds=frames / args.rate)
        entries.append(item)

    report = {"format": "runtime-scsp", "rate": args.rate,
              "sample_rom_bytes": len(sample), "trace_bytes": len(trace_bytes),
              "trace_sha256": sha256(trace_bytes),
              "sample_roms": [{"path": path.name, "bytes": len(data), "sha256": sha256(data)}
                              for path, data in zip(args.sample_roms, physical_roms)],
              "entries": entries,
              "notes": [
                  "Descriptors are taken from SCSP register writes immediately before key-on.",
                  "SA and LEA are recorded as SCSP byte addresses; lengths are authoritative for the runtime voice.",
                  "Entries are chronological key-on events; repeated notes are retained because their routing and timing matter.",
              ]}
    (args.output / "catalog.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"wrote {args.output / 'catalog.json'} ({len(entries)} runtime descriptors)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
