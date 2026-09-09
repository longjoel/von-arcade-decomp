/* Shared helper gate recovered from i960 0x88bd0-0x88cd4. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_startup_mode4_arm_88bd0_dispatch_gate {
    u32 state_51d5e0_before;
    u32 state_51d5e0_after;
    u32 timing_51d5e4;
    u32 marker_51c9b8;
    u32 flag_51c99c_before;
    u32 flag_51c99c_after;
    u32 response_51c998;
    u32 response_51c9a0_before;
    u32 response_51c9a0_after;
    u32 status_byte;
    u32 counter_51c984;
    u32 g14_value;
    u32 initial_gate_passed;
    u32 status_gate_passed;
    u32 dispatch_selector;
    u32 dispatch_table_address;
    u32 continuation;
};

struct recovered_startup_mode4_arm_88bd0_dispatch_gate
recovered_startup_mode4_arm_88bd0_dispatch_gate(
    u32 state_51d5e0, u32 timing_51d5e4, u32 marker_51c9b8,
    u32 flag_51c99c, u32 response_51c998, u32 response_51c9a0,
    u32 status_byte, u32 counter_51c984, u32 g14_value)
{
    struct recovered_startup_mode4_arm_88bd0_dispatch_gate out;
    u32 initial_state = state_51d5e0;

    out.state_51d5e0_before = state_51d5e0;
    out.state_51d5e0_after = state_51d5e0;
    out.timing_51d5e4 = timing_51d5e4;
    out.marker_51c9b8 = marker_51c9b8;
    out.flag_51c99c_before = flag_51c99c;
    out.flag_51c99c_after = flag_51c99c;
    out.response_51c998 = response_51c998;
    out.response_51c9a0_before = response_51c9a0;
    out.response_51c9a0_after = response_51c9a0;
    out.status_byte = status_byte;
    out.counter_51c984 = counter_51c984;
    out.g14_value = g14_value;
    out.dispatch_table_address = 0x00088cecU;
    out.continuation = 0x00088cd4U;

    if (initial_state == 0U && timing_51d5e4 == marker_51c9b8)
        out.state_51d5e0_after = 1U;
    out.initial_gate_passed = initial_state == 0U || flag_51c99c == 1U ? 1U : 0U;
    if (out.initial_gate_passed == 0U)
        return out;
    if (flag_51c99c < 1U)
        return out;

    if (timing_51d5e4 == response_51c998)
        out.response_51c9a0_after = g14_value;
    out.status_gate_passed = status_byte != 0U ? 1U : 0U;
    if (status_byte != 0U && out.response_51c9a0_after != 1U) {
        out.flag_51c99c_after = 2U;
    } else if (counter_51c984 > 0x95U) {
        out.flag_51c99c_after = g14_value;
    } else {
        out.flag_51c99c_after = 1U;
    }
    out.dispatch_selector = out.flag_51c99c_after;
    return out;
}
