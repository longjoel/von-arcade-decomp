/* State-0 classifier from i960 0x790a4-0x79178. */
typedef unsigned int u32;

static float recovered_object_state_zero_float(u32 bits)
{
    union {
        u32 bits;
        float value;
    } raw;

    raw.bits = bits;
    return raw.value;
}

/*
 * mode_bits is 0x504e30, role_value is 0x504d94, and object_value is
 * 0x504d68. A zero return means the ROM falls through to the common return
 * without writing 0x504d98; the caller's pending value must be preserved.
 */
u32 recovered_object_state_zero_route(u32 timer_bits,
                                      u32 mode_bits,
                                      u32 role_value,
                                      u32 object_value,
                                      u32 *transition)
{
    float timer = recovered_object_state_zero_float(timer_bits);

    if (timer >= 0.0f || (mode_bits & (1U << 1)) == 0U) {
        *transition = 7U;
        return 1U;
    }

    if (role_value == 1U || role_value == 2U || role_value == 3U)
        return 0U;

    if (object_value >= 8U) {
        *transition = 8U;
        return 1U;
    }

    if (role_value == 4U)
        return object_value <= 5U ? (*transition = 8U, 1U) : 0U;

    if (role_value == 5U || role_value == 6U)
        return object_value <= 3U ? (*transition = 8U, 1U) : 0U;

    return 0U;
}
