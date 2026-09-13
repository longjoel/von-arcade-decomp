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

