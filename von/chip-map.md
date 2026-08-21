# Cyber Troopers: Virtual-On Chip Map

This is the first hardware map for the Japan Revision B twin set (`vonj`). It
combines the MAME Model 2B-CRX configuration, the ROM board labels, and the
component list documented in `m2comm.cpp` for the Virtual-On communication
board.

Status labels:

- **Confirmed**: directly named by the ROM definition, memory map, or board
  documentation.
- **Inferred**: strongly implied by the hardware arrangement or MAME device
  model, but the exact physical part number is not established.
- **Unknown**: requires PCB photographs, schematics, traces, or disassembly.

## Board Set

| Board | Identification | Status | Role |
| --- | --- | --- | --- |
| Main Model 2 board | Model 2B-CRX | Confirmed | i960 host, 3D/video, I/O, sound interfaces |
| ROM board | `834-12346`, attached to `833-12345` | Confirmed | Program, data, model, texture, sound ROMs |
| Communication board | `837-11615` / `837-11615-02` | Confirmed | Virtual-On cabinet-to-cabinet link |
| Billboard controller | Not populated for Virtual-On | Confirmed | Removed from the dedicated MAME configuration |

## Main Board

| Device or chip | Location/function | Status |
| --- | --- | --- |
| Intel i960KB | Main 32-bit host CPU; `maincpu` | Confirmed |
| 50 MHz crystal | i960 clock source; MAME divides by two | Confirmed |
| Analog Devices ADSP-21062 SHARC | Host-booted coprocessor; geometry/render work and coprocessor data | Confirmed |
| 32 MHz crystal | SHARC clock source | Confirmed |
| Sega 315-5649 | Main I/O controller; coin, start, sticks, buttons, DIP input, EEPROM lines | Confirmed |
| Sega System 24 tilemap ASIC/device | Tile and character video memory interface | Confirmed as emulated device; physical marking unknown |
| Model 2 raster/polygon hardware | Polygon engine, framebuffer, palette, color translation, texture paths | Confirmed as a subsystem; individual ASIC markings unknown |
| Intel 8251 USART | Serial interface in the Model 2B memory map | Confirmed; external connection/use in Virtual-On unknown |
| SCSP | Sound CPU/peripheral and PCM synthesis subsystem | Confirmed as emulated device; physical board partition unknown |
| Motorola 68000 | Audio CPU | Confirmed |
| 45.1584 MHz crystal | SCSP/audio clock source; MAME uses `/4` for the 68000 and `/2` for SCSP | Confirmed |
| 93C46, 16-bit serial EEPROM | Persistent configuration/calibration data | Confirmed |
| NVRAM / backup SRAM | `backup1`, 0x4000 bytes in the Model 2B map | Confirmed as a memory region; physical RAM part unknown |
| Host work RAM | 0x00500000-0x005fffff, 1 MiB mapped region | Confirmed as a mapped region; chip population unknown |
| Coprocessor/buffer RAM | 0x00900000-0x0091ffff and related mirrors | Confirmed as a mapped region; physical chip(s) unknown |
| Texture RAM banks | 0x11000000-0x113fffff | Confirmed as a mapped subsystem; physical chip(s) unknown |
| Framebuffer RAM | 0x11600000-0x116fffff | Confirmed as a mapped subsystem; physical chip(s) unknown |
| Four Model 2 timers | 0x00f00000-0x00ffffff | Confirmed as emulated logic; physical implementation unknown |
| Generic FIFO pair | Host/SHARC command and response paths | Confirmed as a logical subsystem; physical implementation unknown |

### Main Board Address Ownership

| Address range | Owner | Purpose |
| --- | --- | --- |
| `00000000-001fffff` | i960 ROM | Main program image |
| `00500000-005fffff` | Host RAM | Work RAM |
| `00900000-0091ffff` | Shared buffer RAM | Geometry/coprocessor buffers |
| `01000000-010fffff` | Tilemap/character device | 2D tile and character data |
| `01800000-0181bfff` | Palette/color translation | Video color state |
| `01a00000-01a03fff` | Communication board shared RAM | Cabinet link mailbox/frame memory |
| `01a04000` | Communication board CN register | Board enable/reset |
| `01a04002` | Communication board FG register | Flip-gate/communication synchronization |
| `01d00000-01d03fff` | Backup SRAM | Persistent state |
| `02000000-03ffffff` | ROM board data window | Game data |
| `06000000-06ffffff` | ROM board extra data window | Additional game data |
| `11000000-113fffff` | Texture RAM | Runtime texture storage |
| `11600000-116fffff` | Framebuffer RAM | Video framebuffer storage |

