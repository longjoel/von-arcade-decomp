/* Record-loop math packet from i960 0x901b0-0x902b4. */
#include "recovered_common.h"

struct recovered_geometry_diagnostic_math_record_packet_901b0_plan {
    recovered_u32 source_halfword;
    recovered_u32 normalized_source;
    recovered_u32 shifted_source;
    recovered_u32 response_word;
    recovered_u32 computed_word;
    recovered_u32 fifo_word[14];
    recovered_u32 fifo_count;
};

void recovered_geometry_diagnostic_math_record_packet_901b0(
    int32_t source_halfword, recovered_u32 response_word,
    recovered_u32 computed_word,
    struct recovered_geometry_diagnostic_math_record_packet_901b0_plan *plan)
{
    int32_t normalized = source_halfword - 0x253;

    plan->source_halfword = (recovered_u32)source_halfword;
    plan->normalized_source = (recovered_u32)normalized & 0x1ffU;
    plan->shifted_source = plan->normalized_source << 7;
    plan->response_word = response_word;
    plan->computed_word = computed_word;
    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 18U;
    plan->fifo_word[2] = 0x3f000000U;
    plan->fifo_word[3] = 0x3f800000U;
    plan->fifo_word[4] = 0xbfa66666U;
    plan->fifo_word[5] = 21U;
    plan->fifo_word[6] = 0x2012U; /* 18 with bit 11 set. */
    plan->fifo_word[7] = 27U;
    plan->fifo_word[8] = plan->shifted_source;
    plan->fifo_word[9] = 27U;
    plan->fifo_word[10] = plan->shifted_source;
    plan->fifo_word[11] = 20U;
    plan->fifo_word[12] = computed_word;
    plan->fifo_word[13] = 58U; /* 31 + 27 */
    plan->fifo_count = 14U;
}
