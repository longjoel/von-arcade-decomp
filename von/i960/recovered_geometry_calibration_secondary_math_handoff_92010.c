/* Paired calibration helper/math handoff from i960 0x92010-0x92070. */
#include "recovered_common.h"

struct recovered_geometry_calibration_secondary_math_handoff_92010_plan {
    recovered_u32 helper_target;
    recovered_u32 first_table_address;
    recovered_u32 second_table_address;
    recovered_u32 helper_context;
    recovered_u32 response_word;
    recovered_u32 source_sum;
    recovered_u32 first_multiplier;
    recovered_u32 first_bias;
    recovered_u32 second_multiplier;
    recovered_u32 second_bias;
    recovered_u32 next_packet_target;
};

void recovered_geometry_calibration_secondary_math_handoff_92010(
    recovered_u32 helper_context, recovered_u32 response_word,
    recovered_u32 source_sum,
    struct recovered_geometry_calibration_secondary_math_handoff_92010_plan *plan)
{
    plan->helper_target = 0x8e310U;
    plan->first_table_address = 0x2be2cb4U;
    plan->second_table_address = 0x2be2d2cU;
    plan->helper_context = helper_context;
    plan->response_word = response_word;
    plan->source_sum = source_sum;
    plan->first_multiplier = 0xcccccccdU;
    plan->first_bias = 0x3fecccccU;
    plan->second_multiplier = 0xcccccccdU;
    plan->second_bias = 0x400cccccU;
    plan->next_packet_target = 0x92070U;
}
