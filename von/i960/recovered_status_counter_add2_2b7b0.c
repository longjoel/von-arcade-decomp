/* Pure status-counter transition from i960 0x2b7b0-0x2b7d8. */
#include <stdint.h>

uint32_t recovered_status_counter_add2_2b7b0(uint32_t counter)
{
    return counter + 2U;
}
