/* Response-helper gate recovered from i960 0x8ca80-0x8cac8. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 buffer;
    recovered_u32 threshold_address, threshold_value;
    recovered_u32 source_value;
    recovered_u32 gate_address, gate_value;
    recovered_u32 returned;
    recovered_u32 packet_path;
    recovered_u32 packet_entry;
} recovered_startup_mode4_arm_result_8ca80_response_gate;

int recovered_startup_mode4_arm_8ca80_response_gate(
    recovered_u32 buffer, recovered_u32 source_value,
    recovered_startup_mode4_arm_result_8ca80_response_gate *result)
{
    recovered_startup_mode4_arm_result_8ca80_response_gate r = {0};
    r.buffer = buffer;
    r.threshold_address = 0x51c984U;
    r.threshold_value = 0x77U;
    r.source_value = source_value;
    r.gate_address = 0x51c99cU;
    r.gate_value = source_value > r.threshold_value ? 1U : 0U;
    r.returned = r.gate_value == 0U ? 1U : 0U;
    r.packet_path = r.gate_value;
    r.packet_entry = 0x8ccfcU;
    return result != (void *)0 ? (*result = r, 1) : 1;
}
