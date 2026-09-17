# Communication Z80 Disassembly

The communication-board firmware is `epr-18643a.7`, a single 8-bit 27C1001
(128 KiB). Reconstruct the linear image and listing with:

```sh
./bin/vonctl disasm cpu3
```

Generated (git-ignored) outputs:

- `von/build/disasm/vonj-cpu3.bin`
- `von/build/disasm/vonj-cpu3.lst`

## Byte order

MAME declares the ROM `ROM_LOAD16_WORD_SWAP`, but it never executes `cpu3`
(`m2comm` simulates the board), and the part is 8-bit, so the dump is already
in Z80 byte order. `von/tools/extract_cpu3.py` must **not** swap bytes; an
earlier version did, which produced a plausible-looking but invalid image.
The reset bytes are `c3 a2 01` (`jp $01A2`), and `$01A2` is a canonical Z80
startup:

```text
01a2: f3        di
01a3: ed 5e     im   2
01a5: 31 00 a0  ld   sp,$A000
01a8: af        xor  a
01a9: d3 50     out  ($50),a
01ab: 32 01 80  ld   ($8001),a          ; shared[1] role = 0
01ae: cd 3f 01  call $013F              ; clear 0x8000..0x9FEF
01b1: db 50     in   a,($50)
01b3: 32 29 80  ld   ($8029),a
01b6: 21 00 20  ld   hl,$2000
01b9: 22 10 80  ld   ($8010),hl         ; frameStart = 0x2000
01bc: 21 00 0e  ld   hl,$0E00
01bf: 22 12 80  ld   ($8012),hl         ; frameSize  = 0x0E00
01c2: 21 c0 01  ld   hl,$01C0
01c5: 22 14 80  ld   ($8014),hl         ; frameOffset = 0x01C0
```

## Dual-port mailbox

The board exposes 16 KiB of bank-switched dual-port RAM. The Z80 sees two
16 KiB banks at `0x8000` and `0xC000`; the i960 always sees one at shared
offset `0` (its `0x01A10000` mirror). Routine `0x0165` mirrors the Z80 header
`0x8000..` into the i960 bank at `0xC000..`, and `0x018A` reads the i960's
`0xC001`/`0xC012`/`0xC014` back into Z80 `0x8001`/`0x8012`/`0x8014`. The
bank flip is the `0x50` port bit (the FG/ZFG handshake).

Shared header layout, Z80 `0x8000` (i960 offset `0`):

| Z80 | i960 | Meaning |
| --- | --- | --- |
| `0x8000` | `0` | link state: `0x00` searching, `0x01` up, `0xFF` failed |
| `0x8001` | `1` | role, written by the i960 (`1` = master path, else slave/relay) |
| `0x8002` | `2` | link id |
| `0x8003` | `3` | link count |
| `0x8004`/`0x8005` | `4`/`5` | link flags |
| `0x8006` | `6` | current message cursor |
| `0x8008` | `8` | RX descriptor index (stride `0x10`) |
| `0x800A` | `A` | TX descriptor index (stride `0x10`) |
| `0x800E` | `E` | link-active flag |
| `0x8010` | `10` | frameStart `0x2000` |
| `0x8012` | `12` | frameSize `0x0E00` |
| `0x8014` | `14` | frameOffset `0x01C0` |
| `0x8018` | `18` | ring-buffer pointer `0xE1C0` |

The payload ring buffer is `0x0E00` bytes at Z80 `0xE1C0` (i960 shared offset
`0x21C0`); the i960 game re-derives `frameOffset` as `frameSize/2 = 0x0700`.

## Link descriptors

Both rings hold 16-byte descriptors (`0x10` stride, indices `0x8008`/`0x800A`
wrap within `0x100`). `0xC100` (`0x010C`) is the controller-facing ring: the
ISR `0x0356` fills a slot (`[9]`/`[0xA]`/`[0xB]`), clears `[1]`, and kicks
`out ($00),1`. `0xC200` (`0x0119`) is the staging ring that `0x064F` acquires a
free slot from (`[0] == 0x31`) and `0x0500` copies into a `0xC100` slot.

