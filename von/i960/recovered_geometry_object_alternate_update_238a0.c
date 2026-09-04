/* Alternate object update recovered from i960 0x238a0-0x23950. */
#include <stdint.h>
#include "recovered_float.h"

typedef uint32_t u32;

struct recovered_geometry_object_alternate_plan {
    u32 fifo_address;
    u32 first_command;
    u32 first_argument_0;
    u32 first_argument_1;
    u32 first_response;
    u32 object_8_after_first;
    u32 object_0c_after_first;
    u32 float_bias;
    u32 adjusted_object_0c;
    u32 object_4_after;
    u32 object_10_after;
    u32 second_command;
    u32 second_argument_0;
    u32 second_argument_1;
    u32 second_response;
    u32 object_8_after_second;
    u32 object_14_after_second;
    u32 object_18_after;
    u32 object_19_after;
};

void recovered_geometry_object_alternate_update_plan(
    u32 object_08, u32 object_0c, u32 object_10,
    int16_t object_184, int32_t delta_g6,
    u32 first_response, u32 second_response,
    struct recovered_geometry_object_alternate_plan *plan)
{
    u32 adjusted = object_08 - first_response;

    plan->fifo_address = 0x00884000U;
    plan->first_command = 0x1dU;
    plan->first_argument_0 = (u32)(uint16_t)object_184;
    plan->first_argument_1 = 0x43200000U;
    plan->first_response = first_response;
    plan->object_8_after_first = adjusted;
    plan->object_0c_after_first = adjusted;
    plan->float_bias = 0x40200000U;
    plan->adjusted_object_0c = recovered_float_add_bits(object_0c, plan->float_bias);
    plan->object_4_after = plan->adjusted_object_0c;
    plan->object_10_after = plan->adjusted_object_0c;
    plan->second_command = 0x1eU;
    plan->second_argument_0 = (u32)(uint16_t)object_184;
    plan->second_argument_1 = (u32)delta_g6;
    plan->second_response = second_response;
    plan->object_8_after_second = object_10 + second_response;
    plan->object_14_after_second = plan->object_8_after_second;
    plan->object_18_after = 0U;
    plan->object_19_after = 0U;
}
