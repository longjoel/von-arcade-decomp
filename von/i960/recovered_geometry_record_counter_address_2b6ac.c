/* Pure indexed address calculation from i960 0x2b6ac-0x2b6c0. */
#include <stdint.h>

uint32_t recovered_geometry_record_counter_address_2b6ac(uint32_t index)
{
    return 0x51c5b4U + index * 100U;
}
