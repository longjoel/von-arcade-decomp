/* Bounded phase-advance prefix and terminal publication at 0x75300. */

#include <stdint.h>

struct recovered_match_phase_advance_update_75300_plan {
    uint32_t phase_source_register;
    uint32_t zero_phase_target;
    uint32_t phase_index_source;
    uint32_t phase_limit_table;
    uint32_t phase_index_destination;
    uint32_t phase_increment;
    uint32_t coordinate_source;
    uint32_t positive_coordinate_offset;
    uint32_t negative_coordinate_offset;
    uint32_t classifier;
    uint32_t result_table;
    uint32_t result_destination;
    uint32_t state_helper;
    uint32_t returned_state_destination;
    uint32_t phase_state_destination;
    uint32_t terminal_counter_destination;
    uint32_t terminal_counter;
    uint32_t return_address;
};

void recovered_match_phase_advance_update_75300_plan(
    struct recovered_match_phase_advance_update_75300_plan *plan)
{
    plan->phase_source_register = 5U; /* r5 */
    plan->zero_phase_target = 0x0007539cU;
    plan->phase_index_source = 0x00504d74U;
    plan->phase_limit_table = 0x00504de0U;
    plan->phase_index_destination = 0x00504d74U;
    plan->phase_increment = 1U;
    plan->coordinate_source = 0x00504d64U;
    plan->positive_coordinate_offset = 0x1800U;
    plan->negative_coordinate_offset = UINT32_C(0xffffe800);
    plan->classifier = 0x00073508U;
    plan->result_table = 0x00072780U;
    plan->result_destination = 0x00504d94U;
    plan->state_helper = 0x00079050U;
    plan->returned_state_destination = 0x00504db4U;
    plan->phase_state_destination = 0x00504d74U;
    plan->terminal_counter_destination = 0x00504db8U;
    plan->terminal_counter = 30U;
    plan->return_address = 0x00075398U;
}

uint32_t recovered_match_phase_index_increment(uint32_t index)
{
    return index + 1U;
}

uint32_t recovered_match_phase_coordinate_offset(int32_t direction)
{
    return direction >= 0 ? 0x1800U : UINT32_C(0xffffe800);
}
