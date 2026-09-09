/* Duplicated modulo-5 status tables recovered from i960 0x836d0/0x837d0. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_scheduler_mod5_status_table_836d0 {
    u32 handled;
    u32 writes_status;
    u32 status;
    u32 writes_tail;
    u32 tail_504d8c;
    u32 tail_504d90;
};

struct recovered_state_scheduler_mod5_status_table_836d0
recovered_state_scheduler_mod5_status_table_836d0(u32 table_entry,
                                                  int32_t remainder_5,
                                                  u32 caller_g14)
{
    static const u32 statuses[5] = {35U, 19U, 36U, 40U, 42U};
    struct recovered_state_scheduler_mod5_status_table_836d0 out = {
        0U, 0U, 0U, 0U, 0U, 0U
    };

    if (table_entry != 0x836d0U && table_entry != 0x837d0U)
        return out;
    if (remainder_5 < 0 || remainder_5 >= 5)
        return out;
    out.handled = 1U;
    out.writes_status = 1U;
    out.status = statuses[remainder_5];
    if (table_entry == 0x837d0U) {
        out.writes_tail = 1U;
        out.tail_504d8c = caller_g14;
        out.tail_504d90 = 15U;
    }
    return out;
}
