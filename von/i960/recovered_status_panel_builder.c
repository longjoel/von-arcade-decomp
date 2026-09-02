/* Two-block panel plan recovered from i960 0x1f4c0. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_status_panel_builder_plan {
    u32 first_source;
    u32 first_column;
    u32 first_row;
    u32 first_width;
    u32 first_height;
    u32 second_table_entry;
    u32 second_selector;
    u32 second_column;
    u32 second_row;
    u32 second_width;
    u32 second_height;
};

void recovered_status_panel_builder_plan(u32 input_pointer,
                                         struct recovered_status_panel_builder_plan *plan)
{
    u32 adjusted_pointer = input_pointer - 0xd0U;

    plan->first_source = 0x02fe01d4U;
    plan->first_column = 4U;
    plan->first_row = 10U;
    plan->first_width = 5U;
    plan->first_height = 5U;
    plan->second_selector = adjusted_pointer & 0xfU;
    plan->second_table_entry = 0x02ea2010U + (plan->second_selector << 2);
    plan->second_column = 28U;
    plan->second_row = 20U;
    plan->second_width = 8U;
    plan->second_height = 5U;
}
