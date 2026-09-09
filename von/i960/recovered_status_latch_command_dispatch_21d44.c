/* Bounded latch command dispatch recovered from i960 0x21d44-0x21d94. */

#include <stdint.h>

typedef uint32_t u32;

enum recovered_status_latch_command_route {
    RECOVERED_STATUS_LATCH_COMMAND_TAIL = 0,
    RECOVERED_STATUS_LATCH_COMMAND_56 = 1,
    RECOVERED_STATUS_LATCH_COMMAND_66 = 2
};

struct recovered_status_latch_command_dispatch_plan {
    u32 route;
    u32 command_helper;
    u32 command;
    u32 command_source;
    u32 command_index;
    u32 continuation_target;
};

void recovered_status_latch_command_dispatch_plan(
    int32_t latch, u32 selector_value,
    u32 selected_table_command,
    struct recovered_status_latch_command_dispatch_plan *plan)
{
    plan->route = RECOVERED_STATUS_LATCH_COMMAND_TAIL;
    plan->command_helper = 0U;
    plan->command = 0U;
    plan->command_source = 0U;
    plan->command_index = 0U;
    plan->continuation_target = 0x00021fa4U;

    if (latch == 56) {
        plan->route = RECOVERED_STATUS_LATCH_COMMAND_56;
        plan->command_helper = 0x0002a4e0U;
        plan->command_index = selector_value;
        if (selector_value == 0U) {
            plan->command = 0x1322U;
        } else {
            plan->command_source = 0x00021180U;
            plan->command = selected_table_command;
        }
    } else if (latch == 66) {
        plan->route = RECOVERED_STATUS_LATCH_COMMAND_66;
        plan->continuation_target = 0x00021ef8U;
    }
}
