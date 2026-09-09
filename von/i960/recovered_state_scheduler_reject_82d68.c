/* Scheduler reject pre-tail recovered from i960 0x82d68-0x82d74. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_scheduler_reject_82d68 {
    u32 input_value_504d80;
    u32 rejected_value_504d80;
    u32 destination;
    u32 tail_target;
};

struct recovered_state_scheduler_reject_82d68
recovered_state_scheduler_reject_82d68(u32 input_value_504d80)
{
    struct recovered_state_scheduler_reject_82d68 out = {
        input_value_504d80, 8U, 0x00504d80U, 0x00082d74U
    };
    return out;
}
