/* Secondary stage FIFO tail recovered from i960 0x87b10-0x87b2c. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_stage_secondary_fifo_tail_87b10 {
    u32 service_target;
    u32 fifo_address;
    u32 word_count;
    u32 words[2];
    u32 continuation;
};

struct recovered_stage_secondary_fifo_tail_87b10
recovered_stage_secondary_fifo_tail_87b10(void)
{
    struct recovered_stage_secondary_fifo_tail_87b10 out;

    out.service_target = 0x000294b0U;
    out.fifo_address = 0x00884000U;
    out.word_count = 2U;
    out.words[0] = 8U;
    out.words[1] = 16U;
    out.continuation = 0x00087b2cU;
    return out;
}
