/* Selected-record packet prologue recovered from i960 0x7d7f4-0x7d914. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_selected_packet_builder_7d7f4_plan {
    u32 table_base;
    u32 record_stride;
    u32 selected_index;
    u32 record_offset;
    u32 first_field_offset;
    u32 metric_field_offset;
    u32 enabled_field_offset;
    u32 command_count;
    u32 command_ids[3];
    u32 fifo_target;
    u32 classifier_target;
    u32 result_table_base;
    u32 result_destination;
};

void recovered_state_selected_packet_builder_7d7f4(
    u32 selected_index,
    struct recovered_state_selected_packet_builder_7d7f4_plan *plan)
{
    plan->table_base = 0x00505060U;
    plan->record_stride = 6U;
    plan->selected_index = selected_index;
    plan->record_offset = selected_index * plan->record_stride;
    plan->first_field_offset = 0U;
    plan->metric_field_offset = 2U;
    plan->enabled_field_offset = 4U;
    plan->command_count = 3U;
    plan->command_ids[0] = 10U;
    plan->command_ids[1] = 29U;
    plan->command_ids[2] = 30U;
    plan->fifo_target = 0x00884000U;
    plan->classifier_target = 0x00073508U;
    plan->result_table_base = 0x00072630U;
    plan->result_destination = 0x00504d94U;
}
