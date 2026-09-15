#!/usr/bin/env python3
"""Export one mode-3 polygon object with recovered UVs and texture tiles.

The geometry is read from the polygon ROM; each texture is cropped from the
header-selected Model 2 texture RAM (see ``model2_texture``). Pass the RAM state
that was live while the geometry was drawn via ``--bank0`` / ``--bank1`` (a raw
1 MiB ``.bin`` sheet or a MAME ``.hex`` dump).
"""

from __future__ import annotations

import argparse
import base64
import json
import struct
from pathlib import Path

from export_geometry_obj import point, words
from model2_texture import (DEFAULT_BANK0, DEFAULT_BANK1, load_banks, texel,
                            texel_index, texture_sampler, texture_sheet_xy,
                            texture_size, texture_uv, tile_png)
from render_texture_palette import parse_trace

__all__ = [
    "parse_faces", "raster_vertices", "texture_sampler", "texture_size",
    "texture_uv", "texel", "texel_index", "tile_png",
]


def u16(data: bytes, address: int) -> int:
    offset = address * 2
    if offset + 2 > len(data):
        raise ValueError(f"texture address {address:#x} is outside the texture ROM")
    return int.from_bytes(data[offset:offset + 2], "little")


def texture_header(data: bytes, address: int) -> tuple[int, int, int, int]:
    return tuple(u16(data, address + index) for index in range(4))


def raster_vertices(points: tuple[tuple[float, float, float], ...]
                    ) -> tuple[tuple[float, float, float], ...]:
    """Return vertices in the Model 2 rasterizer order.

    Polygon records carry P0 then P1, but the rasterizer assigns those to V1
    then V0. UV records are subsequently read as V0, V1, V2, V3, so this swap
    is essential to keep positions and UVs paired.
    """
    return (points[1], points[0], *points[2:])


