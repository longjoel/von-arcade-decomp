/* Remainder/mode handler recovered from i960 0x8342c-0x834a8. */

#include <stdint.h>

typedef uint32_t u32;

enum recovered_state_scheduler_remainder_handler_8342c_route {
    RECOVERED_REMAINDER_8342C_CALL_79D60 = 0,
    RECOVERED_REMAINDER_8342C_VALUE_21 = 1,
    RECOVERED_REMAINDER_8342C_VALUE_26 = 2,
    RECOVERED_REMAINDER_8342C_VALUE_28 = 3
};

struct recovered_state_scheduler_remainder_handler_8342c {
    enum recovered_state_scheduler_remainder_handler_8342c_route route;
    u32 value_504d80;
    u32 value_504d8c;
    u32 value_504d90;
};

struct recovered_state_scheduler_remainder_handler_8342c
recovered_state_scheduler_remainder_handler_8342c(int32_t remainder_6,
                                                  u32 mode_504e30,
                                                  u32 caller_g14)
{
    struct recovered_state_scheduler_remainder_handler_8342c out = {
        RECOVERED_REMAINDER_8342C_CALL_79D60, 0U, caller_g14, 15U
    };

    if (remainder_6 == 5) {
        out.route = RECOVERED_REMAINDER_8342C_VALUE_21;
        out.value_504d80 = 21U;
    } else if (remainder_6 == 4 && (mode_504e30 & 0x2U) != 0U) {
        out.route = RECOVERED_REMAINDER_8342C_VALUE_26;
        out.value_504d80 = 26U;
    } else if (remainder_6 < 0 && (mode_504e30 & 0x4U) != 0U) {
        out.route = RECOVERED_REMAINDER_8342C_VALUE_28;
        out.value_504d80 = 28U;
    }
    return out;
}
