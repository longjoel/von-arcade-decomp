/* Frame-scan retry loop recovered from i960 0x853a0-0x853c0. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_frame_scan_loop_853a0 {
    u32 incoming_index;
    u32 next_index;
    u32 next_table_offset;
    u32 next_row_offset;
    u32 continues_scan;
    u32 restores_saved_registers;
};

struct recovered_scheduler_frame_scan_loop_853a0
recovered_scheduler_frame_scan_loop_853a0(u32 incoming_index,
                                          u32 table_offset,
                                          u32 row_offset)
{
    struct recovered_scheduler_frame_scan_loop_853a0 out;

    out.incoming_index = incoming_index;
    out.next_index = incoming_index + 1U;
    out.next_table_offset = table_offset + 0x88U;
    out.next_row_offset = row_offset + 0x88U;
    /* cmpi 7,r10 / bge is literal-first: indices 0..7 are scanned. */
    out.continues_scan = out.next_index <= 7U ? 1U : 0U;
    out.restores_saved_registers = out.continues_scan == 0U ? 1U : 0U;
    return out;
}
