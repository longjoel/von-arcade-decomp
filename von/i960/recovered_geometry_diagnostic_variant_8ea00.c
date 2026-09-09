/* Diagnostic geometry packet prefix recovered from i960 0x8ea00-0x8eaf4. */
#include "recovered_common.h"

struct recovered_geometry_diagnostic_variant_8ea00_input {
    recovered_u32 record_word;
    recovered_u32 raw_word_0, raw_word_1, raw_word_2;
    recovered_u32 raw_word_3, raw_word_4;
    recovered_u32 frame_readback;
};

struct recovered_geometry_diagnostic_variant_8ea00_plan {
    recovered_u32 fifo_word[16], fifo_count;
    recovered_u32 masked_word_0, masked_word_1, masked_word_2;
    recovered_u32 control_value;
};

void recovered_geometry_diagnostic_variant_8ea00(
    const struct recovered_geometry_diagnostic_variant_8ea00_input *input,
    struct recovered_geometry_diagnostic_variant_8ea00_plan *plan)
{
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 19U;
    plan->fifo_word[2] = 0x40000000U;
    plan->fifo_word[3] = 0x40000000U;
    plan->fifo_word[4] = 0x40000000U;
    plan->fifo_word[5] = 5U;
    plan->fifo_word[6] = 44U; /* 31 + 13 */
    plan->fifo_word[7] = input->record_word;
    plan->fifo_word[8] = input->raw_word_3;
    plan->fifo_word[9] = input->raw_word_4;
    plan->fifo_word[10] = input->raw_word_0 & 0xffffU;
    plan->fifo_word[11] = input->raw_word_1 & 0xffffU;
    plan->fifo_word[12] = 44U; /* 31 + 13 */
    plan->fifo_word[13] = input->raw_word_2 & 0xffffU;
    plan->fifo_word[14] = 44U; /* 31 + 13 */
    plan->fifo_word[15] = input->frame_readback;
    plan->fifo_count = 16U;
    plan->masked_word_0 = input->raw_word_0 & 0xffffU;
    plan->masked_word_1 = input->raw_word_1 & 0xffffU;
    plan->masked_word_2 = input->raw_word_2 & 0xffffU;
    plan->control_value = 0x101U;
}

struct recovered_geometry_diagnostic_variant_window_plan {
    recovered_u32 state_word, window_word[4];
    recovered_u32 control_address, control_value, next_target;
};

void recovered_geometry_diagnostic_variant_window_8ec84(
    recovered_u32 state_word, recovered_u32 frame_word_3,
    struct recovered_geometry_diagnostic_variant_window_plan *plan)
{
    plan->state_word = state_word;
    plan->window_word[0] = 0x403800U;
    plan->window_word[1] = state_word == 0U ? 0x403930U : 0x5afedeU;
    plan->window_word[2] = 0x8500a2U;
    plan->window_word[3] = state_word == 0U ? 0U : frame_word_3;
    plan->control_address = 0x800010U;
    plan->control_value = 0x101U;
    plan->next_target = 0x8ed7cU;
}

void recovered_geometry_diagnostic_variant_window_8ee14(
    recovered_u32 state_word, recovered_u32 frame_word_3,
    struct recovered_geometry_diagnostic_variant_window_plan *plan)
{
    recovered_geometry_diagnostic_variant_window_8ec84(state_word,
                                                        frame_word_3, plan);
    plan->next_target = 0x8eeb4U;
}

struct recovered_geometry_diagnostic_variant_fixed_plan {
    recovered_u32 fifo_word[11], fifo_count, frame_readback;
};

void recovered_geometry_diagnostic_variant_fixed_8ed7c(
    recovered_u32 frame_readback,
    struct recovered_geometry_diagnostic_variant_fixed_plan *plan)
{
    plan->fifo_word[0] = 6U;
    plan->fifo_word[1] = 5U;
    plan->fifo_word[2] = 44U; /* 31 + 13 */
    plan->fifo_word[3] = 0x40c01a37U;
    plan->fifo_word[4] = 0x413672b0U;
    plan->fifo_word[5] = 0x3f3a9931U;
    plan->fifo_word[6] = 0x3511U;
    plan->fifo_word[7] = 0x1084U;
    plan->fifo_word[8] = 0xf3e7U;
    plan->fifo_word[9] = 44U; /* 31 + 13 */
    plan->fifo_word[10] = frame_readback;
    plan->fifo_count = 11U;
    plan->frame_readback = frame_readback;
}

void recovered_geometry_diagnostic_variant_fixed_8eeb4(
    recovered_u32 frame_readback,
    struct recovered_geometry_diagnostic_variant_fixed_plan *plan)
{
    recovered_geometry_diagnostic_variant_fixed_8ed7c(frame_readback, plan);
    plan->fifo_word[3] = 0xc0c01a37U;
    plan->fifo_word[7] = 0xef7cU;
    plan->fifo_word[8] = 0xc19U;
}

struct recovered_geometry_diagnostic_variant_final_plan {
    recovered_u32 state_word, window_word[4];
    recovered_u32 control_address, control_value, completion_word[2];
};

void recovered_geometry_diagnostic_variant_final_8ef48(
    recovered_u32 state_word, recovered_u32 frame_word_3,
    struct recovered_geometry_diagnostic_variant_final_plan *plan)
{
    plan->state_word = state_word;
    plan->window_word[0] = 0x45e76cU;
    plan->window_word[1] = state_word == 0U ? 0x45ec4cU : 0x5baf2aU;
    plan->window_word[2] = 0x8b518aU;
    plan->window_word[3] = frame_word_3;
    plan->control_address = 0x800010U;
    plan->control_value = 0x101U;
    plan->completion_word[0] = 6U;
    plan->completion_word[1] = 6U;
}
