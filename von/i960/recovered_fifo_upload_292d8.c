/* Geometry-port word pump recovered from i960 0x292d8-0x2932c. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_fifo_upload_plan {
    u32 select_address;
    u32 select_value;
    u32 port_address;
    u32 header_words[2];
    u32 pair_count;
    u32 words_per_pair;
    u32 words_total;
    u32 saves_return_link;
    u32 clears_g14;
};

void recovered_fifo_upload_plan(u32 header_first, u32 pair_count,
                                struct recovered_fifo_upload_plan *plan)
{
    plan->select_address = 0x00800060U;
    plan->select_value = 0x606U;
    plan->port_address = 0x00804000U;
    plan->header_words[0] = header_first;
    plan->header_words[1] = pair_count;
    plan->pair_count = pair_count;
    /* One decrement per iteration with two word stores: the cmpi/bne pair
     * counts pairs while the FIFO port address never advances. */
    plan->words_per_pair = 2U;
    plan->words_total = pair_count * 2U;
    /* The entry saves the return link into g3 and clears g14 for the
     * body, returning through bx (g3) instead of the shared tail. */
    plan->saves_return_link = 1U;
    plan->clears_g14 = 1U;
}
