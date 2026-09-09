/* Bounded schedule for the glyph writer at i960 0x1d6a0. */

#include <stdint.h>

typedef uint32_t u32;

/* Describe normalization and the cursor tail after the two-row emit. */
u32 recovered_text_glyph_writer_1d6a0_plan(
    u32 character,
    u32 origin,
    u32 column,
    u32 row,
    u32 width,
    u32 *normalized_index,
    u32 *next_column,
    u32 *next_row,
    u32 *is_control)
{
    u32 byte = character & 0xffU;
    u32 index;

    *normalized_index = 0U;
    *next_column = column;
    *next_row = row;
    *is_control = 0U;
    if (byte == 0x21U) {
        *next_column = origin;
        *next_row = row + 1U;
        *is_control = 1U;
        return 1U;
    }

    index = byte & 0x7fU;
    if (index < 0x20U)
        index = 0U;
    else
        index -= 0x20U;
    *normalized_index = index;
    if (index == 0x5cU)
        ++column;
    if (column <= 61U)
        column += width;
    *next_column = column;
    return 1U;
}

/* Describe one source halfword and destination tile store. */
u32 recovered_text_glyph_writer_1d6a0_tile_plan(
    u32 row,
    u32 column,
    u32 width,
    u32 plane,
    u32 entry,
    u32 source_base,
    u32 glyph_word,
    u32 *source_address,
    u32 *tile_address,
    u32 *tile_value)
{
    if (plane >= 2U || entry >= width)
        return 0U;
    *source_address = source_base + ((plane * width + entry) << 1);
    *tile_address = 0x01000000U
        + ((((row + plane) << 6) + column + entry) << 1);
    *tile_value = (glyph_word | 0x8000U) & 0xffffU;
    return 1U;
}
