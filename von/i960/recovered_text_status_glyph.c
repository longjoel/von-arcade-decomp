/* Pure selector plan for the alternate status glyph sink at 0x1d570. */

#include <stdint.h>

typedef uint32_t u32;

enum recovered_status_glyph_source_kind {
    RECOVERED_STATUS_GLYPH_DESCRIPTOR = 0,
    RECOVERED_STATUS_GLYPH_SPECIAL = 1,
};

struct recovered_status_glyph_plan {
    u32 glyph_index;
    u32 source_kind;
    u32 source;
    u32 descriptor;
    u32 rows;
    u32 adjustment;
};

void recovered_text_status_glyph_plan(u32 character,
                                      u32 *descriptor_adjustment,
                                      struct recovered_status_glyph_plan *plan)
{
    u32 index = (character & 0x7fU) - 0x20U;

    if (index > 95U)
        index = 0U;

    plan->glyph_index = index;
    plan->source_kind = (index == 41U || index == 42U)
        ? RECOVERED_STATUS_GLYPH_SPECIAL
        : RECOVERED_STATUS_GLYPH_DESCRIPTOR;
    plan->source = index == 41U ? 0x02fd7c90U
        : index == 42U ? 0x02fd7c98U : 0U;
    plan->descriptor = index * 8U + 0x02ea14d0U;
    plan->rows = 2U;
    plan->adjustment = descriptor_adjustment ? *descriptor_adjustment : 0U;
}

/* Describe one of the 0x1d570 two-row plane-0 tile stores. */
u32 recovered_text_status_glyph_tile_plan(u32 row,
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

/* Describe the 0x1d570 cursor tail after both glyph rows are written. */
u32 recovered_text_status_glyph_next_column(u32 character,
                                            u32 column,
                                            u32 width,
                                            u32 trailing_flag,
                                            u32 *next_column)
{
    u32 normalized = character & 0x7fU;

    if (normalized < 0x20U)
        normalized = 0U;
    if (trailing_flag == 1U && ((normalized + 0xd7U) & 0xffU) > 1U)
        ++column;
    if (column <= 61U)
        column += width;
    *next_column = column;
    return 1U;
}
