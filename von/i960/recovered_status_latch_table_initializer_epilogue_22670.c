/* ABI epilogue recovered from i960 0x22670-0x226a0. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_status_latch_table_initializer_epilogue_plan {
    u32 integer_quad_restore_count;
    u32 g13_restore_offset;
    u32 g14_restore_offset;
    u32 floating_restore_count;
    u32 floating_offsets[4];
    u32 return_instruction;
};

void recovered_status_latch_table_initializer_epilogue_plan(
    struct recovered_status_latch_table_initializer_epilogue_plan *plan)
{
    plan->integer_quad_restore_count = 2U;
    plan->g13_restore_offset = 0x40U;
    plan->g14_restore_offset = 0x44U;
    plan->floating_restore_count = 4U;
    plan->floating_offsets[0] = 0x48U;
    plan->floating_offsets[1] = 0x58U;
    plan->floating_offsets[2] = 0x68U;
    plan->floating_offsets[3] = 0x78U;
    plan->return_instruction = 0x0000000aU;
}