def parse_faces(geometry: bytes, texture_data: bytes, oba: int, tpa: int, tha: int,
                include_link0: bool = False):
    # The record list ends at its (attr & 3) == 0 terminator; use a window far
    # larger than any observed strip instead of a fixed 0x4000-word cap.
    values = words(geometry, oba & 0x3fffff, 0x40000)
    cursor = 0
    p0, cursor = point(values, cursor)
    p1, cursor = point(values, cursor)
    uv_address = tpa
    header_address = tha
    faces = []
    while cursor < len(values):
        attr = values[cursor]
        cursor += 1
        if (attr & 3) == 0:
            break
        # Every record is 10 words: attr + normal(3) + P0(n)(3) + P1(n)(3).
        # Triangles still carry the third slot (reserved), so the stride is 9
        # words after the attribute in all cases.
        if cursor + 9 > len(values):
            break
        cursor += 3
        p2, cursor = point(values, cursor)
        if attr & 1:
            p3, cursor = point(values, cursor)
            points = raster_vertices((p0, p1, p2, p3))
        else:
            cursor += 3
            p3 = p2
            points = raster_vertices((p0, p1, p2))

        # Texture points and the header are consumed even when the hardware
        # culls the polygon (MAME reads them before check_culling).
        uv = []
        for _ in points:
            pv = u16(texture_data, uv_address)
            pu = u16(texture_data, uv_address + 1)
            uv.append((pu, pv))
            uv_address += 2
        header = texture_header(texture_data, header_address)

        link = (attr >> 8) & 3
        # Hardware culls linktype 0 (model2_v.cpp check_culling); keep the carry.
        if link != 0 or include_link0:
            faces.append((attr, points, uv, header))

        header_offset = (attr >> 12) & 0x1f
        if header_offset & 0x10:
            header_offset -= 32
        header_address += header_offset * 4

        if link in (0, 2):
            p0, p1 = p2, p3
        elif link == 1:
            p1 = p2
        else:
            p0 = p3
    return faces


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", type=Path, default=Path("von/build/disasm/geometry-rom.bin"))
    parser.add_argument("--texture-rom", type=Path,
                        default=Path("von/build/disasm/texture-pipeline/texture-rom.bin"))
    parser.add_argument("--bank0", type=Path, default=Path(DEFAULT_BANK0),
                        help="texture RAM 0 sheet (.bin or MAME .hex dump)")
    parser.add_argument("--bank1", type=Path, default=Path(DEFAULT_BANK1),
                        help="texture RAM 1 sheet (.bin or MAME .hex dump)")
    parser.add_argument("--palette-trace", type=Path,
                        help="optional MAME trace containing palette/colorxlat/luma writes")
    parser.add_argument("--palette-time", type=float,
                        help="use palette state at or before this emulated timestamp")
    parser.add_argument("--oba", type=lambda value: int(value, 0), required=True)
    parser.add_argument("--tpa", type=lambda value: int(value, 0), required=True)
    parser.add_argument("--tha", type=lambda value: int(value, 0), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    texture_data = args.texture_rom.read_bytes()
    geometry = args.rom.read_bytes()
    banks = load_banks(args.bank0, args.bank1)
    palette_state = (parse_trace(args.palette_trace, args.palette_time)
                     if args.palette_trace else None)
    faces = parse_faces(geometry, texture_data, args.oba, args.tpa, args.tha)

    blob = bytearray()
    views = []
    accessors = []
    primitives: dict[tuple[int, int, int, int], dict[str, list]] = {}
    for _, points, uv, header in faces:
        key = header
        entry = primitives.setdefault(key, {"positions": [], "uv": [], "indices": []})
        base = len(entry["positions"])
        if len(points) == 4:
            triangles = ((0, 1, 2), (0, 2, 3))
        else:
            triangles = ((0, 1, 2),)
        for index in range(len(points)):
            entry["positions"].append(points[index])
            entry["uv"].append(texture_uv(uv[index][0], uv[index][1], header))
        for triangle in triangles:
            entry["indices"].extend(base + index for index in triangle)

    def add_blob(data: bytes, target: int | None = None) -> int:
        offset = len(blob)
        blob.extend(data)
        view = {"buffer": 0, "byteOffset": offset, "byteLength": len(data)}
        if target is not None:
            view["target"] = target
        views.append(view)
        return len(views) - 1

    meshes = []
    materials = []
    images = []
    textures = []
    samplers = []
    sampler_by_mode: dict[tuple[int, int], int] = {}
    for material_index, (header, entry) in enumerate(primitives.items()):
        positions = entry["positions"]
        indices = entry["indices"]
        uvs = entry["uv"]
        position_view = add_blob(b"".join(struct.pack("<3f", *p) for p in positions), 34962)
        uv_view = add_blob(b"".join(struct.pack("<2f", *uv) for uv in uvs), 34962)
        index_view = add_blob(b"".join(struct.pack("<I", i) for i in indices), 34963)
        position_accessor = len(accessors)
        minimum = [min(point[i] for point in positions) for i in range(3)]
        maximum = [max(point[i] for point in positions) for i in range(3)]
        accessors.extend([
            {"bufferView": position_view, "componentType": 5126, "count": len(positions),
             "type": "VEC3", "min": minimum, "max": maximum},
            {"bufferView": uv_view, "componentType": 5126, "count": len(uvs), "type": "VEC2"},
            {"bufferView": index_view, "componentType": 5125, "count": len(indices), "type": "SCALAR"},
        ])
        width, height, origin_x, origin_y, colorbase = texture_size(header)
        textured = ((header[0] >> 13) & 3) & 2
        image_data = tile_png(header, banks, palette_state) if textured else None
        texture_index = None
        if image_data is not None:
            sampler_mode = texture_sampler(header)
            sampler_index = sampler_by_mode.get(sampler_mode)
            if sampler_index is None:
                sampler_index = len(samplers)
                samplers.append({"magFilter": 9729, "minFilter": 9729,
                                 "wrapS": sampler_mode[0], "wrapT": sampler_mode[1]})
                sampler_by_mode[sampler_mode] = sampler_index
            image_index = len(images)
            images.append({"uri": "data:image/png;base64," + base64.b64encode(image_data).decode("ascii"),
                           "name": f"tile_{origin_x:04x}_{origin_y:03x}_{width}x{height}"})
            texture_index = len(textures)
            textures.append({"sampler": sampler_index, "source": image_index})
        material = {"name": f"header_{header[0]:04x}_{header[1]:04x}_{header[2]:04x}_{header[3]:04x}",
                    "extras": {"texheader": list(header), "width": width, "height": height,
                               "origin": [origin_x, origin_y], "colorbase": colorbase,
                               "bank": (header[2] >> 12) & 1,
                               "uv_order": ["u", "v"], "uv_units": "1/8 texel",
                               "uv_image_space": "tile-local",
                               "wrap": list(texture_sampler(header))}}
        if texture_index is not None:
            material["pbrMetallicRoughness"] = {
                "baseColorFactor": [1, 1, 1, 1],
                "metallicFactor": 0,
                "roughnessFactor": 1,
                "baseColorTexture": {"index": texture_index},
            }
        else:
            material["pbrMetallicRoughness"] = {
                "baseColorFactor": [0.65, 0.65, 0.65, 1], "metallicFactor": 0, "roughnessFactor": 1}
        materials.append(material)
        primitives[header]["accessors"] = (position_accessor, position_accessor + 1, position_accessor + 2)
        primitives[header]["material"] = material_index

    mesh_primitives = []
    for header, entry in primitives.items():
        position_accessor, uv_accessor, index_accessor = entry["accessors"]
        mesh_primitives.append({"attributes": {"POSITION": position_accessor, "TEXCOORD_0": uv_accessor},
                                "indices": index_accessor, "material": entry["material"], "mode": 4})

    extras = {"oba": args.oba, "tpa": args.tpa, "tha": args.tha,
              "faces": len(faces), "textured_materials": sum(bool(x) for x in textures),
              "palette_rendered": palette_state is not None}
    if args.palette_time is not None:
        extras["palette_time"] = args.palette_time

    document = {
        "asset": {"version": "2.0", "generator": "von export_geometry_textured_gltf.py"},
        "scene": 0, "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0, "name": f"oba_{args.oba:08x}"}],
        "meshes": [{"name": f"oba_{args.oba:08x}", "primitives": mesh_primitives}],
        "materials": materials, "images": images, "textures": textures, "samplers": samplers,
        "buffers": [{"byteLength": len(blob), "uri": "data:application/octet-stream;base64," +
                     base64.b64encode(blob).decode("ascii")}],
        "bufferViews": views, "accessors": accessors,
        "extras": extras,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2) + "\n")
    print(f"wrote {len(faces)} faces, {len(materials)} materials, and {len(images)} embedded tiles to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
