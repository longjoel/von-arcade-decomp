/* Latch-86 glyph/record route recovered from i960 0x21d98-0x21e78. */

#include <stdint.h>

typedef uint32_t u32;

enum recovered_status_latch_glyph_record_route {
    RECOVERED_STATUS_LATCH_GLYPH_TAIL = 0,
    RECOVERED_STATUS_LATCH_GLYPH_RECORD = 1
};

struct recovered_status_latch_glyph_record_plan {
    u32 route;
    u32 latch;
    u32 selector;
    u32 mode;
    u32 column;
    u32 row;
    u32 matcher;
    u32 matcher_source;
    u32 matcher_stride;
    u32 glyph_index;
    u32 record_table;
    u32 record_stride;
    u32 source_first;
    u32 source_second;
    u32 source_third;
    u32 transfer_helper;
    u32 continuation_target;
};

void recovered_status_latch_glyph_record_plan(
    int32_t latch, u32 selector, u32 mode, u32 glyph_index,
    u32 source_first, u32 source_second, u32 source_third,
    struct recovered_status_latch_glyph_record_plan *plan)
{
    plan->route = RECOVERED_STATUS_LATCH_GLYPH_TAIL;
    plan->latch = (u32)latch;
    plan->selector = selector;
    plan->mode = mode;
    plan->column = 0U;
    plan->row = 0U;
    plan->matcher = 0U;
    plan->matcher_source = 0U;
    plan->matcher_stride = 0U;
    plan->glyph_index = 0U;
    plan->record_table = 0U;
    plan->record_stride = 0U;
    plan->source_first = 0U;
    plan->source_second = 0U;
    plan->source_third = 0U;
    plan->transfer_helper = 0U;
    plan->continuation_target = 0x00021fa4U;

    /* d98-d a4 admits only latch 86 with the selector latch clear. */
    if (latch == 86 && selector == 0U) {
        plan->route = RECOVERED_STATUS_LATCH_GLYPH_RECORD;
        plan->column = mode == 2U ? 26U : mode == 6U ? 23U : 25U;
        plan->row = 8U;
        plan->matcher = 0x0001d880U;
        plan->matcher_source = 0x00020ba8U + mode * 104U;
        plan->matcher_stride = 104U;
        plan->glyph_index = glyph_index;
        plan->record_table = 0x00020b50U;
        plan->record_stride = 0x68U;
        plan->source_first = source_first;
        plan->source_second = source_second;
        plan->source_third = source_third;
        plan->transfer_helper = 0x0001dc10U;
    }
}
