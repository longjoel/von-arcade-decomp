/* Dispatcher prefix recovered from i960 0x7db70-0x7db7c. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_followup_dispatch_7db70_plan {
    u32 dispatch_allowed;
    u32 table_index;
    u32 target;
};

void recovered_state_followup_dispatch_7db70(
    u32 selector, struct recovered_state_followup_dispatch_7db70_plan *plan)
{
    static const u32 targets[10] = {
        0x0007dba8U, 0x0007dbb8U, 0x0007dba8U, 0x0007dbb8U,
        0x0007dbc8U, 0x0007dbd8U, 0x0007dbf4U, 0x0007dc04U,
        0x0007dc98U, 0x0007dca8U,
    };

    plan->dispatch_allowed = 0U;
    plan->table_index = selector;
    plan->target = 0U;
    if (selector > 9U) {
        plan->target = 0x0007dca8U;
        return;
    }
    plan->dispatch_allowed = 1U;
    plan->target = targets[selector];
}
