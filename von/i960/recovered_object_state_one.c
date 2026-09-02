/* State-1 classifier from i960 0x79178-0x791fc. */
typedef unsigned int u32;

static float recovered_object_state_one_float(u32 bits)
{
    union {
        u32 bits;
        float value;
    } raw;

    raw.bits = bits;
    return raw.value;
}

/* mode_bits is 0x504e30 and role_value is 0x504d68. */
u32 recovered_object_state_one_route(u32 timer_bits,
                                     u32 caller_state,
                                     u32 mode_bits,
                                     u32 role_value,
                                     u32 *transition)
{
    float timer = recovered_object_state_one_float(timer_bits);

    if ((mode_bits & (1U << 1)) == 0U || role_value <= 6U) {
        *transition = 7U;
        return 1U;
    }

    if (timer < 0.0f) {
        *transition = 8U;
        return 1U;
    }

    *transition = caller_state <= 2U && (mode_bits & (1U << 2)) != 0U ? 9U : 8U;
    return 1U;
}
