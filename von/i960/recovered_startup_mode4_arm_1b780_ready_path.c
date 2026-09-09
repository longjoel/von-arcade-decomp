/* Slot-12 ready path recovered from i960 0x1b780-0x1b814. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 ready_required, ready_value;
    recovered_u32 record_index_address, record_index;
    recovered_u32 record_table_base, record_table_offset;
    recovered_u32 record_table_entry_address, record_table_entry_before;
    recovered_u32 record_table_entry_after;
    recovered_u32 record_counter_address, record_counter_before, record_counter_after;
    recovered_u32 record_value_address, record_value;
    recovered_u32 status_address, status_value, status_zero;
    recovered_u32 register_19_value;
    recovered_u32 state_address, state_value;
    recovered_u32 command_address, command_value;
    recovered_u32 record_update_call, message_continuation;
} recovered_startup_mode4_arm_result_1b780_ready_path;

int recovered_startup_mode4_arm_1b780_ready_path(
    recovered_u32 ready_value, recovered_u32 record_index,
    recovered_u32 record_table_entry, recovered_u32 record_counter,
    recovered_u32 record_value, recovered_u32 status_value,
    recovered_u32 register_19_value,
    recovered_startup_mode4_arm_result_1b780_ready_path *result)
{
    recovered_startup_mode4_arm_result_1b780_ready_path r = {0};

    r.ready_required = 1U;
    r.ready_value = ready_value;
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
    r.record_value_address = 0x503a84U;
    r.record_value = record_value;
    r.status_address = 0x503aa8U;
    r.status_value = status_value;
    r.status_zero = status_value == 0U ? 1U : 0U;
    r.register_19_value = register_19_value;
    r.state_address = 0x503a00U;
    r.command_address = 0x5032f4U;
    if (r.status_zero != 0U) {
        r.state_value = 15U;
        r.command_value = 19U;
    } else {
        r.state_value = 5U;
        /* stos at 0x5032f4 stores only the low halfword. */
        r.command_value = (register_19_value + 31U) & 0xffffU;
    }
    r.record_update_call = 0x2330U;
    r.message_continuation = 0x1b950U;
    return result != (void *)0 ? (*result = r, 1) : 1;
}
