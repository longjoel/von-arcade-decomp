/* r6 zero gate recovered from i960 0x7f91c-0x7f938. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_transition_r6_zero_gate_7f91c_plan {
    u32 r6_compare_equal_zero;
    u32 equality_gate_passed;
    u32 target;
    u32 return_target;
    u32 arithmetic_route_target;
};

void recovered_transition_r6_zero_gate_7f91c(
    u32 r6_compare_equal_zero,
    struct recovered_transition_r6_zero_gate_7f91c_plan *plan)
{
    const u32 equal = r6_compare_equal_zero ? 1U : 0U;

    plan->r6_compare_equal_zero = equal;
    plan->equality_gate_passed = equal;
    plan->target = equal ? 0x0007f934U : 0x0007f938U;
    plan->return_target = 0x0007f934U;
    plan->arithmetic_route_target = 0x0007f938U;
}