Descriptor field map (offsets are within the 16-byte record):

| Offset | Meaning | Evidence |
| ---: | --- | --- |
| `0` | controller/ownership command `0x31`/`0x35`/`0x37`/`0x3A`/`0x41`; set `0xFF` when consumed | templates; `0x03C8`/`0x04FC`/`0x0547` |
| `1` | constant `0xFF` (HDLC broadcast address candidate) | all templates |
| `2` | header aux `0x00`/`0x01`/`0x02`/`0x05`/`0x62` | templates |
| `3..4` | frame size, little-endian (`0x06C2` = `00 0e`; `0x0677` writes `$8012`) | LIKELY |
| `6` | extra geometry in the type-`0x02` template (`0xE0`) | KNOWN value, role open |
| `8` | message type | `0x047A`/`0x04CA`/`0x0500` |
| `9` | link count | `0x04DF`, `0x0516`, `0x0364` |
| `0xA` | link id | `0x04F6`, `0x053B`, `0x036E` |
| `0xB` | link flags, OR'd with `shared[0x0E]` when building | `0x04E8`, `0x0529` |
| `0xC` | link flags, minus `shared[0x26]` hop offset | `0x04E2`, `0x051F` |
| `0xD..0xF` | zero | templates |

Message types (`[8]`), with the template that seeds each:

| Type | Template | Fields | Meaning |
| --- | --- | --- | --- |
| `0x16` | `0x06A2` | `[9]`/`[0xA]` = count or `-id`, `[0xB]` = active flag | link announce/reset |
| `0x11` | `0x06B2` | `[9]`=count, `[0xA]`=id, `[0xB]`/`[0xC]`=flags | link id/count |
| `0x12` | (built by `0x0500`) | `[0xA]`=id | link ack/id |
| `0x02` | `0x06C2` | `[3..4]`=frame size, `[4]`/`[6]`=geometry | data / vsync |
| `0x10` | `0x06DA` | — | controller seed |

Controller seeds `0x06DA` (`35 FF 62 10 40 05 …`), `0x06EA`/`0x06FA`
(`41 FF …`), `0x070A` (`37 FF …`), `0x071A` (`3A FF …`) are posted at init
(`0x05C8`) and refreshed by `0x02D8`; `0x072A`'s four `00 C0 E1 00` entries
are the ring pointers copied to `0xC300` (`0x055C`).

## Role and hop arithmetic

The role byte `shared[1]` (i960-written) selects the boot path and the id/count
offsets. `sbc a,a`/`cpl` at `0x021B`/`0x0273` derive them:

| `shared[1]` | meaning | `0x800E` active | `0x8024` | `0x8025` id add | `0x8026` count sub |
| ---: | --- | ---: | ---: | ---: | ---: |
| `0` | relay | `0x80` | `0` | `0x00` | `0xFF` |
| `1` | master | `0x01` | `0xFF` | `0` | `0` |
| `2` | slave | `0x80` | `0` | `0xFF` | `0x00` |
| `3` | standalone | `0x80` | `0` | `0xFF` | `0x00` |

`0x0500` applies them: `shared[2] = desc[0xA] + 0x8025` (the slave's id is one
below the master's) and `shared[4] = desc[0xC] - 0x8026` (a relay subtracts one
hop). `0x0356` emits an announce with `[9] = [0xA] = (count == 0 ? -id : count)`
and `[0xB] = shared[0x0E]`.

## Frame handoff and keepalive

The `0x02` type is the per-frame tick, not a control message. In the dispatcher
`0x047A`, an `0x02` descriptor calls `0x0555` (toggle port `0x50`) *before*
`0x0500` services it. That toggle is the dual-port **bank swap**: the Z80 has
been filling the `0x0E00`-byte payload ring for the local i960, and flipping the
bank publishes it. So `0x02` = "new frame + vsync", paired with the ring at
shared `0x21C0`; the other types (`0x16`/`0x11`/`0x12`) are link management and
do not flip the bank.

