/* Latch service routes recovered from i960 0x21f08-0x21fa0. */

#include <stdint.h>

typedef uint32_t u32;

enum recovered_status_latch_service_route {
    RECOVERED_STATUS_LATCH_SERVICE_TAIL = 0,
    RECOVERED_STATUS_LATCH_SERVICE_COMMAND = 1,
    RECOVERED_STATUS_LATCH_SERVICE_CLEAR = 2,
    RECOVERED_STATUS_LATCH_SERVICE_STATE = 3,
    RECOVERED_STATUS_LATCH_SERVICE_BOOKKEEPING = 4
};

struct recovered_status_latch_service_plan {
    u32 route;
    u32 helper;
    u32 command_helper;
    u32 command;
    u32 first_state_helper;
    u32 second_state_helper;
    u32 state_before;
    u32 state_first_result;
    u32 state_after;
    u32 second_state_result;
    u32 counter_before;
    u32 counter_after;
    u32 continuation_target;
};

void recovered_status_latch_service_plan(
    int32_t latch, u32 state_before, u32 first_helper_result,
    u32 second_helper_result, u32 counter_before,
    struct recovered_status_latch_service_plan *plan)
{
    plan->route = RECOVERED_STATUS_LATCH_SERVICE_TAIL;
    plan->helper = 0U;
    plan->command_helper = 0U;
    plan->command = 0U;
    plan->first_state_helper = 0U;
    plan->second_state_helper = 0U;
    plan->state_before = state_before;
    plan->state_first_result = 0U;
    plan->state_after = state_before;
    plan->second_state_result = 0U;
    plan->counter_before = counter_before;
    plan->counter_after = counter_before;
    plan->continuation_target = 0x00021fa4U;

    if (latch == 156) {
        plan->route = RECOVERED_STATUS_LATCH_SERVICE_COMMAND;
        plan->helper = 0x00022c78U;
        plan->command_helper = 0x0002a4e0U;
        plan->command = 0x133fU;
    } else if (latch == 157) {
        plan->route = RECOVERED_STATUS_LATCH_SERVICE_CLEAR;
        plan->helper = 0x00020ae8U;
    } else if (latch >= 158 && latch <= 185) {
        plan->route = RECOVERED_STATUS_LATCH_SERVICE_STATE;
        plan->first_state_helper = 0x000f5058U;
        plan->second_state_helper = 0x000f5058U;
        plan->state_first_result = first_helper_result & 0x1ffU;
        plan->state_after = (state_before + plan->state_first_result) & 0x1ffU;
        plan->second_state_result = second_helper_result & 0x1ffU;
    } else if (latch == 186) {
        plan->route = RECOVERED_STATUS_LATCH_SERVICE_CLEAR;
        plan->helper = 0x00022cb8U;
    } else if (latch >= 187) {
        plan->route = RECOVERED_STATUS_LATCH_SERVICE_BOOKKEEPING;
        plan->counter_after = counter_before - 1U;
    }
}
