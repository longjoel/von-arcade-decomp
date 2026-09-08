/* Selector/state classifier-offset route recovered from i960 0x7f210-0x7f31c. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state31_selector_offset_route_7f210_plan {
    u32 object_state;
    u32 related_state;
    u32 selector;
    u32 selector_minus_3;
    u32 positive_selector_arm;
    u32 base_offset;
    int32_t classifier_offset;
    u32 classifier_input;
    u32 target;
    u32 classifier_table;
};

void recovered_state31_selector_offset_route_7f210(
    u32 object_state, u32 related_state, u32 selector,
    struct recovered_state31_selector_offset_route_7f210_plan *plan)
{
    const u32 selector_minus_3 = selector - 3U;
    const u32 positive_arm = selector_minus_3 > 1U;
    u32 base = 0x1000U;

    if (object_state == 6U) {
        base = 0x1000U;
    } else if (related_state == 5U || related_state == 6U) {
        if (related_state == 6U && object_state == 3U)
            base = 0x1800U;
        if (related_state == 6U && object_state == 5U)
            base = 0x3000U;
    } else {
        base = 0x1800U;
    }

    plan->object_state = object_state;
    plan->related_state = related_state;
    plan->selector = selector;
    plan->selector_minus_3 = selector_minus_3;
    plan->positive_selector_arm = positive_arm;
    plan->base_offset = base;
    plan->classifier_offset = positive_arm ? (int32_t)base : -(int32_t)base;
    plan->classifier_input = (u32)(0x00504d64U + plan->classifier_offset);
    plan->target = 0x0007f31cU;
    plan->classifier_table = 0x00072780U;
}
