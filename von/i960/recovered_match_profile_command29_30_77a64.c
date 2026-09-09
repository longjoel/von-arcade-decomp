/* Command-29/30 request pair recovered from i960 0x77a64-0x77af0. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 command31_response;
    recovered_u32 converted_record_word4;
} recovered_match_profile_command29_30_input_77a64;

typedef struct {
    recovered_u32 masked_response_lane;
    recovered_u32 command29_words[3];
    recovered_u32 command30_words[3];
    recovered_u32 command_word_count;
    recovered_u32 fifo_destination;
} recovered_match_profile_command29_30_result_77a64;

/*
 * After the command-31 response, the source adds 0x3000 and masks to a
 * halfword.  It emits command 29 and command 30 with that lane and the
 * converted record +4 value; the command-30 response is read at 0x77af0.
 */
void recovered_match_profile_command29_30_77a64(
    const recovered_match_profile_command29_30_input_77a64 *input,
    recovered_match_profile_command29_30_result_77a64 *result)
{
    result->masked_response_lane =
        (input->command31_response + 0x3000U) & 0xffffU;
    result->command29_words[0] = 29U;
    result->command29_words[1] = result->masked_response_lane;
    result->command29_words[2] = input->converted_record_word4;
    result->command30_words[0] = 30U;
    result->command30_words[1] = result->masked_response_lane;
    result->command30_words[2] = input->converted_record_word4;
    result->command_word_count = 3U;
    result->fifo_destination = RECOVERED_FIFO_ADDRESS;
}
