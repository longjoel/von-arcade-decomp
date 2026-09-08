/* Paired state-6 fast path recovered from i960 0x7f1f8-0x7f210. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state31_double_state6_fastpath_7f1f8_plan {
    u32 object_state;
    u32 related_state;
    u32 paired_state6;
    u32 target;
    u32 fast_target;
    u32 alternate_target;
};

void recovered_state31_double_state6_fastpath_7f1f8(
    u32 object_state, u32 related_state,
    struct recovered_state31_double_state6_fastpath_7f1f8_plan *plan)
{
    const u32 paired = object_state == 6U && related_state == 6U;

    plan->object_state = object_state;
    plan->related_state = related_state;
    plan->paired_state6 = paired ? 1U : 0U;
    plan->target = paired ? 0x0007f31cU : 0x0007f210U;
    plan->fast_target = 0x0007f31cU;
    plan->alternate_target = 0x0007f210U;
}
