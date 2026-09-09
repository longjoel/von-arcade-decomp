/* Diagnostic geometry packet prefix recovered from i960 0x8e4b0-0x8e590. */
#include "recovered_common.h"

struct recovered_geometry_diagnostic_packet_8e4a0_input {
    recovered_u32 seed_word, payload_word_1, payload_word_2;
    recovered_u32 masked_word_a, masked_word_b, masked_word_c;
    recovered_u32 frame_readback;
};

struct recovered_geometry_diagnostic_packet_8e4a0_plan {
    recovered_u32 fifo_word[16];
    recovered_u32 fifo_count;
    recovered_u32 control_value;
    recovered_u32 masked_word_a, masked_word_b, masked_word_c;
};

void recovered_geometry_diagnostic_packet_8e4a0(
    const struct recovered_geometry_diagnostic_packet_8e4a0_input *input,
    struct recovered_geometry_diagnostic_packet_8e4a0_plan *plan)
{
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 19U;
    plan->fifo_word[2] = 0x40000000U;
    plan->fifo_word[3] = 0x40000000U;
    plan->fifo_word[4] = 0x40000000U;
    plan->fifo_word[5] = 5U;
    plan->fifo_word[6] = 46U; /* 31 + 15 */
    plan->fifo_word[7] = input->seed_word;
    plan->fifo_word[8] = input->payload_word_1;
    plan->fifo_word[9] = input->payload_word_2;
    plan->fifo_word[10] = input->masked_word_a & 0xffffU;
    plan->fifo_word[11] = input->masked_word_b & 0xffffU;
    plan->fifo_word[12] = 46U; /* 31 + 27 */
    plan->fifo_word[13] = input->masked_word_c & 0xffffU;
    plan->fifo_word[14] = 46U; /* 31 + 27 */
    plan->fifo_word[15] = input->frame_readback;
    plan->fifo_count = 16U;
    plan->control_value = 0x101U;
    plan->masked_word_a = input->masked_word_a & 0xffffU;
    plan->masked_word_b = input->masked_word_b & 0xffffU;
    plan->masked_word_c = input->masked_word_c & 0xffffU;
}

struct recovered_geometry_diagnostic_window_8e5b4_plan {
    recovered_u32 selected_response;
    recovered_u32 window_word[4];
    recovered_u32 control_address, control_value;
    recovered_u32 completion_word;
    recovered_u32 next_record_stride;
    recovered_u32 next_record_pointer, record_endpoint;
    recovered_u32 loop_continues;
};

void recovered_geometry_diagnostic_window_8e5b4(
    recovered_u32 response_word,
    const recovered_u32 zero_response_window[3],
    const recovered_u32 nonzero_response_window[3],
    recovered_u32 current_record_pointer, recovered_u32 record_endpoint,
    struct recovered_geometry_diagnostic_window_8e5b4_plan *plan)
{
    const recovered_u32 *selected = response_word == 0U ?
        zero_response_window : nonzero_response_window;
    plan->selected_response = response_word;
    plan->window_word[0] = selected[0];
    plan->window_word[1] = selected[1];
    plan->window_word[2] = selected[2];
    plan->window_word[3] = 0U;
    plan->control_address = 0x800010U;
    plan->control_value = 0x101U;
    plan->completion_word = 6U;
    plan->next_record_stride = 0x2cU; /* pointer advances at 0x8e658/674 */
    plan->next_record_pointer = current_record_pointer + plan->next_record_stride;
    plan->record_endpoint = record_endpoint;
    plan->loop_continues = plan->next_record_pointer <= record_endpoint ? 1U : 0U;
}

struct recovered_geometry_diagnostic_terminal_8e67c_plan {
    recovered_u32 fifo_word[7];
    recovered_u32 fifo_count;
    recovered_u32 frame_readback;
};

void recovered_geometry_diagnostic_terminal_8e67c(
    recovered_u32 frame_readback,
    struct recovered_geometry_diagnostic_terminal_8e67c_plan *plan)
{
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 18U;
    plan->fifo_word[2] = 0xc0789518U;
    plan->fifo_word[3] = 0x4192b46eU;
    plan->fifo_word[4] = 0x80000000U;
    plan->fifo_word[5] = 46U; /* 31 + 15 */
    plan->fifo_word[6] = frame_readback;
    plan->fifo_count = 7U;
    plan->frame_readback = frame_readback;
}

struct recovered_geometry_diagnostic_route_8e6f8_plan {
    recovered_u32 state_word, response_word;
    recovered_u32 next_target;
};

void recovered_geometry_diagnostic_route_8e6f8(
    recovered_u32 state_word, recovered_u32 response_word,
    struct recovered_geometry_diagnostic_route_8e6f8_plan *plan)
{
    plan->state_word = state_word;
    plan->response_word = response_word;
    if (state_word == 0U)
        plan->next_target = 0x8e774U;
    else if (response_word == 0U)
        plan->next_target = 0x8e704U;
    else
        plan->next_target = 0x8e738U;
}

struct recovered_geometry_diagnostic_route_packet_plan {
    recovered_u32 window_word[4];
    recovered_u32 control_address, control_value;
    recovered_u32 next_target;
};

void recovered_geometry_diagnostic_route_packet_8e704(
    struct recovered_geometry_diagnostic_route_packet_plan *plan)
{
    plan->window_word[0] = 0x400de4U;
    plan->window_word[1] = 0x400ea4U;
    plan->window_word[2] = 0x84cf72U;
    plan->window_word[3] = 0U;
    plan->control_address = 0x800010U;
    plan->control_value = 0x101U;
    plan->next_target = 0x8e7f4U;
}

