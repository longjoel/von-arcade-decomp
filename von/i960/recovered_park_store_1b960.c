/* Park-and-publish leaf recovered from i960 0x1b960-0x1b97c.
 *
 * The leaf fixes g0 to 0, so the 0x29c08 clamp stores min(0, 0x100) = 0
 * at 0x51a260 and zeroes the uploader counter/mode slots (parking the
 * 0x29d50 uploader), then publishes 25 to 0x503a00 and saves the caller
 * link at 0x5024c6.
 */
#include <stdint.h>

typedef uint32_t u32;
typedef int32_t s32;

struct recovered_park_store_plan {
    u32 value_addr;
    s32 value_stored;
    u32 counter_addr;
    u32 mode_addr;
    u32 publish_addr;
    u32 publish_value;
    u32 link_addr;
    u32 link_stored;
};

void recovered_park_store_plan(u32 link,
                                struct recovered_park_store_plan *plan)
{
    plan->value_addr = 0x0051a260U;
    /* mov 0,g0 into the clamp: min(0, 0x100) is 0. */
    plan->value_stored = 0;
    plan->counter_addr = 0x0051a264U;
    plan->mode_addr = 0x0051a268U;
    /* mov 25,g1 then st g1,0x503a00. */
    plan->publish_addr = 0x00503a00U;
    plan->publish_value = 25U;
    /* stos g14,0x5024c6. */
    plan->link_addr = 0x005024c6U;
    plan->link_stored = link;
}
