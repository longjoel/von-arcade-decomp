/* State-5 branch recovered from i960 0x83f9c-0x84018. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_scheduler_state5_handler_83f9c {
    u32 write_504e1c;
    u32 value_504e1c;
    u32 write_504d80;
    u32 value_504d80;
};

struct recovered_state_scheduler_state5_handler_83f9c
recovered_state_scheduler_state5_handler_83f9c(u32 mode_504e30,
                                               int32_t value_504e28,
                                               int32_t current_timing,
                                               int32_t converted_504dd8)
{
    struct recovered_state_scheduler_state5_handler_83f9c out = {
        1U, 1U, 1U, 0U
    };

    if ((mode_504e30 & 0x2U) != 0U) {
        out.value_504d80 = value_504e28 == 1 ? 26U : 37U;
    } else if (current_timing > converted_504dd8
               && (mode_504e30 & 0x4U) != 0U) {
        out.value_504d80 = 39U;
    } else {
        out.value_504d80 = 37U;
    }
    return out;
}
