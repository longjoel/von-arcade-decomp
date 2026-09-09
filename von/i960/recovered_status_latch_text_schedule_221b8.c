/* Text schedule recovered from i960 0x221b8-0x222b4. */

#include <stdint.h>

typedef uint32_t u32;

enum recovered_status_latch_text_schedule_route {
    RECOVERED_STATUS_LATCH_TEXT_SCHEDULE_DECIMAL = 0,
    RECOVERED_STATUS_LATCH_TEXT_SCHEDULE_DECIMAL70 = 1
};

struct recovered_status_latch_text_schedule_plan {
    u32 route;
    u32 latch;
    u32 first_row_base;
    u32 second_row_base;
    u32 separator_base;
    u32 character_writer;
    u32 numeric_helper;
    u32 numeric_call_count;
    u32 character_call_count;
    u32 rendered_value[12];
    u32 first_column;
    u32 second_column;
    u32 continuation_target;
};

static u32 recovered_schedule_digit(u32 helper_result)
{
    return helper_result % 10U + 0x30U;
}

void recovered_status_latch_text_schedule_plan(
    int32_t latch, u32 first_row_base, u32 second_row_base,
    u32 separator_base, const u32 helper_result[10],
    struct recovered_status_latch_text_schedule_plan *plan)
{
    plan->route = RECOVERED_STATUS_LATCH_TEXT_SCHEDULE_DECIMAL;
    plan->latch = (u32)latch;
    plan->first_row_base = first_row_base;
    plan->second_row_base = second_row_base;
    plan->separator_base = separator_base;
    plan->character_writer = 0x0001cd18U;
    plan->numeric_helper = 0x000f5058U;
    plan->numeric_call_count = 0U;
    plan->character_call_count = 0U;
    plan->first_column = 13U;
    plan->second_column = 13U;
    plan->continuation_target = 0x000223fcU;
    for (u32 i = 0U; i < 12U; ++i) {
        plan->rendered_value[i] = 0U;
    }

    /* cmpobl 28, latch-41, 0x222b8 leaves latch 0..69 here. */
    if (latch >= 0 && latch <= 69) {
        plan->numeric_call_count = 10U;
        plan->character_call_count = 12U;
        plan->rendered_value[0] = recovered_schedule_digit(helper_result[0]);
        plan->rendered_value[1] = recovered_schedule_digit(helper_result[1]);
        plan->rendered_value[2] = recovered_schedule_digit(helper_result[2]);
        plan->rendered_value[3] = separator_base + 31U;
        plan->rendered_value[4] = recovered_schedule_digit(helper_result[3]);
        plan->rendered_value[5] = recovered_schedule_digit(helper_result[4]);
        plan->rendered_value[6] = recovered_schedule_digit(helper_result[5]);
        plan->rendered_value[7] = recovered_schedule_digit(helper_result[6]);
        plan->rendered_value[8] = separator_base + 31U;
        plan->rendered_value[9] = recovered_schedule_digit(helper_result[7]);
        plan->rendered_value[10] = recovered_schedule_digit(helper_result[8]);
        plan->rendered_value[11] = recovered_schedule_digit(helper_result[9]);
    } else {
        plan->route = RECOVERED_STATUS_LATCH_TEXT_SCHEDULE_DECIMAL70;
        plan->continuation_target = 0x000222b8U;
    }
}
