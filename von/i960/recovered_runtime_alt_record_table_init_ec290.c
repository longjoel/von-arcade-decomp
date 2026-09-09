/* Strided alternate packed-record initializer recovered from i960 0xec290-ec32c. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 workspace_base, packed_byte_count, first_target;
    recovered_u32 shifted_target_first, shifted_target_last, caller_target;
    recovered_u32 scan_call_count, scan_target[18], scanner_address;
    recovered_u32 match_slot_address, normalized_match_value;
    recovered_u32 status_counter_before, status_counter_after;
    recovered_u32 status_counter_address, return_target;
} recovered_runtime_alt_record_table_init_result_ec290;

recovered_runtime_alt_record_table_init_result_ec290
recovered_runtime_alt_record_table_init_ec290(
    recovered_u32 caller_target, recovered_u32 status_counter_before)
{
    recovered_runtime_alt_record_table_init_result_ec290 result;
    recovered_u32 i;
    result.workspace_base = 0x01814000U;
    result.packed_byte_count = 0x00004000U;
    result.first_target = 0xffffU;
    result.shifted_target_first = 1U;
    result.shifted_target_last = 0x8000U;
    result.caller_target = caller_target;
    result.scan_call_count = 18U;
    result.scan_target[0] = 0xffffU;
    for (i = 1U; i <= 16U; ++i)
        result.scan_target[i] = 1U << (i - 1U);
    result.scan_target[17] = caller_target;
    result.scanner_address = 0x000ec1e0U;
    result.match_slot_address = 0x00578594U;
    result.normalized_match_value = 1U;
    result.status_counter_before = status_counter_before;
    result.status_counter_after = status_counter_before + 1U;
    result.status_counter_address = 0x00578510U;
    result.return_target = 0x000ec32cU;
    return result;
}
