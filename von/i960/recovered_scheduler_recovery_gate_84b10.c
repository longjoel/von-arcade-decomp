/* Recovery/table gate recovered from i960 0x84b10-0x84b7c. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_recovery_gate_84b10 {
    int32_t value_509a70;
    u32 writes_509a70;
    u32 table_base;
    u32 continues_to_scan;
};

struct recovered_scheduler_recovery_gate_84b10
recovered_scheduler_recovery_gate_84b10(int32_t value_509a70,
                                        u32 related_field_64,
                                        u32 value_504e50,
                                        u32 value_509ac0,
                                        int32_t value_503a14)
{
    struct recovered_scheduler_recovery_gate_84b10 out = {
        value_509a70, 0U, 0x5074a0U + related_field_64 * 1024U, 0U
    };
    u32 bit2_set = value_504e50 & (1U << 2);

    if (out.value_509a70 >= 0) {
        out.value_509a70++;
        if (out.value_509a70 > 120)
            out.value_509a70 = 0;
        out.writes_509a70 = 1U;
    }
    if (value_509ac0 == 1U && bit2_set == 0U
        && value_503a14 > 239 && out.value_509a70 == 0)
        out.continues_to_scan = 1U;
    return out;
}
