/* Status tail recovered from i960 0x8168c-0x816c8. */

#include <stdint.h>

typedef uint32_t u32;

u32 recovered_transition_status_tail_8168c(int32_t global_504d70,
                                           int32_t value_5024e8)
{
    int32_t remainder;

    if (global_504d70 == 2 || global_504d70 == 7)
        return 18U;
    remainder = value_5024e8 % 240;
    return remainder <= 0x77 ? 18U : 19U;
}
