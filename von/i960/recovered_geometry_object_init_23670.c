/* Geometry-object initializer prefix recovered from i960 0x23670-0x237a8. */
#include <stdint.h>
#include "recovered_float.h"

typedef uint32_t u32;

struct recovered_geometry_object_init_plan {
    u32 fifo_address;
    u32 first_command;
    u32 first_argument_0;
    u32 first_argument_1;
    u32 second_command;
    u32 second_argument_0;
    u32 second_argument_1;
    u32 second_response;
    u32 object_8_after;
    u32 object_94_after;
    u32 float_bias;
    u32 object_0c_plus_bias;
    u32 third_command;
    u32 third_argument_0;
    u32 third_argument_1;
    u32 third_response;
    u32 object_90_after;
    u32 object_9c_after;
    u32 object_a0_after;
    u32 object_a1_after;
};

void recovered_geometry_object_init_plan(
    u32 object_0c, u32 object_08, u32 object_10,
    int16_t object_84, int16_t object_184,
    int32_t parent_0c, int16_t second_response_16,
    u32 third_response, struct recovered_geometry_object_init_plan *plan)
{
    int32_t delta = (int32_t)object_0c - (int32_t)parent_0c;
    int32_t depth_delta = (int32_t)object_84 - (int32_t)object_184;
    u32 adjusted = object_08 - (u32)second_response_16;

    plan->fifo_address = 0x00884000U;
    plan->first_command = 0x0aU;
    plan->first_argument_0 = object_0c;
    plan->first_argument_1 = (u32)delta;
    plan->second_command = 0x1dU;
    plan->second_argument_0 = (u32)(uint16_t)object_184;
    plan->second_argument_1 = 0x43200000U;
    plan->second_response = (u32)second_response_16;
    plan->object_8_after = adjusted;
    plan->object_94_after = adjusted;
    plan->float_bias = 0x40200000U;
    plan->object_0c_plus_bias = recovered_float_add_bits(object_0c, plan->float_bias);
    plan->third_command = 0x1eU;
    plan->third_argument_0 = (u32)(uint16_t)object_184;
    plan->third_argument_1 = (u32)depth_delta;
    plan->third_response = third_response;
    plan->object_90_after = object_10 + third_response;
    plan->object_9c_after = plan->object_90_after;
    plan->object_a0_after = 0U;
    plan->object_a1_after = 0U;
}
