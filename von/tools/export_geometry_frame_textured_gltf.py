#!/usr/bin/env python3
"""Export one traced geometry frame as a textured, instanced glTF scene."""

from __future__ import annotations

import argparse
import base64
import json
import struct
from pathlib import Path

from export_geometry_frame_gltf import MATRIX, OBJECT
from export_geometry_animation_gltf import transform_trs
from export_geometry_textured_gltf import parse_faces
from model2_texture import (DEFAULT_BANK0, DEFAULT_BANK1, load_banks,
                            texture_sampler, texture_size, texture_uv, tile_png)
from render_texture_palette import parse_trace


IDENTITY = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0,
            0.0, 0.0, 0.0)


def load_frames(trace: Path):
    current = IDENTITY
    frames: dict[float, list[tuple[int, tuple[float, ...], dict[str, int | str]]]] = {}
    for line in trace.read_text().splitlines():
        matrix = MATRIX.search(line)
        if matrix:
            values = tuple(float(value) for value in matrix[2].split(","))
            translation = tuple(float(value) for value in matrix[3].split(","))
            current = values + translation
            continue
        match = OBJECT.search(line)
        if not match:
            continue
        time = float(match[1])
        metadata = {
            "tpa": int(match[2], 16),
            "tha": int(match[3], 16),
            "count": int(match[5], 16),
            "mode": int(match[6]),
            "source": match[7],
        }
        frames.setdefault(time, []).append((int(match[4], 16), current, metadata))
    return frames


def select_frame(frames, requested_time: float | None,
                 max_time: float | None, tolerance: float, min_objects: int):
    candidates = sorted(
        ((time, objects) for time, objects in frames.items()
         if len(objects) >= min_objects and
         (max_time is None or time <= max_time)),
        key=lambda item: item[0],
    )
    if not candidates:
        raise SystemExit("no geometry frames met --min-objects")
    if requested_time is None:
        return candidates[-1]
    selected_time, objects = min(candidates,
                                 key=lambda item: abs(item[0] - requested_time))
    if abs(selected_time - requested_time) > tolerance:
        raise SystemExit(
            f"no frame within {tolerance:g}s of {requested_time:g}; "
            f"nearest is {selected_time:g}"
        )
    return selected_time, objects


def filter_obas(objects, object_slots, raw_list):
    """Keep frame objects whose OBA is in the hex list, preserving order."""
    wanted = set()
    for raw in raw_list:
        try:
            wanted.add(int(raw, 16))
        except ValueError:
            raise SystemExit(f"--oba is not hex: {raw}")
    kept = [(item, slot) for item, slot in zip(objects, object_slots)
            if item[0] in wanted]
    if not kept:
        raise SystemExit("no model obas in frame")
    missing = wanted - {item[0] for item, _ in kept}
    if missing:
        raise SystemExit("frame is missing model obas: " +
                         ", ".join(f"{oba:08x}" for oba in sorted(missing)))
    return zip(*kept)


def gather_obas(frames, anchor_time: float, raw_list):
    """One object per requested OBA, taken from the frame nearest the anchor.

    No single frame shows a complete mech (parts cull in and out), so a model
    exported from one frame is always missing limbs. Prefer the anchor frame
    (a neutral idle/select pose) and fill each missing part from the closest
    frame that shows it, so the model carries its whole part set. The source
    time of every part is returned so a common root can re-base borrowed parts.
    """
    wanted = {int(raw, 16) for raw in raw_list}
    chosen: dict[int, tuple] = {}
    frame_of: dict[int, float] = {}
    for time in sorted(frames, key=lambda t: abs(t - anchor_time)):
        for item in frames[time]:
            if item[0] in wanted and item[0] not in chosen:
                chosen[item[0]] = item
                frame_of[item[0]] = time
    missing = wanted - set(chosen)
    if missing:
        raise SystemExit("no frame shows model obas: " +
                         ", ".join(f"{oba:08x}" for oba in sorted(missing)))
    objects = [chosen[oba] for oba in sorted(chosen)]
    return objects, list(range(len(objects))), frame_of


# The geometry matrix stores the rotation columns (x_axis, y_axis, z_axis) in
# m[0:3]/m[3:6]/m[6:9] with the translation in m[9:12]. Convert to a standard
# row-major rotation so composition is ordinary `parent * local`.
def _rot(m):
    return [m[0], m[3], m[6], m[1], m[4], m[7], m[2], m[5], m[8]]


