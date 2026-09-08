/* Callback dimension finalizer recovered from i960 0x85844-0x858e0. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_callback_finalize_85844 {
    u32 value_g1;
    u32 value_g2;
    u32 value_g3;
    u32 value_g13;
    u32 value_504dac;
    u32 value_504db0;
};

static u32 recovered_dimension(u32 dimension, u32 flags)
{
    if (dimension != 2U)
        return 1U;
    return (flags & 1U) != 0U ? 2U : 4U;
}

static u32 recovered_mode_bits(u32 dimension, u32 flags)
{
    u32 value = dimension == 16U ? 0U : (1U << 3);

    if (dimension == 16U)
        value |= (flags & (1U << 3)) != 0U ? (1U << 4) : (1U << 5);
    return value;
}

struct recovered_scheduler_callback_finalize_85844
recovered_scheduler_callback_finalize_85844(u32 value_g1, u32 value_g2,
                                            u32 value_g3, u32 value_g13,
                                            u32 value_504dac,
                                            u32 value_504db0)
{
    struct recovered_scheduler_callback_finalize_85844 out;

    out.value_g1 = value_g1;
    out.value_g2 = value_g2;
    out.value_g3 = value_g3;
    out.value_g13 = value_g13;
    out.value_504dac = recovered_dimension(value_g1, value_504dac)
        | recovered_mode_bits(value_g3, value_504dac);
    out.value_504db0 = recovered_dimension(value_g2, value_504db0)
        | recovered_mode_bits(value_g13, value_504db0);
    return out;
}
