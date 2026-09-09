/* Event setup-helper state prefix recovered from i960 0xeab48-eac1c. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 prior_fifo_word;
    recovered_u32 workspace_word_8_left;
    recovered_u32 workspace_word_8_right;
    recovered_u32 phase_word;
    recovered_u32 phase_word_plus_0x4000;
    recovered_u32 masked_phase_word;
    recovered_u32 extended_real_word;
    recovered_u32 converted_extended_real_word;
    recovered_u32 divided_extended_real_word;
    recovered_u32 preserved_g14_word;
    recovered_u32 workspace_word_8_sum;
    recovered_u32 packet_first[3];
    recovered_u32 packet_second[3];
    recovered_u32 state_3e4;
    recovered_u32 state_3e6;
    recovered_u32 state_3e8;
    recovered_u32 state_3ec;
    recovered_u32 state_3f0;
    recovered_u32 state_3f4;
    recovered_u32 state_address_base;
    recovered_u32 fifo_address;
    recovered_u32 geometry_command;
    recovered_u32 completion_command;
    recovered_u32 next_target;
} recovered_geometry_event_setup_state_prefix_result_eab48;

recovered_geometry_event_setup_state_prefix_result_eab48
recovered_geometry_event_setup_state_prefix_eab48(
    recovered_u32 prior_fifo_word, recovered_u32 phase_word,
    recovered_u32 workspace_word_8_left, recovered_u32 workspace_word_8_right,
    recovered_u32 extended_real_word, recovered_u32 converted_extended_real_word,
    recovered_u32 divided_extended_real_word, recovered_u32 preserved_g14_word)
{
    recovered_geometry_event_setup_state_prefix_result_eab48 result;

    result.prior_fifo_word = prior_fifo_word;
    result.workspace_word_8_left = workspace_word_8_left;
    result.workspace_word_8_right = workspace_word_8_right;
    result.phase_word = phase_word;
    result.phase_word_plus_0x4000 = phase_word + 0x4000U;
    result.masked_phase_word = result.phase_word_plus_0x4000 & 0xffffU;
    result.extended_real_word = extended_real_word;
    result.converted_extended_real_word = converted_extended_real_word;
    result.divided_extended_real_word = divided_extended_real_word;
    result.preserved_g14_word = preserved_g14_word;
    result.workspace_word_8_sum = workspace_word_8_left + workspace_word_8_right;

    result.packet_first[0] = 29U;
    result.packet_first[1] = result.masked_phase_word;
    result.packet_first[2] = extended_real_word;
    result.packet_second[0] = 30U;
    result.packet_second[1] = result.masked_phase_word;
    result.packet_second[2] = extended_real_word;

    result.state_3e4 = result.phase_word_plus_0x4000;
    result.state_3e6 = preserved_g14_word;
    result.state_3e8 = preserved_g14_word;
    result.state_3ec = extended_real_word;
    result.state_3f0 = converted_extended_real_word;
    result.state_3f4 = divided_extended_real_word;
    result.state_address_base = 0x005783e4U;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.geometry_command = 29U;
    result.completion_command = 30U;
    result.next_target = 0x000eac1cU;
    return result;
}
