/* Quadword/status tail recovered from i960 0x84018-0x840a8. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_scheduler_quadword_tail_84018 {
    u32 value_504d80;
    u32 value_504d84;
    u32 value_504d88;
    u32 value_504d8c;
    u32 value_504d90;
};

struct recovered_state_scheduler_quadword_tail_84018
recovered_state_scheduler_quadword_tail_84018(u32 candidate_status,
                                             u32 mode_504e30,
                                             u32 value_504d84,
                                             u32 value_504d88,
                                             u32 value_504d8c)
{
    struct recovered_state_scheduler_quadword_tail_84018 out = {
        candidate_status, value_504d84, value_504d88, value_504d8c, 15U
    };
    u32 mode_status = 31U + mode_504e30;

    if (candidate_status == 26U || candidate_status == mode_status)
        out.value_504d90 = 30U;
    return out;
}
