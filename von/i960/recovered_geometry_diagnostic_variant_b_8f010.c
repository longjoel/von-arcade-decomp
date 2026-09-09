/* Diagnostic geometry packet prefix recovered from i960 0x8f010-0x8f0f8. */
#include "recovered_common.h"

struct recovered_geometry_diagnostic_variant_b_8f010_input {
    recovered_u32 record_word, payload_word_0, payload_word_1;
    recovered_u32 raw_word_0, raw_word_1, raw_word_2, frame_readback;
};

struct recovered_geometry_diagnostic_variant_b_8f010_plan {
    recovered_u32 fifo_word[15], fifo_count;
    recovered_u32 masked_word_0, masked_word_1, masked_word_2;
};

void recovered_geometry_diagnostic_variant_b_8f010(
    const struct recovered_geometry_diagnostic_variant_b_8f010_input *input,
    struct recovered_geometry_diagnostic_variant_b_8f010_plan *plan)
{
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 19U;
    plan->fifo_word[2] = 0x40000000U;
    plan->fifo_word[3] = 0x40000000U;
    plan->fifo_word[4] = 0x40000000U;
    plan->fifo_word[5] = 5U;
    plan->fifo_word[6] = 44U; /* 31 + 13 */
    plan->fifo_word[7] = input->record_word;
    plan->fifo_word[8] = input->payload_word_0;
    plan->fifo_word[9] = input->payload_word_1;
    plan->fifo_word[10] = input->raw_word_0 & 0xffffU;
    plan->fifo_word[11] = input->raw_word_1 & 0xffffU;
    plan->fifo_word[12] = input->raw_word_2 & 0xffffU;
    plan->fifo_word[13] = 58U; /* 31 + 27 */
    plan->fifo_word[14] = input->frame_readback;
    plan->fifo_count = 15U;
    plan->masked_word_0 = input->raw_word_0 & 0xffffU;
    plan->masked_word_1 = input->raw_word_1 & 0xffffU;
    plan->masked_word_2 = input->raw_word_2 & 0xffffU;
}

void recovered_geometry_diagnostic_variant_c_8f1f0(
    const struct recovered_geometry_diagnostic_variant_b_8f010_input *input,
    struct recovered_geometry_diagnostic_variant_b_8f010_plan *plan)
{
    /* 0x8f1f0 has the same FIFO shape; only its record-base constants differ. */
    recovered_geometry_diagnostic_variant_b_8f010(input, plan);
}

void recovered_geometry_diagnostic_variant_d_8f620(
    const struct recovered_geometry_diagnostic_variant_b_8f010_input *input,
    struct recovered_geometry_diagnostic_variant_b_8f010_plan *plan)
{
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 19U;
    plan->fifo_word[2] = 0x3fd9999aU;
    plan->fifo_word[3] = 0x3fd9999aU;
    plan->fifo_word[4] = 0x3fd9999aU;
    plan->fifo_word[5] = 5U;
    plan->fifo_word[6] = 44U; /* 31 + 13 */
    plan->fifo_word[7] = input->record_word;
    plan->fifo_word[8] = input->payload_word_0;
    plan->fifo_word[9] = input->payload_word_1;
    plan->fifo_word[10] = input->raw_word_0 & 0xffffU;
    plan->fifo_word[11] = input->raw_word_1 & 0xffffU;
    plan->fifo_word[12] = input->raw_word_2 & 0xffffU;
    plan->fifo_word[13] = 58U; /* 31 + 27 */
    plan->fifo_word[14] = input->frame_readback;
    plan->fifo_count = 15U;
    plan->masked_word_0 = input->raw_word_0 & 0xffffU;
    plan->masked_word_1 = input->raw_word_1 & 0xffffU;
    plan->masked_word_2 = input->raw_word_2 & 0xffffU;
}

struct recovered_geometry_diagnostic_variant_d_window_plan {
    recovered_u32 state_word, window_word[4];
    recovered_u32 control_address, control_value, next_target;
};

