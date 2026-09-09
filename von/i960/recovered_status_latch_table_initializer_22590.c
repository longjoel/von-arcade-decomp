/* Two-table initializer recovered from i960 0x22590-0x2266c. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_status_latch_table_initializer_plan {
    u32 input_bit0;
    u32 fallback_first;
    u32 fallback_second;
    u32 g14_value;
    u32 first_destination;
    u32 second_destination;
    u32 first_source;
    u32 second_source;
    u32 destination_stride;
    u32 source_stride;
    u32 entry_count;
    u32 counter_address;
    u32 counter_before;
    u32 counter_after;
};

void recovered_status_latch_table_initializer_plan(
    u32 input_bit0, u32 g14_value, u32 counter_before,
    struct recovered_status_latch_table_initializer_plan *plan)
{
    plan->input_bit0 = input_bit0 & 1U;
    plan->fallback_first = 0x000001dfU;
    plan->fallback_second = 0x00007fe0U;
    plan->g14_value = g14_value;
    plan->first_destination = 0x0051a0c0U;
    plan->second_destination = 0x0051a190U;
    plan->first_source = 0x0180099cU;
    plan->second_source = 0x0180099eU;
    plan->destination_stride = 8U;
    plan->source_stride = 0x20U;
    plan->entry_count = 25U;
    plan->counter_address = 0x00504d10U;
    plan->counter_before = counter_before;
    plan->counter_after = counter_before + 1U;
}
