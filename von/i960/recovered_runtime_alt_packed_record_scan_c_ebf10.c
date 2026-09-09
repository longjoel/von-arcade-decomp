/* Third alternate packed-record scan recovered from i960 0xebf10-ebfcc. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 packed_byte_count, initialized_halfword_count, scan_record_count;
    recovered_u32 target_word, scan_base, match_588, match_58c;
    recovered_u32 slot_588_address, slot_58c_address, return_target;
} recovered_runtime_alt_packed_record_scan_c_result_ebf10;

int
recovered_runtime_alt_packed_record_scan_c_ebf10(
    recovered_u32 packed_byte_count, recovered_u32 target_word,
    const uint16_t *scan_words, recovered_u32 scan_word_capacity,
    recovered_runtime_alt_packed_record_scan_c_result_ebf10 *result)
{
    recovered_runtime_alt_packed_record_scan_c_result_ebf10 local;
    recovered_u32 i;

    local.packed_byte_count = packed_byte_count;
    local.initialized_halfword_count = packed_byte_count >> 1U;
    local.scan_record_count = packed_byte_count >> 1U;
    local.target_word = target_word & 0xffffU;
    local.scan_base = 0x005785a4U + packed_byte_count;
    local.match_588 = 0U;
    local.match_58c = 0U;
    local.slot_588_address = 0x00578588U;
    local.slot_58c_address = 0x0057858cU;
    local.return_target = 0x000ebfccU;
    if (result != (recovered_runtime_alt_packed_record_scan_c_result_ebf10 *)0)
        *result = local;
    if (scan_words == (const uint16_t *)0 ||
        scan_word_capacity < local.scan_record_count)
        return 0;
    for (i = 0U; i < local.scan_record_count; ++i) {
        recovered_u32 word = scan_words[i];
        recovered_u32 address = local.scan_base + (i << 1U);
        if ((word & 0xffU) == (local.target_word & 0xffU))
            local.match_588 = address;
        if ((word & 0xff00U) == (local.target_word & 0xff00U))
            local.match_58c = address;
    }
    if (result != (recovered_runtime_alt_packed_record_scan_c_result_ebf10 *)0)
        *result = local;
    return 1;
}
