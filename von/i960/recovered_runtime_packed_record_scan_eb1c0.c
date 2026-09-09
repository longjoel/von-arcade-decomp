/* Packed-record scan recovered from i960 0xeb1c0-eb2bc. */
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
    recovered_u32 match_548;
    recovered_u32 match_54c;
    recovered_u32 match_550;
    recovered_u32 matched_548;
    recovered_u32 matched_54c;
    recovered_u32 matched_550;
    recovered_u32 match_548_address;
    recovered_u32 match_54c_address;
    recovered_u32 match_550_address;
    recovered_u32 workspace_fill_value;
    recovered_u32 slot_548_address;
    recovered_u32 slot_54c_address;
    recovered_u32 slot_550_address;
    recovered_u32 return_target;
} recovered_runtime_packed_record_scan_result_eb1c0;

int
recovered_runtime_packed_record_scan_eb1c0(
    recovered_u32 packed_byte_count, recovered_u32 target_word,
    const uint16_t *scan_words, recovered_u32 scan_word_capacity,
    recovered_runtime_packed_record_scan_result_eb1c0 *result)
{
    recovered_runtime_packed_record_scan_result_eb1c0 local;
    recovered_u32 i;

    local.packed_byte_count = packed_byte_count;
    local.initialized_halfword_count = packed_byte_count >> 1U;
    local.scan_record_count = packed_byte_count >> 2U;
    local.target_word = target_word & 0xffffU;
    local.target_low_byte = local.target_word & 0xffU;
    local.target_high_byte = local.target_word & 0xff00U;
    local.workspace_base = 0x005785a4U;
    local.scan_base = local.workspace_base +
                      (local.initialized_halfword_count << 1U);
    local.match_548 = 0U;
    local.match_54c = 0U;
    local.match_550 = 0U;
    local.matched_548 = 0U;
    local.matched_54c = 0U;
    local.matched_550 = 0U;
    local.match_548_address = 0U;
    local.match_54c_address = 0U;
    local.match_550_address = 0U;
    local.workspace_fill_value = local.target_word;
    local.slot_548_address = 0x00578548U;
    local.slot_54c_address = 0x0057854cU;
    local.slot_550_address = 0x00578550U;
    local.return_target = 0x000eb2bcU;
    if (result != (recovered_runtime_packed_record_scan_result_eb1c0 *)0)
        *result = local;
    if (scan_words == (const uint16_t *)0 ||
        scan_word_capacity < (local.scan_record_count << 1U))
        return 0;

    for (i = 0U; i < local.scan_record_count; ++i) {
        recovered_u32 first = scan_words[i << 1U];
        recovered_u32 second = scan_words[(i << 1U) + 1U];
        recovered_u32 first_address = local.scan_base + (i << 2U);
        recovered_u32 second_address = first_address + 2U;

        if ((first & 0xffU) == local.target_low_byte) {
            local.matched_548 = 1U;
            local.match_548_address = first_address;
        }
        if ((first & 0xff00U) == local.target_high_byte) {
            local.matched_54c = 1U;
            local.match_54c_address = first_address;
        }
        if ((second & 0xffU) == local.target_low_byte) {
            local.matched_54c = 1U;
            local.match_54c_address = second_address;
        }
        if ((second & 0xff00U) == local.target_high_byte) {
            local.matched_550 = 1U;
            local.match_550_address = second_address;
        }
    }
    local.match_548 = local.matched_548 ? local.match_548_address : 0U;
    local.match_54c = local.matched_54c ? local.match_54c_address : 0U;
    local.match_550 = local.matched_550 ? local.match_550_address : 0U;
    if (result != (recovered_runtime_packed_record_scan_result_eb1c0 *)0)
        *result = local;
    return 1;
}