void recovered_geometry_diagnostic_route_packet_8e738(
    recovered_u32 frame_word_3,
    struct recovered_geometry_diagnostic_route_packet_plan *plan)
{
    plan->window_word[0] = 0x400de4U;
    plan->window_word[1] = 0x5af93aU;
    plan->window_word[2] = 0x84cf72U;
    plan->window_word[3] = frame_word_3;
    plan->control_address = 0x800010U;
    plan->control_value = 0x101U;
    plan->next_target = 0x8e7ecU;
}

struct recovered_geometry_diagnostic_zero_state_plan {
    recovered_u32 response_word, frame_base_offset;
    recovered_u32 frame_word[4];
    recovered_u32 control_address, control_value, next_target;
};

void recovered_geometry_diagnostic_zero_state_8e774(
    recovered_u32 response_word, recovered_u32 frame_word_3,
    struct recovered_geometry_diagnostic_zero_state_plan *plan)
{
    plan->response_word = response_word;
    plan->frame_base_offset = response_word == 0U ? 0x50U : 0x60U;
    plan->frame_word[0] = 0x9aee8U;
    plan->frame_word[1] = response_word == 0U ? 0x9afa8U : 0x58f6eaU;
    plan->frame_word[2] = 0x9e35b7U;
    plan->frame_word[3] = frame_word_3;
    plan->control_address = 0x800010U;
    plan->control_value = 0x101U;
    plan->next_target = 0x8e7ecU;
}

struct recovered_geometry_diagnostic_mod_gate_8e7f4_plan {
    recovered_u32 counter, modulus, remainder;
    recovered_u32 completion_word, next_target;
};

void recovered_geometry_diagnostic_mod_gate_8e7f4(
    recovered_u32 counter,
    struct recovered_geometry_diagnostic_mod_gate_8e7f4_plan *plan)
{
    plan->counter = counter;
    plan->modulus = 0x168U;
    plan->remainder = counter % plan->modulus;
    plan->completion_word = 6U;
    plan->next_target = plan->remainder <= 19U ? 0x8e818U : 0x8e834U;
}

struct recovered_geometry_diagnostic_table_select_plan {
    recovered_u32 remainder, state_word;
    recovered_u32 table_base, table_index, selected_table_address;
};

void recovered_geometry_diagnostic_table_select_8e818(
    recovered_u32 remainder, recovered_u32 state_word,
    struct recovered_geometry_diagnostic_table_select_plan *plan)
{
    recovered_u32 base;

    plan->remainder = remainder;
    plan->state_word = state_word;
    plan->table_index = 0U;
    if (remainder <= 19U) {
        base = 0x2be4d10U;
        if (state_word == 0U)
            base -= 0x5a60U;
    } else if (remainder <= 139U) {
        plan->table_index = (remainder - 20U) >> 1;
        base = state_word == 0U ? 0x2be4770U : 0x2be4d10U;
    } else if (remainder <= 239U) {
        base = 0x2be4fd4U;
        if (state_word == 0U)
            base -= 0x5a60U;
    } else {
        plan->table_index = (0x167U - remainder) >> 1;
        base = state_word == 0U ? 0x2be4d10U : 0x2be4770U;
    }
    plan->table_base = base;
    plan->selected_table_address = base + plan->table_index * 4U;
}

struct recovered_geometry_diagnostic_converged_plan {
    recovered_u32 fifo_word[10], fifo_count;
    recovered_u32 table_word_0, table_word_1, table_word_2;
    recovered_u32 frame_word_3, frame_readback;
    recovered_u32 initial_window_word[4];
    recovered_u32 window_word[4];
    recovered_u32 final_window_word_3;
    recovered_u32 control_address, control_value, completion_word;
};

void recovered_geometry_diagnostic_converged_8e8f4(
    recovered_u32 table_word_0, recovered_u32 table_word_1,
    recovered_u32 table_word_2, recovered_u32 frame_word_3,
    recovered_u32 frame_readback,
    struct recovered_geometry_diagnostic_converged_plan *plan)
{
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 44U; /* 31 + 13 */
    plan->fifo_word[2] = 0x4071ff2eU;
    plan->fifo_word[3] = 0x41417c85U;
    plan->fifo_word[4] = 0x3fae1134U;
    plan->fifo_word[5] = 0x1588U;
    plan->fifo_word[6] = frame_word_3;
    plan->fifo_word[7] = 0xfff8U;
    plan->fifo_word[8] = 46U; /* 31 + 15 */
    plan->fifo_word[9] = frame_readback;
    plan->fifo_count = 10U;
    plan->table_word_0 = table_word_0;
    plan->table_word_1 = table_word_1;
    plan->table_word_2 = table_word_2;
    plan->frame_word_3 = frame_word_3;
    plan->frame_readback = frame_readback;
    plan->initial_window_word[0] = table_word_0;
    plan->initial_window_word[1] = table_word_1;
    plan->initial_window_word[2] = table_word_2;
    plan->initial_window_word[3] = frame_word_3;
    plan->window_word[0] = table_word_0;
    plan->window_word[1] = table_word_1;
    plan->window_word[2] = table_word_2;
    plan->window_word[3] = frame_word_3;
    plan->final_window_word_3 = frame_word_3;
    plan->control_address = 0x800010U;
    plan->control_value = 0x101U;
    plan->completion_word = 6U;
}
