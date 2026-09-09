/* Final paired alternate packed-record scan recovered from i960 0xec6a0-ec75c. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 packed_byte_count, initialized_halfword_count, scan_record_count;
    recovered_u32 target_word, scan_base, match_59c, match_5a0;
    recovered_u32 slot_59c_address, slot_5a0_address, return_target;
} recovered_runtime_alt_packed_record_scan_g_result_ec6a0;

int recovered_runtime_alt_packed_record_scan_g_ec6a0(
    recovered_u32 packed_byte_count, recovered_u32 target_word,
    const uint16_t *scan_words, recovered_u32 scan_word_capacity,
    recovered_runtime_alt_packed_record_scan_g_result_ec6a0 *result)
{
    recovered_runtime_alt_packed_record_scan_g_result_ec6a0 local;
    recovered_u32 i;
    local.packed_byte_count = packed_byte_count;
    local.initialized_halfword_count = packed_byte_count >> 1U;
    local.scan_record_count = packed_byte_count >> 1U;
    local.target_word = target_word & 0xffffU;
    local.scan_base = 0x005785a4U + packed_byte_count;
    local.match_59c = 0U; local.match_5a0 = 0U;
    local.slot_59c_address = 0x0057859cU; local.slot_5a0_address = 0x005785a0U;
    local.return_target = 0x000ec75cU;
    if (result != (recovered_runtime_alt_packed_record_scan_g_result_ec6a0 *)0)
        *result = local;
    if (scan_words == (const uint16_t *)0 || scan_word_capacity < (local.scan_record_count << 1U))
        return 0;
    for (i = 0U; i < local.scan_record_count; ++i) {
        recovered_u32 first = scan_words[i << 1U];
        recovered_u32 second = scan_words[(i << 1U) + 1U];
        recovered_u32 address = local.scan_base + (i << 2U);
        if ((first & 0xffU) == (local.target_word & 0xffU)) local.match_59c = address;
        if ((first & 0xff00U) == (local.target_word & 0xff00U)) local.match_59c = address;
        if ((second & 0xffU) == (local.target_word & 0xffU)) local.match_5a0 = address + 2U;
        if ((second & 0xff00U) == (local.target_word & 0xff00U)) local.match_5a0 = address + 2U;
    }
    if (result != (recovered_runtime_alt_packed_record_scan_g_result_ec6a0 *)0)
        *result = local;
    return 1;
}
