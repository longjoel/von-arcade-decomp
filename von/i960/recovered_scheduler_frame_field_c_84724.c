/* Scheduler frame field +0xc construction recovered from i960 0x84724-0x847b0. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_frame_field_c_84724 {
    u32 packed_frame_low16;
    u32 object_108_packed;
    u32 field_0c;
    u32 state31_path;
    u32 set_frame_bit3;
};

struct recovered_scheduler_frame_field_c_84724
recovered_scheduler_frame_field_c_84724(
    u32 frame_509a60, u32 frame_509a62, u32 frame_509a64,
    u32 frame_509a66, u32 object_field_108, u32 object_state_172,
    u32 state31_packed)
{
    u32 packed_frame = frame_509a60 | frame_509a62
                       | frame_509a64 | frame_509a66;
    u32 object_packed = ((object_field_108 & 0x0f00U) >> 4)
                        | (object_field_108 & 0x000fU);
    struct recovered_scheduler_frame_field_c_84724 out = {
        packed_frame & 0xffffU, object_packed,
        (((packed_frame & 0xffffU) << 8) & 0xff00U) | object_packed,
        0U, 0U
    };

    if (object_state_172 == 31U) {
        out.state31_path = 1U;
        out.set_frame_bit3 = 1U;
        out.packed_frame_low16 |= 1U << 3;
        out.field_0c = (((out.packed_frame_low16 << 8) & 0xff00U)
                        | (state31_packed & 0xffffU));
    }
    return out;
}
