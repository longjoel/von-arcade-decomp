/* Success publication recovered from i960 0x84dac-0x84dc4. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_success_publication_84dac {
    u32 value_504e42;
    u32 value_504e44;
    u32 continues_to_84f10;
};

struct recovered_scheduler_success_publication_84dac
recovered_scheduler_success_publication_84dac(u32 incoming_g13,
                                              u32 caller_g14)
{
    struct recovered_scheduler_success_publication_84dac out = {
        incoming_g13 | (1U << 8), caller_g14, 1U
    };
    return out;
}
