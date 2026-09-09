/* Selected frame-row input recovered from i960 0x84a04-0x84a34. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_frame_row_input_84a04 {
    u32 frame_byte_offset;
    u32 destination_offset;
    int32_t source_0;
    int32_t source_2;
    int32_t source_4;
    int32_t source_6;
    int32_t source_a;
    int32_t field_8c;
};

struct recovered_scheduler_frame_row_input_84a04
recovered_scheduler_frame_row_input_84a04(
    u32 selected_frame_offset, u32 table_base, u32 selected_index,
    int32_t frame_0, int32_t frame_2, int32_t frame_4, int32_t frame_6,
    int32_t frame_a,
    int32_t normalized_delay)
{
    struct recovered_scheduler_frame_row_input_84a04 out = {
        selected_frame_offset,
        table_base + selected_index * 144U,
        frame_0, frame_2, frame_4, frame_6, frame_a,
        240 - 4 * normalized_delay
    };
    return out;
}
