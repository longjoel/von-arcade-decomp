/* Deterministic entry route and frame contract recovered from 0x1e030. */

#include <stdint.h>

typedef uint32_t u32;

enum recovered_status_render_route {
    RECOVERED_STATUS_RENDER_SOURCE_BLOCK = 0,
    RECOVERED_STATUS_RENDER_UNRESOLVED = 1,
    RECOVERED_STATUS_RENDER_BLANK_BLOCK = 2,
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

struct recovered_status_secondary_pair_plan {
    u32 secondary_word;
    u32 source;
    u32 source_width;
    u32 blank_width;
    u32 column;
    u32 row;
    u32 height;
    u32 source_helper;
    u32 blank_helper;
};

void recovered_text_status_secondary_pair_plan(
    u32 secondary_word, u32 caller_g13,
    struct recovered_status_secondary_pair_plan *plan)
{
    /* 0x1e0d4 selects the 14/15 pair only for secondary value 1; the
       fall-through 0x1e110 selects the 16/17 pair for every other value. */
    plan->secondary_word = secondary_word;
    plan->source = secondary_word == 1U ? 0x02fd8170U : 0x02fd81a8U;
    plan->source_width = secondary_word == 1U ? 14U : 16U;
    plan->blank_width = secondary_word == 1U ? 15U : 17U;
    plan->column = 1U;
    plan->row = caller_g13 + 31U;
    plan->height = 2U;
    plan->source_helper = 0x0001dd10U;
    plan->blank_helper = 0x0001df70U;
}

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

void recovered_text_status_render_gate_plan(u32 primary_status_nonzero,
                                            u32 secondary_status_nonzero,
                                            u32 signed_counter_nonzero,
                                            u32 caller_g13,
                                            struct recovered_status_render_plan *plan)
{
    plan->route = primary_status_nonzero
        ? RECOVERED_STATUS_RENDER_SOURCE_BLOCK
        : ((!secondary_status_nonzero && !signed_counter_nonzero)
           ? RECOVERED_STATUS_RENDER_BLANK_BLOCK
           : RECOVERED_STATUS_RENDER_UNRESOLVED);
    plan->source = primary_status_nonzero ? 0x02fd81ecU : 0U;
    plan->column = primary_status_nonzero || plan->route == RECOVERED_STATUS_RENDER_BLANK_BLOCK
        ? 1U : 0U;
    plan->row = plan->route == RECOVERED_STATUS_RENDER_UNRESOLVED
        ? 0U : caller_g13 + 31U;
    plan->width = primary_status_nonzero ? 19U
        : (plan->route == RECOVERED_STATUS_RENDER_BLANK_BLOCK ? 21U : 0U);
    plan->height = plan->route == RECOVERED_STATUS_RENDER_UNRESOLVED ? 0U : 2U;
    plan->saved_general_register_words = 8U;
    plan->saved_special_register_words = 2U;
    plan->saved_fp_registers = 4U;
    plan->stack_frame_bytes = 0x50U;
}
