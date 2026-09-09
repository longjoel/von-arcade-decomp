/* Secondary row publication body recovered from i960 0x88030-0x880b8. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_stage_secondary_row_publication_88030 {
    u32 counter_value;
    u32 destination_first;
    u32 destination_second;
    u32 first_row_word;
    u32 second_row_word;
    u32 modulo_divisor;
    u32 counter_remainder;
    u32 row_offset;
    u32 first_row_address;
    u32 second_row_address;
    u32 counter_low_bits;
    u32 asset_upload_admitted;
    u32 asset_index;
    u32 asset_offset;
    u32 asset_source_first;
    u32 asset_source_second;
    u32 asset_destination_first;
    u32 asset_destination_second;
    u32 asset_bytes;
    u32 asset_upload_call;
    u32 continuation;
};

struct recovered_stage_secondary_row_publication_88030
recovered_stage_secondary_row_publication_88030(u32 counter_value,
                                                u32 destination_first,
                                                u32 destination_second,
                                                u32 first_row_word,
                                                u32 second_row_word)
{
    struct recovered_stage_secondary_row_publication_88030 out;

    out.counter_value = counter_value;
    out.destination_first = destination_first;
    out.destination_second = destination_second;
    out.first_row_word = first_row_word & 0xffffU;
    out.second_row_word = second_row_word & 0xffffU;
    out.modulo_divisor = 120U;
    out.counter_remainder = counter_value % out.modulo_divisor;
    out.row_offset = out.counter_remainder * 12U;
    out.first_row_address = 0x005618f0U + out.row_offset;
    out.second_row_address = 0x00561e90U + out.row_offset;
    out.counter_low_bits = counter_value & 3U;
    out.asset_upload_admitted = out.counter_low_bits == 0U ? 0U : 1U;
    out.asset_index = (9U * out.counter_remainder) % 90U;
    out.asset_offset = out.asset_index << 10U;
    out.asset_source_first = 0x00533df0U + out.asset_offset;
    out.asset_source_second = 0x0054a5f0U + out.asset_offset;
    out.asset_destination_first = destination_first + 0x200U;
    out.asset_destination_second = destination_second + 0x200U;
    out.asset_bytes = 0x400U;
    out.asset_upload_call = 0x000f5d40U;
    out.continuation = 0x000880c0U;
    return out;
}
