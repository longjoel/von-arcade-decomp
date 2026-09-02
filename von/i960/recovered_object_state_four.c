/* State-4 classifier from i960 0x79374-0x79400. */
typedef unsigned int u32;

static float recovered_object_state_four_float(u32 bits)
{
    union {
        u32 bits;
        float value;
    } raw;

    raw.bits = bits;
    return raw.value;
}

/*
 * mode_bits is 0x504e30 and role_value is 0x504d68. The ROM loads
 * 0x4072c000 (3.79296875) in the negative-time path, but its first compare
 * uses zero; the loaded value is therefore not an effective state-4 cutoff.
 */
u32 recovered_object_state_four_route(u32 timer_bits,
                                      u32 caller_state,
                                      u32 mode_bits,
                                      u32 role_value,
                                      u32 *transition)
{
    float timer = recovered_object_state_four_float(timer_bits);

    if (timer < 0.0f) {
        if (caller_state > 5U && (mode_bits & (1U << 2)) != 0U) {
            *transition = 9U;
            return 1U;
        }
        if (caller_state <= 2U || (mode_bits & (1U << 1)) == 0U ||
            role_value >= 6U) {
            *transition = 7U;
            return 1U;
        }
        *transition = 8U;
        return 1U;
    }

    *transition = (mode_bits & (1U << 1)) != 0U && role_value < 6U ? 8U : 7U;
    return 1U;
}
