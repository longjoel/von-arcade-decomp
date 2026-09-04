# Original-ROM geometry transform FIFO findings

> **Retained evidence note:** these vectors remain useful fixtures, but the
> historical capture is not grandfathered as canonical evidence. See
> [geometry recovery](../docs/geometry.md).

The bounded selector-0 interactive capture was run against the original
`vonj` staging on `drone0`, with phase-local PC tracking enabled. The capture
reached match entry and exercised `0x76240–0x76498`. Existing geometry response
hooks recorded the following paired command/readback values:

| command PC | command | response PCs and values |
| --- | ---: | --- |
| `0x76240` / `0x76278` | `29` / `0xe000` | `0x76288: 0x00000000`, `0x76290: 0xc129b5af` |
| `0x762a0` / `0x762b0` | `30` / `0xe000` | `0x762b8: 0x00000000`, `0x762c0: 0x4129b39a` |
| `0x762d8` / `0x762e8` | `29` / `0x2000` | `0x762f0: 0x00000000`, `0x762f8: 0x4129b5af` |
| `0x76308` / `0x76318` | `30` / `0x2000` | `0x76320: 0x00000000`, `0x76328: 0x4129b39a` |
| `0x76338` / `0x76344` | `29` / `0x8000` | `0x76354: 0x00000000`, `0x7635c: 0x3e1359e0` |
| `0x76368` / `0x76374` | `30` / `0x8000` | `0x7637c: 0x00000000`, `0x76384: 0xc4bb7fff` |
| `0x76390` / `0x7639c` | `29` / `0x8000` | `0x763b0: 0x00000000`, `0x763b8: 0x3e1359e0` |
| `0x763c0` / `0x763d4` | `30` / `0x8000` | `0x763e0: 0x00000000`, `0x763e8: 0xc4bb7fff` |

These values are evidence for the original hardware response path, not a
complete transform specification. The surrounding routine performs
fixed-point/FPU arithmetic using the readbacks, so no production C model is
promoted until more response vectors and state correspondence are available.
The two additional rows came from a bounded follow-up selector-0 capture on
`drone0`; the run was stopped after the match-entry boundary dump completed,
but the original MAME log had already recorded the response pairs.
The reconstructed `vonjdev` image is diagnostic only and was not used to obtain
these values.

The compact transcription is preserved in
`von/i960/geometry-transform-fifo-fixture.json` and checked by
`von/tools/test_geometry_transform_fifo_fixture.py`.
