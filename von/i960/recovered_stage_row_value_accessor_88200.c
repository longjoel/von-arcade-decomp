/* Secondary row value accessor recovered from i960 0x88200-0x88240. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_stage_row_value_accessor_88200 {
    int32_t state_value;
    u32 timing_index;
    u32 return_trampoline_load_address;
    u32 return_trampoline_target;
    u32 state_address;
    u32 timing_address;
    u32 table_address;
    u32 table_stride;
    u32 row_offset;
    u32 read_address;
    u32 result_value;
    u32 sentinel_value;
    u32 continuation;
};

struct recovered_stage_row_value_accessor_88200
recovered_stage_row_value_accessor_88200(int32_t state_value,
                                         u32 timing_index,
                                         u32 table_value)
{
    struct recovered_stage_row_value_accessor_88200 out;

    out.state_value = state_value;
    out.timing_index = timing_index;
    out.return_trampoline_load_address = 0x00088200U;
    out.return_trampoline_target = 0x00088240U;
    out.state_address = 0x0051c988U;
    out.timing_address = 0x0051d5e4U;
    out.table_address = 0x005618f0U;
    out.table_stride = 12U;
    out.row_offset = timing_index * out.table_stride;
    out.read_address = out.table_address + out.row_offset;
    out.sentinel_value = 0xffffU;
    out.result_value = state_value > 0 ? table_value & 0xffffU : out.sentinel_value;
    out.continuation = out.return_trampoline_target;
    return out;
}
