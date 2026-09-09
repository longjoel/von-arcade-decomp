/* Geometry status emitter phase prefix recovered from i960 0xe6d80-0xe6ec8. */
#include "recovered_common.h"

typedef struct {
    int32_t input_phase;
    int32_t clamped_phase;
    int32_t stored_phase;
    recovered_u32 phase_address;
    recovered_u32 lower_bound;
    recovered_u32 upper_bound;
    recovered_u32 quantization_shift;
    recovered_u32 quantization_mask;
    recovered_u32 fifo_address;
    recovered_u32 first_command;
    recovered_u32 second_command;
    recovered_u32 third_command;
    recovered_u32 final_command;
    recovered_u32 next_target;
} recovered_geometry_status_emit_phase_result_e6d80;

recovered_geometry_status_emit_phase_result_e6d80
recovered_geometry_status_emit_phase_prefix_e6d80(int32_t input_phase)
{
    recovered_geometry_status_emit_phase_result_e6d80 result;

    result.input_phase = input_phase;
    result.clamped_phase = input_phase;
    if (result.clamped_phase < 0)
        result.clamped_phase = 0;
    else if (result.clamped_phase > 40)
        result.clamped_phase = 40;
    result.stored_phase = result.clamped_phase - 1;
    result.phase_address = 0x005783d8U;
    result.lower_bound = 0;
    result.upper_bound = 40U;
    result.quantization_shift = 10U;
    result.quantization_mask = 0xfc00U;
    result.fifo_address = 0x00884000U;
    result.first_command = 29U;
    result.second_command = 29U;
    result.third_command = 30U;
    result.final_command = 18U;
    result.next_target = 0x000e6ee8U;
    return result;
}
