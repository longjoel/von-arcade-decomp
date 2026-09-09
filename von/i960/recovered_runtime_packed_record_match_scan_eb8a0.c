/* Post-bank packed-record match scan recovered from i960 0xeb8a0-eb9a4. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 packed_byte_count;
    recovered_u32 initialized_dword_count;
    recovered_u32 scan_record_count;
    recovered_u32 target_word;
    recovered_u32 workspace_base;
    recovered_u32 scan_base;
    recovered_u32 byte_mask[4];
    recovered_u32 match_address[4];
    recovered_u32 matched[4];
    recovered_u32 slot_address[4];
    recovered_u32 workspace_fill_value;
    recovered_u32 return_target;
} recovered_runtime_packed_record_match_scan_result_eb8a0;

int
recovered_runtime_packed_record_match_scan_eb8a0(
    recovered_u32 packed_byte_count, recovered_u32 target_word,
    const recovered_u32 *scan_words, recovered_u32 scan_word_capacity,
    recovered_runtime_packed_record_match_scan_result_eb8a0 *result)
{
    recovered_runtime_packed_record_match_scan_result_eb8a0 local;
    recovered_u32 i;

    local.packed_byte_count = packed_byte_count;
    local.initialized_dword_count = packed_byte_count >> 2U;
    local.scan_record_count = packed_byte_count >> 2U;
    local.target_word = target_word;
    local.workspace_base = 0x005785b0U;
    local.scan_base = local.workspace_base + (local.initialized_dword_count << 2U);
    local.byte_mask[0] = 0x000000ffU;
    local.byte_mask[1] = 0x0000ff00U;
    local.byte_mask[2] = 0x00ff0000U;
    local.byte_mask[3] = 0xff000000U;
    for (i = 0U; i < 4U; ++i) {
        local.match_address[i] = 0U;
        local.matched[i] = 0U;
        local.slot_address[i] = 0x00578560U + (i << 2U);
    }
    local.workspace_fill_value = target_word;
    local.return_target = 0x000eb9a4U;
    if (result != (recovered_runtime_packed_record_match_scan_result_eb8a0 *)0)
        *result = local;
    if (scan_words == (const recovered_u32 *)0 ||
        scan_word_capacity < local.scan_record_count)
        return 0;

    for (i = 0U; i < local.scan_record_count; ++i) {
        recovered_u32 word = scan_words[i];
        recovered_u32 address = local.scan_base + (i << 2U);
        for (recovered_u32 byte = 0U; byte < 4U; ++byte) {
            recovered_u32 mask = local.byte_mask[byte];
            if ((word & mask) == (target_word & mask)) {
                local.matched[byte] = 1U;
                local.match_address[byte] = address;
            }
        }
    }
    if (result != (recovered_runtime_packed_record_match_scan_result_eb8a0 *)0)
        *result = local;
    return 1;
}