void recovered_geometry_diagnostic_variant_d_window_8f730(
    recovered_u32 state_word, const recovered_u32 zero_window[3],
    const recovered_u32 nonzero_window[3], recovered_u32 frame_word_3,
    struct recovered_geometry_diagnostic_variant_d_window_plan *plan)
{
    const recovered_u32 *selected = state_word == 0U ? zero_window : nonzero_window;

    plan->state_word = state_word;
    plan->window_word[0] = selected[0];
    plan->window_word[1] = selected[1];
    plan->window_word[2] = selected[2];
    plan->window_word[3] = state_word == 0U ? 0U : frame_word_3;
    plan->control_address = 0x800010U;
    plan->control_value = 0x101U;
    plan->next_target = 0x8f7d4U;
}

struct recovered_geometry_diagnostic_variant_d_loop_plan {
    recovered_u32 current_record_pointer, current_aux_pointer;
    recovered_u32 next_record_pointer, next_aux_pointer, record_endpoint;
    recovered_u32 next_record_stride, loop_continues, terminal_completion;
};

void recovered_geometry_diagnostic_variant_d_loop_8f7d4(
    recovered_u32 current_record_pointer, recovered_u32 current_aux_pointer,
    struct recovered_geometry_diagnostic_variant_d_loop_plan *plan)
{
    plan->current_record_pointer = current_record_pointer;
    plan->current_aux_pointer = current_aux_pointer;
    plan->next_record_stride = 0x2cU;
    plan->next_record_pointer = current_record_pointer + 0x2cU;
    plan->next_aux_pointer = current_aux_pointer + 0x2cU;
    plan->record_endpoint = 0x142b94U;
    plan->loop_continues = plan->next_record_pointer <= plan->record_endpoint ? 1U : 0U;
    plan->terminal_completion = plan->loop_continues == 0U ? 6U : 0U;
}

struct recovered_geometry_diagnostic_variant_b_loop_plan {
    recovered_u32 state_word, window_word[4];
    recovered_u32 control_address, control_value;
    recovered_u32 next_record_pointer, record_endpoint, next_aux_pointer;
    recovered_u32 next_record_stride, loop_continues, terminal_completion;
};

void recovered_geometry_diagnostic_variant_b_loop_8f120(
    recovered_u32 state_word, const recovered_u32 zero_window[3],
    const recovered_u32 nonzero_window[3], recovered_u32 frame_word_3,
    recovered_u32 current_record_pointer, recovered_u32 current_aux_pointer,
    struct recovered_geometry_diagnostic_variant_b_loop_plan *plan)
{
    const recovered_u32 *selected = state_word == 0U ? zero_window : nonzero_window;

    plan->state_word = state_word;
    plan->window_word[0] = selected[0];
    plan->window_word[1] = selected[1];
    plan->window_word[2] = selected[2];
    plan->window_word[3] = state_word == 0U ? 0U : frame_word_3;
    plan->control_address = 0x800010U;
    plan->control_value = 0x101U;
    plan->next_record_stride = 0x2cU;
    plan->next_record_pointer = current_record_pointer + plan->next_record_stride;
    plan->next_aux_pointer = current_aux_pointer + plan->next_record_stride;
    plan->record_endpoint = 0x14250cU;
    plan->loop_continues = plan->next_record_pointer <= plan->record_endpoint ? 1U : 0U;
    plan->terminal_completion = plan->loop_continues == 0U ? 6U : 0U;
}

struct recovered_geometry_diagnostic_variant_c_packet_8f3cc_plan {
    recovered_u32 fifo_word[9], fifo_count, frame_word, frame_readback;
};

void recovered_geometry_diagnostic_variant_c_packet_8f3cc(
    recovered_u32 frame_word, recovered_u32 frame_readback,
    struct recovered_geometry_diagnostic_variant_c_packet_8f3cc_plan *plan)
{
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 18U;
    plan->fifo_word[2] = frame_word;
    plan->fifo_word[3] = 0x418edaeeU;
    plan->fifo_word[4] = 0xbed6a162U;
    plan->fifo_word[5] = 20U;
    plan->fifo_word[6] = 0x441U;
    plan->fifo_word[7] = 44U; /* 31 + 13 */
    plan->fifo_word[8] = frame_readback;
    plan->fifo_count = 9U;
    plan->frame_word = frame_word;
    plan->frame_readback = frame_readback;
}

