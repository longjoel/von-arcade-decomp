/* Strided alternate packed-record initializer recovered from i960 0xec3e0-ec47c. */
#include "recovered_common.h"
typedef struct { recovered_u32 workspace_base, packed_byte_count, first_target, shifted_target_first, shifted_target_last, caller_target, scan_call_count, scan_target[18], scanner_address, match_slot_address, normalized_match_value, status_counter_before, status_counter_after, status_counter_address, return_target; } recovered_runtime_alt_record_table_init_result_ec3e0;
recovered_runtime_alt_record_table_init_result_ec3e0 recovered_runtime_alt_record_table_init_ec3e0(recovered_u32 caller_target, recovered_u32 status_counter_before) {
    recovered_runtime_alt_record_table_init_result_ec3e0 result; recovered_u32 i;
    result.workspace_base=0x01818000U; result.packed_byte_count=0x4000U; result.first_target=0xffffU; result.shifted_target_first=1U; result.shifted_target_last=0x8000U; result.caller_target=caller_target; result.scan_call_count=18U; result.scan_target[0]=0xffffU;
    for (i = 1U; i <= 16U; ++i)
        result.scan_target[i] = 1U << (i - 1U);
    result.scan_target[17] = caller_target;
    result.scanner_address = 0xec330U;
    result.match_slot_address = 0x578598U;
    result.normalized_match_value = 1U;
    result.status_counter_before = status_counter_before;
    result.status_counter_after = status_counter_before + 1U;
    result.status_counter_address = 0x578510U;
    result.return_target = 0xec47cU;
    return result;
}
