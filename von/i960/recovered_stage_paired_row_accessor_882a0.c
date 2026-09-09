/* Secondary paired-row accessor recovered from i960 0x882a0-0x88304. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_stage_paired_row_accessor_882a0 {
    int32_t state_value;
    u32 timing_index;
    u32 return_trampoline_load_address;
    u32 return_trampoline_target;
    u32 state_address;
    u32 timing_address;
    u32 table_address;
    u32 table_stride;
    u32 row_offset;
    u32 first_read_address;
    u32 second_read_address;
    u32 first_result;
    u32 second_result;
    u32 continuation;
};

struct recovered_stage_paired_row_accessor_882a0
recovered_stage_paired_row_accessor_882a0(int32_t state_value,
                                          u32 timing_index,
                                          u32 first_table_value,
                                          u32 second_table_value)
{
    struct recovered_stage_paired_row_accessor_882a0 out;

    out.state_value = state_value;
    out.timing_index = timing_index;
    out.return_trampoline_load_address = 0x000882a0U;
    out.return_trampoline_target = 0x00088304U;
    out.state_address = 0x0051c988U;
    out.timing_address = 0x0051d5e4U;
    out.table_address = 0x005618f0U;
    out.table_stride = 12U;
    out.row_offset = timing_index * out.table_stride;
    out.first_read_address = out.table_address + out.row_offset + 4U;
    out.second_read_address = out.table_address + out.row_offset + 8U;
    out.first_result = state_value > 0 ? first_table_value : 0U;
    out.second_result = state_value > 0 ? second_table_value : 0U;
    out.continuation = out.return_trampoline_target;
    return out;
}
