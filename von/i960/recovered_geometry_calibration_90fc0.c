/* Control-flow partition recovered from i960 0x90fc0-0x9139c. */
#include "recovered_common.h"

struct recovered_geometry_calibration_90fc0_plan {
    recovered_u32 source_value, lower_guard;
    recovered_u32 branch_target, branch_class;
};

void recovered_geometry_calibration_90fc0(
    recovered_u32 source_value, recovered_u32 lower_guard,
    struct recovered_geometry_calibration_90fc0_plan *plan)
{
    recovered_u32 target;
    recovered_u32 branch_class;

    if (source_value <= lower_guard) {
        target = 0x9139cU;
        branch_class = 0U;
    } else if (source_value <= 0x8bU) {
        target = 0x91008U;
        branch_class = 1U;
    } else if (source_value <= 0x9fU) {
        target = 0x9107cU;
        branch_class = 2U;
    } else if (source_value <= 0xb3U) {
        target = 0x910e8U;
        branch_class = 3U;
    } else if (source_value <= 0xb8U) {
        target = 0x9139cU;
        branch_class = 4U;
    } else if (source_value <= 0xccU) {
        target = 0x91124U;
        branch_class = 5U;
    } else if (source_value <= 0xf4U) {
        target = 0x91148U;
        branch_class = 6U;
    } else if (source_value <= 0x108U) {
        target = 0x91180U;
        branch_class = 7U;
    } else if (source_value <= 0x11cU) {
        target = 0x911a8U;
        branch_class = 8U;
    } else if (source_value <= 0x1f8U) {
        target = 0x911ccU;
        branch_class = 9U;
    } else if (source_value <= 0x234U) {
        target = 0x91220U;
        branch_class = 10U;
    } else if (source_value <= 0x270U) {
        target = 0x91248U;
        branch_class = 11U;
    } else if (source_value <= 0x284U) {
        target = 0x91268U;
        branch_class = 12U;
    } else if (source_value <= 0x2c0U) {
        target = 0x9128cU;
        branch_class = 13U;
    } else if (source_value <= 0x2d4U) {
        target = 0x912b4U;
        branch_class = 14U;
    } else if (source_value <= 0x310U) {
        target = 0x912d8U;
        branch_class = 15U;
    } else if (source_value <= 0x315U || source_value > 0x379U) {
        target = 0x9139cU;
        branch_class = 16U;
    } else {
        target = 0x91308U;
        branch_class = 17U;
    }

    plan->source_value = source_value;
    plan->lower_guard = lower_guard;
    plan->branch_target = target;
    plan->branch_class = branch_class;
}

struct recovered_geometry_calibration_packet_9139c_plan {
    recovered_u32 input_word[3], calibration_word[3], fifo_word[7], fifo_count;
    recovered_u32 helper_target, operand_word;
};

void recovered_geometry_calibration_packet_9139c(
    const recovered_u32 input_word[3], const recovered_u32 calibration_word[3],
    struct recovered_geometry_calibration_packet_9139c_plan *plan)
{
    for (unsigned i = 0; i < 3; ++i) {
        plan->input_word[i] = input_word[i];
        plan->calibration_word[i] = calibration_word[i];
    }
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 18U;
    plan->fifo_word[2] = input_word[0] + calibration_word[0];
    plan->fifo_word[3] = input_word[1] + calibration_word[1];
    plan->fifo_word[4] = input_word[2] + calibration_word[2];
    plan->fifo_word[5] = 21U;
    plan->fifo_word[6] = 0xc000U; /* shlo 14, 3 */
    plan->fifo_count = 7U;
    plan->helper_target = 0x8e310U;
    plan->operand_word = 0xc000U;
}

void recovered_geometry_calibration_callsite_96964(
    const recovered_u32 calibration_word[3],
    struct recovered_geometry_calibration_packet_9139c_plan *plan)
{
    static const recovered_u32 input_word[3] = {
        0x41e00000U, 0x41d66666U, 0xc17b3333U
    };
    recovered_geometry_calibration_packet_9139c(input_word, calibration_word,
                                                plan);
}

