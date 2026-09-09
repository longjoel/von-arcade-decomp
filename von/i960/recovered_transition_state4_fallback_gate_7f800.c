/* State-4 fallback gate recovered from i960 0x7f800-0x7f878. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_transition_state4_fallback_gate_7f800_plan {
    u32 related_state;
    u32 current_below_407f4000;
    u32 r6_compare_equal_zero;
    u32 related_172_shifted;
    u32 control_504e48;
    u32 state_gate_passed;
    u32 timing_gate_passed;
    u32 floating_gate_passed;
    u32 lower_band_passed;
    u32 upper_gap_passed;
    u32 halfword_gate_passed;
    u32 control_gate_passed;
    u32 admission_passed;
    u32 target;
    u32 failure_target;
};

void recovered_transition_state4_fallback_gate_7f800(
    u32 related_state, u32 current_below_407f4000,
    u32 r6_compare_equal_zero, u32 related_172_shifted,
    u32 control_504e48,
    struct recovered_transition_state4_fallback_gate_7f800_plan *plan)
{
    const u32 state_passed = related_state == 4U;
    const u32 timing_passed = current_below_407f4000 ? 1U : 0U;
    const u32 floating_passed = r6_compare_equal_zero ? 1U : 0U;
    const u32 lower_band = related_172_shifted <= 0x160000U;
    const u32 upper_gap = related_172_shifted > 0x180000U;
    const u32 halfword_passed = lower_band || upper_gap;
    const u32 control_passed = control_504e48 == 2U;
    const u32 admitted = state_passed && timing_passed && floating_passed &&
                         halfword_passed && control_passed;

    plan->related_state = related_state;
    plan->current_below_407f4000 = timing_passed;
    plan->r6_compare_equal_zero = floating_passed;
    plan->related_172_shifted = related_172_shifted;
    plan->control_504e48 = control_504e48;
    plan->state_gate_passed = state_passed;
    plan->timing_gate_passed = timing_passed;
    plan->floating_gate_passed = floating_passed;
    plan->lower_band_passed = lower_band;
    plan->upper_gap_passed = upper_gap;
    plan->halfword_gate_passed = halfword_passed;
    plan->control_gate_passed = control_passed;
    plan->admission_passed = admitted;
    plan->target = admitted ? 0x0007f878U : 0x0007f91cU;
    plan->failure_target = 0x0007f91cU;
}
