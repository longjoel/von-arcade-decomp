/* Selector-1 scale/state checkpoint recovered from i960 0x8c3d0-0x8c510. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 counter_51c984;
    recovered_u32 computed_scale;
    recovered_u32 state_51c94c;
    recovered_u32 rolling_51c958;
    recovered_u32 rolling_51c95c;
    recovered_u32 rolling_51c960;
    recovered_u32 counter_limit;
    recovered_u32 short_scan_path;
    recovered_u32 negative_rolling_path;
    recovered_u32 clamped_rolling_51c95c;
    recovered_u32 scale_constant;
    recovered_u32 compare_constant;
    recovered_u32 clamp_constant;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_8c3d0_scale_state_result;

recovered_startup_mode4_arm_8c3d0_scale_state_result
recovered_startup_mode4_arm_8c3d0_scale_state(
    recovered_u32 counter_51c984, recovered_u32 computed_scale,
    recovered_u32 rolling_51c958, recovered_u32 rolling_51c95c,
    recovered_u32 rolling_51c960)
{
    recovered_startup_mode4_arm_8c3d0_scale_state_result result;

    result.counter_51c984 = counter_51c984;
    result.computed_scale = computed_scale;
    result.state_51c94c = computed_scale;
    result.rolling_51c958 = rolling_51c958;
    result.rolling_51c95c = rolling_51c95c;
    result.rolling_51c960 = rolling_51c960;
    result.counter_limit = 120U;
    result.short_scan_path = counter_51c984 <= 120U ? 1U : 0U;
    result.negative_rolling_path = (int32_t)rolling_51c95c < 0 ? 1U : 0U;
    result.clamped_rolling_51c95c = result.negative_rolling_path != 0U ?
        0x41200000U : rolling_51c95c;
    if (result.negative_rolling_path != 0U)
        result.rolling_51c95c = result.clamped_rolling_51c95c;
    result.scale_constant = 0x403e0000U;
    result.compare_constant = 0x40240000U;
    result.clamp_constant = 0x41200000U;
    result.continuation = 0x0008c510U;
    return result;
}
