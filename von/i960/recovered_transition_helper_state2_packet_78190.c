/* Bounded state-2 FIFO packet contract from transition helper 0x78190. */

#include <stdint.h>

struct recovered_transition_helper_state2_packet_78190_plan {
    uint32_t linked_object_offset;
    uint32_t object_x_offset;
    uint32_t object_y_offset;
    uint32_t fifo;
    uint32_t selector_first;
    uint32_t selector_second;
    uint32_t selector_delta;
    uint32_t halfword_mask;
    uint32_t positive_adjustment;
    uint32_t negative_adjustment;
    uint32_t fixed_float;
    uint32_t response_first_register;
    uint32_t response_second_register;
    uint32_t board_x_offset;
    uint32_t board_y_offset;
    uint32_t selector_final;
    uint32_t classifier;
    uint32_t result_table;
    uint32_t positive_branch;
    uint32_t negative_branch;
    uint32_t continuation;
};

void recovered_transition_helper_state2_packet_78190_plan(
    struct recovered_transition_helper_state2_packet_78190_plan *plan)
{
    plan->linked_object_offset = 0x74U;
    plan->object_x_offset = 0x184U;
    plan->object_y_offset = 0x8U;
    plan->fifo = 0x00884000U;
    plan->selector_first = 29U;
    plan->selector_second = 30U;
    plan->selector_delta = 10U;
    plan->halfword_mask = 0xffffU;
    plan->positive_adjustment = 0x4000U;
    plan->negative_adjustment = UINT32_C(0xffffc000);
    plan->fixed_float = 0x43160000U;
    plan->response_first_register = 1U; /* g1 */
    plan->response_second_register = 5U; /* g5 */
    plan->board_x_offset = 0x10U;
    plan->board_y_offset = 0x8U;
    plan->selector_final = 10U;
    plan->classifier = 0x00073508U;
    plan->result_table = 0x00072930U;
    plan->positive_branch = 0x00078190U;
    plan->negative_branch = 0x00078264U;
    plan->continuation = 0x00078334U;
}

uint32_t recovered_transition_helper_state2_adjust(uint32_t value,
                                                   int32_t adjustment)
{
    return (value + (uint32_t)adjustment) & 0xffffU;
}
