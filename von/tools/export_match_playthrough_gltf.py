#!/usr/bin/env python3
"""Export a match-playthrough window from a frames JSON tap as animated glTF.

Input is the frames format {t: [[oba_hex, r0..r8, x, y, z], ...]} (entries
may also carry tpa/tha after the OBA). A common-mode world drift is
subtracted first (tracked from persistent parts). Everything is chained by
position continuity (greedy nearest neighbour within each OBA family, as in
annotate_bout.py), chains split into maximal single-OBA runs, and runs that
never exceed 0.8 u/s freeze at the median pose -- places, not joints. Each
run becomes one animated node: ROM mesh of its OBA (textured when tpa/tha
are known), LINEAR translation/rotation/scale keys, scale-0 hides gaps.

Usage:
    python3 von/tools/export_match_playthrough_gltf.py --frames /tmp/demo.json \\
        --rom von/build/disasm/geometry-rom.bin --t0 138 --t1 149.5 \\
        --output von-viewer/public/assets/traced/match-playthrough-bout1.gltf
"""
from __future__ import annotations

import argparse
import base64
import json
import math
import statistics
import struct
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from annotate_bout import destab, estimate_yaw_track
from export_geometry_animation_gltf import parse_mesh, transform_trs
from export_geometry_textured_gltf import (parse_faces, texture_sampler,
                                           texture_size, texture_uv, tile_png)

IDENTITY_ROT = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)


def load_frames(path: Path):
    raw = json.loads(path.read_text())
    return {float(t): v for t, v in raw.items()}


