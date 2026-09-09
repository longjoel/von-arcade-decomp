/* Scheduler frame publication recovered from i960 0x8467c-0x84724. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_frame_publication_8467c {
    u32 row_offset;
    u32 selector_result;
    u32 packed_field_08;
    u32 field_08_flags;
    u32 field_0a;
    u32 called_847c0;
};

struct recovered_scheduler_frame_publication_8467c
recovered_scheduler_frame_publication_8467c(
    u32 counter_509a68, u32 value_509ac0, u32 value_509b10,
    u32 frame_field_40, u32 frame_field_44, u32 selector_result)
{
    u32 flags = 0U;
    struct recovered_scheduler_frame_publication_8467c out;

    if (value_509ac0 == 1U)
        flags |= 1U << 15;
    if (value_509b10 == 1U)
        flags |= 1U << 14;
    out.row_offset = counter_509a68 << 4;
    out.selector_result = selector_result;
    out.packed_field_08 = (((frame_field_44 & 0xffffU) << 8)
                           | (frame_field_40 & 0xffffU) | flags) & 0xffffU;
    out.field_08_flags = flags;
    out.field_0a = selector_result & 0xffffU;
    out.called_847c0 = 1U;
    return out;
}
