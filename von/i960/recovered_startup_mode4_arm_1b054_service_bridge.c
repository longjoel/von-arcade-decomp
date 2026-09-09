/* Slot-11 post-prefix service bridge recovered from i960 0x1b054-0x1b160. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 ready_address, ready_value;
    recovered_u32 record_pointer, callback_target_a, callback_target_b;
    recovered_u32 state_address, state_value;
    recovered_u32 first_numerator_address, first_numerator_raw, first_numerator_signed;
    recovered_u32 second_numerator_address, second_numerator_raw, second_numerator_signed;
    recovered_u32 first_timer_address, second_timer_address;
    recovered_u32 first_timer_value, second_timer_value;
    recovered_u32 call_count, conditional_call_included;
    recovered_u32 call_target[24], call_argument[24];
    recovered_u32 continuation;
} recovered_startup_mode4_arm_1b054_service_bridge_result;

int recovered_startup_mode4_arm_1b054_service_bridge(
    recovered_u32 ready_value, recovered_u32 record_pointer,
    recovered_u32 callback_target_a, recovered_u32 callback_target_b,
    recovered_u32 state_value, recovered_u32 first_numerator_raw,
    recovered_u32 second_numerator_raw,
    recovered_startup_mode4_arm_1b054_service_bridge_result *result)
{
    recovered_startup_mode4_arm_1b054_service_bridge_result r = {0};
    r.ready_address = 0x503a7cU;
    r.ready_value = ready_value;
    r.record_pointer = record_pointer;
    r.callback_target_a = callback_target_a;
    r.callback_target_b = callback_target_b;
    r.state_address = 0x503ab0U;
    r.state_value = state_value;
    r.first_numerator_address = 0x503ca2U;
    r.first_numerator_raw = first_numerator_raw;
    r.first_numerator_signed = (recovered_u32)recovered_sign_extend_16(first_numerator_raw);
    r.second_numerator_address = 0x5042a2U;
    r.second_numerator_raw = second_numerator_raw;
    r.second_numerator_signed = (recovered_u32)recovered_sign_extend_16(second_numerator_raw);
    r.first_timer_address = 0x503ca0U;
    r.second_timer_address = 0x5042a0U;
    r.first_timer_value = r.first_numerator_signed;
    r.second_timer_value = r.second_numerator_signed;
    r.conditional_call_included = ready_value == 0U ? 1U : 0U;
    r.call_count = 23U + r.conditional_call_included;
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
    r.call_target[11] = 0xdf070U;
    r.call_target[12] = 0x26cb8U;
    r.call_target[13] = 0xbd810U;
    r.call_target[14] = callback_target_b;
    r.call_target[15] = 0xdf070U;
    r.call_target[16] = 0xbece0U;
    r.call_target[17] = 0x9b320U;
    r.call_target[18] = 0x41f20U;
    r.call_target[19] = 0xc5530U;
    r.call_target[20] = 0x6fec0U;
    r.call_target[21] = 0x71080U;
    r.call_target[22] = 0x23d60U;
    r.call_target[23] = 0x8d0b8U;
    r.call_argument[2] = 0U;
    r.call_argument[4] = 0U;
    r.call_argument[6] = record_pointer;
    r.call_argument[8] = record_pointer;
    r.call_argument[9] = record_pointer;
    r.call_argument[10] = record_pointer;
    r.call_argument[11] = record_pointer;
    r.call_argument[12] = 0x5040d0U;
    r.call_argument[13] = 0x5040d0U;
    r.call_argument[14] = 0x5040d0U;
    r.call_argument[15] = 0x5040d0U;
    r.call_argument[16] = record_pointer;
    r.call_argument[20] = 0U;
    r.call_argument[21] = record_pointer;
    r.call_argument[22] = 0U;
    r.call_argument[23] = state_value;
    r.continuation = 0x1b160U;
    if (result != (void *)0)
        *result = r;
    return 1;
}
