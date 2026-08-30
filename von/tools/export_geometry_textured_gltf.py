#!/usr/bin/env python3
"""Export one mode-3 polygon object with recovered UVs and texture tiles."""

from __future__ import annotations

import argparse
import base64
import json
import struct
import zlib
from pathlib import Path

from export_geometry_obj import point, words


def u16(data: bytes, address: int) -> int:
    offset = address * 2
    if offset + 2 > len(data):
        raise ValueError(f"texture address {address:#x} is outside the texture ROM")
    return int.from_bytes(data[offset:offset + 2], "little")


def texture_header(data: bytes, address: int) -> tuple[int, int, int, int]:
    return tuple(u16(data, address + index) for index in range(4))


def texture_size(header: tuple[int, int, int, int]) -> tuple[int, int, int, int, int]:
    h0, _, h2, h3 = header
    width = 32 << (h0 & 7)
    height = 32 << ((h0 >> 3) & 7)
    origin_x = 32 * (h2 & 0x3f)
    origin_y = 32 * ((h2 >> 6) & 0x1f)
    colorbase = (h3 >> 6) & 0x3ff
    return width, height, origin_x, origin_y, colorbase


def png_gray(width: int, height: int, pixels: bytes) -> bytes:
    def chunk(name: bytes, payload: bytes) -> bytes:
        return (struct.pack(">I", len(payload)) + name + payload +
                struct.pack(">I", zlib.crc32(name + payload) & 0xffffffff))

    rows = b"".join(b"\x00" + pixels[row * width:(row + 1) * width]
                   for row in range(height))
    return (b"\x89PNG\r\n\x1a\n" +
            chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0)) +
            chunk(b"IDAT", zlib.compress(rows, 9)) + chunk(b"IEND", b""))


def texel(bank: bytes, x: int, y: int) -> int:
    x &= 2047
    y &= 1023
    offset = (y // 2) * 512 + (x // 2)
    word = int.from_bytes(bank[(offset >> 1) * 4:(offset >> 1) * 4 + 4], "little")
    if offset & 1:
        word >>= 16
    if not (y & 1):
        word >>= 8
    if not (x & 1):
        word >>= 4
    return (word & 0x0f) * 17


def tile_png(bank: bytes, header: tuple[int, int, int, int]) -> bytes | None:
    width, height, origin_x, origin_y, _ = texture_size(header)
    if width > 2048 or height > 1024:
        return None
    pixels = bytes(texel(bank, origin_x + x, origin_y + y)
                   for y in range(height) for x in range(width))
    return png_gray(width, height, pixels)


def parse_faces(geometry: bytes, texture_data: bytes, oba: int, tpa: int, tha: int):
    values = words(geometry, oba & 0x3fffff, 0x4000)
    cursor = 0
    p0, cursor = point(values, cursor)
    p1, cursor = point(values, cursor)
    uv_address = tpa
    header_address = tha
    faces = []
    while cursor < len(values):
        attr = values[cursor]
        cursor += 1
        if (attr & 3) == 0 or cursor + 6 > len(values):
            break
        cursor += 3
        p2, cursor = point(values, cursor)
        if attr & 1:
            p3, cursor = point(values, cursor)
            points = (p0, p1, p2, p3)
        else:
            cursor += 3
            points = (p0, p1, p2)

        uv = []
        for _ in points:
            pv = u16(texture_data, uv_address)
            pu = u16(texture_data, uv_address + 1)
            uv.append((pu, pv))
            uv_address += 2
        header = texture_header(texture_data, header_address)
        header_offset = (attr >> 12) & 0x1f
        if header_offset & 0x10:
            header_offset -= 32
        header_address += header_offset * 4
        faces.append((attr, points, uv, header))

        link = (attr >> 8) & 3
        if link in (0, 2):
            p0, p1 = p2, points[-1]
        elif link == 1:
            p1 = p2
        else:
            p0 = points[-1]
    return faces


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", type=Path, default=Path("von/build/disasm/geometry-rom.bin"))
    parser.add_argument("--texture-rom", type=Path,
                        default=Path("von/build/disasm/texture-pipeline/texture-rom.bin"))
    parser.add_argument("--bank-primary", type=Path,
                        default=Path("von/build/disasm/texture-pipeline/bank0-primary.bin"))
    parser.add_argument("--bank-secondary", type=Path,
                        default=Path("von/build/disasm/texture-pipeline/bank0-secondary.bin"))
    parser.add_argument("--oba", type=lambda value: int(value, 0), required=True)
    parser.add_argument("--tpa", type=lambda value: int(value, 0), required=True)
    parser.add_argument("--tha", type=lambda value: int(value, 0), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    texture_data = args.texture_rom.read_bytes()
    geometry = args.rom.read_bytes()
    primary = args.bank_primary.read_bytes()
    secondary = args.bank_secondary.read_bytes()
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
        width, height, _, _, _ = texture_size(header)
        for index in range(len(points)):
            entry["positions"].append(points[index])
            entry["uv"].append((uv[index][0] / 8.0 / width,
                                uv[index][1] / 8.0 / height))
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
    samplers = [{"magFilter": 9729, "minFilter": 9729, "wrapS": 10497, "wrapT": 10497}]
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
        bank = secondary if header[2] & 0x1000 else primary
        image_data = tile_png(bank, header) if textured else None
        texture_index = None
        if image_data is not None:
            image_index = len(images)
            images.append({"uri": "data:image/png;base64," + base64.b64encode(image_data).decode("ascii"),
                           "name": f"tile_{origin_x:04x}_{origin_y:03x}_{width}x{height}"})
            texture_index = len(textures)
            textures.append({"sampler": 0, "source": image_index})
        material = {"name": f"header_{header[0]:04x}_{header[1]:04x}_{header[2]:04x}_{header[3]:04x}",
                    "extras": {"texheader": list(header), "width": width, "height": height,
                               "origin": [origin_x, origin_y], "colorbase": colorbase}}
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

    document = {
        "asset": {"version": "2.0", "generator": "von export_geometry_textured_gltf.py"},
        "scene": 0, "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0, "name": f"oba_{args.oba:08x}"}],
        "meshes": [{"name": f"oba_{args.oba:08x}", "primitives": mesh_primitives}],
        "materials": materials, "images": images, "textures": textures, "samplers": samplers,
        "buffers": [{"byteLength": len(blob), "uri": "data:application/octet-stream;base64," +
                     base64.b64encode(blob).decode("ascii")}],
        "bufferViews": views, "accessors": accessors,
        "extras": {"oba": args.oba, "tpa": args.tpa, "tha": args.tha,
                   "faces": len(faces), "textured_materials": sum(bool(x) for x in textures)},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2) + "\n")
    print(f"wrote {len(faces)} faces, {len(materials)} materials, and {len(images)} embedded tiles to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
