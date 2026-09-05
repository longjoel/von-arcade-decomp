/* Ring-queue pump recovered from i960 0x18538-0x185b4. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_queue_pump_plan {
    u32 queue_base;
    u32 head_addr;
    u32 tail_addr;
    u32 port0;
    u32 port1;
    u32 drain_addr;
    u32 drain_src;
    u32 queue_mask;
    u32 pops;
    u32 emit0;
    u32 emit1;
    u32 new_head;
    u32 drains;
    u32 new_drain;
    u32 emit_drain;
};

void recovered_queue_pump_plan(u32 head, u32 tail, u32 head_byte,
                               u32 drain, u32 drain_src,
                               struct recovered_queue_pump_plan *plan)
{
    plan->queue_base = 0x00504c60U;
    plan->head_addr = 0x00504c70U;
    plan->tail_addr = 0x00504c74U;
    plan->port0 = 0x01c00008U;
    plan->port1 = 0x00503312U;
    plan->drain_addr = 0x00504c78U;
    plan->drain_src = 0x00502512U;
    plan->queue_mask = 15U;
    /* Nonempty queues pop one byte to both ports and advance the head
     * modulo 16. */
    plan->pops = head != tail ? 1U : 0U;
    plan->emit0 = head_byte & 0xffU;
    plan->emit1 = head_byte & 0xffU;
    plan->new_head = (head + 1U) & plan->queue_mask;
    /* An empty queue instead refreshes the drain word when it differs
     * and emits its low byte to port 0. */
    plan->drains = !plan->pops && drain != drain_src ? 1U : 0U;
    plan->new_drain = drain_src;
    plan->emit_drain = drain_src & 0xffU;
}
