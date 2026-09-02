/* State-2 classifier from i960 0x791fc-0x7928c. */
typedef unsigned int u32;

static float recovered_object_state_two_float(u32 bits)
{
    union {
        u32 bits;
        float value;
    } raw;

    raw.bits = bits;
    return raw.value;
}

/*
 * mode_bits is 0x504e30, global_state is 0x504d9c, and role_value is
 * 0x504d68. The ROM loads 0x4072c000 (3.79296875), but the effective compare
 * in this arm uses zero and never reads that loaded value.
 */
u32 recovered_object_state_two_route(u32 timer_bits,
                                     u32 caller_state,
                                     u32 mode_bits,
                                     u32 global_state,
                                     u32 role_value,
                                     u32 *transition)
{
    float timer = recovered_object_state_two_float(timer_bits);

    if (global_state == 5U && (mode_bits & (1U << 1)) != 0U) {
        *transition = 8U;
        return 1U;
    }

    if (timer < 0.0f) {
        if (caller_state <= 4U && (mode_bits & (1U << 2)) != 0U)
            *transition = 9U;
        else if (caller_state <= 2U ||
                 (mode_bits & (1U << 1)) == 0U || role_value <= 6U)
            *transition = 7U;
        else
            *transition = 8U;
        return 1U;
    }

    *transition = caller_state > 2U && (mode_bits & (1U << 2)) != 0U ? 9U : 7U;
    return 1U;
}
