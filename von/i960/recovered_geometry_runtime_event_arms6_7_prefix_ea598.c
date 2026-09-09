/* Runtime event arms 6/7 packet prefixes recovered from i960 0xea598-0xea684. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 variant;
    recovered_u32 record_word_184;
    recovered_u32 record_word_8;
    recovered_u32 record_word_10;
    recovered_u32 record_word_c;
    recovered_u32 fifo_geometry_value;
    recovered_u32 fifo_completion_value;
    recovered_u32 adjusted_geometry_word;
    recovered_u32 masked_geometry_word;
    recovered_u32 packet[6];
    recovered_u32 packet_count;
    recovered_u32 record_word_184_offset;
    recovered_u32 record_word_8_offset;
    recovered_u32 record_word_10_offset;
    recovered_u32 record_word_c_offset;
    recovered_u32 fifo_address;
    recovered_u32 geometry_constant;
    recovered_u32 geometry_command;
    recovered_u32 completion_command;
    recovered_u32 shared_continuation;
} recovered_geometry_runtime_event_arms6_7_prefix_result_ea598;

recovered_geometry_runtime_event_arms6_7_prefix_result_ea598
recovered_geometry_runtime_event_arms6_7_prefix_ea598(
    recovered_u32 variant, recovered_u32 record_word_184,
    recovered_u32 record_word_8, recovered_u32 record_word_10,
    recovered_u32 record_word_c, recovered_u32 fifo_geometry_value,
    recovered_u32 fifo_completion_value)
{
    recovered_geometry_runtime_event_arms6_7_prefix_result_ea598 result;
    recovered_u32 offset = variant == 0U ? 0x6000U : 0xffffa000U;

    result.variant = variant;
    result.record_word_184 = record_word_184;
    result.record_word_8 = record_word_8;
    result.record_word_10 = record_word_10;
    result.record_word_c = record_word_c;
    result.fifo_geometry_value = fifo_geometry_value;
    result.fifo_completion_value = fifo_completion_value;
    result.adjusted_geometry_word = record_word_184 + offset;
    result.masked_geometry_word = result.adjusted_geometry_word & 0xffffU;
    result.packet[0] = 29U;
    result.packet[1] = result.masked_geometry_word;
    result.packet[2] = 0x430c0000U;
    result.packet[3] = 30U;
    result.packet[4] = result.masked_geometry_word;
    result.packet[5] = 0x430c0000U;
    result.packet_count = 6U;
    result.record_word_184_offset = 0x184U;
    result.record_word_8_offset = 0x8U;
    result.record_word_10_offset = 0x10U;
    result.record_word_c_offset = 0xcU;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.geometry_constant = 0x430c0000U;
    result.geometry_command = 29U;
    result.completion_command = 30U;
    result.shared_continuation = 0x000ea684U;
    return result;
}
