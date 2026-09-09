/* Byte-map candidate scan recovered from i960 0x85c88-0x85d00. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_callback_byte_map_scan_85c88 {
    u32 candidate_index;
    u32 candidate_nibble;
    u32 used_primary_gate;
    u32 used_fallback_gate;
    u32 row_adjust_path;
    u32 rejected;
    uint8_t map_after[32];
};

static u32 candidate_is_eligible(uint8_t value, u32 previous_halfword,
                                 u32 current_halfword, uint8_t object_200)
{
    u32 bit7 = (value & 0x80U) != 0U;

    if (!bit7)
        return 0U;
    if ((previous_halfword & (1U << 10)) != 0U)
        return 1U;
    if ((previous_halfword & ((1U << 9) | (1U << 8) | (1U << 11))) != 0U)
        return 1U;
    if (current_halfword == 0U)
        return 1U;
    return object_200 == 0U;
}

struct recovered_scheduler_callback_byte_map_scan_85c88
recovered_scheduler_callback_byte_map_scan_85c88(
    const uint8_t map_before[32], uint32_t previous_halfword,
    uint32_t current_halfword, uint8_t object_200, uint8_t callback_g14)
{
    struct recovered_scheduler_callback_byte_map_scan_85c88 out;
    u32 index;

    out.candidate_index = 32U;
    out.candidate_nibble = 0U;
    out.used_primary_gate = 0U;
    out.used_fallback_gate = 0U;
    out.row_adjust_path = 0U;
    out.rejected = 1U;
    for (index = 0U; index < 32U; ++index)
        out.map_after[index] = map_before[index];

    for (index = 0U; index < 32U; ++index) {
        u32 primary = (map_before[index] & 0x80U) != 0U &&
                      (previous_halfword & (1U << 10)) != 0U;
        u32 fallback = !primary && candidate_is_eligible(
            map_before[index], previous_halfword, current_halfword, object_200);
        u32 nibble;
        u32 duplicate = 0U;
        u32 scan;

        if (!primary && !fallback)
            continue;
        nibble = map_before[index] & 0x0fU;
        out.map_after[index] = callback_g14;
        for (scan = 0U; scan < 32U; ++scan) {
            if ((out.map_after[scan] & 0x0fU) == nibble) {
                duplicate = 1U;
                if (primary)
                    out.map_after[scan] |= 1U << 5;
                break;
            }
        }
        /* The primary path uses a duplicate to set bit 5 and continue to
         * the row adjustment; the fallback path rejects that collision. */
        if (duplicate && !primary)
            return out;

        out.candidate_index = index;
        out.candidate_nibble = nibble;
        out.used_primary_gate = primary;
        out.used_fallback_gate = fallback;
        out.row_adjust_path = primary ? duplicate : 1U;
        out.rejected = 0U;
        return out;
    }
    return out;
}
