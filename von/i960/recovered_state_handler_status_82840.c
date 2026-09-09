/* Random/status selector handlers recovered from i960 0x82840-0x82954. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_handler_status_82840 {
    u32 accepted;
    u32 status;
    u32 random_calls;
    int32_t first_remainder;
    int32_t second_remainder;
};

static int32_t rem3(int32_t value) { return value % 3; }
static int32_t rem10(int32_t value) { return value % 10; }

struct recovered_state_handler_status_82840
recovered_state_handler_status_82840(u32 selector, int32_t global_504d60,
                                     int32_t random1, int32_t random2)
{
    struct recovered_state_handler_status_82840 out = {
        0U, 29U, 0U, 0U, 0U
    };
    int32_t remainder;

    if (selector > 9U)
        return out;
    out.accepted = 1U;
    switch (selector) {
    case 0U:
        out.random_calls = 2U;
        out.first_remainder = rem3(random1);
        if (out.first_remainder <= 1) {
            out.second_remainder = rem3(random2);
            out.status = (u32)(13 + out.second_remainder);
        } else {
            out.second_remainder = rem10(random2);
            out.status = out.second_remainder <= 2 ? 30U : 29U;
        }
        break;
    case 1U:
        out.random_calls = 1U;
        remainder = rem10(random1);
        out.second_remainder = remainder;
        out.status = remainder <= 4 ? 30U : 29U;
        break;
    case 2U:
        out.random_calls = 1U;
        remainder = rem10(random1);
        out.second_remainder = remainder;
        out.status = remainder <= 4 ? 30U : 29U;
        break;
    case 3U:
    case 4U:
        out.random_calls = 1U;
        remainder = rem10(random1);
        out.second_remainder = remainder;
        out.status = remainder <= 4 ? 30U : 29U;
        break;
    case 5U:
        out.random_calls = 1U;
        remainder = rem10(random1);
        out.second_remainder = remainder;
        out.status = remainder <= 4 ? 30U : 29U;
        break;
    case 6U:
        if (global_504d60 < 0) {
            out.random_calls = 1U;
            out.first_remainder = rem3(random1);
            if (out.first_remainder <= 1) {
                out.status = 13U;
            } else {
                out.random_calls = 2U;
                out.second_remainder = rem10(random2);
                out.status = out.second_remainder <= 2 ? 30U : 29U;
            }
        } else {
            out.status = 13U;
        }
        break;
    case 7U:
        out.random_calls = 1U;
        remainder = rem10(random1);
        out.second_remainder = remainder;
        out.status = remainder <= 1 ? 30U : 29U;
        break;
    case 8U:
        out.status = 30U;
        break;
    case 9U:
        out.status = 29U;
        break;
    default:
        break;
    }
    return out;
}
