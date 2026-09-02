/* Deterministic status renderer plan recovered from i960 0x1f3b0. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_press_start_plan {
    u32 message;
    u32 text_helper;
    u32 column;
    u32 row;
    u32 flag_address;
    u32 flag_set_mask;
    u32 flag_clear_mask;
};

void recovered_press_start_plan(u32 input_nonzero, u32 caller_g9, u32 caller_g13,
                                struct recovered_press_start_plan *plan)
{
    plan->message = input_nonzero ? 0x0001f370U : 0x0001f390U;
    plan->text_helper = 0x0001d210U;
    plan->column = caller_g9 + 31U;
    plan->row = caller_g13 + 31U;
    plan->flag_address = 0x00502484U;
    plan->flag_set_mask = input_nonzero ? 0x00000004U : 0U;
    plan->flag_clear_mask = input_nonzero ? 0U : 0x0000fffbU;
}
