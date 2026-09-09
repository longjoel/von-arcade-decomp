/* Geometry packets recovered from the 0x936f0 service continuation. */
#include "recovered_common.h"

#define GEOMETRY_01F 0x3dcccccdU

struct recovered_geometry_packet_93700_plan {
    recovered_u32 input_word[3], tail_word, frame_readback;
    recovered_u32 fifo_word[11], fifo_count;
};

void recovered_geometry_packet_93700(
    const recovered_u32 input_word[3], recovered_u32 tail_word,
    recovered_u32 frame_readback,
    struct recovered_geometry_packet_93700_plan *plan)
{
    for (unsigned i = 0; i < 3; ++i)
        plan->input_word[i] = input_word[i];
    plan->tail_word = tail_word;
    plan->frame_readback = frame_readback;
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 18U;
    plan->fifo_word[2] = input_word[0];
    plan->fifo_word[3] = input_word[1];
    plan->fifo_word[4] = input_word[2];
    plan->fifo_word[5] = 19U;
    plan->fifo_word[6] = GEOMETRY_01F;
    plan->fifo_word[7] = GEOMETRY_01F;
    plan->fifo_word[8] = GEOMETRY_01F;
    plan->fifo_word[9] = tail_word;
    plan->fifo_word[10] = frame_readback;
    plan->fifo_count = 11U;
}

struct recovered_geometry_packet_937ec_plan {
    recovered_u32 input_word[3], fill_word, tail_word, frame_readback;
    recovered_u32 fifo_word[12], fifo_count;
};

void recovered_geometry_packet_937ec(
    const recovered_u32 input_word[3], recovered_u32 fill_word,
    recovered_u32 tail_word, recovered_u32 frame_readback,
    struct recovered_geometry_packet_937ec_plan *plan)
{
    for (unsigned i = 0; i < 3; ++i)
        plan->input_word[i] = input_word[i];
    plan->fill_word = fill_word;
    plan->tail_word = tail_word;
    plan->frame_readback = frame_readback;
    plan->fifo_word[0] = 6U;
    plan->fifo_word[1] = 5U;
    plan->fifo_word[2] = 18U;
    plan->fifo_word[3] = input_word[0];
    plan->fifo_word[4] = input_word[1];
    plan->fifo_word[5] = input_word[2];
    plan->fifo_word[6] = 19U;
    plan->fifo_word[7] = fill_word;
    plan->fifo_word[8] = fill_word;
    plan->fifo_word[9] = fill_word;
    plan->fifo_word[10] = tail_word;
    plan->fifo_word[11] = frame_readback;
    plan->fifo_count = 12U;
}

struct recovered_geometry_window_93700_plan {
    recovered_u32 window_word[4], control_address, control_value;
    recovered_u32 publish_address, completion_word;
};

void recovered_geometry_window_93700(
    struct recovered_geometry_window_93700_plan *plan)
{
    plan->window_word[0] = 0x400cecU;
    plan->window_word[1] = 0x400d1cU;
    plan->window_word[2] = 0x84ce4fU;
    plan->window_word[3] = 0U;
    plan->control_address = 0x800010U;
    plan->control_value = 0x101U;
    plan->publish_address = 0x804000U;
    plan->completion_word = 6U;
}

struct recovered_geometry_packet_938d0_plan {
    recovered_u32 computed_word[2], input_word, masked_word;
    recovered_u32 context_word, tail_word, frame_readback;
    recovered_u32 fifo_word[11], fifo_count;
};

void recovered_geometry_packet_938d0(
    recovered_u32 computed_word_0, recovered_u32 computed_word_1,
    recovered_u32 input_word, recovered_u32 masked_word,
    recovered_u32 context_word, recovered_u32 tail_word,
    recovered_u32 frame_readback,
    struct recovered_geometry_packet_938d0_plan *plan)
{
    plan->computed_word[0] = computed_word_0;
    plan->computed_word[1] = computed_word_1;
    plan->input_word = input_word;
    plan->masked_word = masked_word;
    plan->context_word = context_word;
    plan->tail_word = tail_word;
    plan->frame_readback = frame_readback;
    plan->fifo_word[0] = 6U;
    plan->fifo_word[1] = 5U;
    plan->fifo_word[2] = 44U;
    plan->fifo_word[3] = computed_word_0;
    plan->fifo_word[4] = computed_word_1;
    plan->fifo_word[5] = input_word;
    plan->fifo_word[6] = masked_word;
    plan->fifo_word[7] = masked_word;
    plan->fifo_word[8] = context_word;
    plan->fifo_word[9] = tail_word;
    plan->fifo_word[10] = frame_readback;
    plan->fifo_count = 11U;
}