def _store(rot, tx):
    return [rot[0], rot[3], rot[6], rot[1], rot[4], rot[7],
            rot[2], rot[5], rot[8]] + list(tx)


def _mat3_inverse(a):
    x, y, z, u, v, w, p, q, r = a
    det = x * (v * r - w * q) - y * (u * r - w * p) + z * (u * q - v * p)
    if det == 0.0:
        raise ValueError("singular rigid transform")
    return [(v * r - w * q) / det, (z * q - y * r) / det, (y * w - z * v) / det,
            (w * p - u * r) / det, (x * r - z * p) / det, (z * u - x * w) / det,
            (u * q - v * p) / det, (y * p - x * q) / det, (x * v - y * u) / det]


def rigid_inverse(m):
    rot = _rot(m)
    inv_rot = _mat3_inverse(rot)
    trans = [-sum(inv_rot[r * 3 + c] * m[9 + c] for c in range(3)) for r in range(3)]
    return _store(inv_rot, trans)


def rigid_compose(a, b):
    a_rot, b_rot = _rot(a), _rot(b)
    rot = [sum(a_rot[r * 3 + k] * b_rot[k * 3 + c] for k in range(3))
           for r in range(3) for c in range(3)]
    tx = [sum(a_rot[r * 3 + k] * b[9 + k] for k in range(3)) + a[9 + r]
          for r in range(3)]
    return _store(rot, tx)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--rom", type=Path, default=Path("von/build/disasm/geometry-rom.bin"))
    parser.add_argument("--texture-rom", type=Path,
                        default=Path("von/build/disasm/texture-pipeline/texture-rom.bin"))
    parser.add_argument("--bank0", type=Path, default=Path(DEFAULT_BANK0),
                        help="texture RAM 0 sheet (.bin or MAME .hex dump)")
    parser.add_argument("--bank1", type=Path, default=Path(DEFAULT_BANK1),
                        help="texture RAM 1 sheet (.bin or MAME .hex dump)")
    parser.add_argument("--palette-trace", type=Path,
                        help="optional MAME trace containing palette/colorxlat/luma writes")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--time", type=float,
                        help="timestamp to select; defaults to the latest qualifying frame")
    parser.add_argument("--max-time", type=float)
    parser.add_argument("--tolerance", type=float, default=0.02)
    parser.add_argument("--min-objects", type=int, default=1)
    parser.add_argument("--start-object", type=int, default=0,
                        help="first submitted object slot to export")
    parser.add_argument("--max-objects", type=int,
                        help="maximum submitted object slots to export")
    parser.add_argument("--exclude-object", type=int, action="append", default=[],
                        help="relative object slot to omit after --start-object")
    parser.add_argument("--oba", action="append", default=[],
                        help="hex polygon address to keep (repeatable); "
                             "restricts the frame to a ROM model part list")
    parser.add_argument("--fill-missing", action="store_true",
                        help="with --oba, take each part from the nearest frame "
                             "that shows it (complete model) instead of failing")
    parser.add_argument("--retarget-root", type=lambda s: int(s, 16), default=None,
                        help="OBA used as the common frame; parts borrowed from "
                             "other frames are re-based into the anchor pose of "
                             "this root so the assembled model is coherent")
    args = parser.parse_args()

    frames = load_frames(args.trace)
    selected_time, objects = select_frame(
        frames, args.time, args.max_time, args.tolerance, args.min_objects)
    if args.start_object < 0:
        raise SystemExit("--start-object must be non-negative")
    objects = objects[args.start_object:]
    if args.max_objects is not None:
        if args.max_objects <= 0:
            raise SystemExit("--max-objects must be positive")
        objects = objects[:args.max_objects]
    object_slots = list(range(args.start_object,
                              args.start_object + len(objects)))
    excluded = set(args.exclude_object)
    if any(slot < 0 or slot >= len(objects) for slot in excluded):
        raise SystemExit("--exclude-object is outside the selected object slice")
    objects, object_slots = zip(*[
        (item, slot) for relative_slot, (item, slot) in enumerate(
            zip(objects, object_slots)) if relative_slot not in excluded])
    if not objects:
        raise SystemExit("object slice is empty")
    if args.oba:
        if args.fill_missing:
            objects, object_slots, frame_of = gather_obas(
                frames, selected_time, args.oba)
        else:
            objects, object_slots = filter_obas(objects, object_slots, args.oba)
            frame_of = {}
    else:
        frame_of = {}
    if args.retarget_root is not None and frame_of:
        root_at: dict[float, tuple] = {}
        for time, items in frames.items():
            for item in items:
                if item[0] == args.retarget_root:
                    root_at[time] = item[1]
        if root_at:
            anchor = (root_at[selected_time] if selected_time in root_at else
                      root_at[min(root_at, key=lambda t: abs(t - selected_time))])
            rebased = []
            for oba, matrix, metadata in objects:
                source = root_at.get(frame_of.get(oba, selected_time))
                if source is None:
                    rebased.append((oba, matrix, metadata))
                else:
                    local = rigid_compose(rigid_inverse(source), matrix)
                    rebased.append((oba, rigid_compose(anchor, local), metadata))
            objects = rebased
    geometry = args.rom.read_bytes()
    texture_rom = args.texture_rom.read_bytes()
    banks = load_banks(args.bank0, args.bank1)
    palette_state = (parse_trace(args.palette_trace, selected_time)
                     if args.palette_trace else None)

    blob = bytearray()
    views: list[dict[str, int]] = []
    accessors: list[dict[str, object]] = []
    meshes: list[dict[str, object]] = []
    mesh_by_key: dict[tuple[int, int, int], int] = {}
    materials: list[dict[str, object]] = []
    material_by_header: dict[tuple[int, int, int, int], int] = {}
    images: list[dict[str, str]] = []
    textures: list[dict[str, int]] = []
    texture_by_key: dict[tuple[int, int, int, int], int] = {}
    samplers = []
    sampler_by_mode: dict[tuple[int, int], int] = {}

    def add_blob(data: bytes, target: int | None = None) -> int:
        offset = len(blob)
        blob.extend(data)
        view: dict[str, int] = {"buffer": 0, "byteOffset": offset,
                                "byteLength": len(data)}
        if target is not None:
            view["target"] = target
        views.append(view)
        return len(views) - 1

    def material_for(header: tuple[int, int, int, int]) -> int:
        if header in material_by_header:
            return material_by_header[header]
        width, height, origin_x, origin_y, colorbase = texture_size(header)
        textured = bool(((header[0] >> 13) & 3) & 2)
        image_data = tile_png(header, banks, palette_state) if textured else None
        texture_index = None
        texture_key = (header[0], header[1], header[2], header[3])
        if image_data is not None:
            sampler_mode = texture_sampler(header)
            sampler_index = sampler_by_mode.get(sampler_mode)
            if sampler_index is None:
                sampler_index = len(samplers)
                samplers.append({"magFilter": 9729, "minFilter": 9729,
                                 "wrapS": sampler_mode[0], "wrapT": sampler_mode[1]})
                sampler_by_mode[sampler_mode] = sampler_index
            texture_index = texture_by_key.get(texture_key)
            if texture_index is None:
                image_index = len(images)
                images.append({
                    "uri": "data:image/png;base64," + base64.b64encode(image_data).decode("ascii"),
                    "name": f"tile_{origin_x:04x}_{origin_y:03x}_{width}x{height}",
                })
                texture_index = len(textures)
                textures.append({"sampler": sampler_index, "source": image_index})
                texture_by_key[texture_key] = texture_index
        material: dict[str, object] = {
            "name": f"header_{header[0]:04x}_{header[1]:04x}_{header[2]:04x}_{header[3]:04x}",
            "extras": {"texheader": list(header), "width": width,
                       "height": height, "origin": [origin_x, origin_y],
                       "colorbase": colorbase, "bank": (header[2] >> 12) & 1,
                       "uv_order": ["u", "v"],
                       "uv_units": "1/8 texel", "uv_image_space": "tile-local",
                       "wrap": list(texture_sampler(header))},
        }
        if texture_index is not None:
            material["pbrMetallicRoughness"] = {
                "baseColorFactor": [1, 1, 1, 1], "metallicFactor": 0,
                "roughnessFactor": 1, "baseColorTexture": {"index": texture_index},
            }
        else:
            material["pbrMetallicRoughness"] = {
                "baseColorFactor": [0.65, 0.65, 0.65, 1],
                "metallicFactor": 0, "roughnessFactor": 1,
            }
        material_index = len(materials)
        materials.append(material)
        material_by_header[header] = material_index
        return material_index

    def mesh_for(oba: int, tpa: int, tha: int) -> int:
        key = (oba, tpa, tha)
        if key in mesh_by_key:
            return mesh_by_key[key]
        faces = parse_faces(geometry, texture_rom, oba, tpa, tha)
        primitives_by_header: dict[tuple[int, int, int, int], dict[str, list]] = {}
        for _, points, uv, header in faces:
            entry = primitives_by_header.setdefault(
                header, {"positions": [], "uv": [], "indices": []})
            base = len(entry["positions"])
            entry["positions"].extend(points)
            entry["uv"].extend(texture_uv(u, v, header) for u, v in uv)
            if len(points) == 4:
                entry["indices"].extend((base, base + 1, base + 2,
                                          base, base + 2, base + 3))
            else:
                entry["indices"].extend((base, base + 1, base + 2))
        if not primitives_by_header:
            raise SystemExit(f"object {oba:08x} produced no textured faces")

        mesh_primitives = []
        for header, entry in primitives_by_header.items():
            positions = entry["positions"]
            position_view = add_blob(
                b"".join(struct.pack("<3f", *point) for point in positions), 34962)
            uv_view = add_blob(
                b"".join(struct.pack("<2f", *uv) for uv in entry["uv"]), 34962)
            index_view = add_blob(
                b"".join(struct.pack("<I", index) for index in entry["indices"]), 34963)
            position_accessor = len(accessors)
            accessors.extend([
                {"bufferView": position_view, "componentType": 5126,
                 "count": len(positions), "type": "VEC3",
                 "min": [min(point[i] for point in positions) for i in range(3)],
                 "max": [max(point[i] for point in positions) for i in range(3)]},
                {"bufferView": uv_view, "componentType": 5126,
                 "count": len(entry["uv"]), "type": "VEC2"},
                {"bufferView": index_view, "componentType": 5125,
                 "count": len(entry["indices"]), "type": "SCALAR"},
            ])
            mesh_primitives.append({
                "attributes": {"POSITION": position_accessor,
                               "TEXCOORD_0": position_accessor + 1},
                "indices": position_accessor + 2,
                "material": material_for(header), "mode": 4,
            })
        mesh_index = len(meshes)
        meshes.append({"name": f"oba_{oba:08x}_tpa_{tpa:08x}_tha_{tha:08x}",
                       "primitives": mesh_primitives})
        mesh_by_key[key] = mesh_index
        return mesh_index

    nodes = []
    for slot, (oba, matrix, metadata) in zip(object_slots, objects):
        mesh_index = mesh_for(oba, int(metadata["tpa"]), int(metadata["tha"]))
        rotation, scale = transform_trs(matrix)
        nodes.append({
            "mesh": mesh_index,
            "name": f"slot_{slot:03d}_oba_{oba:08x}",
            "translation": list(matrix[9:12]),
            "rotation": list(rotation),
            "scale": list(scale),
            "extras": {"geometry_object": metadata, "trace_time": selected_time},
        })

    extras = {"trace_time": selected_time, "object_slots": len(objects),
              "start_object": args.start_object,
              "unique_meshes": len(meshes), "material_groups": len(materials),
              "embedded_tiles": len(images),
              "palette_rendered": palette_state is not None}
    if palette_state is not None:
        extras["palette_time"] = selected_time

    document = {
        "asset": {"version": "2.0",
                  "generator": "von export_geometry_frame_textured_gltf.py"},
        "scene": 0,
        "scenes": [{"name": f"geometry_frame_{selected_time:.6f}",
                    "nodes": list(range(len(nodes)))}],
        "nodes": nodes, "meshes": meshes, "materials": materials,
        "images": images, "textures": textures, "samplers": samplers,
        "buffers": [{"byteLength": len(blob),
                     "uri": "data:application/octet-stream;base64," +
                     base64.b64encode(blob).decode("ascii")}],
        "bufferViews": views, "accessors": accessors,
        "extras": extras,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2) + "\n")
    print(f"wrote {len(objects)} object slots, {len(meshes)} meshes, "
          f"{len(materials)} material groups, {len(images)} tiles, "
          f"and timestamp {selected_time:.6f} to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
