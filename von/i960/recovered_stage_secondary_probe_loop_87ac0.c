/* Secondary stage probe/retry controller recovered from i960 0x87ac0-0x87b10. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_stage_secondary_probe_loop_87ac0 {
    u32 phase;
    u32 initial_probe_result;
    u32 first_callback_result;
    u32 retry_callback_results[5];
    u32 retry_count;
    u32 helper_8d108_called;
    u32 helper_8d108_target;
    u32 tail_target;
    u32 continuation;
};

struct recovered_stage_secondary_probe_loop_87ac0
recovered_stage_secondary_probe_loop_87ac0(u32 phase,
                                          u32 initial_probe_result,
                                          u32 first_callback_result,
                                          const u32 retry_callback_results[5])
{
    struct recovered_stage_secondary_probe_loop_87ac0 out;
    u32 retry_index;

    out.phase = phase;
    out.initial_probe_result = initial_probe_result;
    out.first_callback_result = first_callback_result;
    out.retry_count = 0U;
    out.helper_8d108_called = 0U;
    out.helper_8d108_target = 0x0008d108U;
    out.tail_target = 0U;
    out.continuation = 0x00087b2cU;
    for (retry_index = 0U; retry_index < 5U; ++retry_index)
        out.retry_callback_results[retry_index] = retry_callback_results[retry_index];

    if (phase == 20U || initial_probe_result == 1U) {
        if (phase == 20U || initial_probe_result != 1U)
            return out;
        if (first_callback_result == 0U) {
            out.helper_8d108_called = 1U;
            out.tail_target = 0x00087b10U;
            return out;
        }
        for (retry_index = 0U; retry_index < 5U; ++retry_index) {
            out.retry_count = retry_index + 1U;
            if (retry_callback_results[retry_index] != 0U) {
                out.helper_8d108_called = 1U;
                out.tail_target = 0x00087b10U;
                return out;
            }
        }
        out.tail_target = 0x00087b10U;
    }
    return out;
}
