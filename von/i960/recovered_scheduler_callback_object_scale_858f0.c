/* Callback object-scale publication recovered from i960 0x858f0-0x85974. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_callback_object_scale_858f0 {
    int32_t object_48;
    int32_t object_4a;
    int32_t object_190;
    int32_t related_state;
    int32_t related_source;
    int32_t normalized_48;
    int32_t normalized_4a;
    int32_t quotient;
    int32_t value_509b8c;
    int32_t value_509b90;
    u32 scaled;
};

struct recovered_scheduler_callback_object_scale_858f0
recovered_scheduler_callback_object_scale_858f0(int16_t object_48,
                                                int16_t object_4a,
                                                int32_t object_190,
                                                int32_t related_state,
                                                int32_t related_63c,
                                                int32_t related_640)
{
    struct recovered_scheduler_callback_object_scale_858f0 out;
    int32_t source = 0;

    out.object_48 = object_48;
    out.object_4a = object_4a;
    out.object_190 = object_190;
    out.related_state = related_state;
    out.related_source = 0;
    out.normalized_48 = object_48;
    out.normalized_4a = object_4a;
    out.quotient = 0;
    out.value_509b8c = out.normalized_48;
    out.value_509b90 = out.normalized_4a;
    out.scaled = 0U;
    if (object_190 == 0 && (related_state == 11 || related_state == 14)) {
        if (related_state == 11) {
            source = related_63c;
            out.related_source = 63;
        } else {
            source = related_640;
            out.related_source = 64;
        }
        out.quotient = source / 100;
        out.value_509b90 = out.normalized_4a * out.quotient;
        out.scaled = 1U;
    }
    return out;
}
