/* Control/ABI gate recovered from i960 0x85080-0x850ac. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_control_gate_85080 {
    u32 saved_g8;
    u32 saved_g12;
    u32 restored_g8;
    u32 restored_g12;
    u32 returns_immediately;
    u32 continues_to_850ac;
};

struct recovered_scheduler_control_gate_85080
recovered_scheduler_control_gate_85080(u32 incoming_g8, u32 incoming_g12,
                                       u32 value_504e50)
{
    struct recovered_scheduler_control_gate_85080 out = {
        incoming_g8, incoming_g12, incoming_g8, incoming_g12, 0U, 0U
    };

    if ((value_504e50 & 1U) != 0U)
        out.returns_immediately = 1U;
    else
        out.continues_to_850ac = 1U;
    return out;
}
