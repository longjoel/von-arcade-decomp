/* State-5 classifier from i960 0x79400-0x794a8. */
typedef unsigned int u32;

static float recovered_object_state_float(u32 bits)
{
    union {
        u32 bits;
        float value;
    } raw;

    raw.bits = bits;
    return raw.value;
}

/*
 * Return nonzero when the state-5 arm writes the pending transition.
 * caller_state is the entry state's remi-10 value (0..9), and mode_bits is
 * the value read from 0x504e30. The common 0x795c4 tail cannot remap this
 * arm because the current object state is 5.
 */
u32 recovered_object_state_five_route(u32 timer_bits,
                                      u32 caller_state,
                                      u32 mode_bits,
                                      u32 *transition)
{
    float timer = recovered_object_state_float(timer_bits);

    if (timer < 0.0f) {
        *transition = (mode_bits & (1U << 1)) != 0U ? 8U : 7U;
        return 1U;
    }

    /* The ROM also loads 0x40590000 here; the compare uses zero instead. */
    if (timer < 3.640625f) {
        *transition = caller_state > 3U &&
                              (mode_bits & (1U << 2)) != 0U ? 9U : 7U;
        return 1U;
    }

    if (caller_state == 0U) {
        *transition = 7U;
    } else if (caller_state <= 4U) {
        *transition = (mode_bits & (1U << 2)) != 0U ? 9U : 7U;
    } else if ((mode_bits & (1U << 1)) != 0U) {
        *transition = 8U;
    } else {
        *transition = (mode_bits & (1U << 2)) != 0U ? 9U : 7U;
    }
    return 1U;
}
