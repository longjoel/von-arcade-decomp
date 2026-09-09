/* Slot-12 clear-ready path recovered from i960 0x1b818-0x1b8a8. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 ready_required, ready_value;
    recovered_u32 initial_state_address, initial_state;
    recovered_u32 record_index_address, record_index;
    recovered_u32 record_table_base, record_table_offset;
    recovered_u32 record_table_entry_address, record_table_entry_before;
    recovered_u32 record_table_entry_after;
    recovered_u32 record_counter_address, record_counter_before, record_counter_after;
    recovered_u32 row_address, row_before, row_after;
    recovered_u32 incoming_value, row_overwritten;
    recovered_u32 row_limit, below_row_limit;
    recovered_u32 state_address, state_value;
    recovered_u32 command_address, command_value;
    recovered_u32 helper_call, helper_target;
    recovered_u32 phase_continuation;
} recovered_startup_mode4_arm_result_1b818_clear_ready_path;

int recovered_startup_mode4_arm_1b818_clear_ready_path(
    recovered_u32 ready_value, recovered_u32 record_index,
    recovered_u32 record_table_entry, recovered_u32 record_counter,
    recovered_u32 row_value, recovered_u32 incoming_value,
    recovered_startup_mode4_arm_result_1b818_clear_ready_path *result)
{
    recovered_startup_mode4_arm_result_1b818_clear_ready_path r = {0};

    r.ready_required = 0U;
    r.ready_value = ready_value;
    r.initial_state_address = 0x503a00U;
    r.initial_state = 7U;
    r.record_index_address = 0x503a98U;
    r.record_index = record_index;
    r.record_table_base = 0x1d00000U;
    r.record_table_offset = 0xacU;
    r.record_table_entry_address = r.record_table_base +
                                   (record_index << 4U) + r.record_table_offset;
    r.record_table_entry_before = record_table_entry;
    r.record_table_entry_after = record_table_entry + 1U;
    r.record_counter_address = 0x503a64U;
    r.record_counter_before = record_counter;
    r.record_counter_after = record_counter + 1U;
    r.row_address = 0x503a80U;
    r.row_before = row_value;
    r.row_after = row_value + 1U;
    r.incoming_value = incoming_value;
    r.row_limit = 9U;
    r.below_row_limit = (int32_t)r.row_after < (int32_t)r.row_limit ? 1U : 0U;
    r.row_overwritten = r.below_row_limit != 0U ? 1U : 0U;
    r.state_address = 0x503a00U;
    r.command_address = 0x5032f4U;
    if (r.below_row_limit != 0U) {
        r.row_after = incoming_value;
        r.helper_call = 0x31c0U;
        r.helper_target = 0x1b888U;
        r.command_value = 19U;
        r.state_value = 17U;
        r.phase_continuation = 0x1b940U;
    } else {
        r.state_value = 7U;
        r.phase_continuation = 0x1b8a8U;
    }
    return result != (void *)0 ? (*result = r, 1) : 1;
}
