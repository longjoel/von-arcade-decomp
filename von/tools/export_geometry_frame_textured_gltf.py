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
from export_geometry_textured_gltf import parse_faces, texture_size, tile_png
from render_texture_palette import parse_trace


IDENTITY = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0,
            0.0, 0.0, 0.0)


def select_frame(trace: Path, requested_time: float | None,
                 max_time: float | None, tolerance: float, min_objects: int):
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--rom", type=Path, default=Path("von/build/disasm/geometry-rom.bin"))
    parser.add_argument("--texture-rom", type=Path,
                        default=Path("von/build/disasm/texture-pipeline/texture-rom.bin"))
    parser.add_argument("--bank-primary", type=Path,
                        default=Path("von/build/disasm/texture-pipeline/bank0-primary.bin"))
    parser.add_argument("--bank-secondary", type=Path,
                        default=Path("von/build/disasm/texture-pipeline/bank0-secondary.bin"))
    parser.add_argument("--palette-trace", type=Path,
                        help="optional MAME trace containing palette/colorxlat/luma writes")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--time", type=float,
                        help="timestamp to select; defaults to the latest qualifying frame")
    parser.add_argument("--max-time", type=float)
    parser.add_argument("--tolerance", type=float, default=0.02)
    parser.add_argument("--min-objects", type=int, default=1)
    args = parser.parse_args()

    selected_time, objects = select_frame(
        args.trace, args.time, args.max_time, args.tolerance, args.min_objects)
    geometry = args.rom.read_bytes()
    texture_rom = args.texture_rom.read_bytes()
    primary = args.bank_primary.read_bytes()
    secondary = args.bank_secondary.read_bytes()
    palette_state = parse_trace(args.palette_trace) if args.palette_trace else None

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
    samplers = [{"magFilter": 9729, "minFilter": 9729,
                 "wrapS": 10497, "wrapT": 10497}]

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
        bank = secondary if header[2] & 0x1000 else primary
        image_data = tile_png(bank, header, palette_state) if textured else None
        texture_index = None
        texture_key = (header[0], header[1], header[2], header[3])
        if image_data is not None:
            texture_index = texture_by_key.get(texture_key)
            if texture_index is None:
                image_index = len(images)
                images.append({
                    "uri": "data:image/png;base64," + base64.b64encode(image_data).decode("ascii"),
                    "name": f"tile_{origin_x:04x}_{origin_y:03x}_{width}x{height}",
                })
                texture_index = len(textures)
                textures.append({"sampler": 0, "source": image_index})
                texture_by_key[texture_key] = texture_index
        material: dict[str, object] = {
            "name": f"header_{header[0]:04x}_{header[1]:04x}_{header[2]:04x}_{header[3]:04x}",
            "extras": {"texheader": list(header), "width": width,
                       "height": height, "origin": [origin_x, origin_y],
                       "colorbase": colorbase},
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
            entry["uv"].extend((u / 8.0 / texture_size(header)[0],
                                 v / 8.0 / texture_size(header)[1])
                                for u, v in uv)
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
    for slot, (oba, matrix, metadata) in enumerate(objects):
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
        "extras": {"trace_time": selected_time, "object_slots": len(objects),
                   "unique_meshes": len(meshes), "material_groups": len(materials),
                   "embedded_tiles": len(images),
                   "palette_rendered": palette_state is not None},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2) + "\n")
    print(f"wrote {len(objects)} object slots, {len(meshes)} meshes, "
          f"{len(materials)} material groups, {len(images)} tiles, "
          f"and timestamp {selected_time:.6f} to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
