/* Secondary slot-update trampoline recovered from i960 0x881b0-0x881f4. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_stage_slot_update_trampoline_881b0 {
    u32 counter_value;
    u32 first_value;
    u32 second_value;
    u32 modulo_divisor;
    u32 counter_remainder;
    u32 row_offset;
    u32 table_address;
    u32 first_store_address;
    u32 second_store_address;
    u32 trampoline_load_address;
    u32 trampoline_target;
    u32 continuation;
};

struct recovered_stage_slot_update_trampoline_881b0
recovered_stage_slot_update_trampoline_881b0(u32 counter_value,
                                             u32 first_value,
                                             u32 second_value)
{
    struct recovered_stage_slot_update_trampoline_881b0 out;

    out.counter_value = counter_value;
    out.first_value = first_value;
    out.second_value = second_value;
    out.modulo_divisor = 120U;
    out.counter_remainder = counter_value % out.modulo_divisor;
    out.row_offset = out.counter_remainder * 12U;
    out.table_address = 0x00561e90U;
    out.first_store_address = out.table_address + out.row_offset + 4U;
    out.second_store_address = out.table_address + out.row_offset + 8U;
    out.trampoline_load_address = 0x000881b0U;
    out.trampoline_target = 0x000881f4U;
    out.continuation = out.trampoline_target;
    return out;
}
