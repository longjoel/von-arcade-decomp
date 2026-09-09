/* Slot-11 setup prefix recovered from i960 0x1afe0-0x1b054. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 ready_address, ready_value;
    recovered_u32 marker_address, marker_value;
    recovered_u32 base_address, base_value;
    recovered_u32 divisor_register, divisor_value;
    recovered_u32 base_quotient, base_remainder;
    recovered_u32 bucket_divisor, bucket_quotient;
    recovered_u32 offset_value, bucket_remainder;
    recovered_u32 scaled_remainder, grid_index;
    recovered_u32 helper_call, helper_argument;
    recovered_u32 timing_source_address, timing_source_value;
    recovered_u32 row_address, row_value;
    recovered_u32 timing_delta;
    recovered_u32 timing_table_address, timing_table_index;
    recovered_u32 timing_table_write_address, timing_table_write_value;
    recovered_u32 continuation_call, continuation_target;
    recovered_u32 valid;
} recovered_startup_mode4_arm_result_1afe0_prefix;

int recovered_startup_mode4_arm_1afe0_prefix(
    recovered_u32 ready_value, recovered_u32 base_value,
    recovered_u32 register_17_value, recovered_u32 register_29_value,
    recovered_u32 timing_source_value, recovered_u32 row_value,
    recovered_u32 register_14_value,
    recovered_startup_mode4_arm_result_1afe0_prefix *result)
{
    recovered_startup_mode4_arm_result_1afe0_prefix r = {0};
    recovered_u32 divisor = register_17_value + 31U;
    recovered_u32 quotient;

    r.ready_address = 0x503a7cU;
    r.ready_value = ready_value;
    r.marker_address = 0x503a60U;
    r.marker_value = register_14_value;
    r.base_address = 0x503a1cU;
    r.base_value = base_value;
    r.divisor_register = 17U;
    r.divisor_value = divisor;
    r.bucket_divisor = 0xb40U;
    r.offset_value = register_29_value + 31U;
    r.timing_source_address = 0x504c90U;
    r.timing_source_value = timing_source_value;
    r.row_address = 0x503a80U;
    r.row_value = row_value;
    r.timing_table_address = 0x503a30U;
    r.continuation_call = 0xde630U;
    r.continuation_target = 0x1b054U;

    if (ready_value == 0U && divisor != 0U) {
        r.base_quotient = base_value / divisor;
        r.base_remainder = base_value % divisor;
        r.bucket_quotient = base_value / r.bucket_divisor;
        quotient = r.base_quotient;
        if (quotient != 0U) {
            r.bucket_remainder = r.offset_value % quotient;
            /* lda (g2)[g2*2],g2 makes 3*remainder; the following shift and
             * addo therefore produce (96+3)*remainder = 99*remainder. */
            r.scaled_remainder = r.base_remainder * 99U;
            r.grid_index = r.scaled_remainder / divisor;
            r.helper_call = 0x1e9e0U;
            r.helper_argument = r.grid_index;
            r.timing_delta = base_value - timing_source_value;
            r.timing_table_index = row_value;
            r.timing_table_write_address = r.timing_table_address + row_value * 4U;
            r.timing_table_write_value = r.timing_delta;
            r.valid = 1U;
        }
    }
    if (result != (void *)0)
        *result = r;
    return 1;
}
