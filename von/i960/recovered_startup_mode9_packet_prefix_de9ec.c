/* Mode-9 startup packet prefix recovered from i960 0xde9ec-0xdea6c. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 status_pair_5040d8_0;
    recovered_u32 status_pair_5040d8_1;
    recovered_u32 status_word_5040e0;
    recovered_u32 geometry_pair_503ad8_0;
    recovered_u32 geometry_pair_503ad8_1;
    recovered_u32 geometry_word_503ae0;
} recovered_startup_mode9_packet_prefix_input_de9ec;

typedef struct {
    recovered_u32 packet_words[10];
    recovered_u32 packet_word_count;
    recovered_u32 fifo_destination;
    recovered_u32 first_command;
    recovered_u32 second_command;
    recovered_u32 constant_word;
} recovered_startup_mode9_packet_prefix_result_de9ec;

/*
 * The mode-9 fall-through emits command 38 with the 0x5040d8 pair, the
 * 0x5040e0 word, constant 0x428c0000, and zero; it then emits command 39
 * with the 0x503ad8 pair and 0x503ae0 word.
 */
void recovered_startup_mode9_packet_prefix_de9ec(
    const recovered_startup_mode9_packet_prefix_input_de9ec *input,
    recovered_startup_mode9_packet_prefix_result_de9ec *result)
{
    result->packet_words[0] = 38U;
    result->packet_words[1] = input->status_pair_5040d8_0;
    result->packet_words[2] = input->status_pair_5040d8_1;
    result->packet_words[3] = input->status_word_5040e0;
    result->packet_words[4] = 0x428c0000U;
    result->packet_words[5] = 0U;
    result->packet_words[6] = 39U;
    result->packet_words[7] = input->geometry_pair_503ad8_0;
    result->packet_words[8] = input->geometry_pair_503ad8_1;
    result->packet_words[9] = input->geometry_word_503ae0;
    result->packet_word_count = 10U;
    result->fifo_destination = RECOVERED_FIFO_ADDRESS;
    result->first_command = 38U;
    result->second_command = 39U;
    result->constant_word = 0x428c0000U;
}