struct recovered_geometry_calibration_packet_91434_plan {
    recovered_u32 computed_word, address_word_0, address_word_1;
    recovered_u32 secondary_word, frame_readback, fifo_word[9], fifo_count;
};

void recovered_geometry_calibration_packet_91434(
    recovered_u32 computed_word, recovered_u32 address_word_0,
    recovered_u32 address_word_1, recovered_u32 secondary_word,
    recovered_u32 frame_readback,
    struct recovered_geometry_calibration_packet_91434_plan *plan)
{
    plan->computed_word = computed_word;
    plan->address_word_0 = address_word_0;
    plan->address_word_1 = address_word_1;
    plan->secondary_word = secondary_word;
    plan->frame_readback = frame_readback;
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 18U;
    plan->fifo_word[2] = computed_word;
    plan->fifo_word[3] = address_word_0;
    plan->fifo_word[4] = address_word_1;
    plan->fifo_word[5] = 21U;
    plan->fifo_word[6] = secondary_word;
    plan->fifo_word[7] = 58U; /* 31 + 27 */
    plan->fifo_word[8] = frame_readback;
    plan->fifo_count = 9U;
}

struct recovered_geometry_calibration_window_914d8_plan {
    recovered_u32 window_word[4], control_address, control_value;
    recovered_u32 publish_address, completion_word;
};

void recovered_geometry_calibration_window_914d8(
    struct recovered_geometry_calibration_window_914d8_plan *plan)
{
    plan->window_word[0] = 0x403968U;
    plan->window_word[1] = 0x4039f0U;
    plan->window_word[2] = 0x850225U;
    plan->window_word[3] = 0U;
    plan->control_address = 0x800010U;
    plan->control_value = 0x101U;
    plan->publish_address = 0x804000U;
    plan->completion_word = 6U; /* emitted by the immediate continuation */
}

struct recovered_geometry_calibration_packet_91510_plan {
    recovered_u32 computed_word, address_word_0, address_word_1;
    recovered_u32 xor_word_0, xor_word_1, auxiliary_word;
    recovered_u32 fifo_word[16], fifo_count;
};

void recovered_geometry_calibration_packet_91510(
    recovered_u32 computed_word, recovered_u32 address_word_0,
    recovered_u32 address_word_1, recovered_u32 xor_word_0,
    recovered_u32 auxiliary_word, recovered_u32 xor_word_1,
    struct recovered_geometry_calibration_packet_91510_plan *plan)
{
    plan->computed_word = computed_word;
    plan->address_word_0 = address_word_0;
    plan->address_word_1 = address_word_1;
    plan->xor_word_0 = xor_word_0;
    plan->auxiliary_word = auxiliary_word;
    plan->xor_word_1 = xor_word_1;
    plan->fifo_word[0] = 6U;
    plan->fifo_word[1] = 5U;
    plan->fifo_word[2] = 18U;
    plan->fifo_word[3] = computed_word;
    plan->fifo_word[4] = address_word_0;
    plan->fifo_word[5] = address_word_1;
    plan->fifo_word[6] = 21U;
    plan->fifo_word[7] = 0x4000U;
    plan->fifo_word[8] = 47U;
    plan->fifo_word[9] = xor_word_0;
    plan->fifo_word[10] = auxiliary_word;
    plan->fifo_word[11] = xor_word_1;
    plan->fifo_word[12] = 19U;
    plan->fifo_word[13] = 0x3e4ccccdU;
    plan->fifo_word[14] = 0x3e4ccccdU;
    plan->fifo_word[15] = 0x3e4ccccdU;
    plan->fifo_count = 16U;
}

void recovered_geometry_calibration_packet_91ccc(
    recovered_u32 computed_word, recovered_u32 address_word_0,
    recovered_u32 address_word_1, recovered_u32 xor_word_0,
    recovered_u32 auxiliary_word, recovered_u32 xor_word_1,
    struct recovered_geometry_calibration_packet_91510_plan *plan)
{
    recovered_geometry_calibration_packet_91510(
        computed_word, address_word_0, address_word_1, xor_word_0,
        auxiliary_word, xor_word_1, plan);
}

