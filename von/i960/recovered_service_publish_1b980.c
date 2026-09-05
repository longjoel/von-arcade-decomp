/* Service-table publish leaf recovered from i960 0x1b980-0x1b9c4.
 *
 * The leaf fixes g0 to 0, so the 0x29c08 clamp stores 0 at 0x51a260
 * and zeroes the uploader counter/mode slots (parking the 0x29d50
 * uploader), then publishes three service-table constants around two
 * caller-owned sub-calls that stay outside this pure store schedule:
 * 0x14a to 0x503a04, 16 to 0x503a00, and -1 (subo 1,0 wrap) to
 * 0x577170. Link/return mechanics are caller-owned.
 */
#include <stdint.h>

typedef uint32_t u32;
typedef int32_t s32;

struct recovered_service_publish_plan {
    u32 value_addr;
    s32 value_stored;
    u32 counter_addr;
    u32 mode_addr;
    u32 table0_addr;
    u32 table0_value;
    u32 table1_addr;
    u32 table1_value;
    u32 table2_addr;
    u32 table2_value;
};

void recovered_service_publish_plan(struct recovered_service_publish_plan *plan)
{
    plan->value_addr = 0x0051a260U;
    /* mov 0,g0 into the clamp: min(max(0, -256), 0x100) is 0. */
    plan->value_stored = 0;
    plan->counter_addr = 0x0051a264U;
    plan->mode_addr = 0x0051a268U;
    /* lda 0x14a,g1 then st g1,0x503a04. */
    plan->table0_addr = 0x00503a04U;
    plan->table0_value = 0x14aU;
    /* mov 16,g1 then st g1,0x503a00. */
    plan->table1_addr = 0x00503a00U;
    plan->table1_value = 16U;
    /* subo 1,0,g1 wraps to -1, then st g1,0x577170. */
    plan->table2_addr = 0x00577170U;
    plan->table2_value = 0xFFFFFFFFU;
}
