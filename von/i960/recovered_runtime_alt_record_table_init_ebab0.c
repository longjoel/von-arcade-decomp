/* Second alternate packed-record initializer recovered from i960 0xebab0-ebb98. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 workspace_base;
    recovered_u32 packed_byte_count;
    recovered_u32 first_target;
    recovered_u32 shifted_target_first;
    recovered_u32 shifted_target_last;
    recovered_u32 caller_target;
    recovered_u32 scan_call_count;
    recovered_u32 scan_target[18];
    recovered_u32 match_slot_address[4];
    recovered_u32 normalized_match_value;
    recovered_u32 scanner_address;
    recovered_u32 status_counter_before;
    recovered_u32 status_counter_after;
    recovered_u32 status_counter_address;
    recovered_u32 return_target;
} recovered_runtime_alt_record_table_init_result_ebab0;

recovered_runtime_alt_record_table_init_result_ebab0
recovered_runtime_alt_record_table_init_ebab0(
    recovered_u32 caller_target, recovered_u32 status_counter_before)
{
    recovered_runtime_alt_record_table_init_result_ebab0 result;
    recovered_u32 i;

    result.workspace_base = 0x00900004U;
    result.packed_byte_count = 0x0000fffcU;
    result.first_target = 0xffffffffU;
    result.shifted_target_first = 0x01010101U;
    result.shifted_target_last = 0x80808080U;
    result.caller_target = caller_target;
    result.scan_call_count = 18U;
    result.scan_target[0] = 0xffffffffU;
    for (i = 1U; i <= 16U; ++i)
        result.scan_target[i] = 0x01010101U << (i - 1U);
    result.scan_target[17] = caller_target;
    result.match_slot_address[0] = 0x00578560U;
    result.match_slot_address[1] = 0x00578564U;
    result.match_slot_address[2] = 0x00578568U;
    result.match_slot_address[3] = 0x0057856cU;
    result.normalized_match_value = 1U;
    result.scanner_address = 0x000eb8a0U;
    result.status_counter_before = status_counter_before;
    result.status_counter_after = status_counter_before + 1U;
    result.status_counter_address = 0x00578510U;
    result.return_target = 0x000ebb98U;
    return result;
}
