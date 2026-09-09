/* Fixed-point diagnostic packet prefix recovered from i960 0x8f824-0x8f910. */
#include "recovered_common.h"

struct recovered_geometry_diagnostic_math_8f810_plan {
    recovered_u32 source_halfword, normalized_source;
    recovered_u32 initial_word, response_word, computed_word;
    recovered_u32 fifo_word[15], fifo_count, frame_readback;
};

void recovered_geometry_diagnostic_math_8f810(
    int32_t source_halfword, recovered_u32 response_word,
    recovered_u32 computed_word, recovered_u32 frame_readback,
    struct recovered_geometry_diagnostic_math_8f810_plan *plan)
{
    int32_t normalized = source_halfword - 0x253;

    plan->source_halfword = (recovered_u32)source_halfword;
    plan->normalized_source = (recovered_u32)normalized & 0x1ffU;
    plan->initial_word = plan->normalized_source << 7;
    plan->response_word = response_word;
    plan->computed_word = computed_word;
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 27U;
    plan->fifo_word[2] = plan->initial_word;
    plan->fifo_word[3] = 27U;
    plan->fifo_word[4] = plan->initial_word;
    plan->fifo_word[5] = 18U;
    plan->fifo_word[6] = 0U;
    plan->fifo_word[7] = computed_word;
    plan->fifo_word[8] = 0U;
    plan->fifo_word[9] = 18U;
    plan->fifo_word[10] = 0U;
    plan->fifo_word[11] = 0xbf800000U;
    plan->fifo_word[12] = 0U;
    plan->fifo_word[13] = 58U; /* 31 + 27 */
    plan->fifo_word[14] = frame_readback;
    plan->fifo_count = 15U;
    plan->frame_readback = frame_readback;
}

struct recovered_geometry_diagnostic_math_packet_8f928_plan {
    recovered_u32 fifo_word[9], fifo_count;
    recovered_u32 computed_word, frame_readback;
};

void recovered_geometry_diagnostic_math_packet_8f928(
    recovered_u32 computed_word, recovered_u32 frame_readback,
    struct recovered_geometry_diagnostic_math_packet_8f928_plan *plan)
{
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 44U; /* 31 + 13 */
    plan->fifo_word[2] = 0xbfe820c5U;
    plan->fifo_word[3] = 0x4189f8a1U;
    plan->fifo_word[4] = 0x3f6c7e28U;
    plan->fifo_word[5] = 0x3c0fU;
    plan->fifo_word[6] = 0xdfc5U;
    plan->fifo_word[7] = computed_word;
    plan->fifo_word[8] = frame_readback;
    plan->fifo_count = 9U;
    plan->computed_word = computed_word;
    plan->frame_readback = frame_readback;
}

struct recovered_geometry_diagnostic_math_window_8f9d0_plan {
    recovered_u32 state_word, window_word[4];
    recovered_u32 control_address, control_value, completion_word, call_target;
};

void recovered_geometry_diagnostic_math_window_8f9d0(
    recovered_u32 state_word, recovered_u32 frame_word_3,
    struct recovered_geometry_diagnostic_math_window_8f9d0_plan *plan)
{
    plan->state_word = state_word;
    plan->window_word[0] = state_word == 0U ? 0x12a7eeU : 0x12b8fcU;
    plan->window_word[1] = state_word == 0U ? 0x12a80eU : 0x5a36f2U;
    plan->window_word[2] = state_word == 0U ? 0xa8b135U : 0xa8c5fcU;
    plan->window_word[3] = state_word == 0U ? 0U : frame_word_3;
    plan->control_address = 0x800010U;
    plan->control_value = 0x101U;
    plan->completion_word = 6U;
    plan->call_target = 0x6fec0U;
}

struct recovered_geometry_diagnostic_math_post_service_plan {
    recovered_u32 fifo_word[10], fifo_count;
    recovered_u32 masked_word_0, masked_word_1, masked_word_2, frame_readback;
};

