/* Fixed startup/device table wrapper recovered from i960 0xe37f0-0xe3824. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 first_source;
    recovered_u32 first_destination;
    recovered_u32 first_bytes;
    recovered_u32 second_source;
    recovered_u32 second_destination;
    recovered_u32 second_bytes;
    recovered_u32 copy_helper;
} recovered_startup_device_table_copy_result_e37f0;

/*
 * The wrapper makes two calls to the shared forward-copy leaf 0xf5d40.  The
 * lengths are literal byte counts: 0x50 for the first table and 0x78 for
 * the second (the latter is formed as shlo 3,15).
 */
void recovered_startup_device_table_copy_e37f0(
    recovered_startup_device_table_copy_result_e37f0 *result)
{
    result->first_source = 0x01d00144U;
    result->first_destination = 0x00578410U;
    result->first_bytes = 0x50U;
    result->second_source = 0x01d00194U;
    result->second_destination = 0x00578460U;
    result->second_bytes = 0x78U;
    result->copy_helper = 0x000f5d40U;
}
