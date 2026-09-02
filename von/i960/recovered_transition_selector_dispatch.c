/* Selector-table contract recovered from i960 0x784c8. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_transition_selector_plan {
    u32 target;
    u32 writes_flag;
    u32 flag_value;
};

struct recovered_transition_action_state {
    u32 transition;
    u32 action;
};

/* A zero target denotes the immediate-return path for an unsigned selector > 9. */
u32 recovered_transition_selector_target(u32 selector)
{
    static const u32 targets[10] = {
        0x00078508, 0x00078524, 0x00078540, 0x00078560, 0x0007857c,
        0x0007859c, 0x000785bc, 0x000785d8, 0x000785f8, 0x00078618,
    };

    return selector < 10 ? targets[selector] : 0;
}

/* Return the handler's write condition; a zero means leave 0x504d84 unchanged. */
u32 recovered_transition_selector_flag(u32 selector, u32 mode_bits)
{
    if (selector >= 10)
        return 0;
    if (selector == 0 || selector == 6)
        return (mode_bits & (1U << 1)) != 0;
    if (selector == 1 || selector == 3)
        return (mode_bits & (1U << 2)) != 0;
    return (mode_bits & ((1U << 1) | (1U << 2))) != 0;
}

void recovered_transition_selector_plan(u32 selector, u32 mode_bits,
                                         struct recovered_transition_selector_plan *plan)
{
    plan->target = recovered_transition_selector_target(selector);
    plan->writes_flag = plan->target != 0 &&
                        recovered_transition_selector_flag(selector, mode_bits) != 0;
    plan->flag_value = plan->writes_flag != 0 ? 1 : 0;
}

u32 recovered_transition_action5_table_value(u32 selector)
{
    static const u32 values[10] = { 8, 12, 12, 12, 12, 13, 13, 13, 19, 8 };

    return selector < 10 ? values[selector] : 0;
}

u32 recovered_transition_action10_table_value(u32 selector)
{
    static const u32 values[10] = { 9, 16, 12, 12, 12, 13, 13, 13, 17, 9 };

    return selector < 10 ? values[selector] : 0;
}

u32 recovered_transition_apply_action5(u32 selector,
                                       struct recovered_transition_action_state *state)
{
    if (selector >= 10)
        return 0;
    state->transition = recovered_transition_action5_table_value(selector);
    state->action = 5;
    return 1;
}

u32 recovered_transition_apply_action10(u32 selector,
                                        struct recovered_transition_action_state *state)
{
    if (selector >= 10)
        return 0;
    state->transition = recovered_transition_action10_table_value(selector);
    state->action = 10;
    return 1;
}
