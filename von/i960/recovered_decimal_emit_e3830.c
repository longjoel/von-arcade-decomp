/* Saturating decimal emitter recovered from i960 0xe3830-0xe3878. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_decimal_emit_plan {
    u32 saturate_limit;
    u32 saturated;
    u32 saturate_string;
    u32 string_walker;
    u32 tens_char;
    u32 ones_char;
    u32 digit_walker;
    u32 digit_mode0;
    u32 digit_mode1;
};

void recovered_decimal_emit_plan(u32 value,
                                 struct recovered_decimal_emit_plan *plan)
{
    /* cmpo compares ordinally, so values above 99 saturate even though
     * divi/remi below are signed. */
    plan->saturate_limit = 99U;
    plan->saturated = value > plan->saturate_limit ? 1U : 0U;
    /* The 0xe3824 fallback holds the ASCII pair "99". */
    plan->saturate_string = 0x000e3824U;
    plan->string_walker = 0x0001d9e0U;
    plan->digit_walker = 0x0001d310U;
    plan->digit_mode0 = 3U;
    plan->digit_mode1 = 0U;
    if (plan->saturated) {
        plan->tens_char = 0U;
        plan->ones_char = 0U;
    } else {
        plan->tens_char = 0x30U + value / 10U;
        plan->ones_char = 0x30U + value % 10U;
    }
}
