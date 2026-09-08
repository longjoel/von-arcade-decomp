/* Secondary callback byte-map finalizer recovered from i960 0x86174-0x861d4. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_callback_secondary_byte_map_finalize_86174 {
    u32 writes;
    uint8_t map_after[32];
};

struct recovered_scheduler_callback_secondary_byte_map_finalize_86174
recovered_scheduler_callback_secondary_byte_map_finalize_86174(
    const uint8_t object_200_bytes[32], const uint16_t object_204_words[32],
    const uint8_t map_before[32], u32 value_504e42)
{
    struct recovered_scheduler_callback_secondary_byte_map_finalize_86174 out;
    u32 index;

    out.writes = 0U;
    for (index = 0U; index < 32U; ++index)
        out.map_after[index] = map_before[index];

    for (index = 0U; index < 32U; ++index) {
        if (object_200_bytes[index] == 0U || object_204_words[index] == 0U ||
            out.map_after[index] != 0U ||
            (value_504e42 & (1U << 11)) == 0U)
            continue;
        out.map_after[index] = (uint8_t)((value_504e42 & 0x0fU) | 0x80U);
        ++out.writes;
    }
    return out;
}
