/*
 * Bounded recovered-C model for the i960 projection tail at 0x0006f820-0x0006f900,
 * the consumer half of the routine whose packet core lives at 0x0006f6f0.
 *
 * The prefix builds and publishes the seven-word 0x35 continuation and reads the
 * board response back into r8 (saved to 0x40(fp)).  This tail then:
 *
 *   0x6f820  ld 0x51bb20,g0          map base pointer
 *   0x6f828  st r8,0x40(fp)          save the response
 *   0x6f82c  shlo 5,g13,g4           (z/40) << 5
 *   0x6f830  addo r4,g4,g4           + (x/40)
 *   0x6f834  ldob (g0)[g4],g4        map byte
 *   0x6f838  lda 0xff,r9
 *   0x6f83c  mov g4,r4
 *   0x6f844  cmpibe g5,r9,0x6f87c    0xff gate
 *   0x6f848  bbc 5,r4,0x6f87c        bit-5 gate
 *   0x6f84c  ld 0x5770f0,g4          callback table state
 *   0x6f860  lda (g4)[g4*2],g4       3 * state
 *   0x6f864  ld 0x6eb70[g4*8],g13    callback = table[state*24]
 *   0x6f86c  lda 0xffffffe0(g5),g4   map - 0x20
 *   0x6f874  shri 6,g4,g2            quadrant
 *   0x6f878  callx (g13)
 *   0x6f87c  ld 0x40(fp),g0          response as single real -> fp0
 *   0x6f884  mov 0,r8
 *   0x6f888  lda 0x408f4000,r9       r8:r9 = double 1000.0 (0x408f400000000000)
 *   0x6f890  cmprl fp0,r8
 *   0x6f894  bl 0x6f8a4              response < 1000.0 selects the mask path
 *   0x6f898  shlo 8,r4,g4            map << 8
 *   0x6f89c  stos g4,(r6)            *out
 *   0x6f8a4  lda 0x503ad0,r9         special object pointer
 *   0x6f8ac  cmpibne r7,r9,0x6f8e0
 *   0x6f8b0  ldos 0x562c80,g4        special mask
 *   0x6f8b8  subo 1,r5,g5            slot = (lookup - 1) & ~1
 *   0x6f8c0  shlo g5,3,g6
 *   0x6f8c4  and g4,g6,g4
 *   0x6f8c8  subo g5,14,g5           shift = 14 - slot
 *   0x6f8cc  shlo 16,g4,g4
 *   0x6f8d0  shri 16,g4,g4           sign-extend the 16-bit field
 *   0x6f8d4  shlo g5,g4,g4
 *   0x6f8d8  stos g4,(r6)
 *   0x6f8e0  ld 0x503a7c,g4          mode word
 *   0x6f8e8  cmpibne 0,g4,0x6f8f8
 *   0x6f8ec  ldos 0x562c84,g4        general mask
 *   0x6f8f4  b 0x6f8b8
 *   0x6f8f8  stos g14,(r6)           runtime fallback word
 *   0x6f8fc  ret
 *
 * The callback target itself and the live map/mask globals are runtime state;
 * this file models the exact address arithmetic, the byte-map gate, the
 * quadrant predicate, the 1000.0 double branch, and the three mask-source
 * outputs.  The upstream reject branch of the same routine stores the 99999.0
 * sentinel 0x47c34f80 at 0x6f74c; it is included here as the tail's sibling
 * failure route because the packet core cannot publish a usable response.
 */

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

#define RECOVERED_GEOMETRY_PROJECTION_TAIL_SENTINEL 0x47c34f80U

#define RECOVERED_GEOMETRY_PROJECTION_TAIL_MAP_BASE_GLOBAL 0x0051bb20U
#define RECOVERED_GEOMETRY_PROJECTION_TAIL_CALLBACK_TABLE 0x0006eb70U
#define RECOVERED_GEOMETRY_PROJECTION_TAIL_CALLBACK_STATE_GLOBAL 0x005770f0U
#define RECOVERED_GEOMETRY_PROJECTION_TAIL_SPECIAL_OBJECT 0x00503ad0U
#define RECOVERED_GEOMETRY_PROJECTION_TAIL_SPECIAL_MASK 0x00562c80U
#define RECOVERED_GEOMETRY_PROJECTION_TAIL_GENERAL_MASK 0x00562c84U
#define RECOVERED_GEOMETRY_PROJECTION_TAIL_MODE_GLOBAL 0x00503a7cU

