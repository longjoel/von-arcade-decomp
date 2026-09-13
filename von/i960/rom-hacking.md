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
integration need the actual input read / state-machine entry. The reliable way
to find them is a GDB-stub watchpoint (see `tools/mame-mcp/`) on the state cells
(`0x500540` select state, `0x500550` mode) during a joined bout, then patching
the branch. The patcher above is the delivery mechanism once the site is known.
