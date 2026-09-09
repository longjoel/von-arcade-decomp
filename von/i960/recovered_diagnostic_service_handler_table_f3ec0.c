/* Diagnostic service table recovered from i960 0xf3ec0-f3ee8. */
#include "recovered_common.h"
typedef struct { recovered_u32 table_address,entry_count; recovered_u32 handler[11]; recovered_u32 return_boundary; } recovered_diagnostic_service_handler_table_result_f3ec0;
recovered_diagnostic_service_handler_table_result_f3ec0 recovered_diagnostic_service_handler_table_f3ec0(void){recovered_diagnostic_service_handler_table_result_f3ec0 r={0x000f3ec0U,11U,{0x000ed220U,0x000ed320U,0x000ed5c0U,0x000eda30U,0x000f04d0U,0x000f0980U,0x000f1c90U,0x000f2e20U,0x000f33a0U,0x000f3ab0U,0x000f3c50U},0x000f3ee8U};return r;}