/* 0x408f4000 is the high word of the double 1000.0 published through the
 * r8:r9 register pair at 0x6f884/0x6f888. */
#define RECOVERED_GEOMETRY_PROJECTION_TAIL_LIMIT_HIGH_WORD 0x408f4000U

#define RECOVERED_GEOMETRY_PROJECTION_TAIL_ROUTE_MAP 0
#define RECOVERED_GEOMETRY_PROJECTION_TAIL_ROUTE_SPECIAL 1
#define RECOVERED_GEOMETRY_PROJECTION_TAIL_ROUTE_GENERAL 2
#define RECOVERED_GEOMETRY_PROJECTION_TAIL_ROUTE_FALLBACK 3

typedef struct recovered_geometry_projection_tail_state {
    u32 cell;
    u32 map_byte;
    u32 quadrant;
    u32 callback_address;
    int dispatched;
    int route;
    u32 output;
} recovered_geometry_projection_tail_state;

static float recovered_geometry_projection_tail_float(u32 bits)
{
    union {
        u32 bits;
        float value;
    } input;

    input.bits = bits;
    return input.value;
}

/* The 0x6f82c pair of integer instructions indexes the byte map with the two
 * 640.0-biased, truncated, 40-unit quotients.  i960 divi truncates toward zero
 * and shlo is a 32-bit logical shift, so the host uses u32 throughout. */
int recovered_geometry_projection_tail_cell(u32 x_bits, u32 z_bits, u32 *cell)
{
    int xs = (int)((double)recovered_geometry_projection_tail_float(x_bits) + 640.0);
    int zs = (int)((double)recovered_geometry_projection_tail_float(z_bits) + 640.0);
    u32 x_quotient = (u32)(xs / 40);
    u32 z_quotient = (u32)(zs / 40);

    if (cell != (u32 *)0)
        *cell = (z_quotient << 5) + x_quotient;
    return 1;
}

/* 0x6f834: ldob (g0)[g4],g4.  The real routine loads the base pointer from
 * 0x51bb20; the host passes the equivalent byte bank directly. */
int recovered_geometry_projection_tail_map_byte(const u8 *map_bank, u32 cell,
                                                u32 *map_byte)
{
    if (map_bank == (const u8 *)0)
        return 0;
    if (map_byte != (u32 *)0)
        *map_byte = (u32)map_bank[cell];
    return 1;
}

/* 0x6f838-0x6f848: the 0xff compare and bit-5 test reject the callback. */
int recovered_geometry_projection_tail_gate(u32 map_byte, u32 *quadrant)
{
    map_byte &= 0xffU;
    if (map_byte == 0xffU || (map_byte & 0x20U) == 0U)
        return 0;
    if (quadrant != (u32 *)0)
        *quadrant = (map_byte - 0x20U) >> 6;
    return 1;
}

/* 0x6f84c-0x6f864: lda (g4)[g4*2] then ld 0x6eb70[g4*8] address 24-byte
 * records, so the byte offset into the callback table is 24 * state. */
u32 recovered_geometry_projection_tail_callback_offset(u32 callback_state)
{
    return callback_state * 24U;
}

u32 recovered_geometry_projection_tail_callback_address(u32 callback_state)
{
    return RECOVERED_GEOMETRY_PROJECTION_TAIL_CALLBACK_TABLE +
           recovered_geometry_projection_tail_callback_offset(callback_state);
}

/* 0x6f8b8-0x6f8d4: select the two-bit field at slot = (lookup-1)&~1, sign
 * extend it with the shlo/shri 16 pair, then place it by the i960
 * subo g5,14,g5 left shift (14 - slot).  Counts outside [0,31] shift to zero. */
