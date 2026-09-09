/* Latch-87 panel route recovered from i960 0x21e7c-0x21ef4. */

#include <stdint.h>

typedef uint32_t u32;

enum recovered_status_latch_panel87_route {
    RECOVERED_STATUS_LATCH_PANEL87_TAIL = 0,
    RECOVERED_STATUS_LATCH_PANEL87_RENDER = 1
};

struct recovered_status_latch_panel87_plan {
    u32 route;
    u32 latch;
    u32 selector;
    u32 first_source;
    u32 first_helper;
    u32 first_width;
    u32 first_height;
    u32 first_column;
    u32 first_row;
    u32 second_source;
    u32 second_helper;
    u32 second_column;
    u32 second_row;
    u32 second_command;
    u32 continuation_target;
};

void recovered_status_latch_panel87_plan(
    int32_t latch, u32 selector, u32 first_column,
    u32 first_source, u32 second_source,
    struct recovered_status_latch_panel87_plan *plan)
{
    plan->route = RECOVERED_STATUS_LATCH_PANEL87_TAIL;
    plan->latch = (u32)latch;
    plan->selector = selector;
    plan->first_source = 0U;
    plan->first_helper = 0U;
    plan->first_width = 0U;
    plan->first_height = 0U;
    plan->first_column = 0U;
    plan->first_row = 0U;
    plan->second_source = 0U;
    plan->second_helper = 0U;
    plan->second_column = 0U;
    plan->second_row = 0U;
    plan->second_command = 0U;
    plan->continuation_target = 0x00021fa4U;

    /* The cmpibg at 0x21e80 sends only latch 87 through this body. */
    if (latch == 87) {
        plan->route = RECOVERED_STATUS_LATCH_PANEL87_RENDER;
        plan->first_source = first_source;
        plan->first_helper = 0x0001dc10U;
        plan->first_width = 20U;
        plan->first_height = 15U;
        plan->first_column = first_column;
        plan->first_row = 24U;
        plan->second_source = second_source;
        plan->second_helper = 0x0001d1d0U;
        plan->second_column = selector + 31U;
        plan->second_row = 26U;
        plan->second_command = 0x1111U;
        plan->continuation_target = 0x00021fa4U;
    }
}
