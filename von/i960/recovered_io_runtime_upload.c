/* Pure protocol boundary for the clean-runtime 0x29d0 -> 0x25d0 -> 0x2990
 * handoff.  Device reads/writes and callback bodies remain caller-owned. */
#include "recovered_common.h"

typedef unsigned short recovered_u16;
typedef unsigned char recovered_u8;

recovered_u32 recovered_io_command_plan(recovered_u16 input_index,
                                        recovered_u16 table_value,
                                        recovered_u8 output[34]);

struct recovered_io_runtime_upload_result {
    recovered_u32 gated;
    recovered_u32 callback_arg;
    recovered_u32 callback_result;
    recovered_u32 normalized_latch;
    recovered_u32 upload_result;
};

/* callback_result is the value returned by the unresolved 0x2540/0x2580
 * helper pair; callback_arg is the value published by that pair. */
recovered_u32 recovered_io_runtime_upload_plan(
    recovered_u32 latch, recovered_u32 callback_result,
    recovered_u32 callback_arg, recovered_u32 upload_limit,
    recovered_u32 upload_enable, recovered_u16 input_index,
    recovered_u16 table_value, recovered_u8 output[34],
    struct recovered_io_runtime_upload_result *result)
{
    result->gated = (latch & (1U << 10)) != 0U;
    result->callback_arg = callback_arg;
    result->callback_result = callback_result;
    result->normalized_latch = latch;
    result->upload_result = 0U;
    if (!result->gated)
        return 0U;

    /* 0x29d0 primes bit 10 before 0x25d0; 0x25d0 republishes it. */
    result->normalized_latch |= 1U << 10;
    if ((recovered_u32)input_index >= upload_limit ||
        (upload_enable & 1U) == 0U)
        return 1U;
    result->upload_result = recovered_io_command_plan(
        input_index, table_value, output);
    return 1U;
}
