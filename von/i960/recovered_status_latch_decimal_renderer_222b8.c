/* Latch-70 decimal renderer recovered from i960 0x222b8-0x223f8. */

#include <stdint.h>

typedef uint32_t u32;

enum recovered_status_latch_decimal_renderer_route {
    RECOVERED_STATUS_LATCH_DECIMAL_TAIL = 0,
    RECOVERED_STATUS_LATCH_DECIMAL_RENDER = 1
};

struct recovered_status_latch_decimal_renderer_plan {
    u32 route;
    u32 latch;
    u32 first_value;
    u32 second_value;
    u32 third_value;
    u32 special_base;
    u32 digit_writer;
    u32 call_count;
    u32 rendered_value[13];
    u32 continuation_target;
};

static u32 recovered_decimal_digit(u32 value, u32 divisor)
{
    return (value / divisor) % 10U + 0x30U;
}

void recovered_status_latch_decimal_renderer_plan(
    int32_t latch, u32 first_value, u32 second_value, u32 third_value,
    u32 special_base,
    struct recovered_status_latch_decimal_renderer_plan *plan)
{
    plan->route = RECOVERED_STATUS_LATCH_DECIMAL_TAIL;
    plan->latch = (u32)latch;
    plan->first_value = first_value;
    plan->second_value = second_value;
    plan->third_value = third_value;
    plan->special_base = special_base;
    plan->digit_writer = 0U;
    plan->call_count = 0U;
    plan->continuation_target = 0x000223fcU;
    for (u32 i = 0U; i < 13U; ++i) {
        plan->rendered_value[i] = 0U;
    }

    if (latch == 70) {
        plan->route = RECOVERED_STATUS_LATCH_DECIMAL_RENDER;
        plan->digit_writer = 0x0001d090U;
        plan->call_count = 13U;
        plan->rendered_value[0] = recovered_decimal_digit(first_value, 1000U);
        plan->rendered_value[1] = recovered_decimal_digit(first_value, 100U);
        plan->rendered_value[2] = recovered_decimal_digit(first_value, 10U);
        plan->rendered_value[3] = special_base + 31U;
        plan->rendered_value[4] = first_value % 10U + 0x30U;
        plan->rendered_value[5] = recovered_decimal_digit(second_value, 1000U);
        plan->rendered_value[6] = recovered_decimal_digit(second_value, 100U);
        plan->rendered_value[7] = recovered_decimal_digit(second_value, 10U);
        plan->rendered_value[8] = special_base + 31U;
        plan->rendered_value[9] = second_value % 10U + 0x30U;
        plan->rendered_value[10] = recovered_decimal_digit(third_value, 100U);
        plan->rendered_value[11] = recovered_decimal_digit(third_value, 10U);
        plan->rendered_value[12] = third_value % 10U + 0x30U;
    }
}
