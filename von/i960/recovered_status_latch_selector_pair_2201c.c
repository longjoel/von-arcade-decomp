/* Selector-pair branch recovered from i960 0x2201c-0x220b4. */

#include <stdint.h>

typedef uint32_t u32;

enum recovered_status_latch_selector_pair_route {
    RECOVERED_STATUS_LATCH_SELECTOR_PAIR_TAIL = 0,
    RECOVERED_STATUS_LATCH_SELECTOR_PAIR_GLYPH = 1,
    RECOVERED_STATUS_LATCH_SELECTOR_PAIR_TEXT = 2
};

struct recovered_status_latch_selector_pair_plan {
    u32 route;
    u32 selector_gate;
    u32 selector;
    u32 first_source;
    u32 second_source;
    u32 helper;
    u32 call_count;
    u32 column;
    u32 row;
    u32 source_stride;
    u32 continuation_target;
};

void recovered_status_latch_selector_pair_plan(
    u32 selector_gate, u32 selector,
    struct recovered_status_latch_selector_pair_plan *plan)
{
    plan->route = RECOVERED_STATUS_LATCH_SELECTOR_PAIR_TAIL;
    plan->selector_gate = selector_gate;
    plan->selector = selector;
    plan->first_source = 0U;
    plan->second_source = 0U;
    plan->helper = 0U;
    plan->call_count = 0U;
    plan->column = 0U;
    plan->row = 0U;
    plan->source_stride = 16U;
    plan->continuation_target = 0x00022108U;

    if (selector_gate == 0U) {
        plan->route = selector <= 7U
            ? RECOVERED_STATUS_LATCH_SELECTOR_PAIR_TEXT
            : RECOVERED_STATUS_LATCH_SELECTOR_PAIR_GLYPH;
        plan->first_source = 0x00020f60U + selector * 16U;
        plan->second_source = plan->first_source + 8U;
        plan->helper = selector <= 7U ? 0x0001d880U : 0x0001d7d0U;
        plan->call_count = 2U;
        plan->column = selector + 31U;
        plan->row = selector + 9U;
    } else {
        plan->continuation_target = 0x000220b8U;
    }
}