struct recovered_geometry_diagnostic_variant_c_window_8f458_plan {
    recovered_u32 state_word, window_word[4];
    recovered_u32 control_address, control_value, next_target;
};

void recovered_geometry_diagnostic_variant_c_window_8f458(
    recovered_u32 state_word, recovered_u32 frame_word_3,
    struct recovered_geometry_diagnostic_variant_c_window_8f458_plan *plan)
{
    plan->state_word = state_word;
    plan->window_word[0] = 0xed0baU;
    plan->window_word[1] = state_word == 0U ? 0xed378U : 0x599a7aU;
    plan->window_word[2] = 0xa466a5U;
    plan->window_word[3] = state_word == 0U ? 0U : frame_word_3;
    plan->control_address = 0x800010U;
    plan->control_value = 0x101U;
    plan->next_target = 0x8f4d0U;
}

struct recovered_geometry_diagnostic_variant_c_fixed_plan {
    recovered_u32 fifo_word[11], fifo_count, frame_readback;
};

void recovered_geometry_diagnostic_variant_c_fixed_8f4d0(
    recovered_u32 frame_word, recovered_u32 frame_readback,
    struct recovered_geometry_diagnostic_variant_c_fixed_plan *plan)
{
    plan->fifo_word[0] = 6U;
    plan->fifo_word[1] = 5U;
    plan->fifo_word[2] = 44U; /* 31 + 13 */
    plan->fifo_word[3] = 0x4019999aU;
    plan->fifo_word[4] = frame_word;
    plan->fifo_word[5] = 0x3f333333U;
    plan->fifo_word[6] = 0x11eU;
    plan->fifo_word[7] = 0xf8ceU;
    plan->fifo_word[8] = 0xfccfU;
    plan->fifo_word[9] = 44U; /* 31 + 13 */
    plan->fifo_word[10] = frame_readback;
    plan->fifo_count = 11U;
    plan->frame_readback = frame_readback;
}

struct recovered_geometry_diagnostic_variant_c_final_plan {
    recovered_u32 state_word, window_word[4];
    recovered_u32 control_address, control_value, completion_word[2];
};

void recovered_geometry_diagnostic_variant_c_final_8f57c(
    recovered_u32 state_word, recovered_u32 frame_word_3,
    struct recovered_geometry_diagnostic_variant_c_final_plan *plan)
{
    plan->state_word = state_word;
    plan->window_word[0] = 0x402f58U;
    plan->window_word[1] = state_word == 0U ? 0x403138U : 0x5afddaU;
    plan->window_word[2] = 0x84f601U;
    plan->window_word[3] = frame_word_3;
    plan->control_address = 0x800010U;
    plan->control_value = 0x101U;
    plan->completion_word[0] = 6U;
    plan->completion_word[1] = 6U;
}

void recovered_geometry_diagnostic_variant_e_90540(
    const struct recovered_geometry_diagnostic_variant_b_8f010_input *input,
    struct recovered_geometry_diagnostic_variant_b_8f010_plan *plan)
{
    /* 0x90540 uses the same 5/19/44/58 framing as variant B. */
    recovered_geometry_diagnostic_variant_b_8f010(input, plan);
}

struct recovered_geometry_diagnostic_variant_e_loop_plan {
    recovered_u32 current_record_pointer, current_aux_pointer;
    recovered_u32 next_record_pointer, next_aux_pointer, record_endpoint;
    recovered_u32 next_record_stride, loop_continues, completion_word;
};

void recovered_geometry_diagnostic_variant_e_loop_90590(
    recovered_u32 current_record_pointer, recovered_u32 current_aux_pointer,
    struct recovered_geometry_diagnostic_variant_e_loop_plan *plan)
{
    plan->current_record_pointer = current_record_pointer;
    plan->current_aux_pointer = current_aux_pointer;
    plan->next_record_stride = 0x2cU;
    plan->next_record_pointer = current_record_pointer + 0x2cU;
    plan->next_aux_pointer = current_aux_pointer + 0x2cU;
    plan->record_endpoint = 0x1427a0U;
    plan->loop_continues = plan->next_record_pointer <= plan->record_endpoint ? 1U : 0U;
    plan->completion_word = 6U;
}

