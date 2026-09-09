/* Slot-10 progress/controller gate recovered from i960 0x1a578-0x1a5cc. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 counter_address, counter_before;
    recovered_u32 controller_byte_address, controller_byte;
    recovered_u32 controller_word_address, controller_word;
    recovered_u32 helper_address, helper_call_count, helper_argument;
    recovered_u32 helper_argument_valid;
    recovered_u32 status_continuation;
} recovered_startup_mode4_arm_1a578_progress_gate_result;

int recovered_startup_mode4_arm_1a578_progress_gate(
    recovered_u32 counter_value, recovered_u32 controller_byte,
    recovered_u32 controller_word,
    recovered_startup_mode4_arm_1a578_progress_gate_result *result)
{
    recovered_startup_mode4_arm_1a578_progress_gate_result r = {0};
    r.counter_address = 0x503a94U;
    r.counter_before = counter_value;
    r.controller_byte_address = 0x5024e8U;
    r.controller_byte = controller_byte & 0xffU;
    r.controller_word_address = 0x5024e8U;
    r.controller_word = controller_word;
    r.helper_address = 0x19b50U;
    r.status_continuation = 0x1a5ccU;

    /* cmpibge 0,g0 skips the block for non-negative signed counters. */
    if ((int32_t)counter_value < 0) {
        if (r.controller_byte == 0U) {
            r.helper_call_count = 1U;
            r.helper_argument = counter_value - 1U;
            r.helper_argument_valid = 1U;
        } else if (r.controller_byte > 64U) {
            recovered_u32 low_bits = controller_word & 31U;
            if (low_bits == 0U || low_bits == 16U) {
                r.helper_call_count = 1U;
                r.helper_argument = low_bits;
                r.helper_argument_valid = 1U;
            }
        }
    }
    if (result != (void *)0)
        *result = r;
    return 1;
}
