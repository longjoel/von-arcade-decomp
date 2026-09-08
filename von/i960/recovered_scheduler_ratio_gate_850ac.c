/* Low-byte gate recovered from i960 0x850ac-0x850c0. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_ratio_gate_850ac {
    u32 low_byte;
    u32 exits_to_85128;
    u32 continues_to_ratio_setup;
};

struct recovered_scheduler_ratio_gate_850ac
recovered_scheduler_ratio_gate_850ac(u32 value_5024e8)
{
    u32 low_byte = value_5024e8 & 0xffU;
    struct recovered_scheduler_ratio_gate_850ac out = {
        low_byte, 0U, 0U
    };

    /* cmpobl 10,g4 is literal-first: only values above 10 exit. */
    if (low_byte > 10U)
        out.exits_to_85128 = 1U;
    else
        out.continues_to_ratio_setup = 1U;
    return out;
}
