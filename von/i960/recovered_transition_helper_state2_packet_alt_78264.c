/* Alternate bit-15 state-2 packet and result publication at 0x78264. */

#include <stdint.h>

struct recovered_transition_helper_state2_packet_alt_78264_plan {
    uint32_t entry;
    uint32_t linked_object_offset;
    uint32_t fifo;
    uint32_t selector_first;
    uint32_t selector_second;
    uint32_t selector_final;
    uint32_t halfword_mask;
    uint32_t adjustment;
    uint32_t fixed_float;
    uint32_t response_first_register;
    uint32_t response_second_register;
    uint32_t object_x_offset;
    uint32_t object_y_offset;
    uint32_t classifier;
    uint32_t result_table;
    uint32_t continuation;
    uint32_t result_counter;
    uint32_t result_counter_destination;
    uint32_t result_destination;
    uint32_t return_address;
};

void recovered_transition_helper_state2_packet_alt_78264_plan(
    struct recovered_transition_helper_state2_packet_alt_78264_plan *plan)
{
    plan->entry = 0x00078264U;
    plan->linked_object_offset = 0x74U;
    plan->fifo = 0x00884000U;
    plan->selector_first = 29U;
    plan->selector_second = 30U;
    plan->selector_final = 10U;
    plan->halfword_mask = 0xffffU;
    plan->adjustment = UINT32_C(0xffffc000);
    plan->fixed_float = 0x43160000U;
    plan->response_first_register = 1U; /* g1 */
    plan->response_second_register = 5U; /* g5 */
    plan->object_x_offset = 0x10U;
    plan->object_y_offset = 0x8U;
    plan->classifier = 0x00073508U;
    plan->result_table = 0x00072960U;
    plan->continuation = 0x00078334U;
    plan->result_counter = 5U;
    plan->result_counter_destination = 0x00504db8U;
    plan->result_destination = 0x00504d94U;
    plan->return_address = 0x00078348U;
}

uint32_t recovered_transition_helper_state2_alt_adjust(uint32_t value)
{
    return (value - 0x4000U) & 0xffffU;
}
