/* Paired action-10 table wrappers at i960 0x78448 and 0x78488. */

#include <stdint.h>

struct recovered_transition_action10_table_wrapper_plan {
    uint32_t entry;
    uint32_t trampoline;
    uint32_t table;
    uint32_t selector_source;
    uint32_t action;
    uint32_t action_destination;
    uint32_t transition_destination;
    uint32_t return_register;
};

void recovered_transition_action10_table_wrappers_78448_plan(
    struct recovered_transition_action10_table_wrapper_plan *plan)
{
    plan[0].entry = 0x00078448U;
    plan[0].trampoline = 0x00078478U;
    plan[0].table = 0x00072990U;
    plan[0].selector_source = 0x00504d68U;
    plan[0].action = 10U;
    plan[0].action_destination = 0x00504db8U;
    plan[0].transition_destination = 0x00504d94U;
    plan[0].return_register = 0U; /* g0 */

    plan[1].entry = 0x00078488U;
    plan[1].trampoline = 0x000784b8U;
    plan[1].table = 0x000729f0U;
    plan[1].selector_source = 0x00504d68U;
    plan[1].action = 10U;
    plan[1].action_destination = 0x00504db8U;
    plan[1].transition_destination = 0x00504d94U;
    plan[1].return_register = 0U; /* g0 */
}

uint32_t recovered_transition_action10_table_select(const uint32_t *table,
                                                     uint32_t selector)
{
    return table[selector];
}
