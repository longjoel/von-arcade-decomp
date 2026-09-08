/* Shared service postprocessing recovered from i960 0x830c0-0x83108. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_service_postprocess_830c0 {
    u32 value_504d94;
    u32 value_504d98;
    u32 value_504db8;
    u32 wrote_status_12;
    u32 wrote_related_default;
};

struct recovered_state_service_postprocess_830c0
recovered_state_service_postprocess_830c0(u32 current_state,
                                          u32 status_504d98,
                                          u32 related_state,
                                          u32 caller_g14)
{
    struct recovered_state_service_postprocess_830c0 out = {
        caller_g14, status_504d98, 0U, 0U, 0U
    };

    if (current_state == 3U && out.value_504d98 == 9U) {
        out.value_504d98 = 12U;
        out.wrote_status_12 = 1U;
    }
    if (related_state == 0U) {
        out.value_504d98 = 1U;
        out.value_504db8 = 10U;
        out.wrote_related_default = 1U;
    }
    return out;
}
