/* Plane-1 glyph emitter recovered from i960 0x1cf40-0x1cfdc. */
#include <stdint.h>

typedef uint32_t u32;
typedef int32_t s32;

struct recovered_glyph_emit_plane1_plan {
    u32 masked_byte;
    s32 biased_byte;
    u32 zeroed;
    u32 glyph_table;
    s32 table_index;
    u32 plane_base;
    u32 glyph_attr;
    u32 tile_addresses[2];
    u32 column_wrap;
    u32 next_column;
};

void recovered_glyph_emit_plane1_plan(u32 byte, u32 column, u32 row,
                                      struct recovered_glyph_emit_plane1_plan *plan)
{
    u32 tile_slot;
    s32 shifted;

    plan->masked_byte = byte & 0x7fU;
    plan->biased_byte = (s32)(plan->masked_byte - 32U);
    /* The gate compares the shifted (not sign-extended) value against
     * 0x5f000000, so every masked byte stays on the table path; only a
     * biased value above 0x5f would be zeroed first. */
    shifted = (s32)((u32)plan->biased_byte << 24);
    plan->zeroed = shifted > (s32)0x5f000000U ? 1U : 0U;
    plan->glyph_table = 0x02ea0fd0U;
    plan->table_index = plan->zeroed ? 0 : plan->biased_byte;
    plan->plane_base = 0x01002000U;
    /* setbit 15 only: plane 1 carries no 0x4000 bank attribute. */
    plan->glyph_attr = 0x8000U;
    plan->column_wrap = 61U;
    tile_slot = row * 64U + column;
    plan->tile_addresses[0] = plan->plane_base + tile_slot * 2U;
    plan->tile_addresses[1] = plan->plane_base + (tile_slot + 64U) * 2U;
    plan->next_column = column > plan->column_wrap ? column : column + 1U;
}
