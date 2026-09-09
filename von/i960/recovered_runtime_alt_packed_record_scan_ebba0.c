/* Parallel packed-record scan recovered from i960 0xebba0-ebc5c. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 packed_byte_count;
    recovered_u32 initialized_halfword_count;
    recovered_u32 scan_record_count;
    recovered_u32 target_word;
    recovered_u32 target_low_byte;
    recovered_u32 target_high_byte;
    recovered_u32 workspace_base;
    recovered_u32 scan_base;
    recovered_u32 match_570;
    recovered_u32 match_574;
    recovered_u32 matched_570;
    recovered_u32 matched_574;
    recovered_u32 match_570_address;
    recovered_u32 match_574_address;
    recovered_u32 workspace_fill_value;
    recovered_u32 slot_570_address;
    recovered_u32 slot_574_address;
    recovered_u32 return_target;
} recovered_runtime_alt_packed_record_scan_result_ebba0;

int
recovered_runtime_alt_packed_record_scan_ebba0(
    recovered_u32 packed_byte_count, recovered_u32 target_word,
    const uint16_t *scan_words, recovered_u32 scan_word_capacity,
    recovered_runtime_alt_packed_record_scan_result_ebba0 *result)
{
    recovered_runtime_alt_packed_record_scan_result_ebba0 local;
    recovered_u32 i;

    local.packed_byte_count = packed_byte_count;
    local.initialized_halfword_count = packed_byte_count >> 1U;
    local.scan_record_count = packed_byte_count >> 1U;
    local.target_word = target_word & 0xffffU;
    local.target_low_byte = local.target_word & 0xffU;
    local.target_high_byte = local.target_word & 0xff00U;
    local.workspace_base = 0x005785a4U;
    local.scan_base = local.workspace_base +
                      (local.initialized_halfword_count << 1U);
    local.match_570 = 0U;
    local.match_574 = 0U;
    local.matched_570 = 0U;
    local.matched_574 = 0U;
    local.match_570_address = 0U;
    local.match_574_address = 0U;
    local.workspace_fill_value = local.target_word;
    local.slot_570_address = 0x00578570U;
    local.slot_574_address = 0x00578574U;
    local.return_target = 0x000ebc5cU;
    if (result != (recovered_runtime_alt_packed_record_scan_result_ebba0 *)0)
        *result = local;
    if (scan_words == (const uint16_t *)0 ||
        scan_word_capacity < local.scan_record_count)
        return 0;

    for (i = 0U; i < local.scan_record_count; ++i) {
        recovered_u32 word = scan_words[i];
        recovered_u32 address = local.scan_base + (i << 1U);
        if ((word & 0xffU) == local.target_low_byte) {
            local.matched_570 = 1U;
            local.match_570_address = address;
        }
        if ((word & 0xff00U) == local.target_high_byte) {
            local.matched_574 = 1U;
            local.match_574_address = address;
        }
    }
    local.match_570 = local.matched_570 ? local.match_570_address : 0U;
    local.match_574 = local.matched_574 ? local.match_574_address : 0U;
    if (result != (recovered_runtime_alt_packed_record_scan_result_ebba0 *)0)
        *result = local;
    return 1;
}
