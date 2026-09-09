/* Shared slot-20 response tail recovered from i960 0x878f8-0x87a00. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 status_a_address, status_a_value, status_a_mode_write;
    recovered_u32 status_b_address, status_b_value, status_b_mode_write;
    recovered_u32 mode_address, mode_value, mode_write_count;
    recovered_u32 timing_address, timing_before, timing_incremented, timing_after;
    recovered_u32 timing_limit;
    recovered_u32 timing_table_index, timing_table_shifted, timing_table_scaled;
    recovered_u32 first_source, first_destination, first_bytes;
    recovered_u32 second_source, second_destination, second_bytes;
    recovered_u32 upload_call, upload_count;
    recovered_u32 post_upload_call;
    recovered_u32 marker_address, marker_value;
    recovered_u32 seed_value;
    recovered_u32 seed_addresses[6];
    recovered_u32 terminal_state_address, terminal_state_value;
    recovered_u32 return_target;
} recovered_startup_mode4_arm_result_878f8_shared_tail;

int recovered_startup_mode4_arm_878f8_shared_tail(
    recovered_u32 status_a_value, recovered_u32 status_b_value,
    recovered_u32 timing_value, recovered_u32 timing_table_index,
    recovered_u32 seed_value, recovered_u32 state_value,
    recovered_startup_mode4_arm_result_878f8_shared_tail *result)
{
    recovered_startup_mode4_arm_result_878f8_shared_tail r = {0};
    recovered_u32 table_offset = ((timing_table_index >> 2U) * 3U) << 9U;

    r.status_a_address = 0x503b34U;
    r.status_a_value = status_a_value;
    r.status_a_mode_write = status_a_value < 7U ? 1U : 0U;
    r.status_b_address = 0x504134U;
    r.status_b_value = status_b_value;
    r.status_b_mode_write = status_b_value < 7U ? 1U : 0U;
    r.mode_address = 0x51c97cU;
    r.mode_value = 1U;
    r.mode_write_count = r.status_a_mode_write + r.status_b_mode_write;
    r.timing_address = 0x51d5e4U;
    r.timing_before = timing_value;
    r.timing_incremented = timing_value + 1U;
    r.timing_limit = 0x77U;
    r.timing_after = r.timing_incremented <= r.timing_limit ? r.timing_incremented : seed_value;
    r.timing_table_index = timing_table_index;
    r.timing_table_shifted = timing_table_index >> 2U;
    r.timing_table_scaled = table_offset;
    r.first_source = 0x51d5f0U + table_offset;
    r.first_destination = 0x503ad0U;
    r.first_bytes = 0x600U;
    r.second_source = 0x5289f0U + table_offset;
    r.second_destination = 0x5040d0U;
    r.second_bytes = 0x600U;
    r.upload_call = 0xf5d40U;
    r.upload_count = 2U;
    r.post_upload_call = 0x88380U;
    r.marker_address = 0x503a60U;
    r.marker_value = 1U;
    r.seed_value = seed_value;
    r.seed_addresses[0] = 0x51c988U;
    r.seed_addresses[1] = 0x51c99cU;
    r.seed_addresses[2] = 0x51d5e0U;
    r.seed_addresses[3] = 0x51c9c0U;
    r.seed_addresses[4] = 0x51c9b4U;
    r.seed_addresses[5] = 0x51c9bcU;
    r.terminal_state_address = 0x503a00U;
    r.terminal_state_value = state_value + 1U;
    r.return_target = 0x87a00U;
    return result != (void *)0 ? (*result = r, 1) : 1;
}
