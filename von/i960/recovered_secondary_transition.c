/* Exact transition selector recovered from i960 0x79d20-0x79d50. */
typedef unsigned int u32;

u32 recovered_secondary_transition_select(u32 gate,
                                          u32 object_state,
                                          u32 *transition)
{
    if (gate != 1U)
        return 0U;
    *transition = object_state == 7U ? 2U : 1U;
    return 1U;
}