struct recovered_geometry_window_93964_plan {
    recovered_u32 window_word[4], control_address, control_value;
    recovered_u32 publish_address, completion_word;
};

void recovered_geometry_window_93964(
    recovered_u32 predicate_zero, recovered_u32 context_word,
    struct recovered_geometry_window_93964_plan *plan)
{
    plan->window_word[0] = 0xcb094U;
    plan->window_word[1] = predicate_zero ? 0xcb120U : 0x59598eU;
    plan->window_word[2] = 0xa1cc84U;
    plan->window_word[3] = predicate_zero ? 0U : context_word;
    plan->control_address = 0x800010U;
    plan->control_value = 0x101U;
    plan->publish_address = 0x804000U;
    plan->completion_word = 6U;
}

struct recovered_geometry_packet_93a1c_plan {
    recovered_u32 computed_word[3], context_word, frame_readback;
    recovered_u32 fifo_word[12], fifo_count;
};

void recovered_geometry_packet_93a1c(
    const recovered_u32 computed_word[3], recovered_u32 context_word,
    recovered_u32 frame_readback,
    struct recovered_geometry_packet_93a1c_plan *plan)
{
    for (unsigned i = 0; i < 3; ++i)
        plan->computed_word[i] = computed_word[i];
    plan->context_word = context_word;
    plan->frame_readback = frame_readback;
    plan->fifo_word[0] = 6U;
    plan->fifo_word[1] = 5U;
    plan->fifo_word[2] = 44U;
    plan->fifo_word[3] = computed_word[0];
    plan->fifo_word[4] = computed_word[1];
    plan->fifo_word[5] = computed_word[2];
    plan->fifo_word[6] = computed_word[2];
    plan->fifo_word[7] = 0x6080U;
    plan->fifo_word[8] = 0x3c80U;
    plan->fifo_word[9] = context_word;
    plan->fifo_word[10] = 58U; /* addo 31,27 */
    plan->fifo_word[11] = frame_readback;
    plan->fifo_count = 12U;
}

struct recovered_geometry_packet_93dec_plan {
    recovered_u32 input_word, masked_word, tail_word, frame_readback;
    recovered_u32 fifo_word[5], fifo_count;
};

void recovered_geometry_packet_93dec(
    recovered_u32 input_word, recovered_u32 tail_word,
    recovered_u32 frame_readback,
    struct recovered_geometry_packet_93dec_plan *plan)
{
    plan->input_word = input_word;
    plan->masked_word = 0x8000U;
    plan->tail_word = tail_word;
    plan->frame_readback = frame_readback;
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 21U;
    plan->fifo_word[2] = plan->masked_word;
    plan->fifo_word[3] = tail_word;
    plan->fifo_word[4] = frame_readback;
    plan->fifo_count = 5U;
}

struct recovered_geometry_packet_93e54_plan {
    recovered_u32 input_word[3], fifo_word[7], fifo_count;
    recovered_u32 helper_target, helper_base[2], helper_offset[2], helper_third;
};

void recovered_geometry_packet_93e54(
    const recovered_u32 input_word[3], const recovered_u32 address_word[3],
    recovered_u32 third_argument,
    struct recovered_geometry_packet_93e54_plan *plan)
{
    for (unsigned i = 0; i < 3; ++i) {
        plan->input_word[i] = input_word[i];
        plan->fifo_word[2 + i] = input_word[i] + address_word[i];
    }
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 18U;
    plan->fifo_word[5] = 21U;
    plan->fifo_word[6] = 0xc000U;
    plan->fifo_count = 7U;
    plan->helper_target = 0x8e310U;
    plan->helper_base[0] = 0x2b4613aU;
    plan->helper_base[1] = 0x2b4613aU;
    plan->helper_offset[0] = 0x9cb7aU;
    plan->helper_offset[1] = 0x9cbf2U;
    plan->helper_third = third_argument;
}

