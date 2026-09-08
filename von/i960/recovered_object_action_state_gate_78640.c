/* Bounded object-action state gate at i960 0x78640. */

#include <stdint.h>

struct recovered_object_action_state_gate_78640_plan {
    uint32_t object_state_offset;
    uint32_t state8;
    uint32_t state8_target;
    uint32_t non_state8_continuation;
    uint32_t return_address;
};

void recovered_object_action_state_gate_78640_plan(
    struct recovered_object_action_state_gate_78640_plan *plan)
{
    plan->object_state_offset = 0x64U;
    plan->state8 = 8U;
    plan->state8_target = 0x00078790U;
    plan->non_state8_continuation = 0x00078658U;
    plan->return_address = 0x00078654U;
}

uint32_t recovered_object_action_state_gate_target(uint32_t object_state)
{
    return object_state == 8U ? 0x00078790U : 0x00078658U;
}
