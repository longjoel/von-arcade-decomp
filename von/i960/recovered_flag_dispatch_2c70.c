/* Input flag dispatchers recovered from i960 0x2c70-0x2d78. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_flag_dispatch_route {
    u32 entry;
    u32 zero_target;
    u32 zero_is_bal;
    u32 nonzero_target;
    u32 nonzero_is_bal;
};

/* All four entries test the same 0x5023e0 flag and forward with no
 * argument shuffling; only the targets and the bal/call link kind
 * differ per arm. */
static const struct recovered_flag_dispatch_route
recovered_flag_dispatch_routes[4] = {
    { 0x00002c70U, 0x000027b8U, 1U, 0x00002bb0U, 0U },
    { 0x00002c90U, 0x00002798U, 1U, 0x00002c10U, 0U },
    { 0x00002cb0U, 0x00002cd8U, 1U, 0x00002cf8U, 1U },
    { 0x00002d60U, 0x00002d88U, 1U, 0x00002da0U, 0U }
};

u32 recovered_flag_dispatch_route_count(void)
{
    return 4U;
}

u32 recovered_flag_dispatch_target(u32 entry, u32 flag,
                                   u32 *is_bal)
{
    u32 index;

    for (index = 0U; index < 4U; ++index) {
        if (recovered_flag_dispatch_routes[index].entry == entry) {
            if (flag == 0U) {
                *is_bal = recovered_flag_dispatch_routes[index].zero_is_bal;
                return recovered_flag_dispatch_routes[index].zero_target;
            }
            *is_bal =
                recovered_flag_dispatch_routes[index].nonzero_is_bal;
            return recovered_flag_dispatch_routes[index].nonzero_target;
        }
    }
    *is_bal = 0U;
    return 0U;
}