/* The 0x94d90 service reaches the same packet/tail shape after its
 * threshold table has selected the three address adjustments and r8 value. */
void recovered_geometry_packet_94d90(
    const recovered_u32 input_word[3], const recovered_u32 address_word[3],
    recovered_u32 third_argument,
    struct recovered_geometry_packet_93e54_plan *plan)
{
    recovered_geometry_packet_93e54(input_word, address_word, third_argument,
                                    plan);
}

void recovered_geometry_packet_callsite_99198(
    const recovered_u32 address_word[3], recovered_u32 third_argument,
    struct recovered_geometry_packet_93e54_plan *plan)
{
    static const recovered_u32 input_word[3] = {
        0x41766666U, 0x41bf3333U, 0xc0fccccdU
    };
    recovered_geometry_packet_94d90(input_word, address_word, third_argument,
                                    plan);
}

struct recovered_geometry_packet_93edc_plan {
    recovered_u32 input_word[3], tail_word, frame_readback;
    recovered_u32 fifo_word[10], fifo_count;
};

void recovered_geometry_packet_93edc(
    const recovered_u32 input_word[3], recovered_u32 tail_word,
    recovered_u32 frame_readback,
    struct recovered_geometry_packet_93edc_plan *plan)
{
    for (unsigned i = 0; i < 3; ++i)
        plan->input_word[i] = input_word[i];
    plan->tail_word = tail_word;
    plan->frame_readback = frame_readback;
    plan->fifo_word[0] = 6U;
    plan->fifo_word[1] = 5U;
    plan->fifo_word[2] = 18U;
    plan->fifo_word[3] = input_word[0];
    plan->fifo_word[4] = input_word[1];
    plan->fifo_word[5] = input_word[2];
    plan->fifo_word[6] = 21U;
    plan->fifo_word[7] = 0xc000U;
    plan->fifo_word[8] = tail_word;
    plan->fifo_word[9] = frame_readback;
    plan->fifo_count = 10U;
}

struct recovered_geometry_window_93f8c_plan {
    recovered_u32 window_word[4], control_address, control_value;
    recovered_u32 publish_address, completion_word;
};

void recovered_geometry_window_93f8c(
    struct recovered_geometry_window_93f8c_plan *plan)
{
    plan->window_word[0] = 0x403968U;
    plan->window_word[1] = 0x4039f0U;
    plan->window_word[2] = 0x850225U;
    plan->window_word[3] = 0U;
    plan->control_address = 0x800010U;
    plan->control_value = 0x101U;
    plan->publish_address = 0x804000U;
    plan->completion_word = 6U;
}

struct recovered_geometry_packet_93fe4_plan {
    recovered_u32 computed_word[2], mask_word, xor_source[2], auxiliary_word;
    recovered_u32 fifo_word[16], fifo_count;
};

void recovered_geometry_packet_93fe4(
    recovered_u32 computed_word_1, recovered_u32 computed_word_0,
    recovered_u32 mask_word, const recovered_u32 xor_source[2],
    recovered_u32 auxiliary_word,
    struct recovered_geometry_packet_93fe4_plan *plan)
{
    plan->computed_word[0] = computed_word_1;
    plan->computed_word[1] = computed_word_0;
    plan->mask_word = mask_word;
    for (unsigned i = 0; i < 2; ++i)
        plan->xor_source[i] = xor_source[i];
    plan->auxiliary_word = auxiliary_word;
    plan->fifo_word[0] = 6U;
    plan->fifo_word[1] = 5U;
    plan->fifo_word[2] = 18U;
    plan->fifo_word[3] = computed_word_1;
    plan->fifo_word[4] = 44U;
    plan->fifo_word[5] = computed_word_0;
    plan->fifo_word[6] = 21U;
    plan->fifo_word[7] = mask_word;
    plan->fifo_word[8] = 47U;
    plan->fifo_word[9] = xor_source[0] ^ mask_word;
    plan->fifo_word[10] = auxiliary_word;
    plan->fifo_word[11] = xor_source[1] ^ mask_word;
    plan->fifo_word[12] = 19U;
    plan->fifo_word[13] = 0x3e4ccccdU;
    plan->fifo_word[14] = 0x3e4ccccdU;
    plan->fifo_word[15] = 0x3e4ccccdU;
    plan->fifo_count = 16U;
}

