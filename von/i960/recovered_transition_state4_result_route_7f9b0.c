/* State-4 result route recovered from i960 0x7f9b0-0x7fac8. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_transition_state4_result_route_7f9b0_plan {
    u32 object_state;
    u32 global_504d70;
    int32_t related_184;
    int32_t current_184;
    u32 related_172_shifted;
    int32_t offset;
    int32_t classifier_input;
    u32 classifier_target;
    u32 result_table;
    u32 direct_result;
    u32 alternate_result;
    u32 selected_result;
    u32 inner_band_passed;
    u32 state4_target;
    u32 alternate_target;
    u32 publication_target;
};

void recovered_transition_state4_result_route_7f9b0(
    u32 object_state, u32 global_504d70, int32_t related_184,
    int32_t current_184, u32 related_172_shifted, int32_t classifier_input,
    u32 direct_result, u32 alternate_result,
    struct recovered_transition_state4_result_route_7f9b0_plan *plan)
{
    int32_t offset;
    if (global_504d70 == 0U)
        offset = -0x1000;
    else if (global_504d70 == 9U)
        offset = 0x1000;
    else if (global_504d70 <= 4U)
        offset = -0x4000;
    else
        offset = 0x4000;

    const u32 state4 = object_state == 4U;
    const u32 in_band = related_172_shifted > 0x150000U &&
                        related_172_shifted <= 0x190000U;

    plan->object_state = object_state;
    plan->global_504d70 = global_504d70;
    plan->related_184 = related_184;
    plan->current_184 = current_184;
    plan->related_172_shifted = related_172_shifted;
    plan->offset = offset;
    plan->classifier_input = classifier_input;
    plan->classifier_target = 0x00073508U;
    plan->result_table = in_band ? 0x00072630U : 0x00072780U;
    plan->direct_result = direct_result;
    plan->alternate_result = alternate_result;
    plan->selected_result = in_band ? direct_result : alternate_result;
    plan->inner_band_passed = in_band;
    plan->state4_target = state4 ? 0x0007fabcU : 0U;
    plan->alternate_target = state4 ? 0U : 0x0007fac8U;
    plan->publication_target = state4 ? 0x0007fabcU : 0x0007fac8U;
    (void)current_184;
}
