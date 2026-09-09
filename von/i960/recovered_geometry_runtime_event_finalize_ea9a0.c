/* Runtime event terminal finalizer recovered from i960 0xea9a0-0xeaa50. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 state_3e4;
    recovered_u32 state_3e8;
    recovered_u32 state_3f0;
    recovered_u32 state_3f4;
    recovered_u32 state_3f8;
    recovered_u32 fifo_word[4];
    recovered_u32 fifo_count;
    recovered_u32 snapshot_504b98;
    recovered_u32 snapshot_504b9c;
    recovered_u32 snapshot_504ba0;
    recovered_u32 snapshot_504ba8;
    recovered_u32 snapshot_504baa;
    recovered_u32 derived_504d28;
    recovered_u32 derived_5770f4;
    recovered_u32 fifo_address;
    recovered_u32 snapshot_base;
    recovered_u32 derived_504d28_address;
    recovered_u32 derived_5770f4_address;
    recovered_u32 opcode;
    recovered_u32 return_target;
} recovered_geometry_runtime_event_finalize_result_ea9a0;

recovered_geometry_runtime_event_finalize_result_ea9a0
recovered_geometry_runtime_event_finalize_ea9a0(
    recovered_u32 state_3e4, recovered_u32 state_3e8,
    recovered_u32 state_3f0, recovered_u32 state_3f4,
    recovered_u32 state_3f8)
{
    recovered_geometry_runtime_event_finalize_result_ea9a0 result;
    recovered_u32 toggled_3f0 = state_3f0 ^ 0x80000000U;
    recovered_u32 toggled_3f4 = state_3f4 ^ 0x80000000U;
    recovered_u32 toggled_3f8 = state_3f8 ^ 0x80000000U;

    result.state_3e4 = state_3e4;
    result.state_3e8 = state_3e8;
    result.state_3f0 = state_3f0;
    result.state_3f4 = state_3f4;
    result.state_3f8 = state_3f8;
    result.fifo_word[0] = 18U;
    result.fifo_word[1] = toggled_3f4;
    result.fifo_word[2] = toggled_3f0;
    result.fifo_word[3] = toggled_3f8;
    result.fifo_count = 4U;
    result.snapshot_504b98 = state_3f4;
    result.snapshot_504b9c = state_3f0;
    result.snapshot_504ba0 = state_3f8;
    result.snapshot_504ba8 = state_3e8 & 0xffffU;
    result.snapshot_504baa = state_3e4 & 0xffffU;
    result.derived_504d28 = (state_3e4 & 0x1fffU) >> 4;
    result.derived_5770f4 = (toggled_3f4 >> 13) & 7U;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.snapshot_base = 0x00504b98U;
    result.derived_504d28_address = 0x00504d28U;
    result.derived_5770f4_address = 0x005770f4U;
    result.opcode = 18U;
    result.return_target = 0x000eaa50U;
    return result;
}
