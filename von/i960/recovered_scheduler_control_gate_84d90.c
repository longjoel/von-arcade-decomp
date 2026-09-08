/* Control/ABI gate recovered from i960 0x84d90-0x84dc4. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_control_gate_84d90 {
    u32 saved_g8;
    u32 restored_g8;
    u32 returns_immediately;
    u32 continues_to_84dc4;
};

struct recovered_scheduler_control_gate_84d90
recovered_scheduler_control_gate_84d90(u32 incoming_g8, u32 value_504e50)
{
    struct recovered_scheduler_control_gate_84d90 out = {
        incoming_g8, incoming_g8, 0U, 0U
    };

    if ((value_504e50 & 1U) != 0U)
        out.returns_immediately = 1U;
    else
        out.continues_to_84dc4 = 1U;
    return out;
}
