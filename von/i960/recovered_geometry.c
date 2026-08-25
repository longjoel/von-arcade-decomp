/*
 * Recovered from i960 routine 0x00028620.
 *
 * This is a host-side reconstruction, not a replacement geometry processor.
 * The register writes and loop bounds are confirmed by the ROM disassembly,
 * Ghidra output, and the MAME boundary trace. Unknown device side effects are
 * intentionally represented only by their observed bus accesses.
 */

typedef unsigned long u32;
typedef unsigned short u16;

#define GEO_STAGING       ((volatile u32 *)0x00900000)
#define GEO_PROGRAM_PORT  ((volatile u32 *)0x00804000)
#define GEO_IOP           ((volatile u32 *)0x00840000)
#define GEO_CONTROL       ((volatile u32 *)0x00980008)
#define GEO_PHASE         ((volatile u32 *)0x00980020)
#define GEO_READ_START    ((volatile u32 *)0x00803008)
#define MAIN_DATA_SOURCE  ((volatile u16 *)0x02fc6290)

#define GEO_STAGING_WORDS 0x8000U
#define GEO_PROGRAM_WORDS 0x247cU

void recovered_geometry_program_upload(void)
{
    volatile u32 *staging = GEO_STAGING;
    volatile u32 *iop = GEO_IOP;
    volatile const u16 *source = MAIN_DATA_SOURCE;
    u32 index;

    for (index = 0; index < GEO_STAGING_WORDS; ++index)
        staging[index] = 0x07800f0fU;

    *GEO_CONTROL = 0x80000000U;
    *GEO_CONTROL = 0;
    *GEO_READ_START = 0;
    *GEO_CONTROL = 0x80000000U;
    *GEO_PHASE = 0;

    iop[0x000 / 4] = 0x00003100U;
    iop[0x004 / 4] = 0;
    iop[0x008 / 4] = 0x0000c400U;
    iop[0x070 / 4] = 0;
    iop[0x100 / 4] = 0x00020000U;
    iop[0x104 / 4] = 1;
    iop[0x108 / 4] = 0x00000c29U;
    iop[0x000 / 4] = 0x00003110U;
    iop[0x070 / 4] = 0x000000a1U;
    iop[0x070 / 4] = 0;

    for (index = 0; index < GEO_PROGRAM_WORDS; ++index)
        *GEO_PROGRAM_PORT = (u32)(source[index] & 0xffffU);

    *GEO_CONTROL = 0;
    *GEO_READ_START = *GEO_READ_START;
}