struct recovered_geometry_calibration_helper_gate_915d0_plan {
    recovered_u32 r15_value, source_value, remainder;
    recovered_u32 helper_target, table_base, flag_value;
};

void recovered_geometry_calibration_helper_gate_915d0(
    recovered_u32 r15_value, recovered_u32 source_value,
    struct recovered_geometry_calibration_helper_gate_915d0_plan *plan)
{
    recovered_u32 remainder = source_value % 3U;
    recovered_u32 alternate = r15_value == 0U || remainder == 2U;

    plan->r15_value = r15_value;
    plan->source_value = source_value;
    plan->remainder = remainder;
    plan->helper_target = 0x8e310U;
    plan->table_base = alternate ? 0x2be296cU : 0x2be2a14U;
    plan->flag_value = alternate ? 0U : 1U;
}

void recovered_geometry_calibration_helper_gate_91d94(
    recovered_u32 r15_value, recovered_u32 source_value,
    struct recovered_geometry_calibration_helper_gate_915d0_plan *plan)
{
    /* The paired caller at 0x91d94 repeats the same gate exactly. */
    recovered_geometry_calibration_helper_gate_915d0(r15_value, source_value, plan);
}

void recovered_geometry_calibration_helper_gate_91dac(
    recovered_u32 r15_value, recovered_u32 source_value,
    struct recovered_geometry_calibration_helper_gate_915d0_plan *plan)
{
    /* Compatibility alias for the remi instruction inside the gate. */
    recovered_geometry_calibration_helper_gate_91d94(r15_value, source_value, plan);
}

struct recovered_geometry_calibration_packet_91a74_plan {
    recovered_u32 input_word[3], fifo_word[9], fifo_count, frame_readback;
};

void recovered_geometry_calibration_packet_91a74(
    const recovered_u32 input_word[3], recovered_u32 frame_readback,
    struct recovered_geometry_calibration_packet_91a74_plan *plan)
{
    for (unsigned i = 0; i < 3; ++i)
        plan->input_word[i] = input_word[i];
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 18U;
    plan->fifo_word[2] = input_word[0];
    plan->fifo_word[3] = input_word[1];
    plan->fifo_word[4] = input_word[2];
    plan->fifo_word[5] = 21U;
    plan->fifo_word[6] = 0xc000U;
    plan->fifo_word[7] = 58U; /* 31 + 27 */
    plan->fifo_word[8] = frame_readback;
    plan->fifo_count = 9U;
    plan->frame_readback = frame_readback;
}

void recovered_geometry_calibration_callsite_969c4(
    const recovered_u32 calibration_word[3], recovered_u32 frame_readback,
    struct recovered_geometry_calibration_packet_91a74_plan *plan)
{
    static const recovered_u32 input_word[3] = {
        0x41b00000U, 0x41ef3333U, 0xc141999aU
    };
    recovered_geometry_calibration_packet_91a74(input_word, frame_readback,
                                                plan);
    for (unsigned i = 0; i < 3; ++i)
        plan->fifo_word[2 + i] = input_word[i] + calibration_word[i];
}

struct recovered_geometry_calibration_window_91b10_plan {
    recovered_u32 window_word[4], control_address, control_value;
    recovered_u32 publish_address, completion_word;
};

void recovered_geometry_calibration_window_91b10(
    struct recovered_geometry_calibration_window_91b10_plan *plan)
{
    plan->window_word[0] = 0x403a90U;
    plan->window_word[1] = 0x403b18U;
    plan->window_word[2] = 0x850387U;
    plan->window_word[3] = 0U;
    plan->control_address = 0x800010U;
    plan->control_value = 0x101U;
    plan->publish_address = 0x804000U;
    plan->completion_word = 6U;
}

