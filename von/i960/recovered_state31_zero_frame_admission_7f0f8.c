/* Initial admission gates recovered from i960 0x7f0f8-0x7f168. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state31_zero_frame_admission_7f0f8_plan {
    u32 frame_is_zero;
    u32 related_state;
    u32 object_state;
    u32 selector;
    u32 frame_gate_passed;
    u32 related_object_exclusion_passed;
    u32 selector_set_passed;
    u32 primary_gate_passed;
    u32 secondary_selector_passed;
    u32 target;
    u32 failure_target;
    u32 secondary_failure_target;
};

void recovered_state31_zero_frame_admission_7f0f8(
    u32 frame_is_zero, u32 related_state, u32 object_state, u32 selector,
    struct recovered_state31_zero_frame_admission_7f0f8_plan *plan)
{
    const u32 frame_passed = frame_is_zero ? 1U : 0U;
    const u32 exclusion_passed = !(related_state == 7U && object_state == 5U);
    const u32 selector_set = selector == 3U || selector == 6U ||
                             selector == 1U || selector == 4U || selector == 7U;
    const u32 primary_passed = frame_passed && exclusion_passed && selector_set;
    const u32 secondary_passed = selector == 3U || selector == 6U;

    plan->frame_is_zero = frame_is_zero;
    plan->related_state = related_state;
    plan->object_state = object_state;
    plan->selector = selector;
    plan->frame_gate_passed = frame_passed;
    plan->related_object_exclusion_passed = exclusion_passed ? 1U : 0U;
    plan->selector_set_passed = selector_set ? 1U : 0U;
    plan->primary_gate_passed = primary_passed;
    plan->secondary_selector_passed = secondary_passed ? 1U : 0U;
    plan->target = !primary_passed ? 0x0007f32cU :
                   (secondary_passed ? 0x0007f168U : 0x0007f1f8U);
    plan->failure_target = 0x0007f32cU;
    plan->secondary_failure_target = 0x0007f1f8U;
}
