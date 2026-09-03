/* Unified behavioral dispatcher for i960 0x79050-0x79630. */
#include "recovered_object_state_pipeline.h"

typedef unsigned int u32;

u32 recovered_object_state_zero_route(u32, u32, u32, u32, u32 *);
u32 recovered_object_state_one_route(u32, u32, u32, u32, u32 *);
u32 recovered_object_state_two_route(u32, u32, u32, u32, u32, u32 *);
u32 recovered_object_state_three_route(u32, u32, u32, u32, u32, u32, u32, u32 *);
u32 recovered_object_state_four_route(u32, u32, u32, u32, u32 *);
u32 recovered_object_state_five_route(u32, u32, u32, u32 *);
u32 recovered_object_state_six_route(u32, u32, u32, u32, u32, u32 *);
u32 recovered_object_state_seven_route(u32, u32, u32, u32, u32 *);
u32 recovered_object_state_terminal_route(u32, u32 *);

/*
 * Dispatch one already-decoded state. The function returns zero for the ROM's
 * invalid-state/no-write cases and one when the selected arm wrote transition.
 * Caller state is supplied explicitly because the ROM derives it from the
 * incoming state before entering the table; this keeps the pointer plumbing
 * outside the pure arm models.
 */
u32 recovered_object_state_dispatch(const struct recovered_object_state_context *context,
                                    u32 *transition)
{
    switch (context->state) {
    case 0U:
        return recovered_object_state_zero_route(
            context->timer_bits, context->mode_bits, context->role_d94,
            context->object_d68, transition);
    case 1U:
        return recovered_object_state_one_route(
            context->timer_bits, context->caller_state, context->mode_bits,
            context->object_d68, transition);
    case 2U:
        return recovered_object_state_two_route(
            context->timer_bits, context->caller_state, context->mode_bits,
            context->global_state, context->object_d68, transition);
    case 3U:
        return recovered_object_state_three_route(
            context->related_state, context->role_d94, context->caller_state,
            context->mode_bits, context->timer_bits, context->global_state,
            *transition, transition);
    case 4U:
        return recovered_object_state_four_route(
            context->timer_bits, context->caller_state, context->mode_bits,
            context->object_d68, transition);
    case 5U:
        return recovered_object_state_five_route(
            context->timer_bits, context->caller_state, context->mode_bits,
            transition);
    case 6U:
        return recovered_object_state_six_route(
            context->role_d94, context->mode_bits, context->related_tag,
            context->related_state, context->global_substate, transition);
    case 7U:
        return recovered_object_state_seven_route(
            context->global_state, context->related_state, context->caller_state,
            context->mode_bits, transition);
    case 8U:
    case 9U:
        return recovered_object_state_terminal_route(context->state, transition);
    default:
        return 0U;
    }
}
