/* Second geometry-object variant preamble recovered from i960 0x23980-0x23a14. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_geometry_object_variant_plan {
    u32 fifo_address;
    u32 command;
    u32 argument_0;
    u32 object_parent_delta;
    u32 first_response;
    int32_t object_172;
    int32_t object_172_fixed;
    int32_t response_delta;
    int32_t response_delta_fixed;
    int32_t object_84_minus_504baa;
    u32 transform_path;
    u32 alternate_path;
};

static int32_t sign_extend_16(u32 value)
{
    return (int32_t)(int16_t)(value & 0xffffU);
}

void recovered_geometry_object_variant_plan(
    u32 object_0c, u32 parent_0c, u32 object_7c,
    int16_t object_172, int16_t object_84, int16_t state_504baa,
    int16_t state_504ba8, u32 first_response,
    struct recovered_geometry_object_variant_plan *plan)
{
    int32_t response_delta = (int32_t)first_response - (int32_t)state_504ba8;
    int32_t object_fixed = (int32_t)((int32_t)object_172 << 16);
    int32_t response_fixed = (int32_t)(response_delta << 16);
    int32_t object_delta = (int32_t)object_0c - (int32_t)parent_0c;
    int32_t depth_delta = (int32_t)object_84 - (int32_t)state_504baa;

    plan->fifo_address = 0x00884000U;
    plan->command = 0x0aU;
    plan->argument_0 = object_7c;
    plan->object_parent_delta = (u32)object_delta;
    plan->first_response = first_response;
    plan->object_172 = object_172;
    plan->object_172_fixed = object_fixed;
    plan->response_delta = response_delta;
    plan->response_delta_fixed = response_fixed;
    plan->object_84_minus_504baa = depth_delta;
    plan->transform_path = object_fixed > 0x150000 &&
        object_fixed <= 0x190000 && response_fixed > 0x1b800000 ? 1U : 0U;
    plan->alternate_path = plan->transform_path ? 0U : 1U;
}
