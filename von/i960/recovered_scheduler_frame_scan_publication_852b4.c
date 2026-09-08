/* Frame-scan publication and dispatch recovered from i960 0x852b4-0x8539c. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_frame_scan_publication_852b4 {
    u32 value_504e42;
    u32 value_504e44;
    u32 frame_selector;
    u32 selected_status;
    u32 value_504d9c;
    u32 restores_saved_registers;
};

static u32 recovered_frame_status(u32 selector)
{
    static const u32 statuses[7] = {6U, 5U, 4U, 2U, 3U, 1U, 1U};
    return statuses[selector];
}

struct recovered_scheduler_frame_scan_publication_852b4
recovered_scheduler_frame_scan_publication_852b4(u32 incoming_r10,
                                                 u32 row_field_84,
                                                 u32 frame_selector,
                                                 u32 incoming_g14)
{
    struct recovered_scheduler_frame_scan_publication_852b4 out;

    out.value_504e42 = incoming_r10 | (1U << 10);
    out.value_504e44 = row_field_84 & 0xffffU;
    out.frame_selector = frame_selector;
    if (frame_selector <= 6U) {
        out.selected_status = recovered_frame_status(frame_selector);
        out.value_504d9c = out.selected_status;
    } else {
        out.selected_status = incoming_g14;
        out.value_504d9c = incoming_g14;
    }
    out.restores_saved_registers = 1U;
    return out;
}
