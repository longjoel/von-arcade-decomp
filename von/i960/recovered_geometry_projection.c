/*
 * Static core recovered from i960 routine 0x0006f6f0.
 *
 * The routine shares the 0x41 lookup table with 0x6ece0, then derives the
 * 0x35 continuation packet from the returned 20-byte record.  Its later
 * callback dispatch and mode-dependent output mask remain device/stateful;
 * this file exposes the exact deterministic request core without hiding that
 * boundary behind a guessed implementation.
 */

typedef unsigned int u32;
typedef unsigned short u16;

#define RECOVERED_GEOMETRY_PROJECTION_SENTINEL 0x47c34f80U

typedef struct recovered_geometry_projection_record {
    u16 unused_0;
    u16 unused_1;
    u32 packet_1;
    u32 packet_2;
    u32 packet_3;
    u32 packet_4;
} recovered_geometry_projection_record;

static int recovered_geometry_projection_truncate(u32 bits)
{
    union {
        u32 bits;
        float value;
    } input;

    input.bits = bits;
    return (int)input.value;
}

static float recovered_geometry_projection_float(u32 bits)
{
    union {
        u32 bits;
        float value;
    } input;

    input.bits = bits;
    return input.value;
}

/* Recover the 0x9baa0 coordinate normalization.  r12:r13 is loaded with
 * the double-precision bit pattern 0x407e000000000000 (480.0), then addrl
 * adds it to each single-precision object field before cvtzri truncates.
 * The divisor is the caller-supplied 31 + r9; the common runtime value is
 * 40, but keeping r9 explicit preserves the actual ABI contract. */
int recovered_geometry_projection_grid_index(u32 first_bits, u32 second_bits,
                                             u32 r9, int *first_quotient,
                                             int *second_quotient,
                                             u32 *index)
{
    int divisor = (int)(31U + r9);
    int first;
    int second;

    if (divisor == 0)
        return 0;
    first = (int)((double)recovered_geometry_projection_float(first_bits) + 480.0);
    second = (int)((double)recovered_geometry_projection_float(second_bits) + 480.0);
    first /= divisor;
    second /= divisor;
    if (first_quotient != (int *)0)
        *first_quotient = first;
    if (second_quotient != (int *)0)
        *second_quotient = second;
    if (index != (u32 *)0)
        *index = (u32)(first * 3 + second);
    return 1;
}

/* The 0x6f820 callback gate skips 0xff and entries without map bit 5. */
int recovered_geometry_projection_callback_quadrant(u32 map_byte, u32 *quadrant)
{
    map_byte &= 0xffU;
    if (map_byte == 0xffU || (map_byte & 0x20U) == 0)
        return 0;
    if (quadrant != (u32 *)0)
        *quadrant = (map_byte - 0x20U) >> 6;
    return 1;
}

/* The 0x6f8a4 branch selects the mask table from object/state. */
u32 recovered_geometry_projection_mask_source(u32 object_pointer, u32 state_word)
{
    if (object_pointer == 0x00503ad0U)
        return 0x00562c80U;
    return state_word != 0U ? 0x00562c84U : 0U;
}

/* The 0x9bc48 geometry loop treats each stored table word as sixteen
 * consecutive 2-bit fields.  The selected field is subsequently shifted
 * left by 14 (the i960 sequence shifts by 30 and then logically back by 16)
 * before the signed geometry comparison. */
u32 recovered_geometry_projection_mask_field(u32 mask_word, u32 slot)
{
    if (slot >= 16U)
        return 0U;
    return (mask_word >> (slot * 2U)) & 3U;
}

u32 recovered_geometry_projection_mask_field_scaled(u32 mask_word, u32 slot)
{
    return recovered_geometry_projection_mask_field(mask_word, slot) << 14U;
}

/* One iteration of the 0x9bc48 loop computes
 *   (0x4800 + (field << 14) - (int16_t)sample) & 0xffff
 * before comparing the result with 0x8fff. */
u32 recovered_geometry_projection_mask_threshold(u32 mask_word, u32 slot,
                                                 u32 sample_word)
{
    int sample = (int)(short)(sample_word & 0xffffU);
    u32 adjusted = 0x4800U + recovered_geometry_projection_mask_field_scaled(
        mask_word, slot);
    return (adjusted - (u32)sample) & 0xffffU;
}

