/* Status/timing tail recovered from i960 0x88b44-0x88bc8. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_startup_mode4_arm_88af0_status_gate {
    u32 timing_input;
    u32 timing_after_upload;
    u32 timing_bias;
    u32 marker_1d0;
    u32 scan_count;
    u32 scan_limit;
    u32 match_found;
    u32 published_value;
    u32 publication_address;
    u32 no_match_value;
    u32 timing_wrap_count;
    u32 return_target;
};

static u32 recovered_scan_timing_88af0(u32 timing)
{
    int32_t signed_timing = (int32_t)timing;

    if (signed_timing <= 0)
        return timing + 0x78U;
    return timing;
}

struct recovered_startup_mode4_arm_88af0_status_gate
recovered_startup_mode4_arm_88af0_status_gate(u32 timing_input, u32 marker_1d0)
{
    struct recovered_startup_mode4_arm_88af0_status_gate out = {0};
    u32 timing = timing_input > 0U ? timing_input + 0x78U : timing_input;
    u32 index;

    out.timing_input = timing_input;
    out.timing_bias = 0x78U;
    out.timing_after_upload = timing;
    out.marker_1d0 = marker_1d0;
    out.scan_limit = 29U;
    out.publication_address = 0x0051c9b8U;
    out.no_match_value = 0xffffffffU;
    out.return_target = 0x00088bc8U;

    for (index = 0U; index < out.scan_limit; ++index) {
        timing = recovered_scan_timing_88af0(timing - 4U);
        out.scan_count = index + 1U;
        if (marker_1d0 != 0U) {
            out.match_found = 1U;
            out.published_value = recovered_scan_timing_88af0(timing - 6U);
            return out;
        }
    }
    out.published_value = out.no_match_value;
    return out;
}