struct recovered_geometry_diagnostic_variant_e_packet_9070c_plan {
    recovered_u32 fifo_word[7], fifo_count, frame_word, frame_readback;
};

void recovered_geometry_diagnostic_variant_e_packet_9070c(
    recovered_u32 frame_word, recovered_u32 frame_readback,
    struct recovered_geometry_diagnostic_variant_e_packet_9070c_plan *plan)
{
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 18U;
    plan->fifo_word[2] = frame_word;
    plan->fifo_word[3] = 0x4187f454U;
    plan->fifo_word[4] = 0x3f0346dcU;
    plan->fifo_word[5] = 58U; /* 31 + 27 */
    plan->fifo_word[6] = frame_readback;
    plan->fifo_count = 7U;
    plan->frame_word = frame_word;
    plan->frame_readback = frame_readback;
}

struct recovered_geometry_diagnostic_variant_e_window_plan {
    recovered_u32 state_word, window_word[4];
    recovered_u32 control_address, control_value, completion_word[2], return_address;
};

void recovered_geometry_diagnostic_variant_e_window_90788(
    recovered_u32 state_word, recovered_u32 frame_word_3,
    struct recovered_geometry_diagnostic_variant_e_window_plan *plan)
{
    plan->state_word = state_word;
    plan->window_word[0] = 0x4029f4U;
    plan->window_word[1] = state_word == 0U ? 0x402e34U : 0x5afcbeU;
    plan->window_word[2] = 0x84f00dU;
    plan->window_word[3] = state_word == 0U ? 0U : frame_word_3;
    plan->control_address = 0x800010U;
    plan->control_value = 0x101U;
    plan->completion_word[0] = 6U;
    plan->completion_word[1] = 6U;
    plan->return_address = 0x9089cU;
}

struct recovered_geometry_diagnostic_variant_f_packet_908a0_plan {
    recovered_u32 record_word, payload_word_0, payload_word_1;
    recovered_u32 raw_word_0, raw_word_1, raw_word_2;
    recovered_u32 masked_word_0, masked_word_1, masked_word_2;
    recovered_u32 fifo_word[14], fifo_count;
};

void recovered_geometry_diagnostic_variant_f_packet_908a0(
    recovered_u32 record_word, recovered_u32 payload_word_0,
    recovered_u32 payload_word_1, recovered_u32 raw_word_0,
    recovered_u32 raw_word_1, recovered_u32 raw_word_2,
    struct recovered_geometry_diagnostic_variant_f_packet_908a0_plan *plan)
{
    plan->record_word = record_word;
    plan->payload_word_0 = payload_word_0;
    plan->payload_word_1 = payload_word_1;
    plan->raw_word_0 = raw_word_0;
    plan->raw_word_1 = raw_word_1;
    plan->raw_word_2 = raw_word_2;
    plan->masked_word_0 = raw_word_0 & 0xffffU;
    plan->masked_word_1 = raw_word_1 & 0xffffU;
    plan->masked_word_2 = raw_word_2 & 0xffffU;
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 19U;
    plan->fifo_word[2] = 0x40000000U;
    plan->fifo_word[3] = 0x40000000U;
    plan->fifo_word[4] = 0x40000000U;
    plan->fifo_word[5] = 5U;
    plan->fifo_word[6] = 44U; /* 31 + 13 */
    plan->fifo_word[7] = record_word;
    plan->fifo_word[8] = payload_word_0;
    plan->fifo_word[9] = payload_word_1;
    plan->fifo_word[10] = plan->masked_word_0;
    plan->fifo_word[11] = plan->masked_word_1;
    plan->fifo_word[12] = plan->masked_word_2;
    plan->fifo_word[13] = 58U; /* 31 + 27 */
    plan->fifo_count = 14U;
}

