/* Post-threshold transition dispatch recovered from i960 0x79720-0x79834. */

#include <stdint.h>

struct recovered_transition_dispatch_79720_state {
    uint32_t transition;
    uint32_t action;
    uint32_t status;
    uint32_t reentered_shared_state;
    uint32_t entered_table;
};

/*
 * threshold_passed represents the unresolved floating comparison at the
 * entry and is intentionally supplied by the caller. The table body itself
 * is exact: caller states 0/1, 2..4, 5..7, and 8/9 use the static arms below.
 */
void recovered_transition_dispatch_79720(
    uint32_t threshold_passed,
    uint32_t caller_state,
    uint32_t transition_gate,
    struct recovered_transition_dispatch_79720_state *state)
{
    state->entered_table = 0U;
    state->reentered_shared_state = 0U;
    if (threshold_passed == 0U)
        return;

    state->entered_table = 1U;
    state->action = 5U;
    if (caller_state > 9U)
        return;

    if ((caller_state <= 1U || caller_state >= 8U) &&
        transition_gate == 1U) {
        state->status = 1U;
        state->reentered_shared_state = 1U;
        state->transition = 1U;
        state->action = 30U;
        return;
    }

    if (caller_state <= 1U || caller_state >= 8U)
        state->transition = caller_state <= 1U ? 18U : 19U;
    else if (caller_state <= 4U)
        state->transition = 12U;
    else
        state->transition = 13U;
}
