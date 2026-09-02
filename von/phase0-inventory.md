# Phase 0 ROM Inventory

This is a historical inventory snapshot. Lifecycle labels below have been
updated to schema-v2 terminology; current totals and stages come from
`./scripts/status.sh`.

Inventory completed against the `vonj` ROM definition in
`third_party/patches/0001-von-mame-support.patch`.

## Audit result

The local audit passed all 24 artifacts against `von/rom_manifest.json`:

```text
ROM audit passed: 24 artifacts verified; set status=unverified
```

The set remains marked `unverified` because that status describes the dump/set
identity, not file integrity.

The canonical assembled i960 image is:

```text
file:   von/build/disasm/vonj-maincpu.bin
size:   0x200000 (2097152 bytes)
sha256: df365f7f7e5cfead057ca8680d77a8a859e00ee3146b1f5824a9b4628eb7caf3
```

It is reproducible with:

```sh
python3 von/tools/extract_maincpu.py \
  --output von/build/disasm/vonj-maincpu.bin
```

The readable listing is generated with `./scripts/remote-disasm-i960.sh`.

## Region reconciliation

| MAME region | Size | ROM artifacts | Classification |
| --- | ---: | --- | --- |
| `maincpu` | 2 MiB | `epr-18664b.15`, `epr-18665b.16`, `epr-18666.13`, `epr-18667.14` | i960 executable firmware plus constants/data |
| `main_data` | 16 MiB loaded | `mpr-18648.11`, `mpr-18649.12`, `mpr-18650.9`, `mpr-18651.10` | host data and uploaded program payloads; executable status unresolved |
| `copro_data` | 4 MiB loaded | `mpr-18662.29`, `mpr-18663.30` | SHARC/coprocessor data; executable boundaries unresolved |
| `polygons` | 16 MiB loaded | `mpr-18654.17`, `mpr-18655.21`, `mpr-18656.18`, `mpr-18657.22` | geometry/model assets |
| `textures` | 8 MiB loaded | `mpr-18660.27`, `mpr-18658.25`, `mpr-18661.28`, `mpr-18659.26` | texture assets |
| `cpu3` | 128 KiB | `epr-18643a.7` | Z80 communication firmware |
| `audiocpu` | 512 KiB | `epr-18670.31` | 68000 audio firmware |
| `samples` | 8 MiB loaded | `mpr-18652.32`, `mpr-18653.34` | SCSP sample assets |
| unassigned | 1 MiB | `vo-prog0.usa`, `vo-prog1.usa` | board position and role unknown |

The region sizes and load layouts are taken from the `vonj` ROM definition;
the artifact hashes and physical sizes remain governed by
`von/rom_manifest.json`.

## Executable classification baseline

The first two i960 code ranges registered in
`von/reconstruction_ledger.json` are:

| Slice | Range | Bytes | Status |
| --- | --- | ---: | --- |
| reset/startup | `0x00000930–0x000009e8` | 184 | planned |
| geometry program upload | `0x00028620–0x00028758` | 312 | modeled |

The ledger now also contains the bounded geometry and texture routines listed
in the reconstruction roadmap as `planned`; those additional ranges bring the
current classified executable denominator to 2,196 bytes. No
Z80, 68000, or SHARC executable ranges have been claimed. The active Phase 0
classification work is now limited to the i960 image; the other firmware
images are inventoried but deferred because MAME's high-level `m2comm` model
replaces the communication board during execution.

The communication-board ROM has now been normalized and disassembled with
MAME's `unidasm` Z80 decoder:

```sh
./scripts/disasm-cpu3.sh
```

The canonical linear image is `von/build/disasm/vonj-cpu3.bin`, with SHA-256
`b5a36907834c9a57528aa1684c84a6dd4f887f671dd293bdc68db8fa7fed1891`. Its
first confirmed control-flow observation is a reset entry at `0x0000` that
branches to `0x01ff`. The bytes between the reset stub and that target include
vector/table-looking fill, so no larger Z80 code range is claimed yet.

## Phase 0 completion state

- ROM integrity: complete.
- Canonical i960 extraction: complete.
- MAME region reconciliation: complete in this document.
- i960 code/data classification: started; known ranges recorded.
- Z80 normalization/disassembly: complete; code/data boundaries deferred.
- 68000 classification: deferred.
- SHARC code/data separation: deferred.
- Byte-validated C translation: 0 bytes / 2,196 classified bytes.
