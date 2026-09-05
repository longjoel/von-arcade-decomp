/* Mode divisor with saturation recovered from i960 0x78090-0x78110. */
#include <stdint.h>

typedef uint32_t u32;
typedef int32_t s32;

struct recovered_divisor_clamp_plan {
    u32 divisor;
    u32 divisor_wide;
    u32 divisor_narrow;
    s32 quotient_raw;
    s32 quotient_sat;
    u32 saturate_max;
    u32 flag_threshold;
    s32 flag;
};

void recovered_divisor_clamp_plan(u32 mode, s32 dividend,
                                  struct recovered_divisor_clamp_plan *plan)
{
    plan->divisor_wide = 0xbb8U;
    plan->divisor_narrow = 0x64U;
    /* be/cmpibe select the wide divisor for modes 4 and 7; the cmpibge
     * arm compares literal-first (4 >= mode), so mode 7 still reaches
     * its own check instead of falling into the narrow path. */
    plan->divisor = (mode == 4U || mode == 7U) ? plan->divisor_wide
                                              : plan->divisor_narrow;
    plan->quotient_raw = dividend / (s32)plan->divisor;
    plan->saturate_max = 90U;
    plan->quotient_sat = plan->quotient_raw > (s32)plan->saturate_max
        ? (s32)plan->saturate_max : plan->quotient_raw;
    plan->flag_threshold = 120U;
    plan->flag = dividend > (s32)plan->flag_threshold ? 1 : plan->quotient_sat;
}
