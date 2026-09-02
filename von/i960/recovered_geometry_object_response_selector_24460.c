/* Object response selector recovered from i960 0x24460-0x24540. */
#include <stdint.h>

typedef uint32_t u32;

enum recovered_geometry_object_selector_route {
    RECOVERED_GEOMETRY_OBJECT_SELECTOR_TABLE_DOUBLE = 0,
    RECOVERED_GEOMETRY_OBJECT_SELECTOR_TABLE_DIRECT = 1,
    RECOVERED_GEOMETRY_OBJECT_SELECTOR_TABLE_HALF = 2,
    RECOVERED_GEOMETRY_OBJECT_SELECTOR_FALLBACK_BIT_CLEAR = 3,
    RECOVERED_GEOMETRY_OBJECT_SELECTOR_FALLBACK_BIT_SET = 4,
    RECOVERED_GEOMETRY_OBJECT_SELECTOR_FALLBACK_FIXED = 5,
};

struct recovered_geometry_object_response_selector_plan {
    u32 table_address;
    u32 table_index;
    u32 selected_value;
    u32 fallback_pointer;
    u32 route;
};

void recovered_geometry_object_response_selector_plan(
    int16_t object_1d0, int16_t object_1d2, int16_t object_1d8,
    u32 state_5024e8, const u32 table[32],
    struct recovered_geometry_object_response_selector_plan *plan)
{
    int32_t d0 = (int32_t)object_1d0;
    int32_t d2 = (int32_t)object_1d2;
    int32_t d8 = (int32_t)object_1d8;
    u32 state = state_5024e8;
    u32 index;

    plan->table_address = 0x02be0088U;
    plan->fallback_pointer = 0U;

    /* cmpibg g5,g4: the first guard compares +0x1d2 against +0x1d0. */
    if (d2 > d0) {
        plan->fallback_pointer = (state & 1U) ?
            0x0049c980U : 0x0040002cU;
        plan->route = (state & 1U) ?
            RECOVERED_GEOMETRY_OBJECT_SELECTOR_FALLBACK_BIT_SET :
            RECOVERED_GEOMETRY_OBJECT_SELECTOR_FALLBACK_BIT_CLEAR;
        plan->table_index = 0U;
        plan->selected_value = plan->fallback_pointer;
        return;
    }

    /* cmpibge uses +0x1d0 >= the shifted/divided +0x1d8 value. */
    if (d0 < (d8 >> 2)) {
        index = (state << 1) & 31U;
        plan->route = RECOVERED_GEOMETRY_OBJECT_SELECTOR_TABLE_DOUBLE;
    } else if (d0 < (d8 / 3)) {
        index = state & 31U;
        plan->route = RECOVERED_GEOMETRY_OBJECT_SELECTOR_TABLE_DIRECT;
    } else if (d0 < (d8 >> 1)) {
        index = (state >> 1) & 31U;
        plan->route = RECOVERED_GEOMETRY_OBJECT_SELECTOR_TABLE_HALF;
    } else {
        plan->fallback_pointer = 0x0049c984U;
        plan->route = RECOVERED_GEOMETRY_OBJECT_SELECTOR_FALLBACK_FIXED;
        plan->table_index = 0U;
        plan->selected_value = plan->fallback_pointer;
        return;
    }

    plan->table_index = index;
    plan->selected_value = table[index];
}
