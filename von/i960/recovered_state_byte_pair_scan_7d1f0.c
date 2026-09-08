/* Exact scan prefix and shared gate recovered from i960 0x7d1f0-0x7d358. */

#include <stddef.h>
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_byte_pair_scan_7d1f0 {
    u32 first_match;       /* g3: 0x9a byte is in [reference, reference + 5]. */
    u32 second_match;      /* g13: 0x98 byte is in the same band. */
    u32 third_scan_done;   /* The 0x94..0x96 loop has no observable result here. */
    u32 dispatch_allowed;  /* The common pre-dispatch gate at 0x7d2d8..0x7d344. */
    u32 selector;          /* object + 0x64, valid only when dispatch_allowed is 1. */
    u32 handler_target;    /* 0x7d358[object_state], valid on dispatch. */
};

static u32 state_handler_target(u32 state)
{
    static const u32 targets[10] = {
        0x0007d380U, 0x0007d390U, 0x0007d3a4U, 0x0007d404U,
        0x0007d4e8U, 0x0007d568U, 0x0007d5a4U, 0x0007d5dcU,
        0x0007d604U, 0x0007d660U,
    };

    return state < 10U ? targets[state] : 0U;
}

static u32 byte_in_band(u32 reference, uint8_t value)
{
    const u32 masked = (u32)value;
    return masked != 0U && reference >= masked && reference <= masked + 5U;
}

/*
 * first_byte, second_byte, and third_bytes correspond to offsets 0x9a,
 * 0x98, and 0x94 respectively in the 0x504da0 record.  The original loops
 * terminate at 0x9b, 0x99, and 0x97, so the first two contain one byte and
 * the third contains three bytes.
 *
 * The third loop performs only a nonzero/ lower-bound comparison and then
 * discards the result; it therefore cannot affect this routine's return or
 * the later dispatch gate.  It is represented by third_scan_done so callers
 * do not mistake that scan for a missing predicate.
 */
struct recovered_state_byte_pair_scan_7d1f0
recovered_state_byte_pair_scan_7d1f0(
    u32 reference, uint8_t first_byte, uint8_t second_byte,
    const uint8_t *third_bytes, size_t third_count,
    u32 r7_504d9c, u32 status_504d94, u32 status_504db4,
    u32 base_504da0, u32 control_504dc8, u32 mode_504e30,
    u32 object_state, u32 selector)
{
    struct recovered_state_byte_pair_scan_7d1f0 out = {
        0U, 0U, 0U, 0U, selector, 0U
    };
    size_t i;

    out.first_match = byte_in_band(reference, first_byte);
    out.second_match = byte_in_band(reference, second_byte);
    for (i = 0; i < third_count; ++i) {
        const u32 masked = (u32)third_bytes[i];
        (void)(masked != 0U && reference >= masked);
    }
    out.third_scan_done = 1U;

    /* cmpob/cmpib branches make every condition below a required gate. */
    if (r7_504d9c == 0U || status_504d94 - 12U <= 1U ||
        (int32_t)status_504db4 > 0 || base_504da0 == 100U ||
        out.second_match != 0U || base_504da0 - 73U <= 5U ||
        base_504da0 - 169U <= 11U || base_504da0 - 19U <= 5U ||
        object_state > 9U) {
        return out;
    }
    (void)control_504dc8;
    (void)mode_504e30;
    out.dispatch_allowed = out.selector <= 9U;
    if (out.dispatch_allowed != 0U)
        out.handler_target = state_handler_target(object_state);
    return out;
}
