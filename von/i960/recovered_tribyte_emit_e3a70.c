/* Three-byte status emitter recovered from i960 0xe3a70-0xe3aa4. */
#include <stdint.h>

typedef uint32_t u32;
typedef int32_t s32;

struct recovered_tribyte_emit_plan {
    u32 callee;
    u32 byte_count;
    u32 offsets[3];
    s32 bytes[3];
};

void recovered_tribyte_emit_plan(const u32 raw[3],
                                 struct recovered_tribyte_emit_plan *plan)
{
    u32 index;

    plan->callee = 0x0001d570U;
    plan->byte_count = 3U;
    for (index = 0U; index < 3U; ++index) {
        plan->offsets[index] = index;
        /* shlo 24/shri 24 sign-extends each low byte (shri is
         * arithmetic in the i960 core). */
        plan->bytes[index] = (s32)(signed char)(raw[index] & 0xffU);
    }
}
