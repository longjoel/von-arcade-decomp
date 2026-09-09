/* Packet-row copy cursor entry recovered from i960 0x84a74-0x84a80. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_packet_row_copy_entry_84a74 {
    u32 next_index;
    u32 wrapped;
    u32 source_byte_offset;
    u32 enters_copy_84a80;
};

struct recovered_scheduler_packet_row_copy_entry_84a74
recovered_scheduler_packet_row_copy_entry_84a74(u32 current_index)
{
    struct recovered_scheduler_packet_row_copy_entry_84a74 out = {
        current_index + 1U, 0U, 0U, 1U
    };

    if (out.next_index > 59U) {
        out.next_index = 0U;
        out.wrapped = 1U;
    }
    out.source_byte_offset = out.next_index << 4;
    return out;
}
