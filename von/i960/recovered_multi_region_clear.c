/* Three-region clear sequence recovered from i960 0x1fe90. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_clear_region {
    u32 column;
    u32 row;
    u32 width;
    u32 height;
    u32 helper;
};

struct recovered_multi_region_clear_plan {
    struct recovered_clear_region first;
    struct recovered_clear_region second;
    struct recovered_clear_region third;
};

void recovered_multi_region_clear_plan(struct recovered_multi_region_clear_plan *plan)
{
    plan->first = (struct recovered_clear_region){4U, 10U, 33U, 8U, 0x1df00U};
    plan->second = (struct recovered_clear_region){22U, 10U, 38U, 8U, 0x1df00U};
    plan->third = (struct recovered_clear_region){20U, 10U, 24U, 8U, 0x1df00U};
}
