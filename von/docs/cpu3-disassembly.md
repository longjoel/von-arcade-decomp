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

## Message grammar

I/O frames are 16-byte descriptors. `[0]` is an HDLC address/flag byte
(`0x31`/`0x37`/`0x41`), `[1]` is `0xFF`, and `[8]` is the message type. The
firmware dispatches on `(IX+8)` in `0x047A`/`0x04CA`/`0x0500`:

| Type | Meaning (LIKELY) |
| --- | --- |
| `0x16` | link announce/reset (checked by `0x0392`/`0x03DB`) |
| `0x11` | link id/count exchange (`[9]`=count, `[0xB]`/`[0xC]`=flags) |
| `0x12` | link ack/id (`[0xA]`=id) |
| `0x02` | data/vsync frame (template `0x06C2` carries frame geometry) |

Descriptor templates live at `0x06A2` (`0x16`), `0x06B2` (`0x11`), `0x06C2`
(`0x02`), `0x06FA`/`0x070A` (`0x41`/`0x37`). The RX descriptor ring is based at
`0xC100` and TX at `0xC200` (0x10-byte stride, advanced by the `0x8008`/`0x800A`
indices; `0x0664` clears `0xE0` bytes and seeds the frame geometry). `0x072A`'s
16-byte ring-pointer table is copied to `0xC300`.

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

The mailbox contract and the message grammar are now recovered well enough to
drive a replacement link. Open items are noted in
[chip-map.md](chip-map.md#communication-board-837-11615): the exact HDLC
address/control fields and the meaning of the `[4]`/`[5]` link flags.
