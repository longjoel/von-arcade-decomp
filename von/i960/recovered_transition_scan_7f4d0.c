/* Repeated two-byte scan recovered from i960 0x7f4d0-0x7f5e8. */

#include <stddef.h>
#include <stdint.h>

typedef uint32_t u32;

struct recovered_transition_scan_7f4d0 {
    u32 entry_allowed;
    u32 status0_match_mask;
    u32 status1_match_mask;
};

static u32 window_match(uint8_t status, uint8_t object)
{
    const u32 s = status;
    const u32 o = object;
    return s != 0U && o >= s && o <= s + 5U;
}

/* object_bytes contains 32 bytes at object+0x200, one per 0x20-byte slot. */
struct recovered_transition_scan_7f4d0
recovered_transition_scan_7f4d0(
    int32_t state_counter_509b28, uint8_t status0, uint8_t status1,
    const uint8_t object_bytes[32])
{
    struct recovered_transition_scan_7f4d0 out = {0U, 0U, 0U};
    size_t i;

    if (state_counter_509b28 <= 0x1f3)
        return out;
    out.entry_allowed = 1U;
    for (i = 0; i < 32; ++i) {
        if (window_match(status0, object_bytes[i]))
            out.status0_match_mask |= 1U << i;
        if (window_match(status1, object_bytes[i]))
            out.status1_match_mask |= 1U << i;
    }
    return out;
}
