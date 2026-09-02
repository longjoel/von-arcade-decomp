/* Paired renderer route recovered from i960 0x1f290 (0x1f2a0 is its prologue). */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_status_panel3_plan {
    u32 helper;
    u32 source;
    u32 fill_value;
    u32 column;
    u32 row;
    u32 width;
    u32 height;
    u32 stack_frame_bytes;
};

void recovered_text_status_panel3_plan(u32 mode, u32 caller_g6, u32 caller_g27,
                                       struct recovered_status_panel3_plan *plan)
{
    plan->helper = mode == 0U ? 0x0001df70U : 0x0001dd10U;
    plan->source = mode == 0U ? 0U : 0x02fd848aU;
    plan->fill_value = 0U;
    plan->column = 2U;
    plan->row = caller_g6 + 31U;
    plan->width = caller_g27 + 31U;
    plan->height = 3U;
    plan->stack_frame_bytes = 0x50U;
}
