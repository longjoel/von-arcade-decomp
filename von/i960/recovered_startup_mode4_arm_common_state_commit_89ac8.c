/* Common selector-tail state commit recovered from i960 0x89ac8-0x89b20. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 record_30;
    recovered_u32 record_64;
    recovered_u32 g14_value;
    recovered_u32 prior_51d5e0;
    recovered_u32 state_51c950;
    recovered_u32 state_51c94c;
    recovered_u32 state_51c954;
    recovered_u32 state_51c9b4;
    recovered_u32 state_51d5e0;
    recovered_u32 state_51c958;
    recovered_u32 state_51c95c;
    recovered_u32 state_51c960;
    recovered_u32 state_51c9b4_address;
    recovered_u32 state_51d5e0_address;
    recovered_u32 return_address;
} recovered_startup_mode4_arm_common_state_commit_89ac8_result;

recovered_startup_mode4_arm_common_state_commit_89ac8_result
recovered_startup_mode4_arm_common_state_commit_89ac8(
    recovered_u32 record_30, recovered_u32 record_64, recovered_u32 g14_value,
    recovered_u32 prior_51d5e0,
    recovered_u32 state_51c950, recovered_u32 state_51c94c,
    recovered_u32 state_51c954)
{
    recovered_startup_mode4_arm_common_state_commit_89ac8_result result;

    result.record_30 = record_30;
    result.record_64 = record_64;
    result.g14_value = g14_value;
    result.prior_51d5e0 = prior_51d5e0;
    result.state_51c950 = state_51c950;
    result.state_51c94c = state_51c94c;
    result.state_51c954 = state_51c954;
    result.state_51c9b4 = record_30 == 0U ? 1U : g14_value;
    result.state_51d5e0 = record_64 == 7U ? g14_value : prior_51d5e0;
    result.state_51c958 = state_51c950;
    result.state_51c95c = state_51c94c;
    result.state_51c960 = state_51c954;
    result.state_51c9b4_address = 0x51c9b4U;
    result.state_51d5e0_address = 0x51d5e0U;
    result.return_address = 0x00089b20U;
    return result;
}
