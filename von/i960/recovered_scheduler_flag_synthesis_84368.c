/* Scheduler flag synthesis recovered from i960 0x84368-0x84470. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_flag_synthesis_84368 {
    u32 value_509a60;
    u32 set_bit0;
    u32 set_bit1;
    u32 set_bit2;
    u32 set_bit3;
    u32 set_bit4;
    u32 set_bit5;
    u32 set_bit2_or_3_final;
};

struct recovered_scheduler_flag_synthesis_84368
recovered_scheduler_flag_synthesis_84368(u32 value_509a60,
                                         u32 value_5024a4,
                                         u32 value_50249c)
{
    struct recovered_scheduler_flag_synthesis_84368 out = {
        value_509a60, 0U, 0U, 0U, 0U, 0U, 0U, 0U
    };

    if ((value_5024a4 & 0x100U) != 0U) {
        out.value_509a60 |= 1U << 4;
        out.set_bit4 = 1U;
    } else if ((value_50249c & 0x100U) != 0U) {
        out.value_509a60 |= 1U << 5;
        out.set_bit5 = 1U;
    }
    if ((value_5024a4 & 0x200U) != 0U) {
        out.value_509a60 |= 1U << 0;
        out.set_bit0 = 1U;
    } else if ((value_50249c & 0x200U) != 0U) {
        out.value_509a60 |= 1U << 1;
        out.set_bit1 = 1U;
    }
    if ((value_5024a4 & 0x400U) != 0U) {
        out.value_509a60 |= 1U << 2;
        out.set_bit2 = 1U;
    } else if ((value_50249c & 0x400U) != 0U) {
        out.value_509a60 |= 1U << 3;
        out.set_bit3 = 1U;
    }
    if ((value_5024a4 & 0x20000U) != 0U) {
        out.value_509a60 |= 1U << 2;
        out.set_bit2_or_3_final = 1U;
    } else if ((value_50249c & 0x20000U) != 0U) {
        out.value_509a60 |= 1U << 3;
        out.set_bit2_or_3_final = 1U;
    }
    return out;
}
