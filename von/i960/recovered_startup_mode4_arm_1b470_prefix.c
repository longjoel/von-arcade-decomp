/* Slot-12 setup/arithmetic prefix recovered from i960 0x1b470-0x1b4b4. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 ready_address, ready_value;
    recovered_u32 base_address, base_value;
    recovered_u32 divisor_value, base_remainder, base_quotient;
    recovered_u32 bucket_divisor, bucket_quotient;
    recovered_u32 offset_value, offset_remainder;
    recovered_u32 scaled_remainder, helper_argument;
    recovered_u32 helper_call, result_address;
    recovered_u32 continuation_call, continuation_target;
    recovered_u32 valid;
} recovered_startup_mode4_arm_1b470_prefix_result;

int recovered_startup_mode4_arm_1b470_prefix(
    recovered_u32 ready_value, recovered_u32 base_value,
    recovered_u32 register_r17, recovered_u32 register_r29,
    recovered_startup_mode4_arm_1b470_prefix_result *result)
{
    recovered_startup_mode4_arm_1b470_prefix_result r = {0};
    recovered_u32 divisor = register_r17 + 31U;
    r.ready_address = 0x503a7cU;
    r.ready_value = ready_value;
    r.base_address = 0x503a1cU;
    r.base_value = base_value;
    r.divisor_value = divisor;
    r.bucket_divisor = 0xb40U;
    r.offset_value = register_r29 + 31U;
    r.helper_call = 0U;
    r.result_address = 0x504c90U;
    r.continuation_call = 0x445a0U;
    r.continuation_target = 0x1b4b4U;
    if (ready_value == 0U && divisor != 0U) {
        r.base_remainder = base_value % divisor;
        r.base_quotient = base_value / divisor;
        r.bucket_quotient = base_value / r.bucket_divisor;
        if (r.base_quotient != 0U) {
            r.offset_remainder = r.offset_value % r.base_quotient;
            r.scaled_remainder = r.base_remainder * 99U;
            r.helper_argument = r.scaled_remainder / divisor;
            r.helper_call = 0x1e9e0U;
            r.valid = 1U;
        }
    }
    if (result != (void *)0)
        *result = r;
    return 1;
}
