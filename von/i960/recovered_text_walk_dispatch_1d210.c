/* Fixed-callee text walkers recovered from i960 0x1d210-0x1d26c. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_text_walk_route {
    u32 entry;
    u32 callee;
};

/* The four entries share one loop shape with the 0x1d1b0 walker: test
 * the byte first, emit each nonzero byte through the fixed callee with
 * the byte in g0, and stop at the first NUL. Only the callee differs. */
static const struct recovered_text_walk_route recovered_text_walk_routes[4] = {
    { 0x0001d1d0U, 0x0001cea0U },
    { 0x0001d210U, 0x0001d090U },
    { 0x0001d230U, 0x0001cf40U },
    { 0x0001d250U, 0x0001cfe0U }
};

u32 recovered_text_walk_route_count(void)
{
    return 4U;
}

u32 recovered_text_walk_callee(u32 entry)
{
    u32 index;

    for (index = 0U; index < 4U; ++index) {
        if (recovered_text_walk_routes[index].entry == entry)
            return recovered_text_walk_routes[index].callee;
    }
    return 0U;
}