struct recovered_geometry_helper_gate_94080_plan {
    recovered_u32 r9_value, divisor_word, remainder, active_argument;
    recovered_u32 helper_target, table_base, flag_address, flag_value;
};

void recovered_geometry_helper_gate_94080(
    recovered_u32 r9_value, recovered_u32 divisor_word,
    recovered_u32 active_argument, recovered_u32 alternate_argument,
    struct recovered_geometry_helper_gate_94080_plan *plan)
{
    recovered_u32 alternate = r9_value == 0U || divisor_word % 3U == 2U;

    plan->r9_value = r9_value;
    plan->divisor_word = divisor_word;
    plan->remainder = divisor_word % 3U;
    plan->active_argument = alternate ? alternate_argument : active_argument;
    plan->helper_target = 0x8e310U;
    plan->table_base = alternate ? 0x2be296cU : 0x2be2a14U;
    plan->flag_address = 0x5624e0U;
    plan->flag_value = alternate ? 0U : 1U;
}

struct recovered_geometry_packet_94bf0_plan {
    recovered_u32 frame_readback, fifo_word[5], fifo_count;
};

void recovered_geometry_packet_94bf0(
    recovered_u32 frame_readback,
    struct recovered_geometry_packet_94bf0_plan *plan)
{
    plan->frame_readback = frame_readback;
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 21U;
    plan->fifo_word[2] = 0x8000U;
    plan->fifo_word[3] = 58U;
    plan->fifo_word[4] = frame_readback;
    plan->fifo_count = 5U;
}

struct recovered_geometry_packet_951ec_plan {
    recovered_u32 computed_word, primary_word, secondary_word;
    recovered_u32 xor_source[2], auxiliary_word, xor_mask;
    recovered_u32 fifo_word[16], fifo_count;
};

void recovered_geometry_packet_951ec(
    recovered_u32 computed_word, recovered_u32 primary_word,
    recovered_u32 secondary_word, recovered_u32 xor_source_0,
    recovered_u32 xor_source_1, recovered_u32 xor_mask,
    recovered_u32 auxiliary_word,
    struct recovered_geometry_packet_951ec_plan *plan)
{
    plan->computed_word = computed_word;
    plan->primary_word = primary_word;
    plan->secondary_word = secondary_word;
    plan->xor_source[0] = xor_source_0;
    plan->xor_source[1] = xor_source_1;
    plan->xor_mask = xor_mask;
    plan->auxiliary_word = auxiliary_word;
    plan->fifo_word[0] = 6U;
    plan->fifo_word[1] = 5U;
    plan->fifo_word[2] = 18U;
    plan->fifo_word[3] = computed_word;
    plan->fifo_word[4] = primary_word;
    plan->fifo_word[5] = secondary_word;
    plan->fifo_word[6] = 21U;
    plan->fifo_word[7] = 0x4000U;
    plan->fifo_word[8] = 47U;
    plan->fifo_word[9] = xor_source_0 ^ xor_mask;
    plan->fifo_word[10] = auxiliary_word;
    plan->fifo_word[11] = xor_source_1 ^ xor_mask;
    plan->fifo_word[12] = 19U;
    plan->fifo_word[13] = 0x3e4ccccdU;
    plan->fifo_word[14] = 0x3e4ccccdU;
    plan->fifo_word[15] = 0x3e4ccccdU;
    plan->fifo_count = 16U;
}

struct recovered_geometry_packet_95360_plan {
    recovered_u32 input_word[3], packed_word;
    recovered_u32 fifo_word[11], fifo_count;
};

void recovered_geometry_packet_95360(
    const recovered_u32 input_word[3], recovered_u32 packed_source,
    struct recovered_geometry_packet_95360_plan *plan)
{
    for (unsigned i = 0; i < 3; ++i) {
        plan->input_word[i] = input_word[i];
        plan->fifo_word[2 + i] = input_word[i];
    }
    plan->packed_word = packed_source & 0xffffU;
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 18U;
    plan->fifo_word[5] = 21U;
    plan->fifo_word[6] = plan->packed_word;
    plan->fifo_word[7] = 19U;
    plan->fifo_word[8] = 0x3e4ccccdU;
    plan->fifo_word[9] = 0x3e4ccccdU;
    plan->fifo_word[10] = 0x3e4ccccdU;
    plan->fifo_count = 11U;
}

