/* Object lifecycle tail recovered from i960 0x23954-0x23978. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_geometry_object_lifecycle_plan {
    u32 state_18;
    u32 state_19_before;
    u32 state_19_after;
    u32 increments_state_19;
};

void recovered_geometry_object_lifecycle_plan(
    uint8_t state_18, uint8_t state_19,
    struct recovered_geometry_object_lifecycle_plan *plan)
{
    plan->state_18 = state_18;
    plan->state_19_before = state_19;
    plan->increments_state_19 = state_18 == 0U && state_19 <= 31U ? 1U : 0U;
    plan->state_19_after = state_19 + plan->increments_state_19;
}
