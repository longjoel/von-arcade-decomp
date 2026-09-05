/* Threshold dispatch tail recovered from i960 0x1ba70-0x1babc.
 *
 * The tail compares the service counter at 0x503a04 against 480
 * (shlo 5,15): only an equal counter issues the caller-owned 0x2a4e0
 * sub-call with 0x1317. Then the familiar dispatch runs on flag
 * 0x5024a4 bit 4: a set bit stores 22 to 0x503a00 with no counter
 * store, otherwise the counter decrements in place (cmpdeci) and the
 * 22-store happens only when the entry counter was exactly 1.
 * Sub-call bodies stay caller-owned.
 */
#include <stdint.h>

typedef uint32_t u32;
typedef int32_t s32;
typedef uint8_t u8;

struct recovered_threshold_dispatch_plan {
    u32 counter_addr;
    s32 call_made;
    u32 call_arg;
    s32 do_store;
    u32 stored_counter;
    s32 store_final;
    u32 final_addr;
    u32 final_value;
};

void recovered_threshold_dispatch_plan(u32 counter, u8 flag,
                                        struct recovered_threshold_dispatch_plan *plan)
{
    plan->counter_addr = 0x00503a04U;
    /* cmpibne g4,g1,0x1ba8c: the call issues only on equality. */
    plan->call_made = counter == 480U ? 1 : 0;
    plan->call_arg = 0x1317U;
    if ((flag >> 4) & 1U) {
        plan->do_store = 0;
        plan->stored_counter = counter;
        plan->store_final = 1;
    } else {
        plan->do_store = 1;
        plan->stored_counter = counter - 1U;
        plan->store_final = counter == 1U ? 1 : 0;
    }
    plan->final_addr = 0x00503a00U;
    plan->final_value = 22U;
}
