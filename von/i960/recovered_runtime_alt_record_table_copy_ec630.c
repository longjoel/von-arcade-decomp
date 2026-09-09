/* Alternate record-table copy recovered from i960 0xec630-ec698. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 source_pointer_address;
    recovered_u32 source_pointer;
    recovered_u32 destination_base;
    recovered_u32 copied_halfword_count;
    recovered_u32 loop_terminal_value;
    recovered_u32 status_counter_before;
    recovered_u32 status_counter_after;
    recovered_u32 status_counter_address;
    recovered_u32 continuation_address;
    recovered_u32 indirect_return_address;
} recovered_runtime_alt_record_table_copy_result_ec630;

recovered_runtime_alt_record_table_copy_result_ec630
recovered_runtime_alt_record_table_copy_ec630(
    recovered_u32 selected_table_pointer, recovered_u32 status_counter_before)
{
    recovered_runtime_alt_record_table_copy_result_ec630 result;
    result.source_pointer_address = 0x005785acU;
    result.source_pointer = selected_table_pointer;
    result.destination_base = 0x01d00000U;
    result.copied_halfword_count = 0x2000U;
    result.loop_terminal_value = 0x1fffU;
    result.status_counter_before = status_counter_before;
    result.status_counter_after = status_counter_before + 1U;
    result.status_counter_address = 0x00578510U;
    result.continuation_address = 0x000ec698U;
    result.indirect_return_address = 0x000ec694U;
    return result;
}
