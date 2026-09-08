/* Connected high-confidence gate chain from i960 producer 0x7d920. */
#include <stdint.h>

typedef uint32_t u32;

enum recovered_state_followup_gate_route_7d920 {
    RECOVERED_FOLLOWUP_ROUTE_DISPATCH = 1,
    RECOVERED_FOLLOWUP_ROUTE_PRIMARY_TABLE = 2,
    RECOVERED_FOLLOWUP_ROUTE_7DB54 = 3,
};

struct recovered_state_followup_gate_chain_7d920_plan {
    u32 ratio_gate_passed;
    u32 span_gate_passed;
    u32 route;
    u32 selector;
    u32 target;
};

void recovered_state_followup_gate_chain_7d920(
    float ratio, int32_t target_difference, u32 counter, u32 selector,
    struct recovered_state_followup_gate_chain_7d920_plan *plan)
{
    plan->ratio_gate_passed = ratio <= 0.4F ? 1U : 0U;
    plan->span_gate_passed = target_difference >= 25 ? 1U : 0U;
    plan->selector = selector;

    if (plan->ratio_gate_passed != 0U || plan->span_gate_passed != 0U) {
        plan->route = RECOVERED_FOLLOWUP_ROUTE_DISPATCH;
        plan->target = 0x0007db70U;
    } else if (counter > 24U) {
        plan->route = RECOVERED_FOLLOWUP_ROUTE_7DB54;
        plan->target = 0x0007db54U;
    } else {
        plan->route = RECOVERED_FOLLOWUP_ROUTE_PRIMARY_TABLE;
        plan->target = 0x0007da8cU;
    }
}
