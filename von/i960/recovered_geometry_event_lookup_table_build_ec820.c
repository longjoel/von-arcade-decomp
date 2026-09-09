/* Geometry-event literal expansion recovered from i960 0xec820-ec8e4. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 literal_source_address;
    recovered_u32 source_words[3];
    recovered_u32 seed_table_address;
    recovered_u32 seed_word;
    recovered_u32 seed_word_count;
    recovered_u32 destination_table_address;
    recovered_u32 destination_stride_bytes;
    recovered_u32 source_record_count;
    recovered_u32 column_count;
    recovered_u32 slot_count;
    uint16_t table[3][32][8];
    recovered_u32 next_target;
} recovered_geometry_event_lookup_table_build_result_ec820;

static recovered_u32
recovered_geometry_event_lookup_table_address_unchecked_ec820(recovered_u32 row,
                                                               recovered_u32 column,
                                                               recovered_u32 slot)
{
    recovered_u32 group = (row << 2U) + (column >> 3U);
    recovered_u32 scaled = (group << 7U) + 0x2000U;
    recovered_u32 halfword_offset = scaled >> 2U;

    return 0x01800010U + halfword_offset + (slot << 1U);
}

recovered_geometry_event_lookup_table_build_result_ec820
recovered_geometry_event_lookup_table_build_ec820(void)
{
    recovered_geometry_event_lookup_table_build_result_ec820 result;
    recovered_u32 row;
    recovered_u32 column;
    recovered_u32 slot;

    result.literal_source_address = 0x000ead20U;
    result.source_words[0] = 0x0001U;
    result.source_words[1] = 0x0020U;
    result.source_words[2] = 0x0400U;
    result.seed_table_address = 0x01080000U;
    result.seed_word = 0x88888888U;
    result.seed_word_count = 8U;
    result.destination_table_address = 0x01800010U;
    result.destination_stride_bytes = 2U;
    result.source_record_count = 3U;
    result.column_count = 32U;
    result.slot_count = 8U;

    for (row = 0U; row < 3U; ++row) {
        for (column = 0U; column < 32U; ++column) {
            for (slot = 0U; slot < 8U; ++slot) {
                recovered_u32 value = 0xffff8000U +
                    (column + slot) * result.source_words[row];
                result.table[row][column][slot] = (uint16_t)value;
            }
        }
    }
    result.next_target = 0x000ec8e4U;
    return result;
}

recovered_u32
recovered_geometry_event_lookup_table_address_ec820(recovered_u32 row,
                                                     recovered_u32 column,
                                                     recovered_u32 slot)
{
    if (row >= 3U || column >= 32U || slot >= 8U)
        return 0U;
    return recovered_geometry_event_lookup_table_address_unchecked_ec820(row, column, slot);
}
