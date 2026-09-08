/* Bounded compact result-phase selector at i960 0x75230. */

#include <stdint.h>

struct recovered_match_result_phase_selector_75230_plan {
    uint32_t phase_source_register;
    uint32_t required_phase;
    uint32_t global_gate;
    uint32_t status_input;
    uint32_t status_bit;
    uint32_t bit_set_status;
    uint32_t bit_set_helper;
    uint32_t bit_set_counter;
    uint32_t table;
    uint32_t table_count;
    uint32_t table_index_subtract;
    uint32_t table_lower_bound;
    uint32_t table_upper_bound;
    uint32_t status_destination;
    uint32_t counter_destination;
    uint32_t counter_base;
    uint32_t bypass_target;
    uint32_t bit_set_target;
};

void recovered_match_result_phase_selector_75230_plan(
    struct recovered_match_result_phase_selector_75230_plan *plan)
{
    plan->phase_source_register = 5U; /* r5 */
    plan->required_phase = 1U;
    plan->global_gate = 0x00504d9cU;
    plan->status_input = 0x00504e50U;
    plan->status_bit = 6U;
    plan->bit_set_status = 7U;
    plan->bit_set_helper = 0x00079d60U;
    plan->bit_set_counter = 30U;
    plan->table = 0x00075294U;
    plan->table_count = 12U;
    plan->table_index_subtract = 8U;
    plan->table_lower_bound = 5U;
    plan->table_upper_bound = 11U;
    plan->status_destination = 0x00504d94U;
    plan->counter_destination = 0x00504db8U;
    plan->counter_base = 31U;
    plan->bypass_target = 0x00075300U;
    plan->bit_set_target = 0x00075300U;
}

uint32_t recovered_match_result_phase_table_value(uint32_t index)
{
    static const uint32_t values[12] = { 4U, 6U, 1U, 6U, 5U, 5U,
                                          5U, 5U, 5U, 5U, 6U, 5U };
    return index < 12U ? values[index] : 0U;
}

uint32_t recovered_match_result_phase_counter(uint32_t selector)
{
    return selector + 31U;
}
