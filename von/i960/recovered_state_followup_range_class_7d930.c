/* Range-class selector recovered from i960 0x7d930-0x7d984. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_followup_range_class_7d930_plan {
    u32 values[4];
    u32 threshold;
    u32 selected_class;
};

struct recovered_state_followup_range_class_7d930_plan
recovered_state_followup_range_class_7d930(int16_t state_base_504d64)
{
    static const u32 offsets[4] = {0x0000e24fU, 0x0000a24fU,
                                   0x0000224fU, 0x0000624fU};
    struct recovered_state_followup_range_class_7d930_plan out;
    u32 i;

    out.threshold = 0x49eU;
    out.selected_class = 0U;
    for (i = 0U; i < 4U; ++i) {
        out.values[i] = ((u32)(int32_t)state_base_504d64 + offsets[i]) & 0xffffU;
        if (out.values[i] <= out.threshold)
            out.selected_class = 1U;
    }
    return out;
}