The link is kept alive by `0x802A`, a counter written to port `0x20`. `0x044D`
walks it back toward zero and `0x0466` increments it; at the `0x00AB` threshold
it counts down, and at `0x64` it clears the active flag `0x800E` and the frame
cursor `0x8006` (`0x0472`), so a silent peer drops the link.

## Frame layout (working hypothesis)

The Z80 never reads frame data: port `0x03` is written exactly once, with the
8-byte init `34 00 00 C1 00 10 10 04` (`0x06D2`, at `0x05A0`), and the only
other accesses are status/control (`0x00`/`0x01`/`0x20`/`0x40`/`0x50`/`0x60`/
`0x70`). The uPD72103 therefore moves frame bytes by DMA against the `0xC000`
bank. `0xC300` holds four `(00, ptr)` entries pointing at the `0xE1C0` ring
(`0x055C`, `0x072A`), i.e. the DMA buffer table. So the on-wire HDLC framing
(flags/FCS) is generated by the controller; the firmware only builds a 16-byte
buffer header plus the `0x0E00` payload ring.

Working layout of the 16-byte buffer/control record (`[8..0xC]` are certain;
the prefix is inferred from usage):

| Offset | Meaning | Confidence |
| ---: | --- | --- |
| `0` | controller command/status: `0x31` = frame present (`0x064F` waits on it), `0x35`/`0x37`/`0x3A`/`0x41` channel ops, `0xFF` = consumed | values KNOWN, roles LIKELY |
| `1` | `0xFF` in every template, cleared to `0` when a slot is posted (`0x0308`/`0x0380`/`0x0612`) | KNOWN |
| `2` | command parameter: `0x00`/`0x01`/`0x02`/`0x05`/`0x62` | KNOWN values, meaning open |
| `3..4` | frame size, little-endian, on the type-`0x02` record (`00 0e`) | LIKELY |
| `5..7`, `0xD..0xF` | zero | KNOWN |
| `8` | message type | KNOWN |
| `9`, `0xA` | link count, link id | KNOWN |
| `0xB`, `0xC` | link flags (`| shared[0x0E]`, `-` hop) | KNOWN |

Bulk frames are the `0x0E00` ring at `0xE1C0`, referenced by the `0xC300`
pointer table and announced by a type-`0x02` record that also flips the bank.
The `0x31`-prefixed records are the link-management messages; the
`0x35`/`0x37`/`0x3A`/`0x41` records are controller buffer setups posted at
init (`0x05C8`) and refresh (`0x02D8`). The controller init bytes
(`34 00 00 C1 00 10 10 04`) are unassigned.

## I/O ports

| Port | Use |
| --- | --- |
| `0x00` | mode/status; polled bits 1 and 5 (`0x0008`/`0x0010`/`0x0018` waits); `out 1` kicks transmit |
| `0x01` | `out 5` startup |
| `0x03` | HDLC (uPD72103) register port; 8-byte init sequence at `0x06D2` |
| `0x20` | link timer output (`0x802A` counter) |
| `0x40` | interrupt enable/ack pulse |
| `0x50` | bank/flip bit (toggled by `0x0555`) |
| `0x60` | ISR acknowledge (`0x013A`) |
| `0x70` | HDLC start/stop (`1`/`0`) |

## Interrupts

Mode 2. The vector table is placed in the i960 bank (`I=0x80`, table at
`0x8000`) with the link ISR `0x0356` at vector `0xEF`; `0x0356` posts the
TX/RX descriptor work (`0x0308`/`0x04B5`) and reports the local link id/count.
`I=0x7D`/`0x7E` later select the ROM vector tables at `0x7D00`/`0x7E00`.

## Status

The mailbox contract, descriptor payload fields (`[8..0xC]`), message types,
and the role/hop arithmetic are recovered. Open items: the `[0]`/`[1]`/`[2]`
controller header semantics and the `[4]`/`[6]` type-`0x02` geometry fields —
both need the uPD72103 register/datasheet context. See
[chip-map.md](chip-map.md#communication-board-837-11615).
