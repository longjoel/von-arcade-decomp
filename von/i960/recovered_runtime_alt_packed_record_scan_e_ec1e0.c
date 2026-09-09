/* Strided alternate packed-record scan recovered from i960 0xec1e0-ec280. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 packed_byte_count, initialized_halfword_count;
    recovered_u32 group_count, records_per_group, group_stride_bytes;
    recovered_u32 target_byte, scan_base, match_594;
    recovered_u32 slot_594_address, return_target;
} recovered_runtime_alt_packed_record_scan_e_result_ec1e0;

int
recovered_runtime_alt_packed_record_scan_e_ec1e0(
    recovered_u32 packed_byte_count, recovered_u32 target_byte,
    const uint16_t *scan_words, recovered_u32 scan_word_capacity,
    recovered_runtime_alt_packed_record_scan_e_result_ec1e0 *result)
{
    recovered_runtime_alt_packed_record_scan_e_result_ec1e0 local;
    recovered_u32 group, record;
    local.packed_byte_count = packed_byte_count;
    local.initialized_halfword_count = packed_byte_count >> 1U;
    local.group_count = 32U;
    local.records_per_group = 128U;
    local.group_stride_bytes = 0x200U;
    local.target_byte = target_byte & 0xffU;
    local.scan_base = 0x005785a4U + packed_byte_count;
    local.match_594 = 0U;
    local.slot_594_address = 0x00578594U;
    local.return_target = 0x000ec280U;
    if (result != (recovered_runtime_alt_packed_record_scan_e_result_ec1e0 *)0)
        *result = local;
    if (scan_words == (const uint16_t *)0 || scan_word_capacity < 4096U)
        return 0;
    for (group = 0U; group < local.group_count; ++group)
        for (record = 0U; record < local.records_per_group; ++record) {
            recovered_u32 index = group * local.records_per_group + record;
            recovered_u32 address = local.scan_base + group * local.group_stride_bytes +
                                    (record << 1U);
            if ((scan_words[index] & 0xffU) == local.target_byte)
                local.match_594 = address;
        }
    if (result != (recovered_runtime_alt_packed_record_scan_e_result_ec1e0 *)0)
        *result = local;
    return 1;
}
