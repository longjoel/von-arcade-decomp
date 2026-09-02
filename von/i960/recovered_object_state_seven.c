/* State-7 classifier from i960 0x7953c-0x795a8. */
typedef unsigned int u32;

/* mode_bits is 0x504e30 and global_state is 0x504d9c. */
u32 recovered_object_state_seven_route(u32 global_state,
                                       u32 related_state,
                                       u32 caller_state,
                                       u32 mode_bits,
                                       u32 *transition)
{
    u32 selected = 7U;

    if (related_state == 4U) {
        if (global_state > 3U) {
            if (caller_state <= 3U && (mode_bits & (1U << 1)) != 0U) {
                selected = 8U;
            } else if (caller_state > 1U &&
                       (mode_bits & (1U << 2)) != 0U) {
                selected = 9U;
            }
        } else if ((mode_bits & (1U << 2)) != 0U) {
            selected = 9U;
        }
    }

    *transition = selected;
    return 1U;
}
