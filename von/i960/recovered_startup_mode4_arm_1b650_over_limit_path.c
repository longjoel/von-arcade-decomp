/* Slot-12 over-limit path recovered from i960 0x1b650-0x1b780. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 helper_31c0_call;
    recovered_u32 helper_31c0_target;
    recovered_u32 selector_address;
    recovered_u32 selector_value;
    recovered_u32 record_index_address;
    recovered_u32 record_index;
    recovered_u32 record_table_base;
    recovered_u32 record_lane_offset;
    recovered_u32 record_increment;
    recovered_u32 record_value_before;
    recovered_u32 record_value_after;
    recovered_u32 record_address;
    recovered_u32 helper_2330_call;
    recovered_u32 helper_2330_target;
    recovered_u32 status_word_address;
    recovered_u32 status_word_value;
    recovered_u32 status_byte_address;
    recovered_u32 status_byte_value;
    recovered_u32 helper_29c08_call;
    recovered_u32 helper_29c08_target;
    recovered_u32 state_address;
    recovered_u32 state_before;
    recovered_u32 state_after;
    recovered_u32 command_address;
    recovered_u32 command_value;
    recovered_u32 row_address;
    recovered_u32 row_before;
    recovered_u32 row_counter_address;
    recovered_u32 row_counter_increment;
    recovered_u32 notify_selector_address;
    recovered_u32 notify_selector_value;
    recovered_u32 notify_argument;
    recovered_u32 helper_184e8_call;
    recovered_u32 helper_184e8_target;
    recovered_u32 continuation_target;
} recovered_startup_mode4_arm_result_1b650_over_limit_path;

int recovered_startup_mode4_arm_1b650_over_limit_path(
    recovered_u32 selector_value, recovered_u32 record_index,
    recovered_u32 record_value,
    recovered_u32 status_word_value,
    recovered_u32 status_byte_value, recovered_u32 state_value,
    recovered_u32 row_value, recovered_u32 notify_selector_value,
    recovered_startup_mode4_arm_result_1b650_over_limit_path *result)
{
    recovered_startup_mode4_arm_result_1b650_over_limit_path r = {0};

    r.helper_31c0_call = 1U;
    r.helper_31c0_target = 0x31c0U;
    r.selector_address = 0x503a7cU;
    r.selector_value = selector_value;
    r.record_index_address = 0x503a9cU;
    r.record_index = record_index;
    r.record_table_base = 0x1d00000U;
    r.record_lane_offset = selector_value != 0U ? 0xacU : 0xb0U;
    r.record_increment = 1U;
    r.record_address = r.record_table_base + (record_index << 4U) +
                       r.record_lane_offset;
    r.record_value_before = record_value;
    r.record_value_after = record_value + r.record_increment;
    r.helper_2330_call = 1U;
    r.helper_2330_target = 0x2330U;
    r.status_word_address = 0x503aa8U;
    r.status_word_value = status_word_value;
    r.status_byte_address = 0x1d00023U;
    r.status_byte_value = status_byte_value;
    r.state_address = 0x503a00U;
    r.state_before = state_value;
    r.command_address = 0x5032f4U;
    r.row_address = 0x503a80U;
    r.row_before = row_value;
    r.row_counter_address = 0x503ac0U;
    r.notify_selector_address = 0x503a08U;
    r.notify_selector_value = notify_selector_value;
    if (status_byte_value == 0U &&
        (selector_value == 0U || status_word_value == 0U)) {
        r.helper_29c08_call = 1U;
        r.helper_29c08_target = 0x29c08U;
        r.command_value = 20U;
        r.state_after = state_value + 1U;
        if (state_value == 0U && row_value == 5U) {
            r.row_counter_increment = 1U;
        }
    } else {
        r.command_value = 19U;
        r.state_after = 15U;
    }
    r.notify_argument = notify_selector_value == 0U ? 0xf0U : 0xf9U;
    r.helper_184e8_call = 1U;
    r.helper_184e8_target = 0x184e8U;
    r.continuation_target = 0x1b950U;
    return result != (void *)0 ? (*result = r, 1) : 1;
}