struct recovered_geometry_diagnostic_variant_f_window_90994_plan {
    recovered_u32 state_word, window_word[4];
    recovered_u32 control_address, control_value, publish_address;
};

void recovered_geometry_diagnostic_variant_f_window_90994(
    recovered_u32 state_word, const recovered_u32 zero_window[3],
    const recovered_u32 nonzero_window[3],
    struct recovered_geometry_diagnostic_variant_f_window_90994_plan *plan)
{
    const recovered_u32 *selected = state_word == 0U ? zero_window : nonzero_window;
    plan->state_word = state_word;
    for (unsigned i = 0; i < 3; ++i)
        plan->window_word[i] = selected[i];
    plan->window_word[3] = 0U;
    plan->control_address = 0x800010U;
    plan->control_value = state_word;
    plan->publish_address = 0x804000U;
}

struct recovered_geometry_diagnostic_variant_f_loop_90a58_plan {
    recovered_u32 current_record_pointer, current_aux_pointer;
    recovered_u32 next_record_pointer, next_aux_pointer, record_endpoint;
    recovered_u32 next_record_stride, loop_continues, completion_word;
};

void recovered_geometry_diagnostic_variant_f_loop_90a58(
    recovered_u32 current_record_pointer, recovered_u32 current_aux_pointer,
    struct recovered_geometry_diagnostic_variant_f_loop_90a58_plan *plan)
{
    plan->current_record_pointer = current_record_pointer;
    plan->current_aux_pointer = current_aux_pointer;
    plan->next_record_stride = 0x2cU;
    plan->next_record_pointer = current_record_pointer + 0x2cU;
    plan->next_aux_pointer = current_aux_pointer + 0x2cU;
    plan->record_endpoint = 0x142dd0U;
    plan->loop_continues = plan->next_record_pointer <= plan->record_endpoint ? 1U : 0U;
    plan->completion_word = 6U;
}

struct recovered_geometry_diagnostic_variant_g_packet_90a7c_plan {
    recovered_u32 input_word, fifo_word[6], fifo_count;
};

void recovered_geometry_diagnostic_variant_g_packet_90a7c(
    recovered_u32 input_word,
    struct recovered_geometry_diagnostic_variant_g_packet_90a7c_plan *plan)
{
    plan->input_word = input_word;
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 18U;
    plan->fifo_word[2] = input_word;
    plan->fifo_word[3] = 0x41900000U;
    plan->fifo_word[4] = 0xbf800000U;
    plan->fifo_word[5] = 58U; /* 31 + 27 */
    plan->fifo_count = 6U;
}

struct recovered_geometry_diagnostic_variant_g_window_90af8_plan {
    recovered_u32 state_word, mode_word, frame_word, window_word[4];
    recovered_u32 control_address, control_value, publish_address;
    recovered_u32 completion_word[2];
};

void recovered_geometry_diagnostic_variant_g_window_90af8(
    recovered_u32 state_word, recovered_u32 mode_word, recovered_u32 frame_word,
    const recovered_u32 state_zero_mode_zero[3],
    const recovered_u32 state_nonzero_mode_zero[3],
    const recovered_u32 state_zero_mode_nonzero[3],
    const recovered_u32 state_nonzero_mode_nonzero[3],
    struct recovered_geometry_diagnostic_variant_g_window_90af8_plan *plan)
{
    const recovered_u32 *selected;
    if (state_word == 0U)
        selected = mode_word == 0U ? state_zero_mode_zero : state_zero_mode_nonzero;
    else
        selected = mode_word == 0U ? state_nonzero_mode_zero : state_nonzero_mode_nonzero;
    plan->state_word = state_word;
    plan->mode_word = mode_word;
    plan->frame_word = frame_word;
    for (unsigned i = 0; i < 3; ++i)
        plan->window_word[i] = selected[i];
    plan->window_word[3] = mode_word == 0U ? 0U : frame_word;
    plan->control_address = 0x800010U;
    plan->control_value = 0x101U;
    plan->publish_address = 0x804000U;
    plan->completion_word[0] = 6U;
    plan->completion_word[1] = 6U;
}
