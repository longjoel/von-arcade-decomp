/* Slot-12 ready/device gate recovered from i960 0x1b5d8-0x1b614. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 ready_address, ready_value;
    recovered_u32 device_word_address, device_word, device_signed;
    recovered_u32 register_19_value, expected_device_word;
    recovered_u32 device_low_halfword, adjusted_status;
    recovered_u32 status_mask, status_offset, status_threshold;
    recovered_u32 branch;
    recovered_u32 return_target, helper_call, helper_continuation;
} recovered_startup_mode4_arm_result_1b5d8_device_gate;

int recovered_startup_mode4_arm_1b5d8_device_gate(
    recovered_u32 ready_value, recovered_u32 device_word,
    recovered_u32 register_19_value,
    recovered_startup_mode4_arm_result_1b5d8_device_gate *result)
{
    recovered_startup_mode4_arm_result_1b5d8_device_gate r = {0};

    r.ready_address = 0x503a7cU;
    r.ready_value = ready_value;
    r.device_word_address = 0x5024f4U;
    r.device_word = device_word;
    r.device_signed = (recovered_u32)recovered_sign_extend_16(device_word);
    r.register_19_value = register_19_value;
    r.expected_device_word = register_19_value + 31U;
    r.device_low_halfword = device_word & 0xffffU;
    r.status_mask = 0xffffU;
    r.status_offset = 0xffedU;
    r.status_threshold = 1U;
    r.return_target = 0x1b95cU;
    r.helper_call = 0x43ee8U;
    r.helper_continuation = 0x423a8U;

    if (ready_value == 0U) {
        r.branch = 1U;
    } else if (r.device_signed == r.expected_device_word) {
        r.branch = 2U;
    } else {
        r.adjusted_status = (r.device_low_halfword + r.status_offset) & r.status_mask;
        if (r.adjusted_status > r.status_threshold)
            r.branch = 1U;
        else
            r.branch = 2U;
    }
    return result != (void *)0 ? (*result = r, 1) : 1;
}
