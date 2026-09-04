/* Pure linked-list initialization from i960 0x29738/0x29778. */
#include <stdint.h>

/* Build the 64-entry next-pointer schedule; the terminal link is NULL. */
void recovered_pointer_table_init_29738(uint32_t head, uint32_t stride,
                                        uint32_t links[64])
{
    uint32_t i;
    for (i = 0; i < 63; ++i)
        links[i] = head + (i + 1U) * stride;
    links[63] = 0;
}
