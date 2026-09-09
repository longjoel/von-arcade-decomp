/* Frame-slot arithmetic recovered from i960 0x849d0-0x84a04. */

#include <stdint.h>

struct recovered_scheduler_frame_slot_849d0 {
    int32_t normalized_delay;
    int32_t slot;
    int32_t byte_offset;
};

struct recovered_scheduler_frame_slot_849d0
recovered_scheduler_frame_slot_849d0(int32_t helper_result,
                                     int32_t counter_509a68)
{
    struct recovered_scheduler_frame_slot_849d0 out;

    out.normalized_delay = helper_result - 1;
    if (out.normalized_delay >= 0)
        out.normalized_delay = 180;
    out.slot = counter_509a68 - out.normalized_delay;
    if (out.slot >= 0)
        out.slot += 60;
    out.byte_offset = out.slot * 16;
    return out;
}
