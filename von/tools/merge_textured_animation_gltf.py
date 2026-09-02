#!/usr/bin/env python3
"""Merge a textured frame glTF with a transform-animation glTF.

The two exporters intentionally produce independent self-contained files. This
tool joins them by ROM object address (OBA), preserving the textured scene's
materials and adding the animation buffer and channels from the motion export.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path


OBA = re.compile(r"oba_([0-9a-fA-F]+)")


def node_oba(node: dict) -> int | None:
    geometry = node.get("extras", {}).get("geometry_object", {})
    if "oba" in geometry:
        return int(geometry["oba"])
    match = OBA.search(node.get("name", ""))
    return int(match.group(1), 16) if match else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--textured", type=Path, required=True)
    parser.add_argument("--animation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    scene = json.loads(args.textured.read_text())
    animation = json.loads(args.animation.read_text())
    textured_nodes = {node_oba(node): index for index, node in enumerate(scene.get("nodes", []))
                      if node_oba(node) is not None}
    animation_nodes = [node_oba(node) for node in animation.get("nodes", [])]
    if any(oba is None for oba in animation_nodes):
        raise SystemExit("animation contains a node without an OBA")
    missing = [oba for oba in animation_nodes if oba not in textured_nodes]
    if missing:
        raise SystemExit("textured scene is missing animation OBAs: " +
                         ", ".join(f"{oba:08x}" for oba in missing))
    if not animation.get("buffers") or not animation["buffers"][0].get("uri"):
        raise SystemExit("animation must contain an embedded buffer")

    result = copy.deepcopy(scene)
    buffer_index = len(result.setdefault("buffers", []))
    views = copy.deepcopy(animation.get("bufferViews", []))
    for view in views:
        view["buffer"] = buffer_index
    view_offset = len(result.setdefault("bufferViews", []))
    accessor_offset = len(result.setdefault("accessors", []))
    result["bufferViews"].extend(views)
    accessors = copy.deepcopy(animation.get("accessors", []))
    for accessor in accessors:
        accessor["bufferView"] += view_offset
    result["accessors"].extend(accessors)
    result["buffers"].append(copy.deepcopy(animation["buffers"][0]))

    animations = copy.deepcopy(animation.get("animations", []))
    if not animations:
        raise SystemExit("animation file contains no animation clips")
    for clip in animations:
        for sampler in clip.get("samplers", []):
            sampler["input"] += accessor_offset
            sampler["output"] += accessor_offset
        for channel in clip.get("channels", []):
            old_node = channel["target"]["node"]
            channel["target"]["node"] = textured_nodes[animation_nodes[old_node]]
    result["animations"] = animations
    result.setdefault("extras", {})["animation_source"] = str(args.animation)
    result["extras"]["animation_nodes_mapped_by"] = "geometry_object OBA"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(f"merged {len(animations)} clip(s) into {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
