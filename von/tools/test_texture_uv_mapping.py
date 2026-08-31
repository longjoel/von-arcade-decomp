#!/usr/bin/env python3
"""Regression checks for Model 2 UV scaling and texture-header sampling flags."""
from __future__ import annotations

from export_geometry_textured_gltf import (raster_vertices, texture_sampler,
                                           texture_sheet_xy, texture_size,
                                           texture_uv)


def expect(actual, expected, label):
    if actual != expected:
        raise SystemExit(f"{label}: expected {expected!r}, got {actual!r}")


def main():
    # 0x40c9: textured, 64x64; 0x09cb selects the 352,224 atlas tile.
    # Its low 0xc9 bits explicitly enable repeat on both axes.
    header = (0x40C9, 0, 0x09CB, 0x7440)
    expect(texture_size(header), (64, 64, 352, 224, 0x1D1), "header decode")
    expect(texture_uv(512, 256, header), (1.0, 0.5), "1/8-texel UV scale")
    expect(texture_sampler(header), (10497, 10497), "captured repeat flags")

    clamp_header = (0x4009, 0, header[2], header[3])
    expect(texture_sampler(clamp_header), (33071, 33071), "default clamp")

    expect(texture_sampler((clamp_header[0] | (1 << 6), 0, header[2], header[3])),
           (10497, 33071), "U repeat")
    expect(texture_sampler((clamp_header[0] | (1 << 7), 0, header[2], header[3])),
           (33071, 10497), "V repeat")
    expect(texture_sampler((clamp_header[0] | (1 << 6) | (1 << 8), 0, header[2], header[3])),
           (33648, 33071), "U mirror overrides repeat")
    expect(texture_sampler((clamp_header[0] | (1 << 7) | (1 << 9), 0, header[2], header[3])),
           (33071, 33648), "V mirror overrides repeat")

    # Model 2 stores the logical right half of its 2048x1024 texture sheet
    # in a second 1024x1024 bank, selected by Y bit 10.
    expect(texture_sheet_xy(1023, 17), (1023, 17), "left texture-sheet half")
    expect(texture_sheet_xy(1024, 17), (0, 1041), "right texture-sheet bank")
    expect(texture_sheet_xy(2047, 1023), (1023, 2047), "right edge sheet bank")

    # Positions P0,P1 arrive in the opposite order from their V0,V1 UVs.
    expect(raster_vertices(((0.0, 0.0, 0.0), (1.0, 0.0, 0.0),
                            (0.0, 1.0, 0.0), (1.0, 1.0, 0.0))),
           ((1.0, 0.0, 0.0), (0.0, 0.0, 0.0),
            (0.0, 1.0, 0.0), (1.0, 1.0, 0.0)),
           "raster vertex/UV correspondence")
    print("PASS: Model 2 UV mapping and sampler flags")


if __name__ == "__main__":
    main()
