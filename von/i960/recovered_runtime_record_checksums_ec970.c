/* Record checksum helpers recovered from i960 0xec970-eca28. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 input_byte_count, chunk_count, checksum;
    recovered_u32 first_byte_offset, second_byte_offset, chunk_stride_bytes;
    recovered_u32 continuation_address, return_target;
} recovered_runtime_record_checksum_result;

static int
checksum_common(const uint8_t *bytes, recovered_u32 byte_count,
                recovered_u32 first_offset, recovered_u32 second_offset,
                recovered_u32 continuation_address,
                recovered_runtime_record_checksum_result *result)
{
    recovered_runtime_record_checksum_result local;
    recovered_u32 i;
    local.input_byte_count = byte_count;
    local.chunk_count = byte_count >> 2U;
    local.checksum = 0U;
    local.first_byte_offset = first_offset;
    local.second_byte_offset = second_offset;
    local.chunk_stride_bytes = 4U;
    local.continuation_address = continuation_address;
    local.return_target = continuation_address;
    if (result != (recovered_runtime_record_checksum_result *)0) *result = local;
    if (bytes == (const uint8_t *)0 || (byte_count & 3U) != 0U) return 0;
    for (i = 0U; i < local.chunk_count; ++i)
        local.checksum += bytes[(i << 2U) + first_offset] +
                          bytes[(i << 2U) + second_offset];
    local.checksum &= 0xffffU;
    if (result != (recovered_runtime_record_checksum_result *)0) *result = local;
    return 1;
}

int recovered_runtime_record_checksum_4stride_ec970(
    const uint8_t *bytes, recovered_u32 byte_count,
    recovered_runtime_record_checksum_result *result)
{ return checksum_common(bytes, byte_count, 0U, 1U, 0x000ec9c0U, result); }

int recovered_runtime_record_checksum_3stride_ec9d0(
    const uint8_t *bytes, recovered_u32 byte_count,
    recovered_runtime_record_checksum_result *result)
{ return checksum_common(bytes, byte_count, 2U, 3U, 0x000eca28U, result); }
