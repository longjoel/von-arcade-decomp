/* Slot-10 ready-clear grid update recovered from i960 0x1a7d0-0x1a820. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 ready_address, ready_value;
    recovered_u32 base_address, base_before, base_after;
    recovered_u32 divisor, register_r17, register_r29;
    recovered_u32 base_value, base_remainder, base_quotient;
    recovered_u32 bucket_divisor, bucket_quotient;
    recovered_u32 offset_value, offset_remainder;
    recovered_u32 scaled_remainder, grid_stride, grid_index;
    recovered_u32 helper_address, helper_call_count;
    recovered_u32 helper_argument0, helper_argument1, helper_argument2;
    recovered_u32 invalid_divisor, continuation;
} recovered_startup_mode4_arm_1a7d0_grid_update_result;

int recovered_startup_mode4_arm_1a7d0_grid_update(
    recovered_u32 ready_value, recovered_u32 base_value,
    recovered_u32 register_r17, recovered_u32 register_r29,
    recovered_startup_mode4_arm_1a7d0_grid_update_result *result)
{
    recovered_startup_mode4_arm_1a7d0_grid_update_result r = {0};
    r.ready_address = 0x503a7cU;
    r.ready_value = ready_value;
    r.base_address = 0x503a1cU;
    r.base_before = base_value;
    r.base_after = base_value + 1U;
    r.divisor = r.base_after;
    r.register_r17 = register_r17;
    r.register_r29 = register_r29;
    r.base_value = 31U + register_r17;
    r.bucket_divisor = 0xb40U;
    r.offset_value = 31U + register_r29;
    r.helper_address = 0x1e9e0U;
    r.continuation = 0x1a820U;
    if (ready_value == 0U) {
        if (r.divisor == 0U) {
            r.invalid_divisor = 1U;
        } else {
            r.base_remainder = r.base_value % r.divisor;
            r.base_quotient = r.base_value / r.divisor;
            r.bucket_quotient = r.bucket_divisor / r.divisor;
            r.scaled_remainder = 35U * r.base_remainder;
            r.grid_stride = r.scaled_remainder;
            if (r.base_quotient == 0U || r.grid_stride == 0U) {
                r.invalid_divisor = 1U;
            } else {
                r.offset_remainder = r.offset_value % r.base_quotient;
                r.grid_index = r.base_value / r.grid_stride;
                r.helper_call_count = 1U;
                r.helper_argument0 = r.bucket_quotient;
                r.helper_argument1 = r.offset_remainder;
                r.helper_argument2 = r.grid_index;
            }
        }
    }
    return result != (void *)0 ? (*result = r, 1) : 1;
}
