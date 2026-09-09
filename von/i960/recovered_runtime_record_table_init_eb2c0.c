/* Packed-record workspace initializer recovered from i960 0xeb2c0-eb3a4. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 workspace_base;
    recovered_u32 packed_byte_count;
    recovered_u32 first_target;
    recovered_u32 power_target_first;
    recovered_u32 power_target_last;
    recovered_u32 caller_target;
    recovered_u32 scan_call_count;
    recovered_u32 scan_target[18];
    recovered_u32 match_slot_address[4];
    recovered_u32 normalized_match_value;
    recovered_u32 status_counter_before;
    recovered_u32 status_counter_after;
    recovered_u32 scanner_address;
    recovered_u32 return_target;
} recovered_runtime_record_table_init_result_eb2c0;

recovered_runtime_record_table_init_result_eb2c0
recovered_runtime_record_table_init_eb2c0(
    recovered_u32 caller_target, recovered_u32 status_counter_before)
{
    recovered_runtime_record_table_init_result_eb2c0 result;
    recovered_u32 i;

    result.workspace_base = 0x00200000U;
    result.packed_byte_count = 0x00220000U;
    result.first_target = 0xffffU;
    result.power_target_first = 1U;
    result.power_target_last = 0x8000U;
    result.caller_target = caller_target;
    result.scan_call_count = 18U;
    result.scan_target[0] = 0xffffU;
    for (i = 1U; i <= 16U; ++i)
        result.scan_target[i] = 1U << (i - 1U);
    result.scan_target[17] = caller_target;
    result.match_slot_address[0] = 0x00578548U;
    result.match_slot_address[1] = 0x0057854cU;
    result.match_slot_address[2] = 0x00578550U;
    result.match_slot_address[3] = 0x00578554U;
    result.normalized_match_value = 1U;
    result.status_counter_before = status_counter_before;
    result.status_counter_after = status_counter_before + 1U;
    result.scanner_address = 0x000eb1c0U;
    result.return_target = 0x000eb3a4U;
    return result;
}
