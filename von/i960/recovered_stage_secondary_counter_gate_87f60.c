/* Secondary shared-helper counter gate recovered from i960 0x87f60-0x87fac. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_stage_secondary_counter_gate_87f60 {
    u32 phase_value;
    u32 counter_before;
    u32 seed_value;
    u32 counter_address;
    u32 counter_after;
    u32 initializer_target;
    u32 initializer_called;
    u32 counter_low_bits;
    u32 modulo_upload_admitted;
    u32 modulo_base;
    u32 modulo_remainder;
    u32 modulo_divisor;
    u32 upload_body_target;
};

struct recovered_stage_secondary_counter_gate_87f60
recovered_stage_secondary_counter_gate_87f60(u32 phase_value,
                                             u32 counter_before,
                                             u32 seed_value)
{
    struct recovered_stage_secondary_counter_gate_87f60 out;

    out.phase_value = phase_value;
    out.counter_before = counter_before;
    out.seed_value = seed_value;
    out.counter_address = 0x0051c9b0U;
    out.initializer_target = 0x0008d170U;
    out.initializer_called = phase_value == 0U ? 1U : 0U;
    out.counter_after = phase_value == 0U ? seed_value : counter_before + 1U;
    out.counter_low_bits = out.counter_after & 3U;
    out.modulo_upload_admitted = out.counter_low_bits == 0U ? 1U : 0U;
    out.modulo_divisor = 120U;
    out.modulo_remainder = out.counter_after % out.modulo_divisor;
    out.modulo_base = 15U << 3U;
    out.upload_body_target = 0x00087facU;
    return out;
}
