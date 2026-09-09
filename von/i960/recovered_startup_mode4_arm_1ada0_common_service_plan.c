/* Slot-10 common-service call plan recovered from i960 0x1ada0-0x1ae64. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 ready_address, ready_value;
    recovered_u32 record_pointer, callback_target_a, callback_target_b;
    recovered_u32 call_count, conditional_call_included;
    recovered_u32 call_target[17], call_argument[17];
    recovered_u32 continuation;
} recovered_startup_mode4_arm_1ada0_common_service_plan_result;

int recovered_startup_mode4_arm_1ada0_common_service_plan(
    recovered_u32 ready_value, recovered_u32 record_pointer,
    recovered_u32 callback_target_a, recovered_u32 callback_target_b,
    recovered_startup_mode4_arm_1ada0_common_service_plan_result *result)
{
    recovered_startup_mode4_arm_1ada0_common_service_plan_result r = {0};
    r.ready_address = 0x503a7cU;
    r.ready_value = ready_value;
    r.record_pointer = record_pointer;
    r.callback_target_a = callback_target_a;
    r.callback_target_b = callback_target_b;
    r.conditional_call_included = ready_value == 0U ? 1U : 0U;
    r.call_count = r.conditional_call_included != 0U ? 17U : 16U;
    r.call_target[0] = 0xde630U;
    r.call_target[1] = 0xc8f10U;
    r.call_target[2] = 0x6fec0U;
    r.call_target[3] = 0x9b308U;
    r.call_target[4] = 0x6fec0U;
    r.call_target[5] = 0xc8f60U;
    r.call_target[6] = 0x9baa0U;
    r.call_target[7] = 0xde990U;
    r.call_target[8] = 0xbe1f0U;
    r.call_target[9] = 0xbd730U;
    r.call_target[10] = callback_target_a;
    r.call_target[11] = 0x23980U;
    r.call_target[12] = 0xdf070U;
    r.call_target[13] = 0x26cb8U;
    r.call_target[14] = 0xbd810U;
    r.call_target[15] = callback_target_b;
    r.call_target[16] = 0xdf070U;
    r.call_argument[2] = 0U;
    r.call_argument[4] = 0U;
    r.call_argument[6] = record_pointer;
    r.call_argument[8] = record_pointer;
    r.call_argument[9] = record_pointer;
    r.call_argument[10] = record_pointer;
    r.call_argument[11] = record_pointer;
    r.call_argument[12] = record_pointer;
    r.call_argument[13] = 0x5040d0U;
    r.call_argument[14] = 0x5040d0U;
    r.call_argument[15] = 0x5040d0U;
    r.call_argument[16] = 0x5040d0U;
    r.continuation = 0x1ae64U;
    if (result != (void *)0)
        *result = r;
    return 1;
}
