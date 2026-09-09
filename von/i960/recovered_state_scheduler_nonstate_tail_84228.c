/* Shared non-state scheduler tail recovered from i960 0x84228-0x8423c. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_scheduler_nonstate_tail_84228 {
    u32 write_504d80;
    u32 value_504d80;
    u32 write_504d8c;
    u32 value_504d8c;
    u32 write_504d90;
    u32 value_504d90;
};

struct recovered_state_scheduler_nonstate_tail_84228
recovered_state_scheduler_nonstate_tail_84228(u32 candidate_status,
                                              u32 caller_g14)
{
    struct recovered_state_scheduler_nonstate_tail_84228 out = {
        1U, candidate_status, 1U, caller_g14, 1U, 15U
    };
    return out;
}
