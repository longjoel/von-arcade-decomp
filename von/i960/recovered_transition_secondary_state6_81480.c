/* State-6 secondary body recovered from i960 0x81480-0x814b4. */
#include <stdint.h>

typedef uint32_t u32;

static int32_t sign_extend_halfword(u32 value)
{
    return (int32_t)(int16_t)(value & 0xffffU);
}

struct recovered_transition_secondary_state6_81480_plan {
    u32 object_state_64;
    u32 related_172;
    u32 related_17e;
    u32 current_state_504d68;
    u32 special_state_match;
    u32 special_related_match;
    u32 special_zero_match;
    u32 result_table;
    u32 result_value;
    u32 result_destination;
    u32 special_target;
    u32 fallback_target;
    u32 target;
};

void recovered_transition_secondary_state6_81480(
    u32 object_state_64,
    u32 related_172,
    u32 related_17e,
    u32 current_state_504d68,
    u32 result_value,
    struct recovered_transition_secondary_state6_81480_plan *plan)
{
    const int32_t loaded_related_172 = sign_extend_halfword(related_172);
    const int32_t loaded_related_17e = sign_extend_halfword(related_17e);
    const u32 state_match = object_state_64 == 2U ? 1U : 0U;
    const u32 related_match = loaded_related_172 == 24 ? 1U : 0U;
    const u32 zero_match = loaded_related_17e == 0 ? 1U : 0U;
    const u32 special = state_match != 0U && related_match != 0U &&
        zero_match != 0U ? 1U : 0U;

    plan->object_state_64 = object_state_64;
    plan->related_172 = (u32)loaded_related_172;
    plan->related_17e = (u32)loaded_related_17e;
    plan->current_state_504d68 = current_state_504d68;
    plan->special_state_match = state_match;
    plan->special_related_match = related_match;
    plan->special_zero_match = zero_match;
    plan->result_table = special != 0U ? 0x00072780U : 0U;
    plan->result_value = result_value;
    plan->result_destination = special != 0U ? 0x00504d94U : 0U;
    plan->special_target = 0x000815e0U;
    plan->fallback_target = 0x000814b4U;
    plan->target = special != 0U ? plan->special_target : plan->fallback_target;
}
