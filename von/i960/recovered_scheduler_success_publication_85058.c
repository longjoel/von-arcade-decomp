/* Second success publication recovered from i960 0x85058-0x85074. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_success_publication_85058 {
    u32 value_504e42;
    u32 value_504e44;
    u32 restores_g8;
};

struct recovered_scheduler_success_publication_85058
recovered_scheduler_success_publication_85058(u32 incoming_g13,
                                              u32 matched_row_8c)
{
    struct recovered_scheduler_success_publication_85058 out = {
        incoming_g13 | (1U << 9), matched_row_8c, 1U
    };
    return out;
}
