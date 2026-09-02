/* Deterministic entry route and frame contract recovered from 0x1e030. */

#include <stdint.h>

typedef uint32_t u32;

enum recovered_status_render_route {
    RECOVERED_STATUS_RENDER_SOURCE_BLOCK = 0,
    RECOVERED_STATUS_RENDER_UNRESOLVED = 1,
};

struct recovered_status_render_plan {
    u32 route;
    u32 source;
    u32 column;
    u32 row;
    u32 width;
    u32 height;
    u32 saved_general_register_words;
    u32 saved_special_register_words;
    u32 saved_fp_registers;
    u32 stack_frame_bytes;
};

void recovered_text_status_render_plan(u32 status_byte_nonzero, u32 caller_g13,
                                       struct recovered_status_render_plan *plan)
{
    plan->route = status_byte_nonzero
        ? RECOVERED_STATUS_RENDER_SOURCE_BLOCK
        : RECOVERED_STATUS_RENDER_UNRESOLVED;
    plan->source = status_byte_nonzero ? 0x02fd81ecU : 0U;
    plan->column = status_byte_nonzero ? 1U : 0U;
    plan->row = status_byte_nonzero ? caller_g13 + 31U : 0U;
    plan->width = status_byte_nonzero ? 19U : 0U;
    plan->height = status_byte_nonzero ? 2U : 0U;
    plan->saved_general_register_words = 8U;
    plan->saved_special_register_words = 2U;
    plan->saved_fp_registers = 4U;
    plan->stack_frame_bytes = 0x50U;
}
