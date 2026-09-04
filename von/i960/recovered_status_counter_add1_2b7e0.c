/* Pure status-counter transition from i960 0x2b7e0-0x2b808. */
#include <stdint.h>

uint32_t recovered_status_counter_add1_2b7e0(uint32_t counter)
{
    return counter + 1U;
}
