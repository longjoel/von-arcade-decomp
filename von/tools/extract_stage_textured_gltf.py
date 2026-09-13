#!/usr/bin/env python3
"""Export a stage's arena statics as a textured glTF.

The stage manifest (von/i960/stage-arena-obas.json) lists each arena static's
polygon OBA but not its texture addresses. This tool recovers the per-OBA
``tpa``/``tha`` from an instrumented geometry trace (patch 0007) or the curated
``oba_texmap.json``, then decodes UVs and embeds palette-rendered texture tiles
reusing the recovered Model 2 texture pipeline.

    python3 von/tools/extract_stage_textured_gltf.py --stage 3 \
        --trace von/build/disasm/vonj-geometry-select-45s.trace \
        --palette-trace von/build/disasm/vonj-geometry-select-45s.trace \
        --output /tmp/stage_03_arena.gltf
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import struct
from pathlib import Path

from export_geometry_animation_gltf import parse_mesh
from export_geometry_textured_gltf import (parse_faces, texture_sampler,
                                           texture_size, texture_uv, tile_png)
from render_texture_palette import parse_trace


OBJECT = re.compile(
    r"vonj_geometry_object: (?:seq=\d+ )?time=([0-9.e+-]+) "
    r"tpa=([0-9a-f]+) tha=([0-9a-f]+) oba=([0-9a-f]+)"
)


def load_obas(manifest: Path, stage: int) -> list[int]:
    entries = json.loads(manifest.read_text())[str(stage)]
    return [int(e["oba"], 0) for e in entries]


def harvest_textures(trace: Path, texmap: Path | None) -> dict[int, tuple[int, int]]:
    table: dict[int, tuple[int, int]] = {}
    if texmap is not None:
        for oba, pairs in json.loads(texmap.read_text()).items():
            if pairs:
                table.setdefault(int(oba, 16), (int(pairs[0][0]), int(pairs[0][1])))
    if trace is not None:
        for line in trace.read_text().splitlines():
            match = OBJECT.search(line)
            if match:
                oba = int(match[4], 16)
                table.setdefault(oba, (int(match[2], 16), int(match[3], 16)))
    return table


def build(stage: int, manifest: Path, rom: Path, texture_rom: Path,
          primary: Path, secondary: Path, table: dict[int, tuple[int, int]],
          palette_state, include_untextured: bool, bank_source: str = "primary"):
    geometry = rom.read_bytes()
    texture_data = texture_rom.read_bytes()
    bank_primary = primary.read_bytes()
    bank_secondary = secondary.read_bytes()

    blob = bytearray()
    views: list[dict] = []
    accessors: list[dict] = []
    meshes: list[dict] = []
    nodes: list[dict] = []
    materials: list[dict] = []
    material_by_header: dict[tuple[int, int, int, int], int] = {}
    images: list[dict] = []
    textures: list[dict] = []
    texture_by_header: dict[tuple[int, int, int, int], int] = {}
    samplers: list[dict] = []
    sampler_by_mode: dict[tuple[int, int], int] = {}
    missing: list[int] = []
    stats = {"obas": 0, "faces": 0, "textured": 0, "images": 0}

    def add_blob(data: bytes, target: int | None = None) -> int:
        offset = len(blob)
        blob.extend(data)
        view = {"buffer": 0, "byteOffset": offset, "byteLength": len(data)}
        if target is not None:
            view["target"] = target
        views.append(view)
        return len(views) - 1

    def material_for(header) -> int:
        if header in material_by_header:
            return material_by_header[header]
        width, height, origin_x, origin_y, colorbase = texture_size(header)
        textured = bool(((header[0] >> 13) & 3) & 2)
        if bank_source == "header":
            bank = bank_secondary if header[2] & 0x1000 else bank_primary
        else:
            bank = bank_primary
        image_data = tile_png(bank, header, palette_state) if textured else None
        texture_index = None
        if image_data is not None:
            sampler_mode = texture_sampler(header)
            sampler_index = sampler_by_mode.get(sampler_mode)
            if sampler_index is None:
                sampler_index = len(samplers)
                samplers.append({"magFilter": 9729, "minFilter": 9729,
                                 "wrapS": sampler_mode[0], "wrapT": sampler_mode[1]})
                sampler_by_mode[sampler_mode] = sampler_index
            texture_index = texture_by_header.get(header)
            if texture_index is None:
                image_index = len(images)
                images.append({"uri": "data:image/png;base64," +
                                       base64.b64encode(image_data).decode("ascii"),
                               "name": f"tile_{origin_x:04x}_{origin_y:03x}_{width}x{height}"})
                texture_index = len(textures)
                textures.append({"sampler": sampler_index, "source": image_index})
                texture_by_header[header] = texture_index
                stats["images"] += 1
        material = {
            "name": f"header_{header[0]:04x}_{header[1]:04x}_{header[2]:04x}_{header[3]:04x}",
            "extras": {"texheader": list(header), "width": width, "height": height,
                       "origin": [origin_x, origin_y], "colorbase": colorbase,
                       "uv_units": "1/8 texel", "wrap": list(texture_sampler(header))},
        }
        if texture_index is not None:
            material["pbrMetallicRoughness"] = {
                "baseColorFactor": [1, 1, 1, 1], "metallicFactor": 0,
                "roughnessFactor": 1, "baseColorTexture": {"index": texture_index}}
            stats["textured"] += 1
        else:
            material["pbrMetallicRoughness"] = {
                "baseColorFactor": [0.65, 0.65, 0.65, 1], "metallicFactor": 0,
                "roughnessFactor": 1}
        index = len(materials)
        materials.append(material)
        material_by_header[header] = index
        return index

    def default_material() -> int:
        if default_material.index < 0:
            default_material.index = len(materials)
            materials.append({
                "name": "untextured",
                "pbrMetallicRoughness": {"baseColorFactor": [0.65, 0.65, 0.65, 1],
                                         "metallicFactor": 0, "roughnessFactor": 1}})
        return default_material.index
    default_material.index = -1

    def emit_primitive(positions, uvs, indices, header) -> dict | None:
        pos_view = add_blob(b"".join(struct.pack("<3f", *p) for p in positions), 34962)
        idx_view = add_blob(b"".join(struct.pack("<I", i) for i in indices), 34963)
        acc = len(accessors)
        accessors.append({"bufferView": pos_view, "componentType": 5126,
                          "count": len(positions), "type": "VEC3",
                          "min": [min(v[k] for v in positions) for k in range(3)],
                          "max": [max(v[k] for v in positions) for k in range(3)]})
        attributes = {"POSITION": acc}
        material_index = default_material()
        if header is not None:
            uv_view = add_blob(b"".join(struct.pack("<2f", *uv) for uv in uvs), 34962)
            accessors.append({"bufferView": uv_view, "componentType": 5126,
                              "count": len(uvs), "type": "VEC2"})
            attributes["TEXCOORD_0"] = acc + 1
            material_index = material_for(header)
        accessors.append({"bufferView": idx_view, "componentType": 5125,
                          "count": len(indices), "type": "SCALAR"})
        return {"attributes": attributes, "indices": len(accessors) - 1,
                "material": material_index, "mode": 4}

    for slot, oba in enumerate(load_obas(manifest, stage)):
        primitives = []
        if oba in table:
            tpa, tha = table[oba]
            faces = parse_faces(geometry, texture_data, oba, tpa, tha)
        else:
            faces = []
            missing.append(oba)
        if faces:
            grouped: dict[tuple[int, int, int, int], dict[str, list]] = {}
            for _, points, uv, header in faces:
                entry = grouped.setdefault(header, {"positions": [], "uv": [], "indices": []})
                base = len(entry["positions"])
                entry["positions"].extend(points)
                entry["uv"].extend(texture_uv(u, v, header) for u, v in uv)
                if len(points) == 4:
                    entry["indices"].extend((base, base + 1, base + 2, base, base + 2, base + 3))
                else:
                    entry["indices"].extend((base, base + 1, base + 2))
            for header, entry in grouped.items():
                if not include_untextured and not texture_by_header.get(header):
                    continue
                primitive = emit_primitive(entry["positions"], entry["uv"],
                                           entry["indices"], header)
                if primitive is not None:
                    primitives.append(primitive)
        if not primitives:
            vertices, indices = parse_mesh(geometry, oba, 0x4000)
            if vertices and indices:
                primitives.append(emit_primitive(vertices, [], indices, None))
        if not primitives:
            continue
        meshes.append({"name": f"oba_{oba:08x}", "primitives": primitives})
        nodes.append({"mesh": len(meshes) - 1, "name": f"slot_{slot:03d}_oba_{oba:08x}"})
        stats["obas"] += 1
        stats["faces"] += len(faces)

    document = {
        "asset": {"version": "2.0", "generator": "extract_stage_textured_gltf.py"},
        "scene": 0,
        "scenes": [{"name": "arena", "nodes": list(range(len(nodes)))}],
        "nodes": nodes, "meshes": meshes, "materials": materials, "images": images,
        "textures": textures, "samplers": samplers, "accessors": accessors,
        "buffers": [{"byteLength": len(blob),
                     "uri": "data:application/octet-stream;base64," +
                            base64.b64encode(bytes(blob)).decode("ascii")}],
        "bufferViews": views,
    }
    return document, stats, missing


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=int, required=True)
    parser.add_argument("--manifest", type=Path,
                        default=Path("von/i960/stage-arena-obas.json"))
    parser.add_argument("--rom", type=Path,
                        default=Path("von/build/disasm/geometry-rom.bin"))
    parser.add_argument("--texture-rom", type=Path,
                        default=Path("von/build/disasm/texture-pipeline/texture-rom.bin"))
    parser.add_argument("--bank-primary", type=Path,
                        default=Path("von/build/disasm/texture-pipeline/bank0-primary.bin"))
    parser.add_argument("--bank-secondary", type=Path,
                        default=Path("von/build/disasm/texture-pipeline/bank0-secondary.bin"))
    parser.add_argument("--trace", type=Path,
                        help="instrumented geometry trace carrying tpa/tha per OBA")
    parser.add_argument("--texmap", type=Path, default=Path("von/oba_texmap.json"))
    parser.add_argument("--palette-trace", type=Path,
                        help="trace carrying palette/colorxlat/luma writes")
    parser.add_argument("--textured-only", dest="include_untextured",
                        action="store_false",
                        help="drop faces whose texture header is not textured")
    parser.add_argument("--bank-source", choices=("primary", "header"), default="primary",
                        help="arena tiles live in the full primary sheet; 'header' "
                             "reproduces the header 0x1000 bank bit used for models")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    table = harvest_textures(args.trace, args.texmap)
    palette_state = parse_trace(args.palette_trace) if args.palette_trace else None
    document, stats, missing = build(
        args.stage, args.manifest, args.rom, args.texture_rom, args.bank_primary,
        args.bank_secondary, table, palette_state, args.include_untextured,
        args.bank_source)
    if not document["meshes"]:
        raise SystemExit(f"stage {args.stage}: no texturable statics found")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2) + "\n")
    print(f"stage {args.stage}: {stats['obas']} statics, {stats['faces']} faces, "
          f"{stats['textured']} textured materials, {stats['images']} tiles -> {args.output}")
    if missing:
        print(f"  no texture address: {', '.join(f'{o:#010x}' for o in missing)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
