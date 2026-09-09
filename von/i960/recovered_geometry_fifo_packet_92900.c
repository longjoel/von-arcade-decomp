/* Shared 0x92910/0x92db0 geometry FIFO packet template. */
#include "recovered_common.h"

struct recovered_geometry_fifo_packet_92900_plan {
    recovered_u32 input_word[3], projected_word;
    recovered_u32 fifo_word[12], fifo_count;
};

void recovered_geometry_fifo_packet_92900(
    const recovered_u32 input_word[3], recovered_u32 g3,
    struct recovered_geometry_fifo_packet_92900_plan *plan)
{
    for (unsigned i = 0; i < 3; ++i)
        plan->input_word[i] = input_word[i];
    plan->projected_word = g3 & 0xffffU;
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 18U;
    plan->fifo_word[2] = input_word[0];
    plan->fifo_word[3] = input_word[1];
    plan->fifo_word[4] = input_word[2];
    plan->fifo_word[5] = 21U;
    plan->fifo_word[6] = plan->projected_word;
    plan->fifo_word[7] = 19U;
    plan->fifo_word[8] = 0x3e4ccccdU;
    plan->fifo_word[9] = 0x3e4ccccdU;
    plan->fifo_word[10] = 0x3e4ccccdU;
    plan->fifo_word[11] = 6U;
    plan->fifo_count = 12U;
}

void recovered_geometry_fifo_packet_92db0(
    const recovered_u32 input_word[3], recovered_u32 g3,
    struct recovered_geometry_fifo_packet_92900_plan *plan)
{
    recovered_geometry_fifo_packet_92900(input_word, g3, plan);
}

struct recovered_geometry_fifo_packet_92da0_prefix_plan {
    recovered_u32 divisor_word, quotient_source, quotient_word;
    recovered_u32 fifo_word[11], fifo_count;
};

void recovered_geometry_fifo_packet_92da0_prefix(
    recovered_u32 input_word[3], recovered_u32 g3,
    recovered_u32 divisor_word, recovered_u32 quotient_source,
    struct recovered_geometry_fifo_packet_92da0_prefix_plan *plan)
{
    plan->divisor_word = divisor_word;
    plan->quotient_source = quotient_source;
    plan->quotient_word = divisor_word == 0U ? 0U : quotient_source / divisor_word;
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 18U;
    plan->fifo_word[2] = input_word[0];
    plan->fifo_word[3] = input_word[1];
    plan->fifo_word[4] = input_word[2];
    plan->fifo_word[5] = 21U;
    plan->fifo_word[6] = g3 & 0xffffU;
    plan->fifo_word[7] = 19U;
    plan->fifo_word[8] = 0x3e4ccccdU;
    plan->fifo_word[9] = 0x3e4ccccdU;
    plan->fifo_word[10] = 0x3e4ccccdU;
    plan->fifo_count = 11U;
}

struct recovered_geometry_fifo_helper_gate_929a0_plan {
    recovered_u32 divisor_word, quotient_source, alternate_source;
    recovered_u32 remainder, helper_argument, helper_target, table_base;
    recovered_u32 flag_address, flag_value;
};

void recovered_geometry_fifo_helper_gate_929a0(
    recovered_u32 divisor_word, recovered_u32 quotient_source,
    recovered_u32 alternate_source, recovered_u32 flag_address,
    struct recovered_geometry_fifo_helper_gate_929a0_plan *plan)
{
    recovered_u32 alternate = divisor_word % 3U == 2U;

    plan->divisor_word = divisor_word;
    plan->quotient_source = quotient_source;
    plan->alternate_source = alternate_source;
    plan->remainder = divisor_word % 3U;
    /* The ROM path normally has a nonzero divisor.  Keep the C model
       defined for a synthetic zero divisor rather than invoking % 0. */
    plan->helper_argument = divisor_word == 0U ? 0U :
        (alternate ? alternate_source : quotient_source) % divisor_word;
    plan->helper_target = 0x8e310U;
    plan->table_base = alternate ? 0x2be296cU : 0x2be2a14U;
    plan->flag_address = flag_address;
    plan->flag_value = alternate ? 0U : 1U;
}

void recovered_geometry_fifo_helper_gate_92e28(
    recovered_u32 divisor_word, recovered_u32 quotient_source,
    recovered_u32 alternate_source,
    struct recovered_geometry_fifo_helper_gate_929a0_plan *plan)
{
    recovered_geometry_fifo_helper_gate_929a0(
        divisor_word, quotient_source, alternate_source, 0x5624e4U, plan);
}
