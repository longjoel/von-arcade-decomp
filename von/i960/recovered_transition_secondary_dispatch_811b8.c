/* State dispatch recovered from i960 0x811b8-0x811d0. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_transition_secondary_dispatch_811b8_plan {
    u32 object_state;
    u32 table_base;
    u32 bounded_to_table;
    u32 selected_target;
};

/* The indirect table has eight entries; the >7 arm enters the modeled bypass at 0x815ac. */
void recovered_transition_secondary_dispatch_811b8(
    u32 object_state,
    struct recovered_transition_secondary_dispatch_811b8_plan *plan)
{
    static const u32 targets[8] = {
        0x000811f0U, 0x00081260U, 0x000812acU, 0x00081300U,
        0x00081390U, 0x0008140cU, 0x00081480U, 0x00081528U
    };
    const u32 bounded = object_state <= 7U ? 1U : 0U;

    plan->object_state = object_state;
    plan->table_base = 0x000811d0U;
    plan->bounded_to_table = bounded;
    plan->selected_target = bounded != 0U
        ? targets[object_state] : 0x000815acU;
}
