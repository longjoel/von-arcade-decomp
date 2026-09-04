/* Pure command stream for the geometry function submitter at 0x28e88. */
#include "recovered_common.h"

recovered_u32 recovered_geometry_function_plan_28e88(
    const recovered_u32 *source, recovered_u32 command, recovered_u32 count,
    recovered_u32 *output, recovered_u32 capacity)
{
    recovered_u32 index = 0;
    if (index < capacity) output[index] = 0x00000404U;
    ++index;
    if (index < capacity) output[index] = (command & 0xffffU) | 0x00800000U;
    ++index;
    if (index < capacity) output[index] = count;
    ++index;
    for (recovered_u32 i = 0; i < count; ++i) {
        if (index < capacity) output[index] = source[i] & 0xffffU;
        ++index;
    }
    if (index < capacity) output[index] = 0x00001010U;
    ++index;
    if (index < capacity) output[index] = 0U;
    ++index;
    return index;
}