struct recovered_geometry_calibration_secondary_partition_91e60_plan {
    recovered_u32 source_value, branch_target, branch_class;
};

void recovered_geometry_calibration_secondary_partition_91e60(
    recovered_u32 source_value,
    struct recovered_geometry_calibration_secondary_partition_91e60_plan *plan)
{
    recovered_u32 target;
    recovered_u32 branch_class;

    if (source_value <= 0x12bU) {
        target = 0x91ea8U;
        branch_class = 0U;
    } else if (source_value <= 0x149U) {
        target = 0x91f30U;
        branch_class = 1U;
    } else if (source_value <= 0x275U) {
        target = 0x91edcU;
        branch_class = 2U;
    } else if (source_value <= 0x293U) {
        target = 0x91f30U;
        branch_class = 3U;
    } else {
        target = 0x91f44U;
        branch_class = 4U;
    }
    plan->source_value = source_value;
    plan->branch_target = target;
    plan->branch_class = branch_class;
}

struct recovered_geometry_calibration_packet_91f44_plan {
    recovered_u32 input_word, masked_word, frame_readback;
    recovered_u32 fifo_word[5], fifo_count;
};

void recovered_geometry_calibration_packet_91f44(
    recovered_u32 input_word, recovered_u32 frame_readback,
    struct recovered_geometry_calibration_packet_91f44_plan *plan)
{
    plan->input_word = input_word;
    plan->masked_word = input_word | 0x8000U;
    plan->frame_readback = frame_readback;
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 21U;
    plan->fifo_word[2] = plan->masked_word;
    plan->fifo_word[3] = 58U;
    plan->fifo_word[4] = frame_readback;
    plan->fifo_count = 5U;
}

struct recovered_geometry_calibration_packet_91fac_plan {
    recovered_u32 input_word[3], fifo_word[7], fifo_count;
    recovered_u32 operand_word, helper_target;
};

void recovered_geometry_calibration_packet_91fac(
    const recovered_u32 input_word[3],
    struct recovered_geometry_calibration_packet_91fac_plan *plan)
{
    for (unsigned i = 0; i < 3; ++i)
        plan->input_word[i] = input_word[i];
    plan->operand_word = 0xc000U;
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 18U;
    plan->fifo_word[2] = input_word[0];
    plan->fifo_word[3] = input_word[1];
    plan->fifo_word[4] = input_word[2];
    plan->fifo_word[5] = 21U;
    plan->fifo_word[6] = plan->operand_word;
    plan->fifo_count = 7U;
    plan->helper_target = 0x8e310U;
}

struct recovered_geometry_calibration_packet_92070_plan {
    recovered_u32 record_word, computed_word[2], auxiliary_word, frame_readback;
    recovered_u32 fifo_word[10], fifo_count;
};

void recovered_geometry_calibration_packet_92070(
    recovered_u32 record_word, recovered_u32 computed_word_0,
    recovered_u32 computed_word_1, recovered_u32 auxiliary_word,
    recovered_u32 frame_readback,
    struct recovered_geometry_calibration_packet_92070_plan *plan)
{
    plan->record_word = record_word;
    plan->computed_word[0] = computed_word_0;
    plan->computed_word[1] = computed_word_1;
    plan->auxiliary_word = auxiliary_word;
    plan->frame_readback = frame_readback;
    plan->fifo_word[0] = 6U;
    plan->fifo_word[1] = 5U;
    plan->fifo_word[2] = 18U;
    plan->fifo_word[3] = record_word;
    plan->fifo_word[4] = computed_word_0;
    plan->fifo_word[5] = computed_word_1;
    plan->fifo_word[6] = 21U;
    plan->fifo_word[7] = 0xc000U; /* r5 carries shlo 14,3 */
    plan->fifo_word[8] = auxiliary_word;
    plan->fifo_word[9] = frame_readback;
    plan->fifo_count = 10U;
}

struct recovered_geometry_calibration_packet_92144_plan {
    recovered_u32 leading_word[3], xor_source[2], xor_mask, auxiliary_word;
    recovered_u32 fifo_word[16], fifo_count;
};

