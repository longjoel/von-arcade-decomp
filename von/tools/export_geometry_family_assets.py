#!/usr/bin/env python3
"""Export canonical ROM-backed glTF assets and manifests for geometry families."""
from __future__ import annotations
import argparse, json, subprocess
from pathlib import Path

def core_obas(canonical, variants):
    sequences = [canonical] + variants
    return [value for index, value in enumerate(canonical)
            if all(index < len(sequence) and sequence[index] == value for sequence in sequences)]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fingerprints", type=Path, required=True)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--rom", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--family", action="append", help="family ID to export; default exports all")
    args = parser.parse_args()
    data = json.loads(args.fingerprints.read_text())
    assemblies = {entry["fingerprint"]: entry for entry in data["assemblies"]}
    families = [entry for entry in data["families"] if not args.family or entry["family"] in args.family]
    exporter = Path(__file__).with_name("export_geometry_frame_gltf.py")
    for family in families:
        canonical = assemblies[family["canonical"]]
        variants = [assemblies[key]["obas"] for key in family["variants"] if key != family["canonical"]]
        target = args.output_dir / family["family"]
        target.mkdir(parents=True, exist_ok=True)
        output = target / "canonical.gltf"
        subprocess.run(["python3", exporter, "--trace", args.trace, "--rom", args.rom,
                        "--output", output, "--time", str(canonical["first_time"]),
                        "--start-object", str(canonical["first_slot"]),
                        "--max-objects", str(canonical["object_count"])], check=True)
        manifest = {"family": family["family"], "canonical": canonical["fingerprint"],
                    "first_slot": canonical["first_slot"], "frames": family["frames"],
                    "variant_count": len(family["variants"]), "canonical_obas": canonical["obas"],
                    "core_obas": core_obas(canonical["obas"], variants),
                    "optional_obas": sorted(set(canonical["obas"]) - set(core_obas(canonical["obas"], variants))),
                    "asset": output.name}
        (target / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"exported {len(families)} geometry family assets")
if __name__ == "__main__": main()
