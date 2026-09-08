/* Byte-window predicate and entry guard recovered from i960 0x7dcc0. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_byte_window_7dcc0 {
    u32 entry_allowed;
    u32 byte_match;
    u32 status_masks[2];
};

/*
 * The routine first uses a signed compare against 0x1f3.  Inside each
 * object-slot iteration, a nonzero status byte is compared with the object
 * byte using the same inclusive five-count band seen at 0x7d1f0.  The
 * masked-halfword test is passed in already masked: the assembly continues
 * only when (field & 0x0f00) == 0.
 */
struct recovered_state_byte_window_7dcc0
recovered_state_byte_window_7dcc0(
    int32_t state_counter_509b34, uint8_t status_byte,
    uint8_t object_byte, uint16_t masked_halfword)
{
    struct recovered_state_byte_window_7dcc0 out = {0U, 0U, {0U, 0U}};
    const u32 status = (u32)status_byte;
    const u32 object = (u32)object_byte;

    if (state_counter_509b34 <= 0x1f3)
        return out;
    out.entry_allowed = 1U;
    out.byte_match = status != 0U && masked_halfword == 0U &&
                     object >= status && object <= status + 5U;
    return out;
}

/* The concrete loop at 0x7dd00 visits 32 slots for two adjacent statuses. */
void recovered_state_byte_window_masks_7dcc0(
    const uint8_t status_bytes[2], const uint8_t object_bytes[32],
    const uint16_t masked_halfwords[32], u32 status_masks[2])
{
    u32 status_index;
    u32 slot;

    status_masks[0] = 0U;
    status_masks[1] = 0U;
    for (status_index = 0U; status_index < 2U; ++status_index) {
        const u32 status = (u32)status_bytes[status_index];
        if (status == 0U)
            continue;
        for (slot = 0U; slot < 32U; ++slot) {
            const u32 object = (u32)object_bytes[slot];
            if (masked_halfwords[slot] == 0U && object >= status &&
                object <= status + 5U)
                status_masks[status_index] |= 1U << slot;
        }
    }
}
