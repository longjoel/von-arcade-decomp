# ROM hacking toolkit

Binary-patch the i960 maincpu ROMs without a reassembly.

## Mapping

The i960 region is two interleaved pairs (`von/tools/extract_maincpu.py`):

| image range | low ROM | high ROM |
| --- | --- | --- |
| `0x000000`-`0x0fffff` | `epr-18664b.15` | `epr-18665b.16` |
| `0x100000`-`0x1fffff` | `epr-18666.13` | `epr-18667.14` |

Within a half, every 4 image bytes are a word pair: bytes 0-1 low, 2-3 high. A
multi-byte image write crosses both chips, so patches must be applied per byte.

## Usage

```sh
# copy the ROM set, then patch i960 addresses
python3 von/tools/patch_maincpu.py --src von/artifacts --dst /tmp/hack/vonj 0x1f370=4841434b
./bin/von vonj -rompath /tmp/hack -video none -sound none -skip_gameinfo -seconds_to_run 5
```

MAME warns the romset is bad (CRC mismatch) but boots it. Verify a patch by
re-assembling the copy with `extract_maincpu.py` and reading the bytes back.

Verified proof-of-concept: patching `0x2030` `"SEGA"` → `"SEGB"` round-trips and
boots.

## Located patch points

- Attract prompts: `0x1f370` `" PRESS START BUTTON"`, `0x1f440`
  `"INSERT COIN(S)"`; drawers at `0x1f3b0`-`0x1f4b4` (call text renderers
  `0x1d210`, `0x1d9e0`).
- Attract/input bridge: `0x3a38` (a debounce counter over structs at
  `0x5024cc`/`0x5024d0`), called from `0x3ae0`.
- I/O window: `0x502400` (29 words) and `0x502440` (29 words), filled from the
  I/O controller at `0x2bb0`. Held Coin/Start leave no clean bit here — the
  inputs are edge-processed, so this is not a direct force point.
- Physics constants: gravity `0.030` (`0x3cf5c28f`) referenced at `0xd2ffc`,
  `0xd9820`, `0xd9938`, `0xdc974`; jump `1.755` (`0x3fe0a3d7`) at `0x2b324`;
  walk cap `3.5` (`0x40600000`) at `0x5d3c`, `0x11f4c`, `0x13e4c`, `0x15d6c`.
  Zeroing the four `3.5` words boots (behavior not yet verified).

## Open

Forcing a match (skip attract, 1P vs Temjin) and locating the movement
integration need the actual input read / state-machine entry.

Two blockers found while hunting them:

1. **The GDB stub is unusable in `bin/von`.** Launching with
   `-debug -debugger gdbstub` fails with
   `cpuname i80960kb not found in gdb stub descriptions`, so the MCP server
   (`tools/mame-mcp/`) cannot connect. `mcp-left-shot-probe.md` used a
   different "core profile" binary that is no longer in the tree; a MAME with
   i960 stub descriptions would have to be rebuilt.
2. **Physics constants are shared** with geometry/animation math (e.g. `1.755`
   and `0.030` appear in SHARC-FIFO feeds at `0x2b2xx`), so grep-locating the
   movement code by constant is unreliable.

Runtime forcing is available instead: **Lua `space:write_u32` persists in work
RAM** (verified writing `0x503a88` and reading it back), unlike write *taps*.
So the practical route to the match/movement sites is a Lua driver that forces
candidate cells and observes the diff, then bake the winning cell/branch into a
ROM patch with `patch_maincpu.py`. The `3.5` word patch above did **not**
change attract movement, so it was the wrong cell.


## Hacking build and tools

Build the instrumented binary (keeps `bin/von` intact):

```sh
VON_MAME_PATCH_SET=hacking VON_MAME_BIN=$PWD/bin/von-hack scripts/build.sh
```

The `hacking` profile = `core` (incl. `0043` i960 GDB stub, `0011` debug Lua
PC tracking, `0041` PC-address tracking, `0044` MCP state load) plus:

- `0050` logs every watchpoint hit (`von_wp: type addr index pc`) to the
  verbose log, so `device_debug:wpset` yields writer PCs without a GDB client.
- `0051` mirrors the last `geo_matrix_write` 12 words into i960 work RAM at
  `0x5ff000`, gated on `VON_MATRIX_SLOT`, so a snapshot can read the transform.

Verified with `bin/von-hack`: the i960 GDB stub listens
(`gdbstub: listening`), and a Lua write watchpoint on `0x500554` logs writer PCs
(`von_wp: type=w addr=00500554 index=1 pc=0000272C`).

`von/tools/hack_bout.lua` (+ `scripts/hack-bout.sh`) drives it headless with
soft video: joins a bout, writes `VON_FORCE="addr=val;..."` every frame, sets
`VON_WP="addr,len,type;..."` watchpoints (`VON_WP_ACTION=""` halts and logs;
`go` resumes), mirrors the matrix (`VON_MIRROR`), draws `VON_OVERLAY` values,
and writes PNG + JSON sidecars (registers, matrix slot, overlay values) to
`VON_HACK_SNAP_DIR`.

```sh
VON_FORCE="0x503a80=3" VON_WP="0x503ad8,4,w" VON_MIRROR=15 \
  VON_HACK_SNAP_EVERY=120 VON_HACK_SECONDS=40 scripts/hack-bout.sh
```

## Camera notes

MAME's Model 2 geometry command set has no explicit view/projection command:
`0x0b`/`0x1b` write a 12-word transformation matrix, `0x0c`/`0x1c` a translation
vector, `0x0a`/`0x1a` a light vector (`src/mame/sega/model2_v.cpp`). So the
camera is baked into the per-object matrices the i960 sends, not a separate
register. The matrix slot captures the **last** matrix of each frame; a real
camera transform likely needs the **first** matrix (or the matrix written just
before the scene objects). Next probe: set a watchpoint on the i960 cell that
feeds the geometry matrix and read its value, or capture the first matrix per
frame (extend `0051` with a per-frame first-matrix slot).
