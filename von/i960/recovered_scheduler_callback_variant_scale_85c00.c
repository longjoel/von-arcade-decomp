/* Stable setup prefix of the callback table mutator at i960 0x85c00-0x85c54. */

#include <stdint.h>

typedef uint32_t u32;
typedef int32_t s32;

struct recovered_scheduler_callback_variant_scale_85c00 {
    int16_t object_4a;
    s32 object_190;
    s32 related_state;
    s32 related_source;
    s32 quotient;
    s32 working_value;
    u32 uses_related_source;
};

struct recovered_scheduler_callback_variant_scale_85c00
recovered_scheduler_callback_variant_scale_85c00(
    int16_t object_4a, s32 object_190, s32 related_state,
    s32 related_63c, s32 related_640)
{
    struct recovered_scheduler_callback_variant_scale_85c00 out;

    out.object_4a = object_4a;
    out.object_190 = object_190;
    out.related_state = related_state;
    out.related_source = 0;
    out.quotient = 0;
    out.working_value = object_4a;
    out.uses_related_source = 0U;

    if (object_190 != 0) {
        out.working_value = 0;
    } else if (related_state == 11 || related_state == 14) {
        out.related_source = related_state == 11 ? related_63c : related_640;
        out.quotient = out.related_source / 100;
        out.working_value = out.quotient * object_4a;
        out.uses_related_source = 1U;
    }
    return out;
}
