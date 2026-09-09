/* Post-scan admission gates recovered from i960 0x7f5ec-0x7f634. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_transition_post_scan_admission_7f5ec_plan {
    u32 related_170;
    u32 related_172;
    u32 related_state;
    u32 published_status;
    u32 r6_compare_equal_zero;
    u32 halfword_gate_passed;
    u32 state_gate_passed;
    u32 status_index;
    u32 status_gate_passed;
    u32 floating_gate_passed;
    u32 admission_passed;
    u32 target;
    u32 failure_target;
};

void recovered_transition_post_scan_admission_7f5ec(
    u32 related_170, u32 related_172, u32 related_state,
    u32 published_status, u32 r6_compare_equal_zero,
    struct recovered_transition_post_scan_admission_7f5ec_plan *plan)
{
    const u32 halfword_passed = related_170 == 3U || related_172 == 1U;
    const u32 state_passed = related_state == 3U || related_state == 8U;
    const u32 status_index = published_status - 2U;
    const u32 status_passed = status_index > 5U;
    const u32 floating_passed = r6_compare_equal_zero ? 1U : 0U;
    const u32 admitted = halfword_passed && state_passed && status_passed &&
                         floating_passed;

    plan->related_170 = related_170;
    plan->related_172 = related_172;
    plan->related_state = related_state;
    plan->published_status = published_status;
    plan->r6_compare_equal_zero = floating_passed;
    plan->halfword_gate_passed = halfword_passed;
    plan->state_gate_passed = state_passed;
    plan->status_index = status_index;
    plan->status_gate_passed = status_passed;
    plan->floating_gate_passed = floating_passed;
    plan->admission_passed = admitted;
    plan->target = admitted ? 0x0007f634U : 0x0007f6b0U;
    plan->failure_target = 0x0007f6b0U;
}
