/* Slot-10 final service gate recovered from i960 0x1ae64-0x1aee4. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 ready_address, ready_value;
    recovered_u32 status_address, status_word, status_threshold;
    recovered_u32 result_r5, result_r6;
    recovered_u32 record_pointer, buffer_pointer;
    recovered_u32 call_count, call_target[7], call_argument[7];
    recovered_u32 completion_service, completion_argument;
    recovered_u32 completion_normal, completion_exception;
    recovered_u32 shared_service, shared_call_count;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_1ae64_completion_gate_result;

int recovered_startup_mode4_arm_1ae64_completion_gate(
    recovered_u32 ready_value, recovered_u32 status_word,
    recovered_u32 result_r5, recovered_u32 result_r6,
    recovered_u32 record_pointer, recovered_u32 buffer_pointer,
    recovered_startup_mode4_arm_1ae64_completion_gate_result *result)
{
    recovered_startup_mode4_arm_1ae64_completion_gate_result r = {0};
    r.ready_address = 0x503a7cU;
    r.ready_value = ready_value;
    r.status_address = 0x503a18U;
    r.status_word = status_word;
    r.status_threshold = 0xf423eU;
    r.result_r5 = result_r5;
    r.result_r6 = result_r6;
    r.record_pointer = record_pointer;
    r.buffer_pointer = buffer_pointer;
    r.call_count = 7U;
    r.call_target[0] = 0xbece0U;
    r.call_target[1] = 0x9b320U;
    r.call_target[2] = 0x41f20U;
    r.call_target[3] = 0xc5530U;
    r.call_target[4] = 0x6fec0U;
    r.call_target[5] = 0x71080U;
    r.call_target[6] = 0x23d60U;
    r.call_argument[0] = record_pointer;
    r.call_argument[1] = record_pointer;
    r.call_argument[4] = 0U;
    r.call_argument[5] = record_pointer;
    r.completion_service = 0x23d60U;
    r.completion_normal = 0U;
    r.completion_exception = 1U;
    r.shared_service = 0x87f60U;
    r.shared_call_count = 1U;
    r.call_argument[6] = (ready_value != 0U && status_word <= r.status_threshold &&
                           result_r5 == 0U && result_r6 == 0U) ? 0U : 1U;
    r.completion_argument = r.call_argument[6];
    r.continuation = 0x1aee4U;
    return result != (void *)0 ? (*result = r, 1) : 1;
}
