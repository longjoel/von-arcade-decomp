/* Direct routes for the state-8 and state-9 arms at i960 0x795a8/0x795b8. */
typedef unsigned int u32;

/*
 * Both arms write transition 7 and then enter the common 0x795c4 tail.
 * The tail's tag/state/caller guard cannot remap these arms because their
 * current state is already 8 or 9 rather than 3.
 */
u32 recovered_object_state_terminal_route(u32 current_object_state,
                                           u32 *transition)
{
    if (current_object_state != 8U && current_object_state != 9U)
        return 0U;

    *transition = 7U;
    return 1U;
}
