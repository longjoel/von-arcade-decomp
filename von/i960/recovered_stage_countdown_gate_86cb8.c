/* Countdown/call gate recovered from i960 0x86cb8-0x86d38. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_stage_countdown_gate_86cb8 {
    u32 control_value;
    u32 counter_before;
    u32 counter_after;
    u32 flag_word_5024a4;
    u32 exception_word_5024f4;
    u32 decremented_address;
    u32 calls_clear_service;
    u32 clear_service_target;
    u32 clear_service_argument;
    u32 continuation;
};

struct recovered_stage_countdown_gate_86cb8
recovered_stage_countdown_gate_86cb8(u32 control_value,
                                     u32 counter_before,
                                     u32 flag_word_5024a4,
                                     u32 exception_word_5024f4,
                                     u32 caller_g0)
{
    struct recovered_stage_countdown_gate_86cb8 out;
    u32 counter_after = counter_before - 1U;
    u32 low_counter_bit_path = counter_after <= 0x57U &&
                               ((flag_word_5024a4 >> 4) & 1U) != 0U;
    u32 high_exception_word = exception_word_5024f4 == 0x60U ||
                              exception_word_5024f4 == 0x62U;

    out.control_value = control_value;
    out.counter_before = counter_before;
    out.counter_after = counter_after;
    out.flag_word_5024a4 = flag_word_5024a4;
    out.exception_word_5024f4 = exception_word_5024f4;
    out.decremented_address = 0x00503a04U;
    out.calls_clear_service = counter_after == 0U || low_counter_bit_path ||
                              (control_value != 0U && high_exception_word);
    out.clear_service_target = 0x0001fe90U;
    /* 0x86d38 calls 0x1fe90 before changing g0, so it inherits caller_g0. */
    out.clear_service_argument = caller_g0;
    out.continuation = out.calls_clear_service != 0U
                           ? 0x00086d38U : 0x00086db4U;
    return out;
}
