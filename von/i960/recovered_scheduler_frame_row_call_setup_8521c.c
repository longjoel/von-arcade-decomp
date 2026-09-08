/* Shared row-handler call setup recovered from i960 0x8521c-0x8522c. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_frame_row_call_setup_8521c {
    u32 object_field_74;
    u32 frame_pointer;
    u32 argument_g0;
    u32 argument_g1;
    u32 argument_g2;
    u32 call_target;
};

struct recovered_scheduler_frame_row_call_setup_8521c
recovered_scheduler_frame_row_call_setup_8521c(u32 object_field_74,
                                               u32 frame_pointer)
{
    struct recovered_scheduler_frame_row_call_setup_8521c out = {
        object_field_74, frame_pointer, object_field_74,
        frame_pointer + 0x40U, frame_pointer + 0x44U, 0x000847c0U
    };
    return out;
}
