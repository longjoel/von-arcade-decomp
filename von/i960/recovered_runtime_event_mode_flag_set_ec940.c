/* Event-mode flag setter recovered from i960 0xec940-ec960. */
#include "recovered_common.h"
typedef struct { recovered_u32 continuation_address, flag_address, flag_value, return_target; } recovered_runtime_event_mode_flag_set_result_ec940;
recovered_runtime_event_mode_flag_set_result_ec940 recovered_runtime_event_mode_flag_set_ec940(void) {
    recovered_runtime_event_mode_flag_set_result_ec940 result;
    result.continuation_address=0xec960U; result.flag_address=0x578514U; result.flag_value=1U; result.return_target=0xec960U; return result;
}
