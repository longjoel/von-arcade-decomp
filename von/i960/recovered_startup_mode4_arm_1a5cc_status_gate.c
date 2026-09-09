/* Slot-10 status split recovered from i960 0x1a5cc-0x1a620. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 status_address, status_word, status_threshold;
    recovered_u32 status_high_path;
    recovered_u32 record_helper_address, record_helper_call_count;
    recovered_u32 record_helper_argument0, record_helper_argument1;
    recovered_u32 controller_address, controller_word, controller_bit4_set;
    recovered_u32 text_service_address, text_string_address;
    recovered_u32 phase_continuation, high_status_continuation;
} recovered_startup_mode4_arm_1a5cc_status_gate_result;

int recovered_startup_mode4_arm_1a5cc_status_gate(
    recovered_u32 status_word, recovered_u32 controller_word,
    recovered_startup_mode4_arm_1a5cc_status_gate_result *result)
{
    recovered_startup_mode4_arm_1a5cc_status_gate_result r = {0};
    r.status_address = 0x503a18U;
    r.status_word = status_word;
    r.status_threshold = 0xf423eU;
    r.record_helper_address = 0x1cac8U;
    r.record_helper_argument0 = 6U;
    r.record_helper_argument1 = 3U;
    r.controller_address = 0x5024e8U;
    r.controller_word = controller_word;
    r.controller_bit4_set = (controller_word & 0x10U) != 0U ? 1U : 0U;
    r.text_string_address = 0x1a490U;
    r.phase_continuation = 0x1a620U;
    r.high_status_continuation = 0x1a7c8U;

    /* cmpi status,threshold followed by ble admits the signed <= arm. */
    if ((int32_t)status_word > (int32_t)r.status_threshold) {
        r.status_high_path = 1U;
        r.record_helper_call_count = 1U;
        r.text_service_address = r.controller_bit4_set != 0U ? 0x1d210U : 0x1d1f0U;
    }
    if (result != (void *)0)
        *result = r;
    return 1;
}