void recovered_geometry_diagnostic_math_post_service_8fa78(
    recovered_u32 payload_word_0, recovered_u32 payload_word_1,
    recovered_u32 payload_word_2, recovered_u32 raw_word_0,
    recovered_u32 raw_word_1, recovered_u32 raw_word_2,
    recovered_u32 frame_readback,
    struct recovered_geometry_diagnostic_math_post_service_plan *plan)
{
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 44U; /* 31 + 13 */
    plan->fifo_word[2] = payload_word_0;
    plan->fifo_word[3] = payload_word_1;
    plan->fifo_word[4] = payload_word_2;
    plan->fifo_word[5] = raw_word_0 & 0xffffU;
    plan->fifo_word[6] = raw_word_1 & 0xffffU;
    plan->fifo_word[7] = raw_word_2 & 0xffffU;
    plan->fifo_word[8] = 58U; /* 31 + 27 */
    plan->fifo_word[9] = frame_readback;
    plan->fifo_count = 10U;
    plan->masked_word_0 = raw_word_0 & 0xffffU;
    plan->masked_word_1 = raw_word_1 & 0xffffU;
    plan->masked_word_2 = raw_word_2 & 0xffffU;
    plan->frame_readback = frame_readback;
}

struct recovered_geometry_diagnostic_math_setup_8fbf4_plan {
    recovered_u32 fifo_word[8], fifo_count, frame_word;
};

void recovered_geometry_diagnostic_math_setup_8fbf4(
    recovered_u32 frame_word,
    struct recovered_geometry_diagnostic_math_setup_8fbf4_plan *plan)
{
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 44U; /* 31 + 13 */
    plan->fifo_word[2] = frame_word;
    plan->fifo_word[3] = 0x419993a9U;
    plan->fifo_word[4] = 0xbdb39c0fU;
    plan->fifo_word[5] = 0xf099U;
    plan->fifo_word[6] = frame_word;
    plan->fifo_word[7] = frame_word;
    plan->fifo_count = 8U;
    plan->frame_word = frame_word;
}

struct recovered_geometry_diagnostic_math_second_plan {
    recovered_u32 source_halfword, normalized_source, initial_word;
    recovered_u32 response_word, computed_word;
    recovered_u32 fifo_word[13], fifo_count, frame_readback;
};

void recovered_geometry_diagnostic_math_second_8fc54(
    int32_t source_halfword, recovered_u32 response_word,
    recovered_u32 computed_word, recovered_u32 frame_readback,
    struct recovered_geometry_diagnostic_math_second_plan *plan)
{
    int32_t normalized = source_halfword - 0x253;

    plan->source_halfword = (recovered_u32)source_halfword;
    plan->normalized_source = (recovered_u32)normalized & 0x1ffU;
    plan->initial_word = plan->normalized_source << 7;
    plan->response_word = response_word;
    plan->computed_word = computed_word;
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 18U;
    plan->fifo_word[2] = 0xbf800000U;
    plan->fifo_word[3] = 0x40000000U;
    plan->fifo_word[4] = 0xbe800000U;
    plan->fifo_word[5] = 27U;
    plan->fifo_word[6] = plan->initial_word;
    plan->fifo_word[7] = 27U;
    plan->fifo_word[8] = plan->initial_word;
    plan->fifo_word[9] = 20U;
    plan->fifo_word[10] = computed_word;
    plan->fifo_word[11] = 58U; /* 31 + 27 */
    plan->fifo_word[12] = frame_readback;
    plan->fifo_count = 13U;
    plan->frame_readback = frame_readback;
}

struct recovered_geometry_diagnostic_math_second_window_plan {
    recovered_u32 state_word, window_word[4];
    recovered_u32 control_address, control_value, next_target;
};

void recovered_geometry_diagnostic_math_second_window_8fd64(
    recovered_u32 state_word, recovered_u32 frame_word_3,
    struct recovered_geometry_diagnostic_math_second_window_plan *plan)
{
    plan->state_word = state_word;
    plan->window_word[0] = 0x12d368U;
    plan->window_word[1] = state_word == 0U ? 0x12d3b0U : 0x5a3a32U;
    plan->window_word[2] = 0xa8e799U;
    plan->window_word[3] = frame_word_3;
    plan->control_address = 0x800010U;
    plan->control_value = 0x101U;
    plan->next_target = 0x8fddcU;
}

struct recovered_geometry_diagnostic_math_terminal_plan {
    recovered_u32 source_halfword, normalized_source, initial_word;
    recovered_u32 computed_word, frame_readback;
    recovered_u32 fifo_word[14], fifo_count;
};

void recovered_geometry_diagnostic_math_terminal_8fdf0(
    int32_t source_halfword, recovered_u32 computed_word,
    recovered_u32 frame_readback,
    struct recovered_geometry_diagnostic_math_terminal_plan *plan)
{
    int32_t normalized = source_halfword - 0x253;

