/* Slot-10 ready/status route recovered from i960 0x1a8d0-0x1a904. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 ready_address, ready_value;
    recovered_u32 hardware_address, hardware_mode;
    recovered_u32 status_address, status_word, status_threshold;
    recovered_u32 result_r5, result_r6;
    recovered_u32 accepted, rejected;
    recovered_u32 ready_clear_target, hardware_target, failed_status_target;
    recovered_u32 accepted_target, selected_target;
} recovered_startup_mode4_arm_1a8d0_ready_route_result;

int recovered_startup_mode4_arm_1a8d0_ready_route(
    recovered_u32 ready_value, recovered_u32 hardware_mode,
    recovered_u32 status_word, recovered_u32 result_r5, recovered_u32 result_r6,
    recovered_startup_mode4_arm_1a8d0_ready_route_result *result)
{
    recovered_startup_mode4_arm_1a8d0_ready_route_result r = {0};
    r.ready_address = 0x503a7cU;
    r.ready_value = ready_value;
    r.hardware_address = 0x503a08U;
    r.hardware_mode = hardware_mode;
    r.status_address = 0x503a18U;
    r.status_word = status_word;
    r.status_threshold = 0xf423eU;
    r.result_r5 = result_r5;
    r.result_r6 = result_r6;
    r.ready_clear_target = 0x1aad4U;
    r.hardware_target = 0x1aa20U;
    r.failed_status_target = 0x1a9e0U;
    r.accepted_target = 0x1a904U;
    if (ready_value == 0U) {
        r.selected_target = r.ready_clear_target;
    } else if (hardware_mode != 0U) {
        r.selected_target = r.hardware_target;
    } else if (status_word > r.status_threshold || result_r5 != 0U || result_r6 != 0U) {
        r.rejected = 1U;
        r.selected_target = r.failed_status_target;
    } else {
        r.accepted = 1U;
        r.selected_target = r.accepted_target;
    }
    if (result != (void *)0)
        *result = r;
    return 1;
}
