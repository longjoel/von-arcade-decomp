/* Pure model of the common transition tail at i960 0x000795c4. */
typedef unsigned int u32;

/* Return nonzero when the tail changes the pending transition. */
u32 recovered_object_state_tail(u32 object_tag,
                                u32 current_object_state,
                                u32 caller_object_state,
                                u32 pending_transition,
                                u32 *transition)
{
    if (object_tag != 31U || current_object_state != 3U ||
        caller_object_state != 6U)
        return 0U;

    if (pending_transition == 8U) {
        *transition = 11U;
        return 1U;
    }
    if (pending_transition == 7U) {
        *transition = 10U;
        return 1U;
    }
    if (pending_transition == 9U) {
        *transition = 12U;
        return 1U;
    }
    return 0U;
}
