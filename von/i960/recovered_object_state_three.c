/* Reduced state-3 classifier from i960 0x7928c-0x79374. */
typedef unsigned int u32;

/*
 * State 3's related-object tests are retained as an input for clarity, but
 * the only branch that could distinguish related_state==3 is reached with
 * caller_state<=2 and mode bit 2 clear; its timer subpath still resolves to
 * transition 7. The reduced observable result therefore does not depend on
 * related_state or timer.
 */
u32 recovered_object_state_three_route(u32 related_state,
                                       u32 role,
                                       u32 caller_state,
                                       u32 mode_bits,
                                       u32 timer_bits,
                                       u32 global_state,
                                       u32 pending_transition,
                                       u32 *transition)
{
    u32 selected;

    (void)related_state;
    (void)timer_bits;
    (void)pending_transition;

    if (role == 4U) {
        if (caller_state > 5U)
            selected = 7U;
        else if ((mode_bits & (1U << 1)) != 0U ||
                 (caller_state <= 2U && (mode_bits & (1U << 2)) != 0U))
            selected = 9U;
        else
            selected = 7U;
    } else if (caller_state <= 2U && (mode_bits & (1U << 2)) != 0U) {
        selected = 9U;
    } else {
        selected = 7U;
    }

    /* 0x79358 -> 0x795b8 overrides the direct selection. */
    if (global_state == 3U && selected == 8U)
        selected = 7U;

    *transition = selected;
    return 1U;
}
