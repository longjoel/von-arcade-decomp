/* Table-backed diagnostic packet recovered from i960 0x90c10-0x90d40. */
#include "recovered_common.h"

struct recovered_geometry_table_packet_90c10_plan {
    recovered_u32 remainder_word, frame_word, frame_readback;
    recovered_u32 fifo_word[14], fifo_count;
};

void recovered_geometry_table_packet_90c10(
    recovered_u32 remainder_word, recovered_u32 frame_word,
    recovered_u32 frame_readback,
    struct recovered_geometry_table_packet_90c10_plan *plan)
{
    plan->remainder_word = remainder_word;
    plan->frame_word = frame_word;
    plan->frame_readback = frame_readback;
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 18U;
    plan->fifo_word[2] = remainder_word;
    plan->fifo_word[3] = 0x40e00000U;
    plan->fifo_word[4] = 0x41800000U;
    plan->fifo_word[5] = frame_word;
    plan->fifo_word[6] = 21U;
    plan->fifo_word[7] = 0xb800U;
    plan->fifo_word[8] = 19U;
    plan->fifo_word[9] = 0x40400000U;
    plan->fifo_word[10] = 0x40400000U;
    plan->fifo_word[11] = 0x40400000U;
    plan->fifo_word[12] = 58U; /* 31 + 27 */
    plan->fifo_word[13] = frame_readback;
    plan->fifo_count = 14U;
}

struct recovered_geometry_table_window_90ccc_plan {
    recovered_u32 table_base, table_index, table_word[3];
    recovered_u32 control_address, control_value, publish_address;
    recovered_u32 published, completion_word;
};

void recovered_geometry_table_window_90ccc(
    recovered_u32 remainder_word, const recovered_u32 table_word[3],
    struct recovered_geometry_table_window_90ccc_plan *plan)
{
    plan->table_base = 0x2be52b0U;
    plan->table_index = remainder_word * 12U;
    for (unsigned i = 0; i < 3; ++i)
        plan->table_word[i] = table_word[i];
    plan->control_address = 0x800010U;
    plan->control_value = 0x101U;
    plan->publish_address = 0x804000U;
    plan->published = table_word[0] != 0U ? 1U : 0U;
    plan->completion_word = 6U;
}

void recovered_geometry_table_packet_variant(
    recovered_u32 remainder_word, recovered_u32 frame_word,
    recovered_u32 operand_word, recovered_u32 frame_readback,
    struct recovered_geometry_table_packet_90c10_plan *plan)
{
    recovered_geometry_table_packet_90c10(remainder_word, frame_word,
                                          frame_readback, plan);
    plan->fifo_word[7] = operand_word;
}

void recovered_geometry_table_packet_90d50(
    recovered_u32 remainder_word, recovered_u32 frame_word,
    recovered_u32 frame_readback,
    struct recovered_geometry_table_packet_90c10_plan *plan)
{
    recovered_geometry_table_packet_variant(remainder_word, frame_word,
                                            0xc000U, frame_readback, plan);
}

void recovered_geometry_table_packet_90e80(
    recovered_u32 remainder_word, recovered_u32 frame_word,
    recovered_u32 frame_readback,
    struct recovered_geometry_table_packet_90c10_plan *plan)
{
    recovered_geometry_table_packet_variant(remainder_word, frame_word,
                                            0xc800U, frame_readback, plan);
}

struct recovered_geometry_table_dispatch_91624_plan {
    recovered_u32 source_value, threshold;
    recovered_u32 adjusted_value[3], call_helper[3], completion_word;
    recovered_u32 helper_target[3], operand_word[3];
};

void recovered_geometry_table_dispatch_91624(
    recovered_u32 source_value,
    struct recovered_geometry_table_dispatch_91624_plan *plan)
{
    static const recovered_u32 offset[3] = {0x109U, 0x113U, 0x11dU};
    static const recovered_u32 helper[3] = {0x90c10U, 0x90d50U, 0x90e80U};
    static const recovered_u32 operand[3] = {0xb800U, 0xc000U, 0xc800U};

    plan->source_value = source_value;
    plan->threshold = 15U << 4;
    for (unsigned i = 0; i < 3; ++i) {
        plan->adjusted_value[i] = source_value - offset[i];
        plan->call_helper[i] = plan->adjusted_value[i] <= plan->threshold ? 1U : 0U;
        plan->helper_target[i] = helper[i];
        plan->operand_word[i] = operand[i];
    }
    plan->completion_word = 6U;
}

void recovered_geometry_table_dispatch_91df4(
    recovered_u32 source_value,
    struct recovered_geometry_table_dispatch_91624_plan *plan)
{
    /* The paired caller at 0x91df4 repeats the exact three predicates. */
    recovered_geometry_table_dispatch_91624(source_value, plan);
}
