/* Shared post-selector dispatch gate recovered from i960 0x8b620-0x8b678. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 counter_51c984;
    recovered_u32 g14_value;
    recovered_u32 threshold_61;
    recovered_u32 threshold_77;
    recovered_u32 selector_51c99c;
    recovered_u32 source_object;
    recovered_u32 linked_record;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_8b620_dispatch_gate_result;

recovered_startup_mode4_arm_8b620_dispatch_gate_result
recovered_startup_mode4_arm_8b620_dispatch_gate(
    recovered_u32 counter_51c984, recovered_u32 g14_value,
    recovered_u32 source_object, recovered_u32 linked_record)
{
    recovered_startup_mode4_arm_8b620_dispatch_gate_result result;

    result.counter_51c984 = counter_51c984;
    result.g14_value = g14_value;
    result.threshold_61 = 61U;
    result.threshold_77 = 0x77U;
    result.source_object = source_object;
    result.linked_record = linked_record;
    if (counter_51c984 <= 61U)
        result.selector_51c99c = g14_value;
    else if (counter_51c984 <= 0x77U)
        result.selector_51c99c = 1U;
    else
        result.selector_51c99c = 2U;
    result.continuation = 0x0008b678U;
    return result;
}
