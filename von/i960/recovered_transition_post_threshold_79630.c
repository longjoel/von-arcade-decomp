/* Pure post-threshold selector contract recovered from i960 0x79630. */

#include <stdint.h>

struct recovered_transition_post_threshold_state {
    uint32_t transition;
    uint32_t table_selected;
    uint32_t reentered_shared_state;
    uint32_t action;
};

void recovered_transition_post_threshold_79630(
    uint32_t normalized_index,
    uint32_t prior_transition,
    struct recovered_transition_post_threshold_state *state)
{
    static const uint32_t transitions[8] = {1U, 1U, 2U, 2U,
                                            3U, 3U, 5U, 6U};

    state->transition = prior_transition;
    state->table_selected = 0U;
    state->reentered_shared_state = 1U;
    state->action = 30U;
    if (normalized_index < 8U) {
        state->transition = transitions[normalized_index];
        state->table_selected = 1U;
    }
}
