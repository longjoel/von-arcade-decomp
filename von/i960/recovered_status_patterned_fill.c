/* Alternate fill and generator update recovered from i960 0x22840-0x228ec. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_status_patterned_fill_plan {
    u32 fill_selected;
    u32 destination;
    u32 repetition_count;
    u32 fill_repetitions_per_group;
    u32 solid_repetitions_per_group;
    u32 fill_value;
    u32 solid_value;
    u32 state_504d28_after;
    u32 state_504d2a_after;
};

void recovered_status_patterned_fill_plan(
    u32 phase, u32 start_row, u32 state_504d28, u32 state_504d2a,
    u32 generator, u32 fill_value,
    struct recovered_status_patterned_fill_plan *plan)
{
    plan->fill_selected = phase % 192U != 0U && start_row <= 1U ? 1U : 0U;
    plan->destination = 0x0100d000U + start_row * 2U;
    plan->repetition_count = 192U;
    plan->fill_repetitions_per_group = 4U;
    plan->solid_repetitions_per_group = 4U;
    plan->fill_value = fill_value;
    plan->solid_value = 0xffffU;
    plan->state_504d28_after =
        (state_504d28 + (generator & 0x1ffU)) & 0x1ffU;
    plan->state_504d2a_after =
        (generator - state_504d2a) & 0x1ffU;
}
