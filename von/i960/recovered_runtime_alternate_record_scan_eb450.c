/* Alternate packed-record scan recovered from i960 0xeb450-eb508. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 packed_byte_count;
    recovered_u32 initialized_halfword_count;
    recovered_u32 scan_record_count;
    recovered_u32 target_word;
    recovered_u32 workspace_base;
    recovered_u32 scan_base;
    recovered_u32 mismatch_558;
    recovered_u32 mismatch_55c;
    recovered_u32 mismatch_558_address;
    recovered_u32 mismatch_55c_address;
    recovered_u32 workspace_fill_value;
    recovered_u32 slot_558_address;
    recovered_u32 slot_55c_address;
    recovered_u32 return_target;
} recovered_runtime_alternate_record_scan_result_eb450;

int
recovered_runtime_alternate_record_scan_eb450(
    recovered_u32 packed_byte_count, recovered_u32 target_word,
    const uint16_t *scan_words, recovered_u32 scan_word_capacity,
    recovered_runtime_alternate_record_scan_result_eb450 *result)
{
    recovered_runtime_alternate_record_scan_result_eb450 local;
    recovered_u32 i;

    local.packed_byte_count = packed_byte_count;
    local.initialized_halfword_count = packed_byte_count >> 1U;
    local.scan_record_count = packed_byte_count >> 2U;
    local.target_word = target_word & 0xffffU;
    local.workspace_base = 0x00501cc0U;
    local.scan_base = local.workspace_base +
                      (local.initialized_halfword_count << 1U);
    local.mismatch_558 = 0U;
    local.mismatch_55c = 0U;
    local.mismatch_558_address = 0U;
    local.mismatch_55c_address = 0U;
    local.workspace_fill_value = local.target_word;
    local.slot_558_address = 0x00578558U;
    local.slot_55c_address = 0x0057855cU;
    local.return_target = 0x000eb508U;
    if (result != (recovered_runtime_alternate_record_scan_result_eb450 *)0)
        *result = local;
    if (scan_words == (const uint16_t *)0 ||
        scan_word_capacity < (local.scan_record_count << 1U))
        return 0;

    for (i = 0U; i < local.scan_record_count; ++i) {
        recovered_u32 first_address = local.scan_base + (i << 2U);
        recovered_u32 second_address = first_address + 2U;

        if ((scan_words[i << 1U] & 0xffffU) != local.target_word) {
            local.mismatch_558 = 1U;
            local.mismatch_558_address = first_address + 2U;
        }
        if ((scan_words[(i << 1U) + 1U] & 0xffffU) != local.target_word) {
            local.mismatch_55c = 1U;
            local.mismatch_55c_address = second_address + 2U;
        }
    }
    local.mismatch_558 = local.mismatch_558 ? local.mismatch_558_address : 0U;
    local.mismatch_55c = local.mismatch_55c ? local.mismatch_55c_address : 0U;
    if (result != (recovered_runtime_alternate_record_scan_result_eb450 *)0)
        *result = local;
    return 1;
}