    plan->source_halfword = (recovered_u32)source_halfword;
    plan->normalized_source = (recovered_u32)normalized & 0x1ffU;
    plan->initial_word = plan->normalized_source << 7;
    plan->computed_word = computed_word;
    plan->frame_readback = frame_readback;
    plan->fifo_word[0] = 6U;
    plan->fifo_word[1] = 5U;
    plan->fifo_word[2] = 18U;
    plan->fifo_word[3] = 0xbf800000U;
    plan->fifo_word[4] = 0x40000000U;
    plan->fifo_word[5] = 0xbe800000U;
    plan->fifo_word[6] = 27U;
    plan->fifo_word[7] = plan->initial_word;
    plan->fifo_word[8] = 27U;
    plan->fifo_word[9] = plan->initial_word;
    plan->fifo_word[10] = 20U;
    plan->fifo_word[11] = computed_word;
    plan->fifo_word[12] = 58U; /* 31 + 27 */
    plan->fifo_word[13] = frame_readback;
    plan->fifo_count = 14U;
}

struct recovered_geometry_diagnostic_math_third_window_plan {
    recovered_u32 state_word, window_word[4];
    recovered_u32 control_address, control_value, publish_address;
    recovered_u32 completion_word;
};

void recovered_geometry_diagnostic_math_third_window_8ff00(
    recovered_u32 state_word, recovered_u32 frame_word_3,
    struct recovered_geometry_diagnostic_math_third_window_plan *plan)
{
    plan->state_word = state_word;
    plan->window_word[0] = 0x12d3b4U;
    plan->window_word[1] = state_word == 0U ? 0x12d3fcU : 0x5a3a36U;
    plan->window_word[2] = 0xa8e818U;
    plan->window_word[3] = state_word == 0U ? 0U : frame_word_3;
    plan->control_address = 0x800010U;
    plan->control_value = 0x101U;
    plan->publish_address = 0x804000U;
    plan->completion_word = 6U;
}

struct recovered_geometry_diagnostic_math_third_setup_plan {
    recovered_u32 fifo_word[8], fifo_count, frame_word;
};

void recovered_geometry_diagnostic_math_third_setup_8ff98(
    recovered_u32 frame_word,
    struct recovered_geometry_diagnostic_math_third_setup_plan *plan)
{
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 44U; /* 31 + 13 */
    plan->fifo_word[2] = frame_word;
    plan->fifo_word[3] = 0x415c7ae1U;
    plan->fifo_word[4] = 0xbfe66666U;
    plan->fifo_word[5] = 0x71U;
    plan->fifo_word[6] = frame_word;
    plan->fifo_word[7] = frame_word;
    plan->fifo_count = 8U;
    plan->frame_word = frame_word;
}

struct recovered_geometry_diagnostic_math_third_plan {
    recovered_u32 source_halfword, normalized_source, initial_word;
    recovered_u32 response_word, computed_word;
    recovered_u32 fifo_word[15], fifo_count, frame_readback;
};

void recovered_geometry_diagnostic_math_third_8fff4(
    int32_t source_halfword, recovered_u32 response_word,
    recovered_u32 computed_word, recovered_u32 frame_readback,
    struct recovered_geometry_diagnostic_math_third_plan *plan)
{
    int32_t normalized = source_halfword - 0x253;

    plan->source_halfword = (recovered_u32)source_halfword;
    plan->normalized_source = (recovered_u32)normalized & 0x1ffU;
    plan->initial_word = plan->normalized_source << 7;
    plan->response_word = response_word;
    plan->computed_word = computed_word;
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 18U;
    plan->fifo_word[2] = 0xbf000000U;
    plan->fifo_word[3] = 0x3f800000U;
    plan->fifo_word[4] = 0xbfa66666U;
    plan->fifo_word[5] = 21U;
    plan->fifo_word[6] = 0xfffff800U;
    plan->fifo_word[7] = 27U;
    plan->fifo_word[8] = plan->initial_word;
    plan->fifo_word[9] = 27U;
    plan->fifo_word[10] = plan->initial_word;
    plan->fifo_word[11] = 20U;
    plan->fifo_word[12] = computed_word;
    plan->fifo_word[13] = 58U; /* 31 + 27 */
    plan->fifo_word[14] = frame_readback;
    plan->fifo_count = 15U;
    plan->frame_readback = frame_readback;
}

struct recovered_geometry_diagnostic_math_third_window_90124_plan {
    recovered_u32 state_word, window_word[4];
    recovered_u32 control_address, control_value, publish_address;
    recovered_u32 completion_word, call_target;
};

