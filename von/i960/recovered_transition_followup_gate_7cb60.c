/* Dispatch prefix recovered from i960 0x7cb60-0x7cbc0. */
#include <stdint.h>

typedef uint32_t u32;

enum recovered_transition_followup_gate_7cb60_route {
    RECOVERED_TRANSITION_7CB60_FALLBACK = 0,
    RECOVERED_TRANSITION_7CB60_FOLLOWUP = 1,
    RECOVERED_TRANSITION_7CB60_STATE_HANDLER = 2,
};

struct recovered_transition_followup_gate_7cb60_plan {
    u32 route;
    u32 fallback_target;
    u32 followup_target;
    u32 state_handler_target;
    u32 selector;
    u32 stores_state_handler_result;
    u32 state_handler_result_destination;
};

/*
 * timing_passed and final_compare_passed abstract the two converted-value
 * comparisons.  The first arm and the selector bound both return through
 * 0x783c8.  Only selectors above 7 reach the final comparison: its passed arm
 * calls the related-record follow-up at 0x7c7b0, while its clear arm calls
 * 0x82800 and stores that handler's result at 0x504d80.
 */
void recovered_transition_followup_gate_7cb60(
    u32 timing_passed, u32 selector, u32 final_compare_passed,
    struct recovered_transition_followup_gate_7cb60_plan *plan)
{
    plan->route = RECOVERED_TRANSITION_7CB60_FALLBACK;
    plan->fallback_target = 0x000783c8U;
    plan->followup_target = 0x0007c7b0U;
    plan->state_handler_target = 0x00082800U;
    plan->selector = selector;
    plan->stores_state_handler_result = 0U;
    plan->state_handler_result_destination = 0U;

    if (timing_passed == 0U || selector <= 7U)
        return;

    if (final_compare_passed != 0U) {
        plan->route = RECOVERED_TRANSITION_7CB60_FOLLOWUP;
        return;
    }

    plan->route = RECOVERED_TRANSITION_7CB60_STATE_HANDLER;
    plan->stores_state_handler_result = 1U;
    plan->state_handler_result_destination = 0x00504d80U;
}
