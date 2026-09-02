/* Deterministic insert-coin renderer plan recovered from i960 0x1f470. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_insert_coin_plan {
    u32 message;
    u32 text_helper;
    u32 column;
    u32 row;
};

void recovered_insert_coin_plan(u32 input_nonzero, u32 caller_g5, u32 caller_g13,
                                struct recovered_insert_coin_plan *plan)
{
    plan->message = input_nonzero ? 0x0001f440U : 0x0001f450U;
    plan->text_helper = 0x0001d9e0U;
    plan->column = caller_g5 + 31U;
    plan->row = caller_g13 + 31U;
}
