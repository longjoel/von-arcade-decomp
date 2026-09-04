/* Common object transform update recovered from i960 0x2381c/0x23b3c. */
#include <stdint.h>
#include "recovered_float.h"

typedef uint32_t u32;

struct recovered_geometry_object_transform_plan {
    u32 base_x;
    u32 base_y;
    u32 base_z;
    u32 scaled_x;
    u32 scaled_y;
    u32 scaled_z;
    u32 object_18_after;
};

void recovered_geometry_object_transform_update_plan(
    u32 parent_14, u32 parent_18, u32 parent_1c,
    u32 parent_1c8, u32 parent_150, u32 parent_1cc,
    u32 scale, struct recovered_geometry_object_transform_plan *plan)
{
    float factor = recovered_float_from_bits(scale);
    float factor_squared = factor * factor;

    plan->base_x = parent_14;
    plan->base_y = parent_18;
    plan->base_z = parent_1c;
    plan->scaled_x = recovered_float_to_bits(recovered_float_from_bits(parent_1c8) * factor
                                             + recovered_float_from_bits(parent_14));
    plan->scaled_y = recovered_float_to_bits(recovered_float_from_bits(parent_150) * factor_squared
                                             + recovered_float_from_bits(parent_18));
    plan->scaled_z = recovered_float_to_bits(recovered_float_from_bits(parent_1cc) * factor
                                             + recovered_float_from_bits(parent_1c));
    plan->object_18_after = 1U;
}
