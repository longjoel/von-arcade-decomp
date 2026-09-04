/* Pure template copy recovered from i960 0x2b5b0-0x2b5dc. */
#include <stdint.h>

/* source_words are the five ldq blocks followed by the 0x2aad0 word. */
uint32_t recovered_geometry_template_copy_2b5b0(uint32_t index,
                                                 const uint32_t source_words[21],
                                                 uint32_t destination_words[21])
{
    uint32_t i;
    for (i = 0; i < 21; ++i)
        destination_words[i] = source_words[i];
    return 0x51c5b0U + index * 100U;
}
