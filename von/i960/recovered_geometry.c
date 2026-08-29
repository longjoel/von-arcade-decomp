/*
 * Recovered from i960 routine 0x00028620.
 *
 * This is a host-side reconstruction, not a replacement geometry processor.
 * The register writes and loop bounds are confirmed by the ROM disassembly,
 * Ghidra output, and the MAME boundary trace. Unknown device side effects are
 * intentionally represented only by their observed bus accesses.
 */

typedef unsigned int u32;
typedef unsigned short u16;

#define GEO_STAGING       ((volatile u32 *)0x00900000)
#define GEO_PROGRAM_PORT  ((volatile u32 *)0x00804000)
#define GEO_IOP           ((volatile u32 *)0x00840000)
#define GEO_CONTROL       ((volatile u32 *)0x00980008)
#define GEO_PHASE         ((volatile u32 *)0x00980020)
#define GEO_READ_START    ((volatile u32 *)0x00803008)
#define MAIN_DATA_SOURCE  ((volatile u16 *)0x02fc6290)
#define SHARC_CONTROL     ((volatile u32 *)0x00980000)
#define SHARC_FIFO        ((volatile u16 *)0x00884000)
#define SHARC_SOURCE      ((volatile const u16 *)0x0016b58c)
#define COPROCESSOR_FIFO  (*(volatile u32 *)0x00884000)
#define GEO_COMMAND_WINDOW ((volatile u32 *)0x00800000)

#define GEOMETRY_SERVICE_PACKET_WORDS 11U

#define GEO_STAGING_WORDS 0x8000U
#define GEO_PROGRAM_WORDS 0x247cU
#define SHARC_BOOT_WORDS  0x2b1eU

#define GEOMETRY_TABLE_WORDS 0x2000U
#define GEOMETRY_TABLE_STEP  0x7f00U

static int geometry_raw_logb(u32 bits)
{
    u32 exponent;
    u32 fraction;
    int highest;

    bits &= 0x7fffffffU;
    exponent = (bits >> 23) & 0xffU;
    fraction = bits & 0x7fffffU;
    if (exponent != 0)
        return (int)exponent - 127;
    if (fraction == 0)
        return -10000;

    highest = -1;
    while (fraction != 0)
    {
        fraction >>= 1;
        ++highest;
    }
    return highest - 149;
}

/* 0x28b40: logbnr(raw bits) + 128, cvtzri, then clamp to [0, 0x80]. */
static u32 recovered_geometry_float_conversion(u32 raw_bits)
{
    int result = geometry_raw_logb(raw_bits) + 128;

    if (result <= 0)
        return 0;
    if (result > 0x80)
        return 0x80;
    return (u32)result;
}

/* 0x28b80: generate the 0x2000-word byte-packed geometry table. */
void recovered_geometry_buffer_prepare(volatile u32 *output)
{
    u32 index;
    u32 value = 0;

    for (index = 0; index < GEOMETRY_TABLE_WORDS; ++index)
    {
        u32 word = recovered_geometry_float_conversion(value);
        value += GEOMETRY_TABLE_STEP;
        word |= recovered_geometry_float_conversion(value) << 8;
        value += GEOMETRY_TABLE_STEP;
        word |= recovered_geometry_float_conversion(value) << 16;
        value += GEOMETRY_TABLE_STEP;
        word |= recovered_geometry_float_conversion(value) << 24;
        value += GEOMETRY_TABLE_STEP;
        output[index] = word;
    }
}

/* Core transfer from the 0x282e0 SHARC bootstrap routine. */
void recovered_sharc_bootstrap_upload(void)
{
    u32 index;

    *SHARC_CONTROL = 0x80000000U;
    for (index = 0; index < SHARC_BOOT_WORDS; ++index)
        *SHARC_FIFO = SHARC_SOURCE[index];
    *SHARC_CONTROL = 0;
}

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

/* Encode the fixed request emitted by the heavily reused 0x2a990 helper. */
u32 recovered_geometry_service_packet(u32 first, u32 second, u32 *output)
{
    output[0] = 5U;
    output[1] = 16U;
    output[2] = 20U;
    output[3] = first & 0xffffU;
    output[4] = 21U;
    output[5] = second & 0xffffU;
    output[6] = 26U;
    output[7] = 0xbf34fdf4U;
    output[8] = 0xbf34fdf4U;
    output[9] = 0x3f34fdf4U;
    output[10] = 6U;
    return GEOMETRY_SERVICE_PACKET_WORDS;
}

/* Recovered from 0x2a990: submit a SHARC service and forward its response. */
void recovered_geometry_service_submit(u32 first, u32 second, u32 command)
{
    u32 packet[GEOMETRY_SERVICE_PACKET_WORDS];
    u32 response0;
    u32 response1;
    u32 response2;
    u32 index;

    recovered_geometry_service_packet(first, second, packet);
    for (index = 0; index < 10U; ++index)
        COPROCESSOR_FIFO = packet[index];

    response0 = COPROCESSOR_FIFO;
    response1 = COPROCESSOR_FIFO;
    response2 = COPROCESSOR_FIFO;
    (void)response2;

    GEO_COMMAND_WINDOW[0xa0U / 4U] = 0x00000a0aU;
    *GEO_PROGRAM_PORT = response0;
    *GEO_PROGRAM_PORT = response1;
    *GEO_PROGRAM_PORT = command;
    COPROCESSOR_FIFO = packet[10];
}
