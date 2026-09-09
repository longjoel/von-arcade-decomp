/* Slot-12 row-5 phase gate recovered from i960 0x1b8a8-0x1b910. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 row_value, row_gate;
    recovered_u32 base_address, base_value;
    recovered_u32 divisor_address, divisor_value, quotient;
    recovered_u32 quotient_threshold, quotient_high;
    recovered_u32 register_19_value;
    recovered_u32 command_address, command_value;
    recovered_u32 state_address, state_value;
    recovered_u32 row_address, row_publication;
    recovered_u32 progress_address, progress_value, progress_written;
    recovered_u32 mmio_address, mmio_before, mmio_after;
    recovered_u32 mmio_bit_set;
    recovered_u32 branch, continuation_target, valid;
} recovered_startup_mode4_arm_result_1b8a8_row5_gate;

int recovered_startup_mode4_arm_1b8a8_row5_gate(
    recovered_u32 row_value, recovered_u32 base_value,
    recovered_u32 divisor_value, recovered_u32 register_19_value,
    recovered_u32 incoming_value, recovered_u32 mmio_value,
    recovered_startup_mode4_arm_result_1b8a8_row5_gate *result)
{
    recovered_startup_mode4_arm_result_1b8a8_row5_gate r = {0};

    r.row_value = row_value;
    r.row_gate = 5U;
    r.base_address = 0x503a1cU;
    r.base_value = base_value;
    r.divisor_address = 0x503a8cU;
    r.divisor_value = divisor_value;
    r.quotient_threshold = 0x690U;
    r.register_19_value = register_19_value;
    r.command_address = 0x5032f4U;
    r.command_value = (register_19_value + 31U) & 0xffffU;
    r.state_address = 0x503a00U;
    r.row_address = 0x503a80U;
    r.progress_address = 0x503a04U;
    r.progress_value = incoming_value;
    r.mmio_address = 0x10000000U;
    r.mmio_before = (recovered_u32)
        recovered_sign_extend_16(mmio_value & 0xffffU);
    r.mmio_after = r.mmio_before;
    if (row_value != r.row_gate) {
        r.branch = 1U;
        r.continuation_target = 0x1b914U;
        r.valid = 1U;
    } else if (divisor_value == 0U) {
        r.valid = 0U;
    } else {
        int32_t signed_base = (int32_t)base_value;
        int32_t signed_divisor = (int32_t)divisor_value;
        int32_t signed_quotient;

        r.valid = 1U;
        /* divi/bg use signed i960 integer semantics. */
        if (signed_base == INT32_MIN && signed_divisor == -1) {
            signed_quotient = INT32_MIN;
        } else {
            signed_quotient = signed_base / signed_divisor;
        }
        r.quotient = (recovered_u32)signed_quotient;
        r.quotient_high = signed_quotient > (int32_t)r.quotient_threshold ? 1U : 0U;
        if (r.quotient_high == 0U) {
            r.state_value = 6U;
            r.row_publication = 6U;
            r.branch = 2U;
            r.continuation_target = 0x1b924U;
        } else {
            r.state_value = 27U;
            r.progress_written = 1U;
            r.mmio_after = (r.mmio_before | 1U) & 0xffffU;
            r.mmio_bit_set = 1U;
            r.branch = 3U;
            r.continuation_target = 0x1b940U;
        }
    }
    return result != (void *)0 ? (*result = r, 1) : 1;
}
