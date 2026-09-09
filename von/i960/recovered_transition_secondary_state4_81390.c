/* State-4 secondary body recovered from i960 0x81390-0x8140c. */
#include <stdint.h>

typedef uint32_t u32;

static float float_from_bits(u32 bits)
{
    union {
        u32 bits;
        float value;
    } converted = {bits};
    return converted.value;
}

struct recovered_transition_secondary_state4_81390_plan {
    u32 control_504dc8;
    u32 flag_504e30;
    u32 result_table;
    u32 result_value;
    u32 result_destination;
    u32 status_destination;
    u32 published_status;
    u32 flag_bit2_set;
    u32 flag_bit1_set;
    float timing_504d60;
    float related_threshold;
    u32 related_float_passed;
    u32 related_float_target;
    u32 bit1_clear_target;
    u32 bit1_set_target;
    u32 control_failure_target;
    u32 target;
};

void recovered_transition_secondary_state4_81390(
    u32 control_504dc8,
    u32 flag_504e30,
    u32 result_value,
    float timing_504d60,
    struct recovered_transition_secondary_state4_81390_plan *plan)
{
    const u32 control_one = control_504dc8 == 1U ? 1U : 0U;
    const u32 bit2 = (flag_504e30 >> 2U) & 1U;
    const u32 bit1 = (flag_504e30 >> 1U) & 1U;
    const float related_threshold = float_from_bits(0x4062c000U);
    const u32 related_passed = timing_504d60 < related_threshold
        ? 1U : 0U;

    plan->control_504dc8 = control_504dc8;
    plan->flag_504e30 = flag_504e30;
    plan->result_table = 0x000728a0U;
    plan->result_value = result_value;
    plan->result_destination = 0x00504d94U;
    plan->status_destination = control_one != 0U ? 0x00504d94U : 0U;
    plan->published_status = control_one != 0U ? 23U : 0U;
    plan->flag_bit2_set = bit2;
    plan->flag_bit1_set = bit1;
    plan->timing_504d60 = timing_504d60;
    plan->related_threshold = related_threshold;
    plan->related_float_passed = related_passed;
    plan->related_float_target = 0x00081570U;
    plan->bit1_clear_target = 0x0008159cU;
    plan->bit1_set_target = 0x0008158cU;
    plan->control_failure_target = 0x000815e0U;
    plan->target = control_one == 0U ? plan->control_failure_target :
                   bit2 != 0U && related_passed != 0U ? plan->related_float_target :
                   bit1 != 0U ? plan->bit1_set_target :
                   plan->bit1_clear_target;
}
