/* Paired alternate packed-record scan recovered from i960 0xebd20-ebe1c. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 packed_byte_count;
    recovered_u32 initialized_halfword_count;
    recovered_u32 scan_record_count;
    recovered_u32 target_word;
    recovered_u32 scan_base;
    recovered_u32 match_578;
    recovered_u32 match_57c;
    recovered_u32 match_580;
    recovered_u32 match_584;
    recovered_u32 slot_578_address;
    recovered_u32 slot_57c_address;
    recovered_u32 slot_580_address;
    recovered_u32 slot_584_address;
    recovered_u32 return_target;
} recovered_runtime_alt_packed_record_scan_b_result_ebd20;

int
recovered_runtime_alt_packed_record_scan_b_ebd20(
    recovered_u32 packed_byte_count, recovered_u32 target_word,
    const uint16_t *scan_words, recovered_u32 scan_word_capacity,
    recovered_runtime_alt_packed_record_scan_b_result_ebd20 *result)
{
    recovered_runtime_alt_packed_record_scan_b_result_ebd20 local;
    recovered_u32 i;

    local.packed_byte_count = packed_byte_count;
    local.initialized_halfword_count = packed_byte_count >> 1U;
    local.scan_record_count = packed_byte_count >> 2U;
    local.target_word = target_word & 0xffffU;
    local.scan_base = 0x005785a4U + packed_byte_count;
    local.match_578 = 0U;
    local.match_57c = 0U;
    local.match_580 = 0U;
    local.match_584 = 0U;
    local.slot_578_address = 0x00578578U;
    local.slot_57c_address = 0x0057857cU;
    local.slot_580_address = 0x00578580U;
    local.slot_584_address = 0x00578584U;
    local.return_target = 0x000ebe1cU;
    if (result != (recovered_runtime_alt_packed_record_scan_b_result_ebd20 *)0)
        *result = local;
    if (scan_words == (const uint16_t *)0 ||
        scan_word_capacity < (local.scan_record_count << 1U))
        return 0;
    for (i = 0U; i < local.scan_record_count; ++i) {
        recovered_u32 first_address = local.scan_base + (i << 2U);
        recovered_u32 second_address = first_address + 2U;
        recovered_u32 first = scan_words[i << 1U];
        recovered_u32 second = scan_words[(i << 1U) + 1U];
        if ((first & 0xffU) == (local.target_word & 0xffU))
            local.match_578 = first_address;
        if ((first & 0xff00U) == (local.target_word & 0xff00U))
            local.match_57c = first_address;
        if ((second & 0xffU) == (local.target_word & 0xffU))
            local.match_580 = second_address;
        if ((second & 0xff00U) == (local.target_word & 0xff00U))
            local.match_584 = second_address;
    }
    if (result != (recovered_runtime_alt_packed_record_scan_b_result_ebd20 *)0)
        *result = local;
    return 1;
}