struct recovered_geometry_packet_95c20_plan {
    recovered_u32 fifo_word[5], fifo_count;
};

void recovered_geometry_packet_95c20(
    struct recovered_geometry_packet_95c20_plan *plan)
{
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 21U;
    plan->fifo_word[2] = 0x8000U;
    plan->fifo_word[3] = 5U;
    plan->fifo_word[4] = 58U; /* addo 31,27 */
    plan->fifo_count = 5U;
}

struct recovered_geometry_window_95c80_plan {
    recovered_u32 window_word[4][4], window_count;
    recovered_u32 control_address, control_value, publish_address;
    recovered_u32 helper_target, helper_call_count;
};

void recovered_geometry_window_95c80(
    recovered_u32 final_window_word, struct recovered_geometry_window_95c80_plan *plan)
{
    static const recovered_u32 windows[3][3] = {
        {0x401e08U, 0x401e50U, 0x84e1d1U},
        {0x401e5cU, 0x401e9cU, 0x84e232U},
        {0x401ea4U, 0x401ebcU, 0x84e289U},
    };
    for (unsigned i = 0; i < 3; ++i) {
        plan->window_word[i][0] = windows[i][0];
        plan->window_word[i][1] = windows[i][1];
        plan->window_word[i][2] = windows[i][2];
        plan->window_word[i][3] = 0U;
    }
    plan->window_word[3][0] = 0x401ec0U;
    plan->window_word[3][1] = 0x401f78U;
    plan->window_word[3][2] = 0x84e2aeU;
    plan->window_word[3][3] = final_window_word;
    plan->window_count = 4U;
    plan->control_address = 0x800010U;
    plan->control_value = 0x101U;
    plan->publish_address = 0x804000U;
    plan->helper_target = 0x6fec0U;
    plan->helper_call_count = 4U;
}

struct recovered_geometry_packet_95db4_plan {
    recovered_u32 frame_readback, fifo_word[10], fifo_count;
};

void recovered_geometry_packet_95db4(
    recovered_u32 frame_readback,
    struct recovered_geometry_packet_95db4_plan *plan)
{
    plan->frame_readback = frame_readback;
    plan->fifo_word[0] = 6U;
    plan->fifo_word[1] = 5U;
    plan->fifo_word[2] = 18U;
    plan->fifo_word[3] = 0x413e7803U;
    plan->fifo_word[4] = 0xc0c66666U;
    plan->fifo_word[5] = 0xc0828db9U;
    plan->fifo_word[6] = 21U;
    plan->fifo_word[7] = 0x10000U; /* setbit 16,0 */
    plan->fifo_word[8] = 58U;      /* addo 31,27 */
    plan->fifo_word[9] = frame_readback;
    plan->fifo_count = 10U;
}

struct recovered_geometry_packet_95e90_plan {
    recovered_u32 frame_readback, fifo_word[6], fifo_count;
};

void recovered_geometry_packet_95e90(
    recovered_u32 frame_readback,
    struct recovered_geometry_packet_95e90_plan *plan)
{
    plan->frame_readback = frame_readback;
    plan->fifo_word[0] = 6U;
    plan->fifo_word[1] = 5U;
    plan->fifo_word[2] = 21U;
    plan->fifo_word[3] = 0x8000U; /* setbit 15,0 */
    plan->fifo_word[4] = 58U;     /* addo 31,27 */
    plan->fifo_word[5] = frame_readback;
    plan->fifo_count = 6U;
}

struct recovered_geometry_packet_95f1c_plan {
    recovered_u32 frame_readback, fifo_word[8], fifo_count;
};

