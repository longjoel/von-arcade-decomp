/* Setup prefix recovered from i960 0x84330-0x84368. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_setup_prefix_84330 {
    u32 stack_adjust;
    u32 clear_509a60;
    u32 clear_words;
    u32 low_two_bits;
};

struct recovered_scheduler_setup_prefix_84330
recovered_scheduler_setup_prefix_84330(u32 value_5024e8)
{
    struct recovered_scheduler_setup_prefix_84330 out = {
        16U, 0U, 0U, value_5024e8 & 3U
    };

    if (out.low_two_bits == 0U) {
        out.clear_509a60 = 1U;
        out.clear_words = 3U;
    }
    return out;
}