void recovered_geometry_diagnostic_math_third_window_90124(
    recovered_u32 state_word, recovered_u32 frame_word_3,
    struct recovered_geometry_diagnostic_math_third_window_90124_plan *plan)
{
    plan->state_word = state_word;
    plan->window_word[0] = 0x12d400U;
    plan->window_word[1] = state_word == 0U ? 0x12d464U : 0x5a3a3aU;
    plan->window_word[2] = 0xa8e897U;
    plan->window_word[3] = frame_word_3;
    plan->control_address = 0x800010U;
    plan->control_value = 0x101U;
    plan->publish_address = 0x804000U;
    plan->completion_word = 6U;
    plan->call_target = 0x6fec0U;
}

struct recovered_geometry_diagnostic_math_record_packet_90398_plan {
    recovered_u32 fifo_word[10], fifo_count;
    recovered_u32 masked_word_0, masked_word_1, masked_word_2, frame_readback;
};

void recovered_geometry_diagnostic_math_record_packet_90398(
    recovered_u32 record_word, recovered_u32 payload_word_0,
    recovered_u32 payload_word_1, recovered_u32 raw_word_0,
    recovered_u32 raw_word_1, recovered_u32 raw_word_2,
    recovered_u32 frame_readback,
    struct recovered_geometry_diagnostic_math_record_packet_90398_plan *plan)
{
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 44U; /* 31 + 13 */
    plan->fifo_word[2] = record_word;
    plan->fifo_word[3] = payload_word_0;
    plan->fifo_word[4] = payload_word_1;
    plan->fifo_word[5] = raw_word_0 & 0xffffU;
    plan->fifo_word[6] = raw_word_1 & 0xffffU;
    plan->fifo_word[7] = raw_word_2 & 0xffffU;
    plan->fifo_word[8] = 58U; /* 31 + 27 */
    plan->fifo_word[9] = frame_readback;
    plan->fifo_count = 10U;
    plan->masked_word_0 = raw_word_0 & 0xffffU;
    plan->masked_word_1 = raw_word_1 & 0xffffU;
    plan->masked_word_2 = raw_word_2 & 0xffffU;
    plan->frame_readback = frame_readback;
}

struct recovered_geometry_diagnostic_math_record_window_9044c_plan {
    recovered_u32 state_word, window_word[4];
    recovered_u32 zero_word[3], nonzero_word[3];
    recovered_u32 control_address, control_value, publish_address;
};

void recovered_geometry_diagnostic_math_record_window_9044c(
    recovered_u32 state_word, const recovered_u32 zero_word[3],
    const recovered_u32 nonzero_word[3], recovered_u32 frame_word,
    struct recovered_geometry_diagnostic_math_record_window_9044c_plan *plan)
{
    plan->state_word = state_word;
    for (unsigned i = 0; i < 3; ++i) {
        plan->zero_word[i] = zero_word[i];
        plan->nonzero_word[i] = nonzero_word[i];
        plan->window_word[i] = state_word == 0U ? zero_word[i] : nonzero_word[i];
    }
    plan->window_word[3] = state_word == 0U ? 0U : frame_word;
    plan->control_address = 0x800010U;
    plan->control_value = 0x101U;
    plan->publish_address = 0x804000U;
}

struct recovered_geometry_diagnostic_math_record_loop_904f4_plan {
    recovered_u32 primary_start, auxiliary_start, primary_end, auxiliary_end;
    recovered_u32 stride, iterations, completion_count, return_address;
};

void recovered_geometry_diagnostic_math_record_loop_904f4(
    recovered_u32 primary_start, recovered_u32 auxiliary_start,
    recovered_u32 primary_limit,
    struct recovered_geometry_diagnostic_math_record_loop_904f4_plan *plan)
{
    recovered_u32 primary = primary_start;
    recovered_u32 auxiliary = auxiliary_start;
    recovered_u32 iterations = 0U;

    do {
        ++iterations;
        primary += 0x2cU;
        auxiliary += 0x2cU;
    } while (primary <= primary_limit);

    plan->primary_start = primary_start;
    plan->auxiliary_start = auxiliary_start;
    plan->primary_end = primary;
    plan->auxiliary_end = auxiliary;
    plan->stride = 0x2cU;
    plan->iterations = iterations;
    plan->completion_count = iterations + 1U;
    plan->return_address = 0x9052cU;
}
