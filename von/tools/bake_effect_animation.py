#!/usr/bin/env python3
"""Bake an arcade weapon/effect OBA stream into a Godot-playable animation.

Weapon and effect visuals in the Model 2 game are per-frame mesh sequences: an
effect's object OBA pointer advances every frame, so each frame is a distinct
polygon object (its own geometry and texture header), not a moving static mesh.
This tool reconstructs that sequence from a geometry capture.

It scans a `vonj_geometry_object` trace for objects whose OBA family byte
matches `--family`, splits them into contiguous spawn runs (a projectile or
muzzle flash lives ~1 frame per tick), groups runs by their first OBA, and bakes
the longest run of each group. For every frame it parses the polygon geometry
(`export_geometry_textured_gltf.parse_faces`) and crops the referenced texture
tile through the captured palette state, then writes a compact JSON:

    von-effect-bake/1
      family, frame_seconds, sequences[]
        start_oba, kind, frames[]
          positions, uvs, indices, texture (base64 PNG), header

The Godot side (scripts/von_effect_library.gd) builds an ArrayMesh per frame
and plays the sequence by projectile age.

Usage:
    python3 von/tools/bake_effect_animation.py --family 0x9b \
        --trace von/captures/attract-20260912T/mame.log --out effect-009b.json
"""
from __future__ import annotations

import argparse
import base64
import json
import re
import struct
import sys
import zlib
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_geometry_animation_gltf import transform_trs  # noqa: E402
from export_geometry_frame_gltf import MATRIX, OBJECT  # noqa: E402
from export_geometry_textured_gltf import parse_faces  # noqa: E402
from model2_texture import (DEFAULT_BANK0, DEFAULT_BANK1, load_banks,  # noqa: E402
                            select_sheet, texel_index, texture_size,
                            texture_uv)

SCHEMA = "von-effect-bake/1"

_PALETTE = re.compile(
    r"vonj_palette_write: (?:time=[0-9.e+-]+ )?offset=([0-9a-f]+).*value=([0-9a-f]+)")
_COLORXLAT = re.compile(
    r"vonj_colorxlat_write: (?:time=[0-9.e+-]+ )?offset=([0-9a-f]+).*value=([0-9a-f]+)")
_LUMA = re.compile(
    r"vonj_luma_write: (?:time=[0-9.e+-]+ )?offset=([0-9a-f]+) data=([0-9a-f]+)")
_TIME = re.compile(r"(?:^| )time=([0-9.e+-]+)(?: |$)")


def family_of(oba: int) -> int:
    return (oba >> 16) & 0xFF


def load_objects(trace: Path, family: int):
    """Return object rows for one OBA family, time-sorted.

    Each row is (time, oba, tpa, tha, world_translation, matrix). The matrix is
    the object's world transform; its rotation and scale are part of the effect
    (a bolt is oriented along its flight and stretched as it grows).
    """
    current = (0.0, 0.0, 0.0)
    rotation = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)
    rows = []
    with trace.open(errors="ignore") as handle:
        for line in handle:
            matrix = MATRIX.search(line)
            if matrix:
                rotation = tuple(float(value) for value in matrix[2].split(","))
                current = tuple(float(value) for value in matrix[3].split(","))
                continue
            match = OBJECT.search(line)
            if not match:
                continue
            oba = int(match[4], 16)
            if family_of(oba) != family:
                continue
            rows.append((float(match[1]), oba, int(match[2], 16),
                         int(match[3], 16), current, rotation))
    rows.sort(key=lambda row: row[0])
    return rows


