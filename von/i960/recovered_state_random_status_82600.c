/* Random status selector recovered from i960 0x82600-0x82650. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_random_status_82600 {
    int32_t random_value;
    int32_t remainder_mod3;
    u32 writes_status;
    u32 status_504d80;
    u32 destination;
};

struct recovered_state_random_status_82600
recovered_state_random_status_82600(int32_t random_value)
{
    const int32_t remainder = random_value % 3;
    struct recovered_state_random_status_82600 out = {
        random_value, remainder, 0U, 0U, 0U
    };

    if (remainder == 0)
        out.status_504d80 = 20U;
    else if (remainder == 1)
        out.status_504d80 = 19U;
    else if (remainder == 2)
        out.status_504d80 = 33U;
    else
        return out;
    out.writes_status = 1U;
    out.destination = 0x00504d80U;
    return out;
}