int recovered_geometry_projection_mask_threshold_passes(u32 mask_word,
                                                         u32 slot,
                                                         u32 sample_word)
{
    return recovered_geometry_projection_mask_threshold(mask_word, slot,
                                                         sample_word) <= 0x8fffU;
}

int recovered_geometry_projection_validate(u32 x_bits, u32 y_bits,
                                            u32 quadrant, u32 threshold_bits,
                                            u32 *result)
{
    float x;
    float y;
    float lhs;
    int negative_quadrant;
    int valid;

    if (quadrant > 3U)
        return 0;

    x = recovered_geometry_projection_float(x_bits);
    y = recovered_geometry_projection_float(y_bits);
    negative_quadrant = quadrant == 1U || quadrant == 2U;
    /* The ROM loads a float-looking g5 constant, but the arithmetic consumes
     * g4 and fp0; g5 is dead on every validator path. */
    (void)threshold_bits;
    lhs = negative_quadrant ? -x : x;
    valid = negative_quadrant ? lhs <= y : lhs >= y;
    if (!valid && result != (u32 *)0)
        *result = RECOVERED_GEOMETRY_PROJECTION_SENTINEL;
    return valid;
}

/* Recover the negative-result output mask at 0x6f8b8.  The caller chooses
 * mask_bits from 0x562c80 or 0x562c84 according to its object/state branch. */
u16 recovered_geometry_projection_output_mask(u16 mask_bits,
                                              u32 lookup_response)
{
    u32 slot = (lookup_response - 1U) & ~1U;
    int shift = (int)slot - 14;
    u32 selected;
    u32 value;

    /* The ROM's valid device responses keep this shift in range. Keep the
     * host helper defined for malformed responses rather than invoking C UB. */
    if (shift < 0 || shift >= 32)
        return 0;
    /* i960 shlo has the count first: ``shlo g5,3,g6`` means 3 << slot. */
    selected = (u32)mask_bits & (3U << slot);
    value = (u32)(int)(short)(selected & 0xffffU);
    value <<= shift;
    return (u16)value;
}

/*
 * Model the immediate 0x6f6f0 consumer of the opcode-0x35 result. A
 * nonnegative result publishes the x/40 quotient in the high byte lane. A
 * negative result, including the helper's -0.1 sentinel, diverts to the
 * packed mask-selection tail at 0x6f8a4.
 * Return 0 for the ordinary quotient route and 1 for the negative route.
 */
int recovered_geometry_projection_result_route(
    u32 result_bits, u32 x_quotient, u32 lookup_response,
    u32 object_pointer, u32 state_word, u16 special_mask, u16 general_mask,
    u32 *output)
{
    float result = recovered_geometry_projection_float(result_bits);
    u32 source = recovered_geometry_projection_mask_source(
        object_pointer, state_word);
    u16 mask = source == 0x00562c80U ? special_mask : general_mask;

    if (!(result < 0.0f))
    {
        if (output != (u32 *)0)
            *output = x_quotient << 8;
        return 0;
    }
    if (output != (u32 *)0)
        *output = source == 0U ? 0U : recovered_geometry_projection_output_mask(
            mask, lookup_response);
    return 1;
}

/*
 * Build the 0x41 request and 0x35 continuation emitted by 0x6f6f0.
 * packet receives: 53, packet_1, x_bits, packet_3, y_bits, packet_4,
 * packet_4, packet_2 with bit 31 inverted.  The returned table quotients
 * are the values used by the routine's later output-selection tail.
 */
int recovered_geometry_projection_packet(
    u32 x_bits,
    u32 y_bits,
    u32 lookup_index,
    const recovered_geometry_projection_record *table,
    u32 *request_index,
    u32 *packet,
    u32 *x_quotient,
    u32 *y_quotient)
{
    int x = recovered_geometry_projection_truncate(x_bits);
    int y = recovered_geometry_projection_truncate(y_bits);
    const recovered_geometry_projection_record *record;

    if (x < 0 || x >= 1024 || y < 0 || y >= 1024)
        return 0;

    *request_index = ((u32)y >> 1 << 9) + ((u32)x >> 1);
    record = &table[lookup_index];
    *x_quotient = (u32)x / 40U;
    *y_quotient = (u32)y / 40U;

    packet[0] = 53U;
    packet[1] = record->packet_1;
    packet[2] = x_bits;
    packet[3] = record->packet_3;
    packet[4] = y_bits;
    packet[5] = record->packet_4;
    packet[6] = record->packet_4;
    packet[7] = record->packet_2 ^ 0x80000000U;
    return 1;
}