def tick_and_step(rows):
    """Estimate the per-frame interval and the typical per-frame OBA advance."""
    times = sorted({round(row[0], 6) for row in rows})
    gaps = [b - a for a, b in zip(times, times[1:]) if 0.0 < b - a < 0.1]
    gaps.sort()
    tick = gaps[len(gaps) // 10] if len(gaps) > 4 else (gaps[0] if gaps else 1 / 60)
    deltas = []
    previous = None
    for row in rows:
        time, oba = row[0], row[1]
        if previous is not None:
            dt = time - previous[0]
            if 0.0 < dt <= tick * 1.6:
                delta = abs(oba - previous[1])
                if delta:
                    deltas.append(delta)
        previous = (time, oba)
    deltas.sort()
    step = deltas[len(deltas) // 5] if deltas else 1
    return tick, max(1, step)


def reconstruct_instance(rows, tick, step):
    """Return the longest single instance as time-ordered row indices.

    Objects from every overlapping spawn share one trace, so an instance is
    rebuilt as the longest chain of objects that are one frame apart in time
    and one mesh-record step apart in OBA, holding a single pointer direction.
    """
    count = len(rows)
    length = [1] * count
    back = [-1] * count
    direction = [0] * count
    low, high = 0.4 * step, 3.0 * step
    for i in range(count):
        time_i, oba_i = rows[i][0], rows[i][1]
        best_len, best_j, best_sign, best_err = 0, -1, 0, float("inf")
        for j in range(i - 1, max(-1, i - 96), -1):
            dt = time_i - rows[j][0]
            if dt < 0.25 * tick:
                continue
            if dt > 2.5 * tick:
                break
            delta = oba_i - rows[j][1]
            magnitude = abs(delta)
            if magnitude < low or magnitude > high:
                continue
            sign = 1 if delta > 0 else -1
            if direction[j] != 0 and direction[j] != sign:
                continue
            err = abs(magnitude - step)
            if length[j] > best_len or (length[j] == best_len and err < best_err):
                best_len, best_j, best_sign, best_err = length[j], j, sign, err
        length[i] = best_len + 1
        back[i] = best_j
        direction[i] = best_sign if best_j >= 0 else 0
    end = max(range(count), key=lambda i: length[i])
    chain = []
    while end != -1:
        chain.append(end)
        end = back[end]
    chain.reverse()
    return chain


def dominant_stream(rows):
    """Longest single effect instance as a frame-ordered row list."""
    if len(rows) < 2:
        return [], []
    tick, step = tick_and_step(rows)
    chain = reconstruct_instance(rows, tick, step)
    return [rows[index] for index in chain], [(rows[index][1], tick) for index in chain]


class Palettes:
    """Palette state at a time, applied incrementally as queries advance."""

    def __init__(self, trace: Path):
        events = defaultdict(list)
        if trace is not None:
            with trace.open(errors="ignore") as handle:
                for line in handle:
                    stamp = _TIME.search(line)
                    if not stamp:
                        continue
                    time = float(stamp[1])
                    for kind, pattern in (("p", _PALETTE), ("c", _COLORXLAT),
                                          ("l", _LUMA)):
                        found = pattern.search(line)
                        if found:
                            events[time].append(
                                (kind, int(found[1], 16), int(found[2], 16)))
                            break
        self._times = sorted(events)
        self._events = events
        self._cursor = 0
        self.palette: dict[int, int] = {}
        self.colorxlat: dict[int, int] = {}
        self.luma: dict[int, int] = {}

    def at(self, time: float):
        while self._cursor < len(self._times) and self._times[self._cursor] <= time:
            for kind, offset, value in self._events[self._times[self._cursor]]:
                if kind == "p":
                    self.palette[offset] = value
                elif kind == "c":
                    self.colorxlat[offset] = value
                else:
                    self.luma[offset] = value
            self._cursor += 1
        return self.palette, self.colorxlat, self.luma


def png_rgba(width: int, height: int, pixels: bytes) -> bytes:
    def chunk(name: bytes, payload: bytes) -> bytes:
        return (struct.pack(">I", len(payload)) + name + payload +
                struct.pack(">I", zlib.crc32(name + payload) & 0xffffffff))

    rows = b"".join(b"\x00" + pixels[row * width * 4:(row + 1) * width * 4]
                    for row in range(height))
    return (b"\x89PNG\r\n\x1a\n" +
            chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)) +
            chunk(b"IDAT", zlib.compress(rows, 9)) + chunk(b"IEND", b""))


def tile_png_rgba(header, banks, palette_state):
    """Crop one tile as RGBA, mapping Model 2 texel index 0 to transparent."""
    width, height, origin_x, origin_y, colorbase = texture_size(header)
    if width > 2048 or height > 1024:
        return None
    sheet = select_sheet(header, banks)
    indices = [texel_index(sheet, origin_x + x, origin_y + y)
               for y in range(height) for x in range(width)]
    pixels = bytearray()
    if palette_state is None:
        for index in indices:
            value = index * 17
            pixels += bytes((value, value, value, 0 if index == 0 else 255))
    else:
        from render_texture_palette import palette_rgb
        palette, colorxlat, luma = palette_state
        for index in indices:
            red, green, blue = palette_rgb(index, colorbase, palette,
                                           colorxlat, luma)
            pixels += bytes((red, green, blue, 0 if index == 0 else 255))
    return png_rgba(width, height, bytes(pixels))


def bake_frame(geometry: bytes, texture_rom: bytes, banks, palette_state,
               oba: int, tpa: int, tha: int):
    """Return [(header, positions, uvs, indices, png_bytes)] for one frame."""
    faces = parse_faces(geometry, texture_rom, oba, tpa, tha)
    groups: dict[tuple[int, int, int, int], dict] = {}
    order: list[tuple[int, int, int, int]] = []
    for _, points, uv, header in faces:
        entry = groups.get(header)
        if entry is None:
            entry = {"positions": [], "uvs": [], "indices": []}
            groups[header] = entry
            order.append(header)
        base = len(entry["positions"])
        entry["positions"].extend(points)
        entry["uvs"].extend(texture_uv(u, v, header) for u, v in uv)
        if len(points) == 4:
            entry["indices"].extend((base, base + 1, base + 2,
                                     base, base + 2, base + 3))
        else:
            entry["indices"].extend((base, base + 1, base + 2))
    baked = []
    for header in order:
        entry = groups[header]
        png = tile_png_rgba(header, banks, palette_state)
        baked.append({
            "header": list(header),
            "positions": [round(value, 4) for point in entry["positions"]
                          for value in point],
            "uvs": [round(value, 6) for pair in entry["uvs"] for value in pair],
            "indices": entry["indices"],
            "bytes": sum(len(point) for point in entry["positions"]),
            "texture": ("data:image/png;base64," +
                        base64.b64encode(png).decode("ascii")) if png else "",
        })
    return baked


