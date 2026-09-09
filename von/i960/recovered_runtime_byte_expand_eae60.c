/* Byte-expansion helper recovered from i960 0xeae60-eaea4. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 encoded_count;
    recovered_u32 source_count;
    recovered_u32 output_count;
    recovered_u32 source_advance;
    recovered_u32 destination_advance;
    recovered_u32 continuation_target;
} recovered_runtime_byte_expand_result_eae60;

int
recovered_runtime_byte_expand_eae60(const uint8_t *source, uint8_t *destination,
                                    recovered_u32 encoded_count,
                                    recovered_u32 destination_capacity,
                                    recovered_u32 continuation_target,
                                    recovered_runtime_byte_expand_result_eae60 *result)
{
    recovered_runtime_byte_expand_result_eae60 local;
    recovered_u32 i;

    local.encoded_count = encoded_count;
    local.source_count = encoded_count >> 1U;
    local.output_count = local.source_count << 1U;
    local.source_advance = local.source_count;
    local.destination_advance = local.output_count;
    local.continuation_target = continuation_target;
    if (result != (recovered_runtime_byte_expand_result_eae60 *)0)
        *result = local;
    if (source == (const uint8_t *)0 || destination == (uint8_t *)0 ||
        destination_capacity < local.output_count)
        return 0;
    for (i = 0U; i < local.source_count; ++i) {
        destination[i << 1U] = source[i];
        destination[(i << 1U) + 1U] = 0U;
    }
    return 1;
}
