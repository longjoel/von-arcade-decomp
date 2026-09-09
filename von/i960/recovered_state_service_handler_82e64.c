/* Service handler recovered from i960 0x82e64-0x82e9c. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_service_handler_82e64 {
    u32 admitted;
    u32 downstream_value;
    int32_t remainder_7;
};

struct recovered_state_service_handler_82e64
recovered_state_service_handler_82e64(int32_t random_value, u32 object_state)
{
    int32_t remainder = random_value % 7;
    struct recovered_state_service_handler_82e64 out = {
        0U, 0U, remainder
    };

    if ((remainder == 4 || remainder == 6) &&
        (object_state == 0U || object_state == 1U ||
         object_state == 5U || object_state == 6U)) {
        out.admitted = 1U;
        out.downstream_value = 2U;
    }
    return out;
}