## Communication Board `837-11615`

The board documentation identifies this as the Virtual-On Model 2B
communication board. The exact Virtual-On firmware is present as
`epr-18643a.7`.

| Chip | Marking/function | Status |
| --- | --- | --- |
| Zilog Z0840008PSC | Z80 communication-board CPU, 8 MHz class part | Confirmed |
| Fujitsu MB84256A-70LL | 32K x 8 dual-port/static RAM devices; the board diagram shows multiple devices | Confirmed family; exact population and bank wiring need PCB confirmation |
| NEC uPD72103A | HDLC/frame-relay communication controller | Confirmed |
| Lattice GAL16V8B-25LP | `315-5751` PAL/GAL | Confirmed |
| Lattice GAL16V8B-25LP | `315-5752` PAL/GAL | Confirmed |
| ICT PEEL18CV8P-15 | `315-5753A` PAL/PEEL | Confirmed |
| AMI 18CV8PC-25 | `315-5547A` PAL | Confirmed |
| M27C1001, 128 KiB | `EPR-18643A.7`, communication firmware | Confirmed |
| Link connectors | CN1/CN3/CN8 and jumper area JP7-JP9 | Board documentation confirms connectors; exact signal assignment unknown |

The current MAME `m2comm` device models the board as shared RAM plus CN/FG
registers. It does not emulate the Z80, uPD72103A, PALs, or the actual HDLC
electrical protocol yet.

## ROM Board Mapping

The `vonj` ROM definition gives the following direct chip-to-region mapping:

| Physical labels | MAME region | Size | Likely role |
| --- | --- | ---: | --- |
| `epr-18664b.15`, `epr-18665b.16`, `epr-18666.13`, `epr-18667.14` | `maincpu` | 2 MiB assembled | i960 program |
| `mpr-18648.11`, `mpr-18649.12`, `mpr-18650.9`, `mpr-18651.10` | `main_data` | 16 MiB loaded | Main executable/data ROM |
| `mpr-18662.29`, `mpr-18663.30` | `copro_data` | 4 MiB loaded | SHARC coprocessor data, collision/height maps |
| `mpr-18654.17`, `mpr-18655.21`, `mpr-18656.18`, `mpr-18657.22` | `polygons` | 16 MiB loaded | Polygon/model data |
| `mpr-18660.27`, `mpr-18658.25`, `mpr-18661.28`, `mpr-18659.26` | `textures` | 8 MiB loaded | Texture data |
| `epr-18643a.7` | `cpu3` | 128 KiB | Communication-board Z80 firmware |
| `epr-18670.31` | `audiocpu` | 512 KiB | 68000 sound program |
| `mpr-18652.32`, `mpr-18653.34` | `samples` | 8 MiB loaded | SCSP sample data |

## Artifact Reconciliation

The local manifest contains 24 files. The `vonj` MAME definition consumes 22
named ROM files from the set above. `vo-prog0.usa` and `vo-prog1.usa` are not
referenced by the `vonj` definition and remain unassigned artifacts until their
board position and contents are identified. They must not be silently treated
as program ROMs.

## Reverse-Engineering Priorities

1. Dump and disassemble `epr-18664b.15`/`epr-18665b.16` as the i960 reset and
   boot path.
2. Identify the i960 ROM-board copy/decompression routines for `main_data`,
   `polygons`, and `textures`.
3. Trace Model 2B communication accesses at `0x01a00000`, `0x01a04000`, and
   `0x01a04002` from the i960 program.
4. Disassemble `epr-18643a.7` separately as Z80 communication firmware rather
   than treating the host-side socket model as the protocol specification.
5. Load `copro_data` and identify SHARC boot/table references before assigning
   collision and height-map subregions.
6. Determine the physical markings and wiring of the main-board raster,
   texture, framebuffer, and RAM devices from PCB photographs or schematics.

## Open Questions

- What are the exact main-board custom ASIC markings for the Model 2B-CRX video
  and raster pipeline?
- How many MB84256A devices are populated on the specific `837-11615` board,
  and how are their banks assigned?
- What are `vo-prog0.usa` and `vo-prog1.usa`, and are they duplicate/renamed
  dumps or chips from another board?
- Which portions of the communication-board firmware are cabinet role setup,
  frame scheduling, and game payload transport?
- Which EEPROM fields configure twin/relay behavior independently of the ROM?
