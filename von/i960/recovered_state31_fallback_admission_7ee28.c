/* State-31 fallback admission recovered from i960 0x7ee28-0x7ee8c. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state31_fallback_admission_7ee28_plan {
    u32 timing_nonnegative;
    u32 object_state_64;
    u32 related_state_64;
    u32 selector_504e4c;
    u32 object_state_gate_passed;
    u32 related_state_gate_passed;
    u32 selector_gate_passed;
    u32 admitted;
    u32 success_target;
    u32 failure_target;
};

void recovered_state31_fallback_admission_7ee28(
    u32 timing_nonnegative, u32 object_state_64, u32 related_state_64,
    u32 selector_504e4c,
    struct recovered_state31_fallback_admission_7ee28_plan *plan)
{
    const u32 timing_passed = timing_nonnegative != 0U ? 1U : 0U;
    const u32 object_passed = object_state_64 == 3U;
    const u32 related_passed = related_state_64 == 5U ||
                               related_state_64 == 6U;
    const u32 selector_passed = selector_504e4c == 0U ||
                                selector_504e4c == 2U ||
                                selector_504e4c == 5U;
    const u32 admitted = timing_passed && object_passed && related_passed &&
                         selector_passed;

    plan->timing_nonnegative = timing_passed;
    plan->object_state_64 = object_state_64;
    plan->related_state_64 = related_state_64;
    plan->selector_504e4c = selector_504e4c;
    plan->object_state_gate_passed = object_passed;
    plan->related_state_gate_passed = related_passed;
    plan->selector_gate_passed = selector_passed;
    plan->admitted = admitted;
    plan->success_target = 0x0007ee8cU;
    plan->failure_target = admitted ? 0U : 0x0007f0bcU;
}