def chain_family(snaps, gate=8.0):
    """Greedy nearest-neighbour chains; entries are (oba, rot9, pos) or None."""
    med_n = statistics.median(len(s) for s in snaps)
    si = min(range(len(snaps)), key=lambda i: abs(len(snaps[i]) - med_n))
    chains = [[e] for e in snaps[si]]

    def step(fi: int, forward: bool):
        cur = snaps[fi]
        used: set[int] = set()
        for c in chains:
            ref = c[-1] if forward else c[0]
            if ref is None:
                seq = reversed(c) if forward else iter(c)
                ref = next((e for e in seq if e is not None), None)
            best = None
            bd = gate
            if ref is not None:
                # Prefer same-OBA continuation: a visible part keeps its OBA
                # until a segment switch, so identity beats proximity and
                # neighbors can't steal the track. Positional fallback covers
                # segment switches (new OBA, same spot).
                same = [(j, e) for j, e in enumerate(cur)
                        if j not in used and e[0] == ref[0]]
                pool = same if same else [(j, e) for j, e in enumerate(cur)
                                          if j not in used]
                for j, e in pool:
                    d = math.dist(ref[2], e[2])
                    if d < bd:
                        bd = d
                        best = (j, e)
            if best is not None:
                if forward:
                    c.append(best[1])
                else:
                    c.insert(0, best[1])
                used.add(best[0])
            else:
                c.append(None) if forward else c.insert(0, None)

    for fi in range(si + 1, len(snaps)):
        step(fi, True)
    for fi in range(si - 1, -1, -1):
        step(fi, False)
    return chains


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--frames", type=Path, required=True)
    p.add_argument("--rom", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--t0", type=float, default=None)
    p.add_argument("--t1", type=float, default=None)
    p.add_argument("--stride", type=int, default=2)
    p.add_argument("--min-fill", type=int, default=5)
    p.add_argument("--texture-rom", type=Path,
                   default=Path("von/build/disasm/texture-pipeline/texture-rom.bin"))
    p.add_argument("--bank-primary", type=Path,
                   default=Path("von/build/disasm/texture-pipeline/bank0-primary.bin"))
    p.add_argument("--bank-secondary", type=Path,
                   default=Path("von/build/disasm/texture-pipeline/bank0-secondary.bin"))
    p.add_argument("--texmap", type=Path, default=None,
                   help="JSON oba-hex -> [[tpa, tha], ...] fallback texture addresses")
    a = p.parse_args()

    frames = load_frames(a.frames)
    ts = sorted(t for t in frames if (a.t0 is None or t >= a.t0) and (a.t1 is None or t <= a.t1))
    print(f"window: {len(ts)} frames {ts[0]:.2f}-{ts[-1]:.2f}s")
    rom = a.rom.read_bytes()
    texture_rom = a.texture_rom.read_bytes()
    primary = a.bank_primary.read_bytes()
    secondary = a.bank_secondary.read_bytes()
    texmap = json.loads(a.texmap.read_text()) if a.texmap else {}

    def entry_meta(o):
        # New format carries tpa/tha; old format falls back to the texmap.
        if len(o) >= 14:
            return o[0], int(o[1]), int(o[2]), tuple(o[3:12]), tuple(o[12:15])
        cand = texmap.get(o[0], [[None, None]])[0]
        return o[0], cand[0], cand[1], tuple(o[1:10]), tuple(o[10:13])

    # Diorama rule: OBA churn IS animation. Chain everything positionally,
    # then freeze by churn, not by displacement:
    # - chains spanning >= 2 distinct OBAs are mech joints: ALWAYS raw, so a
    #   player piece can never be frozen in the wrong place;
    # - single-OBA chains are stage/scrollers: frozen at the median pose,
    #   except transient fast movers (flying debris: low fill + real travel),
    #   which stay live.
    #
    # Stabilize first: the tap frame yaws with the demo camera (a rigid
    # baseline sweeps ~70 degrees over a bout) plus a translation drift.
    # De-yaw/de-translate every frame from persistent reference parts so the
    # diorama sits still; relative motion (dashes, distances) is preserved.
    # Part facings are de-yawed too (quaternion premultiply at emit time).
    def yaw_quat(a: float):
        return (0.0, math.sin(a / 2), 0.0, math.cos(a / 2))

    raw_by_frame: list[list] = []
    for t in ts:
        lst = []
        for o in frames[t]:
            oba, tpa, tha, rot, pos = entry_meta(o)
            lst.append((oba, rot, pos, tpa, tha, oba[:4]))
        raw_by_frame.append(lst)
    # Stabilization lives in annotate_bout (rigidity-selected yaw rig with
    # trust gates); this export consumes yaw_s/centers/c0 from it.
    fob = [[(e[0], list(e[2])) for e in lst] for lst in raw_by_frame]
    yaw_s, centers, c0, stab_info = estimate_yaw_track(fob)
    entries_by_frame = []
    for lst, yw, c in zip(raw_by_frame, yaw_s, centers):
        out = []
        for e in lst:
            out.append((e[0], e[1], destab(list(e[2]), yw, c, c0),
                        e[3], e[4], e[5]))
        entries_by_frame.append(out)
    print(f"stabilized: trusted={stab_info['yaw_trusted']} "
          f"span={stab_info['span_deg']}deg refs={stab_info['n_refs']} "
          f"arms={stab_info['n_arms']} spread={stab_info['spread_deg']}deg "
          f"star={stab_info['star']}")

    fams: dict[str, list[list]] = {}
    for lst in entries_by_frame:
        per: dict[str, list] = {}
        for e in lst:
            per.setdefault(e[5], []).append(e[:5])
        for fam, entries in per.items():
            fams.setdefault(fam, []).append(entries)
    for fam, snaps in fams.items():
        if len(snaps) < len(ts):
            fams[fam] = snaps + [[]] * (len(ts) - len(snaps))

    chains = []
    for fam, snaps in sorted(fams.items()):
        for c in chain_family(snaps):
            if sum(1 for e in c if e) >= a.min_fill:
                chains.append((fam, c))

    # Split chains into maximal single-OBA runs. A run boundary is either a
    # genuine segment switch (seamless handoff: consecutive nodes draw the
    # same joint back to back) or a tracking latch onto a neighbor (which the
    # split quarantines instead of baking in). Runs keep frame alignment so
    # gaps still hide via scale-0.
    runs: list = []
    for fam, c in chains:
        run: list = []
        for fi, e in enumerate(c):
            if e is None or (run and e[0] != run[-1][1][0]):
                if run:
                    runs.append((fam, run))
                run = []
            if e is not None:
                run.append((fi, e))
        if run:
            runs.append((fam, run))
    runs = [(fam, run) for fam, run in runs if len(run) >= a.min_fill]
    full: list = []
    for fam, run in runs:
        c = [None] * len(ts)
        for fi, e in run:
            c[fi] = e
        full.append((fam, c))

    # Freeze runs that never move fast (places, not joints). Genuine motion
    # -- dashes, debris, scrolling layers -- always has fast frames and stays
    # raw, so a player piece can never stick.
    STILL_FPS = 0.8
    frozen = 0
    for fam, c in full:
        peak = 0.0
        prev = None
        for fi, e in enumerate(c):
            if e is None:
                prev = None
                continue
            if prev is not None:
                dt = ts[fi] - ts[prev[0]]
                if dt > 0:
                    peak = max(peak, math.dist(e[2], prev[1][2]) / dt)
            prev = (fi, e)
        if peak >= STILL_FPS:
            continue
        pts = [e[2] for e in c if e]
        med = [statistics.median(p[k] for p in pts) for k in range(3)]
        top_rot = Counter(e[1] for e in c if e).most_common(1)[0][0]
        for i, e in enumerate(c):
            if e is not None:
                c[i] = (e[0], top_rot, tuple(med), e[3], e[4])
        frozen += 1
    print(f"chains: {len(chains)} runs: {len(full)} frozen still: {frozen}")
    chains = full

    # Representative (oba, tpa, tha) mesh per chain (dedup identical).
    mesh_by_key: dict[tuple, int] = {}
    meshes: list = []
    materials: list = []
    material_by_header: dict = {}
    images: list = []
    textures: list = []
    texture_by_key: dict = {}
    samplers: list = []
    sampler_by_mode: dict = {}
    blob = bytearray()
    views: list = []
    accessors: list = []

    def add_blob(data: bytes, target: int | None = None) -> int:
        offset = len(blob)
        blob.extend(data)
        view: dict = {"buffer": 0, "byteOffset": offset, "byteLength": len(data)}
        if target is not None:
            view["target"] = target
        views.append(view)
        return len(views) - 1

    def material_for(header) -> int:
        if header in material_by_header:
            return material_by_header[header]
        width, height, origin_x, origin_y, colorbase = texture_size(header)
        textured = bool(((header[0] >> 13) & 3) & 2)
        bank = secondary if header[2] & 0x1000 else primary
        image_data = tile_png(bank, header, None) if textured else None
        texture_index = None
        if image_data is not None:
            sampler_mode = texture_sampler(header)
            sampler_index = sampler_by_mode.get(sampler_mode)
            if sampler_index is None:
                sampler_index = len(samplers)
                samplers.append({"magFilter": 9729, "minFilter": 9729,
                                 "wrapS": sampler_mode[0], "wrapT": sampler_mode[1]})
                sampler_by_mode[sampler_mode] = sampler_index
            texture_key = (header[0], header[1], header[2], header[3])
            texture_index = texture_by_key.get(texture_key)
            if texture_index is None:
                images.append({
                    "uri": "data:image/png;base64," + base64.b64encode(image_data).decode("ascii"),
                    "name": f"tile_{origin_x:04x}_{origin_y:03x}_{width}x{height}"})
                texture_index = len(textures)
                textures.append({"sampler": sampler_index, "source": len(images) - 1})
                texture_by_key[texture_key] = texture_index
        material: dict = {"name": f"header_{header[0]:04x}_{header[1]:04x}_{header[2]:04x}_{header[3]:04x}"}
        if texture_index is not None:
            material["pbrMetallicRoughness"] = {
                "baseColorFactor": [1, 1, 1, 1], "metallicFactor": 0,
                "roughnessFactor": 1, "baseColorTexture": {"index": texture_index}}
        else:
            material["pbrMetallicRoughness"] = {
                "baseColorFactor": [0.65, 0.65, 0.65, 1],
                "metallicFactor": 0, "roughnessFactor": 1}
        material_by_header[header] = len(materials)
        materials.append(material)
        return material_by_header[header]

    def mesh_for(oba: int, tpa, tha):
        key = (oba, tpa, tha)
        if key in mesh_by_key:
            return mesh_by_key[key]
        primitives_by_header: dict = {}
        if tpa is not None and tha is not None:
            try:
                faces = parse_faces(rom, texture_rom, oba, tpa, tha)
            except Exception:
                faces = []
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
            # Untextured fallback: raw polygon-ROM mesh, gray material.
            try:
                vertices, indices = parse_mesh(rom, oba)
            except Exception:
                vertices, indices = [], []
            if not 1 <= len(vertices) <= 6000 or not indices:
                return None
            positions = b"".join(struct.pack("<3f", *v) for v in vertices)
            index_data = b"".join(struct.pack("<I", x) for x in indices)
            pv = add_blob(positions, 34962)
            iv = add_blob(index_data, 34963)
            accessors.extend([
                {"bufferView": pv, "componentType": 5126, "count": len(vertices),
                 "type": "VEC3",
                 "min": [min(v[k] for v in vertices) for k in range(3)],
                 "max": [max(v[k] for v in vertices) for k in range(3)]},
                {"bufferView": iv, "componentType": 5125, "count": len(indices),
                 "type": "SCALAR"},
            ])
            gray = {"name": "untextured_gray", "pbrMetallicRoughness": {
                "baseColorFactor": [0.65, 0.65, 0.65, 1],
                "metallicFactor": 0, "roughnessFactor": 1}}
            mesh_by_key[key] = len(meshes)
            meshes.append({"name": f"oba_{oba:08x}", "primitives": [{
                "attributes": {"POSITION": len(accessors) - 2},
                "indices": len(accessors) - 1, "material": len(materials),
                "mode": 4}]})
            materials.append(gray)
            return mesh_by_key[key]
        mesh_primitives = []
        for header, entry in primitives_by_header.items():
            positions = entry["positions"]
            pv = add_blob(b"".join(struct.pack("<3f", *p) for p in positions), 34962)
            uvv = add_blob(b"".join(struct.pack("<2f", *u) for u in entry["uv"]), 34962)
            iv = add_blob(b"".join(struct.pack("<I", x) for x in entry["indices"]), 34963)
            pa = len(accessors)
            accessors.extend([
                {"bufferView": pv, "componentType": 5126, "count": len(positions),
                 "type": "VEC3",
                 "min": [min(p[k] for p in positions) for k in range(3)],
                 "max": [max(p[k] for p in positions) for k in range(3)]},
                {"bufferView": uvv, "componentType": 5126, "count": len(entry["uv"]),
                 "type": "VEC2"},
                {"bufferView": iv, "componentType": 5125, "count": len(entry["indices"]),
                 "type": "SCALAR"},
            ])
            mesh_primitives.append({
                "attributes": {"POSITION": pa, "TEXCOORD_0": pa + 1},
                "indices": pa + 2, "material": material_for(header), "mode": 4})
        mesh_by_key[key] = len(meshes)
        meshes.append({"name": f"oba_{oba:08x}_tpa_{tpa:08x}_tha_{tha:08x}",
                       "primitives": mesh_primitives})
        return mesh_by_key[key]

    nodes: list = []
    skipped = Counter()
    textured_chains = untextured_chains = 0
    for i, (fam, c) in enumerate(chains):
        top = Counter((e[0], e[3], e[4]) for e in c if e).most_common(1)[0][0]
        oba_hex, tpa, tha = top
        mesh_index = mesh_for(int(oba_hex, 16), tpa, tha)
        if mesh_index is None:
            skipped[fam] += 1
            continue
        if tpa is None:
            untextured_chains += 1
        else:
            textured_chains += 1
        nodes.append({"mesh": mesh_index,
                      "name": f"track_{len(nodes):03d}_oba_{oba_hex}",
                      "extras": {"family": fam},
                      "_chain": c})
    print(f"nodes: {len(nodes)} meshes: {len(meshes)} textured: {textured_chains} "
          f"untextured: {untextured_chains} skipped: {dict(skipped)}")

    def qmult(a, b):
        ax, ay, az, aw = a
        bx, by, bz, bw = b
        return (aw * bx + ax * bw + ay * bz - az * by,
                aw * by - ax * bz + ay * bw + az * bx,
                aw * bz + ax * by - ay * bx + az * bw,
                aw * bw - ax * bx - ay * by - az * bz)

    keep_ts = ts[::a.stride]
    input_view = add_blob(b"".join(struct.pack("<f", t - keep_ts[0]) for t in keep_ts))
    input_accessor = len(accessors)
    accessors.append({"bufferView": input_view, "componentType": 5126,
                      "count": len(keep_ts), "type": "SCALAR",
                      "min": [0.0], "max": [keep_ts[-1] - keep_ts[0]]})
    anim_channels: list = []
    anim_samplers: list = []
    for ni, node in enumerate(nodes):
        c = node.pop("_chain")
        idx = [ts.index(t) for t in keep_ts]
        trs = []
        present_poses = set(e[2] for e in c if e is not None)
        present_rots = set(e[1] for e in c if e is not None)
        hold = len(present_poses) == 1 and len(present_rots) == 1
        for fi in idx:
            e = c[fi]
            if e is None:
                if hold:
                    frozen_pose = next(iter(present_poses))
                    frozen_rot = next(iter(present_rots))
                    rq, _ = transform_trs(frozen_rot)
                    rq = qmult(yaw_quat(-yaw_s[fi]), rq)
                    trs.append((frozen_pose, rq, (1.0, 1.0, 1.0)))
                else:
                    trs.append(((0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 1.0), (0.0, 0.0, 0.0)))
            else:
                quat, scale = transform_trs(e[1])
                quat = qmult(yaw_quat(-yaw_s[fi]), quat)
                trs.append((e[2], quat, scale))
        for path, k in (("translation", 0), ("rotation", 1), ("scale", 2)):
            data = b"".join(struct.pack("<3f" if path != "rotation" else "<4f", *t[k]) for t in trs)
            view = add_blob(data)
            accessor = len(accessors)
            accessors.append({"bufferView": view, "componentType": 5126,
                              "count": len(keep_ts),
                              "type": "VEC4" if path == "rotation" else "VEC3"})
            sampler = len(anim_samplers)
            anim_samplers.append({"input": input_accessor, "output": accessor,
                                  "interpolation": "LINEAR"})
            anim_channels.append({"sampler": sampler,
                                  "target": {"node": ni, "path": path}})
    span = keep_ts[-1] - keep_ts[0]
    document = {
        "asset": {"version": "2.0", "generator": "von export_match_playthrough_gltf.py"},
        "scene": 0, "scenes": [{"nodes": list(range(len(nodes)))}], "nodes": nodes,
        "meshes": meshes, "materials": materials, "images": images,
        "textures": textures, "samplers": samplers,
        "animations": [{"name": f"playthrough ({span:.1f}s, {len(keep_ts)} keys)",
                        "samplers": anim_samplers, "channels": anim_channels}],
        "buffers": [{"byteLength": len(blob), "uri": "data:application/octet-stream;base64," +
                     base64.b64encode(bytes(blob)).decode("ascii")}],
        "bufferViews": views, "accessors": accessors,
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(document) + "\n")
    size = a.output.stat().st_size
    print(f"wrote {a.output} ({size / 1048576:.1f} MiB, {len(nodes)} nodes, {len(keep_ts)} keys)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