void recovered_geometry_packet_95f1c(
    recovered_u32 frame_readback,
    struct recovered_geometry_packet_95f1c_plan *plan)
{
    plan->frame_readback = frame_readback;
    plan->fifo_word[0] = 6U;
    plan->fifo_word[1] = 5U;
    plan->fifo_word[2] = 18U;
    plan->fifo_word[3] = 0x3f8ccccdU;
    plan->fifo_word[4] = 0xc00ccccdU;
    plan->fifo_word[5] = 0xc0800000U;
    plan->fifo_word[6] = 58U; /* addo 31,27 */
    plan->fifo_word[7] = frame_readback;
    plan->fifo_count = 8U;
}

struct recovered_geometry_window_95fac_plan {
    recovered_u32 window_word[2][4], window_count;
    recovered_u32 control_address, control_value, publish_address;
};

void recovered_geometry_window_95fac(
    recovered_u32 final_window_word,
    struct recovered_geometry_window_95fac_plan *plan)
{
    plan->window_word[0][0] = 0x40368cU;
    plan->window_word[0][1] = 0x4037e0U;
    plan->window_word[0][2] = 0x84feedU;
    plan->window_word[0][3] = final_window_word;
    plan->window_word[1][0] = 0x404a64U;
    plan->window_word[1][1] = 0x404ac4U;
    plan->window_word[1][2] = 0x851590U;
    plan->window_word[1][3] = final_window_word;
    plan->window_count = 2U;
    plan->control_address = 0x800010U;
    plan->control_value = 0x101U;
    plan->publish_address = 0x804000U;
}

struct recovered_geometry_window_964a0_plan {
    recovered_u32 window_word[2][4], window_count;
    recovered_u32 control_address, control_value, publish_address;
};

void recovered_geometry_window_964a0(
    recovered_u32 final_window_word,
    struct recovered_geometry_window_964a0_plan *plan)
{
    plan->window_word[0][0] = 0x402218U;
    plan->window_word[0][1] = 0x4022c8U;
    plan->window_word[0][2] = 0x84e6bfU;
    plan->window_word[0][3] = final_window_word;
    plan->window_word[1][0] = 0x4029bcU;
    plan->window_word[1][1] = 0x4029ecU;
    plan->window_word[1][2] = 0x84efcaU;
    plan->window_word[1][3] = final_window_word;
    plan->window_count = 2U;
    plan->control_address = 0x800010U;
    plan->control_value = 0x101U;
    plan->publish_address = 0x804000U;
}

struct recovered_geometry_indexed_table_update_97d50_plan {
    recovered_u32 index, existing_word, existing_negative;
    recovered_u32 helper_input[2], helper_result[2], helper_target;
    recovered_u32 updated_word[3], updated_mask[3];
    recovered_u32 packet_target;
};

static recovered_u32 recovered_geometry_cvtir_bits(int32_t value)
{
    union { float real; recovered_u32 bits; } converted;
    converted.real = (float)value;
    return converted.bits;
}

static recovered_u32 recovered_geometry_add_half_bits(recovered_u32 bits)
{
    union { float real; recovered_u32 bits; } converted;
    union { float real; recovered_u32 bits; } input;

    input.bits = bits;
    /* addrl operates in the i960 real format; round only at the store. */
    converted.real = (float)((double)input.real + 0.5);
    return converted.bits;
}

static recovered_u32 recovered_geometry_indexed_quantize(
    recovered_u32 helper_result)
{
    int32_t biased = (int32_t)(helper_result & 0xffU) - 0x7f;
    return recovered_geometry_cvtir_bits(biased / 20);
}

static recovered_u32 recovered_geometry_real_is_negative(recovered_u32 bits)
{
    recovered_u32 magnitude = bits & 0x7fffffffU;
    /* Match cmprl against zero: NaNs are unordered, and -0 is not less. */
    return (bits & 0x80000000U) != 0U && magnitude != 0U &&
           (magnitude >> 23) != 0xffU;
}

void recovered_geometry_indexed_table_update_97d50(
    recovered_u32 index, recovered_u32 existing_word,
    recovered_u32 helper_result_0, recovered_u32 helper_result_1,
    recovered_u32 random_source_base,
    struct recovered_geometry_indexed_table_update_97d50_plan *plan)
{
    recovered_u32 negative = recovered_geometry_real_is_negative(existing_word);
    recovered_u32 helper_input = index + random_source_base;

