/* Recovery status tail recovered from i960 0x84d60-0x84d80. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_recovery_status_tail_84d60 {
    u32 value_509ac0;
    u32 value_509b10;
};

struct recovered_scheduler_recovery_status_tail_84d60
recovered_scheduler_recovery_status_tail_84d60(u32 recovery_flag,
                                               u32 value_504e50)
{
    struct recovered_scheduler_recovery_status_tail_84d60 out = {
        recovery_flag, (value_504e50 >> 3) & 1U
    };
    return out;
}
