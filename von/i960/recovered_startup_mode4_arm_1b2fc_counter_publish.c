/* Slot-11 counter/publication seam recovered from i960 0x1b2fc-0x1b37c. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 counter_74_address, counter_74_before, counter_74_after;
    recovered_u32 counter_6c_address, counter_6c_value, counter_6c_low;
    recovered_u32 counter_70_address, counter_70_value, counter_70_low;
    recovered_u32 ready_address, ready_value;
    recovered_u32 limit_address, limit_value;
    recovered_u32 row_address, row_value;
    recovered_u32 publication_30a_address, publication_30a_value;
    recovered_u32 publication_30c_address, publication_30c_value;
    recovered_u32 publication_30e_address, publication_30e_value;
    recovered_u32 trigger_ready_clear, trigger_progress_exceeded;
    recovered_u32 trigger_row_exceeded, trigger_command;
    recovered_u32 command_address, command_value;
    recovered_u32 trigger_call, continuation_target;
} recovered_startup_mode4_arm_result_1b2fc_counter_publish;

int recovered_startup_mode4_arm_1b2fc_counter_publish(
    recovered_u32 counter_74_value, recovered_u32 counter_6c_value,
    recovered_u32 counter_70_value, recovered_u32 ready_value,
    recovered_u32 limit_value, recovered_u32 row_value,
    recovered_startup_mode4_arm_result_1b2fc_counter_publish *result)
{
    recovered_startup_mode4_arm_result_1b2fc_counter_publish r = {0};

    r.counter_74_address = 0x503a74U;
    r.counter_74_before = counter_74_value;
    r.counter_74_after = counter_74_value + 1U;
    r.counter_6c_address = 0x503a6cU;
    r.counter_6c_value = counter_6c_value;
    r.counter_6c_low = counter_6c_value & 0xffffU;
    r.counter_70_address = 0x503a70U;
    r.counter_70_value = counter_70_value;
    r.counter_70_low = counter_70_value & 0xffffU;
    r.ready_address = 0x503a7cU;
    r.ready_value = ready_value;
    r.limit_address = 0x503a78U;
    r.limit_value = limit_value;
    r.row_address = 0x503a80U;
    r.row_value = row_value;
    r.publication_30a_address = 0x50330aU;
    r.publication_30a_value = r.counter_74_after & 0xffffU;
    r.publication_30c_address = 0x50330cU;
    r.publication_30c_value = r.counter_6c_low;
    r.publication_30e_address = 0x50330eU;
    r.publication_30e_value = r.counter_70_low;
    r.trigger_ready_clear = ready_value == 0U ? 1U : 0U;
    /* The later gates reload the full counter and use signed comparisons. */
    r.trigger_progress_exceeded = (int32_t)counter_6c_value >
                                  (int32_t)limit_value ? 1U : 0U;
    r.trigger_row_exceeded = (int32_t)row_value > 8 ? 1U : 0U;
    r.trigger_command = r.trigger_ready_clear != 0U &&
                        r.trigger_progress_exceeded != 0U &&
                        r.trigger_row_exceeded != 0U;
    r.command_address = 0x5032f4U;
    r.command_value = r.trigger_command != 0U ? 20U : 0U;
    r.trigger_call = r.trigger_command != 0U ? 0x31c0U : 0U;
    r.continuation_target = 0x1b380U;
    if (result != (void *)0)
        *result = r;
    return 1;
}
