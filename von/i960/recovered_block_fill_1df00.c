/* Block fill recovered from i960 0x1df00-0x1df64. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_block_fill_plan {
    u32 row_addr;
    u32 col_addr;
    u32 plane_base;
    /* The fill halfword is the caller link in g14, opaque to this plan. */
    u32 fill_is_caller_link;
    u32 row_stride_slots;
    u32 width;
    u32 rows;
    u32 total_tiles;
    u32 start_slot;
};

void recovered_block_fill_plan(u32 width, u32 rows, u32 column, u32 row,
                               struct recovered_block_fill_plan *plan)
{
    plan->row_addr = 0x00504ce4U;
    plan->col_addr = 0x00504ce0U;
    plan->plane_base = 0x01000000U;
    plan->fill_is_caller_link = 1U;
    plan->row_stride_slots = 64U;
    plan->width = width;
    plan->rows = rows;
    plan->total_tiles = width * rows;
    plan->start_slot = row * 64U + column;
}