    plan->index = index;
    plan->existing_word = existing_word;
    plan->existing_negative = negative;
    plan->helper_input[0] = helper_input;
    plan->helper_input[1] = helper_input;
    plan->helper_result[0] = helper_result_0;
    plan->helper_result[1] = helper_result_1;
    plan->helper_target = 0xf5058U;
    plan->packet_target = 0x97e10U;
    for (unsigned i = 0; i < 3; ++i) {
        plan->updated_word[i] = 0U;
        plan->updated_mask[i] = 0U;
    }
    if (negative) {
        plan->updated_word[1] = recovered_geometry_add_half_bits(existing_word);
        plan->updated_mask[1] = 1U;
    } else {
        plan->updated_word[0] = recovered_geometry_indexed_quantize(helper_result_0);
        plan->updated_word[1] = 0xc1880000U;
        plan->updated_word[2] = recovered_geometry_indexed_quantize(helper_result_1);
        plan->updated_mask[0] = 1U;
        plan->updated_mask[1] = 1U;
        plan->updated_mask[2] = 1U;
    }
}

/* The 0x97e10 consumer uses values prepared by the 0x97d50 table updater. */
struct recovered_geometry_packet_97e10_plan {
    recovered_u32 table_word[3], context_word, derived_word;
    recovered_u32 fifo_word[12], fifo_count;
};

void recovered_geometry_packet_97e10(
    const recovered_u32 table_word[3], recovered_u32 context_word,
    struct recovered_geometry_packet_97e10_plan *plan)
{
    for (unsigned i = 0; i < 3; ++i) {
        plan->table_word[i] = table_word[i];
        plan->fifo_word[2 + i] = table_word[i];
    }
    plan->context_word = context_word;
    plan->derived_word = 0x10000U - context_word;
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 18U;
    plan->fifo_word[5] = 21U;
    plan->fifo_word[6] = plan->derived_word;
    plan->fifo_word[7] = 19U;
    plan->fifo_word[8] = 0x3e800000U;
    plan->fifo_word[9] = 0x3f800000U;
    plan->fifo_word[10] = 0x3f800000U;
    plan->fifo_word[11] = 58U; /* addo 31,27 */
    plan->fifo_count = 12U;
}

/* Models the fall-through at 0x97e10 after the indexed table update. */
void recovered_geometry_indexed_table_update_and_packet_97d50(
    recovered_u32 index, const recovered_u32 existing_word[3],
    recovered_u32 helper_result_0, recovered_u32 helper_result_1,
    recovered_u32 random_source_base, recovered_u32 context_word,
    struct recovered_geometry_indexed_table_update_97d50_plan *update,
    struct recovered_geometry_packet_97e10_plan *packet)
{
    recovered_u32 table_word[3];

    recovered_geometry_indexed_table_update_97d50(
        index, existing_word[1], helper_result_0, helper_result_1,
        random_source_base, update);
    for (unsigned i = 0; i < 3; ++i)
        table_word[i] = existing_word[i];
    for (unsigned i = 0; i < 3; ++i)
        if (update->updated_mask[i] != 0U)
            table_word[i] = update->updated_word[i];
    recovered_geometry_packet_97e10(table_word, context_word, packet);
}

struct recovered_geometry_indexed_update_loop_plan {
    recovered_u32 start_index, end_exclusive, iteration_count;
    recovered_u32 packet_preamble[6], packet_preamble_count;
    recovered_u32 update_target, packet_target, completion_word;
    recovered_u32 window_word[4], control_address, control_value;
};

static void recovered_geometry_indexed_update_loop(
    recovered_u32 start_index, recovered_u32 end_exclusive,
    recovered_u32 preamble_word, recovered_u32 preamble_word_1,
    recovered_u32 has_preamble,
    struct recovered_geometry_indexed_update_loop_plan *plan)
{
    plan->start_index = start_index;
    plan->end_exclusive = end_exclusive;
    plan->iteration_count = end_exclusive - start_index;
    plan->packet_preamble[0] = 5U;
    plan->packet_preamble[1] = 18U;
    plan->packet_preamble[2] = preamble_word;
    plan->packet_preamble[3] = 0x4089999aU;
    plan->packet_preamble[4] = preamble_word_1;
    plan->packet_preamble[5] = 58U;
    plan->packet_preamble_count = has_preamble != 0U ? 6U : 0U;
    plan->update_target = 0x97d50U;
    plan->packet_target = 0x97e10U;
    plan->completion_word = 6U;
    plan->window_word[0] = 0x403198U;
    plan->window_word[1] = 0x403518U;
    plan->window_word[2] = 0x84f888U;
    plan->window_word[3] = 0U;
    plan->control_address = 0x800010U;
    plan->control_value = 0x101U;
}

