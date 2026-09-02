/* Signed position-delta helper recovered from i960 0x23ce8-0x23d5c. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_geometry_position_delta_plan {
    u32 return_stub;
    int32_t raw_delta;
    int32_t signed_limit;
    int32_t selected_delta;
    int32_t stored_position;
    u32 negative_delta_suppressed;
};

static int16_t store_halfword(int32_t value)
{
    return (int16_t)(uint16_t)value;
}

/*
 * The i960 cmpib* forms compare the displayed src1 and src2 operands.  Thus:
 *
 *   cmpible g5,g4  => branch when delta <= limit
 *   cmpibge g5,g4 => branch when delta >= -limit
 *
 * The deliberately direct spelling below follows those branches rather
 * than imposing a higher-level interpretation on the object fields.
 */
void recovered_geometry_position_delta_plan(
    int16_t object_1d0, int16_t object_1d2, int16_t object_1d4,
    u32 global_503a60,
    struct recovered_geometry_position_delta_plan *plan)
{
    int32_t delta = (int32_t)object_1d0 - (int32_t)object_1d2;
    int32_t limit = (int32_t)object_1d4;
    int32_t selected;
    u32 suppressed = 0U;

    if (delta <= limit) {
        selected = limit;
    } else if (delta >= -limit) {
        selected = delta;
    } else {
        selected = -limit;
    }

    if (selected < 0 && global_503a60 == 0U) {
        selected = 0;
        suppressed = 1U;
    }

    plan->return_stub = 0x00023d5cU;
    plan->raw_delta = delta;
    plan->signed_limit = limit;
    plan->selected_delta = selected;
    plan->stored_position = (int32_t)store_halfword(
        (int32_t)object_1d2 + selected);
    plan->negative_delta_suppressed = suppressed;
}
