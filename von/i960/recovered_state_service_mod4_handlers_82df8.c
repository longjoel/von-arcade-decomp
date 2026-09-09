/* Modulo-4 service selector arms recovered from i960 0x82df8-0x82e40. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_service_mod4_handlers_82df8 {
    u32 handled;
    int32_t selector;
    int32_t remainder_4;
};

static int32_t normalized_remainder_4(int32_t random_value)
{
    int32_t adjusted = random_value;
    int32_t block;

    if (adjusted < 0)
        adjusted += 3;
    block = adjusted & ~3;
    return random_value - block;
}

struct recovered_state_service_mod4_handlers_82df8
recovered_state_service_mod4_handlers_82df8(u32 entry, int32_t random_value,
                                            u32 object_state)
{
    struct recovered_state_service_mod4_handlers_82df8 out = {
        0U, 0, 0
    };

    if (entry != 0x82df8U && entry != 0x82e0cU)
        return out;
    out.handled = 1U;
    out.remainder_4 = normalized_remainder_4(random_value);
    out.selector = out.remainder_4;
    if (entry == 0x82e0cU)
        out.selector = object_state == 3U ? 7 : out.remainder_4 + 4;
    return out;
}
