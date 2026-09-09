/* Runtime event arm 0 fixed-point/state prefix recovered from i960 0xe9470-0xe95a0. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 prior_phase;
    recovered_u32 record_word_184;
    recovered_u32 record_word_8;
    recovered_u32 record_word_10;
    recovered_u32 record_word_c;
    recovered_u32 fifo_geometry_value;
    recovered_u32 fifo_completion_value;
    recovered_u32 adjusted_record_base;
    recovered_u32 phase_plus_0x100;
    recovered_u32 masked_geometry_word;
    recovered_u32 negated_word_c;
    recovered_u32 packet[6];
    recovered_u32 packet_count;
    recovered_u32 state_3e4;
    recovered_u32 state_3e6;
    recovered_u32 state_3e8;
    recovered_u32 state_3ec;
    recovered_u32 state_3f4;
    recovered_u32 state_3f8;
    recovered_u32 state_address_base;
    recovered_u32 fifo_address;
    recovered_u32 continuation_target;
} recovered_geometry_runtime_event_arm0_result_e9470;

recovered_geometry_runtime_event_arm0_result_e9470
recovered_geometry_runtime_event_arm0_e9470(
    recovered_u32 prior_phase, recovered_u32 record_word_184,
    recovered_u32 record_word_8, recovered_u32 record_word_10,
    recovered_u32 record_word_c, recovered_u32 fifo_geometry_value,
    recovered_u32 fifo_completion_value)
{
    recovered_geometry_runtime_event_arm0_result_e9470 result;

    result.prior_phase = prior_phase;
    result.record_word_184 = record_word_184;
    result.record_word_8 = record_word_8;
    result.record_word_10 = record_word_10;
    result.record_word_c = record_word_c;
    result.fifo_geometry_value = fifo_geometry_value;
    result.fifo_completion_value = fifo_completion_value;
    result.adjusted_record_base = record_word_184 + 0x3000U;
    result.phase_plus_0x100 = prior_phase + 0x100U;
    result.masked_geometry_word =
        (result.adjusted_record_base + result.phase_plus_0x100) & 0xffffU;
    result.negated_word_c = 0U - record_word_c;
    result.packet[0] = 29U;
    result.packet[1] = result.masked_geometry_word;
    result.packet[2] = 0x43020000U;
    result.packet[3] = 30U;
    result.packet[4] = result.masked_geometry_word;
    result.packet[5] = 0x43020000U;
    result.packet_count = 6U;
    result.state_3e4 = result.adjusted_record_base + result.phase_plus_0x100;
    result.state_3e6 = result.phase_plus_0x100;
    result.state_3e8 = 0U;
    result.state_3ec = 0x43020000U;
    result.state_3f4 = fifo_geometry_value + record_word_8;
    result.state_3f8 = record_word_10 - fifo_completion_value;
    result.state_address_base = 0x005783e4U;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.continuation_target = 0x000ea720U;
    return result;
}
