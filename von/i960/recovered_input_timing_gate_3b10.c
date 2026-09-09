/* Input timing gate recovered from i960 0x3b10-0x3b9c. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_input_timing_gate_3b10 {
    u32 counter_step;
    u32 limit_check_passed;
    u32 status34_checked;
    u32 status34_nonzero;
    u32 status_a4_bit4_checked;
    u32 status_a4_bit4_set;
    u32 accepted;
    u32 field38_subtracted;
    u32 field38_after;
    u32 table_copy_called;
    u32 service_called;
    u32 service_argument;
    u32 table_copy_helper;
    u32 service_helper;
    u32 return_address;
};

void recovered_input_timing_gate_3b10(
    u32 counter_halfword, u32 field38, u32 status34, u32 status_a4,
    struct recovered_input_timing_gate_3b10 *out)
{
    u32 step = (counter_halfword + 1U) & 0xffffU;
    u32 limit_passed = field38 >= step;
    u32 preliminary_passed = limit_passed || status34 != 0U;
    u32 flag_set = (status_a4 & 0x10U) != 0U;

    out->counter_step = step;
    out->limit_check_passed = limit_passed;
    out->status34_checked = limit_passed == 0U;
    out->status34_nonzero = status34 != 0U;
    out->status_a4_bit4_checked = preliminary_passed;
    out->status_a4_bit4_set = preliminary_passed && flag_set;
    out->accepted = preliminary_passed && flag_set;
    /* The bne at 0x3b68 skips the copy for ordinary steps; only the
     * counter-wrap value zero reaches the subtract/store/copy sequence. */
    out->field38_subtracted = out->accepted && step == 0U;
    out->field38_after = out->field38_subtracted != 0U ? field38 - step : field38;
    out->table_copy_called = out->field38_subtracted;
    out->service_called = out->accepted;
    out->service_argument = 0x111cU;
    out->table_copy_helper = 0x00002330U;
    out->service_helper = 0x0002a580U;
    out->return_address = out->accepted != 0U ? 0x00003b94U : 0x00003b98U;
}
