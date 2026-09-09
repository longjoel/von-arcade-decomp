/* Runtime event arm selector recovered from i960 0xe91d0-0xe921c. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 input_counter;
    recovered_u32 remainder;
    recovered_u32 accepted;
    recovered_u32 counter_address;
    recovered_u32 table_address;
    recovered_u32 target;
    recovered_u32 fallback_target;
    recovered_u32 arm[12];
} recovered_geometry_runtime_event_arm_dispatch_result_e91d0;

recovered_geometry_runtime_event_arm_dispatch_result_e91d0
recovered_geometry_runtime_event_arm_dispatch_e91d0(recovered_u32 counter)
{
    recovered_geometry_runtime_event_arm_dispatch_result_e91d0 result;
    static const recovered_u32 targets[12] = {
        0x000e9470U, 0x000e95a4U, 0x000e9da8U, 0x000ea1a0U,
        0x000e9da8U, 0x000ea1a0U, 0x000ea598U, 0x000ea610U,
        0x000e96b8U, 0x000e99fcU, 0x000e9bccU, 0x000e9220U
    };
    unsigned int i;

    result.input_counter = counter;
    result.remainder = counter % 12U;
    result.accepted = result.remainder < 12U;
    result.counter_address = 0x005783fcU;
    result.table_address = 0x000e91f0U;
    result.fallback_target = 0x000ea744U;
    for (i = 0; i < 12U; ++i)
        result.arm[i] = targets[i];
    result.target = result.accepted ? result.arm[result.remainder] : result.fallback_target;
    return result;
}
