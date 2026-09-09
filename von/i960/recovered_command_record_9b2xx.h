#ifndef VON_RECOVERED_COMMAND_RECORD_9B2XX_H
#define VON_RECOVERED_COMMAND_RECORD_9B2XX_H

#include "recovered_common.h"

/* Shared layout established by 0x9b288 stores and 0x9b320/0x9b498 accesses:
 * sixteen records, each 0x10 bytes, rooted at 0x562b80. */
typedef struct {
    uint8_t active;
    uint8_t reserved;
    uint16_t value_2;
    recovered_u32 value_4;
    recovered_u32 value_8;
    recovered_u32 value_c;
} recovered_command_record_9b2xx;

typedef struct {
    recovered_command_record_9b2xx record[16];
    recovered_u32 cursor;
} recovered_command_record_table_9b2xx;

#endif
