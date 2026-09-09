/* Startup mode handler 3 recovered from i960 0x190d0-0x19170. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 setup_call, setup_argument, reset_call, phase_helper_call;
    recovered_u32 enabled_byte_address, enabled_byte_value;
    recovered_u32 video_base_address, video_base_value;
    recovered_u32 upload_base_address, upload_base_value;
    recovered_u32 clear_address[9], clear_count;
    recovered_u32 mode_address, mode_before, mode_after;
    recovered_u32 return_target;
} recovered_startup_mode_handler_3_result_190d0;

int recovered_startup_mode_handler_3_190d0(
    recovered_u32 mode_value,
    recovered_startup_mode_handler_3_result_190d0 *result)
{
    recovered_startup_mode_handler_3_result_190d0 r = {0};
    static const recovered_u32 clears[9] = {
        0x503a84U, 0x503a80U, 0x503a88U, 0x504c98U,
        0x503a8cU, 0x503a90U, 0x503a1cU, 0x504c90U, 0x503ac0U
    };
    r.setup_call = 0x2a4e0U;
    r.setup_argument = 0x1111U;
    r.reset_call = 0x1c618U;
    r.phase_helper_call = 0x1bda0U;
    r.enabled_byte_address = 0x504b96U;
    r.enabled_byte_value = 1U;
    r.video_base_address = 0x503b48U;
    r.video_base_value = 0x5046d0U;
    r.upload_base_address = 0x504148U;
    r.upload_base_value = 0x504930U;
    for (recovered_u32 i = 0; i < 9U; ++i)
        r.clear_address[i] = clears[i];
    r.clear_count = 9U;
    r.mode_address = 0x5039f4U;
    r.mode_before = mode_value;
    r.mode_after = mode_value + 1U;
    r.return_target = 0x19170U;
    if (result != (void *)0)
        *result = r;
    return 1;
}
