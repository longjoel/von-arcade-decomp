/* Credit arithmetic formatter recovered from i960 0xf1db0-f1ebc. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 divisor_r8, addend_r11, scale_r12, x_base_r10, y_base_r9;
    recovered_u32 valid, iteration_count, rendered_count;
    recovered_u32 product[5], adjusted_product[5], quotient[5], remainder[5];
    recovered_u32 render_kind[5], rendered_string[5], rendered_x[5], rendered_y[5];
    recovered_u32 blank_string, special_string, general_string, return_target;
} recovered_diagnostic_credit_math_formatter_result_f1db0;

int
recovered_diagnostic_credit_math_formatter_f1db0(
    recovered_u32 r10, recovered_u32 r9, recovered_u32 r12,
    recovered_u32 r11, recovered_u32 r8,
    recovered_diagnostic_credit_math_formatter_result_f1db0 *result)
{
    recovered_diagnostic_credit_math_formatter_result_f1db0 local = {0};
    local.divisor_r8=r8; local.addend_r11=r11; local.scale_r12=r12;
    local.x_base_r10=r10; local.y_base_r9=r9;
    local.blank_string=0x000f1d90U; local.special_string=0x000f1d50U;
    local.general_string=0x000f1d70U; local.return_target=0x000f1ebcU;
    if (r12 == 0U) { if (result != (void *)0) *result=local; return 0; }
    local.valid=1U;
    recovered_u32 prior=0U, continue_loop=1U;
    for (recovered_u32 i=0U; i<5U; ++i) {
        if (!continue_loop) { local.rendered_string[i]=local.blank_string; local.rendered_y[i]=r9+i; continue; }
        recovered_u32 product=(i+1U)*r11, adjusted=product;
        if (r8 != 0U && product < r8) adjusted += product/r8;
        if (r8 != 0U && product >= r8) continue_loop=0U;
        local.product[i]=product; local.adjusted_product[i]=adjusted;
        local.quotient[i]=adjusted/r12; local.remainder[i]=adjusted%r12;
        local.rendered_x[i]=r10; local.rendered_y[i]=r9+i;
        if (local.quotient[i] == 0U || local.quotient[i] <= prior) {
            local.render_kind[i]=0U; local.rendered_string[i]=local.blank_string;
        } else if (i == 0U && 1U < local.quotient[i] && 1U%local.quotient[i] == 0U) {
            local.render_kind[i]=1U; local.rendered_string[i]=local.special_string;
        } else { local.render_kind[i]=2U; local.rendered_string[i]=local.general_string; }
        if (local.render_kind[i] != 0U) ++local.rendered_count;
        prior=local.quotient[i];
    }
    local.iteration_count=5U;
    if (result != (void *)0) *result=local;
    return 1;
}