void recovered_geometry_calibration_packet_92144(
    const recovered_u32 leading_word[3], const recovered_u32 xor_source[2],
    recovered_u32 xor_mask, recovered_u32 auxiliary_word,
    struct recovered_geometry_calibration_packet_92144_plan *plan)
{
    for (unsigned i = 0; i < 3; ++i)
        plan->leading_word[i] = leading_word[i];
    for (unsigned i = 0; i < 2; ++i)
        plan->xor_source[i] = xor_source[i];
    plan->xor_mask = xor_mask;
    plan->auxiliary_word = auxiliary_word;
    plan->fifo_word[0] = 6U;
    plan->fifo_word[1] = 5U;
    plan->fifo_word[2] = 18U;
    plan->fifo_word[3] = leading_word[0];
    plan->fifo_word[4] = leading_word[1];
    plan->fifo_word[5] = leading_word[2];
    plan->fifo_word[6] = 21U;
    plan->fifo_word[7] = 0x4000U; /* setbit 14,0 */
    plan->fifo_word[8] = 47U; /* 31 + 16 */
    plan->fifo_word[9] = xor_source[0] ^ xor_mask;
    plan->fifo_word[10] = auxiliary_word;
    plan->fifo_word[11] = xor_source[1] ^ xor_mask;
    plan->fifo_word[12] = 19U;
    plan->fifo_word[13] = 0x3e4ccccdU;
    plan->fifo_word[14] = 0x3e4ccccdU;
    plan->fifo_word[15] = 0x3e4ccccdU;
    plan->fifo_count = 16U;
}

struct recovered_geometry_calibration_helper_gate_921f8_plan {
    recovered_u32 r10_value, source_value, remainder;
    recovered_u32 helper_target, table_base, flag_address, flag_value;
};

void recovered_geometry_calibration_helper_gate_921f8(
    recovered_u32 r10_value, recovered_u32 source_value,
    struct recovered_geometry_calibration_helper_gate_921f8_plan *plan)
{
    recovered_u32 alternate = r10_value == 0U || source_value % 3U == 2U;

    plan->r10_value = r10_value;
    plan->source_value = source_value;
    plan->remainder = source_value % 3U;
    plan->helper_target = 0x8e310U;
    plan->table_base = alternate ? 0x2be296cU : 0x2be2a14U;
    plan->flag_address = 0x5624d8U;
    plan->flag_value = alternate ? 0U : 1U;
}

struct recovered_geometry_calibration_packet_91b58_plan {
    recovered_u32 input_word[3], secondary_word, fifo_word[7], fifo_count;
    recovered_u32 helper_target, completion_word;
};

void recovered_geometry_calibration_packet_91b58(
    const recovered_u32 input_word[3], recovered_u32 secondary_word,
    struct recovered_geometry_calibration_packet_91b58_plan *plan)
{
    for (unsigned i = 0; i < 3; ++i)
        plan->input_word[i] = input_word[i];
    plan->secondary_word = secondary_word;
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 18U;
    plan->fifo_word[2] = input_word[0];
    plan->fifo_word[3] = input_word[1];
    plan->fifo_word[4] = input_word[2];
    plan->fifo_word[5] = 21U;
    plan->fifo_word[6] = secondary_word;
    plan->fifo_count = 7U;
    plan->helper_target = 0x8e310U;
    plan->completion_word = 6U;
}

void recovered_geometry_calibration_packet_91bc8(
    const recovered_u32 input_word[3], recovered_u32 secondary_word,
    struct recovered_geometry_calibration_packet_91b58_plan *plan)
{
    recovered_geometry_calibration_packet_91b58(input_word, secondary_word, plan);
}

void recovered_geometry_calibration_packet_91c58(
    const recovered_u32 input_word[3], recovered_u32 secondary_word,
    struct recovered_geometry_calibration_packet_91b58_plan *plan)
{
    recovered_geometry_calibration_packet_91b58(input_word, secondary_word, plan);
}
