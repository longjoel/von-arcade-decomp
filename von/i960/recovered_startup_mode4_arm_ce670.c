/* Fourth phase-table arm recovered from i960 0xce670-0xce8ec. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 frame_adjust, saved_register_bytes;
    recovered_u32 reset_call, reset_argument;
    recovered_u32 startup_state_address, startup_state_value;
    recovered_u32 phase_helper_call, phase_helper_argument;
    recovered_u32 phase_address, phase_before, phase_after;
    recovered_u32 helper_call[3], helper_call_count;
    recovered_u32 result_address, result_value;
    recovered_u32 template_source, template_word_count;
    recovered_u32 record_base, record_stride, record_index;
    recovered_u32 record_word_offset[21], record_word_value[21];
    recovered_u32 clear_address[5], clear_count;
    recovered_u32 setup_call[2], setup_argument[2], setup_count;
    recovered_u32 workspace_address[5], workspace_clear_count;
    recovered_u32 workspace_phase_source, workspace_table_source;
    recovered_u32 workspace_return_load_address, return_target;
} recovered_startup_mode4_arm_result_ce670;

int recovered_startup_mode4_arm_ce670(
    recovered_u32 record_index, recovered_u32 phase_value,
    const recovered_u32 template_words[21], recovered_u32 *result_words,
    recovered_startup_mode4_arm_result_ce670 *result)
{
    recovered_startup_mode4_arm_result_ce670 r = {0};
    static const recovered_u32 offsets[21] = {
        0U, 4U, 8U, 12U, 16U, 20U, 24U, 28U, 32U, 36U, 40U,
        44U, 48U, 52U, 56U, 60U, 64U, 68U, 72U, 76U, 80U
    };
    r.frame_adjust = 16U;
    r.saved_register_bytes = 32U;
    r.reset_call = 0x29c08U;
    r.reset_argument = 0U;
    r.startup_state_address = 0x577590U;
    r.startup_state_value = 12U;
    r.phase_helper_call = 0x1ccf8U;
    r.phase_helper_argument = 0x7cc1U;
    r.phase_address = 0x503a00U;
    r.phase_before = phase_value;
    r.phase_after = phase_value + 1U;
    r.helper_call[0] = 0x6f9e8U;
    r.helper_call[1] = 0x6fa48U;
    r.helper_call[2] = 0x6fad8U;
    r.helper_call_count = 3U;
    r.result_address = 0x51c850U;
    r.template_source = 0xc9220U;
    r.template_word_count = 21U;
    r.record_base = 0x51c5b0U;
    r.record_stride = 0x154U;
    r.record_index = record_index;
    for (recovered_u32 i = 0; i < 21U; ++i) {
        r.record_word_offset[i] = offsets[i];
        r.record_word_value[i] = template_words != (void *)0 ? template_words[i] : 0U;
        if (result_words != (void *)0)
            result_words[i] = r.record_word_value[i];
    }
    r.clear_address[0] = 0x503aacU;
    r.clear_address[1] = 0x503a94U;
    r.clear_address[2] = 0x503b34U;
    r.clear_address[3] = 0x504134U;
    r.clear_address[4] = 0x577138U;
    r.clear_count = 5U;
    r.setup_call[0] = 0x2a4e0U;
    r.setup_call[1] = 0xc9a00U;
    r.setup_argument[0] = 0x100cU;
    r.setup_argument[1] = 0U;
    r.setup_count = 2U;
    r.workspace_address[0] = 0x577120U;
    r.workspace_address[1] = 0x577124U;
    r.workspace_address[2] = 0x577128U;
    r.workspace_address[3] = 0x57712cU;
    r.workspace_address[4] = 0x577130U;
    r.workspace_clear_count = 5U;
    r.workspace_phase_source = 0x503a80U;
    r.workspace_table_source = 0xc98d0U;
    r.workspace_return_load_address = 0x577590U;
    r.return_target = 0xce8ecU;
    if (result != (void *)0)
        *result = r;
    return 1;
}
