/* Status-scan continuation recovered from i960 0x88a64-0x88ae8. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_startup_mode4_arm_88a10_status_scan {
    u32 timing_input;
    u32 timing_after_upload;
    u32 timing_bias;
    u32 scan_count;
    u32 scan_limit;
    u32 zero_status_found;
    u32 matched_timing;
    u32 publish_address;
    u32 publish_value;
    u32 fallback_address;
    u32 fallback_value;
    u32 return_target;
};

static u32 recovered_scan_timing_88a10(u32 timing)
{
    int32_t signed_timing = (int32_t)timing;

    if (signed_timing <= 0)
        return timing + 0x78U;
    return timing;
}

struct recovered_startup_mode4_arm_88a10_status_scan
recovered_startup_mode4_arm_88a10_status_scan(
    u32 timing_input, const uint8_t status_bytes[29], u32 g14_value)
{
    struct recovered_startup_mode4_arm_88a10_status_scan out = {0};
    u32 timing = timing_input > 0U ? timing_input + 0x78U : timing_input;
    u32 index;

    out.timing_input = timing_input;
    out.timing_bias = 0x78U;
    out.timing_after_upload = timing;
    out.scan_limit = 29U;
    out.publish_address = 0x0051c998U;
    out.fallback_address = 0x0051c9a0U;
    out.fallback_value = g14_value;
    out.return_target = 0x00088ae8U;

    /* 0x88a6c subtracts four before the first status probe. */
    timing = recovered_scan_timing_88a10(timing - 4U);
    for (index = 0U; index < out.scan_limit; ++index) {
        out.scan_count = index + 1U;
        if (status_bytes[index] == 0U) {
            out.zero_status_found = 1U;
            out.matched_timing = timing;
            out.publish_value = timing;
            out.fallback_value = 0U;
            return out;
        }
        timing = recovered_scan_timing_88a10(timing - 4U);
    }
    return out;
}
