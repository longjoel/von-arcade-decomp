/* Follow-up admission recovered from i960 0x7f6b0-0x7f70c. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_transition_followup_admission_7f6b0_plan {
    u32 related_state;
    u32 related_170;
    u32 related_172;
    u32 published_status;
    u32 global_status;
    u32 r6_compare_equal_zero;
    u32 state4_excluded;
    u32 state4_halfword_checked;
    u32 halfword_gate_passed;
    u32 floating_gate_passed;
    u32 status_index;
    u32 status_gate_passed;
    u32 global_index;
    u32 global_gate_passed;
    u32 admission_passed;
    u32 target;
    u32 failure_target;
};

void recovered_transition_followup_admission_7f6b0(
    u32 related_state, u32 related_170, u32 related_172,
    u32 published_status, u32 global_status, u32 r6_compare_equal_zero,
    struct recovered_transition_followup_admission_7f6b0_plan *plan)
{
    const u32 state4 = related_state == 4U;
    const u32 state4_excluded = state4 ? 0U : 1U;
    const u32 halfword_passed = related_170 == 3U;
    const u32 status_index = published_status - 2U;
    const u32 global_index = global_status - 2U;
    const u32 floating_passed = r6_compare_equal_zero ? 1U : 0U;
    const u32 status_passed = status_index > 5U;
    const u32 global_passed = global_index > 5U;
    const u32 admitted = state4_excluded && halfword_passed && floating_passed &&
                         status_passed && global_passed;

    plan->related_state = related_state;
    plan->related_170 = related_170;
    plan->related_172 = related_172;
    plan->published_status = published_status;
    plan->global_status = global_status;
    plan->r6_compare_equal_zero = floating_passed;
    plan->state4_excluded = state4_excluded;
    plan->state4_halfword_checked = state4;
    plan->halfword_gate_passed = halfword_passed;
    plan->floating_gate_passed = floating_passed;
    plan->status_index = status_index;
    plan->status_gate_passed = status_passed;
    plan->global_index = global_index;
    plan->global_gate_passed = global_passed;
    plan->admission_passed = admitted;
    plan->target = admitted ? 0x0007f708U : 0x0007f808U;
    plan->failure_target = 0x0007f808U;
}
