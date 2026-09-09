/* Selector-1 packet prefix recovered from i960 0x88ea0-0x88f04. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 record_184;
    recovered_u32 transformed_record_184;
    recovered_u32 fifo_response;
    recovered_u32 record_8;
    recovered_u32 packet_29[3];
    recovered_u32 packet_30[3];
    recovered_u32 fifo_address;
    recovered_u32 float_constant;
    recovered_u32 first_command;
    recovered_u32 second_command;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_88ea0_packet_prefix_result;

recovered_startup_mode4_arm_88ea0_packet_prefix_result
recovered_startup_mode4_arm_88ea0_packet_prefix(
    recovered_u32 record_184, recovered_u32 fifo_response,
    recovered_u32 record_8)
{
    recovered_startup_mode4_arm_88ea0_packet_prefix_result result;

    result.record_184 = record_184;
    result.transformed_record_184 = (record_184 + 0x6000U) & 0xffffU;
    result.fifo_response = fifo_response;
    result.record_8 = record_8;
    result.packet_29[0] = 29U;
    result.packet_29[1] = result.transformed_record_184;
    result.packet_29[2] = 0x42a00000U;
    result.packet_30[0] = 30U;
    result.packet_30[1] = result.transformed_record_184;
    result.packet_30[2] = 0x42a00000U;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.float_constant = 0x42a00000U;
    result.first_command = 29U;
    result.second_command = 30U;
    result.continuation = 0x00088f04U;
    return result;
}
