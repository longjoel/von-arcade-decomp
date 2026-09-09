/* State/class gate recovered from i960 0x76b00-0x76b9c. */
#include "recovered_common.h"

struct recovered_match_geometry_state_gate_76b00_input {
    recovered_u32 current_state;
    recovered_u32 related_class;
    recovered_u32 related_state;
    recovered_u32 global_bit6_set;
};

struct recovered_match_geometry_state_gate_76b00_plan {
    recovered_u32 early_return_state9;
    recovered_u32 class_19_or_20;
    recovered_u32 state6_arm;
    recovered_u32 bit6_publication_arm;
    recovered_u32 related_state3_arm;
};

void recovered_match_geometry_state_gate_76b00(
    const struct recovered_match_geometry_state_gate_76b00_input *input,
    struct recovered_match_geometry_state_gate_76b00_plan *plan)
{
    recovered_u32 related_class = input->related_class & 0xffffU;

    plan->early_return_state9 = input->current_state == 9U ? 1U : 0U;
    plan->class_19_or_20 = (related_class == 19U || related_class == 20U) ? 1U : 0U;
    plan->state6_arm = (plan->class_19_or_20 != 0U &&
                        input->current_state == 6U) ? 1U : 0U;
    plan->bit6_publication_arm = input->global_bit6_set == 0U ? 1U : 0U;
    plan->related_state3_arm = (plan->bit6_publication_arm != 0U &&
                                input->related_state == 3U) ? 1U : 0U;
}
