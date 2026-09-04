/* Pure progress mapping from i960 0x2b870-0x2b930. */
#include <stdint.h>

struct recovered_progress_mapping {
    uint32_t display_value;
    uint32_t counter_increment;
    uint32_t next_progress;
};

void recovered_progress_mapping_2b870(uint32_t progress,
                                      struct recovered_progress_mapping *out)
{
    if (progress <= 15U)
        out->display_value = 0x200U - (progress << 5);
    else if (progress <= 32U && (progress & 1U))
        out->display_value = 2U * (progress - 32U);
    else
        out->display_value = 0U;
    out->counter_increment = (progress == 128U) ? 1U : 0U;
    out->next_progress = progress + 1U;
}
