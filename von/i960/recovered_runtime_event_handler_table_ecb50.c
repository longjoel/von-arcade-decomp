/* Event-handler address table recovered from i960 0xecb50-ecbb0. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 base_address;
    recovered_u32 entry_count;
    recovered_u32 entry[25];
    recovered_u32 terminator_address;
} recovered_runtime_event_handler_table_result_ecb50;

recovered_runtime_event_handler_table_result_ecb50
recovered_runtime_event_handler_table_ecb50(void)
{
    recovered_runtime_event_handler_table_result_ecb50 result = {
        0x000ecb50U, 25U,
        {0x000eca30U, 0x000eca60U, 0x000eca90U, 0x000ecac0U,
         0x000ecaf0U, 0x000ecb20U, 0x000eb2c0U, 0x000ebab0U,
         0x000ec920U, 0x000ebe20U, 0x000ebc60U, 0x000ebfd0U,
         0x000ec140U, 0x000ec290U, 0x000ec3e0U, 0x000ec8f0U,
         0x000ec480U, 0x000ec760U, 0x000ec630U, 0x000eb830U,
         0x000ec8f0U, 0x000ec940U, 0x000ec940U, 0x000ec940U,
         0x000ec940U},
        0x000ecbb4U
    };
    return result;
}
