/* Callback flag decoder recovered from i960 0x8552c-0x8558c. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_callback_flag_decode_8552c {
    u32 flag_byte;
    u32 value_g1;
    u32 value_g2;
    u32 value_g3;
    u32 value_g13;
};

struct recovered_scheduler_callback_flag_decode_8552c
recovered_scheduler_callback_flag_decode_8552c(u32 table_word)
{
    struct recovered_scheduler_callback_flag_decode_8552c out = {
        (table_word & 0xff00U) >> 8, 1U, 1U, 8U, 8U
    };
    u32 flags = out.flag_byte;

    /* chkbit 4 plus bbc 5: both bits must be set for the first override. */
    if ((flags & (1U << 4)) != 0U && (flags & (1U << 5)) != 0U) {
        out.value_g1 = 2U;
        out.value_g2 = 1U;
    }
    /* bbs 0 / bbc 1: bit 0 set or bit 1 clear selects (1,2). */
    if ((flags & (1U << 0)) != 0U || (flags & (1U << 1)) == 0U) {
        out.value_g1 = 1U;
        out.value_g2 = 2U;
    }
    /* bbs 2 / bbc 3: bit 2 set or bit 3 clear selects 16. */
    if ((flags & (1U << 2)) != 0U || (flags & (1U << 3)) == 0U) {
        out.value_g3 = 16U;
        out.value_g13 = 16U;
    }
    /* bbs 6 / bbc 7: bit 6 set or bit 7 clear selects (2,2). */
    if ((flags & (1U << 6)) != 0U || (flags & (1U << 7)) == 0U) {
        out.value_g1 = 2U;
        out.value_g2 = 2U;
    }
    return out;
}
