/* Compact callback/state trampolines recovered from i960 0x8d0b0-0x8d134. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 callback;
    recovered_u32 callback_return;
    recovered_u32 state_address, state_value;
} recovered_startup_mode4_arm_8d0b0_store_result;

typedef struct {
    recovered_u32 callback;
    recovered_u32 callback_return;
    recovered_u32 state_address, state_value;
    recovered_u32 returned_value;
} recovered_startup_mode4_arm_8d0d0_query_result;

typedef struct {
    recovered_u32 callback;
    recovered_u32 callback_return;
    recovered_u32 timing_address, timing_value;
    recovered_u32 progress_address, progress_value;
    recovered_u32 latch_address, latch_value;
} recovered_startup_mode4_arm_8d100_initialize_result;

typedef struct {
    recovered_u32 callback;
    recovered_u32 callback_return;
    recovered_u32 state_address, state_value;
    recovered_u32 returned_value;
} recovered_startup_mode4_arm_8d140_query_result;

int recovered_startup_mode4_arm_8d0b0_store(
    recovered_u32 callback, recovered_u32 state_value,
    recovered_startup_mode4_arm_8d0b0_store_result *result)
{
    recovered_startup_mode4_arm_8d0b0_store_result r = {0};
    r.callback = callback;
    r.callback_return = 0x8d0ccU;
    r.state_address = 0x51c9d0U;
    r.state_value = state_value;
    return result != (void *)0 ? (*result = r, 1) : 1;
}

int recovered_startup_mode4_arm_8d0d0_query(
    recovered_u32 callback, recovered_u32 state_value,
    recovered_startup_mode4_arm_8d0d0_query_result *result)
{
    recovered_startup_mode4_arm_8d0d0_query_result r = {0};
    r.callback = callback;
    r.callback_return = 0x8d0fcU;
    r.state_address = 0x51d5e0U;
    r.state_value = state_value;
    r.returned_value = state_value == 1U ? 1U : 0U;
    return result != (void *)0 ? (*result = r, 1) : 1;
}

int recovered_startup_mode4_arm_8d100_initialize(
    recovered_u32 callback,
    recovered_startup_mode4_arm_8d100_initialize_result *result)
{
    recovered_startup_mode4_arm_8d100_initialize_result r = {0};
    r.callback = callback;
    r.callback_return = 0x8d134U;
    r.timing_address = 0x51d5e0U;
    r.timing_value = 2U;
    r.progress_address = 0x503a04U;
    r.progress_value = 1U;
    r.latch_address = 0x51c9c0U;
    r.latch_value = 1U;
    return result != (void *)0 ? (*result = r, 1) : 1;
}

int recovered_startup_mode4_arm_8d140_query(
    recovered_u32 callback, recovered_u32 state_value,
    recovered_startup_mode4_arm_8d140_query_result *result)
{
    recovered_startup_mode4_arm_8d140_query_result r = {0};
    r.callback = callback;
    r.callback_return = 0x8d16cU;
    r.state_address = 0x51c9c0U;
    r.state_value = state_value;
    r.returned_value = state_value == 1U ? 1U : 0U;
    return result != (void *)0 ? (*result = r, 1) : 1;
}
