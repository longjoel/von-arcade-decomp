/* Shared post-epilogue dispatch recovered from i960 0x8bfd0-0x8c0c8. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 initial_selector;
    recovered_u32 scan_word_51c998;
    recovered_u32 candidate_51d5e4;
    recovered_u32 mode_byte;
    recovered_u32 state_51c9a0;
    recovered_u32 g14_value;
    recovered_u32 retry_51c9a8;
    recovered_u32 selector_51c99c;
    recovered_u32 state_updated;
    recovered_u32 retry_limit;
    recovered_u32 retry_promoted;
    recovered_u32 current_record_10;
    recovered_u32 linked_record_10;
    recovered_u32 current_record_8;
    recovered_u32 linked_record_8;
    recovered_u32 delta_10;
    recovered_u32 delta_8;
    recovered_u32 packet_command;
    recovered_u32 fifo_response;
    recovered_u32 continuation;
} recovered_startup_mode4_common_dispatch_8bfd0_result;

recovered_startup_mode4_common_dispatch_8bfd0_result
recovered_startup_mode4_common_dispatch_8bfd0(
    recovered_u32 initial_selector, recovered_u32 scan_word_51c998,
    recovered_u32 candidate_51d5e4, recovered_u32 mode_byte,
    recovered_u32 state_51c9a0, recovered_u32 g14_value,
    recovered_u32 retry_51c9a8, recovered_u32 current_record_10,
    recovered_u32 linked_record_10, recovered_u32 current_record_8,
    recovered_u32 linked_record_8, recovered_u32 fifo_response)
{
    recovered_startup_mode4_common_dispatch_8bfd0_result result;

    result.initial_selector = initial_selector;
    result.scan_word_51c998 = scan_word_51c998;
    result.candidate_51d5e4 = candidate_51d5e4;
    result.mode_byte = mode_byte;
    result.state_51c9a0 = state_51c9a0;
    result.g14_value = g14_value;
    result.retry_51c9a8 = retry_51c9a8;
    result.selector_51c99c = initial_selector;
    result.state_updated = 0U;
    result.retry_limit = 9U;
    result.retry_promoted = 0U;
    if (initial_selector == 0U) {
        if (scan_word_51c998 == candidate_51d5e4) {
            result.state_51c9a0 = g14_value;
            result.state_updated = 1U;
        }
        if (mode_byte == 0U)
            result.selector_51c99c = result.state_51c9a0 == 1U ? 1U : g14_value;
    }
    if (result.selector_51c99c == 1U) {
        result.retry_51c9a8 = retry_51c9a8 + 1U;
        if (result.retry_51c9a8 < 9U) {
            result.selector_51c99c = g14_value;
            result.retry_promoted = 1U;
        }
    }
    result.current_record_10 = current_record_10;
    result.linked_record_10 = linked_record_10;
    result.current_record_8 = current_record_8;
    result.linked_record_8 = linked_record_8;
    result.delta_10 = current_record_10 - linked_record_10;
    result.delta_8 = current_record_8 - linked_record_8;
    result.packet_command = 10U;
    result.fifo_response = fifo_response;
    result.continuation = 0x0008c0c8U;
    return result;
}
