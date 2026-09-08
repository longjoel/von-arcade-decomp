/* Post-threshold state schedule recovered from i960 0x79840-0x7990c. */

#include <stdint.h>

struct recovered_transition_728d0_variant_state {
    uint32_t transition;
    uint32_t action;
    uint32_t status;
    uint32_t reentered_shared_state;
    uint32_t entered_table;
};

/* The 0x728d0 ROM value is supplied because its contents are not yet decoded. */
void recovered_transition_728d0_variant_79840(
    uint32_t threshold_passed,
    uint32_t caller_state,
    uint32_t table_transition,
    uint32_t transition_gate,
    struct recovered_transition_728d0_variant_state *state)
{
    state->entered_table = 0U;
    state->reentered_shared_state = 0U;
    if (threshold_passed == 0U)
        return;

    state->entered_table = 1U;
    state->transition = table_transition;
    state->action = 5U;

    if ((caller_state <= 1U || caller_state > 7U) &&
        transition_gate == 1U) {
        state->status = 1U;
        state->reentered_shared_state = 1U;
        state->transition = caller_state <= 1U ? 1U : 3U;
        state->action = 30U;
    } else if (caller_state <= 1U) {
        state->transition = 18U;
    } else if (caller_state > 7U) {
        state->transition = 19U;
    }
}
