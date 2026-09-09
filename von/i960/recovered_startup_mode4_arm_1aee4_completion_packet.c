/* Slot-10 completion packet recovered from i960 0x1aee4-0x1afd0. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 phase_latch;
    recovered_u32 fifo_address, fifo_word_count, fifo_word[13];
    recovered_u32 register_r27, derived_command;
    recovered_u32 frame_publish_address, frame_word[4];
    recovered_u32 control_address, control_value;
    recovered_u32 pointer_source_address, pointer_value, pointer_destination;
    recovered_u32 pointer_destination_value;
    recovered_u32 packet_emitted, return_target;
} recovered_startup_mode4_arm_1aee4_completion_packet_result;

int recovered_startup_mode4_arm_1aee4_completion_packet(
    recovered_u32 phase_latch, recovered_u32 register_r27,
    recovered_u32 device_control_value,
    recovered_startup_mode4_arm_1aee4_completion_packet_result *result)
{
    recovered_startup_mode4_arm_1aee4_completion_packet_result r = {0};
    r.phase_latch = phase_latch;
    r.fifo_address = 0x884000U;
    r.fifo_word_count = 13U;
    r.register_r27 = register_r27;
    r.derived_command = 31U + register_r27;
    r.frame_publish_address = 0x804000U;
    r.frame_word[0] = 0U;
    r.frame_word[1] = 0x400128U;
    r.frame_word[2] = 0x8f31a0U;
    r.frame_word[3] = 0U;
    r.control_address = 0x800010U;
    r.control_value = 0x101U;
    r.pointer_source_address = 0x802008U;
    r.pointer_value = device_control_value;
    r.pointer_destination = 0x801008U;
    r.pointer_destination_value = device_control_value + RECOVERED_POINTER_OFFSET;
    r.return_target = 0x1afd0U;
    if (phase_latch != 0U) {
        r.packet_emitted = 1U;
        r.fifo_word[0] = 5U;
        r.fifo_word[1] = 16U;
        r.fifo_word[2] = 18U;
        r.fifo_word[3] = 0U;
        r.fifo_word[4] = 0U;
        r.fifo_word[5] = 0x3dcccccdU;
        r.fifo_word[6] = 19U;
        r.fifo_word[7] = 0x41a00000U;
        r.fifo_word[8] = 0x41a00000U;
        r.fifo_word[9] = 0x3f800000U;
        r.fifo_word[10] = r.derived_command;
        r.fifo_word[11] = device_control_value;
        r.fifo_word[12] = 6U;
    }
    if (result != (void *)0)
        *result = r;
    return 1;
}
