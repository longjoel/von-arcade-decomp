/* Bounded result-prefix contract recovered from i960 0x72ea0. */

#include <stdint.h>

struct recovered_match_state_result_prefix_plan {
    uint32_t mode_global;
    uint32_t state_global;
    uint32_t input_port;
    uint32_t input_mask;
    uint32_t record_base;
    uint32_t record_stride;
    uint32_t record_byte_offsets[2];
    uint32_t result_addresses[2];
    uint32_t state_gate;
    uint32_t mode_gate;
    uint32_t emit_targets[2];
};

void recovered_match_state_result_prefix_plan(
    struct recovered_match_state_result_prefix_plan *plan)
{
    plan->mode_global = 0x00503a08U;
    plan->state_global = 0x005039f4U;
    plan->input_port = 0x01a14002U;
    plan->input_mask = 1U;
    plan->record_base = 0x005024f0U;
    plan->record_stride = 0x100U;
    plan->record_byte_offsets[0] = 0x514U;
    plan->record_byte_offsets[1] = 0x515U;
    plan->result_addresses[0] = 0x00504dacU;
    plan->result_addresses[1] = 0x00504db0U;
    plan->state_gate = 2U;
    plan->mode_gate = 4U;
    plan->emit_targets[0] = 0x000882a8U;
    plan->emit_targets[1] = 0x00088318U;
}

uint32_t recovered_match_state_result_record_offset(uint32_t input)
{
    return (input & 1U) * 0x100U;
}
