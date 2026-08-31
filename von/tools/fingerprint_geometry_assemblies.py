#!/usr/bin/env python3
"""Stream traced geometry frames into stable, ROM-assembly fingerprints."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from export_geometry_frame_gltf import MATRIX, OBJECT
from export_geometry_assemblies import split_assemblies

def fingerprint(group):
    obas = [item[0] for _, item in group]
    digest = hashlib.sha256(b"".join(oba.to_bytes(4, "little") for oba in obas)).hexdigest()[:16]
    return f"oba-{digest}", obas

def family_summary(assemblies, minimum_overlap):
    """Merge exact fingerprints whose ordered slots share a stable core."""
    families = []
    for assembly in sorted(assemblies, key=lambda x: (-x["frames"], x["first_slot"])):
        candidate = [int(oba, 16) for oba in assembly["obas"]]
        for family in families:
            if assembly["first_slot"] != family["first_slot"]:
                continue
            canonical = [int(oba, 16) for oba in family["canonical_obas"]]
            matching = sum(a == b for a, b in zip(candidate, canonical))
            if matching / max(len(candidate), len(canonical)) >= minimum_overlap:
                family["frames"] += assembly["frames"]
                family["variants"].append(assembly["fingerprint"])
                break
        else:
            families.append({"family": f"family-{len(families):02d}",
                "first_slot": assembly["first_slot"], "canonical": assembly["fingerprint"],
                "canonical_obas": assembly["obas"], "frames": assembly["frames"],
                "variants": [assembly["fingerprint"]]})
    return families

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--min-objects", type=int, default=1)
    parser.add_argument("--distance", type=float, default=15.0)
    parser.add_argument("--max-time", type=float)
    parser.add_argument("--family-overlap", type=float, default=0.7)
    args = parser.parse_args()
    if args.distance <= 0 or not 0 < args.family_overlap <= 1: raise SystemExit("invalid grouping bounds")
    current = (1.,0.,0.,0.,1.,0.,0.,0.,1.,0.,0.,0.)
    frames, identities = {}, {}
    for line in args.trace.open(errors="replace"):
        line = line.rstrip()
        matrix = MATRIX.search(line)
        if matrix:
            current = tuple(float(x) for x in matrix[2].split(",")) + tuple(float(x) for x in matrix[3].split(",")); continue
        match = OBJECT.search(line)
        if not match or int(match[6]) != 3 or match[7] != "polygon-rom": continue
        time = float(match[1])
        if args.max_time is not None and time > args.max_time: continue
        frames.setdefault(time, []).append((int(match[4],16), current, {}))
    complete = [(time, items) for time, items in sorted(frames.items()) if len(items) >= args.min_objects]
    for time, items in complete:
        for group in split_assemblies(items, args.distance):
            key, obas = fingerprint(group); entry = identities.setdefault(key, {"fingerprint": key, "obas": [f"{x:08x}" for x in obas], "object_count": len(group), "frames": 0, "first_time": time, "last_time": time, "first_slot": group[0][0]})
            entry["frames"] += 1; entry["last_time"] = time
    assemblies = sorted(identities.values(), key=lambda x: (-x["frames"], x["first_slot"]))
    output = {"trace": str(args.trace), "distance": args.distance, "family_overlap": args.family_overlap, "complete_frames": len(complete), "assemblies": assemblies, "families": family_summary(assemblies, args.family_overlap)}
    args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(json.dumps(output, indent=2) + "\n")
    print(f"fingerprinted {len(assemblies)} assemblies in {len(output['families'])} families across {len(complete)} frames")
if __name__ == "__main__": main()
