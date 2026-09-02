/* Geometry response/state selector recovered from i960 0x23ef0-0x240dc. */
#include <stdint.h>

typedef uint32_t u32;

enum recovered_geometry_selector_route {
    RECOVERED_GEOMETRY_SELECTOR_TABLE_DOUBLE = 0,
    RECOVERED_GEOMETRY_SELECTOR_TABLE_DIRECT = 1,
    RECOVERED_GEOMETRY_SELECTOR_TABLE_HALF = 2,
    RECOVERED_GEOMETRY_SELECTOR_FALLBACK_BIT_CLEAR = 3,
    RECOVERED_GEOMETRY_SELECTOR_FALLBACK_BIT_SET = 4,
};

struct recovered_geometry_response_selector_plan {
    u32 fifo_read_address;
    u32 table_address;
    u32 table_index;
    u32 selected_value;
    u32 fallback_pointer;
    u32 route;
};

void recovered_geometry_response_selector_plan(
    int16_t state_ca0, int16_t state_ca2, int16_t state_ca8,
    u32 state_5024e8, const u32 table[32],
    struct recovered_geometry_response_selector_plan *plan)
{
    int32_t ca0 = (int32_t)state_ca0;
    int32_t ca2 = (int32_t)state_ca2;
    int32_t ca8 = (int32_t)state_ca8;
    u32 state = state_5024e8;
    u32 index;

    plan->fifo_read_address = 0x00884000U;
    plan->table_address = 0x02be0008U;
    plan->fallback_pointer = 0U;

    /* cmpibg g5,g4: the first guard compares +0x1ca2 against +0x1ca0. */
    if (ca2 > ca0) {
        plan->fallback_pointer = (state & 1U) ?
            0x0049c980U : 0x0040005cU;
        plan->route = (state & 1U) ?
            RECOVERED_GEOMETRY_SELECTOR_FALLBACK_BIT_SET :
            RECOVERED_GEOMETRY_SELECTOR_FALLBACK_BIT_CLEAR;
        plan->table_index = 0U;
        plan->selected_value = plan->fallback_pointer;
        return;
    }

    /* cmpibge uses +0x1ca0 >= the shifted/divided +0x1ca8 value. */
    if (ca0 < (ca8 >> 2)) {
        index = (state << 1) & 31U;
        plan->route = RECOVERED_GEOMETRY_SELECTOR_TABLE_DOUBLE;
    } else if (ca0 < (ca8 / 3)) {
        index = state & 31U;
        plan->route = RECOVERED_GEOMETRY_SELECTOR_TABLE_DIRECT;
    } else if (ca0 < (ca8 >> 1)) {
        index = (state >> 1) & 31U;
        plan->route = RECOVERED_GEOMETRY_SELECTOR_TABLE_HALF;
    } else {
        plan->fallback_pointer = 0x0049c980U;
        plan->route = RECOVERED_GEOMETRY_SELECTOR_FALLBACK_BIT_SET;
        plan->table_index = 0U;
        plan->selected_value = plan->fallback_pointer;
        return;
    }

    plan->table_index = index;
    plan->selected_value = table[index];
}
