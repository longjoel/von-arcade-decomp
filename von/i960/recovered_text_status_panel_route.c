/* Paired renderer route recovered from i960 0x1f0d0. */

#include <stdint.h>

typedef uint32_t u32;

enum recovered_status_panel_route {
    RECOVERED_STATUS_PANEL_SOURCE_BLOCK = 0,
    RECOVERED_STATUS_PANEL_ZERO_FILL = 1,
};

struct recovered_status_panel_plan {
    u32 route;
    u32 helper;
    u32 source;
    u32 fill_value;
    u32 column;
    u32 row;
    u32 width;
    u32 height;
    u32 stack_frame_bytes;
};

void recovered_text_status_panel_plan(u32 mode, u32 caller_g6, u32 caller_g10,
                                      struct recovered_status_panel_plan *plan)
{
    plan->route = mode == 0U
        ? RECOVERED_STATUS_PANEL_ZERO_FILL
        : RECOVERED_STATUS_PANEL_SOURCE_BLOCK;
    plan->helper = mode == 0U ? 0x0001df70U : 0x0001dd10U;
    plan->source = mode == 0U ? 0U : 0x02fd8238U;
    plan->fill_value = 0U;
    plan->column = 10U;
    plan->row = caller_g6 + 31U;
    plan->width = caller_g10 + 31U;
    plan->height = 3U;
    plan->stack_frame_bytes = 0x50U;
}