void recovered_geometry_indexed_update_loop_97f20(
    struct recovered_geometry_indexed_update_loop_plan *plan)
{
    recovered_geometry_indexed_update_loop(
        0x40U, 0x4fU, 0xc2700000U, 0xc1a00000U, 1U, plan);
}

void recovered_geometry_indexed_update_loop_98000(
    struct recovered_geometry_indexed_update_loop_plan *plan)
{
    recovered_geometry_indexed_update_loop(
        0x50U, 0x5fU, 0x42700000U, 0xc1a00000U, 1U, plan);
}

void recovered_geometry_indexed_update_loop_98114(
    struct recovered_geometry_indexed_update_loop_plan *plan)
{
    recovered_geometry_indexed_update_loop(
        0x60U, 0x6fU, 0xc1a00000U, 0xc2700000U, 1U, plan);
}

void recovered_geometry_indexed_update_loop_98200(
    struct recovered_geometry_indexed_update_loop_plan *plan)
{
    recovered_geometry_indexed_update_loop(
        0x70U, 0x7fU, 0U, 0U, 0U, plan);
}

struct recovered_geometry_packet_982f8_plan {
    recovered_u32 response_word[3], context_word, derived_word;
    recovered_u32 fifo_word[11], fifo_count;
};

void recovered_geometry_packet_982f8(
    recovered_u32 response_word_0, recovered_u32 response_word_1,
    recovered_u32 response_word_2, recovered_u32 context_word,
    struct recovered_geometry_packet_982f8_plan *plan)
{
    plan->response_word[0] = response_word_0;
    plan->response_word[1] = response_word_1;
    plan->response_word[2] = response_word_2;
    plan->context_word = context_word;
    plan->derived_word = 0x10000U - context_word;
    plan->fifo_word[0] = 18U;
    plan->fifo_word[1] = response_word_0;
    plan->fifo_word[2] = response_word_1;
    plan->fifo_word[3] = response_word_2;
    plan->fifo_word[4] = 21U;
    plan->fifo_word[5] = plan->derived_word;
    plan->fifo_word[6] = 19U;
    plan->fifo_word[7] = 0x3f88f5c3U;
    plan->fifo_word[8] = 0x3f800000U;
    plan->fifo_word[9] = 0x3f800000U;
    plan->fifo_word[10] = 58U; /* addo 31,27 */
    plan->fifo_count = 11U;
}

struct recovered_geometry_indexed_post_loop_98200_plan {
    recovered_u32 source_word, source_byte;
    recovered_u32 service_first, service_second, service_target;
    recovered_u32 completion_word, command29, command30;
    recovered_u32 context_word, constant_word, zero_response_word;
    recovered_u32 packet_target;
};

/* Exact setup between the 0x98200 loop and the 0x982f8 response packet. */
void recovered_geometry_indexed_post_loop_98200(
    recovered_u32 source_word, recovered_u32 context_word,
    recovered_u32 response_word_0, recovered_u32 response_word_2,
    struct recovered_geometry_indexed_post_loop_98200_plan *plan,
    struct recovered_geometry_packet_982f8_plan *packet)
{
    plan->source_word = source_word;
    plan->source_byte = source_word & 0xffU;
    plan->service_first = plan->source_byte << 8;
    plan->service_second = 0x6a00U;
    plan->service_target = 0x2a990U;
    plan->completion_word = 6U;
    plan->command29 = 29U;
    plan->command30 = 30U;
    plan->context_word = context_word;
    plan->constant_word = 0x40b33333U;
    plan->zero_response_word = 0U;
    plan->packet_target = 0x982f8U;
    recovered_geometry_packet_982f8(response_word_0, 0U, response_word_2,
                                    context_word, packet);
}
