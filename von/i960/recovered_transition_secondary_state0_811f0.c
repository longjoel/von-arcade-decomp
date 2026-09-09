/* State-0 secondary body recovered from i960 0x811f0-0x81208. */
#include <stdint.h>

typedef uint32_t u32;

static int32_t sign_extend_halfword(u32 value)
{
    return (int32_t)(int16_t)(value & 0xffffU);
}

struct recovered_transition_secondary_state0_811f0_plan {
    u32 related_state;
    u32 related_172;
    u32 related_17e;
    u32 state_gate_passed;
    u32 offset_gate_passed;
    u32 zero_offset_passed;
    u32 target;
};

/* The first two failures branch to the common 0x81208 path. */
void recovered_transition_secondary_state0_811f0(
    u32 related_state,
    u32 related_172,
    u32 related_17e,
    struct recovered_transition_secondary_state0_811f0_plan *plan)
{
    const int32_t loaded_related_172 = sign_extend_halfword(related_172);
    const int32_t loaded_related_17e = sign_extend_halfword(related_17e);
    const u32 state_passed = related_state == 2U ? 1U : 0U;
    const u32 offset_passed = loaded_related_172 == 24 ? 1U : 0U;
    const u32 zero_passed = loaded_related_17e == 0 ? 1U : 0U;

    plan->related_state = related_state;
    plan->related_172 = (u32)loaded_related_172;
    plan->related_17e = (u32)loaded_related_17e;
    plan->state_gate_passed = state_passed;
    plan->offset_gate_passed = state_passed != 0U ? offset_passed : 0U;
    plan->zero_offset_passed = state_passed != 0U && offset_passed != 0U
        ? zero_passed : 0U;
    plan->target = state_passed != 0U && offset_passed != 0U &&
                   zero_passed == 0U ? 0x00081498U : 0x00081208U;
}
