/* Object ratio prefix recovered from i960 0x8490c-0x8497c. */

#include <stdint.h>

typedef uint32_t u32;

enum recovered_scheduler_object_ratio_prefix_8490c_source {
    RECOVERED_8490C_SOURCE_NONE = 0,
    RECOVERED_8490C_SOURCE_63C = 1,
    RECOVERED_8490C_SOURCE_640 = 2
};

struct recovered_scheduler_object_ratio_prefix_8490c {
    u32 rejected_nonzero_190;
    enum recovered_scheduler_object_ratio_prefix_8490c_source source;
    int32_t quotient;
    int32_t scaled_value;
    u32 zero_product_exit;
};

struct recovered_scheduler_object_ratio_prefix_8490c
recovered_scheduler_object_ratio_prefix_8490c(int32_t value_190,
                                              int32_t related_state,
                                              int32_t value_63c,
                                              int32_t value_640,
                                              int32_t value_4a)
{
    struct recovered_scheduler_object_ratio_prefix_8490c out = {
        0U, RECOVERED_8490C_SOURCE_NONE, 0, 0, 0U
    };
    int32_t source_value;

    if (value_190 != 0) {
        out.rejected_nonzero_190 = 1U;
        return out;
    }
    if (related_state == 11) {
        out.source = RECOVERED_8490C_SOURCE_63C;
        source_value = value_63c;
    } else if (related_state == 14) {
        out.source = RECOVERED_8490C_SOURCE_640;
        source_value = value_640;
    } else {
        return out;
    }
    out.quotient = source_value / 100;
    out.scaled_value = value_4a * out.quotient;
    out.zero_product_exit = out.scaled_value == 0;
    return out;
}
