/* Selected-profile packet prefix recovered from i960 0x779f0-0x77a64. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 selected_index;
    recovered_u32 converted_table_word0;
    recovered_u32 converted_table_word2;
    recovered_u32 object_word8;
    recovered_u32 object_word10;
} recovered_match_profile_packet_prefix_input_779f0;

typedef struct {
    recovered_u32 table_base;
    recovered_u32 record_stride;
    recovered_u32 record_offset;
    recovered_u32 command31_words[5];
    recovered_u32 command31_word_count;
    recovered_u32 next_command;
    recovered_u32 fifo_destination;
} recovered_match_profile_packet_prefix_result_779f0;

/*
 * The selected record is addressed as index*6.  The first fixed request at
 * 0x779f0 emits command 31 followed by the converted record +0/+2 values
 * interleaved with object +0x08/+0x10.  The command-29/30 requests begin
 * after the response read at 0x77a5c and are intentionally outside this
 * prefix contract.
 */
void recovered_match_profile_packet_prefix_779f0(
    const recovered_match_profile_packet_prefix_input_779f0 *input,
    recovered_match_profile_packet_prefix_result_779f0 *result)
{
    result->table_base = 0x00505060U;
    result->record_stride = 6U;
    result->record_offset = input->selected_index * 6U;
    result->command31_words[0] = 31U;
    result->command31_words[1] = input->converted_table_word0;
    result->command31_words[2] = input->object_word8;
    result->command31_words[3] = input->converted_table_word2;
    result->command31_words[4] = input->object_word10;
    result->command31_word_count = 5U;
    result->next_command = 29U;
    result->fifo_destination = RECOVERED_FIFO_ADDRESS;
}
