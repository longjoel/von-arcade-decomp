/* Block string emitter recovered from i960 0x1dc90-0x1dd04. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_block_emit_plan {
    u32 row_addr;
    u32 col_addr;
    u32 plane_base;
    u32 glyph_attr;
    u32 row_stride_slots;
    u32 width;
    u32 rows;
    u32 total_halfwords;
    u32 start_slot;
};

void recovered_block_emit_plan(u32 width, u32 rows, u32 column, u32 row,
                               struct recovered_block_emit_plan *plan)
{
    plan->row_addr = 0x00504ce4U;
    plan->col_addr = 0x00504ce0U;
    plan->plane_base = 0x01000000U;
    /* shlo 14,3 then or: every emitted halfword carries 0xc000. */
    plan->glyph_attr = 0xc000U;
    plan->row_stride_slots = 64U;
    plan->width = width;
    plan->rows = rows;
    plan->total_halfwords = width * rows;
    plan->start_slot = row * 64U + column;
}
