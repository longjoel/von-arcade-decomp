/* State-6 classifier plus the 0x795c4 remap from i960 0x794ac-0x7953c. */
typedef unsigned int u32;

static int recovered_object_state_six_special_value(u32 value)
{
    return value == 1U || value == 3U || value == 4U ||
           value == 6U || value == 7U;
}

u32 recovered_object_state_six_route(u32 role_value,
                                     u32 mode_bits,
                                     u32 related_tag,
                                     u32 related_state,
                                     u32 global_substate,
                                     u32 *transition)
{
    u32 selected;

    if (role_value == 5U || role_value == 6U) {
        selected = 1U;
    } else if (role_value >= 7U || role_value == 0U || role_value == 4U) {
        selected = (mode_bits & (1U << 1)) != 0U ? 8U : 7U;
    } else {
        /* The ROM's role 1..3 path has an exceptional guarded subcase. */
        if (related_tag == 31U && related_state == 3U &&
            recovered_object_state_six_special_value(global_substate)) {
            selected = (mode_bits & (1U << 1)) != 0U &&
                               (global_substate == 3U || global_substate == 6U)
                           ? 8U : 7U;
        } else {
            selected = (mode_bits & (1U << 1)) != 0U ? 8U : 7U;
        }
    }

    /* Current state is 6, so the common tail can remap only 7 and 8. */
    if (related_tag == 31U && related_state == 3U) {
        if (selected == 7U)
            selected = 10U;
        else if (selected == 8U)
            selected = 11U;
    }

    *transition = selected;
    return 1U;
}
