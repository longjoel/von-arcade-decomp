/* Recovery-row source seed recovered from i960 0x84bec-0x84c1c. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_recovery_row_seed_84bec {
    u32 source_index;
    u32 wrapped;
    u32 source_byte_offset;
    u32 scan_limit;
    u32 mask;
    u32 loaded_low_nibble;
};

struct recovered_scheduler_recovery_row_seed_84bec
recovered_scheduler_recovery_row_seed_84bec(u32 counter_509a68,
                                            u32 frame_field_08)
{
    struct recovered_scheduler_recovery_row_seed_84bec out;

    if (counter_509a68 == 0U) {
        out.source_index = 59U;
        out.wrapped = 1U;
    } else {
        out.source_index = counter_509a68 - 1U;
        out.wrapped = 0U;
    }
    out.source_byte_offset = out.source_index << 4;
    out.scan_limit = 59U;
    out.mask = 0xffffU;
    out.loaded_low_nibble = frame_field_08 & 0x0fU;
    return out;
}
