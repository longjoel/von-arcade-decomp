/* State-31 classifier-offset route recovered from 0x7ee90-0x7efb0. */
#include <stdint.h>

typedef uint32_t u32;

extern u32 recovered_signed_band(u32 raw);

struct recovered_state31_classifier_route_7ee90_plan {
    u32 entry_condition_passed;
    u32 global_504d70;
    u32 high_global_arm;
    u32 related_state_64;
    u32 object_state_64;
    int32_t classifier_offset;
    u32 classifier_input;
    u32 classifier_band;
    u32 result_table;
    u32 publication_target;
    u32 callback_target;
    u32 action_value;
    u32 control_value;
    u32 continuation_value;
};

void recovered_state31_classifier_route_7ee90(
    u32 entry_condition_passed, u32 global_504d70, u32 related_state_64,
    u32 object_state_64,
    struct recovered_state31_classifier_route_7ee90_plan *plan)
{
    const u32 high_global = global_504d70 > 4U;
    int32_t offset;

    if (high_global) {
        if (related_state_64 == 6U)
            offset = object_state_64 == 1U ? 0x1800 : 0x800;
        else
            offset = object_state_64 == 3U ? 0x1800 : 0x2800;
    } else if (related_state_64 != 6U) {
        offset = -0xc00;
    } else {
        offset = object_state_64 == 1U ? -0x1800 : -0x800;
    }

    plan->entry_condition_passed = entry_condition_passed != 0U ? 1U : 0U;
    plan->global_504d70 = global_504d70;
    plan->high_global_arm = high_global;
    plan->related_state_64 = related_state_64;
    plan->object_state_64 = object_state_64;
    plan->classifier_offset = offset;
    plan->classifier_input = (u32)(0x00504d64 + offset);
    plan->classifier_band = recovered_signed_band(plan->classifier_input);
    plan->result_table = 0x0072780U;
    plan->publication_target = 0x0007efb0U;
    plan->callback_target = 0x00079050U;
    plan->action_value = 30U;
    plan->control_value = 3U;
    plan->continuation_value = 0x64U;
}
