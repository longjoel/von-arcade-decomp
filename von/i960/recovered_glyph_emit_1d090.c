/* Plane-0 glyph emitter recovered from i960 0x1d090-0x1d1a0. */
#include <stdint.h>

typedef uint32_t u32;
typedef int32_t s32;

struct recovered_glyph_emit_plan {
    u32 masked_byte;
    s32 biased_byte;
    u32 control_selector;
    u32 control_tiles[2];
    u32 glyph_table;
    s32 table_index;
    u32 plane_base;
    u32 glyph_attr;
    u32 tile_addresses[2];
    u32 column_wrap;
    u32 next_column;
};

void recovered_glyph_emit_plan(u32 byte, u32 column, u32 row,
                               struct recovered_glyph_emit_plan *plan)
{
    u32 tile_slot;

    plan->masked_byte = byte & 0x7fU;
    /* lda -32(g0) followed by the shlo-24/shri-24 pair sign-extends the
     * biased low byte, so bytes below 0x20 yield negative table indices. */
    plan->biased_byte = (s32)(plan->masked_byte - 32U);
    plan->glyph_table = 0x02ea0fd0U;
    plan->plane_base = 0x01000000U;
    plan->glyph_attr = 0xc000U;
    plan->column_wrap = 61U;
    if (plan->biased_byte == 0x4b) {
        plan->control_selector = 1U;
        plan->control_tiles[0] = 0x837cU;
        plan->control_tiles[1] = 0x837dU;
        plan->table_index = 0;
    } else if (plan->biased_byte == 0x54) {
        plan->control_selector = 2U;
        plan->control_tiles[0] = 0x837eU;
        plan->control_tiles[1] = 0x837fU;
        plan->table_index = 0;
    } else {
        plan->control_selector = 0U;
        plan->control_tiles[0] = 0U;
        plan->control_tiles[1] = 0U;
        /* cmpible keeps every 7-bit byte on the table path; only a
         * biased value above 0x5f would be zeroed first. */
        plan->table_index = plan->biased_byte > 0x5f ? 0 : plan->biased_byte;
    }
    tile_slot = row * 64U + column;
    plan->tile_addresses[0] = plan->plane_base + tile_slot * 2U;
    plan->tile_addresses[1] = plan->plane_base + (tile_slot + 64U) * 2U;
    plan->next_column = column > plan->column_wrap ? column : column + 1U;
}
