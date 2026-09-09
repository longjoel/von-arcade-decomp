/* Alternate record-base selector recovered from i960 0xec480-ec624. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 selected_base;
    recovered_u32 selected_family;
    recovered_u32 matched;
    recovered_u32 fallback_counter_before;
    recovered_u32 fallback_counter_after;
    recovered_u32 fallback_counter_address;
    recovered_u32 continuation_address;
    recovered_u32 indirect_return_address;
} recovered_runtime_alt_record_base_select_result_ec480;

recovered_runtime_alt_record_base_select_result_ec480
recovered_runtime_alt_record_base_select_ec480(
    const recovered_u32 markers[15], recovered_u32 fallback_counter)
{
    recovered_runtime_alt_record_base_select_result_ec480 result;
    result.selected_base = 0U;
    result.selected_family = 0U;
    result.matched = 0U;
    result.fallback_counter_before = fallback_counter;
    result.fallback_counter_after = fallback_counter;
    result.fallback_counter_address = 0x00578510U;
    result.continuation_address = 0x000ec5b8U;
    result.indirect_return_address = 0x000ec61cU;
    if (markers == (const recovered_u32 *)0)
        return result;
    if (markers[0] == 1U && markers[1] == 1U && markers[2] == 1U && markers[3] == 1U) {
        result.selected_base = 0x00200000U; result.selected_family = 1U; result.matched = 1U;
    } else if (markers[4] == 1U && markers[5] == 1U) {
        result.selected_base = 0x01000000U; result.selected_family = 2U; result.matched = 1U;
    } else if (markers[6] == 1U && markers[7] == 1U && markers[8] == 1U && markers[9] == 1U) {
        result.selected_base = 0x01080000U; result.selected_family = 3U; result.matched = 1U;
    } else if (markers[10] == 1U && markers[11] == 1U) {
        result.selected_base = 0x01800000U; result.selected_family = 4U; result.matched = 1U;
    } else if (markers[12] == 1U) {
        result.selected_base = 0x01810000U; result.selected_family = 5U; result.matched = 1U;
    } else if (markers[13] == 1U) {
        result.selected_base = 0x01814000U; result.selected_family = 6U; result.matched = 1U;
    } else if (markers[14] == 1U) {
        result.selected_base = 0x01818000U; result.selected_family = 7U; result.matched = 1U;
    }
    if (!result.matched) {
        result.fallback_counter_after = fallback_counter + 1U;
    }
    return result;
}
