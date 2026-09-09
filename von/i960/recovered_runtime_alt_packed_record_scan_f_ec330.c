/* Strided alternate packed-record scan recovered from i960 0xec330-ec3d0. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 packed_byte_count, initialized_halfword_count;
    recovered_u32 group_count, records_per_group, group_stride_bytes;
    recovered_u32 target_byte, scan_base, match_598;
    recovered_u32 slot_598_address, return_target;
} recovered_runtime_alt_packed_record_scan_f_result_ec330;

int
recovered_runtime_alt_packed_record_scan_f_ec330(
    recovered_u32 packed_byte_count, recovered_u32 target_byte,
    const uint16_t *scan_words, recovered_u32 scan_word_capacity,
    recovered_runtime_alt_packed_record_scan_f_result_ec330 *result)
{
    recovered_runtime_alt_packed_record_scan_f_result_ec330 local;
    recovered_u32 group, record;
    local.packed_byte_count = packed_byte_count;
    local.initialized_halfword_count = packed_byte_count >> 1U;
    local.group_count = 32U; local.records_per_group = 128U;
    local.group_stride_bytes = 0x200U;
    local.target_byte = target_byte & 0xffU;
    local.scan_base = 0x005785a4U + packed_byte_count;
    local.match_598 = 0U; local.slot_598_address = 0x00578598U;
    local.return_target = 0x000ec3d0U;
    if (result != (recovered_runtime_alt_packed_record_scan_f_result_ec330 *)0)
        *result = local;
    if (scan_words == (const uint16_t *)0 || scan_word_capacity < 4096U)
        return 0;
    for (group = 0U; group < 32U; ++group)
        for (record = 0U; record < 128U; ++record) {
            recovered_u32 index = group * 128U + record;
            recovered_u32 address = local.scan_base + group * 0x200U + (record << 1U);
            if ((scan_words[index] & 0xffU) == local.target_byte)
                local.match_598 = address;
        }
    if (result != (recovered_runtime_alt_packed_record_scan_f_result_ec330 *)0)
        *result = local;
    return 1;
}