def _travel_dir(worlds):
    """Unit direction of an instance's world motion (its authored forward)."""
    if len(worlds) < 2:
        return (0.0, 0.0, 1.0)
    start, end = worlds[0], worlds[-1]
    direction = [end[index] - start[index] for index in range(3)]
    length = sum(value * value for value in direction) ** 0.5
    if length < 1e-6:
        return (0.0, 0.0, 1.0)
    return tuple(value / length for value in direction)


def sequence_kind(worlds, span):
    """Classify a stream by how far its world translation travels."""
    if not worlds:
        return "effect", 0.0
    start, end = worlds[0], worlds[-1]
    distance = sum((end[i] - start[i]) ** 2 for i in range(3)) ** 0.5
    return ("projectile" if distance > 24.0 else
            "muzzle" if span < 0.2 else "effect"), round(distance, 2)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--family", required=True,
                        help="effect OBA family byte in hex, e.g. 0x9b")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--rom", type=Path,
                        default=Path("von/build/disasm/geometry-rom.bin"))
    parser.add_argument("--texture-rom", type=Path,
                        default=Path("von/build/disasm/texture-pipeline/texture-rom.bin"))
    parser.add_argument("--bank0", type=Path, default=Path(DEFAULT_BANK0))
    parser.add_argument("--bank1", type=Path, default=Path(DEFAULT_BANK1))
    parser.add_argument("--palette-trace", type=Path,
                        help="trace containing vonj palette/colorxlat/luma writes")
    parser.add_argument("--max-frames", type=int, default=0,
                        help="truncate the stream (0 keeps all)")
    parser.add_argument("--list", action="store_true",
                        help="list the dominant stream and exit (diagnostic)")
    args = parser.parse_args()

    family = int(args.family, 16)
    rows = load_objects(args.trace, family)
    if not rows:
        raise SystemExit(f"no objects for family {family:#04x} in {args.trace}")
    chain, diagnostics = dominant_stream(rows)
    if args.list:
        for oba, value in diagnostics:
            print(f"  {oba:08x} x{value}")
        return 0
    if len(chain) < 2:
        raise SystemExit(f"family {family:#04x}: no multi-frame stream found")

    geometry = args.rom.read_bytes()
    texture_rom = args.texture_rom.read_bytes()
    banks = load_banks(args.bank0, args.bank1)
    palettes = Palettes(args.palette_trace)

    if args.max_frames and len(chain) > args.max_frames:
        chain = chain[:args.max_frames]
    frames = []
    worlds = []
    for time, oba, tpa, tha, world, matrix in chain:
        groups = bake_frame(geometry, texture_rom, banks,
                            palettes.at(time), oba, tpa, tha)
        rotation, scale = transform_trs(matrix)
        worlds.append(world)
        frames.append({
            "oba": f"{oba:08x}", "tpa": f"{tpa:08x}", "tha": f"{tha:08x}",
            "time": round(time, 6),
            "world": [round(value, 3) for value in world],
            # The object's world orientation and per-frame stretch, so the host
            # can point the effect along the projectile's velocity and scale it.
            "rotation": [round(value, 6) for value in rotation],
            "scale": [round(value, 5) for value in scale],
            "groups": groups,
        })
    gaps = sorted(chain[i + 1][0] - chain[i][0] for i in range(len(chain) - 1))
    step = gaps[len(gaps) // 2] if gaps else 1.0 / 60.0
    span = chain[-1][0] - chain[0][0]
    kind, distance = sequence_kind(worlds, span)
    sequences = [{
        "start_oba": f"{chain[0][1]:08x}",
        "kind": kind,
        "displacement": distance,
        "frame_seconds": round(step, 6),
        "travel": [round(value, 6) for value in _travel_dir(worlds)],
        "frames": frames,
    }]
    total_bytes = sum(group["bytes"] for frame in frames
                      for group in frame["groups"])
    print(f"{chain[0][1]:08x} kind={kind:10} frames={len(frames):3d} "
          f"displacement={distance:8.2f} verts={total_bytes} "
          f"step={step:.5f}s")

    document = {
        "schema": SCHEMA,
        "family": family,
        "source": str(args.trace),
        "sequences": sequences,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(document) + "\n")
    print(f"wrote {len(sequences)} sequence(s) to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
