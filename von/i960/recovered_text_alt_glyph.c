/* Pure write-plan for the alternate two-row glyph sinks at 0x1ce00/0x1cea0. */
typedef unsigned int u32;

struct recovered_alt_glyph_plan {
    u32 glyph_index;
    u32 first_tile;
    u32 second_tile;
    u32 attribute;
    u32 next_column;
};

void recovered_text_alt_glyph_plan(u32 character,
                                   u32 row,
                                   u32 column,
                                   u32 attributed,
                                   struct recovered_alt_glyph_plan *plan)
{
    u32 normalized = (character & 0x7fU) - 0x20U;

    if (normalized > 95U)
        normalized = 0U;

    plan->glyph_index = normalized;
    plan->first_tile = (row << 6) + column;
    plan->second_tile = plan->first_tile + 0x40U;
    plan->attribute = attributed ? 0xc000U : 0U;
    plan->next_column = column <= 30U ? column + 1U : column;
}
