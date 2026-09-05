/* Plane-1 attributed glyph emitter recovered from i960 0x1cfe0-0x1d080. */
#include <stdint.h>

typedef uint32_t u32;
typedef int32_t s32;

struct recovered_glyph_emit_attr_plan {
    u32 masked_byte;
    s32 biased_byte;
    u32 zeroed;
    u32 glyph_table;
    s32 table_index;
    u32 plane_base;
    u32 glyph_attr;
    u32 attr_forces_bank;
    u32 tile_addresses[2];
    u32 column_wrap;
    u32 next_column;
};

void recovered_glyph_emit_attr_plan(u32 byte, u32 column, u32 row,
                                    struct recovered_glyph_emit_attr_plan *plan)
{
    u32 tile_slot;
    s32 shifted;

    plan->masked_byte = byte & 0x7fU;
    plan->biased_byte = (s32)(plan->masked_byte - 32U);
    shifted = (s32)((u32)plan->biased_byte << 24);
    plan->zeroed = shifted > (s32)0x5f000000U ? 1U : 0U;
    plan->glyph_table = 0x02ea0fd0U;
    plan->table_index = plan->zeroed ? 0 : plan->biased_byte;
    plan->plane_base = 0x01002000U;
    plan->glyph_attr = 0xc000U;
    /* or (not setbit 15): the 0x1cf40 sibling preserves a set bit 14
     * from glyph data, while this emitter forces both attribute bits. */
    plan->attr_forces_bank = 1U;
    plan->column_wrap = 61U;
    tile_slot = row * 64U + column;
    plan->tile_addresses[0] = plan->plane_base + tile_slot * 2U;
    plan->tile_addresses[1] = plan->plane_base + (tile_slot + 64U) * 2U;
    plan->next_column = column > plan->column_wrap ? column : column + 1U;
}