u32 recovered_geometry_projection_tail_mask_output(u16 mask_bits,
                                                   u32 lookup_index)
{
    u32 slot = (lookup_index - 1U) & ~1U;
    u32 shift;
    u32 selected;
    int field;

    if (slot >= 32U)
        return 0U;
    shift = 14U - slot;
    if (shift >= 32U)
        return 0U;
    selected = (u32)mask_bits & (3U << slot);
    field = (int)(short)(selected & 0xffffU);
    return (u32)field << shift;
}

/* 0x6f87c-0x6f8fc: the response is loaded as a single real and compared with
 * the double 1000.0 in r8:r9; fp0 >= 1000.0 publishes map << 8 while the bl
 * target selects the special mask, the general mask, or the runtime fallback. */
int recovered_geometry_projection_tail_route(
    u32 result_bits, u32 map_byte, u32 object_pointer, u32 mode_word,
    u32 lookup_index, u16 special_mask, u16 general_mask, u32 fallback,
    u32 *output)
{
    float result = recovered_geometry_projection_tail_float(result_bits);

    if (!((double)result < 1000.0))
    {
        if (output != (u32 *)0)
            *output = (map_byte & 0xffU) << 8U;
        return RECOVERED_GEOMETRY_PROJECTION_TAIL_ROUTE_MAP;
    }
    if (object_pointer == RECOVERED_GEOMETRY_PROJECTION_TAIL_SPECIAL_OBJECT)
    {
        if (output != (u32 *)0)
            *output = recovered_geometry_projection_tail_mask_output(
                special_mask, lookup_index);
        return RECOVERED_GEOMETRY_PROJECTION_TAIL_ROUTE_SPECIAL;
    }
    if (mode_word == 0U)
    {
        if (output != (u32 *)0)
            *output = recovered_geometry_projection_tail_mask_output(
                general_mask, lookup_index);
        return RECOVERED_GEOMETRY_PROJECTION_TAIL_ROUTE_GENERAL;
    }
    if (output != (u32 *)0)
        *output = fallback;
    return RECOVERED_GEOMETRY_PROJECTION_TAIL_ROUTE_FALLBACK;
}

/* 0x6f74c: the packet core's invalid-coordinate return publishes the 99999.0
 * float sentinel in g0 and stores the fallback (zero) to *out. */
u32 recovered_geometry_projection_tail_reject(u32 *output)
{
    if (output != (u32 *)0)
        *output = 0U;
    return RECOVERED_GEOMETRY_PROJECTION_TAIL_SENTINEL;
}

/* Whole-tail entry: map lookup, gate, callback address, and output route. */
int recovered_geometry_projection_tail_6f820(
    u32 x_bits, u32 z_bits, const u8 *map_bank, u32 callback_state,
    u32 object_pointer, u32 mode_word, u32 lookup_index, u32 result_bits,
    u16 special_mask, u16 general_mask, u32 fallback,
    recovered_geometry_projection_tail_state *state)
{
    recovered_geometry_projection_tail_state local;

    local.cell = 0U;
    local.map_byte = 0U;
    local.quadrant = 0U;
    local.callback_address = 0U;
    local.dispatched = 0;
    local.route = 0;
    local.output = 0U;

    if (map_bank == (const u8 *)0)
        return 0;

    recovered_geometry_projection_tail_cell(x_bits, z_bits, &local.cell);
    local.map_byte = (u32)map_bank[local.cell];
    local.dispatched = recovered_geometry_projection_tail_gate(
        local.map_byte, &local.quadrant);
    local.callback_address = local.dispatched
        ? recovered_geometry_projection_tail_callback_address(callback_state)
        : 0U;
    local.route = recovered_geometry_projection_tail_route(
        result_bits, local.map_byte, object_pointer, mode_word, lookup_index,
        special_mask, general_mask, fallback, &local.output);

    if (state != (recovered_geometry_projection_tail_state *)0)
        *state = local;
    return 1;
}
