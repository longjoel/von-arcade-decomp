/* Pure dispatch decision from i960 0x2ba44-0x2ba84. */
#include <stdint.h>

uint32_t recovered_progress_dispatch_2ba44(uint32_t progress,
                                           uint32_t service_mode,
                                           uint32_t callback)
{
    (void)progress; /* caller performs progress & 31 table indexing */
    return (callback == 0U || (service_mode == 2U && callback == 0x000e3ab0U)) ? 1U : 0U;
}
