/* Event setup-helper packet handoff recovered from i960 0xeac1c-eac84. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 masked_phase_word;
    recovered_u32 extended_real_word;
    recovered_u32 preserved_g14_word;
    recovered_u32 fifo_response_after_packet;
    recovered_u32 packet_replay[3];
    recovered_u32 packet_delta[3];
    recovered_u32 event_counter;
    recovered_u32 event_counter_address;
    recovered_u32 rolling_counter;
    recovered_u32 rolling_counter_address;
    recovered_u32 fifo_address;
    recovered_u32 replay_command;
    recovered_u32 delta_command;
    recovered_u32 geometry_constant;
    recovered_u32 next_target;
} recovered_geometry_event_setup_handoff_result_eac1c;

recovered_geometry_event_setup_handoff_result_eac1c
recovered_geometry_event_setup_handoff_eac1c(
    recovered_u32 masked_phase_word, recovered_u32 extended_real_word,
    recovered_u32 preserved_g14_word, recovered_u32 fifo_response_after_packet)
{
    recovered_geometry_event_setup_handoff_result_eac1c result;

    result.masked_phase_word = masked_phase_word;
    result.extended_real_word = extended_real_word;
    result.preserved_g14_word = preserved_g14_word;
    result.fifo_response_after_packet = fifo_response_after_packet;
    result.packet_replay[0] = 30U;
    result.packet_replay[1] = masked_phase_word;
    result.packet_replay[2] = extended_real_word;
    result.packet_delta[0] = 10U;
    result.packet_delta[1] = extended_real_word;
    result.packet_delta[2] = 0x430c0000U;
    result.event_counter = preserved_g14_word;
    result.event_counter_address = 0x00578400U;
    result.rolling_counter = preserved_g14_word;
    result.rolling_counter_address = 0x005783fcU;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.replay_command = 30U;
    result.delta_command = 10U;
    result.geometry_constant = 0x430c0000U;
    result.next_target = 0x000eac84U;
    return result;
}
