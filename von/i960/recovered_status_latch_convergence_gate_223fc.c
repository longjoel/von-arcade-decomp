/* Convergence gate recovered from i960 0x223fc-0x22418. */

#include <stdint.h>

typedef uint32_t u32;

enum recovered_status_latch_convergence_route {
    RECOVERED_STATUS_LATCH_CONVERGENCE_SKIP = 0,
    RECOVERED_STATUS_LATCH_CONVERGENCE_ATTRIBUTED = 1,
    RECOVERED_STATUS_LATCH_CONVERGENCE_PLAIN = 2
};

struct recovered_status_latch_convergence_gate_plan {
    u32 route;
    u32 selector_gate;
    u32 latch;
    u32 latch_minus_87;
    u32 bit3_set;
    u32 continuation_target;
};

void recovered_status_latch_convergence_gate_plan(
    u32 selector_gate, int32_t latch, u32 bit3_set,
    struct recovered_status_latch_convergence_gate_plan *plan)
{
    plan->route = RECOVERED_STATUS_LATCH_CONVERGENCE_SKIP;
    plan->selector_gate = selector_gate;
    plan->latch = (u32)latch;
    plan->latch_minus_87 = latch >= 0 ? (u32)(latch - 87) : 0xffffffffU;
    plan->bit3_set = bit3_set != 0U ? 1U : 0U;
    plan->continuation_target = 0x00022590U;

    /* cmpibe selector,0 and cmpobg latch-87,68 both skip this gate. */
    if (selector_gate != 0U && latch >= 0 && latch <= 155) {
        plan->route = bit3_set != 0U
            ? RECOVERED_STATUS_LATCH_CONVERGENCE_ATTRIBUTED
            : RECOVERED_STATUS_LATCH_CONVERGENCE_PLAIN;
        plan->continuation_target = bit3_set != 0U
            ? 0x0002241cU : 0x000224e4U;
    }
}
