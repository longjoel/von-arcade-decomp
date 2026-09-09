/* Offset/classifier route recovered from i960 0x81610-0x8168c. */
#include <stdint.h>

typedef uint32_t u32;

extern u32 recovered_signed_band(u32 raw);

static int32_t sign_extend_halfword(u32 value)
{
    return (int32_t)(int16_t)(value & 0xffffU);
}

struct recovered_transition_offset_classifier_81610_plan {
    u32 object_pointer;
    u32 object_value_74;
    u32 classifier_input_g2;
    u32 timing_low_g0;
    u32 timing_high_g1;
    u32 global_state_504d70;
    u32 signed_g2_minus_3;
    u32 status_tail_target;
    u32 classifier_input;
    u32 classifier_bias;
    u32 classifier_target;
    u32 classifier_index;
    u32 result_table;
    u32 result_value;
    u32 action_destination;
    u32 action_value;
    u32 result_destination;
    u32 result_status;
    u32 helper_target;
    u32 tail_target;
};

void recovered_transition_offset_classifier_81610(
    u32 object_pointer,
    u32 object_value_74,
    u32 classifier_input_g2,
    u32 timing_low_g0,
    u32 timing_high_g1,
    u32 global_state_504d70,
    u32 result_value,
    struct recovered_transition_offset_classifier_81610_plan *plan)
{
    const int32_t signed_g2_minus_3 = (int32_t)classifier_input_g2 - 3;
    const u32 status_tail = signed_g2_minus_3 < 3 ? 1U : 0U;
    const u32 bias = global_state_504d70 > 4U ? 0x00004000U : 0xffffc000U;
    const int32_t normalized_timing = sign_extend_halfword(timing_high_g1);

    plan->object_pointer = object_pointer;
    plan->object_value_74 = object_value_74;
    plan->classifier_input_g2 = classifier_input_g2;
    plan->timing_low_g0 = timing_low_g0;
    plan->timing_high_g1 = timing_high_g1;
    plan->global_state_504d70 = global_state_504d70;
    plan->signed_g2_minus_3 = (u32)signed_g2_minus_3;
    plan->status_tail_target = 0x0008168cU;
    plan->classifier_input = (u32)(normalized_timing + (int32_t)bias);
    plan->classifier_bias = bias;
    plan->classifier_target = 0x00073508U;
    plan->classifier_index = recovered_signed_band(plan->classifier_input);
    plan->result_table = 0x00072780U;
    plan->result_value = result_value;
    plan->action_destination = 0x00504db8U;
    plan->action_value = 30U;
    plan->result_destination = 0x00504d94U;
    plan->result_status = 0U;
    plan->helper_target = 0x00079050U;
    plan->tail_target = status_tail != 0U ? plan->status_tail_target :
                        plan->helper_target;
}
