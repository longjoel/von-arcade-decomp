/* CRT diagnostic service contract recovered from i960 0xf04d0-f08b4. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 result_state_address, result_state_init_value;
    recovered_u32 pattern_state_address, pattern_state_init_value;
    recovered_u32 pattern_state_initial;
    recovered_u32 pattern_data_address, pattern_data_init_value;
    recovered_u32 continuation_address, header_x, header_y, header_string;
    recovered_u32 label_wrapper, pattern_service, handler_table_address;
    recovered_u32 handler_count, handler_address[6];
    recovered_u32 return_target;
} recovered_diagnostic_crt_test_service_result_f04d0;

recovered_diagnostic_crt_test_service_result_f04d0
recovered_diagnostic_crt_test_service_f04d0(void)
{
    recovered_diagnostic_crt_test_service_result_f04d0 result = {
        0x00578500U, 1U, 0x005784f4U, 6U, 6U,
        0x01004e14U, 30U, 0x005784f0U,
        12U, 6U, 0x000eaf90U, 0x000eaeb0U, 0x000184e8U,
        0x000f0674U, 6U,
        {0x000f068cU,0x000f06ecU,0x000f074cU,0x000f07b8U,
         0x000f0818U,0x000f0888U},
        0x000f08b4U
    };
    return result;
}
