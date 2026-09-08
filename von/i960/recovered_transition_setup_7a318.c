/* Transition setup recovered from i960 0x7a318-0x7a3d0. */
#include <stdint.h>

typedef uint32_t u32;
typedef int32_t s32;

enum recovered_transition_setup_route {
    RECOVERED_TRANSITION_SETUP_CURSOR = 0,
    RECOVERED_TRANSITION_SETUP_LOW_STATE = 1,
    RECOVERED_TRANSITION_SETUP_HIGH_STATE = 2,
};

struct recovered_transition_setup_plan {
    u32 route;
    u32 writes_504d84;
    u32 value_504d84;
    u32 writes_504d98;
    u32 value_504d98;
    u32 writes_504db8;
    u32 value_504db8;
    u32 writes_504d94;
    u32 value_504d94;
};

void recovered_transition_setup_7a318(
    u32 object_state, u32 control_gate, u32 cursor_504dbc,
    u32 reference_a, u32 reference_b,
    struct recovered_transition_setup_plan *plan)
{
    u32 state_minus_one = object_state - 1U;
    u32 cursor_limit = cursor_504dbc + 22U;
    u32 reference_limit = reference_a + 31U;

    plan->route = RECOVERED_TRANSITION_SETUP_CURSOR;
    plan->writes_504d84 = 0U;
    plan->value_504d84 = 0U;
    plan->writes_504d98 = 0U;
    plan->value_504d98 = 0U;
    plan->writes_504db8 = 0U;
    plan->value_504db8 = 0U;
    plan->writes_504d94 = 0U;
    plan->value_504d94 = 0U;

    if (control_gate == 1U) {
        plan->writes_504d84 = 1U;
        plan->value_504d84 = 1U;
        plan->writes_504d98 = 1U;
        plan->value_504d98 = 1U;
    }

    /* States 1, 2, 4, 5, and 7 share the cursor publication path. */
    if (object_state == 1U || object_state == 2U || object_state == 4U
            || object_state == 5U || object_state == 7U) {
        u32 selected = (s32)reference_limit < (s32)cursor_limit
            ? reference_b + 31U : cursor_limit;

        plan->writes_504db8 = 1U;
        plan->value_504db8 = selected;
        return;
    }

    /* Gate-1 non-cursor states take the literal action-10 arm at 0x7a394. */
    if (control_gate == 1U) {
        plan->writes_504db8 = 1U;
        plan->value_504db8 = 10U;
        return;
    }

    /* cmpobl 3,state_minus_one is literal-first unsigned comparison. */
    plan->writes_504d94 = 1U;
    if (state_minus_one > 3U) {
        plan->route = RECOVERED_TRANSITION_SETUP_HIGH_STATE;
        plan->value_504d94 = 13U;
    } else {
        plan->route = RECOVERED_TRANSITION_SETUP_LOW_STATE;
        plan->value_504d94 = 12U;
    }
}
