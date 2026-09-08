/* Descriptor lookup boundary recovered from i960 0x7e390. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_geometry_descriptor_7e390 {
    u32 object_byte_offset;       /* 0x200 + 32 * slot. */
    u32 descriptor_index;
    u32 descriptor_offset;        /* 48 * descriptor_index. */
    u32 descriptor_base;
    u32 state3_special;
    u32 descriptor_field4;
    u32 descriptor_field12;
    u32 descriptor_field36;
    u32 scale_constant_40c00000;
    u32 scale_constant_42f00000;
    u32 special_scale_3ff80000;
};

/*
 * g1 is the caller's slot selector and the byte at object+0x200+(g1<<5)
 * indexes 48-byte records at 0x562cb0.  The listing uses ldis for +0xc and
 * ordinary loads for +0x4/+0x24; the values are therefore returned raw so
 * the later fixed-point/float interpretation is not guessed here.
 */
struct recovered_state_geometry_descriptor_7e390
recovered_state_geometry_descriptor_7e390(
    u32 slot, uint8_t object_index_byte, u32 object_state,
    u32 field4, int16_t field12, u32 field36)
{
    struct recovered_state_geometry_descriptor_7e390 out = {
        0x200U + (slot << 5), object_index_byte,
        (u32)object_index_byte * 48U, 0x562cb0U,
        object_state == 3U, field4, (u32)(int32_t)field12, field36,
        0x40c00000U, 0x42f00000U, 0x3ff80000U
    };
    return out;
}
